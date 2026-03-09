#!/usr/bin/env python3
"""
会话恢复检测器
检测用户输入是否包含急救口令，如果是，返回恢复提示
"""

import json
import sys
from pathlib import Path

SNAPSHOT_FILE = Path.home() / ".openclaw" / "workspace" / "memory" / "snapshots" / "current_session.json"

RECOVERY_PHRASES = [
    "继续之前的工作",
    "继续刚才的",
    "恢复会话",
    "我是雪子",
    "继续修复定时任务",
    "继续模型测试",
    "继续备份",
    "继续股票分析",
    "继续储能测算",
]

def detect_recovery_intent(user_message):
    """检测用户是否有恢复会话的意图"""
    msg = user_message.lower()
    
    for phrase in RECOVERY_PHRASES:
        if phrase.lower() in msg:
            return True
    
    # 检测其他恢复信号
    recovery_signals = [
        "刚才",
        "之前",
        "上午",
        "昨天",
        "之前聊",
        "我们说",
    ]
    
    for signal in recovery_signals:
        if signal in msg and ("聊" in msg or "说" in msg or "做" in msg):
            return True
    
    return False

def get_recovery_context():
    """获取恢复上下文"""
    if not SNAPSHOT_FILE.exists():
        return None
    
    try:
        with open(SNAPSHOT_FILE, 'r', encoding='utf-8') as f:
            snapshot = json.load(f)
        
        context_parts = []
        
        if snapshot.get('current_task'):
            context_parts.append(f"📋 当前任务: {snapshot['current_task']}")
        
        if snapshot.get('pending_items'):
            context_parts.append("📌 待办事项:")
            for item in snapshot['pending_items']:
                context_parts.append(f"  - {item}")
        
        if snapshot.get('key_context'):
            context_parts.append("💡 关键上下文:")
            for k, v in snapshot['key_context'].items():
                context_parts.append(f"  - {k}: {v}")
        
        if snapshot.get('last_messages') and len(snapshot['last_messages']) >= 2:
            context_parts.append("\n💬 最近对话:")
            for msg in snapshot['last_messages'][-4:]:
                context_parts.append(f"  {msg}")
        
        return "\n".join(context_parts) if context_parts else None
        
    except Exception as e:
        print(f"Error loading snapshot: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: recovery-detector.py '<user message>'")
        sys.exit(1)
    
    user_message = sys.argv[1]
    
    if detect_recovery_intent(user_message):
        context = get_recovery_context()
        if context:
            print(f"检测到恢复意图！\n\n{context}")
        else:
            print("检测到恢复意图，但没有可用的会话快照")
    else:
        print("NO_RECOVERY")