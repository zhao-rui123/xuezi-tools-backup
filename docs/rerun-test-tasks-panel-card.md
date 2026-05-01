# 重跑测试任务面板 V1

## 目标
从控制动作分级里挑一个最安全的试点：只针对测试任务的“重跑候选”。

## 脚本
- `scripts/rerun_test_tasks_panel_card.py`

## 输出
- `summary/cards/rerun-test-tasks-panel-card.json`

## 当前阶段
- 先列出可重跑候选
- 暂不直接执行
- 真执行前需要二次确认

## 设计原则
1. 只碰测试任务
2. 不碰正式项目任务
3. 先让规则清晰，再接控制按钮
