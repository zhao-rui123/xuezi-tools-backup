# 重跑执行规范卡片 V1

## 目标
在真正接入“重跑测试任务”之前，先把安全边界和执行规则定清楚。

## 脚本
- `scripts/rerun_execution_policy_card.py`

## 输出
- `summary/cards/rerun-execution-policy-card.json`

## 规范核心
1. 允许范围：只限测试任务、只限 screen / agent-screen
2. 触发方式：优先复用原有 agent-screen 元数据
3. 二次确认：必须先确认任务名/工作目录/执行方式
4. 状态回写：追加新记录，不覆盖旧记录
5. 失败反馈：不能静默
