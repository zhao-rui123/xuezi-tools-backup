#!/usr/bin/env python3
"""清理测试任务二次确认卡片 V1"""
from __future__ import annotations
import argparse, json
from pathlib import Path

WORKSPACE = Path('/Users/zhaoruicn/.openclaw/workspace')
OUTPUT_DIR = WORKSPACE / 'summary' / 'cards'
DEFAULT_OPEN_ID = 'ou_5a7b7ec0339ffe0c1d5bb6c5bc162579'
DEFAULT_EXPIRES_AT = 1893456000000
AGENT_SCREEN_DIR = WORKSPACE / 'logs' / 'agent-screen'
ALLOWED = {'cc-min-test','cc-wrapper-test','codex-wrapper-test'}


def quick_action(command: str, action: str, open_id: str = DEFAULT_OPEN_ID, chat_type: str = 'p2p') -> dict:
    return {'oc':'ocf1','k':'quick','a':action,'q':command,'c':{'u':open_id,'e':DEFAULT_EXPIRES_AT,'t':chat_type}}


def parse_meta(path: Path) -> dict:
    kv = {}
    for line in path.read_text(errors='ignore').splitlines():
        if '=' in line:
            k, v = line.split('=', 1)
            kv[k.strip()] = v.strip().strip("'")
    return kv


def find_task(task_name: str) -> dict | None:
    if task_name not in ALLOWED:
        return None
    path = AGENT_SCREEN_DIR / f'{task_name}.meta'
    if not path.exists():
        return None
    return parse_meta(path)


def build_card(task_name: str, open_id: str = DEFAULT_OPEN_ID) -> dict:
    meta = find_task(task_name)
    if not meta:
        return {
            'header': {'title': {'tag': 'plain_text', 'content': '⚠️ 未找到可清理测试任务'}, 'template': 'red'},
            'elements': [
                {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f'没有找到可清理任务：`{task_name}`'}},
                {'tag': 'action', 'actions': [
                    {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '返回清理面板'}, 'type': 'primary', 'value': quick_action('clean test tasks panel card', 'feishu.quick_actions.clean_test_tasks_panel', open_id=open_id)}
                ]}
            ]
        }

    return {
        'header': {'title': {'tag': 'plain_text', 'content': '🗑️ 清理确认 V1'}, 'template': 'orange'},
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**请确认**：你要清理的是下面这个测试任务。'}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': (
                f"**{task_name}**\n"
                f"- Agent：{meta.get('AGENT', '?')}\n"
                f"- 工作目录：`{meta.get('WORKDIR', '?')}`\n"
                f"- 日志：`{Path(meta.get('LOG_FILE','')).name if meta.get('LOG_FILE') else 'unknown'}`\n"
                f"- 启动时间：{meta.get('STARTED_AT', '未知')}"
            )}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**执行说明**：点击确认后，会清理该测试任务的活跃元信息；日志保留，不碰正式任务。'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': f'确认清理 {task_name}'}, 'type': 'primary', 'value': quick_action(f'clean execute {task_name}', 'feishu.quick_actions.clean_test_execute', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '返回清理面板'}, 'type': 'default', 'value': quick_action('clean test tasks panel card', 'feishu.quick_actions.clean_test_tasks_panel', open_id=open_id)},
            ]},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '← 模型与控制'}, 'type': 'default', 'value': quick_action('model_control_hub card', 'feishu.quick_actions.model_control_hub', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '⌂ 主控制台'}, 'type': 'default', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
            ]},
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='清理测试任务二次确认卡片 V1')
    parser.add_argument('task_name')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.task_name, args.open_id)
    out = OUTPUT_DIR / f'clean-confirm-{args.task_name}.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
