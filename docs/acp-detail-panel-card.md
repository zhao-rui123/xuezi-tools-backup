# ACP / 子线程详情卡片 V1

## 目标
把执行中心里的 ACP 子线程从“数量”升级成“明细视图”。

## 脚本
- `scripts/acp_detail_panel_card.py`

## 输出
- `summary/cards/acp-detail-panel-card.json`

## 当前内容
- key
- sessionId
- 最近更新时间
- session 文件名

## 设计原则
1. 先用现有 `~/.openclaw/agents/claude-code/sessions/sessions.json` 做只读详情
2. 不做线程控制操作，只做观察和导航
3. 后续再补日志入口、screen 详情、后台任务历史
