"""Local executor backed by detached screen sessions."""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import time
from datetime import datetime, timezone

from ..core.models import ExecutionResult, ExecutorType, Task, TaskType
from .base import BaseExecutor
from .screen_utils import ScreenArtifacts, build_screen_command, dump_meta


class LocalExecutor(BaseExecutor):
    """Execute acpx commands on the local machine through screen."""

    CODEX_PROXY = "http://127.0.0.1:1087"

    def __init__(
        self,
        acpx_path: str = "acpx",
        workspace: str = "~/.openclaw/workspace",
        runtime_kind: str = "claude",
        model: str | None = None,
        screen_base_dir: str = "~/.ai_coder/screen",
    ):
        super().__init__(ExecutorType.LOCAL)
        self.acpx_path = acpx_path
        self.workspace = os.path.expanduser(workspace)
        self.runtime_kind = runtime_kind
        self.model = model
        self.screen_base_dir = screen_base_dir

    def is_available(self) -> bool:
        try:
            if shutil.which("screen") is None:
                return False
            subprocess.run(
                [self.acpx_path, self.runtime_kind, "--help"],
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
        artifacts = ScreenArtifacts.for_task(self.screen_base_dir, task.id, self.runtime_kind)
        command = self._build_launch_command(task)
        dump_meta(
            artifacts,
            {
                "task_id": task.id,
                "runtime_kind": self.runtime_kind,
                "session_name": task.session_name,
                "task_type": task.type.value,
                "command": command,
            },
        )
        try:
            launch = subprocess.run(
                build_screen_command(
                    artifacts=artifacts,
                    workdir=self.workspace,
                    command=command,
                ),
                capture_output=True,
                text=True,
                timeout=task.timeout,
            )
            if launch.returncode != 0:
                return self._result(
                    start=start,
                    started_at=started_at,
                    success=False,
                    output=launch.stdout,
                    error=launch.stderr,
                    exit_code=launch.returncode,
                    session_id=task.session_name,
                )
            if task.no_wait:
                return self._result(
                    start=start,
                    started_at=started_at,
                    success=True,
                    output=launch.stdout,
                    error=launch.stderr,
                    exit_code=0,
                    session_id=task.session_name,
                    background_task_id=task.id,
                )
            return self._wait_for_completion(
                artifacts=artifacts,
                timeout=task.timeout,
                started_at=started_at,
                start=start,
                session_id=task.session_name,
            )
        except subprocess.TimeoutExpired:
            return self._result(
                start=start,
                started_at=started_at,
                success=False,
                output="",
                error=f"Timeout after {task.timeout}s",
                exit_code=-1,
                session_id=task.session_name,
            )
        except OSError as exc:
            return self._result(
                start=start,
                started_at=started_at,
                success=False,
                output="",
                error=str(exc),
                exit_code=-1,
                session_id=task.session_name,
            )

    def _wait_for_completion(
        self,
        *,
        artifacts: ScreenArtifacts,
        timeout: int,
        started_at: str,
        start: float,
        session_id: str | None,
    ) -> ExecutionResult:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if os.path.exists(artifacts.done_path):
                exit_code = self._read_exit_code(artifacts.exit_code_path)
                return self._result(
                    start=start,
                    started_at=started_at,
                    success=exit_code == 0,
                    output=self._read_text_file(artifacts.stdout_path),
                    error=self._read_text_file(artifacts.stderr_path),
                    exit_code=exit_code,
                    session_id=session_id,
                )
            time.sleep(1)
        return self._result(
            start=start,
            started_at=started_at,
            success=False,
            output=self._read_text_file(artifacts.stdout_path),
            error=f"Timeout after {timeout}s",
            exit_code=-1,
            session_id=session_id,
        )

    def _read_text_file(self, path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                return handle.read()
        except FileNotFoundError:
            return ""

    def _read_exit_code(self, path: str) -> int:
        raw = self._read_text_file(path).strip()
        try:
            return int(raw)
        except ValueError:
            return -1

    def _result(
        self,
        *,
        start: float,
        started_at: str,
        success: bool,
        output: str,
        error: str,
        exit_code: int,
        session_id: str | None,
        background_task_id: str | None = None,
    ) -> ExecutionResult:
        duration_ms = int((time.perf_counter() - start) * 1000)
        return ExecutionResult(
            success=success,
            output=output,
            error=error,
            exit_code=exit_code,
            started_at=started_at,
            completed_at=datetime.now(timezone.utc).isoformat(),
            duration_ms=duration_ms,
            executor_type=self.executor_type,
            session_id=session_id,
            background_task_id=background_task_id,
        )

    def _build_command(self, task: Task) -> list[str]:
        cmd = [self.acpx_path, self.runtime_kind]
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
        payload = f"{task.skill_name}: {task.command}" if task.type == TaskType.OMC else (task.command or "")
        if self.runtime_kind == "codex" and not task.session_name:
            cmd.extend(["exec", payload])
        else:
            cmd.append(payload)
        return cmd

    def _build_launch_command(self, task: Task) -> str:
        command = shlex.join(self._build_command(task))
        if self.runtime_kind != "codex":
            return command
        return (
            f"http_proxy={shlex.quote(self.CODEX_PROXY)} "
            f"https_proxy={shlex.quote(self.CODEX_PROXY)} "
            f"HTTP_PROXY={shlex.quote(self.CODEX_PROXY)} "
            f"HTTPS_PROXY={shlex.quote(self.CODEX_PROXY)} "
            f"{command}"
        )
