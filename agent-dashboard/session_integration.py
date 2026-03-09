#!/usr/bin/env python3
"""
OpenClaw 会话集成模块
在每次会话中自动记录任务状态和token消耗
"""

import sys
import os
import json
from datetime import datetime

# 添加追踪器路径
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace/agent-dashboard')

try:
    from status_tracker import start_task, complete_task, add_tokens, get_status
    TRACKER_AVAILABLE = True
except ImportError:
    TRACKER_AVAILABLE = False
    print("⚠️ 状态追踪器未安装")

# 会话状态文件
SESSION_STATE_FILE = '/Users/zhaoruicn/.openclaw/workspace/agent-dashboard/data/session_state.json'

def record_session_start(task_name: str = None):
    """记录会话开始"""
    if not TRACKER_AVAILABLE:
        return
    
    if task_name is None:
        task_name = f"会话_{datetime.now().strftime('%H:%M')}"
    
    start_task(task_name)
    
    # 保存会话状态
    state = {
        'session_start': datetime.now().isoformat(),
        'task_name': task_name,
        'status': 'working'
    }
    with open(SESSION_STATE_FILE, 'w') as f:
        json.dump(state, f)
    
    print(f"🦞 已记录会话开始: {task_name}")

def record_session_end(tokens_used: int = 0):
    """记录会话结束"""
    if not TRACKER_AVAILABLE:
        return
    
    complete_task(tokens_used)
    
    # 清理会话状态
    if os.path.exists(SESSION_STATE_FILE):
        os.remove(SESSION_STATE_FILE)
    
    print(f"🦞 已记录会话结束，消耗 {tokens_used} tokens")

def get_current_session_status():
    """获取当前会话状态"""
    if not TRACKER_AVAILABLE:
        return None
    
    return get_status()

# 如果直接运行此脚本，显示当前状态
if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'start' and len(sys.argv) > 2:
            record_session_start(sys.argv[2])
        elif command == 'end' and len(sys.argv) > 2:
            record_session_end(int(sys.argv[2]))
        elif command == 'status':
            status = get_current_session_status()
            if status:
                print(json.dumps(status, ensure_ascii=False, indent=2))
            else:
                print("无法获取状态")
        else:
            print("用法: python3 session_integration.py [start|end|status] [任务名|tokens]")
    else:
        # 显示当前状态
        status = get_current_session_status()
        if status:
            print("🦞 当前状态:")
            print(f"   状态: {status['status']}")
            print(f"   任务: {status['current_task'] or '无'}")
            print(f"   今日完成: {status['tasks_completed']} 个任务")
            print(f"   Token消耗: {status['tokens_used']}")
            print(f"   工作时长: {status['work_time_formatted']}")
        else:
            print("🦞 状态追踪器未运行")
            print("   请先运行: ./start-tracker.sh")
