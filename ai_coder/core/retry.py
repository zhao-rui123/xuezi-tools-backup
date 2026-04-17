"""
Retry wrapper with Feishu alerting and task audit logging for ai_coder.

Usage:
    from core.retry import retry_with_alert
    result = retry_with_alert(executor).execute(task)
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import asdict
from functools import wraps
from pathlib import Path
from typing import Callable, ParamSpec, TypeVar

from .models import ExecutionResult, Task

P = ParamSpec("P")
T = TypeVar("T")

# Default config
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 5  # seconds
FEISHU_APP_ID = "cli_a9184ac97e78dbdf"


def get_audit_log_path() -> Path:
    """Get the audit log file path, creating the directory if needed."""
    base = Path(os.environ.get("AI_CODER_HOME", "/home/ccuser/ai-coder"))
    log_dir = base / "data"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "tasks.jsonl"


def _send_feishu_alert(
    task: Task,
    result: ExecutionResult,
    *,
    attempts: int,
    webhook_url: str | None = None,
) -> str | None:
    """Send failure alert via Feishu webhook."""
    url = webhook_url or os.environ.get(
        "AI_CODER_FEISHU_WEBHOOK_URL",
        f"https://open.feishu.cn/open-apis/bot/v2/hook/{FEISHU_APP_ID}",
    )
    payload = {
        "msg_type": "text",
        "content": {
            "text": (
                f"🤖 ai-coder task failed after {attempts} attempts\n"
                f"Command: {task.command[:100]}\n"
                f"Session: {task.session_name or 'N/A'}\n"
                f"Error: {result.error or 'Unknown'[:200]}"
            )
        },
    }
    try:
        import urllib.request

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8")
    except Exception as exc:  # noqa: BLE001
        return str(exc)


def _record_audit(
    task: Task,
    result: ExecutionResult,
    *,
    attempt: int,
    max_retries: int,
    event: str,
    alert_error: str | None = None,
) -> None:
    """Record task event to audit log."""
    log_path = get_audit_log_path()
    entry = {
        "event": event,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "command": task.command,
        "session_name": task.session_name,
        "attempt": attempt,
        "max_retries": max_retries,
        "success": result.success,
        "exit_code": result.exit_code,
        "error": result.error,
    }
    if alert_error is not None:
        entry["alert_error"] = alert_error
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def retry_with_alert(
    executor,  # BaseExecutor
    *,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_delay: float = DEFAULT_RETRY_DELAY,
    send_alert: bool = True,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator that adds retry + Feishu alerting + audit logging to executor.execute().

    Args:
        executor: The executor instance to wrap
        max_retries: Maximum number of retry attempts (default 3)
        retry_delay: Seconds to wait between retries (default 5)
        send_alert: Whether to send Feishu alert on final failure (default True)

    Returns:
        Decorated execute method

    Example:
        executor = RemoteExecutor(...)
        result = retry_with_alert(executor).execute(task)
    """

    def decorator(fn: Callable[P, T]) -> Callable[P, T]:
        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_result: ExecutionResult | None = None

            for attempt in range(1, max_retries + 1):
                result = fn(*args, **kwargs)

                if isinstance(result, ExecutionResult) and result.success:
                    _record_audit(
                        args[0].task if args and hasattr(args[0], "task") else Task(command="?"),
                        result,
                        attempt=attempt,
                        max_retries=max_retries,
                        event="task_completed",
                    )
                    return result

                last_result = result

                if attempt < max_retries:
                    time.sleep(retry_delay)
                    _record_audit(
                        args[0].task if args and hasattr(args[0], "task") else Task(command="?"),
                        result,
                        attempt=attempt,
                        max_retries=max_retries,
                        event="task_retry",
                    )

            # All retries exhausted
            task = args[0].task if args and hasattr(args[0], "task") else Task(command="?")
            alert_error = None
            if send_alert and last_result is not None:
                alert_error = _send_feishu_alert(
                    task,
                    last_result,
                    attempts=max_retries,
                )

            _record_audit(
                task,
                last_result or Task(command="?"),
                attempt=max_retries,
                max_retries=max_retries,
                event="task_failed",
                alert_error=alert_error,
            )

            return last_result or result  # type: ignore

        return wrapper  # type: ignore

    return decorator


class RetryExecutor:
    """Wrapper class that adds retry/alerting to any executor."""

    def __init__(
        self,
        executor,
        *,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        send_alert: bool = True,
    ):
        self._executor = executor
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._send_alert = send_alert

    def execute(self, task: Task) -> ExecutionResult:
        last_result: ExecutionResult | None = None

        for attempt in range(1, self._max_retries + 1):
            result = self._executor.execute(task)

            if result.success:
                _record_audit(
                    task,
                    result,
                    attempt=attempt,
                    max_retries=self._max_retries,
                    event="task_completed",
                )
                return result

            last_result = result

            if attempt < self._max_retries:
                time.sleep(self._retry_delay)
                _record_audit(
                    task,
                    result,
                    attempt=attempt,
                    max_retries=self._max_retries,
                    event="task_retry",
                )

        # All retries exhausted
        alert_error = None
        if self._send_alert and last_result is not None:
            alert_error = _send_feishu_alert(
                task,
                last_result,
                attempts=self._max_retries,
            )

        _record_audit(
            task,
            last_result or Task(command="?"),
            attempt=self._max_retries,
            max_retries=self._max_retries,
            event="task_failed",
            alert_error=alert_error,
        )

        return last_result or Task(command="?")  # type: ignore
