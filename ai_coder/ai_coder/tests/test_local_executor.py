from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
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

    def test_build_command_uses_codex_exec_without_session(self) -> None:
        executor = LocalExecutor(acpx_path="acpx", workspace="~", runtime_kind="codex")
        task = Task(
            type=TaskType.EXEC,
            executor=ExecutorType.LOCAL,
            command="do work",
            no_wait=False,
        )
        self.assertEqual(executor._build_command(task), ["acpx", "codex", "exec", "do work"])

    @patch("ai_coder.executors.local.subprocess.run")
    def test_execute_returns_background_id_for_no_wait(self, run_mock: Mock) -> None:
        run_mock.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout="queued\n", stderr="")
        executor = LocalExecutor(acpx_path="acpx", workspace="~", screen_base_dir="~/.ai_coder/test-screen")
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
        self.assertEqual(run_mock.call_args.args[0][:2], ["screen", "-dmS"])

    def test_execute_wait_reads_screen_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            executor = LocalExecutor(acpx_path="acpx", workspace=tmpdir, screen_base_dir=tmpdir)
            task = Task(
                id="task-456",
                type=TaskType.EXEC,
                executor=ExecutorType.LOCAL,
                command="do work",
                no_wait=False,
                timeout=5,
            )

            def fake_run(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                artifacts_dir = Path(tmpdir) / "claude" / "task-456"
                artifacts_dir.mkdir(parents=True, exist_ok=True)
                (artifacts_dir / "stdout.log").write_text("done\n", encoding="utf-8")
                (artifacts_dir / "stderr.log").write_text("", encoding="utf-8")
                (artifacts_dir / "exit_code").write_text("0\n", encoding="utf-8")
                (artifacts_dir / "done").write_text("2026-04-20T00:00:00Z\n", encoding="utf-8")
                return subprocess.CompletedProcess(args=argv, returncode=0, stdout="", stderr="")

            with patch("ai_coder.executors.local.subprocess.run", side_effect=fake_run):
                result = executor.execute(task)

            self.assertTrue(result.success)
            self.assertEqual(result.output, "done\n")


if __name__ == "__main__":
    unittest.main()
