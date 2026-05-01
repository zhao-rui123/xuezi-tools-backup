# ACP 语义任务面板 V1

## 目标
把 ACP 子线程从纯技术 key/sessionId 转成更可读的任务展示：
- 任务名（保守标签）
- 执行方式
- 状态
- 最近时间

## 脚本
- `scripts/acp_semantic_panel_card.py`

## 输出
- `summary/cards/acp-semantic-panel-card.json`

## 设计原则
1. 先保守，不硬猜具体业务任务
2. 至少先把执行方式明确成 ACP / Claude Code
3. 后续如果拿到更多元数据，再把“子线程 1/2”升级成真正业务任务名
