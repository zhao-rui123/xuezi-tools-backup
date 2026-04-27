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


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _clean_message_text(text: str) -> str:
    cleaned = text
    if "Conversation info (untrusted metadata):" in cleaned and "[message_id:" in cleaned:
        cleaned = cleaned.split("[message_id:", 1)[1]
        if "]" in cleaned:
            cleaned = cleaned.split("]", 1)[1]
    cleaned = cleaned.split("[Bootstrap truncation warning]", 1)[0]
    cleaned = cleaned.replace("[[reply_to_current]]", "")
    cleaned = re.sub(r"```json.*?```", "", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"Sender \(untrusted metadata\):", "", cleaned)
    cleaned = re.sub(r"^ou_[a-z0-9]+:\s*", "", cleaned.strip())
    cleaned = _normalize_text(cleaned)
    if cleaned.startswith("/"):
        return ""
    return cleaned[:240]


def _is_control_like_message(text: str) -> bool:
    clean = _normalize_text(text)
    if clean.startswith("/"):
        return True
    lowered = clean.lower()
    if lowered in {"new", "reset"}:
        return True
    if "我要new" in clean or "我先new" in clean or "准备new" in clean:
        return True
    if "我要reset" in clean or "我先reset" in clean or "准备reset" in clean:
        return True
    if ":" in clean:
        tail = clean.rsplit(":", 1)[-1].strip()
        if tail.startswith("/"):
            return True
    return False


def _score_task_candidate(text: str) -> int:
    clean = _normalize_text(text)
    score = 0
    strong_markers = ("约定", "记住", "等于", "修复", "任务", "问题", "验证", "测试", "deepseek", "codex")
    weak_markers = ("继续", "处理", "整合", "恢复", "快照", "session", "上下文")
    casual_markers = ("哈哈", "验收", "朴实而无华", "去吧", "回来", "聊着")

    for marker in strong_markers:
        if marker.lower() in clean.lower():
            score += 4
    for marker in weak_markers:
        if marker.lower() in clean.lower():
            score += 2
    for marker in casual_markers:
        if marker in clean:
            score -= 3
    if _is_control_like_message(clean):
        score -= 10
    return score


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

    def add_task(text: str, prefix: str = "") -> None:
        clean = re.sub(r"\s+", " ", text).strip()
        if not clean:
            return
        if set(clean) <= {"-", "|", " "}:
            return
        if clean.startswith("合计 |") or clean.startswith("|"):
            return
        if len(clean) < 6:
            return
        candidate = (prefix + clean)[:120]
        if candidate not in tasks:
            tasks.append(candidate)

    recent_snapshot_task = _load_recent_snapshot_task()
    if recent_snapshot_task:
        add_task(recent_snapshot_task, "[快照] ")

    for item in re.findall(r"^##\s+(.+)$", content, re.MULTILINE)[-3:]:
        add_task(item, "[主题] ")

    # Prefer recent update blocks because they usually contain the active task.
    update_blocks = re.findall(
        r"### \[UPDATE\][^\n]*\n+(.+?)(?=\n###|\n##|\Z)",
        content,
        re.DOTALL,
    )
    for block in update_blocks[-3:]:
        lines = [line.strip().lstrip("-*").strip() for line in block.splitlines()]
        for line in lines:
            if line and not line.startswith("#"):
                add_task(line)
                break

    # Include recently completed checklist items.
    for item in re.findall(r"- \[x\] (.+)", content)[-3:]:
        add_task(item, "[完成] ")

    # Include active checklist items if no better task summary exists.
    if len(tasks) < 3:
        for item in re.findall(r"- \[ \] (.+)", content)[-3:]:
            add_task(item, "[待办] ")

    # Fall back to bold project markers when updates are sparse.
    for item in re.findall(r"\*\*.*?\*\*.*?(?:\n|$)", content)[-2:]:
        clean = re.sub(r"\*\*(.+?)\*\*", r"\1", item).strip()
        add_task(clean)

    summary = tasks[-1] if tasks else "无记录"
    return {
        "date": today,
        "summary": summary,
        "tasks": tasks[-5:],
        "task_count": len(tasks),
        "timestamp": datetime.now().isoformat(),
        "memory_file": str(memory_file),
    }


def _load_recent_snapshot_task() -> Optional[str]:
    snapshot_dir = MEMORY_DIR / "snapshots"
    if not snapshot_dir.exists():
        return None

    snapshot_files = sorted(
        snapshot_dir.glob("snapshot_*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for path in snapshot_files[:5]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        task = str(data.get("current_task", "")).strip()
        if task:
            return task
    return None


def _resolve_session_file(session_file: Optional[str], session_id: Optional[str] = None) -> Optional[Path]:
    if session_file:
        path = Path(session_file)
        if path.exists():
            return path

        reset_matches = sorted(
            path.parent.glob(f"{path.name}.reset.*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if reset_matches:
            return reset_matches[0]

    if session_id:
        reset_matches = sorted(
            SESSIONS_DIR.glob(f"{session_id}.jsonl.reset.*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if reset_matches:
            return reset_matches[0]

        direct = SESSIONS_DIR / f"{session_id}.jsonl"
        if direct.exists():
            return direct

    return None


def extract_tasks_from_session_file(session_file: str) -> dict:
    tasks: List[str] = []
    fallback_tasks: List[str] = []
    transcript: List[str] = []
    path = Path(session_file)
    if not path.exists():
        return {"summary": None, "tasks": [], "transcript": [], "task_count": 0}

    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue
            if entry.get("type") != "message":
                continue
            message = entry.get("message") or {}
            role = message.get("role")
            if role not in {"user", "assistant"}:
                continue
            content = message.get("content")
            text = ""
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text = item.get("text") or ""
                        break
            elif isinstance(content, str):
                text = content
            cleaned = _clean_message_text(text)
            if not cleaned:
                continue
            prefix = "user" if role == "user" else "assistant"
            transcript.append(f"{prefix}: {cleaned}")
            is_control = _is_control_like_message(cleaned)
            if role == "user":
                target = f"[用户] {cleaned[:120]}"
                if not is_control:
                    tasks.append(target)
            else:
                target = f"[助手] {cleaned[:120]}"
                if not is_control and any(
                    marker in cleaned for marker in ("我来", "整合", "方案", "搞定", "接下来", "修", "处理")
                ):
                    tasks.append(target)
                else:
                    fallback_tasks.append(target)
    except Exception:
        return {"summary": None, "tasks": [], "transcript": [], "task_count": 0}

    deduped_tasks: List[str] = []
    for task in tasks + fallback_tasks:
        if task not in deduped_tasks:
            deduped_tasks.append(task)

    summary = None
    best_score = -999
    for item in deduped_tasks:
        candidate = item.replace("[用户] ", "", 1).replace("[助手] ", "", 1)
        score = _score_task_candidate(candidate)
        if item.startswith("[用户] "):
            score += 1
        if score >= best_score:
            best_score = score
            summary = item
    if not summary and deduped_tasks:
        summary = deduped_tasks[-1]

    return {
        "summary": summary,
        "tasks": deduped_tasks[-6:],
        "transcript": transcript[-12:],
        "task_count": len(deduped_tasks),
    }


def save_snapshot(
    task: Optional[str] = None,
    session_file: Optional[str] = None,
    session_id: Optional[str] = None,
    session_key: Optional[str] = None,
) -> bool:
    """Persist today's snapshot into memory/YYYY-MM-DD.json."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    memory_info = extract_tasks_from_memory()
    resolved_session_file = _resolve_session_file(session_file, session_id=session_id)
    session_extract = extract_tasks_from_session_file(str(resolved_session_file)) if resolved_session_file else {
        "summary": None,
        "tasks": [],
        "transcript": [],
        "task_count": 0,
    }
    session_info = _get_current_session_info()
    ignored_manual_notes = {"未标注任务", "自动保存", "日常对话"}
    manual = task if task and task not in ignored_manual_notes else None
    summary = (
        manual
        or session_extract.get("summary")
        or memory_info.get("summary")
        or "无标注"
    )
    from_session = session_extract.get("tasks", [])
    from_memory = memory_info.get("tasks", [])
    captured_session_id = session_id or session_info.get("current_session_id")
    captured_session_key = session_key or session_info.get("current_session_key")
    data = {
        "date": _today(),
        "summary": summary,
        "manual_note": manual,
        "from_session": from_session,
        "from_memory": from_memory,
        "session_transcript": session_extract.get("transcript", []),
        "task_count": max(
            session_extract.get("task_count", 0),
            memory_info.get("task_count", 0),
        ),
        "timestamp": datetime.now().isoformat(),
        "current_session": captured_session_id,
        "current_session_key": captured_session_key,
        "previous_session": session_info.get("previous_session_id"),
        "reset_file": session_info.get("reset_file"),
        "source_session_file": str(resolved_session_file) if resolved_session_file else session_file,
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
        print("Usage: session-snapshot.py <save|load> [task] [--session-file PATH] [--session-id ID] [--session-key KEY]")
        raise SystemExit(1)

    action = sys.argv[1]
    if action == "save":
        task = "未标注任务"
        session_file = None
        session_id = None
        session_key = None
        idx = 2
        if idx < len(sys.argv) and not sys.argv[idx].startswith("--"):
            task = sys.argv[idx]
            idx += 1
        while idx < len(sys.argv):
            arg = sys.argv[idx]
            if arg == "--session-file" and idx + 1 < len(sys.argv):
                session_file = sys.argv[idx + 1]
                idx += 2
            elif arg == "--session-id" and idx + 1 < len(sys.argv):
                session_id = sys.argv[idx + 1]
                idx += 2
            elif arg == "--session-key" and idx + 1 < len(sys.argv):
                session_key = sys.argv[idx + 1]
                idx += 2
            else:
                idx += 1
        save_snapshot(task, session_file=session_file, session_id=session_id, session_key=session_key)
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
