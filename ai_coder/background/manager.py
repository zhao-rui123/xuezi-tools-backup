"""Background metadata manager."""

from __future__ import annotations

from ..core.models import ExecutionResult, Task, TaskStatus
from .store import BackgroundTaskStore


class BackgroundTaskManager:
    """Track local metadata for tasks delegated to acpx --no-wait."""

    def __init__(self, store: BackgroundTaskStore):
        self.store = store

    def record(self, task: Task, result: ExecutionResult) -> None:
        if task.no_wait and result.success:
            status = TaskStatus.SUBMITTED
        else:
            status = TaskStatus.COMPLETED if result.success else TaskStatus.FAILED
        self.store.upsert(task, status, result)

    def get_status(self, task_id: str) -> dict[str, object] | None:
        return self.store.get(task_id)

    def list_recent(self, limit: int = 20) -> list[dict[str, object]]:
        return self.store.list_recent(limit=limit)
