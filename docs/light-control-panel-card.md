# 轻控制入口卡片 V1

## 目标
在不引入危险操作的前提下，提供一层轻控制：
- 查看详情
- 跳转面板
- 返回主控台

## 脚本
- `scripts/light_control_panel_card.py`

## 输出
- `summary/cards/light-control-panel-card.json`

## 设计原则
1. 只做低风险控制，不做停任务/重跑
2. 先把跳转链路统一顺
3. 后续如需强控制，再单独拆权限和风险策略
