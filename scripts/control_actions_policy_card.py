#!/usr/bin/env python3
"""
控制动作分级卡片 V1

目标：
- 明确哪些控制动作可先开放
- 哪些动作需要二次确认
- 哪些动作暂时不开放
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
            'title': {'tag': 'plain_text', 'content': '🛡️ 控制动作分级 V1'},
            'template': 'red'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**目标**：把主控制台里的控制动作按风险分级，先开安全的，再逐步放开危险的。'}},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**P0｜现在就能开放（低风险）**\n- 查看任务详情\n- 查看日志文件位置\n- 跳转到相关面板\n- 返回主控台\n- 查看状态 / 历史 / 最近时间'}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**P1｜可做，但需要确认（中风险）**\n- 清理测试任务\n- 重跑测试任务\n- 停止明确标记为测试的 screen 任务\n- 重新打开某个已结束的测试链路'}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**P2｜后面再做（高风险）**\n- 停止正式项目任务\n- 重跑正式项目任务\n- 恢复失败任务\n- 停止 ACP 正式线程\n- 改动定时任务配置'}},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**当前建议**\n1. 先把 P0 做全\n2. 再挑 1~2 个 P1 动作试点\n3. P2 必须等权限策略和确认机制设计好再开放'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '轻控制入口'}, 'type': 'primary', 'value': quick_action('light control panel card', 'feishu.quick_actions.light_control_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '执行中心'}, 'type': 'default', 'value': quick_action('execution center card', 'feishu.quick_actions.execution_center', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '主控制台'}, 'type': 'default', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': '下一步最合适的是：从 P1 里先挑一个最安全的控制动作做试点，比如“重跑测试任务”或“清理测试任务”。'}
            ]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='控制动作分级卡片 V1')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.open_id)
    out = OUTPUT_DIR / 'control-actions-policy-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
