#!/usr/bin/env python3
"""
ACP / 子线程详情卡片生成器 V1

聚焦：
- 当前可见 ACP 子线程明细
- sessionId / 最近更新时间 / sessionFile
- 先做只读详情版
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


def load_acp_sessions() -> list[tuple[str, dict]]:
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


def build_card(open_id: str = DEFAULT_OPEN_ID) -> dict:
    items = load_acp_sessions()
    detail_blocks = []
    for key, meta in items[:8]:
        session_id = meta.get('sessionId', 'unknown')
        updated = fmt_ts(meta.get('updatedAt'))
        session_file = meta.get('sessionFile', '')
        file_name = Path(session_file).name if session_file else 'unknown'
        detail_blocks.append({
            'tag': 'div',
            'text': {
                'tag': 'lark_md',
                'content': (
                    f"**{key}**\n"
                    f"- sessionId: `{session_id}`\n"
                    f"- 最近更新: {updated}\n"
                    f"- 文件: `{file_name}`"
                )
            }
        })

    if not detail_blocks:
        detail_blocks.append({
            'tag': 'div',
            'text': {'tag': 'lark_md', 'content': '**当前未发现 ACP 子线程会话文件。**'}
        })

    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': '🔎 ACP / 子线程详情 V1'},
            'template': 'purple'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f'**总览**：当前记录到 {len(items)} 个 ACP 子线程会话。'}},
            *detail_blocks,
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '执行中心'}, 'type': 'primary', 'value': quick_action('execution center card', 'feishu.quick_actions.execution_center', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '后台任务中心'}, 'type': 'default', 'value': quick_action('runtime tasks panel card', 'feishu.quick_actions.runtime_tasks_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '主控制台'}, 'type': 'default', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': '下一步可以补 screen 详情、后台任务历史，或者给这些线程加日志入口。'}
            ]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='ACP / 子线程详情卡片生成器 V1')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.open_id)
    out = OUTPUT_DIR / 'acp-detail-panel-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
