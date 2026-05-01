#!/usr/bin/env python3
"""
任务面板卡片生成器 V1

聚焦：
- 任务中心状态
- 候选 inbox 状态
- 高频任务动作入口
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path

WORKSPACE = Path('/Users/zhaoruicn/.openclaw/workspace')
OUTPUT_DIR = WORKSPACE / 'summary' / 'cards'
DEFAULT_OPEN_ID = 'ou_5a7b7ec0339ffe0c1d5bb6c5bc162579'
DEFAULT_EXPIRES_AT = 1893456000000
TASK_FILE = WORKSPACE / 'projects' / 'task-center' / 'tasks.json'
CANDIDATE_DIR = WORKSPACE / 'memory' / 'auto-candidates'


def quick_action(command: str, action: str, open_id: str = DEFAULT_OPEN_ID, chat_type: str = 'p2p') -> dict:
    return {
        'oc': 'ocf1',
        'k': 'quick',
        'a': action,
        'q': command,
        'c': {
            'u': open_id,
            'e': DEFAULT_EXPIRES_AT,
            't': chat_type,
        },
    }


def load_tasks() -> list[dict]:
    if not TASK_FILE.exists():
        return []
    try:
        return json.loads(TASK_FILE.read_text(encoding='utf-8')).get('tasks', [])
    except Exception:
        return []


def load_candidates(day: str) -> list[dict]:
    path = CANDIDATE_DIR / f'{day}.json'
    if not path.exists():
        return []
    try:
        items = json.loads(path.read_text(encoding='utf-8')).get('items', [])
        for item in items:
            item.setdefault('state', 'new')
        return items
    except Exception:
        return []


def top_lines(items: list[dict], kind: str, limit: int = 4) -> str:
    lines = []
    for item in items[:limit]:
        if kind == 'task':
            lines.append(f"- `{item.get('id')}` {item.get('title')}")
        else:
            lines.append(f"- `{item.get('id')}` {item.get('type')} | {item.get('content')}")
    if len(items) > limit:
        lines.append(f"- ... 还有 {len(items) - limit} 条")
    return '\n'.join(lines) if lines else '- 无'


def build_card(open_id: str = DEFAULT_OPEN_ID) -> dict:
    today = date.today().strftime('%Y-%m-%d')
    tasks = load_tasks()
    candidates = load_candidates(today)
    by_state = Counter(x.get('state', 'new') for x in candidates)

    blocked = [t for t in tasks if t.get('status') == 'blocked']
    doing = [t for t in tasks if t.get('status') == 'doing']
    high = [t for t in tasks if t.get('status') == 'todo' and t.get('priority') == 'high']
    auto_today = [t for t in tasks if t.get('created_at', '').startswith(today) and 'auto-import' in (t.get('tags') or [])]
    inbox = [x for x in candidates if x.get('state', 'new') == 'new']

    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': f'📋 任务面板 V1 | {today}'},
            'template': 'blue'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**任务总览**：把工作台里最常用的任务状态收成一个专题面板。'}},
            {'tag': 'div', 'fields': [
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**Inbox**\n{len(inbox)}'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**Blocked**\n{len(blocked)}'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**Doing**\n{len(doing)}'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**High**\n{len(high)}'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**已导入**\n{by_state.get("imported", 0)}'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**已忽略**\n{by_state.get("ignored", 0)}'}},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f"**当前阻塞**\n{top_lines(blocked, 'task')}"}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f"**高优先级待办**\n{top_lines(high, 'task')}"}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f"**待处理 Inbox**\n{top_lines(inbox, 'candidate')}"}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f"**今日自动导入**\n{top_lines(auto_today, 'task')}"}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '工作台总览'}, 'type': 'primary', 'value': quick_action('workspace card', 'feishu.quick_actions.cockpit_workspace', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'Inbox'}, 'type': 'default', 'value': quick_action('inbox card', 'feishu.quick_actions.inbox', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '阻塞'}, 'type': 'default', 'value': quick_action('blocked card', 'feishu.quick_actions.blocked', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '高优先级'}, 'type': 'default', 'value': quick_action('high card', 'feishu.quick_actions.high', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '摘要'}, 'type': 'default', 'value': quick_action('digest card', 'feishu.quick_actions.digest', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '返回主控台'}, 'type': 'default', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': '下一步可以继续做模型面板，把 OpenClaw / Claude Code 模型状态彻底拆开。'}
            ]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='任务面板卡片生成器 V1')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.open_id)
    out = OUTPUT_DIR / 'task-panel-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
