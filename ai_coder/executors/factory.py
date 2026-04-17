"""Executor factory with cached instances."""

from __future__ import annotations

from ..config.schema import Settings
from ..core.models import ExecutorType
from .local import LocalExecutor
from .remote import RemoteExecutor


class ExecutorFactory:
    """Build and cache executors on demand."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._instances: dict[ExecutorType, object] = {}

    def create(self, executor_type: ExecutorType) -> object:
        if executor_type in self._instances:
            return self._instances[executor_type]
        if executor_type == ExecutorType.LOCAL:
            executor = LocalExecutor(
                acpx_path=self.settings.local.acpx_path,
                workspace=self.settings.local.resolved_workspace,
            )
        else:
            remote = self.settings.remote
            executor = RemoteExecutor(
                remote.host,
                remote.user,
                remote.resolved_ssh_key,
                acpx_path=remote.acpx_path,
                known_hosts=remote.resolved_known_hosts,
            )
        self._instances[executor_type] = executor
        return executor

    def close_all(self) -> None:
        for executor in self._instances.values():
            close = getattr(executor, "close", None)
            if callable(close):
                close()
        self._instances.clear()
