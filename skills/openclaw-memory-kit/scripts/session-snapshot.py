#!/usr/bin/env python3
"""
会话快照工具 - 增强版
自动保存对话上下文，支持急救恢复
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 快照目录
SNAPSHOT_DIR = Path.home() / ".openclaw" / "workspace" / "memory" / "snapshots"
CURRENT_SNAPSHOT = SNAPSHOT_DIR / "current_session.json"

def ensure_dir():
    """确保目录存在"""
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

def save_snapshot(task="", pending=None, context=None, last_messages=None):
    """
    保存会话快照
    
    Args:
        task: 当前进行中的任务
        pending: 待办事项列表
        context: 关键上下文字典
        last_messages: 最近几条消息（可选）
    """
    ensure_dir()
    
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "session_key": "agent:main:main",
        "current_task": task,
        "pending_items": pending or [],
        "key_context": context or {},
        "last_messages": last_messages or [],
        "recovery_phrase": generate_recovery_phrase(task, pending)
    }
    
    # 保存当前快照
    with open(CURRENT_SNAPSHOT, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    
    # 同时保存历史快照
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_file = SNAPSHOT_DIR / f"session_{timestamp}.json"
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    
    # 清理旧快照（保留最近20个）
    cleanup_old_snapshots(keep=20)
    
    return str(CURRENT_SNAPSHOT)

def generate_recovery_phrase(task, pending):
    """生成急救口令关键词"""
    keywords = []
    
    if task:
        # 提取任务关键词（前10个字符）
        keywords.append(task[:20])
    
    if pending:
        keywords.extend([item[:15] for item in pending[:3]])
    
    return " | ".join(keywords) if keywords else "继续之前的工作"

def get_latest_snapshot():
    """获取最新快照"""
    if CURRENT_SNAPSHOT.exists():
        with open(CURRENT_SNAPSHOT, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def cleanup_old_snapshots(keep=20):
    """清理旧快照"""
    snapshots = sorted(SNAPSHOT_DIR.glob("session_*.json"), reverse=True)
    for old_snap in snapshots[keep:]:
        old_snap.unlink()

def generate_recovery_card():
    """生成恢复卡片，用于 MEMORY.md"""
    snap = get_latest_snapshot()
    
    if not snap:
        return "# 没有可用的会话快照"
    
    lines = [
        "# 🚨 会话恢复卡片",
        "",
        f"**最后更新**: {snap.get('timestamp', 'unknown')}",
        f"**急救口令**: `{snap.get('recovery_phrase', '继续之前的工作')}`",
        "",
        "## 当前任务",
        f"{snap.get('current_task', '无')}",
        "",
    ]
    
    if snap.get('pending_items'):
        lines.extend([
            "## 待办事项",
            *[f"- [ ] {item}" for item in snap['pending_items']],
            "",
        ])
    
    if snap.get('key_context'):
        lines.extend([
            "## 关键上下文",
            *[f"- **{k}**: {v}" for k, v in snap['key_context'].items()],
            "",
        ])
    
    lines.extend([
        "---",
        "**恢复方法**: 新会话时说急救口令即可",
    ])
    
    return "\n".join(lines)

def quick_save(task=""):
    """快速保存 - 用于定时自动保存"""
    save_snapshot(
        task=task,
        pending=[],
        context={}
    )
    print(f"✅ 会话已保存: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: session-snapshot.py <save|load|card> [task]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "save":
        task = sys.argv[2] if len(sys.argv) > 2 else ""
        quick_save(task)
    
    elif action == "load":
        snap = get_latest_snapshot()
        if snap:
            print(json.dumps(snap, ensure_ascii=False, indent=2))
        else:
            print("{}")
    
    elif action == "card":
        print(generate_recovery_card())
    
    else:
        print(f"Unknown action: {action}")