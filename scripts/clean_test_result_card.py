#!/usr/bin/env python3
"""清理测试任务结果卡片生成器"""
import argparse, json
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


def build_result_card(task: str, open_id: str = DEFAULT_OPEN_ID, removed: bool = True) -> dict:
    title = '✅ 清理成功' if removed else '⚠️ 清理结果待确认'
    template = 'green' if removed else 'orange'
    result_text = '已从活跃测试任务列表移除' if removed else '执行完成，请复查活跃测试任务列表'
    return {
        'header': {'title': {'tag': 'plain_text', 'content': title}, 'template': template},
        'elements': [
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': (
                f'**测试任务清理完成**\n\n'
                f'- 任务：`{task}`\n'
                f'- 结果：{result_text}\n'
                f'- 日志文件：保留\n'
                f'- 正式任务：未触碰'
            )}},
            {'tag': 'hr'},
            {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '现在可以回到清理面板复查，或直接回主控制台继续操作。'}},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '返回清理面板'}, 'type': 'primary', 'value': quick_action('clean test tasks panel card', 'feishu.quick_actions.clean_test_tasks_panel', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '← 模型与控制'}, 'type': 'default', 'value': quick_action('model_control_hub card', 'feishu.quick_actions.model_control_hub', open_id=open_id)},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '⌂ 主控制台'}, 'type': 'default', 'value': quick_action('cockpit card', 'feishu.quick_actions.cockpit_home', open_id=open_id)},
            ]},
        ]
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', required=True)
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--save', action='store_true')
    args = parser.parse_args()
    card = build_result_card(args.task, args.open_id)
    if args.save:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        safe = args.task.replace('-', '_')
        out = OUTPUT_DIR / f'clean-result-{safe}.json'
        out.write_text(json.dumps(card, ensure_ascii=False, indent=2))
        print(f'✅ 已保存: {out}')
    else:
        print(json.dumps(card, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
