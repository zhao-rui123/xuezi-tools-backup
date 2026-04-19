"""Audit logging for task submission and completion."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


class JsonLineAuditLogger:
    """Append-only JSONL audit logger."""

    def __init__(self, *, enabled: bool, path: str):
        self.enabled = enabled
        self.path = Path(path).expanduser()

    def record(self, event_type: str, payload: Mapping[str, Any]) -> None:
        if not self.enabled:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "payload": dict(payload),
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=True) + "\n")
