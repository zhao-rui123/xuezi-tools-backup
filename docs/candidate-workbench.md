# 候选工作台

## 目标
给 `memory/auto-candidates/YYYY-MM-DD.json` 提供一个可操作的工作台视图，不删除原始数据，只做状态管理和整理预览。

## 脚本
- `scripts/candidate_state_manager.py`

## 新增能力

### 待处理 inbox
```bash
python3 scripts/candidate_state_manager.py inbox --day 2026-05-01
python3 scripts/candidate_state_manager.py inbox --day 2026-05-01 --type risk
```

### 整理预览
```bash
python3 scripts/candidate_state_manager.py cleanup-preview --day 2026-05-01
```

### 批量忽略
```bash
python3 scripts/candidate_state_manager.py mark-batch-ignored --day 2026-05-01 --type rule
```

## 原则
- 不删除原始候选
- 只通过 `state` 管理候选生命周期
- inbox 只聚焦 `state=new`
- cleanup-preview 只做预览，不做 destructive 操作
