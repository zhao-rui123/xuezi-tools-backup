"""Thin lifecycle facade around dispatch and status lookups."""

from __future__ import annotations

from ..background.manager import BackgroundTaskManager
from .dispatcher import Dispatcher
from .models import ExecutionResult, Task


class TaskLifecycle:
    """Submit tasks and retrieve local background metadata."""

    def __init__(self, dispatcher: Dispatcher, background_manager: BackgroundTaskManager):
        self.dispatcher = dispatcher
        self.background_manager = background_manager

    def submit(self, task: Task) -> ExecutionResult:
        return self.dispatcher.dispatch(task)

    def get_local_status(self, task_id: str) -> dict[str, object] | None:
        return self.background_manager.get_status(task_id)
