"""
Retry wrapper with Feishu alerting and task audit logging for ai_coder.

Usage:
    from core.retry import RetryExecutor
    result = RetryExecutor(executor).execute(task)
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Optional

from .models import ExecutionResult, Task

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
    webhook_url: Optional[str] = None,
) -> Optional[str]:
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
    except Exception:  # noqa: BLE001
        return None


def _record_audit(
    task: Task,
    result: ExecutionResult,
    *,
    attempt: int,
    max_retries: int,
    event: str,
    alert_error: Optional[str] = None,
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
        last_result: Optional[ExecutionResult] = None

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
            last_result or task,
            attempt=self._max_retries,
            max_retries=self._max_retries,
            event="task_failed",
            alert_error=alert_error,
        )

        return last_result or ExecutionResult(
            success=False,
            output="",
            error="max retries exceeded",
            exit_code=-1,
            started_at="",
            completed_at="",
            duration_ms=0,
            executor_type=self._executor.executor_type,
        )
