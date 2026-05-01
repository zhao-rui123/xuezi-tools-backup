#!/usr/bin/env python3
"""
Claude Code 模型切换卡片生成器
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


def build_card(open_id: str = DEFAULT_OPEN_ID) -> dict:
    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': '🎛️ Claude Code 模型切换'},
            'template': 'indigo'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**用途**：切换本地 Claude Code 默认模型环境。'}},
            {'tag': 'div', 'fields': [
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': '**Feinian**\nGPT-5.4 / 高质量'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': '**DeepSeek**\nV4 Flash / 性价比'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': '**MiniMax**\nM2.7 / 稳定卡片链路'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': '**查看当前**\n当前 CC 配置状态'}}
            ]},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '切 Feinian'}, 'type': 'primary', 'value': quick_action('cc model feinian', 'feishu.quick_actions.cc_model_feinian', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '切 DeepSeek'}, 'type': 'default', 'value': quick_action('cc model deepseek', 'feishu.quick_actions.cc_model_deepseek', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '切 MiniMax'}, 'type': 'default', 'value': quick_action('cc model minimax', 'feishu.quick_actions.cc_model_minimax', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '查看当前'}, 'type': 'default', 'value': quick_action('cc model status', 'feishu.quick_actions.cc_model_status', open_id=open_id)}
            ]},
            {'tag': 'note', 'elements': [{'tag': 'plain_text', 'content': '点击后会执行本地切换脚本，并回复结果。'}]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='Claude Code 模型切换卡片生成器')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.open_id)
    out = OUTPUT_DIR / 'cc-model-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
