"""Local executor backed by subprocess without shell interpolation."""

from __future__ import annotations

import os
import subprocess
import time
from datetime import datetime, timezone

from ..core.models import ExecutionResult, ExecutorType, Task, TaskType
from .base import BaseExecutor


class LocalExecutor(BaseExecutor):
    """Execute acpx commands on the local machine."""

    def __init__(self, acpx_path: str = "acpx", workspace: str = "~/.openclaw/workspace", model: str | None = None):
        super().__init__(ExecutorType.LOCAL)
        self.acpx_path = acpx_path
        self.workspace = os.path.expanduser(workspace)
        self.model = model

    def is_available(self) -> bool:
        try:
            subprocess.run(
                [self.acpx_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=True,
            )
            return True
        except (OSError, subprocess.SubprocessError):
            return False

    def execute(self, task: Task) -> ExecutionResult:
        self.validate_task(task)
        started_at = datetime.now(timezone.utc).isoformat()
        start = time.perf_counter()
        try:
            result = subprocess.run(
                self._build_command(task),
                capture_output=True,
                text=True,
                timeout=task.timeout,
                cwd=self.workspace if os.path.isdir(self.workspace) else None,
            )
            duration_ms = int((time.perf_counter() - start) * 1000)
            return ExecutionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                exit_code=result.returncode,
                started_at=started_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=duration_ms,
                executor_type=self.executor_type,
                session_id=task.session_name,
                background_task_id=task.id if task.no_wait and result.returncode == 0 else None,
            )
        except subprocess.TimeoutExpired:
            duration_ms = int((time.perf_counter() - start) * 1000)
            return ExecutionResult(
                success=False,
                output="",
                error=f"Timeout after {task.timeout}s",
                exit_code=-1,
                started_at=started_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=duration_ms,
                executor_type=self.executor_type,
                session_id=task.session_name,
            )
        except OSError as exc:
            duration_ms = int((time.perf_counter() - start) * 1000)
            return ExecutionResult(
                success=False,
                output="",
                error=str(exc),
                exit_code=-1,
                started_at=started_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=duration_ms,
                executor_type=self.executor_type,
                session_id=task.session_name,
            )

    def _build_command(self, task: Task) -> list[str]:
        cmd = [self.acpx_path, "claude"]
        model = task.model if task.model is not None else self.model
        if model:
            cmd.extend(["--model", model])
        if task.type == TaskType.SESSION_NEW:
            cmd.extend(["sessions", "new", "--name", task.session_name or ""])
            return cmd
        if task.type == TaskType.SESSION_CLOSE:
            cmd.extend(["sessions", "close", task.session_name or ""])
            return cmd
        if task.type == TaskType.STATUS:
            cmd.extend(["-s", task.session_name or "", "status"])
            return cmd
        if task.session_name:
            cmd.extend(["-s", task.session_name])
        if task.no_wait:
            cmd.append("--no-wait")
        if task.type == TaskType.OMC:
            cmd.append(f"{task.skill_name}: {task.command}")
        else:
            cmd.append(task.command or "")
        return cmd
