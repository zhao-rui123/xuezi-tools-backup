"""SQLite persistence for local task metadata."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from ..config import defaults
from ..core.models import ExecutionResult, Task, TaskStatus
from ..exceptions import StoreError


class BackgroundTaskStore:
    """Persist submitted task metadata for later inspection."""

    def __init__(self, db_path: str = defaults.BACKGROUND_DB_PATH):
        self.db_path = Path(os.path.expanduser(db_path))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    executor TEXT NOT NULL,
                    command TEXT,
                    session_name TEXT,
                    skill_name TEXT,
                    no_wait INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    output TEXT,
                    error TEXT,
                    exit_code INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def upsert(self, task: Task, status: TaskStatus, result: ExecutionResult) -> None:
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO tasks (
                        id, type, executor, command, session_name, skill_name,
                        no_wait, status, output, error, exit_code, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        status = excluded.status,
                        output = excluded.output,
                        error = excluded.error,
                        exit_code = excluded.exit_code,
                        updated_at = excluded.updated_at
                    """,
                    (
                        task.id,
                        task.type.value,
                        task.executor.value,
                        task.command,
                        task.session_name,
                        task.skill_name,
                        int(task.no_wait),
                        status.value,
                        result.output,
                        result.error,
                        result.exit_code,
                        task.created_at,
                        result.completed_at,
                    ),
                )
        except sqlite3.Error as exc:  # pragma: no cover
            raise StoreError(str(exc)) from exc

    def get(self, task_id: str) -> dict[str, object] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return dict(row) if row else None

    def list_recent(self, limit: int = 20) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM tasks ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]
