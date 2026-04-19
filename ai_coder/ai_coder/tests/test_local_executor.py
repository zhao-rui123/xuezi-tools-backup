from __future__ import annotations

import subprocess
import unittest
from unittest.mock import Mock, patch

from ai_coder.core.models import ExecutorType, Task, TaskType
from ai_coder.executors.local import LocalExecutor


class LocalExecutorTests(unittest.TestCase):
    def test_build_command_uses_string_enums(self) -> None:
        executor = LocalExecutor(acpx_path="acpx", workspace="~")
        task = Task(
            type=TaskType.SESSION_NEW,
            executor=ExecutorType.LOCAL,
            session_name="demo",
            no_wait=False,
        )
        self.assertEqual(executor._build_command(task), ["acpx", "claude", "sessions", "new", "--name", "demo"])

    @patch("ai_coder.executors.local.subprocess.run")
    def test_execute_returns_background_id_for_no_wait(self, run_mock: Mock) -> None:
        run_mock.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout="queued\n", stderr="")
        executor = LocalExecutor(acpx_path="acpx", workspace="~")
        task = Task(
            id="task-123",
            type=TaskType.EXEC,
            executor=ExecutorType.LOCAL,
            command="do work",
            no_wait=True,
        )
        result = executor.execute(task)
        self.assertTrue(result.success)
        self.assertEqual(result.background_task_id, "task-123")
