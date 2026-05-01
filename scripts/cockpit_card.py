#!/usr/bin/env python3
"""
总驾驶台互动卡片生成器 V2

目标：
1. 首页状态化，而不是只做导航
2. 汇总模型 / 任务 / 健康 / 备份四类核心信息
3. 保留高频按钮，作为主控制台首页
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from datetime import date, datetime
from pathlib import Path

WORKSPACE = Path('/Users/zhaoruicn/.openclaw/workspace')
OUTPUT_DIR = WORKSPACE / 'summary' / 'cards'
DEFAULT_OPEN_ID = 'ou_5a7b7ec0339ffe0c1d5bb6c5bc162579'
DEFAULT_EXPIRES_AT = 1893456000000
HEALTH_SCRIPT = WORKSPACE / 'scripts' / 'healthcheck_openclaw.py'
CC_MODEL_SCRIPT = WORKSPACE / 'scripts' / 'cc-model-switch.sh'
TASK_FILE = WORKSPACE / 'projects' / 'task-center' / 'tasks.json'
CANDIDATE_DIR = WORKSPACE / 'memory' / 'auto-candidates'
BACKUP_LOG = Path('/tmp/backup_cron.log')
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


def run(cmd: list[str], timeout: int = 20) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(WORKSPACE))
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        return 1, '', str(e)


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


def get_cc_model() -> str:
    if not CC_MODEL_SCRIPT.exists():
        return '未知'
    code, out, _ = run(['bash', str(CC_MODEL_SCRIPT), 'status'], timeout=20)
    if code != 0 or not out:
        return '未知'
    m = re.search(r'模型:\s*([^\n]+)', out)
    if not m:
        return '未知'
    raw = m.group(1).strip()
    mapping = {
        'gpt-5.4': 'Feinian / GPT-5.4',
        'deepseek-v4-flash': 'DeepSeek / V4 Flash',
        'MiniMax-M2.7': 'MiniMax / M2.7',
    }
    return mapping.get(raw, raw)


def get_backup_summary() -> tuple[str, str]:
    parts = []
    risk = ''

    if BACKUP_LOG.exists():
        t = datetime.fromtimestamp(BACKUP_LOG.stat().st_mtime).strftime('%m-%d %H:%M')
        parts.append(f'本地备份 {t}')
    else:
        parts.append('本地备份缺失')
        risk = '未找到本地备份日志'

    if CLOUD_BACKUP_LOG.exists():
        t = datetime.fromtimestamp(CLOUD_BACKUP_LOG.stat().st_mtime).strftime('%m-%d %H:%M')
        parts.append(f'云端同步 {t}')
        try:
            tail = '\n'.join(CLOUD_BACKUP_LOG.read_text(errors='ignore').splitlines()[-8:])
            if '远程端当前备份数量: 0' in tail:
                risk = '云端同步跑了，但远程端数量为 0'
        except Exception:
            pass
    else:
        parts.append('云端同步缺失')
        if not risk:
            risk = '未找到云端同步日志'

    return '｜'.join(parts), risk


def get_health_summary() -> tuple[str, int, str]:
    if not HEALTH_SCRIPT.exists():
        return '健康检查脚本缺失', 1, '健康检查脚本缺失'
    try:
        proc = subprocess.run(
            ['python3', str(HEALTH_SCRIPT), '--summary'],
            capture_output=True,
            text=True,
            timeout=45,
            cwd=str(WORKSPACE),
        )
        if proc.returncode != 0:
            return '健康检查执行失败', 1, '健康检查执行失败'
        lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
        if not lines:
            return '健康检查无输出', 1, '健康检查无输出'
        summary_line = next((x for x in lines if x.startswith('总览：')), '')
        risk_index = next((i for i, x in enumerate(lines) if x.startswith('风险：')), -1)
        risk_line = ''
        if risk_index >= 0 and risk_index + 1 < len(lines):
            risk_line = lines[risk_index + 1].lstrip('- ').strip()
        warn = 0
        fail = 0
        m = re.search(r'✅(\d+)\s*⚠️(\d+)\s*❌(\d+)', summary_line)
        if m:
            warn = int(m.group(2))
            fail = int(m.group(3))
        risk_count = warn + fail
        parts = []
        if summary_line:
            parts.append(summary_line)
        if risk_line:
            parts.append(f'关注：{risk_line}')
        return ' ｜ '.join(parts) if parts else lines[0], risk_count, risk_line
    except Exception:
        return '健康检查读取异常', 1, '健康检查读取异常'


def resolve_openclaw_model_label(model: str = '') -> str:
    mapping = {
        'feinian/gpt-5.4': 'Feinian / GPT-5.4',
        'deepseek/deepseek-v4-flash': 'DeepSeek / V4 Flash',
        'minimax-cn/MiniMax-M2.7': 'MiniMax / M2.7',
        '5.4mini': '5.4mini',
    }
    if not model:
        return '当前会话'
    return mapping.get(model, model)


def build_card(open_id: str = DEFAULT_OPEN_ID, oc_model_raw: str = '') -> dict:
    today = date.today().strftime('%Y-%m-%d')
    tasks = load_tasks()
    candidates = load_candidates(today)
    candidate_by_state = Counter(x.get('state', 'new') for x in candidates)

    blocked_count = sum(1 for t in tasks if t.get('status') == 'blocked')
    high_count = sum(1 for t in tasks if t.get('status') == 'todo' and t.get('priority') == 'high')
    doing_count = sum(1 for t in tasks if t.get('status') == 'doing')

    oc_model = resolve_openclaw_model_label(oc_model_raw)
    cc_model = get_cc_model()
    backup_summary, backup_risk = get_backup_summary()
    health_summary, health_risk_count, health_risk = get_health_summary()

    top_fields = [
        f'**当前会话模型**\n{oc_model}',
        f'**Claude Code 模型**\n{cc_model}',
        f'**阻塞 / 高优**\n{blocked_count} / {high_count}',
        f'**进行中 / Inbox**\n{doing_count} / {candidate_by_state.get("new", 0)}',
        f'**健康风险数**\n{health_risk_count}',
        f'**最近备份**\n{backup_summary}',
    ]

    quick_focus = []
    if blocked_count:
        quick_focus.append(f'阻塞 {blocked_count} 条')
    if high_count:
        quick_focus.append(f'高优先级 {high_count} 条')
    if health_risk_count:
        quick_focus.append(f'健康风险 {health_risk_count} 项')
    if backup_risk:
        quick_focus.append('备份需复查')
    focus_text = '｜'.join(quick_focus) if quick_focus else '当前无明显高优先级风险'

    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': f'🕹️ 主控制台 V2 | {today}'},
            'template': 'turquoise'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': f'**今日焦点**：{focus_text}'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '今日重点建议'}, 'type': 'primary', 'value': quick_action('focus panel card', 'feishu.quick_actions.focus_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '主控制台'}, 'type': 'default', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
            ]},
            {'tag': 'div', 'fields': [
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': x}} for x in top_fields
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**🧠 模型区**'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '模型面板'}, 'type': 'primary', 'value': quick_action('model panel card', 'feishu.quick_actions.model_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'OpenClaw 模型卡'}, 'type': 'default', 'value': quick_action('openclaw model card', 'feishu.quick_actions.cockpit_oc_model', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'Claude Code 模型卡'}, 'type': 'default', 'value': quick_action('cc model card', 'feishu.quick_actions.cockpit_cc_model', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '会话状态'}, 'type': 'default', 'value': quick_action('/status', 'feishu.quick_actions.oc_status', open_id=open_id)},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**📋 任务区**'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '任务面板'}, 'type': 'primary', 'value': quick_action('task panel card', 'feishu.quick_actions.task_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '工作台总览'}, 'type': 'default', 'value': quick_action('workspace card', 'feishu.quick_actions.cockpit_workspace', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '待处理 Inbox'}, 'type': 'default', 'value': quick_action('inbox card', 'feishu.quick_actions.inbox', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '阻塞'}, 'type': 'default', 'value': quick_action('blocked card', 'feishu.quick_actions.blocked', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '高优先级'}, 'type': 'default', 'value': quick_action('high card', 'feishu.quick_actions.high', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '摘要'}, 'type': 'default', 'value': quick_action('digest card', 'feishu.quick_actions.digest', open_id=open_id)},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**⚡ 快捷动作区**'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '快捷动作面板'}, 'type': 'primary', 'value': quick_action('quick actions panel card', 'feishu.quick_actions.quick_actions_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '全面检查'}, 'type': 'default', 'value': quick_action('healthcheck summary', 'feishu.quick_actions.healthcheck', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'Inbox'}, 'type': 'default', 'value': quick_action('inbox card', 'feishu.quick_actions.inbox', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '切 Feinian'}, 'type': 'default', 'value': quick_action('/model feinian', 'feishu.quick_actions.oc_model_feinian', open_id=open_id)},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**🧠 记忆区**'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '记忆面板'}, 'type': 'primary', 'value': quick_action('memory panel card', 'feishu.quick_actions.memory_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'Inbox'}, 'type': 'default', 'value': quick_action('inbox card', 'feishu.quick_actions.inbox', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '摘要'}, 'type': 'default', 'value': quick_action('digest card', 'feishu.quick_actions.digest', open_id=open_id)},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**🩺 系统区**'}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': health_summary}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '系统面板'}, 'type': 'primary', 'value': quick_action('system panel card', 'feishu.quick_actions.system_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '全面检查'}, 'type': 'default', 'value': quick_action('healthcheck summary', 'feishu.quick_actions.healthcheck', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '备份状态'}, 'type': 'default', 'value': quick_action('backup status', 'feishu.quick_actions.backup_status', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '帮助'}, 'type': 'default', 'value': quick_action('/help', 'feishu.quick_actions.help', open_id=open_id)},
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': f'备份：{backup_summary}'}
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': 'V2 目标：先做状态化首页，再继续拆模型/任务/系统专题面板。'}
            ]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='总驾驶台互动卡片生成器 V2')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--oc-model', default='')
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.open_id, args.oc_model)
    out = OUTPUT_DIR / 'cockpit-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
