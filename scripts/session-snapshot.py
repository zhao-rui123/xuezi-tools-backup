#!/usr/bin/env python3
"""
会话快照工具 - 统一记忆系统整合版
调用 unified-memory/session_recovery.py 的 API
"""
import json
import sys
from pathlib import Path

# 添加 unified-memory 路径
UMS_DIR = Path.home() / ".openclaw" / "workspace" / "skills" / "unified-memory"
sys.path.insert(0, str(UMS_DIR))

from session_recovery import SessionRecovery, on_session_start, on_session_end

def main():
    if len(sys.argv) < 2:
        print("Usage: session-snapshot.py <save|load> [task]")
        sys.exit(1)
    
    action = sys.argv[1]
    task = sys.argv[2] if len(sys.argv) > 2 else ""
    
    if action == "save":
        # 使用 unified-memory 的 API
        context = {
            "current_task": task,
            "has_unfinished_work": bool(task),
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        recovery = SessionRecovery()
        recovery.save_session_state(context)
        print(f"✅ 已保存到 unified-memory: {task}")
    
    elif action == "load":
        # 使用 unified-memory 的 API
        prompt = on_session_start()
        if prompt:
            print(json.dumps({
                "recovered": True,
                "prompt": prompt
            }, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"recovered": False}, indent=2))
    
    elif action == "card":
        # 生成恢复卡片
        recovery = SessionRecovery()
        state = recovery.check_last_session()
        if state:
            print(recovery.generate_recovery_prompt(state))
        else:
            print("# 没有可用的会话状态")
    
    else:
        print(f"Unknown action: {action}")

if __name__ == "__main__":
    main()
