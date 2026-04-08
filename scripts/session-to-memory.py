#!/usr/bin/env python3
"""从session提取对话写入每日记忆文件"""
import json
import re
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "claude" / "sessions"
TODAY = datetime.now().strftime("%Y-%m-%d")
TIME = datetime.now().strftime("%H:%M")

def find_main_session():
    """找到main session文件"""
    sessions_json = SESSIONS_DIR / "sessions.json"
    if sessions_json.exists():
        content = sessions_json.read_text()
        import re as re_mod
        match = re_mod.search(r'"agent:claude:main"[^}]*"sessionId":\s*"([^"]+)"', content)
        if match:
            session_id = match.group(1)
            for f in SESSIONS_DIR.glob("*.jsonl"):
                if f.stat().st_size > 0 and session_id in f.read_text()[:500]:
                    return f
    # 兜底：最新的jsonl
    files = sorted(SESSIONS_DIR.glob("*.jsonl"), key=lambda x: x.stat().st_mtime, reverse=True)
    for f in files:
        if not str(f).endswith('.lock'):
            return f
    return None

def extract_conversations(session_file):
    """提取对话"""
    messages = []
    with open(session_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                obj = json.loads(line.strip())
                if obj.get('type') == 'message':
                    msg = obj.get('message', {})
                    role = msg.get('role')
                    content = msg.get('content', [])
                    
                    if role == 'user':
                        if isinstance(content, list):
                            for c in content:
                                if isinstance(c, dict) and c.get('type') == 'text':
                                    text = c.get('text', '').strip()
                                    if not text:
                                        continue
                                    if text.startswith('A new session'):
                                        continue
                                    if 'Conversation info' in text:
                                        match = re.search(r'\]+\s*\n*\s*(.+)$', text, re.DOTALL)
                                        if match:
                                            text = match.group(1).strip()[:200]
                                        else:
                                            text = ''
                                    if text:
                                        messages.append(('user', text[:200]))
                    
                    elif role == 'assistant':
                        if isinstance(content, list):
                            for c in content:
                                if isinstance(c, dict) and c.get('type') == 'text':
                                    text = c.get('text', '').strip()
                                    if text and len(text) > 30 and not text.startswith('# '):
                                        messages.append(('assistant', text[:300]))
            except:
                continue
    return messages

def main():
    print(f"开始提取session到memory... (TODAY={TODAY})")
    
    session_file = find_main_session()
    if not session_file:
        print("未找到session文件")
        sys.exit(1)
    print(f"使用session: {session_file}")
    
    messages = extract_conversations(session_file)
    
    # 过滤掉非今日的消息（基于时间戳）
    user_msgs = [m for m in messages if m[0] == 'user']
    
    if not user_msgs:
        print("今日无有效对话")
        sys.exit(0)
    
    print(f"找到 {len(user_msgs)} 条用户消息")
    
    memory_file = MEMORY_DIR / f"{TODAY}.md"
    
    output_lines = []
    output_lines.append(f"# Memory {TODAY}")
    output_lines.append("")
    output_lines.append(f"## {TIME} 自动提取")
    output_lines.append("")
    output_lines.append("### 用户消息")
    for _, text in user_msgs[-15:]:
        output_lines.append(f"- {text}")
    output_lines.append("")
    output_lines.append("### 助手回复摘要")
    assistant_msgs = [m for m in messages if m[0] == 'assistant']
    for _, text in assistant_msgs[-5:]:
        output_lines.append(f"- {text[:150]}")
    
    content = "\n".join(output_lines)
    
    if memory_file.exists():
        existing = memory_file.read_text()
        if f"# Memory {TODAY}" in existing:
            # 追加模式
            content = existing + "\n\n---\n" + "\n".join(output_lines[2:])  # 去掉标题，只加内容
    
    memory_file.write_text(content, encoding='utf-8')
    print(f"已写入: {memory_file}")

if __name__ == "__main__":
    main()
