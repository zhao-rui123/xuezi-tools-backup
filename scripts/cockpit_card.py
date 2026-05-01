#!/usr/bin/env python3
"""
总驾驶台互动卡片生成器 V1

整合：
1. OpenClaw 会话模型切换
2. Claude Code 模型切换
3. 工作台/任务跟踪
4. 健康检查入口
5. 常用系统入口
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import date
from pathlib import Path

WORKSPACE = Path('/Users/zhaoruicn/.openclaw/workspace')
OUTPUT_DIR = WORKSPACE / 'summary' / 'cards'
DEFAULT_OPEN_ID = 'ou_5a7b7ec0339ffe0c1d5bb6c5bc162579'
DEFAULT_EXPIRES_AT = 1893456000000
HEALTH_SCRIPT = WORKSPACE / 'scripts' / 'healthcheck_openclaw.py'


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


def get_health_summary() -> str:
    if not HEALTH_SCRIPT.exists():
        return '健康检查脚本缺失，暂无法读取摘要。'
    try:
        proc = subprocess.run(
            ['python3', str(HEALTH_SCRIPT), '--summary'],
            capture_output=True,
            text=True,
            timeout=45,
            cwd=str(WORKSPACE),
        )
        if proc.returncode != 0:
            return '健康检查执行失败，请点“全面检查”获取详情。'
        lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
        if not lines:
            return '健康检查无输出，请点“全面检查”获取详情。'
        summary_line = next((x for x in lines if x.startswith('总览：')), '')
        risk_index = next((i for i, x in enumerate(lines) if x.startswith('风险：')), -1)
        risk_line = ''
        if risk_index >= 0 and risk_index + 1 < len(lines):
            risk_line = lines[risk_index + 1].lstrip('- ').strip()
        parts = []
        if summary_line:
            parts.append(summary_line)
        if risk_line:
            parts.append(f'关注：{risk_line}')
        return ' ｜ '.join(parts) if parts else lines[0]
    except Exception:
        return '健康检查读取异常，请点“全面检查”获取详情。'


def build_card(open_id: str = DEFAULT_OPEN_ID) -> dict:
    today = date.today().strftime('%Y-%m-%d')
    health_summary = get_health_summary()
    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': f'🕹️ 总驾驶台 | {today}'},
            'template': 'turquoise'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**定位**：把模型切换、任务跟踪、系统检查收进一张总入口卡里。'}},
            {'tag': 'div', 'fields': [
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': '**OpenClaw**\n会话模型切换'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': '**Claude Code**\n本地模型切换'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': '**工作台**\nInbox / Blocked / High / Digest'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': '**全面检查**\n系统健康与风险摘要'}},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**🧠 模型区**'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'OpenClaw 模型'}, 'type': 'primary', 'value': quick_action('openclaw model card', 'feishu.quick_actions.cockpit_oc_model', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'Claude Code 模型'}, 'type': 'default', 'value': quick_action('cc model card', 'feishu.quick_actions.cockpit_cc_model', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '会话 Status'}, 'type': 'default', 'value': quick_action('/status', 'feishu.quick_actions.oc_status', open_id=open_id)},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**📋 任务区**'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '工作台总览'}, 'type': 'primary', 'value': quick_action('workspace card', 'feishu.quick_actions.cockpit_workspace', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'Inbox'}, 'type': 'default', 'value': quick_action('inbox card', 'feishu.quick_actions.inbox', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'Blocked'}, 'type': 'default', 'value': quick_action('blocked card', 'feishu.quick_actions.blocked', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'High'}, 'type': 'default', 'value': quick_action('high card', 'feishu.quick_actions.high', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'Digest'}, 'type': 'default', 'value': quick_action('digest card', 'feishu.quick_actions.digest', open_id=open_id)},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**🩺 系统区**'}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': health_summary}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '全面检查'}, 'type': 'primary', 'value': quick_action('healthcheck summary', 'feishu.quick_actions.healthcheck', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '备份状态'}, 'type': 'default', 'value': quick_action('backup status', 'feishu.quick_actions.backup_status', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '帮助'}, 'type': 'default', 'value': quick_action('/help', 'feishu.quick_actions.help', open_id=open_id)},
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': '建议把它当首页入口：先看总览，再点进模型、任务、检查。'}
            ]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='总驾驶台互动卡片生成器 V1')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.open_id)
    out = OUTPUT_DIR / 'cockpit-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
