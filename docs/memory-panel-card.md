# 记忆面板卡片 V1

## 目标
把记忆候选层从主控制台首页拆成专题面板，集中展示：
- 今日候选数
- Inbox / imported / ignored
- 风险 / 规则 / 待办 / 进展候选

## 脚本
- `scripts/memory_panel_card.py`

## 输出
- `summary/cards/memory-panel-card.json`

## 按钮
- 记忆面板（从主控制台进入）
- Inbox
- 摘要
- 任务面板
- 返回主控台

## 设计原则
1. 记忆候选先看状态与类型，再决定导入或忽略
2. 优先突出风险 / 规则类候选
3. 保持与任务面板联动，但不直接污染 MEMORY.md
