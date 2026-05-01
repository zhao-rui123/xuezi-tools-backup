# 模型面板卡片 V1

## 目标
把模型相关能力从主控制台首页拆成专题面板，集中处理：
- OpenClaw 当前会话模型
- Claude Code 当前模型
- 两条链路的快捷切换入口

## 脚本
- `scripts/model_panel_card.py`

## 输出
- `summary/cards/model-panel-card.json`

## 按钮
- 模型面板（从主控制台进入）
- OpenClaw 模型卡
- Claude Code 模型卡
- OpenClaw 快捷切换按钮
- Claude Code 快捷切换按钮
- 查看状态
- 返回主控台

## 设计原则
1. 首页只保留当前模型摘要
2. 具体切换动作下钻到模型面板
3. 继续复用已打通的模型卡与 quick action 命令
