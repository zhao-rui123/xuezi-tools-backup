"""Remote executor backed by Paramiko and detached screen sessions."""

from __future__ import annotations

import json
import os
import shlex
import time
from datetime import datetime, timezone
from typing import Any

from ..core.models import ExecutionResult, ExecutorType, Task, TaskType
from ..core.retry import DEFAULT_MAX_RETRIES, DEFAULT_RETRY_DELAY
from ..exceptions import DependencyUnavailableError
from .base import BaseExecutor
from .screen_utils import ScreenArtifacts, build_screen_command

try:
    import paramiko
except ImportError:  # pragma: no cover
    paramiko = None  # type: ignore[assignment]


class RemoteExecutor(BaseExecutor):
    """Execute acpx commands on a remote host over SSH through screen."""

    def __init__(
        self,
        host: str,
        user: str,
        ssh_key: str,
        *,
        acpx_path: str,
        known_hosts: str,
        runtime_kind: str = "codex",
        model: str | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        workspace: str | None = None,
        screen_base_dir: str | None = None,
    ):
        super().__init__(ExecutorType.REMOTE)
        self.host = host
        self.user = user
        self.ssh_key = os.path.expanduser(ssh_key)
        self.acpx_path = acpx_path
        self.known_hosts = os.path.expanduser(known_hosts)
        self.runtime_kind = runtime_kind
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.workspace = workspace or f"/home/{self.user}"
        self.screen_base_dir = screen_base_dir or f"/home/{self.user}/.ai_coder/screen"
        self._client: Any | None = None

    def _ensure_dependency(self) -> None:
        if paramiko is None:
            raise DependencyUnavailableError("paramiko is required for remote execution")

    def _get_client(self) -> Any:
        self._ensure_dependency()
        if self._client is None:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            if os.path.exists(self.known_hosts):
                client.load_host_keys(self.known_hosts)
            client.set_missing_host_key_policy(paramiko.RejectPolicy())
            client.connect(
                hostname=self.host,
                username=self.user,
                key_filename=self.ssh_key,
                look_for_keys=False,
                allow_agent=False,
                timeout=10,
            )
            self._client = client
        return self._client

    def is_available(self) -> bool:
        try:
            if self._run_single_cmd("command -v screen >/dev/null 2>&1", timeout=5).exit_code != 0:
                return False
            result = self._run_single_cmd(
                shlex.join([self.acpx_path, self.runtime_kind, "--help"]),
                timeout=5,
            )
            return result.exit_code == 0
        except Exception:
            return False

    def _cleanup_closed_sessions(self) -> None:
        """Clean up closed session files to prevent accumulation."""
        try:
            result = self._run_single_cmd(
                shlex.join([self.acpx_path, self.runtime_kind, "sessions", "list"]),
                timeout=10,
            )
            if result.success:
                import re

                for line in result.output.split("\n"):
                    if "[closed]" not in line:
                        continue
                    match = re.match(r"^([0-9a-f-]+)\s+\[closed\]", line)
                    if match:
                        sid = match.group(1)
                        self._run_single_cmd(
                            f"rm -f /home/{self.user}/.acpx/sessions/{sid}*.json",
                            timeout=5,
                        )
        except Exception:
            pass

    def _run_single_cmd(self, cmd: str, timeout: int) -> ExecutionResult:
        """Run a single shell command via SSH."""
        started_at = datetime.now(timezone.utc).isoformat()
        start = time.perf_counter()
        try:
            client = self._get_client()
            transport = client.get_transport()
            if transport is None:
                raise RuntimeError("SSH transport is unavailable")
            channel = transport.open_session()
            channel.settimeout(timeout)
            channel.exec_command(cmd)
            stdout = channel.makefile("rb", -1).read().decode("utf-8", errors="replace")
            stderr = channel.makefile_stderr("rb", -1).read().decode("utf-8", errors="replace")
            exit_code = channel.recv_exit_status()
            channel.close()
            return self._result(
                start=start,
                started_at=started_at,
                success=exit_code == 0,
                output=stdout,
                error=stderr,
                exit_code=exit_code,
                session_id=None,
            )
        except Exception as exc:
            return self._result(
                start=start,
                started_at=started_at,
                success=False,
                output="",
                error=str(exc),
                exit_code=-1,
                session_id=None,
            )

    def execute(self, task: Task) -> ExecutionResult:
        self.validate_task(task)
        self._cleanup_closed_sessions()

        artifacts = ScreenArtifacts.for_task(self.screen_base_dir, task.id, self.runtime_kind)
        command = shlex.join(self._build_remote_argv(task))
        meta_preamble = self._build_remote_meta_command(
            artifacts,
            {
                "task_id": task.id,
                "runtime_kind": self.runtime_kind,
                "session_name": task.session_name,
                "task_type": task.type.value,
                "command": command,
            },
        )
        launch_cmd = shlex.join(
            build_screen_command(
                artifacts=artifacts,
                workdir=self.workspace,
                command=command,
                preamble=meta_preamble,
            )
        )
        last_result: ExecutionResult | None = None

        for attempt in range(1, self.max_retries + 1):
            result = self._run_screen_task(
                task=task,
                artifacts=artifacts,
                launch_cmd=launch_cmd,
                session_id=task.session_name,
            )
            if result.success:
                return result
            last_result = result
            if attempt < self.max_retries:
                time.sleep(self.retry_delay)

        return last_result

    def _run_screen_task(
        self,
        *,
        task: Task,
        artifacts: ScreenArtifacts,
        launch_cmd: str,
        session_id: str | None,
    ) -> ExecutionResult:
        started_at = datetime.now(timezone.utc).isoformat()
        start = time.perf_counter()
        launch = self._run_single_cmd(launch_cmd, timeout=task.timeout)
        if launch.exit_code != 0:
            return self._result(
                start=start,
                started_at=started_at,
                success=False,
                output=launch.output,
                error=launch.error,
                exit_code=launch.exit_code,
                session_id=session_id,
            )
        if task.no_wait:
            return self._result(
                start=start,
                started_at=started_at,
                success=True,
                output=launch.output,
                error=launch.error,
                exit_code=0,
                session_id=session_id,
                background_task_id=task.id,
            )
        return self._wait_for_completion(
            artifacts=artifacts,
            timeout=task.timeout,
            started_at=started_at,
            start=start,
            session_id=session_id,
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
            if self._remote_path_exists(artifacts.done_path):
                exit_code = self._read_remote_exit_code(artifacts.exit_code_path)
                return self._result(
                    start=start,
                    started_at=started_at,
                    success=exit_code == 0,
                    output=self._read_remote_file(artifacts.stdout_path),
                    error=self._read_remote_file(artifacts.stderr_path),
                    exit_code=exit_code,
                    session_id=session_id,
                )
            time.sleep(1)
        return self._result(
            start=start,
            started_at=started_at,
            success=False,
            output=self._read_remote_file(artifacts.stdout_path),
            error=f"Timeout after {timeout}s",
            exit_code=-1,
            session_id=session_id,
        )

    def _build_remote_meta_command(self, artifacts: ScreenArtifacts, payload: dict[str, object]) -> str:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        return (
            f"mkdir -p {shlex.quote(artifacts.root_dir)}; "
            f"printf '%s\\n' {shlex.quote(body)} > {shlex.quote(artifacts.meta_path)}"
        )

    def _remote_path_exists(self, path: str) -> bool:
        result = self._run_single_cmd(f"test -f {shlex.quote(path)}", timeout=5)
        return result.exit_code == 0

    def _read_remote_file(self, path: str) -> str:
        result = self._run_single_cmd(f"cat {shlex.quote(path)}", timeout=5)
        return result.output if result.exit_code == 0 else ""

    def _read_remote_exit_code(self, path: str) -> int:
        raw = self._read_remote_file(path).strip()
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

    def _build_remote_argv(self, task: Task) -> list[str]:
        argv = [self.acpx_path, self.runtime_kind]
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
        payload = f"{task.skill_name}: {task.command}" if task.type == TaskType.OMC else (task.command or "")
        if self.runtime_kind == "codex" and not task.session_name:
            argv.extend(["exec", payload])
        else:
            argv.append(payload)
        return argv

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def __del__(self) -> None:  # pragma: no cover
        self.close()
