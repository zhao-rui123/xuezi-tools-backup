#!/usr/bin/env python3
"""专业服务 Hub - Expert Agent 入口"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

WORKSPACE = Path('/Users/zhaoruicn/.openclaw/workspace')
OUT = WORKSPACE / 'summary' / 'cards' / 'cockpit-v5-professional_services_hub.json'
DEFAULT_OPEN_ID = 'ou_5a7b7ec0339ffe0c1d5bb6c5bc162579'
DEFAULT_EXPIRES_AT = 1893456000000


def qa(cmd: str, action: str, open_id: str = DEFAULT_OPEN_ID):
    return {
        'oc': 'ocf1', 'k': 'quick', 'a': action, 'q': cmd,
        'c': {'u': open_id, 'e': DEFAULT_EXPIRES_AT, 't': 'p2p'}
    }


def build_card(open_id: str = DEFAULT_OPEN_ID) -> dict:
    elements = [
        {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**📊 专业服务** — Expert Agent 入口'}},
        {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '专业领域 Agent，**你说需求，Agent 执行**。'}},
        {'tag': 'hr'},
        {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**⚡ 电力行业专家** *(开发中)*'}},
        {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '电气接线图 / 电价查询 / 储能选型 / 电费清单处理'}},
        {'tag': 'action', 'actions': [
            {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '⚡ 电力行业专家'}, 'type': 'primary', 'value': qa('电力行业专家 agent card', 'feishu.quick_actions.electric_power_expert', open_id=open_id)},
        ]},
        {'tag': 'hr'},
        {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**🌱 零碳专家** *(开发中)*'}},
        {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '零碳园区 / 碳排放计算 / 光储充 / 项目测算'}},
        {'tag': 'action', 'actions': [
            {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '🌱 零碳专家'}, 'type': 'primary', 'value': qa('零碳专家 agent card', 'feishu.quick_actions.zero_carbon_expert', open_id=open_id)},
        ]},
        {'tag': 'hr'},
        {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**📈 股票分析专家** *(即将上线)*'}},
        {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '技术分析 / 策略筛选 / 持仓监控'}},
        {'tag': 'action', 'actions': [
            {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '📈 股票分析专家'}, 'type': 'default', 'value': qa('股票分析专家 agent card', 'feishu.quick_actions.stock_expert', open_id=open_id)},
        ]},
        {'tag': 'hr'},
        {'tag': 'action', 'actions': [
            {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '← 返回主控制台'}, 'type': 'default', 'value': qa('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
        ]},
    ]

    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': '📊 专业服务'},
            'template': 'turquoise'
        },
        'elements': elements
    }


def main():
    parser = argparse.ArgumentParser(description='专业服务 Hub - Expert Agent 入口')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    card = build_card(open_id=args.open_id)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ {OUT}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()