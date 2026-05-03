#!/usr/bin/env python3
"""
快捷动作面板卡片生成器 V1

聚焦：
- 最常用动作集中成执行按钮
- 减少在多个面板间来回跳转
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
            'title': {'tag': 'plain_text', 'content': '⚡ 快捷动作面板 V1'},
            'template': 'orange'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**定位**：把最常用动作集中成一组直接可点的执行按钮。'}},
            {'tag': 'div', 'fields': [
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': '**系统动作**\n全面检查 / 备份状态 / 会话状态'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': '**任务动作**\nInbox / 阻塞 / 高优先级 / 摘要'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': '**模型动作**\n切 OpenClaw / 切 Claude Code'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': '**导航动作**\n返回主控制台 / 打开专题面板'}},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**🩺 系统动作**'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '全面检查'}, 'type': 'primary', 'value': quick_action('healthcheck summary', 'feishu.quick_actions.healthcheck', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '备份状态'}, 'type': 'default', 'value': quick_action('backup status', 'feishu.quick_actions.backup_status', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '会话状态'}, 'type': 'default', 'value': quick_action('/status', 'feishu.quick_actions.oc_status', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '系统面板'}, 'type': 'default', 'value': quick_action('system panel card', 'feishu.quick_actions.system_panel', open_id=open_id)},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**📋 任务动作**'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'Inbox'}, 'type': 'primary', 'value': quick_action('inbox card', 'feishu.quick_actions.inbox', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '阻塞'}, 'type': 'default', 'value': quick_action('blocked card', 'feishu.quick_actions.blocked', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '高优先级'}, 'type': 'default', 'value': quick_action('high card', 'feishu.quick_actions.high', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '摘要'}, 'type': 'default', 'value': quick_action('digest card', 'feishu.quick_actions.digest', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '任务面板'}, 'type': 'default', 'value': quick_action('task panel card', 'feishu.quick_actions.task_panel', open_id=open_id)},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**🧠 模型动作**'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '切 Feinian'}, 'type': 'primary', 'value': quick_action('/model feinian', 'feishu.quick_actions.oc_model_feinian', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '切 DeepSeek'}, 'type': 'default', 'value': quick_action('/model deepseek', 'feishu.quick_actions.oc_model_deepseek', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '切 MiniMax'}, 'type': 'default', 'value': quick_action('/model minimax', 'feishu.quick_actions.oc_model_minimax', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'CC 切 DeepSeek'}, 'type': 'default', 'value': quick_action('cc model deepseek', 'feishu.quick_actions.cc_model_deepseek', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '模型面板'}, 'type': 'default', 'value': quick_action('model panel card', 'feishu.quick_actions.model_panel', open_id=open_id)},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**🧭 导航动作**'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '← 快捷'}, 'type': 'default', 'value': quick_action('quick_hub card', 'feishu.quick_actions.quick_hub', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '⌂ 主控制台'}, 'type': 'primary', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '记忆面板'}, 'type': 'default', 'value': quick_action('memory panel card', 'feishu.quick_actions.memory_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '工作台总览'}, 'type': 'default', 'value': quick_action('workspace card', 'feishu.quick_actions.cockpit_workspace', open_id=open_id)},
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': '下一步可做“今日重点建议”，让主控制台从状态面板升级为半自动指挥台。'}
            ]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='快捷动作面板卡片生成器 V1')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.open_id)
    out = OUTPUT_DIR / 'quick-actions-panel-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
