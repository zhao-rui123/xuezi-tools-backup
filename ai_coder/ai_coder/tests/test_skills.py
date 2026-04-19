from __future__ import annotations

import unittest
from pathlib import Path

from ai_coder.core.models import ExecutionResult, ExecutorType, Task, TaskType
from ai_coder.skills.loader import SkillLoader
from ai_coder.skills.registry import SkillRegistry
from ai_coder.skills.runner import SkillRunner


class FakeExecutor:
    def __init__(self) -> None:
        self.last_task = None

    def execute(self, task: Task) -> ExecutionResult:
        self.last_task = task
        return ExecutionResult(
            success=True,
            output=task.command or "",
            error="",
            exit_code=0,
            started_at="start",
            completed_at="end",
            duration_ms=1,
            executor_type=task.executor,
        )


class FakeFactory:
    def __init__(self) -> None:
        self.executor = FakeExecutor()

    def create(self, executor_type: ExecutorType) -> FakeExecutor:
        return self.executor


class SkillTests(unittest.TestCase):
    def test_yaml_skill_load_and_run(self) -> None:
        skill_path = Path(__file__).parent / "fixtures" / "sample_skill.yaml"
        loader = SkillLoader()
        registry = SkillRegistry()
        registry.register(loader.load_file(skill_path))
        factory = FakeFactory()
        runner = SkillRunner(registry, factory)
        result = runner.run(
            Task(
                type=TaskType.OMC,
                executor=ExecutorType.LOCAL,
                skill_name="summarize",
                command="write docs",
            )
        )
        self.assertEqual(result.output, "summarize: write docs")
        self.assertEqual(factory.executor.last_task.type, TaskType.EXEC)
