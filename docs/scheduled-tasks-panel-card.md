# 定时任务中心卡片 V1

## 目标
把自动跑的任务单独收成专题面板，便于主控制台统一查看：
- 每日备份
- 云端同步
- 股票推送
- 会话快照
- 周清理

## 脚本
- `scripts/scheduled_tasks_panel_card.py`

## 输出
- `summary/cards/scheduled-tasks-panel-card.json`

## 设计原则
1. 先看日志更新时间，不先改任务配置
2. 真实入口以 HEARTBEAT.md / 日志文件为准
3. 先做监控视图，再决定是否补“手动触发”类按钮
