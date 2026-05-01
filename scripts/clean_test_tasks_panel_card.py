#!/usr/bin/env python3
"""
清理测试任务面板 V1

目标：
- 列出可安全清理的测试任务
- 只列出测试任务，不碰正式任务
- 点确认后才真正清理
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

WORKSPACE = Path('/Users/zhaoruicn/.openclaw/workspace')
OUTPUT_DIR = WORKSPACE / 'summary' / 'cards'
DEFAULT_OPEN_ID = 'ou_5a7b7ec0339ffe0c1d5bb6c5bc162579'
DEFAULT_EXPIRES_AT = 1893456000000
AGENT_SCREEN_DIR = WORKSPACE / 'logs' / 'agent-screen'
ALLOWED = {'cc-min-test','cc-wrapper-test','codex-wrapper-test'}

def quick_action(command: str, action: str, open_id: str = DEFAULT_OPEN_ID) -> dict:
    return {'oc':'ocf1','k':'quick','a':action,'q':command,
            'c':{'u':open_id,'e':DEFAULT_EXPIRES_AT,'t':'p2p'}}

def load_cleanable() -> list[dict]:
    items = []
    if not AGENT_SCREEN_DIR.exists():
        return items
    for meta in sorted(AGENT_SCREEN_DIR.glob('*.meta'), key=lambda p: p.stat().st_mtime, reverse=True):
        task = meta.stem
        if task in ALLOWED:
            kv = {}
            for line in meta.read_text(errors='ignore').splitlines():
                if '=' in line:
                    k,v = line.split('=',1)
                    kv[k.strip()] = v.strip().strip("'")
            items.append({
                'task_name': task,
                'agent': kv.get('AGENT','?'),
                'started_at': kv.get('STARTED_AT','?'),
                'workdir': kv.get('WORKDIR','?'),
                'log_file': Path(kv.get('LOG_FILE','')).name,
            })
    return items

def build_card(open_id: str = DEFAULT_OPEN_ID) -> dict:
    items = load_cleanable()
    blocks = []
    for item in items:
        blocks.append({
            'tag': 'div', 'text': {'tag': 'lark_md', 'content':
                f"**{item['task_name']}**\n"
                f"- Agent：{item['agent']}\n"
                f"- 启动时间：{item['started_at']}\n"
                f"- 工作目录：{Path(item['workdir']).name}"}
        })
        blocks.append({
            'tag': 'action', 'actions': [
                {'tag':'button', 'text':{'tag':'plain_text','content':f'确认清理 {item["task_name"]}'},
                 'type':'primary',
                 'value': quick_action(f'clean confirm {item["task_name"]}', 'feishu.quick_actions.clean_test_confirm', open_id=open_id)},
            ]
        })
    if not blocks:
        blocks.append({'tag':'div','text':{'tag':'lark_md','content':'**没有可清理的测试任务。**'}})

    return {
        'header': {'title':{'tag':'plain_text','content':'🗑️ 清理测试任务 V1'},'template':'orange'},
        'elements': [
            {'tag':'div','text':{'tag':'lark_md','content':'**说明**：这里只列出测试任务，正式任务不在范围内。清理后会从“活跃测试任务”列表中移除，但日志文件保留。'}},
            {'tag':'hr'},
            *blocks,
            {'tag':'hr'},
            {'tag':'action','actions':[
                {'tag':'button','text':{'tag':'plain_text','content':'轻控制入口'},'type':'default',
                 'value': quick_action('light control panel card','feishu.quick_actions.light_control_panel',open_id=open_id)},
                {'tag':'button','text':{'tag':'plain_text','content':'主控制台'},'type':'default',
                 'value': quick_action('cockpit card','feishu.quick_actions.cockpit_home',open_id=open_id)},
            ]},
            {'tag':'note','elements':[{'tag':'plain_text','content':'下一步：扩清理执行脚本 + 结果卡'}]},
        ]
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    parser.add_argument('--print', action='store_true')
    args = parser.parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(args.open_id)
    out = OUTPUT_DIR / 'clean-test-tasks-panel-card.json'
    out.write_text(json.dumps(card, ensure_ascii=False, indent=2))
    print(f'✅ {out}')
    if args.print:
        print(json.dumps(card, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
