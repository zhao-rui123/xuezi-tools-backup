#!/usr/bin/env python3
"""
重跑执行规范卡片 V1

目标：
- 给“重跑测试任务”建立执行边界
- 明确允许范围、触发方式、状态回写、失败反馈
- 作为真实执行前的最后一层规则
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

WORKSPACE = Path('/Users/zhaoruicn/.openclaw/workspace')
OUTPUT_DIR = WORKSPACE / 'summary' / 'cards'
DEFAULT_OPEN_ID = 'ou_5a7b7ec0339ffe0c1d5bb6c5bc162579'
DEFAULT_EXPIRES_AT = 1893456000000


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


def build_card(open_id: str = DEFAULT_OPEN_ID) -> dict:
    return {
        'header': {
            'title': {'tag': 'plain_text', 'content': '📐 重跑执行规范 V1'},
            'template': 'grey'
        },
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**目标**：在接真正的“重跑测试任务”前，把安全边界和执行规则先定清楚。'}},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**1. 允许重跑的范围**\n- 仅限测试任务\n- 仅限 screen / agent-screen 可识别任务\n- 不碰正式项目任务\n- 不碰 ACP 正式线程\n- 不碰定时任务'}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**2. 触发方式（建议）**\n- 优先复用原 `agent-screen-run.sh` 链路\n- 复用 meta 中已有的 `AGENT / WORKDIR / PROMPT_FILE / PATTERN` 信息\n- 如果 prompt 文件缺失，则不允许直接重跑'}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**3. 二次确认规则**\n- 第一层：从“重跑测试任务”面板选中目标\n- 第二层：确认卡再次显示任务名 / 工作目录 / 执行方式\n- 只有二次确认后，才允许触发真实重跑'}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**4. 状态回写（建议）**\n- 控制台里显示：已触发 / 进行中 / 完成 / 失败\n- 历史中心里新增一条“重跑记录”\n- 不覆盖旧任务，只追加新的一次执行记录'}},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**5. 失败反馈（建议）**\n- 如果脚本未找到 → 直接提示不可重跑\n- 如果 prompt 文件缺失 → 直接提示缺关键上下文\n- 如果执行启动失败 → 返回失败状态，不静默\n- 如果已成功启动 → 明确回显“已触发重跑”'}},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**当前建议结论**\n先做最小闭环：\n1. 只支持重跑 `cc-min-test / cc-wrapper-test / codex-wrapper-test`\n2. 只支持有完整 meta + prompt 文件的任务\n3. 先用追加历史记录，而不是覆盖旧状态'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '重跑测试任务面板'}, 'type': 'primary', 'value': quick_action('rerun test tasks panel card', 'feishu.quick_actions.rerun_test_tasks_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '轻控制入口'}, 'type': 'default', 'value': quick_action('light control panel card', 'feishu.quick_actions.light_control_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '主控制台'}, 'type': 'default', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
            ]},
            {'tag': 'note', 'elements': [
                {'tag': 'plain_text', 'content': '下一步如果继续，就可以按这份规范把“重跑测试任务 V3（真正触发版）”接上。'}
            ]}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='重跑执行规范卡片 V1')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.open_id)
    out = OUTPUT_DIR / 'rerun-execution-policy-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已生成: {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
