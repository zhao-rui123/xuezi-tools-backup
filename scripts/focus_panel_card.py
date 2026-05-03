#!/usr/bin/env python3
"""
今日重点建议卡片生成器 V1

目标：
- 从任务 / 风险 / 健康 / 备份里，给出当前最值得先处理的事情
- 先做规则版，不依赖额外模型推理
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from datetime import date
from pathlib import Path

WORKSPACE = Path('/Users/zhaoruicn/.openclaw/workspace')
OUTPUT_DIR = WORKSPACE / 'summary' / 'cards'
DEFAULT_OPEN_ID = 'ou_5a7b7ec0339ffe0c1d5bb6c5bc162579'
DEFAULT_EXPIRES_AT = 1893456000000
TASK_FILE = WORKSPACE / 'projects' / 'task-center' / 'tasks.json'
CANDIDATE_DIR = WORKSPACE / 'memory' / 'auto-candidates'
HEALTH_SCRIPT = WORKSPACE / 'scripts' / 'healthcheck_openclaw.py'
CLOUD_BACKUP_LOG = Path('/tmp/cloud-backup.log')


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


def load_tasks() -> list[dict]:
    if not TASK_FILE.exists():
        return []
    try:
        return json.loads(TASK_FILE.read_text(encoding='utf-8')).get('tasks', [])
    except Exception:
        return []


def load_candidates(day: str) -> list[dict]:
    path = CANDIDATE_DIR / f'{day}.json'
    if not path.exists():
        return []
    try:
        items = json.loads(path.read_text(encoding='utf-8')).get('items', [])
        for item in items:
            item.setdefault('state', 'new')
        return items
    except Exception:
        return []


def get_health_risks() -> list[str]:
    if not HEALTH_SCRIPT.exists():
        return ['健康检查脚本缺失']
    try:
        proc = subprocess.run(
            ['python3', str(HEALTH_SCRIPT), '--json'],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(WORKSPACE),
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return ['健康检查执行失败']
        payload = json.loads(proc.stdout)
        return payload.get('risks', [])
    except Exception:
        return ['健康检查读取异常']


def backup_risk() -> str:
    if not CLOUD_BACKUP_LOG.exists():
        return '云端同步日志缺失'
    try:
        tail = '\n'.join(CLOUD_BACKUP_LOG.read_text(errors='ignore').splitlines()[-10:])
        if '远程端当前备份数量: 0' in tail:
            return '云端同步跑了，但远程端数量为 0'
    except Exception:
        return '云端同步日志读取异常'
    return ''


def prioritize(tasks: list[dict], candidates: list[dict], risks: list[str], backup_issue: str) -> list[dict]:
    suggestions: list[dict] = []

    blocked = [t for t in tasks if t.get('status') == 'blocked']
    high = [t for t in tasks if t.get('status') == 'todo' and t.get('priority') == 'high']
    risk_candidates = [x for x in candidates if x.get('type') == 'risk' and x.get('state') == 'new']
    inbox = [x for x in candidates if x.get('state') == 'new']

    if blocked:
        suggestions.append({
            'title': '先清阻塞任务',
            'reason': f'当前有 {len(blocked)} 条 blocked，优先解除卡点。',
            'action_text': '查看阻塞',
            'command': 'blocked card',
            'action': 'feishu.quick_actions.blocked',
        })

    if backup_issue:
        suggestions.append({
            'title': '复查云端备份',
            'reason': backup_issue,
            'action_text': '看备份状态',
            'command': 'backup status',
            'action': 'feishu.quick_actions.backup_status',
        })

    if risks:
        suggestions.append({
            'title': '关注系统风险',
            'reason': risks[0],
            'action_text': '全面检查',
            'command': 'healthcheck summary',
            'action': 'feishu.quick_actions.healthcheck',
        })

    if high:
        suggestions.append({
            'title': '推进高优先级待办',
            'reason': f'当前有 {len(high)} 条高优先级待办。',
            'action_text': '看高优先级',
            'command': 'high card',
            'action': 'feishu.quick_actions.high',
        })

    if risk_candidates:
        suggestions.append({
            'title': '整理风险候选',
            'reason': f'当前有 {len(risk_candidates)} 条未处理 risk 候选。',
            'action_text': '看记忆面板',
            'command': 'memory panel card',
            'action': 'feishu.quick_actions.memory_panel',
        })

    if inbox:
        suggestions.append({
            'title': '清理 Inbox',
            'reason': f'当前还有 {len(inbox)} 条待处理 inbox。',
            'action_text': '打开 Inbox',
            'command': 'inbox card',
            'action': 'feishu.quick_actions.inbox',
        })

    return suggestions[:4]


def build_card(open_id: str = DEFAULT_OPEN_ID) -> dict:
    today = date.today().strftime('%Y-%m-%d')
    tasks = load_tasks()
    candidates = load_candidates(today)
    by_type = Counter(x.get('type', 'unknown') for x in candidates)
    risks = get_health_risks()
    backup_issue = backup_risk()
    suggestions = prioritize(tasks, candidates, risks, backup_issue)

    suggestion_blocks = []
    for idx, item in enumerate(suggestions, start=1):
        suggestion_blocks.append({
            'tag': 'div',
            'text': {
                'tag': 'lark_md',
                'content': f"**建议 {idx}｜{item['title']}**\n- 原因：{item['reason']}\n- 建议动作：{item['action_text']}"
            }
        })
        suggestion_blocks.append({
            'tag': 'action',
            'actions': [
                {
                    'tag': 'button',
                    'text': {'tag': 'plain_text', 'content': item['action_text']},
                    'type': 'primary' if idx == 1 else 'default',
                    'value': quick_action(item['command'], item['action'], open_id=open_id),
                }
            ]
        })

    if not suggestions:
        suggestion_blocks.append({
            'tag': 'div',
            'text': {'tag': 'lark_md', 'content': '**当前判断**：没有明显需要优先处理的异常项，可以按正常节奏推进。'}
        })

    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': f'🎯 今日重点建议 V1 | {today}'},
            'template': 'green'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f"**规则版判断**：基于任务、风险、备份、健康检查，给出当前最值得先处理的事。"}},
            {'tag': 'div', 'fields': [
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f"**高优先级待办**\n{sum(1 for t in tasks if t.get('status') == 'todo' and t.get('priority') == 'high')}"}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f"**阻塞任务**\n{sum(1 for t in tasks if t.get('status') == 'blocked')}"}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f"**风险候选**\n{by_type.get('risk', 0)}"}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f"**Inbox**\n{sum(1 for x in candidates if x.get('state') == 'new')}"}},
            ]},
            {'tag': 'hr'},
            *suggestion_blocks,
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '快捷动作面板'}, 'type': 'default', 'value': quick_action('quick actions panel card', 'feishu.quick_actions.quick_actions_panel', open_id=open_id)},
            ]},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '← 任务与记忆'}, 'type': 'default', 'value': quick_action('task_hub card', 'feishu.quick_actions.task_hub', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '⌂ 主控制台'}, 'type': 'default', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': '下一步可做“定时任务中心”或“后台任务中心”，让主控制台继续向总控台靠近。'}
            ]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='今日重点建议卡片生成器 V1')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.open_id)
    out = OUTPUT_DIR / 'focus-panel-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
