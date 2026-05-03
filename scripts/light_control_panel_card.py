#!/usr/bin/env python3
"""
轻控制入口面板 V1

目标：
- 不做危险操作
- 只做查看详情 / 跳转 / 返回相关面板
- 作为主控制台到专题面板的快捷桥梁
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
            'title': {'tag': 'plain_text', 'content': '🪄 轻控制入口 V1'},
            'template': 'indigo'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**定位**：先做低风险控制，只负责查看详情、跳转、返回，不直接停任务。'}},
            {'tag': 'div', 'fields': [
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': '**看任务详情**\n执行中心 / 语义任务 / screen / ACP'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': '**看系统详情**\n系统面板 / 定时任务 / 备份 / 健康检查'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': '**看模型详情**\n模型面板 / OpenClaw / Claude Code'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': '**返回主控制台**\n主控制台首页'}},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**📋 任务与执行**'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '执行中心'}, 'type': 'primary', 'value': quick_action('execution center card', 'feishu.quick_actions.execution_center', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '任务语义面板'}, 'type': 'default', 'value': quick_action('semantic execution panel card', 'feishu.quick_actions.semantic_execution_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'screen 详情'}, 'type': 'default', 'value': quick_action('screen detail panel card', 'feishu.quick_actions.screen_detail_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'ACP 语义面板'}, 'type': 'default', 'value': quick_action('acp semantic panel card', 'feishu.quick_actions.acp_semantic_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '任务历史中心'}, 'type': 'default', 'value': quick_action('task history panel card', 'feishu.quick_actions.task_history_panel', open_id=open_id)},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**🩺 系统与健康**'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '系统面板'}, 'type': 'primary', 'value': quick_action('system panel card', 'feishu.quick_actions.system_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '定时任务中心'}, 'type': 'default', 'value': quick_action('scheduled tasks panel card', 'feishu.quick_actions.scheduled_tasks_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '备份状态'}, 'type': 'default', 'value': quick_action('backup status', 'feishu.quick_actions.backup_status', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '全面检查'}, 'type': 'default', 'value': quick_action('healthcheck summary', 'feishu.quick_actions.healthcheck', open_id=open_id)},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**🧠 模型与会话**'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '模型面板'}, 'type': 'primary', 'value': quick_action('model panel card', 'feishu.quick_actions.model_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'OpenClaw 模型卡'}, 'type': 'default', 'value': quick_action('openclaw model card', 'feishu.quick_actions.cockpit_oc_model', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'Claude Code 模型卡'}, 'type': 'default', 'value': quick_action('cc model card', 'feishu.quick_actions.cockpit_cc_model', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '会话状态'}, 'type': 'default', 'value': quick_action('/status', 'feishu.quick_actions.oc_status', open_id=open_id)},
            ]},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '← 模型与控制'}, 'type': 'default', 'value': quick_action('model_control_hub card', 'feishu.quick_actions.model_control_hub', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '⌂ 主控制台'}, 'type': 'primary', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '今日重点建议'}, 'type': 'default', 'value': quick_action('focus panel card', 'feishu.quick_actions.focus_panel', open_id=open_id)},
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': '这里只放高频低风险快捷动作；复杂控制请回专题面板。'}
            ]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='轻控制入口面板 V1')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.open_id)
    out = OUTPUT_DIR / 'light-control-panel-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
