"""Utility for spawning parallel sub-agents via sessions_spawn.

Used by workflow_run to execute parallel steps in a workflow.
"""

from __future__ import annotations

import concurrent.futures
import time
from dataclasses import dataclass
from typing import Any

from ai_coder.core.models import ExecutorType, Task, TaskType, ExecutionResult
from ai_coder.workflows.workflow_loader import utc_now_iso


@dataclass
class SubAgentResult:
    name: str
    agent: str
    step_id: str | None
    success: bool
    output: str
    error: str
    duration_ms: int


def spawn_parallel_agents(
    dispatcher: Any,
    steps: list,
    executor_type: ExecutorType,
    session_name: str | None,
    timeout: int,
    sanitizer: Any,
    max_workers: int = 10,
) -> list[dict[str, Any]]:
    """Execute multiple workflow steps in parallel.

    Args:
        dispatcher: The task dispatcher
        steps: List of WorkflowStep objects to execute in parallel
        executor_type: LOCAL or REMOTE
        session_name: Optional session name
        timeout: Per-step timeout in seconds
        sanitizer: Input sanitizer for command validation
        max_workers: Maximum parallel workers (default 10)

    Returns:
        List of dicts with keys: name, agent, step_id, result
    """

    def validate_and_dispatch(step) -> dict[str, Any]:
        start = time.time()
        started_at = utc_now_iso()

        # Sanitize the prompt
        sanitized = sanitizer.sanitize(step.prompt)
        command = sanitized.value if sanitized.is_valid else step.prompt

        task_obj = Task(
            type=TaskType.EXEC,
            executor=executor_type,
            command=command,
            session_name=session_name,
            no_wait=False,  # always wait for parallel
            timeout=timeout,
            model=None,
        )
        result = dispatcher.dispatch(task_obj)
        duration_ms = int((time.time() - start) * 1000)

        return {
            "name": step.name,
            "agent": step.agent,
            "step_id": getattr(step, "id", None),
            "result": result,
            "duration_ms": duration_ms,
            "started_at": started_at,
        }

    results: list[dict[str, Any]] = []

    # Use ThreadPoolExecutor for I/O-bound parallelism
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(max_workers, len(steps))) as executor:
        future_to_step = {executor.submit(validate_and_dispatch, step): step for step in steps}

        for future in concurrent.futures.as_completed(future_to_step):
            step = future_to_step[future]
            try:
                result_data = future.result(timeout=timeout + 30)
                results.append(result_data)
            except concurrent.futures.TimeoutError:
                fake_result = ExecutionResult(
                    success=False,
                    output="",
                    error=f"步骤 '{step.name}' 执行超时 (>{timeout}s)",
                    exit_code=124,
                    started_at=utc_now_iso(),
                    completed_at=utc_now_iso(),
                    duration_ms=timeout * 1000,
                    executor_type=executor_type,
                    task_id=None,
                )
                results.append({
                    "name": step.name,
                    "agent": step.agent,
                    "step_id": getattr(step, "id", None),
                    "result": fake_result,
                    "duration_ms": timeout * 1000,
                    "started_at": utc_now_iso(),
                })
            except Exception as exc:
                fake_result = ExecutionResult(
                    success=False,
                    output="",
                    error=f"步骤 '{step.name}' 执行失败：{exc}",
                    exit_code=1,
                    started_at=utc_now_iso(),
                    completed_at=utc_now_iso(),
                    duration_ms=0,
                    executor_type=executor_type,
                    task_id=None,
                )
                results.append({
                    "name": step.name,
                    "agent": step.agent,
                    "step_id": getattr(step, "id", None),
                    "result": fake_result,
                    "duration_ms": 0,
                    "started_at": utc_now_iso(),
                })

    # Sort results to maintain order of submission
    name_to_result = {r["name"]: r for r in results}
    ordered_results = [name_to_result[s.name] for s in steps if s.name in name_to_result]
    return ordered_results
