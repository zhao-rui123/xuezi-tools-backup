#!/usr/bin/env python3
"""主控制台 V5 Hub - 带二级标题的两级导航"""
from pathlib import Path
import json

OUT = Path('/Users/zhaoruicn/.openclaw/workspace/summary/cards/cockpit-v5-hub.json')
DEFAULT_OPEN_ID = 'ou_5a7b7ec0339ffe0c1d5bb6c5bc162579'

def qa(cmd, action):
    return {'oc':'ocf1','k':'quick','a':action,'q':cmd,
            'c':{'u':DEFAULT_OPEN_ID,'e':1893456000000,'t':'p2p'}}

HUBS = [
    ('⚡','执行链路','execution_hub',[
        '执行中心 | 语义任务面板 | ACP | screen详情 | 重跑测试任务 | 任务历史 | 后台任务中心'
    ]),
    ('📋','任务与记忆','task_hub',[
        '任务面板 | 记忆面板 | 今日重点 | 阻塞 | 高优先级 | Inbox | 摘要'
    ]),
    ('🩺','系统与定时','system_hub',[
        '系统面板 | 定时任务中心 | 健康检查 | 备份状态'
    ]),
    ('🤖','模型与控制','model_control_hub',[
        '模型面板 | 切换CC模型 | 轻控制入口 | 重跑测试任务 | 清理测试任务 | 会话状态'
    ]),
    ('🔧','快捷','quick_hub',[
        '快捷动作面板 | 主控制台 | 会话状态 | 帮助'
    ]),
]

elements = [
    {'tag':'div','text':{'tag':'lark_md','content':'**🕹️ 主控制台 V5**  两级导航 — 点按钮进专题，文字说明二级内容'}},
    {'tag':'hr'},
]

for icon, name, key, sub_labels in HUBS:
    elements.append({
        'tag': 'action', 'actions': [
            {'tag':'button','text':{'tag':'plain_text','content':f'{icon} {name}'},'type':'primary','value':qa(f'{key} card',f'feishu.quick_actions.{key}')}
        ]
    })
    for label in sub_labels:
        elements.append({'tag':'div','text':{'tag':'lark_md','content':f'  → {label}'}})

elements.append({'tag':'hr'})
elements.append({'tag':'div','text':{'tag':'lark_md','content':'直接发送专题名称也可，如：“执行中心”“系统面板”“重跑测试任务”'}})

card = {'header':{'title':{'tag':'plain_text','content':'🕹️ 主控制台 V5'},'template':'turquoise'},'elements':elements}
OUT.write_text(json.dumps(card, ensure_ascii=False, indent=2))
print(f'✅ {OUT}')
