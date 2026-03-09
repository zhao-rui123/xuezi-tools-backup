#!/usr/bin/env python3
"""
自动会话保存守护进程 - 统一记忆系统整合版
每5分钟自动保存当前会话状态到 unified-memory
"""
import json
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
SESSION_STATE_DIR = MEMORY_DIR / "session_states"
CURRENT_STATE_FILE = SESSION_STATE_DIR / "current_session.json"

def auto_save():
    """自动保存 - 保存到 unified-memory 的路径"""
    SESSION_STATE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 读取现有状态（如果有）
    state = {}
    if CURRENT_STATE_FILE.exists():
        try:
            with open(CURRENT_STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
        except:
            state = {}
    
    # 构建 unified-memory 格式的上下文
    context = state.get("context", {})
    context.update({
        "auto_saved_at": datetime.now().isoformat(),
        "has_unfinished_work": True,
        "timestamp": datetime.now().isoformat()
    })
    
    # 保留之前的任务信息
    if not context.get("current_task"):
        context["current_task"] = "自动保存 - 用户可能卡死前的工作"
    
    # unified-memory 格式的状态
    new_state = {
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "context": context,
        "has_unfinished_work": True,
        "pending_tasks": state.get("context", {}).get("pending_tasks", []),
        "current_project": state.get("context", {}).get("current_project", ""),
        "last_query": state.get("context", {}).get("last_query", "")
    }
    
    # 保存到 unified-memory 的路径
    with open(CURRENT_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_state, f, ensure_ascii=False, indent=2)
    
    print(f"[{datetime.now().strftime('%H:%M')}] 自动保存完成 (unified-memory)")

if __name__ == '__main__':
    auto_save()
