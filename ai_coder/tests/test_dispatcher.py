from __future__ import annotations

import unittest
from unittest.mock import Mock

from ai_coder.core.dispatcher import Dispatcher
from ai_coder.core.models import ExecutionResult, ExecutorType, Task, TaskType


class DispatcherTests(unittest.TestCase):
    def _result(self) -> ExecutionResult:
        return ExecutionResult(
            success=True,
            output="ok",
            error="",
            exit_code=0,
            started_at="start",
            completed_at="end",
            duration_ms=10,
            executor_type=ExecutorType.LOCAL,
        )

    def test_exec_task_uses_executor_factory(self) -> None:
        executor = Mock()
        executor.execute.return_value = self._result()
        factory = Mock()
        factory.create.return_value = executor
        background = Mock()
        dispatcher = Dispatcher(factory, background_manager=background)
        task = Task(type=TaskType.EXEC, executor=ExecutorType.LOCAL, command="do work")
        result = dispatcher.dispatch(task)
        self.assertTrue(result.success)
        executor.execute.assert_called_once_with(task)
        background.record.assert_called_once()

    def test_skill_task_uses_skill_runner(self) -> None:
        factory = Mock()
        skill_runner = Mock()
        skill_runner.run.return_value = self._result()
        dispatcher = Dispatcher(factory, skill_runner=skill_runner)
        task = Task(type=TaskType.OMC, executor=ExecutorType.LOCAL, skill_name="omx", command="do work")
        dispatcher.dispatch(task)
        skill_runner.run.assert_called_once_with(task)
