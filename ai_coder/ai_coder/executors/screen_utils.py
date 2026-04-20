"""Helpers for detached screen-based task execution."""

from __future__ import annotations

import json
import os
import shlex
from dataclasses import dataclass


def _safe_name(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in value)
    return cleaned[:64] or "task"


@dataclass(frozen=True)
class ScreenArtifacts:
    """Filesystem locations used to track a detached screen task."""

    task_id: str
    runtime_kind: str
    root_dir: str
    session_name: str
    stdout_path: str
    stderr_path: str
    exit_code_path: str
    done_path: str
    meta_path: str

    @classmethod
    def for_task(cls, base_dir: str, task_id: str, runtime_kind: str) -> "ScreenArtifacts":
        root_dir = os.path.join(os.path.expanduser(base_dir), runtime_kind, task_id)
        session_name = _safe_name(f"ai-coder-{runtime_kind}-{task_id[:12]}")
        return cls(
            task_id=task_id,
            runtime_kind=runtime_kind,
            root_dir=root_dir,
            session_name=session_name,
            stdout_path=os.path.join(root_dir, "stdout.log"),
            stderr_path=os.path.join(root_dir, "stderr.log"),
            exit_code_path=os.path.join(root_dir, "exit_code"),
            done_path=os.path.join(root_dir, "done"),
            meta_path=os.path.join(root_dir, "meta.json"),
        )


def build_screen_command(
    *,
    artifacts: ScreenArtifacts,
    workdir: str,
    command: str,
    preamble: str | None = None,
) -> list[str]:
    """Build a detached screen launch command that records output to files."""

    parts = [
        "set -e",
        f"mkdir -p {shlex.quote(artifacts.root_dir)}",
        f": > {shlex.quote(artifacts.stdout_path)}",
        f": > {shlex.quote(artifacts.stderr_path)}",
        f"rm -f {shlex.quote(artifacts.exit_code_path)} {shlex.quote(artifacts.done_path)}",
        f"cd {shlex.quote(os.path.expanduser(workdir))}",
    ]
    if preamble:
        parts.append(preamble)
    parts.extend(
        [
            "set +e",
            f"{command} >> {shlex.quote(artifacts.stdout_path)} 2>> {shlex.quote(artifacts.stderr_path)}",
            'status="$?"',
            f'printf "%s\\n" "$status" > {shlex.quote(artifacts.exit_code_path)}',
            f'date -u +"%Y-%m-%dT%H:%M:%SZ" > {shlex.quote(artifacts.done_path)}',
            "exit 0",
        ]
    )
    script = "; ".join(parts)
    return ["screen", "-dmS", artifacts.session_name, "bash", "-lc", script]


def dump_meta(artifacts: ScreenArtifacts, payload: dict[str, object]) -> None:
    os.makedirs(artifacts.root_dir, exist_ok=True)
    with open(artifacts.meta_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
