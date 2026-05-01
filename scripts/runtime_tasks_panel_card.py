#!/usr/bin/env python3
"""
后台任务中心卡片生成器 V1

聚焦：
- 当前主会话状态
- 活跃会话/子会话概览
- 后台执行侧入口
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

WORKSPACE = Path('/Users/zhaoruicn/.openclaw/workspace')
OUTPUT_DIR = WORKSPACE / 'summary' / 'cards'
DEFAULT_OPEN_ID = 'ou_5a7b7ec0339ffe0c1d5bb6c5bc162579'
DEFAULT_EXPIRES_AT = 1893456000000


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


def build_card(open_id: str = DEFAULT_OPEN_ID, *, oc_model: str = '', tokens: str = '', context: str = '', child_count: int = 0, active_tasks: str = '') -> dict:
    child_text = f'{child_count} 个子会话/ACP 线程' if child_count else '当前未发现子会话'
    active_text = active_tasks or '当前 1 active'
    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': '🧵 后台任务中心 V1'},
            'template': 'indigo'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**执行侧总览**：把主会话、后台线程、运行状态收成一个专题面板。'}},
            {'tag': 'div', 'fields': [
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**当前模型**\n{oc_model or "未知"}'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**Tokens**\n{tokens or "未知"}'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**Context**\n{context or "未知"}'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**活跃任务**\n{active_text}'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**后台线程**\n{child_text}'}},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**当前判断**\n- 主会话正在运行\n- 已挂出子会话/ACP 线程可继续扩展\n- 这一版先做只读观测，不做线程管理操作'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '查看会话状态'}, 'type': 'primary', 'value': quick_action('/status', 'feishu.quick_actions.oc_status', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '模型面板'}, 'type': 'default', 'value': quick_action('model panel card', 'feishu.quick_actions.model_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '主控制台'}, 'type': 'default', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': '下一步如果要更强，可以做 ACP/子线程列表、最近后台任务历史、甚至停止/恢复入口。'}
            ]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='后台任务中心卡片生成器 V1')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--oc-model', default='')
    parser.add_argument('--tokens', default='')
    parser.add_argument('--context', default='')
    parser.add_argument('--child-count', type=int, default=0)
    parser.add_argument('--active-tasks', default='')
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(
        args.open_id,
        oc_model=args.oc_model,
        tokens=args.tokens,
        context=args.context,
        child_count=args.child_count,
        active_tasks=args.active_tasks,
    )
    out = OUTPUT_DIR / 'runtime-tasks-panel-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
