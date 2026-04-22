#!/usr/bin/env python3
"""
Session snapshot helper for OpenClaw startup and /new recovery.

This file restores the canonical path expected by legacy scripts:
  ~/.openclaw/workspace/scripts/session-snapshot.py
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional


WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE_DIR / "memory"
SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "claude" / "sessions"
SESSION_INDEX = SESSIONS_DIR / "sessions.json"


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _snapshot_file(date_str: Optional[str] = None) -> Path:
    return MEMORY_DIR / f"{date_str or _today()}.json"


def _get_current_session_info() -> dict:
    """Get current and previous session IDs from sessions.json."""
    info = {
        "current_session_id": None,
        "current_session_key": None,
        "previous_session_id": None,
        "reset_file": None,
    }

    if not SESSION_INDEX.exists():
        return info

    try:
        # sessions.json is a regular JSON object keyed by sessionKey
        with open(SESSION_INDEX, encoding="utf-8") as f:
            data = json.load(f)

        # Current session
        current_key = "agent:claude:main"
        if current_key in data:
            info["current_session_id"] = data[current_key].get("sessionId")
            info["current_session_key"] = current_key

        # Find a previous main session (different from current)
        current_id = info["current_session_id"]
        for key, val in data.items():
            sid = val.get("sessionId", "") if isinstance(val, dict) else ""
            if sid and sid != current_id and "subagent" not in key:
                info["previous_session_id"] = sid
                info["previous_session_key"] = key
                break

        # Find reset file for current session
        if current_id:
            reset_files = sorted(
                SESSIONS_DIR.glob(f"{current_id}*.reset*"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if reset_files:
                info["reset_file"] = str(reset_files[0])

        return info
    except Exception as e:
        return info


def extract_tasks_from_memory() -> dict:
    """Extract a lightweight summary from today's memory markdown."""
    today = _today()
    memory_file = MEMORY_DIR / f"{today}.md"

    if not memory_file.exists():
        return {
            "date": today,
            "tasks": [],
            "summary": "无记忆文件",
            "task_count": 0,
            "timestamp": datetime.now().isoformat(),
            "memory_file": str(memory_file),
        }

    content = memory_file.read_text(encoding="utf-8")
    tasks: List[str] = []

    # Prefer recent update blocks because they usually contain the active task.
    update_blocks = re.findall(
        r"### \[UPDATE\][^\n]*\n+(.+?)(?=\n###|\n##|\Z)",
        content,
        re.DOTALL,
    )
    for block in update_blocks[-3:]:
        lines = [line.strip().lstrip("-*").strip() for line in block.splitlines()]
        for line in lines:
            if len(line) > 5:
                tasks.append(line[:120])
                break

    # Include recently completed checklist items.
    for item in re.findall(r"- \[x\] (.+)", content)[-3:]:
        tasks.append("[完成] " + item[:100])

    # Fall back to bold project markers when updates are sparse.
    for item in re.findall(r"\*\*.*?\*\*.*?(?:\n|$)", content)[-2:]:
        clean = re.sub(r"\*\*(.+?)\*\*", r"\1", item).strip()
        if len(clean) > 5:
            tasks.append(clean[:120])

    summary = tasks[-1] if tasks else "无记录"
    return {
        "date": today,
        "summary": summary,
        "tasks": tasks[-5:],
        "task_count": len(tasks),
        "timestamp": datetime.now().isoformat(),
        "memory_file": str(memory_file),
    }


def save_snapshot(task: Optional[str] = None) -> bool:
    """Persist today's snapshot into memory/YYYY-MM-DD.json."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    info = extract_tasks_from_memory()
    session_info = _get_current_session_info()
    manual = task if task and task != "未标注任务" else None
    data = {
        "date": _today(),
        "summary": manual or info.get("summary", "无标注"),
        "manual_note": manual,
        "from_memory": info.get("tasks", []),
        "task_count": info.get("task_count", 0),
        "timestamp": datetime.now().isoformat(),
        "current_session": session_info.get("current_session_id"),
        "current_session_key": session_info.get("current_session_key"),
        "previous_session": session_info.get("previous_session_id"),
        "reset_file": session_info.get("reset_file"),
    }
    data = {key: value for key, value in data.items() if value not in (None, [])}

    _snapshot_file().write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"已保存: {data.get('summary', '')[:60]}")
    if session_info.get("current_session_id"):
        print(f"  session: {session_info['current_session_id'][:20]}...")
    if session_info.get("reset_file"):
        print(f"  reset文件: {Path(session_info['reset_file']).name}")
    return True


def load_snapshot() -> Optional[dict]:
    """Load today's snapshot first, otherwise fall back to the most recent one."""
    today_file = _snapshot_file()
    if today_file.exists():
        data = json.loads(today_file.read_text(encoding="utf-8"))
        print(f"恢复今日 ({_today()}): {data.get('summary', '无描述')[:80]}")
        if data.get("from_memory"):
            print(f"  记忆文件任务数: {data.get('task_count', 0)}")
        if data.get("current_session"):
            print(f"  session: {data['current_session'][:20]}...")
        if data.get("reset_file"):
            print(f"  旧session reset: {Path(data['reset_file']).name}")
        return data

    snapshot_files = sorted(
        MEMORY_DIR.glob("????-??-??.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for path in snapshot_files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        print(f"恢复: {data.get('date', path.stem)} - {data.get('summary', '无描述')[:60]}")
        return data

    print("无快照，尝试从记忆文件恢复...")
    info = extract_tasks_from_memory()
    if info.get("tasks"):
        print(f"从记忆文件恢复了 {len(info['tasks'])} 条任务")
        return info
    return None


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: session-snapshot.py <save|load> [task]")
        raise SystemExit(1)

    action = sys.argv[1]
    if action == "save":
        task = sys.argv[2] if len(sys.argv) > 2 else "未标注任务"
        save_snapshot(task)
        return

    if action == "load":
        result = load_snapshot()
        if result:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"Unknown action: {action}")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
