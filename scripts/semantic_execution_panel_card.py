#!/usr/bin/env python3
"""
任务语义执行面板 V1

目标：
- 从技术任务名翻成业务任务名
- 给每个任务附上链路 / 状态 / 最近时间
- 优先给雪子看“任务本身”，不是底层 id
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


def map_business_name(task_name: str, workdir: str) -> tuple[str, str]:
    wd = workdir.lower()
    tn = task_name.lower()

    if 'railway-storage-5mwh' in wd:
        if 'codex' in tn:
            return '铁路储能 5MWh 项目（Codex 包装链路测试）', '项目开发'
        if 'claude' in tn or 'cc-' in tn:
            return '铁路储能 5MWh 项目（Claude Code 包装链路测试）', '项目开发'
        return '铁路储能 5MWh 项目任务', '项目开发'

    if 'cc-min-test' in tn:
        return 'Claude Code 最小链路测试', '链路测试'

    if 'codex' in tn:
        return 'Codex 后台任务', '后台执行'
    if 'cc-' in tn or 'claude' in tn:
        return 'Claude Code 后台任务', '后台执行'

    return task_name, '未分类'


def infer_status(task_name: str) -> str:
    tn = task_name.lower()
    if 'test' in tn:
        return '已完成/测试'
    return '最近活跃'


def load_semantic_tasks(limit: int = 8) -> list[dict]:
    items = []
    if not AGENT_SCREEN_DIR.exists():
        return items
    metas = sorted(AGENT_SCREEN_DIR.glob('*.meta'), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in metas[:limit]:
        meta = parse_meta(path)
        task_name = meta.get('TASK_NAME', path.stem)
        workdir = meta.get('WORKDIR', '')
        business_name, category = map_business_name(task_name, workdir)
        items.append({
            'business_name': business_name,
            'category': category,
            'chain': meta.get('AGENT', 'unknown'),
            'status': infer_status(task_name),
            'started_at': meta.get('STARTED_AT', '未知'),
            'task_name': task_name,
            'log_file': Path(meta.get('LOG_FILE', '')).name if meta.get('LOG_FILE') else 'unknown',
        })
    return items


def build_card(open_id: str = DEFAULT_OPEN_ID) -> dict:
    tasks = load_semantic_tasks()
    blocks = []
    for item in tasks:
        blocks.append({
            'tag': 'div',
            'text': {
                'tag': 'lark_md',
                'content': (
                    f"**{item['business_name']}**\n"
                    f"- 类型：{item['category']}\n"
                    f"- 链路：{item['chain']}\n"
                    f"- 状态：{item['status']}\n"
                    f"- 最近时间：{item['started_at']}\n"
                    f"- 技术任务名：`{item['task_name']}`"
                )
            }
        })

    if not blocks:
        blocks.append({
            'tag': 'div',
            'text': {'tag': 'lark_md', 'content': '**当前没有可映射的后台任务。**'}
        })

    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': '🧭 任务语义执行面板 V1'},
            'template': 'blue'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**定位**：优先显示“任务本身是什么、什么情况”，而不是底层进程 id。'}},
            *blocks,
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '执行中心'}, 'type': 'primary', 'value': quick_action('execution center card', 'feishu.quick_actions.execution_center', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '后台任务中心'}, 'type': 'default', 'value': quick_action('runtime tasks panel card', 'feishu.quick_actions.runtime_tasks_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '主控制台'}, 'type': 'default', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': '下一步可补：把 ACP 线程也做成业务任务名映射，而不只显示 key。'}
            ]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='任务语义执行面板 V1')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.open_id)
    out = OUTPUT_DIR / 'semantic-execution-panel-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
