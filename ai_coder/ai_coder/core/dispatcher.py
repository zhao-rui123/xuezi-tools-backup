"""Task routing across executors and skills."""

from __future__ import annotations

from typing import Any

from ..background.manager import BackgroundTaskManager
from ..exceptions import SkillError
from ..security.audit import JsonLineAuditLogger
from ..skills.runner import SkillRunner
from .models import ExecutionResult, Task, TaskType


class Dispatcher:
    """Dispatch tasks to the correct execution surface."""

    def __init__(
        self,
        executor_factory: Any,
        *,
        skill_runner: SkillRunner | None = None,
        background_manager: BackgroundTaskManager | None = None,
        audit_logger: JsonLineAuditLogger | None = None,
    ):
        self.executor_factory = executor_factory
        self.skill_runner = skill_runner
        self.background_manager = background_manager
        self.audit_logger = audit_logger

    def dispatch(self, task: Task) -> ExecutionResult:
        self._audit("task.received", {"task_id": task.id, "type": task.type.value, "executor": task.executor.value})
        try:
            if task.type == TaskType.OMC:
                if self.skill_runner is None:
                    raise SkillError("Skill runner is not configured")
                result = self.skill_runner.run(task)
            else:
                executor = self.executor_factory.create(task.executor)
                result = executor.execute(task)
            if self.background_manager is not None:
                self.background_manager.record(task, result)
            self._audit(
                "task.completed",
                {
                    "task_id": task.id,
                    "success": result.success,
                    "exit_code": result.exit_code,
                    "background_task_id": result.background_task_id,
                },
            )
            return result
        except Exception as exc:
            self._audit("task.failed", {"task_id": task.id, "error": str(exc)})
            raise

    def _audit(self, event_type: str, payload: dict[str, Any]) -> None:
        if self.audit_logger is not None:
            self.audit_logger.record(event_type, payload)
