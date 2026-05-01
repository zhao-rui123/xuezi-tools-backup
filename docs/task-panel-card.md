# 任务面板卡片 V1

## 目标
把任务区从主控制台首页拆成专题面板，集中展示：
- 当前阻塞
- 高优先级待办
- 待处理 Inbox
- 今日自动导入

## 脚本
- `scripts/task_panel_card.py`

## 输出
- `summary/cards/task-panel-card.json`

## 按钮
- 任务面板（从主控制台进入）
- 工作台总览
- Inbox
- 阻塞
- 高优先级
- 摘要
- 返回主控台

## 设计原则
1. 首页保留数字摘要，细节下钻到任务面板
2. 优先展示最该处理的内容，而不是完整列表
3. 继续复用已打通的 inbox / blocked / high / digest 命令
