#!/usr/bin/env python3
"""
OpenClaw会话自动追踪钩子
在每次会话开始和结束时自动调用
"""

import sys
import os
import atexit
from datetime import datetime

# 添加路径
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace/agent-dashboard-v2')

try:
    from openclaw_integration import session_start, session_end, record_tool
    from tracker import get_tracker
    ENABLED = True
except ImportError as e:
    print(f"[LobsterTracker] 导入失败: {e}")
    ENABLED = False

class SessionTracker:
    """会话追踪器"""
    
    def __init__(self):
        self.session_active = False
        self.start_time = None
        
    def on_session_start(self, task_hint: str = None):
        """会话开始钩子"""
        if not ENABLED:
            return
            
        # 生成任务名
        if task_hint:
            task_name = task_hint
        else:
            # 从环境或默认
            task_name = f"会话_{datetime.now().strftime('%H:%M')}"
        
        self.start_time = datetime.now()
        self.session_active = True
        
        # 启动追踪
        session_start(task_name)
        
        # 注册退出钩子
        atexit.register(self.on_session_end)
        
        print(f"\n🦞 [小龙虾追踪] 会话已记录: {task_name}\n")
        
    def on_session_end(self):
        """会话结束钩子"""
        if not ENABLED or not self.session_active:
            return
            
        self.session_active = False
        
        # 计算耗时
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
        else:
            duration = 0
        
        # 结束追踪
        session_end(success=True)
        
        print(f"\n🦞 [小龙虾追踪] 会话结束，耗时 {int(duration)}秒\n")
        
    def on_tool_executed(self, tool_name: str, tokens: int = 0):
        """工具执行钩子"""
        if not ENABLED or not self.session_active:
            return
            
        record_tool(tool_name, tokens)


# 创建全局实例
tracker = SessionTracker()

# 导出函数
start_tracking = tracker.on_session_start
end_tracking = tracker.on_session_end
track_tool = tracker.on_tool_executed

# 自动启动（如果作为模块导入）
if __name__ != '__main__':
    # 检查是否有会话提示
    import os
    task_hint = os.environ.get('LOBSTER_TASK')
    if task_hint:
        start_tracking(task_hint)
