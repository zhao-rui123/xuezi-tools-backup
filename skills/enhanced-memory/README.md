# Enhanced Memory for OpenClaw

一个简化版的增强记忆系统，基于 LanceDB Pro 思路，纯 Python 实现，零复杂依赖。

## 🚀 快速开始

### 1. 解压到技能包目录

```bash
# 解压到 OpenClaw workspace 的 skills 目录
cd ~/.openclaw/workspace/skills
tar -xzvf enhanced-memory.tar.gz
```

### 2. 安装依赖（可选）

```bash
pip install numpy jieba
```

- `numpy`: 加速向量计算（可选，没有也能跑）
- `jieba`: 中文分词（可选，没有则用简单分词）

### 3. 测试

```bash
cd ~/.openclaw/workspace/skills/enhanced-memory

# 添加记忆
python -m enhanced_memory add "我喜欢Python编程" --category preference --importance 0.8

# 搜索记忆
python -m enhanced_memory search "编程"

# 查看统计
python -m enhanced_memory stats
```

## 📦 功能特性

- ✅ **混合检索**：向量相似度 + BM25 文本搜索
- ✅ **时间衰减**：老记忆自动降级（60天半衰期）
- ✅ **重要性加权**：重要记忆优先
- ✅ **噪声过滤**：自动过滤低质量内容
- ✅ **多作用域**：支持 global/agent 隔离
- ✅ **会话记忆**：可提取 /new 前的会话内容

## 📁 文件说明

```
enhanced-memory/
├── __init__.py           # 核心模块
├── __main__.py           # CLI 入口
├── session_distiller.py  # 会话记忆提取器
├── session-hook.sh       # /new 钩子示例
└── SKILL.md              # 详细文档
```

## 💡 使用示例

### Python API

```python
import sys
sys.path.insert(0, '/Users/YOURNAME/.openclaw/workspace/skills/enhanced-memory')

from enhanced_memory import store_memory, recall_memory

# 存储记忆
store_memory(
    text="用户喜欢储能行业",
    category="preference",
    importance=0.9,
    scope="global"
)

# 检索记忆
results = recall_memory("用户偏好", top_k=3)
for r in results:
    print(f"[{r['score']:.3f}] {r['text']}")
```

### CLI 命令

```bash
python -m enhanced_memory list              # 列出记忆
python -m enhanced_memory search "关键词"    # 搜索记忆
python -m enhanced_memory delete mem_00001  # 删除记忆
python -m enhanced_memory stats             # 查看统计
```

## 🔧 与 Session Snapshot 集成

如果你有用 `session-snapshot.py` 保存会话，可以自动提取记忆：

```bash
python session_distiller.py
```

这会自动读取 `~/.openclaw/workspace/memory/snapshots/current_session.json`，
提取关键信息存储到记忆库。

## ⚠️ 注意事项

1. **向量计算是简化的**：使用字符哈希，不是神经网络 Embedding，精度略低但够用
2. **适合中小规模**：< 10,000 条记忆，大了建议用专业向量数据库
3. **存储位置**：`~/.openclaw/memory/enhanced/index.json`

## 📊 和原版对比

| 功能 | LanceDB Pro | Enhanced Memory |
|------|-------------|-----------------|
| 向量检索 | ✅ 神经网络 | ⚠️ 字符哈希 |
| BM25 | ✅ | ✅ |
| Cross-Encoder | ✅ | ❌ |
| 时间衰减 | ✅ | ✅ |
| 依赖 | LanceDB + API | 纯 Python |
| 稳定性 | 复杂易出错 | 简单可靠 |

## 📝 许可证

MIT - 自由使用、修改、分享

## 🙏 致谢

基于 [memory-lancedb-pro](https://github.com/win4r/memory-lancedb-pro) 思路简化实现

---
*Made by 雪子助手 for OpenClaw*
