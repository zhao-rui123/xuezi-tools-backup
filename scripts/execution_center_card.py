#!/usr/bin/env python3
"""
执行中心面板卡片生成器 V2

聚焦：
- ACP / 子会话
- screen 会话
- 本地后台任务与主会话状态
- 尽量展示可见任务名，而不是只给数量
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


def load_recent_meta_tasks(limit: int = 6) -> list[dict]:
    items: list[dict] = []
    if not AGENT_SCREEN_DIR.exists():
        return items
    metas = sorted(AGENT_SCREEN_DIR.glob('*.meta'), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in metas[:limit]:
        text = path.read_text(errors='ignore')
        kv = {}
        for line in text.splitlines():
            if '=' in line:
                k, v = line.split('=', 1)
                kv[k.strip()] = v.strip().strip("'")
        items.append({
            'task_name': kv.get('TASK_NAME', path.stem),
            'agent': kv.get('AGENT', 'unknown'),
            'started_at': kv.get('STARTED_AT', '未知'),
            'log_file': Path(kv.get('LOG_FILE', '')).name if kv.get('LOG_FILE') else 'unknown',
        })
    return items


def build_card(
    open_id: str = DEFAULT_OPEN_ID,
    *,
    main_model: str = '',
    active_tasks: str = '',
    acp_count: int = 0,
    acp_list: list[str] | None = None,
    screen_count: int = 0,
    screen_list: list[str] | None = None,
    runtime_note: str = '',
) -> dict:
    acp_list = acp_list or []
    screen_list = screen_list or []
    recent_tasks = load_recent_meta_tasks()

    acp_text = '\n'.join(f'- {x}' for x in acp_list[:5]) if acp_list else '- 当前未发现可见 ACP 子线程详情'
    if len(acp_list) > 5:
        acp_text += f'\n- ... 还有 {len(acp_list) - 5} 个'

    screen_text = '\n'.join(f'- {x}' for x in screen_list[:5]) if screen_list else '- 当前没有 screen 会话'
    if len(screen_list) > 5:
        screen_text += f'\n- ... 还有 {len(screen_list) - 5} 个'

    if recent_tasks:
        recent_text = '\n'.join(
            f"- `{x['task_name']}` | {x['agent']} | {x['started_at']} | {x['log_file']}" for x in recent_tasks
        )
    else:
        recent_text = '- 当前没有可见 agent-screen 任务元数据'

    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': '🚦 执行中心 V2'},
            'template': 'violet'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**定位**：把 ACP、screen、本地后台任务收进一个统一执行中心，并尽量展示具体任务名。'}},
            {'tag': 'div', 'fields': [
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**主会话模型**\n{main_model or "未知"}'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**活跃任务**\n{active_tasks or "未知"}'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**ACP / 子线程数**\n{acp_count}'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**screen 会话数**\n{screen_count}'}},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f'**ACP / 子会话**\n{acp_text}'}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f'**screen 会话**\n{screen_text}'}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f'**最近后台任务名**\n{recent_text}'}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f'**当前判断**\n- {runtime_note or "执行链路总体正常，当前先做只读观测版。"}'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '语义任务面板'}, 'type': 'primary', 'value': quick_action('semantic execution panel card', 'feishu.quick_actions.semantic_execution_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'ACP 语义面板'}, 'type': 'default', 'value': quick_action('acp semantic panel card', 'feishu.quick_actions.acp_semantic_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'ACP 详情'}, 'type': 'default', 'value': quick_action('acp detail panel card', 'feishu.quick_actions.acp_detail_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '后台任务中心'}, 'type': 'default', 'value': quick_action('runtime tasks panel card', 'feishu.quick_actions.runtime_tasks_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '会话状态'}, 'type': 'default', 'value': quick_action('/status', 'feishu.quick_actions.oc_status', open_id=open_id)},
            ]},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '← 执行链路'}, 'type': 'default', 'value': quick_action('execution_hub card', 'feishu.quick_actions.execution_hub', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '⌂ 主控制台'}, 'type': 'default', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': '目前 screen 任务名可以通过 agent-screen meta 看到；ACP 暂时只能稳定拿到线程 key / sessionId。'}
            ]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='执行中心面板卡片生成器 V2')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--main-model', default='')
    parser.add_argument('--active-tasks', default='')
    parser.add_argument('--acp-count', type=int, default=0)
    parser.add_argument('--acp-list', default='[]', help='JSON array')
    parser.add_argument('--screen-count', type=int, default=0)
    parser.add_argument('--screen-list', default='[]', help='JSON array')
    parser.add_argument('--runtime-note', default='')
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    try:
        acp_list = json.loads(args.acp_list)
    except Exception:
        acp_list = []
    try:
        screen_list = json.loads(args.screen_list)
    except Exception:
        screen_list = []

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(
        args.open_id,
        main_model=args.main_model,
        active_tasks=args.active_tasks,
        acp_count=args.acp_count,
        acp_list=acp_list,
        screen_count=args.screen_count,
        screen_list=screen_list,
        runtime_note=args.runtime_note,
    )
    out = OUTPUT_DIR / 'execution-center-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
