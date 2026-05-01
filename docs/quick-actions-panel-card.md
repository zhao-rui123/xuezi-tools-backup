# 快捷动作面板卡片 V1

## 目标
把最常用的执行动作集中成一张操作卡，减少在多个专题面板之间来回跳转。

## 脚本
- `scripts/quick_actions_panel_card.py`

## 输出
- `summary/cards/quick-actions-panel-card.json`

## 当前动作分组
- 系统动作：全面检查 / 备份状态 / 会话状态 / 系统面板
- 任务动作：Inbox / 阻塞 / 高优先级 / 摘要 / 任务面板
- 模型动作：切 OpenClaw 模型 / 切 Claude Code 模型 / 模型面板
- 导航动作：主控制台 / 记忆面板 / 工作台总览

## 设计原则
1. 这是操作面板，不是状态面板
2. 先收高频动作，再考虑个性化排序
3. 继续复用已打通的 quick action 命令
