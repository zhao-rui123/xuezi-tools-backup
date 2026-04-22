"""Task Planner - Decompose high-level goals into actionable sub-tasks.

Uses a structured decomposition strategy based on OMC's agent roles.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SubTask:
    """A single decomposable sub-task."""

    id: str
    description: str
    agent: str = "executor"
    prompt_template: str = ""
    depends_on: list[str] = field(default_factory=list)
    priority: int = 1  # 1=highest
    tags: list[str] = field(default_factory=list)

    def prompt(self, context: dict[str, Any] | None = None) -> str:
        """Render the prompt template with context."""
        if not self.prompt_template:
            return self.description
        ctx = context or {}
        result = self.prompt_template

        def replacer(match: re.Match) -> str:
            key = match.group(1).strip()
            if "." in key:
                # e.g. {{task.output}}
                parts = key.split(".", 1)
                val = ctx.get(parts[0], {})
                if isinstance(val, dict):
                    return str(val.get(parts[1], match.group(0)))
                return str(val)
            return str(ctx.get(key, match.group(0)))

        result = re.sub(r"\{\{([^}]+)\}\}", replacer, result)
        return result


@dataclass
class TaskPlan:
    """A complete plan with decomposed sub-tasks."""

    goal: str
    tasks: list[SubTask] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def serial_order(self) -> list[SubTask]:
        """Return tasks in dependency-respected order (simple topological sort)."""
        remaining = {t.id: t for t in self.tasks}
        ordered: list[SubTask] = []
        emitted: set[str] = set()

        while remaining:
            progress = False
            for tid, task in list(remaining.items()):
                if all(dep in emitted for dep in task.depends_on):
                    ordered.append(task)
                    emitted.add(tid)
                    del remaining[tid]
                    progress = True
            if not progress:
                # Circular dependency or missing dep - just emit remaining
                ordered.extend(remaining.values())
                break

        return ordered

    def parallel_bundles(self) -> list[list[SubTask]]:
        """Return tasks grouped into parallel bundles (independent tasks together)."""
        ordered = self.serial_order()
        bundles: list[list[SubTask]] = []
        current_bundle: list[SubTask] = []
        seen_deps: set[str] = set()

        for task in ordered:
            if task.depends_on and any(dep in seen_deps for dep in task.depends_on):
                if current_bundle:
                    bundles.append(current_bundle)
                    current_bundle = []
                current_bundle.append(task)
            else:
                current_bundle.append(task)
            seen_deps.add(task.id)

        if current_bundle:
            bundles.append(current_bundle)
        return bundles


# --------------------------------------------------------------------------- #
# Decomposer
# --------------------------------------------------------------------------- #

# Keywords that trigger specific agent routing
AGENT_KEYWORDS = {
    "architect": ["架构", "设计", "design", "architect", "技术选型", "系统设计"],
    "code-reviewer": ["审查", "review", "代码质量", "review code"],
    "security-reviewer": ["安全", "security", "漏洞", "渗透"],
    "analyst": ["分析", "analyse", "analyze", "调研", "research"],
    "explore": ["探索", "explore", "查找", "find", "搜索"],
    "debugger": ["调试", "debug", "bug", "修复", "fix", "排查"],
    "test-engineer": ["测试", "test", "测试用例", "单元测试"],
    "verifier": ["验证", "verify", "验收", "assert"],
    "git-master": ["git", "版本", "commit", "branch"],
}

# High-level goal patterns that trigger decomposition
GOAL_PATTERNS = {
    "user-auth": {
        "keywords": ["用户认证", "登录", "注册", "auth", "login", "register", "oauth", "jwt"],
        "tasks": [
            SubTask(id="auth-spec", description="编写用户认证系统规格说明", agent="architect",
                    prompt_template="设计一个用户认证系统，包含{{features|用户名密码认证}}功能。使用 JWT Token。输出架构设计文档。",
                    tags=["spec"]),
            SubTask(id="auth-db", description="设计数据库表结构", agent="executor",
                    prompt_template="为用户认证系统设计数据库表，包含 users 表和 refresh_tokens 表。输出 SQL。",
                    depends_on=["auth-spec"], tags=["db"]),
            SubTask(id="auth-backend", description="实现后端认证 API", agent="executor",
                    prompt_template="实现用户注册、登录、Token刷新、登出的后端 API。使用 Python Flask。",
                    depends_on=["auth-db"], tags=["backend"]),
            SubTask(id="auth-frontend", description="实现前端认证表单", agent="executor",
                    prompt_template="实现登录和注册表单，包含输入验证和错误处理。",
                    depends_on=["auth-backend"], tags=["frontend"]),
            SubTask(id="auth-test", description="编写认证功能测试", agent="test-engineer",
                    prompt_template="为认证系统编写单元测试，覆盖正常流程和错误处理。",
                    depends_on=["auth-backend"], tags=["test"]),
        ],
    },
    "rest-api": {
        "keywords": ["rest", "api", "接口", "restful", "rest api"],
        "tasks": [
            SubTask(id="api-design", description="设计 REST API 规范", agent="architect",
                    prompt_template="设计 REST API 规范，包含资源定义、HTTP 方法、状态码。输出 OpenAPI/Swagger 文档。",
                    tags=["spec"]),
            SubTask(id="api-implement", description="实现 API 端点", agent="executor",
                    prompt_template="实现 REST API，包括 CRUD 操作、输入验证、错误处理。",
                    depends_on=["api-design"], tags=["backend"]),
            SubTask(id="api-doc", description="生成 API 文档", agent="writer",
                    prompt_template="为 REST API 生成使用文档，包含示例请求和响应。",
                    depends_on=["api-implement"], tags=["doc"]),
        ],
    },
    "web-app": {
        "keywords": ["web", "网站", "web app", "前端", "frontend", "react", "vue"],
        "tasks": [
            SubTask(id="web-design", description="设计 UI/UX", agent="designer",
                    prompt_template="设计 Web 应用的 UI，包含页面布局、组件结构和样式规范。输出 Figma 格式或详细说明。",
                    tags=["design"]),
            SubTask(id="web-frontend", description="实现前端页面", agent="executor",
                    prompt_template="使用 React 实现 Web 前端页面，包含{{components|主页和详情页}}。",
                    depends_on=["web-design"], tags=["frontend"]),
            SubTask(id="web-backend", description="实现后端服务", agent="executor",
                    prompt_template="实现 Web 后端服务，包含 API 和数据库交互。",
                    depends_on=["web-design"], tags=["backend"]),
            SubTask(id="web-test", description="端到端测试", agent="qa-tester",
                    prompt_template="对 Web 应用进行端到端测试，验证核心功能流程。",
                    depends_on=["web-frontend", "web-backend"], tags=["test"]),
        ],
    },
}


class TaskDecomposer:
    """Decompose high-level goals into structured sub-tasks."""

    def decompose(self, goal: str, context: dict[str, Any] | None = None) -> TaskPlan:
        """Parse a high-level goal and produce a task plan.

        Uses keyword matching to select a predefined decomposition pattern,
        falling back to a generic single-task plan.
        """
        goal_lower = goal.lower()
        ctx = context or {}

        # Try to match a known pattern
        for pattern_name, pattern in GOAL_PATTERNS.items():
            for kw in pattern["keywords"]:
                if kw.lower() in goal_lower:
                    return self._build_plan(goal, pattern["tasks"], ctx)

        # Fallback: generic single-task plan
        agent = self._detect_agent(goal)
        return TaskPlan(
            goal=goal,
            tasks=[
                SubTask(
                    id="main",
                    description=goal,
                    agent=agent,
                    prompt_template=goal,
                    tags=["main"],
                )
            ],
            metadata={"fallback": True},
        )

    def _build_plan(
        self, goal: str, template_tasks: list[SubTask], context: dict[str, Any]
    ) -> TaskPlan:
        """Build a TaskPlan from template tasks, rendering prompt templates."""
        tasks = []
        for t in template_tasks:
            tasks.append(
                SubTask(
                    id=t.id,
                    description=t.description,
                    agent=t.agent,
                    prompt_template=t.prompt_template,
                    depends_on=list(t.depends_on),
                    priority=t.priority,
                    tags=list(t.tags),
                )
            )
        return TaskPlan(goal=goal, tasks=tasks, metadata={"pattern": "matched"})

    def _detect_agent(self, goal: str) -> str:
        """Detect the most appropriate agent based on goal keywords."""
        goal_lower = goal.lower()
        best_agent = "executor"
        best_score = 0
        for agent, keywords in AGENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in goal_lower)
            if score > best_score:
                best_score = score
                best_agent = agent
        return best_agent
