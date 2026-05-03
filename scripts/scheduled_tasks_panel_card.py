#!/usr/bin/env python3
"""
定时任务中心卡片生成器 V1

聚焦：
- 每日备份
- 云端同步
- 股票推送
- 会话快照
- 周清理
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/zhaoruicn/.openclaw/workspace')
OUTPUT_DIR = WORKSPACE / 'summary' / 'cards'
DEFAULT_OPEN_ID = 'ou_5a7b7ec0339ffe0c1d5bb6c5bc162579'
DEFAULT_EXPIRES_AT = 1893456000000

TASKS = [
    ('每日备份', Path('/tmp/backup_cron.log'), '22:00', '每日'),
    ('云端同步', Path('/tmp/cloud-backup.log'), '22:35', '每日'),
    ('股票推送', Path('/tmp/stock_push.log'), '16:30', '工作日'),
    ('会话快照', Path('/tmp/session-snapshot.log'), '每10分钟', '高频'),
    ('周清理', Path.home() / '.openclaw/ops/logs/tasks/ouc_cleanup.log', '周日03:00', '每周'),
]


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


def check_log(path: Path) -> tuple[str, str]:
    if not path.exists():
        return 'fail', '日志缺失'
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    text = path.read_text(errors='ignore')
    tail = '\n'.join(text.splitlines()[-6:])
    if 'error' in tail.lower() or '失败' in tail or '❌' in tail:
        return 'warn', mtime.strftime('%m-%d %H:%M')
    return 'ok', mtime.strftime('%m-%d %H:%M')


def icon(status: str) -> str:
    return {'ok': '✅', 'warn': '⚠️', 'fail': '❌'}.get(status, '•')


def build_card(open_id: str = DEFAULT_OPEN_ID) -> dict:
    rows = []
    ok = warn = fail = 0
    for name, path, schedule, kind in TASKS:
        status, last = check_log(path)
        if status == 'ok':
            ok += 1
        elif status == 'warn':
            warn += 1
        else:
            fail += 1
        rows.append((name, status, last, schedule, kind))

    fields = []
    for name, status, last, schedule, kind in rows:
        fields.append({
            'tag': 'field',
            'text': {
                'tag': 'lark_md',
                'content': f'**{name}**\n{icon(status)} 最近：{last}\n计划：{schedule}｜{kind}'
            }
        })

    risk_lines = []
    for name, status, last, schedule, kind in rows:
        if status != 'ok':
            risk_lines.append(f'- {name}：{last}')
    risk_text = '\n'.join(risk_lines) if risk_lines else '- 当前主要定时任务最近都有更新'

    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': '⏰ 定时任务中心 V1'},
            'template': 'lime'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f'**任务总览**：✅{ok} / ⚠️{warn} / ❌{fail}'}},
            {'tag': 'div', 'fields': fields},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f'**关注项**\n{risk_text}'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '全面检查'}, 'type': 'primary', 'value': quick_action('healthcheck summary', 'feishu.quick_actions.healthcheck', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '备份状态'}, 'type': 'default', 'value': quick_action('backup status', 'feishu.quick_actions.backup_status', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '系统面板'}, 'type': 'default', 'value': quick_action('system panel card', 'feishu.quick_actions.system_panel', open_id=open_id)},
            ]},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '← 系统与定时'}, 'type': 'default', 'value': quick_action('system_hub card', 'feishu.quick_actions.system_hub', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '⌂ 主控制台'}, 'type': 'default', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': '这里只看定时任务；临时执行任务请回执行链路专题。'}
            ]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='定时任务中心卡片生成器 V1')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.open_id)
    out = OUTPUT_DIR / 'scheduled-tasks-panel-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
