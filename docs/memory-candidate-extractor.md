# 自动记忆提炼器 V1（候选层）

## 目标
先做低风险版本：
- 从文本中提取结构化记忆候选项
- 不直接写 `MEMORY.md`
- 不直接修改 daily memory 主文件
- 统一写到 `memory/auto-candidates/YYYY-MM-DD.json`

## 提炼类型
- `decision` 决策
- `todo` 待办
- `rule` 规则
- `progress` 进展
- `risk` 风险/坑点
- `blocked` 阻塞

## 文件
- 脚本：`scripts/memory_candidate_extractor.py`
- 输出目录：`memory/auto-candidates/`

## 用法

### 1. 直接传文本
```bash
python3 scripts/memory_candidate_extractor.py extract "以后先做记忆提炼，再增强任务中心。待办：把候选层接进任务系统。这个先暂停，等我确认。" --project openclaw --save
```

### 2. 从文件提取
```bash
python3 scripts/memory_candidate_extractor.py extract --file memory/2026-04-29.md --project openclaw --save
```

## 当前原则
- 先候选，后落主记忆
- 先去重，后联动任务中心
- 先规则提取，后做更复杂语义提取

## 下一步
1. 给任务中心接 `todo/blocked/progress`
2. 给候选项加“采纳/忽略”状态
3. 再考虑自动写入 `MEMORY.md` 的安全流程
