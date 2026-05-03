#!/usr/bin/env python3
"""
Safely switch OpenClaw models.

For DeepSeek targets, save a session snapshot and rotate the main session so the
next incoming message starts from a clean session while BOOTSTRAP restores the
summary context.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict


HOME = Path.home()
WORKSPACE = HOME / ".openclaw" / "workspace"
SESSIONS_DIR = HOME / ".openclaw" / "agents" / "claude" / "sessions"
SESSIONS_INDEX = SESSIONS_DIR / "sessions.json"
SNAPSHOT_SCRIPT = WORKSPACE / "scripts" / "session-snapshot.py"
MAIN_SESSION_KEY = "agent:claude:main"

MODELS: Dict[str, str] = {
    "mini": "minimax-cn/MiniMax-M2.7",
    "minimax": "minimax-cn/MiniMax-M2.7",
    "k2.5": "bailian/kimi-k2.5",
    "kimi": "bailian/kimi-k2.5",
    "qwen": "bailian/qwen3.5-plus",
    "code": "kimi-coding/kimi-for-coding",
    "coding": "kimi-coding/kimi-for-coding",
    "deepseek": "deepseek/deepseek-v4-flash",
    "ds": "deepseek/deepseek-v4-flash",
}


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def should_rotate_session(model_name: str) -> bool:
    return model_name.startswith("deepseek/")


def save_snapshot(note: str) -> None:
    if not SNAPSHOT_SCRIPT.exists():
        raise RuntimeError(f"snapshot script not found: {SNAPSHOT_SCRIPT}")
    result = run(["python3", str(SNAPSHOT_SCRIPT), "save", note])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "snapshot save failed")


def rotate_main_session() -> str:
    if not SESSIONS_INDEX.exists():
        raise RuntimeError(f"sessions index not found: {SESSIONS_INDEX}")

    with open(SESSIONS_INDEX, encoding="utf-8") as f:
        data = json.load(f)

    session = data.get(MAIN_SESSION_KEY)
    if not isinstance(session, dict):
        raise RuntimeError(f"session key not found: {MAIN_SESSION_KEY}")

    old_session_id = session.get("sessionId")
    old_session_file = session.get("sessionFile")
    if not old_session_id or not old_session_file:
        raise RuntimeError("current main session is missing session metadata")

    old_path = Path(old_session_file)
    if old_path.exists():
        stamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        reset_path = old_path.with_name(f"{old_path.stem}.jsonl.reset.{stamp}")
        shutil.move(str(old_path), str(reset_path))

    new_session_id = str(uuid.uuid4())
    session["sessionId"] = new_session_id
    session["updatedAt"] = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
    session["sessionFile"] = str(SESSIONS_DIR / f"{new_session_id}.jsonl")
    session["systemSent"] = False
    session["abortedLastRun"] = False
    session["compactionCount"] = 0

    with open(SESSIONS_INDEX, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return new_session_id


def switch_model(model_name: str) -> None:
    result = run(["openclaw", "models", "set", model_name])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "model switch failed")


def restart_gateway() -> None:
    if sys.platform == "darwin":
        label = "ai.openclaw.gateway"
        plist_path = HOME / "Library" / "LaunchAgents" / f"{label}.plist"
        if plist_path.exists():
            target = f"gui/{os.getuid()}/{label}"
            result = run(["launchctl", "kickstart", "-k", target])
            if result.returncode == 0:
                return
    result = run(["openclaw", "gateway", "restart"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "gateway restart failed")


def normalize_target(raw: str) -> str:
    key = raw.strip().lower()
    if key in MODELS:
        return MODELS[key]
    return raw.strip()


def model_display(alias: str) -> str:
    mapping = {
        "deepseek": "DeepSeek / V4 Flash",
        "minimax": "MiniMax / M2.7",
        "mini": "MiniMax / M2.7",
        "kimi": "Kimi / K2.5",
        "k2.5": "Kimi / K2.5",
        "qwen": "Qwen / 3.5 Plus",
        "code": "Kimi Coding",
        "coding": "Kimi Coding",
    }
    return mapping.get(alias, alias)


def show_status() -> int:
    result = run(["openclaw", "config", "get", "agents.defaults.model.primary"])
    if result.returncode != 0:
        print(result.stderr.strip() or result.stdout.strip() or "无法读取当前模型", file=sys.stderr)
        return 1
    print(f"当前模型: {result.stdout.strip()}")
    print("可用别名: " + ", ".join(sorted(MODELS)))
    return 0


def main(argv: list[str]) -> int:
    if not argv or argv[0] in {"status", "--status"}:
        return show_status()

    target = normalize_target(argv[0])
    rotated = False
    new_session_id = ""

    if should_rotate_session(target):
        save_snapshot(f"切换到 {target} 前自动保存")
        new_session_id = rotate_main_session()
        rotated = True

    switch_model(target)
    restart_gateway()
    subprocess.run([
        "bash",
        str(Path.home() / ".openclaw" / "workspace" / "scripts" / "refresh-cockpit-cards.sh"),
        "models",
    ], env={**os.environ, "CURRENT_MODEL": model_display(target)}, check=False, capture_output=True, text=True)

    print(f"已切换到 {target}")
    if rotated:
        print("已自动保存快照并重置主会话")
        print(f"新主会话 ID: {new_session_id}")
        print("下一条消息会按 BOOTSTRAP 自动恢复快照摘要，不会带入旧的 reasoning 历史")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except RuntimeError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        raise SystemExit(1)
