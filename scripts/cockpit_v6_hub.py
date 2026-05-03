#!/usr/bin/env python3
"""主控制台 V6 Hub - 轻状态版（带真数据）"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

WORKSPACE = Path('/Users/zhaoruicn/.openclaw/workspace')
OUT = WORKSPACE / 'summary' / 'cards' / 'cockpit-v6-hub.json'
TASK_FILE = WORKSPACE / 'projects' / 'task-center' / 'tasks.json'
DEFAULT_OPEN_ID = 'ou_5a7b7ec0339ffe0c1d5bb6c5bc162579'
DEFAULT_EXPIRES_AT = 1893456000000
SH_TZ = ZoneInfo('Asia/Shanghai')

HUBS = [
    ('⚡', '执行链路', 'execution_hub', '执行中心 | 语义任务面板 | ACP语义面板 | screen详情 | 重跑测试任务 | 任务历史中心 | 后台任务中心'),
    ('📋', '任务与记忆', 'task_hub', '任务面板 | 记忆面板 | 今日重点建议 | 阻塞 | 高优先级 | 待处理Inbox | 摘要'),
    ('🩺', '系统与定时', 'system_hub', '系统面板 | 定时任务中心 | 健康检查 | 备份状态'),
    ('🤖', '模型与控制', 'model_control_hub', '模型面板 | 切换CC模型 | OpenClaw模型卡 | 会话状态 | 轻控制入口 | 重跑测试 | 清理测试'),
    ('🔧', '快捷', 'quick_hub', '快捷动作面板 | 主控制台 | 帮助'),
    ('📊', '专业服务', 'professional_services_hub', '电力及零碳专家 | 股票分析专家（即将上线）'),
]


def qa(cmd: str, action: str, open_id: str = DEFAULT_OPEN_ID):
    return {
        'oc': 'ocf1', 'k': 'quick', 'a': action, 'q': cmd,
        'c': {'u': open_id, 'e': DEFAULT_EXPIRES_AT, 't': 'p2p'}
    }


def load_tasks() -> list[dict]:
    if not TASK_FILE.exists():
        return []
    try:
        return json.loads(TASK_FILE.read_text(encoding='utf-8')).get('tasks', [])
    except Exception:
        return []


def summarize_tasks(tasks: list[dict]) -> tuple[int, int]:
    doing = [t for t in tasks if t.get('status') == 'doing']
    todo_high = [t for t in tasks if t.get('status') == 'todo' and t.get('priority') == 'high']
    blocked = [t for t in tasks if t.get('status') == 'blocked']
    focus = len(doing) + len(todo_high)
    return focus, len(blocked)


def run(cmd: str) -> str:
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=8)
        return (res.stdout or '') + (res.stderr or '')
    except Exception:
        return ''


def count_screen_tasks() -> int:
    out = run('screen -ls 2>&1 || true')
    if 'No Sockets found' in out:
        return 0
    return len(re.findall(r'\t[^\n]+\(Detached\)|\t[^\n]+\(Attached\)', out))


def parse_recent_acpx_count(tool: str, active_hours: int = 24) -> int:
    if not shutil_which('acpx'):
        return 0
    out = run(f'acpx {tool} sessions list 2>/dev/null || true')
    now = datetime.now(tz=SH_TZ)
    count = 0
    for raw in out.splitlines():
        line = raw.strip()
        if not line or '[closed]' in line:
            continue
        parts = line.split()
        if not parts:
            continue
        ts = parts[-1]
        try:
            dt = datetime.fromisoformat(ts.replace('Z', '+00:00')).astimezone(SH_TZ)
        except Exception:
            count += 1
            continue
        if now - dt <= timedelta(hours=active_hours):
            count += 1
    return count


def shutil_which(name: str) -> str | None:
    from shutil import which
    return which(name)


def count_background_tasks(active_hours: int = 24) -> tuple[int, int, int]:
    screen_count = count_screen_tasks()
    acpx_claude = parse_recent_acpx_count('claude', active_hours=active_hours)
    acpx_codex = parse_recent_acpx_count('codex', active_hours=active_hours)
    acpx_total = acpx_claude + acpx_codex
    return screen_count + acpx_total, screen_count, acpx_total


def build_card(current_model: str, open_id: str = DEFAULT_OPEN_ID, active_hours: int = 24) -> dict:
    tasks = load_tasks()
    focus_count, blocked_count = summarize_tasks(tasks)
    bg_total, screen_count, acpx_count = count_background_tasks(active_hours=active_hours)

    elements = [
        {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**🕹️ 主控制台 V6**  — 轻状态版'}},
        {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f'**当前模型：{current_model or "未知"}**'}},
        {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f'今日重点：{focus_count}｜阻塞：{blocked_count}｜后台任务：{bg_total}'}},
        {'tag': 'hr'},
    ]

    for icon, name, key, sub_label in HUBS:
        elements.append({
            'tag': 'action',
            'actions': [
                {
                    'tag': 'button',
                    'text': {'tag': 'plain_text', 'content': f'{icon} {name}'},
                    'type': 'primary',
                    'value': qa(f'{key} card', f'feishu.quick_actions.{key}', open_id=open_id)
                }
            ]
        })
        elements.append({'tag': 'div', 'text': {'tag': 'lark_md', 'content': f'  → {sub_label}'}})

    elements.extend([
        {'tag': 'hr'},
        {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '直接发送专题名称也可，如：「执行中心」「系统面板」「今日重点」'}}
    ])

    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': '🕹️ 主控制台 V6'},
            'template': 'turquoise'
        },
        'elements': elements
    }


def main():
    parser = argparse.ArgumentParser(description='主控制台 V6 Hub - 轻状态版（带真数据）')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--current-model', default='')
    parser.add_argument('--active-hours', type=int, default=24)
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    card = build_card(args.current_model, open_id=args.open_id, active_hours=args.active_hours)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ {OUT}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
