#!/usr/bin/env python3
"""
记忆面板卡片生成器 V1

聚焦：
- 今日候选统计
- 风险 / 规则 / 待办 / 进展候选
- 候选状态管理入口
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


def lines(items: list[dict], limit: int = 4) -> str:
    out = []
    for item in items[:limit]:
        out.append(f"- `{item.get('id')}` {item.get('type')} | {item.get('content')}")
    if len(items) > limit:
        out.append(f"- ... 还有 {len(items) - limit} 条")
    return '\n'.join(out) if out else '- 无'


def build_card(open_id: str = DEFAULT_OPEN_ID) -> dict:
    today = date.today().strftime('%Y-%m-%d')
    items = load_candidates(today)
    by_state = Counter(x.get('state', 'new') for x in items)
    by_type = Counter(x.get('type', 'unknown') for x in items)

    inbox = [x for x in items if x.get('state', 'new') == 'new']
    risks = [x for x in items if x.get('type') == 'risk']
    rules = [x for x in items if x.get('type') == 'rule']
    todos = [x for x in items if x.get('type') == 'todo']
    progress = [x for x in items if x.get('type') == 'progress']

    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': f'🧠 记忆面板 V1 | {today}'},
            'template': 'carmine'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**记忆总览**：把候选层、状态管理和风险/规则入口收成专题面板。'}},
            {'tag': 'div', 'fields': [
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**候选总数**\n{len(items)}'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**Inbox**\n{by_state.get("new", 0)}'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**已导入 / 已忽略**\n{by_state.get("imported", 0)} / {by_state.get("ignored", 0)}'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**风险 / 规则**\n{by_type.get("risk", 0)} / {by_type.get("rule", 0)}'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**待办 / 进展**\n{by_type.get("todo", 0)} / {by_type.get("progress", 0)}'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**今日焦点**\n{len(risks)} 风险候选'}},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f"**风险候选**\n{lines(risks)}"}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f"**规则候选**\n{lines(rules)}"}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f"**待处理 Inbox**\n{lines(inbox)}"}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f"**待办 / 进展候选**\n{lines(todos + progress)}"}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'Inbox'}, 'type': 'primary', 'value': quick_action('inbox card', 'feishu.quick_actions.inbox', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '摘要'}, 'type': 'default', 'value': quick_action('digest card', 'feishu.quick_actions.digest', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '任务面板'}, 'type': 'default', 'value': quick_action('task panel card', 'feishu.quick_actions.task_panel', open_id=open_id)},
            ]},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '← 任务与记忆'}, 'type': 'default', 'value': quick_action('task_hub card', 'feishu.quick_actions.task_hub', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '⌂ 主控制台'}, 'type': 'default', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': '下一步可做快捷动作面板，把最常用操作集中成一组“执行按钮”。'}
            ]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='记忆面板卡片生成器 V1')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.open_id)
    out = OUTPUT_DIR / 'memory-panel-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
