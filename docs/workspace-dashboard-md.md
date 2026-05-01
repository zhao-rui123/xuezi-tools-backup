# Markdown 工作台摘要

## 目标
生成一份稳定、可读、可复用的 markdown 工作台摘要，作为：
1. 人直接阅读
2. 后续飞书卡片层的数据来源

## 脚本
- `scripts/workspace_dashboard_md.py`

## 用法
```bash
python3 scripts/workspace_dashboard_md.py generate --day 2026-05-01 --print
```

## 输出位置
- `summary/dashboards/YYYY-MM-DD-dashboard.md`

## 当前内容
- 候选状态统计
- 候选类型分布
- 待处理候选 inbox
- 当前阻塞任务
- 当前进行中任务
- 高优先级待办
- 今日自动导入任务
