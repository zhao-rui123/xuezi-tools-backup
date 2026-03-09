#!/usr/bin/env python3
"""
OpenClaw 深度集成模块
自动追踪每个会话的工作状态
"""

import sys
import json
import os
import time
from datetime import datetime
from pathlib import Path

# 添加tracker路径
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace/agent-dashboard-v2')

try:
    from tracker import start_task, complete_task, add_tokens, switch_status, get_current_room
    TRACKER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ tracker导入失败: {e}")
    TRACKER_AVAILABLE = False

# 会话状态文件
SESSION_FILE = '/Users/zhaoruicn/.openclaw/workspace/agent-dashboard-v2/data/current_session.json'

class OpenClawIntegration:
    """OpenClaw集成类"""
    
    def __init__(self):
        self.session_start = None
        self.task_name = None
        self.tokens_used = 0
        self.tool_calls = 0
        
    def start_session(self, task_name: str = None):
        """会话开始"""
        if not TRACKER_AVAILABLE:
            return
            
        self.session_start = datetime.now()
        self.task_name = task_name or f"会话_{datetime.now().strftime('%H:%M')}"
        self.tokens_used = 0
        self.tool_calls = 0
        
        # 通知tracker开始任务
        room = start_task(self.task_name)
        
        # 保存会话状态
        self._save_session_state()
        
        print(f"🦞 [OpenClaw] 会话开始: {self.task_name}")
        print(f"🦞 [OpenClaw] 小龙虾去了: {room}")
        
    def record_tool_call(self, tool_name: str, tokens: int = 0):
        """记录工具调用"""
        if not TRACKER_AVAILABLE:
            return
            
        self.tool_calls += 1
        self.tokens_used += tokens
        
        # 每10个工具调用保存一次
        if self.tool_calls % 10 == 0:
            add_tokens(tokens)
            self._save_session_state()
            
    def end_session(self, success: bool = True):
        """会话结束"""
        if not TRACKER_AVAILABLE:
            return
            
        if not self.session_start:
            return
            
        duration = (datetime.now() - self.session_start).total_seconds()
        
        # 通知tracker完成任务
        room = complete_task(tokens_used=self.tokens_used, success=success)
        
        # 清理会话状态
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        
        print(f"🦞 [OpenClaw] 会话结束")
        print(f"🦞 [OpenClaw] 耗时: {int(duration)}秒")
        print(f"🦞 [OpenClaw] Tokens: {self.tokens_used}")
        print(f"🦞 [OpenClaw] 小龙虾去了: {room}")
        
        self.session_start = None
        self.task_name = None
        self.tokens_used = 0
        self.tool_calls = 0
        
    def _save_session_state(self):
        """保存会话状态"""
        try:
            state = {
                'session_start': self.session_start.isoformat() if self.session_start else None,
                'task_name': self.task_name,
                'tokens_used': self.tokens_used,
                'tool_calls': self.tool_calls,
                'updated_at': datetime.now().isoformat()
            }
            with open(SESSION_FILE, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            print(f"保存会话状态失败: {e}")


# 全局实例
_integration = None

def get_integration() -> OpenClawIntegration:
    """获取集成实例"""
    global _integration
    if _integration is None:
        _integration = OpenClawIntegration()
    return _integration

# 便捷API
def session_start(task_name: str = None):
    """会话开始"""
    return get_integration().start_session(task_name)

def session_end(success: bool = True):
    """会话结束"""
    return get_integration().end_session(success)

def record_tool(tool_name: str, tokens: int = 0):
    """记录工具调用"""
    return get_integration().record_tool_call(tool_name, tokens)


# 如果直接运行
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == 'start':
            task = sys.argv[2] if len(sys.argv) > 2 else 'OpenClaw会话'
            session_start(task)
        elif cmd == 'end':
            session_end()
        elif cmd == 'tool':
            tool = sys.argv[2] if len(sys.argv) > 2 else 'unknown'
            tokens = int(sys.argv[3]) if len(sys.argv) > 3 else 0
            record_tool(tool, tokens)
        else:
            print("用法:")
            print("  python3 openclaw_integration.py start '任务名'")
            print("  python3 openclaw_integration.py end")
            print("  python3 openclaw_integration.py tool '工具名' 100")
    else:
        # 测试
        print("🦞 OpenClaw集成模块测试")
        session_start("测试任务")
        time.sleep(2)
        record_tool("web_search", 500)
        time.sleep(1)
        session_end()
