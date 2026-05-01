#!/usr/bin/env python3
"""
ACP 语义任务面板 V2

目标：
- 给 ACP 子线程加一层人话标签
- 显示：任务名｜执行方式｜状态｜最近时间
- 增加是否仍活跃的状态判断
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
ACP_SESSIONS_FILE = Path.home() / '.openclaw/agents/claude-code/sessions/sessions.json'


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


def load_sessions() -> list[tuple[str, dict]]:
    if not ACP_SESSIONS_FILE.exists():
        return []
    try:
        data = json.loads(ACP_SESSIONS_FILE.read_text(encoding='utf-8'))
        return list(data.items())
    except Exception:
        return []


def fmt_ts(ms: int | None) -> str:
    if not ms:
        return '未知'
    return datetime.fromtimestamp(ms / 1000).strftime('%m-%d %H:%M')


def infer_status(updated_at_ms: int | None, alive: bool) -> str:
    if alive:
        return '进行中/活跃'
    if not updated_at_ms:
        return '未知'
    days = (datetime.now().timestamp() * 1000 - updated_at_ms) / 1000 / 3600 / 24
    if days > 7:
        return '历史线程/最近未活跃'
    if days > 1:
        return '近期未活跃'
    return '最近活跃'


def semantic_name(key: str, idx: int) -> str:
    if 'claude-code:acp' in key:
        return f'Claude Code ACP 子线程 {idx}'
    return f'ACP 子线程 {idx}'


def build_card(open_id: str = DEFAULT_OPEN_ID, active_keys: set[str] | None = None) -> dict:
    active_keys = active_keys or set()
    sessions = load_sessions()
    blocks = []
    for idx, (key, meta) in enumerate(sessions, start=1):
        updated_at = meta.get('updatedAt')
        alive = key in active_keys
        blocks.append({
            'tag': 'div',
            'text': {
                'tag': 'lark_md',
                'content': (
                    f"**{semantic_name(key, idx)}**｜**ACP / Claude Code**｜**{infer_status(updated_at, alive)}**\n"
                    f"- 存活：{'存活中' if alive else '当前未存活'}\n"
                    f"- 最近时间：{fmt_ts(updated_at)}\n"
                    f"- sessionId：`{meta.get('sessionId', 'unknown')}`\n"
                    f"- 技术线程名：`{key}`"
                )
            }
        })

    if not blocks:
        blocks.append({
            'tag': 'div',
            'text': {'tag': 'lark_md', 'content': '**当前未发现 ACP 子线程会话。**'}
        })

    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': '🧩 ACP 语义任务面板 V2'},
            'template': 'purple'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**定位**：把 ACP 线程翻成可读任务，并显示是否仍活跃。'}},
            *blocks,
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'ACP 详情'}, 'type': 'primary', 'value': quick_action('acp detail panel card', 'feishu.quick_actions.acp_detail_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '执行中心'}, 'type': 'default', 'value': quick_action('execution center card', 'feishu.quick_actions.execution_center', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '主控制台'}, 'type': 'default', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': '这版先保守显示“Claude Code ACP 子线程 X”；后续如果拿到更强元数据，再映射成具体业务任务。'}
            ]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='ACP 语义任务面板 V2')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--active-keys', default='[]', help='JSON array of active ACP keys')
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    try:
        active_keys = set(json.loads(args.active_keys))
    except Exception:
        active_keys = set()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.open_id, active_keys)
    out = OUTPUT_DIR / 'acp-semantic-panel-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
