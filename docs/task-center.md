# 统一任务中心（最小可用版）

## 目标
先落一个本地可用的任务中心，统一管理：
- 答应过要做的事
- 进行中 / 阻塞 / 已完成
- 今日关注任务

当前版本只做最小能力：
- 本地 JSON 存储
- CLI 增删改查
- 不直接接消息路由，不改现有 heartbeat / memory 主链路

## 文件位置
- 脚本：`scripts/task_center.py`
- 数据：`projects/task-center/tasks.json`

## 用法

### 1. 新增任务
```bash
python3 scripts/task_center.py add "整理 OpenClaw 功能路线图" --priority high --project openclaw --due-date 2026-05-01
```

### 2. 查看全部未归档任务
```bash
python3 scripts/task_center.py list
```

### 3. 按状态筛选
```bash
python3 scripts/task_center.py list --status doing
python3 scripts/task_center.py list --status blocked
```

### 4. 查看今日关注任务
```bash
python3 scripts/task_center.py today
```

### 5. 标记状态
```bash
python3 scripts/task_center.py doing <task_id> --note "开始处理"
python3 scripts/task_center.py block <task_id> "等用户确认" --note "先暂停"
python3 scripts/task_center.py done <task_id> --note "已完成并验证"
python3 scripts/task_center.py reopen <task_id> --note "重新打开"
python3 scripts/task_center.py archive <task_id> --note "已归档"
```

### 6. 查看单个任务详情
```bash
python3 scripts/task_center.py show <task_id>
```

## 当前状态字段
- `todo`：待处理
- `doing`：进行中
- `blocked`：阻塞
- `done`：完成
- `archived`：归档

## 候选层导入（已支持）
现在任务中心已支持从 `memory/auto-candidates/` 导入：
- `todo`
- `blocked`
- `progress`

### 导入命令
```bash
python3 scripts/task_center.py import-candidates --day 2026-05-01 --high-priority-todo
```

说明：
- 按 `dedupe_key` 去重，重复导入不会重复建任务
- `blocked` 会自动变成阻塞任务
- `progress` 会自动变成进行中任务
- `todo` 可选择导入为高优先级

## 下一步建议
后续可以逐步接入：
1. 从对话自动抽取待办并自动写入候选层
2. 后台任务完成后自动写回任务状态
3. 飞书卡片展示任务中心
