# 飞书工作台卡片 V1

## 目标
把工作台摘要映射成飞书 interactive card，先提供稳定静态总览，再考虑后续按钮动作处理。

## 脚本
- `scripts/workspace_dashboard_card.py`

## 用法
```bash
python3 scripts/workspace_dashboard_card.py generate --day 2026-05-01 --print
```

## 输出位置
- `summary/cards/YYYY-MM-DD-dashboard-card.json`

## 当前内容
- 总览统计
- 待处理候选
- 当前阻塞
- 当前进行中
- 高优先级待办
- 今日自动导入
- 预留按钮：查看 Inbox / 查看阻塞 / 查看高优先级
