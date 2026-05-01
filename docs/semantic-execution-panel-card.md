# 任务语义执行面板 V2

## 目标
把后台任务从技术视角翻成业务任务视角：
- 这是什么任务
- 属于什么类型
- 现在什么状态
- 走哪条链路

## 脚本
- `scripts/semantic_execution_panel_card.py`

## 输出
- `summary/cards/semantic-execution-panel-card.json`

## 当前能力
- 基于 agent-screen meta 的 task_name / workdir 做规则映射
- 优先把项目路径翻成业务任务名
- 统一显示：**任务名｜执行方式｜状态｜最近时间**
- 先给出人话状态（如：已完成/测试、最近活跃）

## 设计原则
1. 雪子先看业务任务名，再看技术任务名
2. 先做规则映射，再考虑更智能的命名
3. 后续继续补 ACP 任务的业务语义映射
