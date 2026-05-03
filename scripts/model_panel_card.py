#!/usr/bin/env python3
"""
模型面板卡片生成器 V1

聚焦：
- OpenClaw 当前会话模型
- Claude Code 当前模型
- 两条模型链路的快捷切换入口
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

WORKSPACE = Path('/Users/zhaoruicn/.openclaw/workspace')
OUTPUT_DIR = WORKSPACE / 'summary' / 'cards'
DEFAULT_OPEN_ID = 'ou_5a7b7ec0339ffe0c1d5bb6c5bc162579'
DEFAULT_EXPIRES_AT = 1893456000000
CC_MODEL_SCRIPT = WORKSPACE / 'scripts' / 'cc-model-switch.sh'


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


def resolve_openclaw_model_label(model: str = '') -> str:
    mapping = {
        'feinian/gpt-5.4': 'Feinian / GPT-5.4',
        'deepseek/deepseek-v4-flash': 'DeepSeek / V4 Flash',
        'minimax-cn/MiniMax-M2.7': 'MiniMax / M2.7',
        '5.4mini': '5.4mini',
    }
    return mapping.get(model, model or '当前会话')


def get_cc_model() -> str:
    if not CC_MODEL_SCRIPT.exists():
        return '未知'
    code, out, _ = run(['bash', str(CC_MODEL_SCRIPT), 'status'])
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


def build_card(open_id: str = DEFAULT_OPEN_ID, oc_model_raw: str = '') -> dict:
    oc_model = resolve_openclaw_model_label(oc_model_raw)
    cc_model = get_cc_model()
    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': '🧠 模型面板 V1'},
            'template': 'purple'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**模型总览**：把 OpenClaw 会话模型和 Claude Code 模型收成一个专题面板。'}},
            {'tag': 'div', 'fields': [
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**OpenClaw 当前会话**\n{oc_model}'}},
                {'tag': 'field', 'text': {'tag': 'lark_md', 'content': f'**Claude Code 当前模型**\n{cc_model}'}},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**OpenClaw 会话模型**\n- 作用范围：只影响当前飞书会话\n- 常用：Feinian / DeepSeek / MiniMax / 5.4mini'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'OpenClaw 模型卡'}, 'type': 'primary', 'value': quick_action('openclaw model card', 'feishu.quick_actions.cockpit_oc_model', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '切 Feinian'}, 'type': 'default', 'value': quick_action('/model feinian', 'feishu.quick_actions.oc_model_feinian', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '切 DeepSeek'}, 'type': 'default', 'value': quick_action('/model deepseek', 'feishu.quick_actions.oc_model_deepseek', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '切 MiniMax'}, 'type': 'default', 'value': quick_action('/model minimax', 'feishu.quick_actions.oc_model_minimax', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '切 5.4mini'}, 'type': 'default', 'value': quick_action('/model 5.4mini', 'feishu.quick_actions.oc_model_5_4mini', open_id=open_id)},
            ]},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**Claude Code 模型**\n- 作用范围：本地 Claude Code 默认环境\n- 当前支持：Feinian / DeepSeek / MiniMax'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'Claude Code 模型卡'}, 'type': 'primary', 'value': quick_action('cc model card', 'feishu.quick_actions.cockpit_cc_model', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'CC 切 Feinian'}, 'type': 'default', 'value': quick_action('cc model feinian', 'feishu.quick_actions.cc_model_feinian', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'CC 切 DeepSeek'}, 'type': 'default', 'value': quick_action('cc model deepseek', 'feishu.quick_actions.cc_model_deepseek', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'CC 切 MiniMax'}, 'type': 'default', 'value': quick_action('cc model minimax', 'feishu.quick_actions.cc_model_minimax', open_id=open_id)},
            ]},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '查看会话状态'}, 'type': 'default', 'value': quick_action('/status', 'feishu.quick_actions.oc_status', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '查看 CC 当前'}, 'type': 'default', 'value': quick_action('cc model status', 'feishu.quick_actions.cc_model_status', open_id=open_id)},
            ]},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '← 模型与控制'}, 'type': 'default', 'value': quick_action('model_control_hub card', 'feishu.quick_actions.model_control_hub', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '⌂ 主控制台'}, 'type': 'default', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': '下一步可以继续做记忆面板或快捷动作面板。'}
            ]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='模型面板卡片生成器 V1')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--oc-model', default='')
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.open_id, args.oc_model)
    out = OUTPUT_DIR / 'model-panel-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
