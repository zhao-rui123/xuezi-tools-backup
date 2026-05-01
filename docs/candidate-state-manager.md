# 候选状态管理器

## 目标
管理 `memory/auto-candidates/YYYY-MM-DD.json` 中候选项的处理状态，避免候选越积越乱。

## 脚本
- `scripts/candidate_state_manager.py`

## 状态
- `new`：新候选，未处理
- `imported`：已导入任务中心
- `ignored`：已忽略

## 用法

### 查看统计
```bash
python3 scripts/candidate_state_manager.py stats --day 2026-05-01
```

### 查看候选列表
```bash
python3 scripts/candidate_state_manager.py list --day 2026-05-01
python3 scripts/candidate_state_manager.py list --day 2026-05-01 --state imported
```

### 手动标记
```bash
python3 scripts/candidate_state_manager.py mark-imported --day 2026-05-01 --dedupe-key <key> --task-id <task_id>
python3 scripts/candidate_state_manager.py mark-ignored --day 2026-05-01 --dedupe-key <key>
```

## 当前接入
- `task_center.py import-candidates` 会尝试自动回写 imported
- `memory_task_flow.py run` 会尝试自动回写 imported
