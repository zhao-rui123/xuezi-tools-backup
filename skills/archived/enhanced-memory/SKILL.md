# Enhanced Memory Skill

基于 LanceDB Pro 思路的简化版增强记忆系统，使用本地文件存储，无需额外数据库。

## 功能特性

- 🔍 **混合检索**：向量相似度 + BM25 文本搜索
- ⏰ **时间衰减**：老记忆自动降级
- ⭐ **重要性加权**：重要记忆优先
- 🧹 **噪声过滤**：自动过滤低质量内容
- 🏷️ **多作用域**：支持 global/agent 隔离
- 🔄 **会话记忆**：/new 时自动提取保存

## 安装

```bash
# 技能包已在本地，无需额外安装
# 依赖：numpy, jieba（中文分词）
pip install numpy jieba
```

## 使用方法

### 1. 存储记忆

```python
from enhanced_memory import store_memory

store_memory(
    text="用户喜欢Python编程",
    category="preference",  # preference/fact/decision/entity
    importance=0.8,         # 0-1
    scope="global"          # global 或 agent:<id>
)
```

### 2. 检索记忆

```python
from enhanced_memory import recall_memory

results = recall_memory(
    query="用户编程偏好",
    scope="global",
    top_k=5
)
```

### 3. 会话记忆（/new 自动保存）

当用户执行 `/new` 时，自动提取上一个会话的关键信息：

```bash
# 手动运行记忆提取
python ~/.openclaw/workspace/skills/enhanced-memory/session_distiller.py
```

提取的内容包括：
- 上次会话任务
- 待办事项
- 关键上下文

### 4. CLI 管理

```bash
cd ~/.openclaw/workspace/skills/enhanced-memory

# 列出记忆
python -m enhanced_memory list

# 搜索记忆
python -m enhanced_memory search "编程"

# 删除记忆
python -m enhanced_memory delete <id>

# 查看统计
python -m enhanced_memory stats

# 手动提取会话记忆
python session_distiller.py
```

## 评分算法

```
最终得分 = 相似度得分 × 时间衰减 × 重要性加权

时间衰减 = 0.5 + 0.5 × exp(-年龄天数 / 60)
重要性加权 = 0.7 + 0.3 × importance
```

## 与系统对比

| 功能 | 系统 memory-core | enhanced-memory |
|------|-----------------|-----------------|
| 存储 | 文件 | 文件 |
| 向量搜索 | ❌ | ✅ |
| BM25 | ❌ | ✅ |
| 时间衰减 | ❌ | ✅ |
| 重要性 | ❌ | ✅ |
| 会话记忆 | ❌ | ✅ |
| 安装难度 | 无 | 简单 |

## 配置

在 `~/.openclaw/workspace/enhanced-memory/config.json`：

```json
{
  "db_path": "~/.openclaw/memory/enhanced",
  "embedding_model": "local",
  "auto_decay": true,
  "default_scope": "global"
}
```

## 与 Session Snapshot 集成

本技能包与 `session-snapshot.py` 自动集成：

1. 每次会话保存快照 → `memory/snapshots/session_*.json`
2. 执行 `/new` 时 → 调用 `session_distiller.py`
3. 提取关键信息 → 存储到 enhanced-memory
4. 新会话自动读取 → `recall_memory("上次任务")`

## 文件结构

```
enhanced-memory/
├── SKILL.md                  # 技能文档
├── __init__.py               # 核心模块
├── __main__.py               # CLI 入口
├── session_distiller.py      # 会话记忆提取器
└── session-hook.sh           # /new 钩子脚本
```

## 注意事项

- 使用本地简化的向量计算（基于词频），精度不如 OpenAI Embedding
- 适合中小规模记忆（< 10,000 条）
- 大向量计算需要 numpy

## 未来计划

- [ ] 支持 OpenAI/Gemini Embedding API
- [ ] 支持 Cross-Encoder 重排序
- [ ] OpenClaw 工具集成（memory_recall/memory_store）

---
*基于 memory-lancedb-pro 思路简化实现*
