#!/usr/bin/env python3
"""
重跑测试任务二次确认卡片 V1

目标：
- 给单个测试任务提供二次确认视图
- 先确认“就是这个任务”，再进入真实执行阶段
- 当前版本只做确认层，不直接执行
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


def find_task(task_name: str) -> dict | None:
    if not AGENT_SCREEN_DIR.exists():
        return None
    for path in AGENT_SCREEN_DIR.glob('*.meta'):
        meta = parse_meta(path)
        if meta.get('TASK_NAME') == task_name:
            return meta
    return None


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


def build_card(task_name: str, open_id: str = DEFAULT_OPEN_ID) -> dict:
    meta = find_task(task_name)
    if not meta:
        return {
            'header': {'title': {'tag': 'plain_text', 'content': '⚠️ 未找到测试任务'}, 'template': 'red'},
            'elements': [
                {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f'没有找到任务：`{task_name}`'}},
                {'tag': 'action', 'actions': [
                    {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '返回重跑面板'}, 'type': 'primary', 'value': quick_action('rerun test tasks panel card', 'feishu.quick_actions.rerun_test_tasks_panel', open_id=open_id)}
                ]}
            ]
        }

    workdir = meta.get('WORKDIR', '')
    agent = meta.get('AGENT', 'unknown')
    biz = business_name(task_name, workdir)

    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': '♻️ 重跑确认 V1'},
            'template': 'orange'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**请确认**：你要重跑的是下面这个测试任务。'}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': (
                f"**{biz}**\n"
                f"- 执行方式：{execution_mode(agent)}\n"
                f"- 工作目录：`{workdir}`\n"
                f"- 日志：`{Path(meta.get('LOG_FILE','')).name if meta.get('LOG_FILE') else 'unknown'}`\n"
                f"- 上次时间：{meta.get('STARTED_AT', '未知')}\n"
                f"- 技术任务名：`{task_name}`"
            )}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**执行说明**：点击下面的确认按钮，会向当前会话发送重跑指令；由当前会话执行 `rerun-test-task.sh`。'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': f'确认并重跑 {task_name}'}, 'type': 'primary', 'value': quick_action(f'rerun execute {task_name}', 'feishu.quick_actions.rerun_test_execute', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '返回重跑面板'}, 'type': 'default', 'value': quick_action('rerun test tasks panel card', 'feishu.quick_actions.rerun_test_tasks_panel', open_id=open_id)},
            ]},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '← 执行链路'}, 'type': 'default', 'value': quick_action('execution_hub card', 'feishu.quick_actions.execution_hub', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '⌂ 主控制台'}, 'type': 'default', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': '当前只允许 3 个测试任务：cc-min-test / cc-wrapper-test / codex-wrapper-test。'}
            ]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='重跑测试任务二次确认卡片 V1')
    parser.add_argument('task_name')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.task_name, args.open_id)
    out = OUTPUT_DIR / f'rerun-confirm-{args.task_name}.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
