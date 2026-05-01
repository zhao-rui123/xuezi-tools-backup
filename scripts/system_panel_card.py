#!/usr/bin/env python3
"""
系统面板卡片生成器 V1

聚焦：
- 健康检查关键状态
- 备份与同步状态
- 系统常用动作入口
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/zhaoruicn/.openclaw/workspace')
OUTPUT_DIR = WORKSPACE / 'summary' / 'cards'
DEFAULT_OPEN_ID = 'ou_5a7b7ec0339ffe0c1d5bb6c5bc162579'
DEFAULT_EXPIRES_AT = 1893456000000
HEALTH_SCRIPT = WORKSPACE / 'scripts' / 'healthcheck_openclaw.py'
BACKUP_LOG = Path('/tmp/backup_cron.log')
CLOUD_BACKUP_LOG = Path('/tmp/cloud-backup.log')


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


def run_health_payload() -> dict:
    if not HEALTH_SCRIPT.exists():
        return {'summary': {'ok': 0, 'warn': 1, 'fail': 1}, 'items': [], 'risks': ['健康检查脚本缺失']}
    try:
        proc = subprocess.run(
            ['python3', str(HEALTH_SCRIPT), '--json'],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(WORKSPACE),
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return {'summary': {'ok': 0, 'warn': 1, 'fail': 1}, 'items': [], 'risks': ['健康检查执行失败']}
        return json.loads(proc.stdout)
    except Exception:
        return {'summary': {'ok': 0, 'warn': 1, 'fail': 1}, 'items': [], 'risks': ['健康检查读取异常']}


def get_item(payload: dict, name: str) -> dict:
    for item in payload.get('items', []):
        if item.get('name') == name:
            return item
    return {'name': name, 'status': 'info', 'summary': '暂无数据'}


def fmt_status(item: dict) -> str:
    icon = {'ok': '✅', 'warn': '⚠️', 'fail': '❌', 'info': 'ℹ️'}.get(item.get('status'), '•')
    return f"{icon} {item.get('summary', '暂无数据')}"


def log_mtime(path: Path) -> str:
    if not path.exists():
        return '缺失'
    return datetime.fromtimestamp(path.stat().st_mtime).strftime('%m-%d %H:%M')


def build_card(open_id: str = DEFAULT_OPEN_ID) -> dict:
    payload = run_health_payload()
    summary = payload.get('summary', {})

    gateway = get_item(payload, 'Gateway')
    feishu = get_item(payload, 'Feishu 通道')
    tasks = get_item(payload, '任务系统')
    tailscale = get_item(payload, 'OpenClaw 视角 Tailscale')
    remote_ssh = get_item(payload, '云服务器 SSH')
    remote_v2ray = get_item(payload, '云服务器 V2Ray')
    update = get_item(payload, '版本更新')

    risks = payload.get('risks', [])[:4]
    risk_text = '\n'.join(f'- {x}' for x in risks) if risks else '- 暂无明显风险'

    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': '🩺 系统面板 V1'},
            'template': 'wathet'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f"**系统总览**：✅{summary.get('ok', 0)} / ⚠️{summary.get('warn', 0)} / ❌{summary.get('fail', 0)}"}},
            {'tag': 'div', 'fields': [
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f"**Gateway**\n{fmt_status(gateway)}"}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f"**Feishu 通道**\n{fmt_status(feishu)}"}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f"**任务系统**\n{fmt_status(tasks)}"}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f"**Tailscale**\n{fmt_status(tailscale)}"}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f"**云服务器 SSH**\n{fmt_status(remote_ssh)}"}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f"**云服务器 V2Ray**\n{fmt_status(remote_v2ray)}"}},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f"**备份状态**\n- 本地备份：{log_mtime(BACKUP_LOG)}\n- 云端同步：{log_mtime(CLOUD_BACKUP_LOG)}\n- 版本更新：{fmt_status(update)}"}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f"**风险提示**\n{risk_text}"}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '全面检查'}, 'type': 'primary', 'value': quick_action('healthcheck summary', 'feishu.quick_actions.healthcheck', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '备份状态'}, 'type': 'default', 'value': quick_action('backup status', 'feishu.quick_actions.backup_status', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '会话状态'}, 'type': 'default', 'value': quick_action('/status', 'feishu.quick_actions.oc_status', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '返回主控台'}, 'type': 'default', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': '这一版先把系统状态收成专题面板，下一步可继续拆任务面板。'}
            ]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='系统面板卡片生成器 V1')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.open_id)
    out = OUTPUT_DIR / 'system-panel-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
