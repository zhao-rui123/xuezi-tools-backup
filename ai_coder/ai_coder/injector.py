"""Direct Prompt Injection for running workflows.

Allows real-time intervention into running workflow tasks by injecting
new prompts at specific steps without restarting the entire workflow.
"""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ai_coder.workflows.workflow_loader import WORKFLOW_RUNS_DIR, get_run_dir, utc_now_iso

# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #


@dataclass
class Injection:
    """A single prompt injection request."""

    id: str
    run_id: str
    prompt: str
    step_index: int | None = None  # 1-based step index, None = inject at next step
    created_at: str = field(default_factory=lambda: utc_now_iso())
    executed: bool = False
    executed_at: str | None = None
    result: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "run_id": self.run_id,
            "prompt": self.prompt,
            "step_index": self.step_index,
            "created_at": self.created_at,
            "executed": self.executed,
            "executed_at": self.executed_at,
            "result": self.result,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Injection":
        return cls(
            id=data["id"],
            run_id=data["run_id"],
            prompt=data["prompt"],
            step_index=data.get("step_index"),
            created_at=data.get("created_at", utc_now_iso()),
            executed=data.get("executed", False),
            executed_at=data.get("executed_at"),
            result=data.get("result"),
            error=data.get("error"),
        )


# --------------------------------------------------------------------------- #
# Store
# --------------------------------------------------------------------------- #


class InjectionStore:
    """Thread-safe store for prompt injections per workflow run."""

    def __init__(self, run_id: str) -> None:
        self._run_id = run_id
        self._run_dir = get_run_dir(run_id)
        self._run_dir.mkdir(parents=True, exist_ok=True)
        self._path = self._run_dir / "injections.json"
        self._lock = threading.Lock()
        self._cache: list[Injection] | None = None

    def _load(self) -> list[Injection]:
        if not self._path.exists():
            return []
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            return [Injection.from_dict(d) for d in data]
        except Exception:
            return []

    def _save(self, injections: list[Injection]) -> None:
        self._path.write_text(
            json.dumps([inj.to_dict() for inj in injections], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self._cache = injections

    def add(self, prompt: str, step_index: int | None = None) -> Injection:
        """Add a new injection request."""
        import uuid
        inj = Injection(
            id=str(uuid.uuid4())[:8],
            run_id=self._run_id,
            prompt=prompt,
            step_index=step_index,
        )
        with self._lock:
            injections = self._load()
            injections.append(inj)
            self._save(injections)
        return inj

    def pending(self) -> list[Injection]:
        """Return all pending (not yet executed) injections."""
        with self._lock:
            return [inj for inj in self._load() if not inj.executed]

    def mark_executed(
        self, injection_id: str, result: str | None = None, error: str | None = None
    ) -> None:
        """Mark an injection as executed."""
        with self._lock:
            injections = self._load()
            for inj in injections:
                if inj.id == injection_id:
                    inj.executed = True
                    inj.executed_at = utc_now_iso()
                    inj.result = result
                    inj.error = error
                    break
            self._save(injections)

    def peek_next(self) -> Injection | None:
        """Return the next pending injection (FIFO), or None."""
        pending = self.pending()
        return pending[0] if pending else None

    def clear_executed(self) -> None:
        """Remove all executed injections to keep the file small."""
        with self._lock:
            injections = self._load()
            remaining = [inj for inj in injections if not inj.executed]
            self._save(remaining)


# --------------------------------------------------------------------------- #
# Module-level helpers
# --------------------------------------------------------------------------- #


def inject(run_id: str, prompt: str, step_index: int | None = None) -> Injection:
    """Add a prompt injection to a running workflow.

    Args:
        run_id: The workflow run ID (e.g. "abc12345")
        prompt: The prompt to inject
        step_index: Optional 1-based step index to target specific step

    Returns:
        The created Injection object
    """
    store = InjectionStore(run_id)
    return store.add(prompt, step_index)


def pending_injections(run_id: str) -> list[Injection]:
    """Return all pending injections for a run."""
    return InjectionStore(run_id).pending()


def consume_injection(run_id: str) -> tuple[Injection | None, list[Injection]]:
    """Atomically peek and return all pending injections.

    Returns (next_injection, all_pending).
    """
    store = InjectionStore(run_id)
    next_inj = store.peek_next()
    all_pending = store.pending()
    return next_inj, all_pending
