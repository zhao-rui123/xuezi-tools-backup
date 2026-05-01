# screen 详情面板 V1

## 目标
把 screen / agent-screen 任务继续下钻，展示执行细节：
- 业务任务名
- 执行方式
- 状态
- 工作目录
- 日志文件
- 启动时间

## 脚本
- `scripts/screen_detail_panel_card.py`

## 输出
- `summary/cards/screen-detail-panel-card.json`

## 设计原则
1. 先以 agent-screen meta 为准
2. 优先显示业务任务名和执行方式
3. 后续再补日志摘要、screen 存活状态
