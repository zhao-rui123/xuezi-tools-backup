"""Background metadata manager."""

from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING

from ..core.models import ExecutionResult, Task, TaskStatus
from .store import BackgroundTaskStore

if TYPE_CHECKING:
    from ..executors.base import BaseExecutor


class BackgroundTaskManager:
    """Track local metadata for tasks delegated to acpx --no-wait."""

    def __init__(self, store: BackgroundTaskStore, executor: BaseExecutor | None = None):
        self.store = store
        self._executor = executor
        self._poll_thread: threading.Thread | None = None
        self._stop_polling = threading.Event()

    def record(self, task: Task, result: ExecutionResult) -> None:
        if task.no_wait and result.success:
            status = TaskStatus.SUBMITTED
        else:
            status = TaskStatus.COMPLETED if result.success else TaskStatus.FAILED
        self.store.upsert(task, status, result)

    def get_status(self, task_id: str) -> dict[str, object] | None:
        # Try to refresh if status is still SUBMITTED
        record = self.store.get(task_id)
        if record is None:
            return None
        if record.get("status") == TaskStatus.SUBMITTED.value and self._executor is not None:
            self._refresh_task_status(task_id)
            record = self.store.get(task_id)
        return record

    def _refresh_task_status(self, task_id: str) -> None:
        """Query the executor for the latest status of a submitted background task."""
        try:
            # Poll the background task via the executor
            # The executor's poll_background_status method returns
            # (success, output, error, exit_code) or None if not yet complete
            result = self._poll_background_task(task_id)
            if result is None:
                return  # Still running
            success, output, error, exit_code = result
            self.store.update_status(task_id, TaskStatus.COMPLETED if success else TaskStatus.FAILED, output, error, exit_code)
        except Exception:
            pass  # Polling failures are non-fatal

    def _poll_background_task(self, task_id: str) -> tuple[bool, str, str, int] | None:
        """Poll a background task. Returns (success, output, error, exit_code) or None if still running."""
        if self._executor is None:
            return None
        # Import here to avoid circular deps
        from ..core.models import Task as TaskModel, TaskType
        poll_task = TaskModel(
            type=TaskType.EXEC,
            executor=self._executor.executor_type,
            command=f"acpx codex status {task_id}",
            no_wait=True,
            timeout=30,
        )
        # For now, use the store's background_task_id to correlate
        # The actual polling is best-effort via the executor
        try:
            result = self._executor.execute(poll_task)
            # Parse result to determine if task is complete
            if "completed" in result.output.lower() or result.exit_code == 0:
                return (True, result.output, result.error, result.exit_code)
            elif "failed" in result.output.lower() or result.exit_code != 0:
                return (False, result.output, result.error, result.exit_code)
        except Exception:
            pass
        return None

    def refresh_submitted(self) -> None:
        """Refresh status of all SUBMITTED tasks."""
        for record in self.store.list_recent(limit=100):
            if record.get("status") == TaskStatus.SUBMITTED.value:
                self._refresh_task_status(record["id"])

    def list_recent(self, limit: int = 20) -> list[dict[str, object]]:
        return self.store.list_recent(limit=limit)
