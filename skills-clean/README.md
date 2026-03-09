# OpenClaw 记忆管理技能包合集

## 包含技能包

| 技能包 | 功能 | 用途 |
|--------|------|------|
| **enhanced-memory** | 增强记忆系统 | 向量搜索、BM25检索、会话记忆自动提取 |
| **memory-search** | 记忆搜索工具 | 语义检索、文件读取 |
| **context-management** | 上下文管理 | Token优化、会话压缩、长对话管理 |
| **session-persistence** | 会话持久化 | 模型切换时保存/恢复上下文 |

## 安装方法

### 1. 复制到 OpenClaw 技能包目录

```bash
# 解压到 workspace/skills/ 目录
tar -xzvf memory-skills-clean.tar.gz -C ~/.openclaw/workspace/skills/
```

### 2. 安装依赖

```bash
# enhanced-memory 需要
pip install numpy jieba
```

### 3. 配置 OpenClaw

编辑 `~/.openclaw/workspace/SKILL.md` 或相应启动文件，确保加载这些技能。

## 各技能包使用说明

### enhanced-memory

**存储记忆：**
```python
from enhanced_memory import store_memory
store_memory(
    text="用户喜欢Python编程",
    category="preference",
    importance=0.8,
    scope="global"
)
```

**检索记忆：**
```python
from enhanced_memory import recall_memory
results = recall_memory(query="编程偏好", scope="global", top_k=5)
```

**CLI 管理：**
```bash
cd ~/.openclaw/workspace/skills/enhanced-memory
python -m enhanced_memory list
python -m enhanced_memory search "关键词"
python -m enhanced_memory stats
```

### memory-search

这是 OpenClaw 内置工具，无需额外配置。在对话中会自动使用 `memory_search` 和 `memory_get` 工具。

### context-management

查看当前配置：
```bash
openclaw config get agents.defaults.compaction
```

手动压缩会话：
```bash
/compact
```

### session-persistence

保存会话状态：
```bash
bash ~/.openclaw/workspace/scripts/session-state.sh save
```

恢复会话状态：
```bash
bash ~/.openclaw/workspace/scripts/session-state.sh restore
```

## 文件结构

```
memory-skills/
├── enhanced-memory/
│   ├── SKILL.md
│   ├── __init__.py
│   ├── __main__.py
│   └── session_distiller.py
├── memory-search/
│   └── SKILL.md
├── context-management/
│   └── SKILL.md
├── session-persistence/
│   └── SKILL.md
└── README.md
```

## 注意事项

1. **隐私安全**：这些技能包本身不包含任何个人数据，只是工具框架
2. **依赖安装**：enhanced-memory 需要 numpy 和 jieba
3. **配置路径**：根据你的实际 OpenClaw 安装路径调整命令中的路径
4. **模型支持**：所有 OpenClaw 支持的模型都可以使用这些技能

## 自定义配置

### enhanced-memory 配置

创建配置文件 `~/.openclaw/workspace/enhanced-memory/config.json`：

```json
{
  "db_path": "~/.openclaw/memory/enhanced",
  "embedding_model": "local",
  "auto_decay": true,
  "default_scope": "global"
}
```

## 故障排查

### 问题：import 失败
**解决**：确保技能包在 Python 路径中，或从技能包目录运行

### 问题：搜索无结果
**解决**：检查记忆文件是否已创建，先存储一些测试数据

### 问题：权限错误
**解决**：确保 OpenClaw 进程有读写 `~/.openclaw/` 目录的权限

## 开源协议

这些技能包基于 OpenClaw 生态创建，可自由使用和修改。

---
*技能包版本：2026-03-07*  
*适用：OpenClaw 2026.2.x*
