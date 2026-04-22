"""Abstract executor contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..core.models import ExecutionResult, ExecutorType, Task, TaskType
from ..exceptions import ValidationError


class BaseExecutor(ABC):
    """Base executor with shared validation."""

    acpx_path: str = "acpx"
    model: str | None = None

    def __init__(self, executor_type: ExecutorType):
        self.executor_type = executor_type

    @abstractmethod
    def execute(self, task: Task) -> ExecutionResult:
        """Execute a task."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return whether this executor is reachable."""

    def validate_task(self, task: Task) -> None:
        if task.executor != self.executor_type:
            raise ValidationError(
                f"Task executor type {task.executor.value!r} does not match executor {self.executor_type.value!r}"
            )

    def _build_argv(self, task: Task) -> list[str]:
        """Build command argv shared by LocalExecutor and RemoteExecutor."""
        argv = [self.acpx_path]
        model = task.model if task.model is not None else self.model
        if model:
            argv.extend(["--model", model])
        if task.type == TaskType.SESSION_NEW:
            argv.extend(["sessions", "new", "--name", task.session_name or ""])
            return argv
        if task.type == TaskType.SESSION_CLOSE:
            argv.extend(["sessions", "close", task.session_name or ""])
            return argv
        if task.type == TaskType.STATUS:
            argv.extend(["-s", task.session_name or "", "status"])
            return argv
        if task.session_name:
            argv.extend(["-s", task.session_name])
        if task.no_wait:
            argv.append("--no-wait")
        if task.type == TaskType.OMC:
            argv.append(f"{task.skill_name}: {task.command}")
        else:
            argv.append(task.command or "")
        return argv
