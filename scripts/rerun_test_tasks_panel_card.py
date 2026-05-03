#!/usr/bin/env python3
"""
重跑测试任务面板 V2

目标：
- 列出可安全试点的测试任务
- 给每个测试任务接“二次确认”入口
- 暂不直接执行真实重跑，先完成确认层
"""

from __future__ import annotations

import argparse
import json
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


def business_name(task_name: str, workdir: str) -> str:
    wd = workdir.lower()
    tn = task_name.lower()
    if 'railway-storage-5mwh' in wd:
        return '铁路储能 5MWh 项目测试链路'
    if 'cc-min-test' in tn:
        return 'Claude Code 最小链路测试'
    return task_name


def execution_mode(agent: str) -> str:
    return 'screen / Codex' if agent == 'codex' else 'screen / Claude Code' if agent == 'claude' else agent


def collect_candidates() -> list[dict]:
    out = []
    if not AGENT_SCREEN_DIR.exists():
        return out
    for path in sorted(AGENT_SCREEN_DIR.glob('*.meta'), key=lambda p: p.stat().st_mtime, reverse=True):
        meta = parse_meta(path)
        task_name = meta.get('TASK_NAME', path.stem)
        if 'test' not in task_name.lower():
            continue
        out.append({
            'task_name': task_name,
            'business_name': business_name(task_name, meta.get('WORKDIR', '')),
            'mode': execution_mode(meta.get('AGENT', 'unknown')),
            'started_at': meta.get('STARTED_AT', '未知'),
            'workdir': meta.get('WORKDIR', ''),
            'log_file': Path(meta.get('LOG_FILE', '')).name if meta.get('LOG_FILE') else 'unknown',
        })
    return out


def build_card(open_id: str = DEFAULT_OPEN_ID) -> dict:
    items = collect_candidates()
    elements = [
        {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**试点原则**：先只针对测试任务，不直接执行，先明确候选和规则。'}},
        {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**当前规则**\n- 仅限测试任务\n- 不碰正式项目任务\n- 真执行前必须二次确认\n- 这一版按钮只进入确认层，不直接重跑'}},
        {'tag': 'hr'},
    ]

    if not items:
        elements.append({'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**当前没有可识别的测试任务候选。**'}})
    else:
        for item in items:
            elements.append({
                'tag': 'div',
                'text': {
                    'tag': 'lark_md',
                    'content': (
                        f"**{item['business_name']}**\n"
                        f"- 执行方式：{item['mode']}\n"
                        f"- 上次时间：{item['started_at']}\n"
                        f"- 工作目录：`{item['workdir']}`\n"
                        f"- 日志：`{item['log_file']}`\n"
                        f"- 技术任务名：`{item['task_name']}`"
                    )
                }
            })
            elements.append({
                'tag': 'action',
                'actions': [
                    {
                        'tag': 'button',
                        'text': {'tag': 'plain_text', 'content': f'确认重跑 {item["task_name"]}'},
                        'type': 'primary',
                        'value': quick_action(f'rerun confirm {item["task_name"]}', 'feishu.quick_actions.rerun_test_confirm', open_id=open_id)
                    }
                ]
            })

    elements.extend([
        {'tag': 'action', 'actions': [
            {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '轻控制入口'}, 'type': 'primary', 'value': quick_action('light control panel card', 'feishu.quick_actions.light_control_panel', open_id=open_id)},
            {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '任务历史中心'}, 'type': 'default', 'value': quick_action('task history panel card', 'feishu.quick_actions.task_history_panel', open_id=open_id)},
        ]},
        {'tag': 'action', 'actions': [
            {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '← 执行链路'}, 'type': 'default', 'value': quick_action('execution_hub card', 'feishu.quick_actions.execution_hub', open_id=open_id)},
            {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '⌂ 主控制台'}, 'type': 'default', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
        ]},
        {'tag': 'note', 'elements': [
            {'tag': 'plain_text', 'content': '这里只允许测试任务重跑，不碰正式任务。'}
        ]}
    ])

    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': '♻️ 重跑测试任务 V2'},
            'template': 'orange'
        },
        'elements': elements,
    }


def main():
    parser = argparse.ArgumentParser(description='重跑测试任务面板 V2')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.open_id)
    out = OUTPUT_DIR / 'rerun-test-tasks-panel-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
