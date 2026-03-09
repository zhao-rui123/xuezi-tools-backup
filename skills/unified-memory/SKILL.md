# Memory QA System - 智能问答系统

基于 unified-memory 的记忆智能问答模块，支持自然语言查询、自动总结和上下文感知回复。

## 功能特性

### 1. 基于记忆的问答 (answer)
- 自然语言理解问题
- 智能匹配相关记忆
- 按时间和主题过滤
- 返回结构化答案

### 2. 时间段总结 (summarize_period)
- 指定时间范围总结
- 按类别统计分析
- 提取重要亮点
- 主题聚焦功能

### 3. 相关内容查找 (find_related)
- 主题关联搜索
- 生成时间线
- 相关主题推荐
- 相关度排序

### 4. 上下文感知回复 (generate_context_aware_response)
- 结合对话历史
- 上下文联想
- 智能建议
- 多轮对话支持

## 安装

```bash
# 确保 memory_qa.py 在 unified-memory 目录
cp memory_qa.py ~/.openclaw/workspace/skills/unified-memory/
chmod +x ~/.openclaw/workspace/skills/unified-memory/memory_qa.py
```

## 使用方法

### Python API

```python
from memory_qa import MemoryQA

# 初始化
qa = MemoryQA()

# 1. 回答用户问题
result = qa.answer("昨天完成了什么工作？")
print(result["answer"])
print(f"置信度: {result['confidence']}")

# 2. 总结时间段
summary = qa.summarize_period("2026-03-01", "2026-03-08", focus="项目")
print(summary["summary"])

# 3. 查找相关内容
related = qa.find_related("股票分析", limit=5)
for item in related["timeline"]:
    print(f"[{item['date']}] {item['title']}")

# 4. 上下文感知回复
history = [
    {"role": "user", "content": "之前讨论过小龙虾之家"},
    {"role": "assistant", "content": "是的，我们完成了开发"}
]
response = qa.generate_context_aware_response("它有什么功能？", history)
print(response["response"])
```

### 命令行接口

```bash
# 回答用户问题
python3 memory_qa.py answer "小龙虾之家是什么项目？"
python3 memory_qa.py answer "股票分析系统" --json

# 总结时间段
python3 memory_qa.py summarize 2026-03-01 2026-03-08
python3 memory_qa.py summarize 2026-03-01 2026-03-08 --focus "项目"

# 查找相关内容
python3 memory_qa.py find "股票分析" --limit 5
python3 memory_qa.py find "小龙虾之家" --json

# 上下文感知回复
python3 memory_qa.py context "它有什么功能？"
```

## 支持的时间关键词

- 今天、昨天、前天
- 本周、上周
- 本月、上个月
- 今年
- 具体日期: 2026-03-01

## 自动分类系统

系统会自动识别以下类别：

| 类别 | 关键词 | Emoji |
|------|--------|-------|
| project | 项目、开发、完成、部署 | 🚀 |
| decision | 决定、决策、选择、方案 | 🎯 |
| task | 任务、待办、计划、工作 | 📋 |
| meeting | 会议、讨论、沟通 | 🗣️ |
| learning | 学习、研究、分析 | 📚 |
| issue | 问题、bug、错误、修复 | 🐛 |
| stock | 股票、股市、行情 | 📈 |
| skill | 技能包、工具、脚本 | 🛠️ |
| backup | 备份、归档、保存 | 💾 |

## 重要性计算

系统自动计算每条记忆的重要性（0-1）：
- 基础分: 0.5
- 标签权重: +0.2（重要标签）
- 关键词权重: +0.05（每个重要关键词）
- 长度权重: +0.1（适中长度）

## 相关度计算

评分公式：
```
最终得分 = 相关度 × (0.5 + 0.5 × 重要性)
```

相关度考虑因素：
- 主题匹配: +0.4
- 关键词匹配: 最高 +0.3
- 分类匹配: +0.2
- 标签匹配: +0.1
- 时间衰减: +0.1（越新越高）

## 测试

```bash
# 运行功能测试
python3 test_memory_qa.py
```

## 文件结构

```
unified-memory/
├── memory_qa.py          # 主模块（25KB）
├── test_memory_qa.py     # 测试脚本
└── SKILL.md              # 本文档
```

## 集成使用

可以集成到 unified-memory 主系统中：

```python
# 在 unified-memory 主模块中使用
from memory_qa import MemoryQA

class UnifiedMemory:
    def __init__(self):
        self.qa = MemoryQA()
    
    def query(self, question: str) -> str:
        """自然语言查询接口"""
        result = self.qa.answer(question)
        return result["answer"]
```

## 第一阶段增强功能 (2026-03-09)

### 5. 自动归档系统 (auto_archive.py)
**功能**: 自动管理记忆文件生命周期
- 7天后自动归档到 `archive/YYYY/MM/`
- 30天后提取关键信息到 `permanent/`
- 90天后自动压缩
- 清理过期快照

**使用**:
```bash
# 手动运行
python3 auto_archive.py

# 定时任务 (每天凌晨2点)
0 2 * * * /Users/zhaoruicn/.openclaw/workspace/skills/unified-memory/cron_tasks.sh
```

### 6. 重要性评估系统 (importance_scorer.py)
**功能**: 智能评估记忆重要性
- 自动评分 (0-1分)
- 标记重要决策、项目、任务
- 分类统计 (project/decision/task/issue等)
- 生成重要性报告

**使用**:
```bash
# 评估所有记忆
python3 importance_scorer.py

# 查看评分结果
cat ~/.openclaw/workspace/memory/memory_scores.json
```

**评分维度**:
| 维度 | 权重 | 说明 |
|------|------|------|
| 基础分 | 0.5 | 默认分数 |
| 决策标记 | 0.25 | 包含[DECISION]区块 |
| 项目标记 | 0.2 | 包含[PROJECT]区块 |
| 关键词 | 0.05/个 | 匹配重要关键词 |
| 代码块 | 0.1 | 包含代码示例 |

### 7. 语义搜索优化 (semantic_search.py)
**功能**: 快速智能检索
- 关键词索引 (自动构建)
- 语义相似度计算
- 重要性加权排序
- 响应时间 < 500ms

**使用**:
```bash
# 重建索引
python3 semantic_search.py

# Python API
from semantic_search import EnhancedSearch

search = EnhancedSearch()
results = search.search("小龙虾", limit=5)
for r in results:
    print(f"{r.title} (相关度: {r.relevance})")
```

## 定时任务配置

```bash
# 添加到 crontab
crontab -e

# 添加以下行
0 2 * * * /Users/zhaoruicn/.openclaw/workspace/skills/unified-memory/cron_tasks.sh >> /Users/zhaoruicn/.openclaw/workspace/memory/cron.log 2>&1
```

## 版本历史

- v1.1.0 (2026-03-09): 第一阶段增强
  - 添加自动归档系统
  - 添加重要性评估系统
  - 添加语义搜索优化
  - 定时任务自动化

- v1.0.0 (2026-03-08): 初始版本
  - 实现 answer, summarize_period, find_related, generate_context_aware_response
  - 支持命令行和Python API
  - 完整测试覆盖
