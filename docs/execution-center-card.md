# 执行中心卡片 V1

## 目标
把 ACP / 子会话 / screen / 本地后台任务统一纳入一个执行中心面板。

## 脚本
- `scripts/execution_center_card.py`

## 输出
- `summary/cards/execution-center-card.json`

## 当前内容
- 主会话模型
- 活跃任务概览
- ACP / 子线程数量
- screen 会话数量
- 可见 ACP / screen 列表（运行时注入）

## 设计原则
1. 先做只读总览，再考虑控制操作
2. 运行时数据由工具注入，不在脚本里写死来源
3. 后续再补日志入口、停止/恢复入口
