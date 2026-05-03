#!/usr/bin/env python3
"""
screen 详情面板卡片生成器 V2

目标：
- 展示 screen/agent-screen 任务的详情
- 下钻看到工作目录、日志、agent、启动时间
- 增加 screen 存活状态
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


def business_label(task_name: str, workdir: str) -> str:
    wd = workdir.lower()
    tn = task_name.lower()
    if 'railway-storage-5mwh' in wd:
        return '铁路储能 5MWh 项目测算'
    if 'cc-min-test' in tn:
        return 'Claude Code 最小链路测试'
    return task_name


def execution_mode(agent: str) -> str:
    mapping = {
        'claude': 'screen / Claude Code',
        'codex': 'screen / Codex',
    }
    return mapping.get(agent.lower(), agent)


def load_items(active_screen_names: set[str], limit: int = 8) -> list[dict]:
    items = []
    if not AGENT_SCREEN_DIR.exists():
        return items
    metas = sorted(AGENT_SCREEN_DIR.glob('*.meta'), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in metas[:limit]:
        meta = parse_meta(path)
        task_name = meta.get('TASK_NAME', path.stem)
        workdir = meta.get('WORKDIR', '')
        agent = meta.get('AGENT', 'unknown')
        alive = task_name in active_screen_names
        items.append({
            'business_name': business_label(task_name, workdir),
            'task_name': task_name,
            'execution_mode': execution_mode(agent),
            'workdir': workdir.replace(str(WORKSPACE) + '/', ''),
            'log_file': Path(meta.get('LOG_FILE', '')).name if meta.get('LOG_FILE') else 'unknown',
            'started_at': meta.get('STARTED_AT', '未知'),
            'prompt_file': Path(meta.get('PROMPT_FILE', '')).name if meta.get('PROMPT_FILE') else 'unknown',
            'pattern': meta.get('PATTERN', 'unknown'),
            'status': '进行中' if alive else ('已完成/测试' if 'test' in task_name.lower() else '最近活跃'),
            'alive_text': '存活中' if alive else '当前未存活',
        })
    return items


def build_card(open_id: str = DEFAULT_OPEN_ID, active_screen_names: set[str] | None = None) -> dict:
    active_screen_names = active_screen_names or set()
    items = load_items(active_screen_names)
    blocks = []
    for item in items:
        blocks.append({
            'tag': 'div',
            'text': {
                'tag': 'lark_md',
                'content': (
                    f"**{item['business_name']}**\n"
                    f"- 执行方式：{item['execution_mode']}\n"
                    f"- 状态：{item['status']}\n"
                    f"- 存活：{item['alive_text']}\n"
                    f"- 工作目录：`{item['workdir'] or '.'}`\n"
                    f"- 日志：`{item['log_file']}`\n"
                    f"- 启动时间：{item['started_at']}\n"
                    f"- 技术任务名：`{item['task_name']}`"
                )
            }
        })

    if not blocks:
        blocks.append({
            'tag': 'div',
            'text': {'tag': 'lark_md', 'content': '**当前没有可见的 screen 任务元数据。**'}
        })

    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': '🖥️ screen 详情面板 V2'},
            'template': 'cyan'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**定位**：下钻查看 screen / agent-screen 任务的执行细节，并显示是否还活着。'}},
            *blocks,
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '语义任务面板'}, 'type': 'primary', 'value': quick_action('semantic execution panel card', 'feishu.quick_actions.semantic_execution_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '执行中心'}, 'type': 'default', 'value': quick_action('execution center card', 'feishu.quick_actions.execution_center', open_id=open_id)},
            ]},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '← 执行链路'}, 'type': 'default', 'value': quick_action('execution_hub card', 'feishu.quick_actions.execution_hub', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '⌂ 主控制台'}, 'type': 'default', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': '这里展示最近 screen 元信息；为空通常代表已清理或当前没有可见记录。'}
            ]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='screen 详情面板 V2')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--active-screen', default='[]', help='JSON array of live screen task names')
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    try:
        active = set(json.loads(args.active_screen))
    except Exception:
        active = set()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.open_id, active)
    out = OUTPUT_DIR / 'screen-detail-panel-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
