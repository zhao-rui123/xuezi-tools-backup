"""Core task and result models."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from ..exceptions import ValidationError


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TaskType(str, Enum):
    EXEC = "exec"
    SESSION_NEW = "session_new"
    SESSION_CLOSE = "session_close"
    STATUS = "status"
    OMC = "omc"


class ExecutorType(str, Enum):
    LOCAL = "local"
    REMOTE = "remote"


class TaskStatus(str, Enum):
    SUBMITTED = "submitted"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class Task:
    """Immutable task definition."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: TaskType = TaskType.EXEC
    executor: ExecutorType = ExecutorType.LOCAL
    command: str | None = None
    session_name: str | None = None
    skill_name: str | None = None
    timeout: int = 300
    no_wait: bool = True
    model: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.timeout <= 0:
            raise ValidationError("Task timeout must be greater than zero")
        if self.type == TaskType.EXEC and not self.command:
            raise ValidationError("EXEC task requires command")
        if self.type in {TaskType.SESSION_NEW, TaskType.SESSION_CLOSE, TaskType.STATUS} and not self.session_name:
            raise ValidationError(f"{self.type.value} task requires session_name")
        if self.type == TaskType.OMC:
            if not self.skill_name:
                raise ValidationError("OMC task requires skill_name")
            if not self.command:
                raise ValidationError("OMC task requires command")


@dataclass
class ExecutionResult:
    """Executor result payload."""

    success: bool
    output: str
    error: str
    exit_code: int
    started_at: str
    completed_at: str
    duration_ms: int
    executor_type: ExecutorType
    task_id: str | None = None
    session_id: str | None = None
    background_task_id: str | None = None
