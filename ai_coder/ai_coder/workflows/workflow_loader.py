"""Workflow template loader and manager.

Loads .flow template files from the workflows/ directory,
parses them into structured Workflow objects, supports
parameter substitution and auto-matching by task type.

Phase 2 enhancements: parallel steps, context passing, workflow run persistence.
"""

from __future__ import annotations

import json
import re
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Try to use PyYAML for robust parsing, fall back to simple parser
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# --------------------------------------------------------------------------- #
# Data models
# --------------------------------------------------------------------------- #


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class WorkflowStep:
    """A single step within a workflow template."""

    name: str
    prompt: str
    agent: str = "executor"
    parallel: bool = False
    id: str | None = None  # step identifier for context passing

    def render_prompt(self, params: dict[str, Any]) -> str:
        """Render the step prompt by substituting parameters.

        Supports {{var}} and {{var|default}} syntax.
        """
        result = self.prompt

        def replacer(match: re.Match) -> str:
            inner = match.group(1)
            if "|" in inner:
                var_name, default_val = inner.split("|", 1)
                var_name = var_name.strip()
                default_val = default_val.strip()
                return str(params.get(var_name, default_val))
            else:
                var_name = inner.strip()
                return str(params.get(var_name, match.group(0)))

        result = re.sub(r"\{\{([^}]+)\}\}", replacer, result)
        return result

    def render_prompt_with_context(
        self, params: dict[str, Any], context: dict[str, Any]
    ) -> str:
        """Render prompt with both params and step context (e.g. {{step_id.output}})."""
        result = self.render_prompt(params)

        def context_replacer(match: re.Match) -> str:
            path = match.group(1).strip()
            if "." in path:
                step_id, field_name = path.split(".", 1)
                step_data = context.get(step_id, {})
                if isinstance(step_data, dict):
                    return str(step_data.get(field_name, match.group(0)))
                return str(step_data)
            else:
                return str(context.get(path, match.group(0)))

        result = re.sub(r"\{\{([^}]+)\}\}", context_replacer, result)
        return result


@dataclass
class ParallelWorkflowStep:
    """A parallel step containing multiple sub-agents executing simultaneously."""

    name: str
    agents: list[WorkflowStep]
    id: str | None = None

    def render_prompts_with_context(
        self, params: dict[str, Any], context: dict[str, Any]
    ) -> list[WorkflowStep]:
        """Return new WorkflowSteps with rendered prompts."""
        return [
            WorkflowStep(
                name=sa.name,
                prompt=sa.render_prompt_with_context(params, context),
                agent=sa.agent,
                parallel=True,
                id=sa.id or None,
            )
            for sa in self.agents
        ]


@dataclass
class Workflow:
    """A complete workflow template."""

    name: str
    description: str
    steps: list[WorkflowStep | ParallelWorkflowStep] = field(default_factory=list)
    agent: str = "executor"
    parallel: bool = False
    file_path: str | None = None

    def render(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> Workflow:
        """Return a new Workflow with all prompts rendered using params and context."""
        ctx = context or {}
        rendered_steps: list[WorkflowStep | ParallelWorkflowStep] = []
        for step in self.steps:
            if isinstance(step, ParallelWorkflowStep):
                rendered_sub_steps = step.render_prompts_with_context(params, ctx)
                rendered_steps.append(
                    ParallelWorkflowStep(
                        name=step.name,
                        agents=rendered_sub_steps,
                        id=step.id,
                    )
                )
            else:
                rendered_steps.append(
                    WorkflowStep(
                        name=step.name,
                        prompt=step.render_prompt_with_context(params, ctx),
                        agent=step.agent,
                        parallel=step.parallel,
                        id=step.id,
                    )
                )
        return Workflow(
            name=self.name,
            description=self.description,
            steps=rendered_steps,
            agent=self.agent,
            parallel=self.parallel,
            file_path=self.file_path,
        )


# --------------------------------------------------------------------------- #
# YAML-based Parser (preferred)
# --------------------------------------------------------------------------- #

class WorkflowParseError(ValueError):
    """Raised when a .flow file cannot be parsed."""


def _strip_flow_comments(content: str) -> str:
    """Remove comment lines from a .flow file.

    Comments are lines where the stripped content starts with '#'.
    These are skipped entirely. All other lines are kept as-is.
    This preserves the YAML structure while removing .flow file comments.
    """
    lines = content.splitlines()
    result: list[str] = []
    for line in lines:
        stripped = line.strip()
        # Skip pure comment lines (including '# autopilot.flow - ...' headers)
        if stripped.startswith("#"):
            continue
        # Keep everything else (including blank lines)
        result.append(line)
    return "\n".join(result)


def _sanitize_yaml_value(value: Any) -> str:
    """Convert a YAML value to string, handling None and non-string types."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def parse_flow_file(content: str, file_path: str | None = None) -> Workflow:
    """Parse a .flow file content into a Workflow object.

    Uses YAML for robust parsing with the following format::

        name: 模板名称
        description: 模板描述
        steps:
          - name: 步骤1
            prompt: |
              多行 prompt 内容
            agent: executor  (可选，默认 executor)
            parallel: false (可选，默认 false)
          - name: 步骤2
            prompt: 简短 prompt
        agent: executor      (可选)
        parallel: false      (可选)

    Blank lines are ignored. Lines starting with '#' are treated as comments.
    """
    if YAML_AVAILABLE:
        return _parse_flow_yaml(content, file_path)
    else:
        return _parse_flow_simple(content, file_path)


def _parse_flow_yaml(content: str, file_path: str | None) -> Workflow:
    """Parse using PyYAML (preferred)."""
    clean = _strip_flow_comments(content)
    try:
        data = yaml.safe_load(clean)
    except yaml.YAMLError as exc:
        raise WorkflowParseError(
            f"YAML parse error{f' in {file_path}' if file_path else ''}: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise WorkflowParseError(
            f"Expected dict at root{f' in {file_path}' if file_path else ''}, got {type(data).__name__}"
        )

    name = data.get("name")
    if not name:
        raise WorkflowParseError(f"Missing required 'name' field{f' in {file_path}' if file_path else ''}")

    description = _sanitize_yaml_value(data.get("description"))
    default_agent = data.get("agent", "executor")
    default_parallel = str(data.get("parallel", "false")).lower() == "true"

    steps_raw = data.get("steps", [])
    if not isinstance(steps_raw, list):
        raise WorkflowParseError(f"'steps' must be a list{f' in {file_path}' if file_path else ''}")

    steps: list[WorkflowStep | ParallelWorkflowStep] = []
    for i, step_raw in enumerate(steps_raw, 1):
        if not isinstance(step_raw, dict):
            raise WorkflowParseError(
                f"Step {i} must be a dict{f' in {file_path}' if file_path else ''}"
            )

        # Parallel step with multiple agents
        if "agents" in step_raw and "parallel" in step_raw and str(step_raw.get("parallel", "false")).lower() == "true":
            agents_list = step_raw.get("agents", [])
            if not isinstance(agents_list, list):
                raise WorkflowParseError(
                    f"Step '{step_raw.get('name', i)}' 'agents' must be a list{f' in {file_path}' if file_path else ''}"
                )
            sub_steps: list[WorkflowStep] = []
            for j, agent_raw in enumerate(agents_list, 1):
                if not isinstance(agent_raw, dict):
                    raise WorkflowParseError(
                        f"Agent {j} in parallel step must be a dict{f' in {file_path}' if file_path else ''}"
                    )
                agent_name = agent_raw.get("name", f"agent_{j}")
                agent_prompt = _sanitize_yaml_value(agent_raw.get("prompt", ""))
                if not agent_prompt:
                    raise WorkflowParseError(
                        f"Agent '{agent_name}' in parallel step missing 'prompt'{f' in {file_path}' if file_path else ''}"
                    )
                sub_steps.append(
                    WorkflowStep(
                        name=agent_name,
                        prompt=agent_prompt,
                        agent=agent_raw.get("agent", "executor"),
                        parallel=True,
                        id=agent_raw.get("id"),
                    )
                )
            steps.append(
                ParallelWorkflowStep(
                    name=step_raw.get("name", f"并行步骤_{i}"),
                    agents=sub_steps,
                    id=step_raw.get("id"),
                )
            )
            continue

        # Regular step
        step_name = step_raw.get("name")
        if not step_name:
            raise WorkflowParseError(
                f"Step {i} missing 'name'{f' in {file_path}' if file_path else ''}"
            )
        prompt = _sanitize_yaml_value(step_raw.get("prompt", ""))
        if not prompt:
            raise WorkflowParseError(
                f"Step '{step_name}' missing non-empty 'prompt'{f' in {file_path}' if file_path else ''}"
            )
        steps.append(
            WorkflowStep(
                name=step_name,
                prompt=prompt,
                agent=step_raw.get("agent", "executor"),
                parallel=str(step_raw.get("parallel", "false")).lower() == "true",
                id=step_raw.get("id"),
            )
        )

    return Workflow(
        name=name,
        description=description,
        steps=steps,
        agent=default_agent,
        parallel=default_parallel,
        file_path=file_path,
    )


# --------------------------------------------------------------------------- #
# Simple regex-based parser (fallback when PyYAML unavailable)
# --------------------------------------------------------------------------- #

def _parse_flow_simple(content: str, file_path: str | None) -> Workflow:
    """Minimal fallback parser using regex — used when PyYAML is unavailable."""
    lines = content.splitlines()
    name: str | None = None
    description = ""
    steps: list[WorkflowStep] = []
    default_agent = "executor"
    default_parallel = False
    current_step: dict[str, str] | None = None
    prompt_lines: list[str] = []
    prompt_indent = 0
    in_prompt = False

    def _flush_step() -> None:
        nonlocal current_step, prompt_lines, prompt_indent, in_prompt
        if current_step is not None:
            step_name = current_step.get("name", "").strip()
            prompt = "\n".join(prompt_lines).strip()
            if prompt_indent > 0:
                import textwrap
                prompt = textwrap.dedent(prompt).strip()
            if step_name and prompt:
                steps.append(
                    WorkflowStep(
                        name=step_name,
                        prompt=prompt,
                        agent=current_step.get("agent", "executor").strip(),
                        parallel=current_step.get("parallel", "false").strip().lower() == "true",
                    )
                )
            current_step = None
            prompt_lines = []
            prompt_indent = 0
            in_prompt = False

    i = 0
    while i < len(lines):
        raw_line = lines[i]
        line = raw_line.rstrip()
        stripped = line.strip()

        # Skip blank and pure comment lines
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        # End prompt collection when we hit a non-indented key
        if in_prompt and stripped and not stripped.startswith("-") and ":" in stripped:
            indent = len(raw_line) - len(raw_line.lstrip())
            if indent <= prompt_indent - 1:
                in_prompt = False

        if in_prompt:
            # Collect prompt content (de-indent by prompt_indent)
            content_line = raw_line[prompt_indent:]
            prompt_lines.append(content_line)
            i += 1
            continue

        # List item
        if stripped.startswith("- name:"):
            _flush_step()
            value = stripped[len("- name:") :].strip()
            current_step = {"name": value}
            i += 1
            continue

        # Key: value
        if ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()

            if key == "name":
                if current_step is None:
                    name = value
            elif key == "description":
                description = value
            elif key == "agent":
                if current_step is not None:
                    current_step["agent"] = value
                else:
                    default_agent = value
            elif key == "parallel":
                if current_step is not None:
                    current_step["parallel"] = value
                else:
                    default_parallel = value.lower() == "true"
            elif key == "prompt":
                # Multi-line: collect indented lines that follow
                if value:
                    prompt_lines = [value]
                else:
                    prompt_lines = []
                prompt_indent = len(raw_line) - len(raw_line.lstrip()) + len(line) - len(stripped) - 1
                if prompt_indent < 0:
                    prompt_indent = len(raw_line) - len(raw_line.lstrip()) + 1
                in_prompt = True
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    next_stripped = next_line.strip()
                    if not next_stripped or next_stripped.startswith("#"):
                        j += 1
                        continue
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent <= prompt_indent - 1 and next_stripped and ":" in next_stripped:
                        break
                    # Collect de-indented
                    if next_indent >= prompt_indent:
                        prompt_lines.append(next_line[prompt_indent:])
                    else:
                        prompt_lines.append(next_line)
                    j += 1
                i = j - 1

        i += 1

    _flush_step()

    if not name:
        raise WorkflowParseError(
            f"Missing required 'name' field{f' in {file_path}' if file_path else ''}"
        )

    return Workflow(
        name=name,
        description=description,
        steps=steps,
        agent=default_agent,
        parallel=default_parallel,
        file_path=file_path,
    )


# --------------------------------------------------------------------------- #
# Loader
# --------------------------------------------------------------------------- #

class WorkflowLoadError(Exception):
    """Raised when workflows cannot be loaded."""


class WorkflowLoader:
    """Load and manage workflow templates from .flow files."""

    # Keywords used to auto-match a workflow by task description
    AUTO_MATCH_KEYWORDS: dict[str, list[str]] = {
        "autopilot": [
            "autopilot", "自动驾驶", "完整开发", "端到端",
            "implement", "开发", "构建", "create", "build",
        ],
        "review": [
            "review", "审查", "检查", "audit", "检视",
            "代码审查", "review code",
        ],
        "research": [
            "research", "调研", "调查", "研究",
            "investigate", "分析", "survey",
        ],
    }

    def __init__(self, workflows_dir: str | Path | None = None):
        """Initialize loader with the workflows directory.

        If not specified, defaults to the workflows/ subdirectory of this module.
        """
        if workflows_dir is None:
            workflows_dir = Path(__file__).parent
        self.workflows_dir = Path(workflows_dir)

    def load_file(self, file_path: str | Path) -> Workflow:
        """Load a single .flow file."""
        path = Path(file_path)
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise WorkflowLoadError(
                f"Cannot read workflow file {path}: {exc}"
            ) from exc

        try:
            return parse_flow_file(content, str(path))
        except WorkflowParseError:
            raise
        except Exception as exc:
            raise WorkflowLoadError(
                f"Failed to parse workflow file {path}: {exc}"
            ) from exc

    def load_directory(self, workflows_dir: str | Path | None = None) -> dict[str, Workflow]:
        """Load all .flow files from the workflows directory.

        Returns a dict mapping workflow name (slug) to Workflow object.
        Slug is derived from filename: autopilot.flow -> "autopilot"
        """
        if workflows_dir is not None:
            dir_path = Path(workflows_dir)
        else:
            dir_path = self.workflows_dir

        if not dir_path.is_dir():
            raise WorkflowLoadError(f"Workflows directory not found: {dir_path}")

        workflows: dict[str, Workflow] = {}
        for path in sorted(dir_path.glob("*.flow")):
            try:
                wf = self.load_file(path)
                slug = path.stem
                workflows[slug] = wf
            except WorkflowLoadError as exc:
                print(f"Warning: skipped invalid workflow {path}: {exc}", file=sys.stderr)
                continue

        return workflows

    def find_matching(self, task_description: str, workflows: dict[str, Workflow]) -> Workflow | None:
        """Auto-match a workflow based on task description keywords.

        Checks each workflow's AUTO_MATCH_KEYWORDS against the task description
        (case-insensitive) and returns the first matching workflow.
        Falls back to None if no match is found.
        """
        desc_lower = task_description.lower()
        for slug, wf in workflows.items():
            keywords = self.AUTO_MATCH_KEYWORDS.get(slug, [])
            for kw in keywords:
                if kw.lower() in desc_lower:
                    return wf
        return None

    def get(self, name: str, workflows: dict[str, Workflow]) -> Workflow | None:
        """Get a workflow by exact name (case-insensitive) or slug."""
        name_lower = name.lower()
        if name_lower in workflows:
            return workflows[name_lower]
        for wf in workflows.values():
            if wf.name.lower() == name_lower:
                return wf
        return None


# --------------------------------------------------------------------------- #
# Serialization / Deserialization
# --------------------------------------------------------------------------- #

def serialize_workflow(wf: Workflow) -> str:
    """Serialize a Workflow object back to a .flow YAML string.

    This is the inverse of parse_flow_file: it takes a Workflow object
    and produces a reproducible YAML representation that can be saved
    to a .flow file and re-imported.
    """
    lines: list[str] = []
    lines.append(f"name: {wf.name}")
    if wf.description:
        lines.append(f"description: {wf.description}")
    lines.append("steps:")
    for step in wf.steps:
        if isinstance(step, ParallelWorkflowStep):
            lines.append(f"  - name: {step.name}")
            if step.id:
                lines.append(f"    id: {step.id}")
            lines.append("    parallel: true")
            lines.append("    agents:")
            for sa in step.agents:
                lines.append(f"      - name: {sa.name}")
                if sa.id:
                    lines.append(f"        id: {sa.id}")
                prompt_lines = sa.prompt.splitlines()
                if len(prompt_lines) > 1:
                    lines.append("        prompt: |")
                    for pl in prompt_lines:
                        lines.append(f"          {pl}")
                else:
                    lines.append(f"        prompt: {sa.prompt}")
                if sa.agent != "executor":
                    lines.append(f"        agent: {sa.agent}")
        else:
            lines.append(f"  - name: {step.name}")
            if step.id:
                lines.append(f"    id: {step.id}")
            # Multi-line prompt: use | block scalar
            prompt_lines = step.prompt.splitlines()
            if len(prompt_lines) > 1:
                lines.append("    prompt: |")
                for pl in prompt_lines:
                    lines.append(f"      {pl}")
            else:
                lines.append(f"    prompt: {step.prompt}")
            if step.agent != "executor":
                lines.append(f"    agent: {step.agent}")
            if step.parallel:
                lines.append("    parallel: true")
    if wf.agent != "executor":
        lines.append(f"agent: {wf.agent}")
    if wf.parallel:
        lines.append("parallel: true")
    lines.append("")  # trailing newline
    return "\n".join(lines)


def deserialize_workflow(content: str) -> Workflow:
    """Parse a .flow YAML string into a Workflow object.

    This is the same as parse_flow_file but named more clearly for
    the import/export use case.
    """
    return parse_flow_file(content)


# --------------------------------------------------------------------------- #
# Workflow Run Persistence
# --------------------------------------------------------------------------- #

WORKFLOW_RUNS_DIR = Path.home() / ".ai_coder" / "workflow_runs"


def get_run_dir(run_id: str) -> Path:
    run_dir = WORKFLOW_RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


@dataclass
class StepResult:
    """Result of a single step execution."""

    step_name: str
    step_id: str | None
    agent: str
    success: bool
    output: str
    error: str
    started_at: str
    completed_at: str
    duration_ms: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_name": self.step_name,
            "step_id": self.step_id,
            "agent": self.agent,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_ms": self.duration_ms,
        }


@dataclass
class WorkflowRunRecord:
    """A complete workflow run record."""

    run_id: str
    workflow_name: str
    params: dict[str, Any]
    started_at: str
    completed_at: str | None = None
    status: str = "running"  # running | completed | failed
    steps: list[StepResult] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "workflow_name": self.workflow_name,
            "params": self.params,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "status": self.status,
            "steps": [s.to_dict() for s in self.steps],
            "context": self.context,
        }

    def save(self) -> None:
        """Persist the run record to disk."""
        run_dir = get_run_dir(self.run_id)
        record_path = run_dir / "record.json"
        record_path.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

        if self.context:
            context_path = run_dir / "context.json"
            context_path.write_text(json.dumps(self.context, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, run_id: str) -> "WorkflowRunRecord | None":
        """Load a run record from disk."""
        record_path = WORKFLOW_RUNS_DIR / run_id / "record.json"
        if not record_path.exists():
            return None
        try:
            data = json.loads(record_path.read_text(encoding="utf-8"))
            steps = [StepResult(**s) for s in data.get("steps", [])]
            return cls(
                run_id=data["run_id"],
                workflow_name=data["workflow_name"],
                params=data.get("params", {}),
                started_at=data["started_at"],
                completed_at=data.get("completed_at"),
                status=data.get("status", "running"),
                steps=steps,
                context=data.get("context", {}),
            )
        except Exception:
            return None

    def update_context(self, step_id: str, output: str, extra: dict[str, Any] | None = None) -> None:
        """Store a step's output in the workflow context."""
        self.context[step_id] = {
            "output": output,
            **(extra or {}),
        }
        context_path = get_run_dir(self.run_id) / "context.json"
        context_path.write_text(json.dumps(self.context, ensure_ascii=False, indent=2), encoding="utf-8")

    def append_step_result(self, result: StepResult) -> None:
        """Append a step result and persist."""
        self.steps.append(result)
        self.save()

    def finalize(self, status: str) -> None:
        """Mark the run as completed or failed."""
        self.completed_at = utc_now_iso()
        self.status = status
        self.save()


def list_workflow_runs() -> list[WorkflowRunRecord]:
    """List all workflow run records."""
    runs: list[WorkflowRunRecord] = []
    if not WORKFLOW_RUNS_DIR.is_dir():
        return runs
    for run_dir in sorted(WORKFLOW_RUNS_DIR.iterdir(), reverse=True):
        record = WorkflowRunRecord.load(run_dir.name)
        if record:
            runs.append(record)
    return runs


# --------------------------------------------------------------------------- #
# Module-level convenience
# --------------------------------------------------------------------------- #

_default_workflows: dict[str, Workflow] | None = None


def get_workflows() -> dict[str, Workflow]:
    """Load and cache all workflows from the default directory."""
    global _default_workflows
    if _default_workflows is None:
        _default_workflows = WorkflowLoader().load_directory()
    return _default_workflows


def get_workflow(name: str) -> Workflow | None:
    """Get a named workflow from the default collection."""
    return WorkflowLoader().get(name, get_workflows())


def list_workflows() -> list[Workflow]:
    """List all available workflows from the default collection."""
    return list(get_workflows().values())
