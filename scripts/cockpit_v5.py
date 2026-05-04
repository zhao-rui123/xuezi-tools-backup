#!/usr/bin/env python3
"""
主控制台 V5 - 两级导航

Level 1: 5个一级入口
Level 2: 每个入口对应的专题面板
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

WORKSPACE = Path('/Users/zhaoruicn/.openclaw/workspace')
OUTPUT_DIR = WORKSPACE / 'summary' / 'cards'
DEFAULT_OPEN_ID = 'ou_5a7b7ec0339ffe0c1d5bb6c5bc162579'
DEFAULT_EXPIRES_AT = 1893456000000

def qa(cmd, action):
    return {'oc':'ocf1','k':'quick','a':action,'q':cmd,
            'c':{'u':DEFAULT_OPEN_ID,'e':DEFAULT_EXPIRES_AT,'t':'p2p'}}

CATEGORIES = [
    ('⚡', '执行链路', 'execution_hub', 'feishu.quick_actions.exec_hub', [
        ('🚦 执行中心', 'execution center card', 'feishu.quick_actions.execution_center'),
        ('🧭 语义任务面板', 'semantic execution panel card', 'feishu.quick_actions.semantic_execution_panel'),
        ('🔌 ACP 语义面板', 'acp semantic panel card', 'feishu.quick_actions.acp_semantic_panel'),
        ('📺 screen 详情', 'screen detail panel card', 'feishu.quick_actions.screen_detail_panel'),
        ('♻️ 重跑测试任务', 'rerun test tasks panel card', 'feishu.quick_actions.rerun_test_tasks_panel'),
        ('📋 任务历史中心', 'task history panel card', 'feishu.quick_actions.task_history_panel'),
        ('⚙️ 后台任务中心', 'runtime tasks panel card', 'feishu.quick_actions.runtime_tasks_panel'),
    ]),
    ('📋', '任务与记忆', 'task_hub', 'feishu.quick_actions.task_hub', [
        ('📌 任务面板', 'task panel card', 'feishu.quick_actions.task_panel'),
        ('🧠 记忆面板', 'memory panel card', 'feishu.quick_actions.memory_panel'),
        ('🎯 今日重点建议', 'focus panel card', 'feishu.quick_actions.focus_panel'),
        ('🔒 阻塞', 'blocked card', 'feishu.quick_actions.blocked'),
        ('⭐ 高优先级', 'high card', 'feishu.quick_actions.high'),
        ('📥 待处理 Inbox', 'inbox card', 'feishu.quick_actions.inbox'),
        ('📰 摘要', 'digest card', 'feishu.quick_actions.digest'),
    ]),
    ('🩺', '系统与定时', 'system_hub', 'feishu.quick_actions.system_hub', [
        ('🩺 系统面板', 'system panel card', 'feishu.quick_actions.system_panel'),
        ('⏰ 定时任务中心', 'scheduled tasks panel card', 'feishu.quick_actions.scheduled_tasks_panel'),
        ('🔍 健康检查', 'healthcheck summary', 'feishu.quick_actions.healthcheck'),
        ('💾 备份状态', 'backup status', 'feishu.quick_actions.backup_status'),
    ]),
    ('🤖', '模型与控制', 'model_control_hub', 'feishu.quick_actions.model_control_hub', [
        ('🤖 模型面板', 'model panel card', 'feishu.quick_actions.model_panel'),
        ('🔄 切换 Claude Code 模型', 'cc model card', 'feishu.quick_actions.cockpit_cc_model'),
        ('🔄 OpenClaw 模型卡', 'openclaw model card', 'feishu.quick_actions.cockpit_oc_model'),
        ('🪄 轻控制入口', 'light control panel card', 'feishu.quick_actions.light_control_panel'),
        ('♻️ 重跑测试任务', 'rerun test tasks panel card', 'feishu.quick_actions.rerun_test_tasks_panel'),
        ('🗑️ 清理测试任务', 'clean test tasks panel card', 'feishu.quick_actions.clean_test_tasks_panel'),
        ('📊 会话状态', '/status', 'feishu.quick_actions.oc_status'),
    ]),
    ('🔧', '快捷', 'quick_hub', 'feishu.quick_actions.quick_hub', [
        ('⚡ 快捷动作面板', 'quick actions panel card', 'feishu.quick_actions.quick_actions_panel'),
        ('🕹️ 主控制台', 'cockpit card', 'feishu.quick_actions.cockpit_home'),
        ('❓ 帮助', '/help', 'feishu.quick_actions.help'),
    ]),
]

def build_hub():
    blocks = [
        {'tag':'div','text':{'tag':'lark_md','content':'**主控制台 V5 - 两级导航**  点下方按钮进入专题'}},
        {'tag':'hr'},
    ]
    for icon, name, key, action, subs in CATEGORIES:
        blocks.append({
            'tag': 'action', 'actions': [
                {'tag':'button','text':{'tag':'plain_text','content':f'{icon} {name}'},
                 'type':'primary','value': qa(f'{key} card', action)}
            ]
        })
    blocks.append({'tag':'hr'})
    blocks.append({
        'tag':'div','text':{'tag':'lark_md','content':'直接发送专题名称也可以，如：“执行中心”“系统面板”“重跑测试任务”'}})
    return {'header':{'title':{'tag':'plain_text','content':'🕹️ 主控制台 V5'},'template':'turquoise'},'elements':blocks}

def build_sub_panel(cat_key):
    cat = next((c for c in CATEGORIES if c[2] == cat_key), None)
    if not cat:
        return None
    icon, name, key, action, subs = cat
    blocks = [{'tag':'div','text':{'tag':'lark_md','content':f'**{icon} {name}** — 选择专题'}}]
    rows = []
    for i in range(0, len(subs), 2):
        row = subs[i:i+2]
        actions = []
        for label, cmd, act in row:
            actions.append({'tag':'button','text':{'tag':'plain_text','content':label},'type':'primary','value':qa(cmd,act)})
        if len(row) == 1:
            actions.append({'tag':'button','text':{'tag':'plain_text','content':'　'},'type':'default','value':qa('','feishu.quick_actions.nop')})
        blocks.append({'tag':'action','actions':actions})
    blocks.append({'tag':'hr'})
    blocks.append({'tag':'action','actions':[{'tag':'button','text':{'tag':'plain_text','content':'← 返回主控制台'},'type':'default','value':qa('cockpit card','feishu.quick_actions.cockpit_home')}]})
    return {'header':{'title':{'tag':'plain_text','content':f'{icon} {name}'},'template':'turquoise'},'elements':blocks}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hub', action='store_true')
    parser.add_argument('--sub', default='')
    parser.add_argument('--open-id', default=DEFAULT_OPEN_ID)
    args = parser.parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if args.hub:
        card = build_hub()
        out = OUTPUT_DIR / 'cockpit-v5-hub.json'
        out.write_text(json.dumps(card, ensure_ascii=False, indent=2))
        print(f'✅ {out}')
    elif args.sub:
        card = build_sub_panel(args.sub)
        if card:
            out = OUTPUT_DIR / f'cockpit-v5-{args.sub}.json'
            out.write_text(json.dumps(card, ensure_ascii=False, indent=2))
            print(f'✅ {out}')
        else:
            print(f'未知: {args.sub}')
    else:
        print('Usage: --hub or --sub <key>')

if __name__ == '__main__':
    main()
