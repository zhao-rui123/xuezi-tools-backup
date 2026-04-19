from __future__ import annotations

import io
import types
import unittest
from unittest.mock import patch

from ai_coder.core.models import ExecutorType, Task, TaskType
from ai_coder.executors.remote import RemoteExecutor


class FakeChannel:
    def __init__(self) -> None:
        self.command = None

    def settimeout(self, timeout: int) -> None:
        self.timeout = timeout

    def exec_command(self, command: str) -> None:
        self.command = command

    def makefile(self, mode: str, size: int) -> io.BytesIO:
        return io.BytesIO(b"remote ok\n")

    def makefile_stderr(self, mode: str, size: int) -> io.BytesIO:
        return io.BytesIO(b"")

    def recv_exit_status(self) -> int:
        return 0

    def close(self) -> None:
        return None


class FakeTransport:
    def __init__(self) -> None:
        self.channel = FakeChannel()

    def open_session(self) -> FakeChannel:
        return self.channel


class FakeSSHClient:
    def __init__(self) -> None:
        self.policy = None
        self.transport = FakeTransport()
        self.connect_kwargs = None
        self.loaded_system = False
        self.loaded_hosts = None

    def load_system_host_keys(self) -> None:
        self.loaded_system = True

    def load_host_keys(self, path: str) -> None:
        self.loaded_hosts = path

    def set_missing_host_key_policy(self, policy: object) -> None:
        self.policy = policy

    def connect(self, **kwargs: object) -> None:
        self.connect_kwargs = kwargs

    def get_transport(self) -> FakeTransport:
        return self.transport

    def close(self) -> None:
        return None


class FakeRejectPolicy:
    pass


class RemoteExecutorTests(unittest.TestCase):
    def test_build_remote_argv(self) -> None:
        executor = RemoteExecutor(
            "example.com",
            "ccuser",
            "~/.ssh/id_ed25519",
            acpx_path="/opt/acpx",
            known_hosts="~/.ssh/known_hosts",
        )
        task = Task(
            type=TaskType.EXEC,
            executor=ExecutorType.REMOTE,
            command="fix bug",
            session_name="sess",
            no_wait=True,
        )
        self.assertEqual(
            executor._build_remote_argv(task),
            ["/opt/acpx", "codex", "-s", "sess", "--no-wait", "fix bug"],
        )

    def test_client_uses_reject_policy(self) -> None:
        fake_paramiko = types.SimpleNamespace(SSHClient=FakeSSHClient, RejectPolicy=FakeRejectPolicy)
        with patch("ai_coder.executors.remote.paramiko", fake_paramiko), patch("ai_coder.executors.remote.os.path.exists", return_value=True):
            executor = RemoteExecutor(
                "example.com",
                "ccuser",
                "~/.ssh/id_ed25519",
                acpx_path="/opt/acpx",
                known_hosts="~/.ssh/known_hosts",
            )
            client = executor._get_client()
            self.assertIsInstance(client.policy, FakeRejectPolicy)
            self.assertEqual(client.connect_kwargs["hostname"], "example.com")
