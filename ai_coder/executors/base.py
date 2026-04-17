"""Abstract executor contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..core.models import ExecutionResult, ExecutorType, Task
from ..exceptions import ValidationError


class BaseExecutor(ABC):
    """Base executor with shared validation."""

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
