"""Skill orchestration."""

from __future__ import annotations

from ..core.models import ExecutionResult, Task, TaskType
from ..exceptions import SkillError
from .registry import SkillRegistry


class SkillRunner:
    """Render a skill command and execute it via the selected executor."""

    def __init__(self, registry: SkillRegistry, executor_factory: object):
        self.registry = registry
        self.executor_factory = executor_factory

    def run(self, task: Task) -> ExecutionResult:
        if task.type != TaskType.OMC:
            raise SkillError("SkillRunner only accepts OMC tasks")
        skill = self.registry.get(task.skill_name or "")
        rendered = skill.render(task.command or "", task.metadata)
        exec_task = Task(
            id=task.id,
            type=TaskType.EXEC,
            executor=skill.executor or task.executor,
            command=rendered,
            session_name=task.session_name,
            timeout=task.timeout,
            no_wait=task.no_wait,
            created_at=task.created_at,
            metadata=task.metadata,
        )
        executor = self.executor_factory.create(exec_task.executor)
        return executor.execute(exec_task)
