#!/usr/bin/env python3
"""
从session提取对话写入每日记忆文件
改造版：四段结构化格式（决策/任务/知识/讨论）
"""
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

# 分类关键词（高置信度，只留明确词）
DECISION_KEYWORDS = [
    "决定用", "决定不", "决定改", "决定取消", "决定恢复",
    "就用", "就不改", "就不做", "就用它",
    "取消这个", "取消计划", "取消任务",
    "改用", "换成", "改回",
    "停止这个", "停止做", "先不做", "先不改",
    "开始干", "先这样", "就这样"
]
TASK_KEYWORDS = [
    "去做", "开始做", "完成了", "没完成",
    "待办", "还没做", "正在做", "进行中",
    "改完了", "改好了", "修好了", "搞定了", "搞定", "做完了", "部署了",
    "写好了", "提交了", "发给你", "发到", "发给你了"
]
KNOWLEDGE_KEYWORDS = [
    "学会了", "原来如此", "新发现", "第一次知道",
    "明白了", "懂了", "学到了", "记住了",
    "这就是", "原来是"  
]
TASK_KEYWORDS = [
    "去做", "开始", "完成", "还没", "待办", "做了吗", "还没做",
    "正在", "进行中", "等我", "等我一下", "我来做", "你去做",
    "改完了", "改好了", "修好了", "搞定了", "写好了", "发给你",
    "可以了", "好了", "搞定", "做完了"
]
KNOWLEDGE_KEYWORDS = [
    "学会了", "原来", "新发现", "原来如此", "居然", "竟然",
    "明白了", "懂了", "学到了", "记住", "知识库", "第一次"
]
TRASH_PATTERNS = [
    r"^\[.*?\]\s*$",  # 空的时间戳行
    r"^<<<\s*BEGIN",   # OpenClaw内部上下文
    r"^OpenClaw runtime",
    r"^Session info",
    r"^Sender",
    r"^\s*$",
]


def is_trash(text):
    """判断是否为噪音内容"""
    for pat in TRASH_PATTERNS:
        if re.match(pat, text.strip()):
            return True
    if len(text.strip()) < 5:
        return True
    return False


def classify(text, role="user"):
    """分类一条消息"""
    text_lower = text.lower()

    # 检查关键词
    for kw in DECISION_KEYWORDS:
        if kw in text:
            return "DECISION"

    for kw in TASK_KEYWORDS:
        if kw in text:
            return "TASK"

    for kw in KNOWLEDGE_KEYWORDS:
        if kw in text:
            return "KNOWLEDGE"

    return "DISCUSSION"


def clean_text(text):
    """清洗文本"""
    # 去掉 Conversation info 元数据
    if "Conversation info" in text:
        text = re.sub(r"\[.*?Conversation info.*?\]\s*", "", text, flags=re.DOTALL)
    # 截断过长内容
    if len(text) > 300:
        text = text[:300] + "..."
    return text.strip()


def find_main_session():
    """找到main session文件"""
    sessions_json = SESSIONS_DIR / "sessions.json"
    if sessions_json.exists():
        content = sessions_json.read_text()
        match = re.search(r'"agent:claude:main"[^}]*"sessionId":\s*"([^"]+)"', content)
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
                                    text = clean_text(c.get('text', ''))
                                    if text and not is_trash(text):
                                        messages.append(('user', text))

                    elif role == 'assistant':
                        if isinstance(content, list):
                            for c in content:
                                if isinstance(c, dict) and c.get('type') == 'text':
                                    text = clean_text(c.get('text', ''))
                                    if text and len(text) > 20 and not is_trash(text):
                                        messages.append(('assistant', text))
            except:
                continue
    return messages


def build_sections(messages):
    """按分类构建四段"""
    sections = {
        "DECISION": [],
        "TASK": [],
        "KNOWLEDGE": [],
        "DISCUSSION": []
    }

    seen = set()  # 去重

    for role, text in messages:
        cat = classify(text, role)
        # 简短讨论忽略
        if cat == "DISCUSSION" and len(text) < 50:
            continue
        # 精确去重
        key = text[:80].lower()
        if key in seen:
            continue
        seen.add(key)

        icon = {"DECISION": "🔴", "TASK": "📋", "KNOWLEDGE": "💡", "DISCUSSION": "💬"}[cat]
        label = {"DECISION": "决策", "TASK": "任务", "KNOWLEDGE": "知识", "DISCUSSION": "讨论"}[cat]
        prefix = f"{icon} [{label}]" if cat != "DISCUSSION" else f"💬"
        sections[cat].append(f"- {prefix} {text}")

    return sections


def main():
    print(f"开始提取session到memory... (TODAY={TODAY})")

    session_file = find_main_session()
    if not session_file:
        print("未找到session文件")
        sys.exit(1)
    print(f"使用session: {session_file}")

    messages = extract_conversations(session_file)
    print(f"找到 {len(messages)} 条有效消息")

    if not messages:
        print("今日无有效对话")
        sys.exit(0)

    sections = build_sections(messages)

    memory_file = MEMORY_DIR / f"{TODAY}.md"

    output_lines = []
    output_lines.append(f"# Memory {TODAY}")
    output_lines.append("")
    output_lines.append(f"## {TIME} 自动记录")
    output_lines.append("")

    for cat in ["DECISION", "TASK", "KNOWLEDGE", "DISCUSSION"]:
        items = sections[cat]
        if not items:
            continue
        label = {"DECISION": "决策 (DECISION)", "TASK": "任务 (TASK)",
                 "KNOWLEDGE": "知识 (KNOWLEDGE)", "DISCUSSION": "讨论 (DISCUSSION)"}[cat]
        output_lines.append(f"### {label}")
        for item in items[:10]:  # 每类最多10条
            output_lines.append(item)
        output_lines.append("")

    content = "\n".join(output_lines)

    if memory_file.exists():
        existing = memory_file.read_text()
        if f"# Memory {TODAY}" in existing:
            # 追加模式：在最后的 TIME 块后追加
            content = existing + "\n\n---\n" + "\n".join(output_lines[2:])

    memory_file.write_text(content, encoding='utf-8')
    print(f"已写入: {memory_file}")
    print(f"  决策:{len(sections['DECISION'])} 任务:{len(sections['TASK'])} 知识:{len(sections['KNOWLEDGE'])} 讨论:{len(sections['DISCUSSION'])}")


if __name__ == "__main__":
    main()
