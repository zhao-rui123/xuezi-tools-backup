"""CLI entrypoint."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import click

from .background.manager import BackgroundTaskManager
from .background.store import BackgroundTaskStore
from .config.loader import load_settings
from .core.dispatcher import Dispatcher
from .core.models import ExecutorType, Task, TaskType
from .exceptions import AICoderError, ConfigError
from .executors.factory import ExecutorFactory
from .executors.local import LocalExecutor
from .executors.remote import RemoteExecutor
from .security.audit import JsonLineAuditLogger
from .security.sanitizer import InputSanitizer
from .skills.builtin import build_omc_skill, build_omx_skill
from .skills.loader import SkillLoader
from .skills.registry import SkillRegistry
from .skills.runner import SkillRunner


def _provider_to_executor(provider: str) -> ExecutorType:
    return ExecutorType.LOCAL if provider == "local" else ExecutorType.REMOTE


def _build_runtime(config_path: str | None) -> dict[str, Any]:
    settings = load_settings(config_path)
    sanitizer = InputSanitizer(settings.security.max_task_length)
    audit_logger = JsonLineAuditLogger(
        enabled=settings.security.enable_audit,
        path=settings.security.resolved_audit_log_path,
    )
    store = BackgroundTaskStore()
    background_manager = BackgroundTaskManager(store)
    factory = ExecutorFactory(settings)
    registry = SkillRegistry()
    registry.register(build_omc_skill())
    registry.register(build_omx_skill())
    registry.load_many(SkillLoader().load_directory(Path("skills")))
    runner = SkillRunner(registry, factory)
    dispatcher = Dispatcher(
        factory,
        skill_runner=runner,
        background_manager=background_manager,
        audit_logger=audit_logger,
    )
    return {
        "settings": settings,
        "sanitizer": sanitizer,
        "background_manager": background_manager,
        "factory": factory,
        "registry": registry,
        "dispatcher": dispatcher,
    }


def _ensure_remote_if_needed(runtime: dict[str, Any], provider: str) -> None:
    if provider == "kr":
        runtime["settings"].remote


def _validate_task_text(sanitizer: InputSanitizer, text: str) -> str:
    result = sanitizer.sanitize(text)
    if not result.is_valid:
        raise click.ClickException("; ".join(result.violations))
    return result.value


def _validate_session(sanitizer: InputSanitizer, session_name: str) -> str:
    result = sanitizer.validate_session_name(session_name)
    if not result.is_valid:
        raise click.ClickException("; ".join(result.violations))
    return result.value


def _print_result(result: Any) -> None:
    if result.output:
        click.echo(result.output.rstrip("\n"))
    if result.error:
        click.echo(result.error.rstrip("\n"), err=True)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--config", "config_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.pass_context
def cli(ctx: click.Context, config_path: Path | None) -> None:
    """AI Coder."""

    try:
        ctx.obj = _build_runtime(str(config_path) if config_path else None)
    except (AICoderError, ConfigError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command("exec")
@click.argument("task")
@click.option("--provider", "-p", type=click.Choice(["local", "kr"]), default="local")
@click.option("--session", "-s")
@click.option("--wait/--no-wait", default=True)
@click.option("--timeout", type=int, default=300, show_default=True)
@click.pass_obj
def exec_command(runtime: dict[str, Any], task: str, provider: str, session: str | None, wait: bool, timeout: int) -> None:
    try:
        sanitizer = runtime["sanitizer"]
        _ensure_remote_if_needed(runtime, provider)
        command = _validate_task_text(sanitizer, task)
        session_name = _validate_session(sanitizer, session) if session else None
        task_obj = Task(
            type=TaskType.EXEC,
            executor=_provider_to_executor(provider),
            command=command,
            session_name=session_name,
            no_wait=not wait,
            timeout=timeout,
        )
        result = runtime["dispatcher"].dispatch(task_obj)
        _print_result(result)
        if not result.success:
            raise SystemExit(result.exit_code)
    except (AICoderError, ConfigError) as exc:
        raise click.ClickException(f"配置错误：{exc}") from exc
    except Exception as exc:
        raise click.ClickException(f"执行任务失败：{exc}") from exc


@cli.command("session-new")
@click.argument("name")
@click.option("--provider", "-p", type=click.Choice(["local", "kr"]), default="local")
@click.option("--timeout", type=int, default=300, show_default=True)
@click.pass_obj
def session_new(runtime: dict[str, Any], name: str, provider: str, timeout: int) -> None:
    try:
        sanitizer = runtime["sanitizer"]
        _ensure_remote_if_needed(runtime, provider)
        session_name = _validate_session(sanitizer, name)
        result = runtime["dispatcher"].dispatch(
            Task(
                type=TaskType.SESSION_NEW,
                executor=_provider_to_executor(provider),
                session_name=session_name,
                no_wait=False,
                timeout=timeout,
            )
        )
        _print_result(result)
        if not result.success:
            raise SystemExit(result.exit_code)
    except (AICoderError, ConfigError) as exc:
        raise click.ClickException(f"配置错误：{exc}") from exc
    except Exception as exc:
        raise click.ClickException(f"创建session失败：{exc}") from exc


@cli.command("session-close")
@click.argument("name")
@click.option("--provider", "-p", type=click.Choice(["local", "kr"]), default="local")
@click.option("--timeout", type=int, default=300, show_default=True)
@click.pass_obj
def session_close(runtime: dict[str, Any], name: str, provider: str, timeout: int) -> None:
    try:
        sanitizer = runtime["sanitizer"]
        _ensure_remote_if_needed(runtime, provider)
        session_name = _validate_session(sanitizer, name)
        result = runtime["dispatcher"].dispatch(
            Task(
                type=TaskType.SESSION_CLOSE,
                executor=_provider_to_executor(provider),
                session_name=session_name,
                no_wait=False,
                timeout=timeout,
            )
        )
        _print_result(result)
        if not result.success:
            raise SystemExit(result.exit_code)
    except (AICoderError, ConfigError) as exc:
        raise click.ClickException(f"配置错误：{exc}") from exc
    except Exception as exc:
        raise click.ClickException(f"关闭session失败：{exc}") from exc


@cli.command("status")
@click.option("--provider", "-p", type=click.Choice(["local", "kr"]), default="local")
@click.option("--session", "-s")
@click.option("--task-id")
@click.option("--json-output", is_flag=True, default=False)
@click.option("--timeout", type=int, default=300, show_default=True)
@click.pass_obj
def status_command(
    runtime: dict[str, Any],
    provider: str,
    session: str | None,
    task_id: str | None,
    json_output: bool,
    timeout: int,
) -> None:
    try:
        sanitizer = runtime["sanitizer"]
        if task_id:
            record = runtime["background_manager"].get_status(task_id)
            if record is None:
                raise click.ClickException(f"未找到任务：{task_id}")
            click.echo(json.dumps(record, ensure_ascii=False, indent=2) if json_output else f"{record['id']} {record['status']}")
            return
        if not session:
            raise click.ClickException("请指定 --session 或 --task-id")
        _ensure_remote_if_needed(runtime, provider)
        session_name = _validate_session(sanitizer, session)
        result = runtime["dispatcher"].dispatch(
            Task(
                type=TaskType.STATUS,
                executor=_provider_to_executor(provider),
                session_name=session_name,
                no_wait=False,
                timeout=timeout,
            )
        )
        _print_result(result)
        if not result.success:
            raise SystemExit(result.exit_code)
    except (AICoderError, ConfigError) as exc:
        raise click.ClickException(f"配置错误：{exc}") from exc
    except Exception as exc:
        raise click.ClickException(f"查询状态失败：{exc}") from exc


@cli.command("skill")
@click.argument("skill_name")
@click.argument("task")
@click.option("--provider", "-p", type=click.Choice(["local", "kr"]), default="local")
@click.option("--session", "-s")
@click.option("--wait/--no-wait", default=True)
@click.option("--timeout", type=int, default=300, show_default=True)
@click.pass_obj
def skill_command(
    runtime: dict[str, Any],
    skill_name: str,
    task: str,
    provider: str,
    session: str | None,
    wait: bool,
    timeout: int,
) -> None:
    # 先检查skill是否存在
    registry = runtime["registry"]
    available_skills = [s.name for s in registry.list()]
    if skill_name not in available_skills:
        raise click.ClickException(
            f"未找到skill：{skill_name}\n"
            f"可用的skills：\n  " + "\n  ".join(available_skills)
        )
    try:
        sanitizer = runtime["sanitizer"]
        _ensure_remote_if_needed(runtime, provider)
        command = _validate_task_text(sanitizer, task)
        session_name = _validate_session(sanitizer, session) if session else None
        result = runtime["dispatcher"].dispatch(
            Task(
                type=TaskType.OMC,
                executor=_provider_to_executor(provider),
                command=command,
                session_name=session_name,
                skill_name=skill_name,
                no_wait=not wait,
                timeout=timeout,
            )
        )
        _print_result(result)
        if not result.success:
            raise SystemExit(result.exit_code)
    except (AICoderError, ConfigError) as exc:
        raise click.ClickException(f"配置错误：{exc}") from exc
    except Exception as exc:
        raise click.ClickException(f"运行skill失败：{exc}") from exc


@cli.command("skills")
@click.pass_obj
def list_skills(runtime: dict[str, Any]) -> None:
    for skill in runtime["registry"].list():
        click.echo(f"{skill.name}\t{skill.description}")


# --------------------------------------------------------------------------- #
# doctor command helpers
# --------------------------------------------------------------------------- #

import subprocess
import textwrap

try:
    import paramiko
    _PARAMIKO_AVAILABLE = True
except ImportError:
    _PARAMIKO_AVAILABLE = False


class DoctorCheck:
    """A single health-check item with result and optional fix."""

    def __init__(self, label: str) -> None:
        self.label = label
        self.passed = False
        self.warning = False
        self.error_msg = ""
        self.fixes: list[str] = []

    def ok(self) -> "DoctorCheck":
        self.passed = True
        return self

    def warn(self, msg: str, *fixes: str) -> "DoctorCheck":
        self.warning = True
        self.error_msg = msg
        self.fixes = list(fixes)
        return self

    def fail(self, msg: str, *fixes: str) -> "DoctorCheck":
        self.passed = False
        self.error_msg = msg
        self.fixes = list(fixes)
        return self


def _run_doctor() -> list[DoctorCheck]:
    checks: list[DoctorCheck] = []

    # ── 1. Config loading ──────────────────────────────────────────────────
    cfg_check = DoctorCheck("Config file")
    try:
        settings = load_settings()
        cfg_check.ok()
    except Exception as exc:
        cfg_check.fail(str(exc), "Check ~/.ai_coder/config.yaml syntax", "Run: ai_coder --config /path/to/config.toml doctor")
    checks.append(cfg_check)

    if not cfg_check.passed:
        return checks  # can't proceed without config

    # ── 2. Local acpx ──────────────────────────────────────────────────────
    local_check = DoctorCheck("Local acpx")
    local_exec = LocalExecutor(
        acpx_path=settings.local.acpx_path,
        workspace=settings.local.resolved_workspace,
    )
    if local_exec.is_available():
        local_check.ok()
    else:
        local_check.fail(
            f"acpx not found at '{settings.local.acpx_path}'",
            f"Install: pip install acpx  (or check AI_CODER_LOCAL_ACPX_PATH)",
            f"Verify Claude Code is installed and reachable.",
        )
    checks.append(local_check)

    # ── 3. Workspace directory ──────────────────────────────────────────────
    ws_check = DoctorCheck("Workspace directory")
    ws_path = settings.local.resolved_workspace
    from pathlib import Path
    if Path(ws_path).is_dir():
        ws_check.ok()
    else:
        ws_check.warn(
            f"Workspace not a directory: {ws_path}",
            f"Create: mkdir -p {ws_path}",
            f"Set workspace in config: local.workspace = ~/.openclaw/workspace",
        )
    checks.append(ws_check)

    # ── 4. Paramiko ────────────────────────────────────────────────────────
    paramiko_check = DoctorCheck("paramiko installed")
    if _PARAMIKO_AVAILABLE:
        paramiko_check.ok()
    else:
        paramiko_check.fail(
            "paramiko not installed (required for remote/KR execution)",
            "Install: pip install paramiko",
        )
    checks.append(paramiko_check)

    # ── 5. Remote config (env/config file) ────────────────────────────────
    remote_cfg_check = DoctorCheck("Remote config (KR)")
    has_remote = settings.has_remote_config()
    if has_remote:
        remote_cfg_check.ok()
    else:
        remote_cfg_check.fail(
            "Remote config incomplete: AI_CODER_KR_HOST / AI_CODER_KR_USER / AI_CODER_SSH_KEY not set",
            "Set env vars: export AI_CODER_KR_HOST=<ip> AI_CODER_KR_USER=ccuser AI_CODER_SSH_KEY=~/.ssh/id_ed25519",
            "Or add to ~/.ai_coder/config.yaml under [remote] section.",
        )
    checks.append(remote_cfg_check)

    if not has_remote:
        return checks  # can't test SSH without config

    # ── 6. SSH key file ────────────────────────────────────────────────────
    ssh_key_check = DoctorCheck("SSH private key")
    ssh_key = settings.remote.resolved_ssh_key
    from pathlib import Path as P
    if P(ssh_key).is_file():
        ssh_key_check.ok()
    else:
        ssh_key_check.fail(
            f"SSH key not found: {ssh_key}",
            f"Generate: ssh-keygen -t ed25519 -f {ssh_key} -N ''",
            f"Add to remote server: ssh-copy-id -i {ssh_key} ccuser@<host>",
        )
    checks.append(ssh_key_check)

    # ── 7. SSH connectivity ───────────────────────────────────────────────
    ssh_check = DoctorCheck("SSH connection to KR")
    if not _PARAMIKO_AVAILABLE:
        ssh_check.warn("paramiko missing – cannot test SSH", "pip install paramiko")
        checks.append(ssh_check)
        return checks

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
        known_hosts = settings.remote.resolved_known_hosts
        if P(known_hosts).is_file():
            client.load_host_keys(known_hosts)
        client.connect(
            hostname=settings.remote.host,
            username=settings.remote.user,
            key_filename=ssh_key,
            look_for_keys=False,
            allow_agent=False,
            timeout=10,
        )
        client.close()
        ssh_check.ok()
    except paramiko.AuthenticationException:
        ssh_check.fail(
            f"Authentication failed for {settings.remote.user}@{settings.remote.host}",
            "Verify SSH key is authorized on remote server.",
            f"Copy key: ssh-copy-id -i {ssh_key} {settings.remote.user}@{settings.remote.host}",
        )
    except paramiko.SSHException as exc:
        ssh_check.fail(
            f"SSH error: {exc}",
            "Check remote SSH service is running.",
            f"Verify host: {settings.remote.host}",
        )
    except OSError as exc:
        ssh_check.fail(
            f"Connection refused / unreachable: {exc}",
            f"Check host is reachable: ping {settings.remote.host}",
            "Verify firewall allows port 22.",
        )
    except Exception as exc:
        ssh_check.fail(str(exc), "Check SSH configuration.")
    checks.append(ssh_check)

    # ── 8. Remote acpx availability ──────────────────────────────────────
    remote_acpx_check = DoctorCheck("Remote acpx on KR")
    if not has_remote or not _PARAMIKO_AVAILABLE:
        remote_acpx_check.warn("Skipped – remote config or paramiko unavailable")
        checks.append(remote_acpx_check)
        return checks

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
        known_hosts_path = settings.remote.resolved_known_hosts
        if P(known_hosts_path).is_file():
            client.load_host_keys(known_hosts_path)
        client.connect(
            hostname=settings.remote.host,
            username=settings.remote.user,
            key_filename=ssh_key,
            look_for_keys=False,
            allow_agent=False,
            timeout=10,
        )
        _, stdout, stderr = client.exec_command(
            f"{settings.remote.acpx_path} --version", timeout=10
        )
        exit_code = stdout.channel.recv_exit_status()
        client.close()
        if exit_code == 0:
            version = stdout.read().decode().strip() or stdout.read().decode().strip()
            remote_acpx_check.ok()
        else:
            err = stderr.read().decode().strip()
            remote_acpx_check.fail(
                f"Remote acpx returned exit code {exit_code}: {err}",
                f"Verify acpx is installed at {settings.remote.acpx_path} on remote.",
                "Check remote AI_CODER_KR_ACPX_PATH setting.",
            )
    except Exception as exc:
        remote_acpx_check.fail(
            f"Could not run acpx on remote: {exc}",
            f"Verify acpx is installed at {settings.remote.acpx_path} on remote server.",
        )
    checks.append(remote_acpx_check)

    return checks


@cli.command("doctor")
@click.pass_obj
def doctor_command(runtime: dict[str, Any]) -> None:
    """Run health checks on configuration, dependencies, and connectivity."""
    checks = _run_doctor()

    summary_pass = sum(1 for c in checks if c.passed)
    summary_warn = sum(1 for c in checks if c.warning and not c.passed)
    summary_fail = sum(1 for c in checks if not c.passed and not c.warning)

    click.echo(click.style("\n=== AI Coder Doctor ===\n", bold=True))

    for check in checks:
        if check.passed:
            icon = click.style("✓", fg="green")
            label = click.style("PASS", fg="green")
        elif check.warning:
            icon = click.style("!", fg="yellow")
            label = click.style("WARN", fg="yellow")
        else:
            icon = click.style("✗", fg="red")
            label = click.style("FAIL", fg="red")

        click.echo(f"  {icon} [{label}] {check.label}")
        if check.error_msg:
            indent = "      "
            wrapped = textwrap.indent(textwrap.fill(check.error_msg, width=60), indent)
            click.echo(click.style(wrapped, fg="cyan"))
        if check.fixes and not check.passed:
            for fix in check.fixes:
                indent = "      → "
                click.echo(click.style(f"{indent}{fix}", fg="cyan"))

    click.echo()
    total = len(checks)
    click.echo(
        click.style(
            f"Summary: {summary_pass}/{total} passed",
            fg="green" if summary_fail == 0 and summary_warn == 0 else "yellow" if summary_fail == 0 else "red",
        )
    )
    if summary_fail > 0:
        raise SystemExit(1)


# --------------------------------------------------------------------------- #
# workflow inject command
# --------------------------------------------------------------------------- #

@cli.group("workflow")
def workflow_group() -> None:
    """Workflow management commands."""
    pass


@workflow_group.command("inject")
@click.argument("run-id")
@click.argument("prompt")
@click.option("--step", "-s", "step_index", type=int, default=None,
              help="1-based step index to target specific step")
@click.pass_obj
def workflow_inject(runtime: dict[str, Any], run_id: str, prompt: str, step_index: int | None) -> None:
    """Inject a prompt into a running workflow.

    RUN-ID: The workflow run ID (e.g. "abc12345")
    PROMPT: The prompt text to inject
    """
    try:
        from .injector import inject
        injection = inject(run_id, prompt, step_index)
        click.echo(f"Injection queued: {injection.id}")
        click.echo(f"  Run ID: {injection.run_id}")
        click.echo(f"  Step: {injection.step_index or 'next step'}")
        click.echo(f"  Created: {injection.created_at}")
    except Exception as exc:
        raise click.ClickException(f"注入prompt失败：{exc}") from exc


# --------------------------------------------------------------------------- #
# ceo command group
# --------------------------------------------------------------------------- #

@cli.group("ceo")
def ceo_group() -> None:
    """CEO / Goal Planning commands."""
    pass


@ceo_group.command("run")
@click.argument("goal")
@click.option("--format", "-f", "output_format", type=click.Choice(["text", "json"]), default="text",
              help="Output format")
@click.pass_obj
def ceo_run(runtime: dict[str, Any], goal: str, output_format: str) -> None:
    """Decompose a high-level goal into actionable sub-tasks.

    GOAL: The goal description to decompose
    """
    try:
        from .ceo.planner import TaskDecomposer
        decomposer = TaskDecomposer()
        plan = decomposer.decompose(goal)

        if output_format == "json":
            import json
            data = {
                "goal": plan.goal,
                "tasks": [
                    {
                        "id": t.id,
                        "description": t.description,
                        "agent": t.agent,
                        "depends_on": t.depends_on,
                        "priority": t.priority,
                        "tags": t.tags,
                    }
                    for t in plan.tasks
                ],
                "metadata": plan.metadata,
            }
            click.echo(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            click.echo(click.style(f"\n=== Goal: {plan.goal} ===\n", bold=True))
            for i, task in enumerate(plan.serial_order(), 1):
                deps = f" (depends: {', '.join(task.depends_on)})" if task.depends_on else ""
                click.echo(f"  {i}. [{task.agent}] {task.description}{deps}")
                click.echo(f"     Tags: {', '.join(task.tags)}")
    except Exception as exc:
        raise click.ClickException(f"CEO规划失败：{exc}") from exc


if __name__ == "__main__":  # pragma: no cover
    try:
        cli()
    except BrokenPipeError:
        sys.exit(1)
