"""Remote executor backed by Paramiko with strict host key verification."""

from __future__ import annotations

import os
import shlex
import time
from datetime import datetime, timezone
from typing import Any

from ..core.models import ExecutionResult, ExecutorType, Task, TaskType
from ..core.retry import DEFAULT_RETRY_DELAY, DEFAULT_MAX_RETRIES
from ..exceptions import DependencyUnavailableError
from .base import BaseExecutor

try:
    import paramiko
except ImportError:  # pragma: no cover
    paramiko = None  # type: ignore[assignment]


class RemoteExecutor(BaseExecutor):
    """Execute acpx commands on a remote host over SSH."""

    def __init__(
        self,
        host: str,
        user: str,
        ssh_key: str,
        *,
        acpx_path: str,
        known_hosts: str,
        model: str | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        use_direct_codex: bool = False,
    ):
        super().__init__(ExecutorType.REMOTE)
        self.host = host
        self.user = user
        self.ssh_key = os.path.expanduser(ssh_key)
        self.acpx_path = acpx_path
        self.known_hosts = os.path.expanduser(known_hosts)
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.use_direct_codex = use_direct_codex
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
            transport = client.get_transport()
            if transport:
                transport.set_keepalive(30)
            self._client = client
        return self._client

    def is_available(self) -> bool:
        try:
            result = self._run_argv([self.acpx_path, "--version"], timeout=5)
            return result.exit_code == 0
        except Exception:
            return False

    def _cleanup_closed_sessions(self) -> None:
        """Clean up closed session files to prevent accumulation."""
        # Whitelist validation: user must be a valid Unix username
        if not self.user or not self._is_valid_username(self.user):
            return
        try:
            # Get list of closed sessions
            result = self._run_argv(
                [self.acpx_path, "codex", "sessions", "list"],
                timeout=10,
            )
            if result.success:
                import re
                # Parse closed session IDs from output
                for line in result.output.split('\n'):
                    if '[closed]' in line:
                        # Extract session ID (first column)
                        match = re.match(r'^([0-9a-f-]+)\s+\[closed\]', line)
                        if match:
                            sid = match.group(1)
                            # Delete session files via bash
                            cmd = f"rm -f /home/{shlex.quote(self.user)}/.acpx/sessions/{shlex.quote(sid)}*.json"
                            self._run_single_cmd(cmd, timeout=5)
        except Exception:
            pass  # Silently fail - cleanup is best effort

    @staticmethod
    def _is_valid_username(user: str) -> bool:
        """Validate username is a safe Unix username (whitelist check)."""
        import re
        return bool(re.match(r'^[a-z_][a-z0-9_-]*$', user))

    def _run_single_cmd(self, cmd: str, timeout: int) -> ExecutionResult:
        """Run a single shell command via SSH."""
        started_at = datetime.now(timezone.utc).isoformat()
        start = time.perf_counter()
        channel = None
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
            duration_ms = int((time.perf_counter() - start) * 1000)
            return ExecutionResult(
                success=exit_code == 0,
                output=stdout,
                error=stderr,
                exit_code=exit_code,
                started_at=started_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=duration_ms,
                executor_type=self.executor_type,
            )
        except Exception as exc:
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
            )
        finally:
            if channel is not None:
                channel.close()

    def execute(self, task: Task) -> ExecutionResult:
        self.validate_task(task)
        # Clean up closed sessions before each execution
        self._cleanup_closed_sessions()

        argv = self._build_argv(task)
        last_result: ExecutionResult | None = None

        for attempt in range(1, self.max_retries + 1):
            result = self._run_argv(
                argv,
                timeout=task.timeout,
                session_id=task.session_name,
                task_id=task.id if task.no_wait else None,
            )

            if result.success:
                return result

            last_result = result
            if attempt < self.max_retries:
                time.sleep(self.retry_delay)

        return last_result

    def _run_argv(
        self,
        argv: list[str],
        *,
        timeout: int,
        session_id: str | None = None,
        task_id: str | None = None,
    ) -> ExecutionResult:
        started_at = datetime.now(timezone.utc).isoformat()
        start = time.perf_counter()
        channel = None
        try:
            client = self._get_client()
            transport = client.get_transport()
            if transport is None:
                raise RuntimeError("SSH transport is unavailable")
            channel = transport.open_session()
            channel.settimeout(timeout)
            channel.exec_command(shlex.join(argv))
            stdout = channel.makefile("rb", -1).read().decode("utf-8", errors="replace")
            stderr = channel.makefile_stderr("rb", -1).read().decode("utf-8", errors="replace")
            exit_code = channel.recv_exit_status()
            duration_ms = int((time.perf_counter() - start) * 1000)
            return ExecutionResult(
                success=exit_code == 0,
                output=stdout,
                error=stderr,
                exit_code=exit_code,
                started_at=started_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=duration_ms,
                executor_type=self.executor_type,
                session_id=session_id,
                background_task_id=task_id if task_id and exit_code == 0 else None,
            )
        except Exception as exc:
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
                session_id=session_id,
            )
        finally:
            if channel is not None:
                channel.close()

    def _build_argv(self, task: Task) -> list[str]:
        # Direct codex exec mode - bypasses CCR/acpx
        if self.use_direct_codex:
            return self._build_direct_codex_argv(task)
        
        argv = [self.acpx_path, "codex"]
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

    def _build_direct_codex_argv(self, task: Task) -> list[str]:
        """Build command for direct codex exec (bypasses CCR/acpx)."""
        # For direct codex exec, we need to wrap the command in a shell script
        # because codex exec reads from stdin
        if task.type == TaskType.SESSION_NEW:
            # Direct mode doesn't support session management
            return ["echo", "Direct mode does not support session management"]
        if task.type == TaskType.SESSION_CLOSE:
            return ["echo", "Direct mode does not support session management"]
        if task.type == TaskType.STATUS:
            return ["echo", "Direct mode does not support status check"]
        
        # Build the codex exec command
        command = task.command or ""
        if task.type == TaskType.OMC:
            command = f"{task.skill_name}: {task.command}"
        
        # Escape special characters in the command for shell safety
        escaped_command = command.replace("'", "'\\''")
        
        # Build a shell command that sources nvm, changes to workspace, and runs codex exec
        # Using bash -c with the command piped to codex exec
        shell_cmd = f"source ~/.nvm/nvm.sh && cd /home/{self.user} && echo '{escaped_command}' | codex exec --skip-git-repo-check"
        
        return ["bash", "-c", shell_cmd]

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def __del__(self) -> None:  # pragma: no cover
        self.close()
