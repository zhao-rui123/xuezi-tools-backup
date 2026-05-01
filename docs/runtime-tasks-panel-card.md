# 后台任务中心卡片 V1

## 目标
把执行侧能力纳入主控制台，先提供只读观察视图：
- 当前主会话状态
- 当前模型 / token / context
- 子会话 / ACP 线程数量
- 活跃任务概览

## 脚本
- `scripts/runtime_tasks_panel_card.py`

## 输出
- `summary/cards/runtime-tasks-panel-card.json`

## 设计原则
1. 先做稳定观察，不急着做线程控制
2. 当前动态值由运行时注入，不在脚本里硬编码来源
3. 后续可扩展为 ACP/子线程列表、停止/恢复入口
