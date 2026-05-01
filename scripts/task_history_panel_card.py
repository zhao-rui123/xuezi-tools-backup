#!/usr/bin/env python3
"""
任务历史中心卡片生成器 V1

目标：
- 展示最近跑过的任务
- 区分项目任务 / 测试任务 / 定时任务
- 提供“当前 + 历史”视角补充
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
AGENT_SCREEN_DIR = WORKSPACE / 'logs' / 'agent-screen'

SCHEDULED = [
    ('股票日报推送', Path('/tmp/stock_push.log'), '定时任务'),
    ('每日备份', Path('/tmp/backup_cron.log'), '定时任务'),
    ('云端同步', Path('/tmp/cloud-backup.log'), '定时任务'),
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


def parse_meta(path: Path) -> dict:
    kv = {}
    for line in path.read_text(errors='ignore').splitlines():
        if '=' in line:
            k, v = line.split('=', 1)
            kv[k.strip()] = v.strip().strip("'")
    return kv


def business_label(task_name: str, workdir: str) -> tuple[str, str]:
    wd = workdir.lower()
    tn = task_name.lower()
    if 'railway-storage-5mwh' in wd:
        return '铁路储能 5MWh 项目测算', '项目任务'
    if 'cc-min-test' in tn:
        return 'Claude Code 最小链路测试', '测试任务'
    if 'test' in tn:
        return task_name, '测试任务'
    return task_name, '后台任务'


def execution_mode(agent: str) -> str:
    return 'screen / Codex' if agent == 'codex' else 'screen / Claude Code' if agent == 'claude' else agent


def collect_history(limit: int = 12) -> list[dict]:
    items = []
    if AGENT_SCREEN_DIR.exists():
        metas = sorted(AGENT_SCREEN_DIR.glob('*.meta'), key=lambda p: p.stat().st_mtime, reverse=True)
        for path in metas:
            meta = parse_meta(path)
            task_name = meta.get('TASK_NAME', path.stem)
            workdir = meta.get('WORKDIR', '')
            name, kind = business_label(task_name, workdir)
            items.append({
                'name': name,
                'kind': kind,
                'mode': execution_mode(meta.get('AGENT', 'unknown')),
                'time': meta.get('STARTED_AT', '未知'),
                'tech': task_name,
            })
    for name, path, kind in SCHEDULED:
        if path.exists():
            t = datetime.fromtimestamp(path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            items.append({
                'name': name,
                'kind': kind,
                'mode': '定时任务',
                'time': t,
                'tech': path.name,
            })
    items.sort(key=lambda x: x['time'], reverse=True)
    return items[:limit]


def build_card(open_id: str = DEFAULT_OPEN_ID) -> dict:
    items = collect_history()
    blocks = []
    for item in items:
        blocks.append({
            'tag': 'div',
            'text': {
                'tag': 'lark_md',
                'content': (
                    f"**{item['name']}**｜**{item['mode']}**\n"
                    f"- 类型：{item['kind']}\n"
                    f"- 最近时间：{item['time']}\n"
                    f"- 技术标识：`{item['tech']}`"
                )
            }
        })

    if not blocks:
        blocks.append({
            'tag': 'div',
            'text': {'tag': 'lark_md', 'content': '**当前没有可见的任务历史记录。**'}
        })

    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': '🗂️ 任务历史中心 V1'},
            'template': 'blue'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**定位**：从历史角度看最近系统到底忙过什么。'}},
            *blocks,
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '主控制台'}, 'type': 'primary', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '执行中心'}, 'type': 'default', 'value': quick_action('execution center card', 'feishu.quick_actions.execution_center', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '定时任务中心'}, 'type': 'default', 'value': quick_action('scheduled tasks panel card', 'feishu.quick_actions.scheduled_tasks_panel', open_id=open_id)},
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': '下一步可以继续做“轻控制入口”，比如查看详情/跳转/回到相关面板。'}
            ]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='任务历史中心 V1')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.open_id)
    out = OUTPUT_DIR / 'task-history-panel-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
