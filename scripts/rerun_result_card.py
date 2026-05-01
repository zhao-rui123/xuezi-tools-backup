#!/usr/bin/env python3
"""
重跑结果卡片生成器
接收 rerun-test-task-result.sh 的原始输出，生成飞书结果卡片
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

WORKSPACE = Path('/Users/zhaoruicn/.openclaw/workspace')
OUTPUT_DIR = WORKSPACE / 'summary' / 'cards'
DEFAULT_OPEN_ID = 'ou_5a7b7ec0339ffe0c1d5bb6c5bc162579'
DEFAULT_EXPIRES_AT = 1893456000000

def quick_action(command: str, action: str, open_id: str = DEFAULT_OPEN_ID) -> dict:
    return {
        'oc': 'ocf1', 'k': 'quick', 'a': action, 'q': command,
        'c': {'u': open_id, 'e': DEFAULT_EXPIRES_AT, 't': 'p2p'},
    }

def parse_result(raw: str) -> dict:
    out = {}
    for line in raw.strip().splitlines():
        m = re.match(r'[-\u2022] (.+?): (.+)', line)
        if m:
            out[m.group(1).strip()] = m.group(2).strip()
    return out

def build_result_card(task: str, raw: str, open_id: str = DEFAULT_OPEN_ID) -> dict:
    r = parse_result(raw)
    new_task = r.get('新任务', 'unknown')
    log_name = Path(r.get('日志','')).name
    screen = r.get('Screen', '')
    meta_name = Path(r.get('Meta','')).name

    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': f'✅ 重跑成功'},
            'template': 'green'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f'**任务重跑完成**\n\n'
                f'- 原任务：`{task}`\n'
                f'- 新任务：`{new_task}`\n'
                f'- 日志：`{log_name}`\n'
                f'- Meta：`{meta_name}`\n'
                f'- Screen：`{screen}`'}},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '现在可以进入新链路，或返回主控制台查看。'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '查看日志'},
                 'type': 'default',
                 'value': quick_action(f'tail -20 logs/{log_name}', 'feishu.quick_actions.oc_exec', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '重跑面板'},
                 'type': 'primary',
                 'value': quick_action('rerun test tasks panel card', 'feishu.quick_actions.rerun_test_tasks_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '主控制台'},
                 'type': 'default',
                 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
            ]},
        ]
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', required=True)
    parser.add_argument('--result', required=True)
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--save', action='store_true')
    args = parser.parse_args()

    card = build_result_card(args.task, args.result, args.open_id)

    if args.save:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        safe = args.task.replace('-','_')
        out = OUTPUT_DIR / f'rerun-result-{safe}.json'
        out.write_text(json.dumps(card, ensure_ascii=False, indent=2))
        print(f'✅ 已保存: {out}')
    else:
        print(json.dumps(card, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
