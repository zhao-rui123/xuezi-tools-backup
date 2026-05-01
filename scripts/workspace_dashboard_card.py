#!/usr/bin/env python3
"""
飞书工作台卡片生成器 V2（真交互版）

按钮改为 OpenClaw Feishu 插件支持的 structured quick action。
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path

WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
TASK_FILE = WORKSPACE / "projects" / "task-center" / "tasks.json"
CANDIDATE_DIR = WORKSPACE / "memory" / "auto-candidates"
OUTPUT_DIR = WORKSPACE / "summary" / "cards"
DEFAULT_OPEN_ID = "ou_5a7b7ec0339ffe0c1d5bb6c5bc162579"
DEFAULT_EXPIRES_AT = 1893456000000


def today_str() -> str:
    return date.today().strftime("%Y-%m-%d")


def load_tasks():
    if not TASK_FILE.exists():
        return []
    return json.loads(TASK_FILE.read_text(encoding="utf-8")).get("tasks", [])


def load_candidates(day: str):
    path = CANDIDATE_DIR / f"{day}.json"
    if not path.exists():
        return []
    items = json.loads(path.read_text(encoding="utf-8")).get("items", [])
    for item in items:
        item.setdefault("state", "new")
    return items


def quick_action(command: str, action: str, open_id: str = DEFAULT_OPEN_ID, chat_type: str = "p2p") -> dict:
    return {
        "oc": "ocf1",
        "k": "quick",
        "a": action,
        "q": command,
        "c": {
            "u": open_id,
            "e": DEFAULT_EXPIRES_AT,
            "t": chat_type,
        },
    }


def trim_lines(items, kind="task", limit=5):
    out = []
    for item in items[:limit]:
        if kind == "task":
            text = f"- `{item.get('id')}` {item.get('title')}"
        else:
            text = f"- `{item.get('id')}` {item.get('type')} | {item.get('content')}"
        out.append(text)
    if len(items) > limit:
        out.append(f"- ... 还有 {len(items) - limit} 条")
    return "\n".join(out) if out else "- 无"


def build_card(day: str, open_id: str = DEFAULT_OPEN_ID) -> dict:
    tasks = load_tasks()
    candidates = load_candidates(day)

    by_state = Counter(x.get("state", "new") for x in candidates)
    inbox = [x for x in candidates if x.get("state", "new") == "new"]
    blocked = [t for t in tasks if t.get("status") == "blocked"]
    doing = [t for t in tasks if t.get("status") == "doing"]
    todo_high = [t for t in tasks if t.get("status") == "todo" and t.get("priority") == "high"]
    auto_today = [t for t in tasks if (t.get("created_at", "").startswith(day) and "auto-import" in (t.get("tags") or []))]

    fields_top = [
        f"**候选待处理**\n{by_state.get('new', 0)}",
        f"**已导入**\n{by_state.get('imported', 0)}",
        f"**已忽略**\n{by_state.get('ignored', 0)}",
        f"**阻塞**\n{len(blocked)}",
        f"**进行中**\n{len(doing)}",
        f"**高优先级待办**\n{len(todo_high)}",
    ]
    field_elements = [{"tag": "field", "text": {"tag": "lark_md", "content": x}} for x in fields_top]

    return {
        "header": {
            "title": {"tag": "plain_text", "content": f"🧭 工作台总览 | {day}"},
            "template": "blue"
        },
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": "**概览**：主卡片只保留核心统计，详细内容通过按钮查看。"}},
            {"tag": "div", "fields": field_elements},
            {"tag": "action",
             "actions": [
                {"tag": "button", "text": {"tag": "plain_text", "content": "📥 Inbox"}, "type": "default", "value": quick_action("inbox card", "feishu.quick_actions.inbox", open_id=open_id)},
                {"tag": "button", "text": {"tag": "plain_text", "content": "⛔ 阻塞"}, "type": "default", "value": quick_action("blocked card", "feishu.quick_actions.blocked", open_id=open_id)},
                {"tag": "button", "text": {"tag": "plain_text", "content": "🔥 高优先级"}, "type": "primary", "value": quick_action("high card", "feishu.quick_actions.high", open_id=open_id)},
                {"tag": "button", "text": {"tag": "plain_text", "content": "🧾 摘要"}, "type": "default", "value": quick_action("digest card", "feishu.quick_actions.digest", open_id=open_id)}
             ]},
            {"tag": "note", "elements": [{"tag": "plain_text", "content": "点击按钮会返回对应的子卡片内容。"}]}
        ]
    }


def cmd_generate(args):
    day = args.day or today_str()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(day, open_id=args.open_id or DEFAULT_OPEN_ID)
    out = OUTPUT_DIR / f"{day}-dashboard-card.json"
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 已生成卡片: {out}")
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


def build_parser():
    parser = argparse.ArgumentParser(description="飞书工作台卡片生成器 V2（真交互版）")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("generate")
    p.add_argument("--day", default="")
    p.add_argument("--open-id", default="")
    p.add_argument("--print", action="store_true")
    p.set_defaults(func=cmd_generate)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
