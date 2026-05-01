# 控制动作分级卡片 V1

## 目标
为主控制台未来的“停任务 / 重跑 / 清理”能力先建立风险分级。

## 脚本
- `scripts/control_actions_policy_card.py`

## 输出
- `summary/cards/control-actions-policy-card.json`

## 分级
- P0：现在就能开放（低风险）
- P1：可做但需要确认（中风险）
- P2：后面再做（高风险）

## 设计原则
1. 先开查看和跳转
2. 再开测试任务级别的控制
3. 正式任务控制必须最后做
