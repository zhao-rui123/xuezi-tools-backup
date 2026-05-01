# 自动化触发入口 V1

## 目标
把以下流程串成一步：
1. 提炼候选
2. 保存候选
3. 导入任务中心
4. 输出 digest

## 脚本
- `scripts/memory_task_flow.py`

## 用法

### 直接传文本
```bash
python3 scripts/memory_task_flow.py run "待办：把这个链路接到对话入口。已经把候选层和任务中心打通。等我确认后再接飞书卡片。注意不要直接写 MEMORY.md。" --project openclaw --policy all-tasklike --high-priority-todo
```

### 从文件跑
```bash
python3 scripts/memory_task_flow.py run --file memory/2026-04-29.md --project openclaw
```

## 当前能力
- 自动提炼候选
- 自动写入 `memory/auto-candidates/YYYY-MM-DD.json`
- 自动按策略导入任务中心
- 自动输出整理视图

## 下一步
后续可接：
1. 对话消息自动触发
2. daily memory 定时扫描
3. 飞书卡片展示 digest
