#!/usr/bin/env python3
"""
实时记忆记录器
每次对话后自动追加到 memory/YYYY-MM-DD.md
"""
import json
import sys
from datetime import datetime
from pathlib import Path

def log_conversation(user_msg, ai_response, topic=""):
    """记录对话到每日记忆文件"""
    memory_dir = Path.home() / ".openclaw" / "workspace" / "memory"
    memory_dir.mkdir(exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = memory_dir / f"{today}.md"
    
    # 读取现有内容或创建新文件
    if memory_file.exists():
        content = memory_file.read_text(encoding='utf-8')
    else:
        content = f"# {today} 记忆日志\n\n"
    
    # 追加新对话
    time_str = datetime.now().strftime("%H:%M")
    new_entry = f"\n## {time_str}\n"
    if topic:
        new_entry += f"**主题**: {topic}\n\n"
    new_entry += f"**用户**: {user_msg}\n\n"
    new_entry += f"**助手**: {ai_response}\n"
    
    # 写入文件
    memory_file.write_text(content + new_entry, encoding='utf-8')
    print(f"✅ 已记录到 {memory_file}")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        user_msg = sys.argv[1]
        ai_response = sys.argv[2]
        topic = sys.argv[3] if len(sys.argv) > 3 else ""
        log_conversation(user_msg, ai_response, topic)
    else:
        print("Usage: memory_logger.py '用户消息' '助手回复' [主题]")
