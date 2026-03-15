# Knowledge Module - 知识管理模块

Memory Suite v4.0 - Phase 2 知识管理模块

## 模块概述

本模块负责 Memory Suite v4.0 的知识管理功能，包括知识图谱构建、知识导入、知识同步等核心功能。

## 文件结构

```
knowledge/
├── __init__.py              # 模块入口
├── knowledge_graph.py       # 知识图谱构建和查询
├── knowledge_importer.py    # 从记忆导入知识
├── knowledge_sync.py        # 双向知识同步
├── knowledge_manager.py     # 知识条目 CRUD (已有)
├── knowledge_search.py      # 知识搜索 (已有)
└── README.md                # 本文档
```

## 功能说明

### 1. knowledge_graph.py - 知识图谱

**功能：**
- 实体提取和关系识别
- 知识图谱构建
- 图谱查询和遍历
- 路径查找

**核心类：**
- `Entity` - 知识实体数据类
- `Relation` - 实体关系数据类
- `KnowledgeGraph` - 知识图谱容器
- `EntityExtractor` - 实体和关系提取器
- `GraphBuilder` - 图谱构建器

**使用示例：**
```python
from knowledge import GraphBuilder, build_knowledge_graph

# 构建图谱
builder = GraphBuilder()
result = builder.build_from_memory(force=False)

# 查询实体
entity = builder.query_entity("project_储能项目")
relations = builder.query_relations(entity.id)

# 查找路径
paths = builder.find_path("entity_1", "entity_2", max_depth=3)
```

### 2. knowledge_importer.py - 知识导入

**功能：**
- 从记忆文件自动导入知识
- 内容分析和关键信息提取
- 智能去重和合并
- 知识条目生成

**核心类：**
- `KnowledgeEntry` - 知识条目数据类
- `ContentAnalyzer` - 内容分析器
- `KnowledgeDeduplicator` - 去重器
- `KnowledgeImporter` - 知识导入器

**使用示例：**
```python
from knowledge import KnowledgeImporter, import_knowledge

# 导入知识
importer = KnowledgeImporter()
result = importer.import_from_memory(force=False)

# 搜索知识
results = importer.search("储能", category="project")
```

### 3. knowledge_sync.py - 知识同步

**功能：**
- memory/ ↔ knowledge-base/ 双向同步
- 冲突检测和解决
- 同步状态管理
- 同步历史记录

**核心类：**
- `SyncDirection` - 同步方向枚举
- `ConflictResolution` - 冲突解决策略枚举
- `SyncItem` - 同步项数据类
- `KnowledgeSync` - 知识同步器

**使用示例：**
```python
from knowledge import KnowledgeSync, sync_knowledge, SyncDirection, ConflictResolution

# 双向同步
result = sync_knowledge(direction="bidirectional", force=False)

# 单向同步（记忆 → 知识库）
result = sync_knowledge(direction="memory_to_kb")

# 自定义冲突解决
sync = KnowledgeSync(conflict_resolution=ConflictResolution.KEEP_NEWER)
result = sync.sync(direction=SyncDirection.BIDIRECTIONAL)
```

## 命令行使用

### 知识图谱
```bash
python3 knowledge_graph.py --build          # 构建图谱
python3 knowledge_graph.py --build --force  # 强制重建
python3 knowledge_graph.py --query "实体名"  # 查询实体
```

### 知识导入
```bash
python3 knowledge_importer.py --import-knowledge  # 导入知识
python3 knowledge_importer.py --import-knowledge --force  # 强制导入
python3 knowledge_importer.py --search "关键词"   # 搜索知识
```

### 知识同步
```bash
python3 knowledge_sync.py --sync                # 执行同步
python3 knowledge_sync.py --sync --direction bidirectional  # 双向同步
python3 knowledge_sync.py --sync --force        # 强制同步
python3 knowledge_sync.py --history             # 查看历史
python3 knowledge_sync.py --status              # 查看状态
```

## 与 Scheduler 集成

所有模块都设计为可被 scheduler.py 调用：

```python
# scheduler.py 示例
from knowledge import build_knowledge_graph, import_knowledge, sync_knowledge

def run_knowledge_graph():
    """每天 01:00 运行"""
    return build_knowledge_graph()

def run_knowledge_import():
    """每天 06:00 运行"""
    return import_knowledge()

def run_knowledge_sync():
    """每天 06:00 运行"""
    return sync_knowledge(direction="bidirectional")
```

## 配置

模块使用标准路径配置：

```python
WORKSPACE = Path("/home/user/workspace")
MEMORY_DIR = WORKSPACE / "memory"
KNOWLEDGE_DIR = WORKSPACE / "knowledge-base"

# 知识图谱
GRAPH_DIR = KNOWLEDGE_DIR / "graph"
GRAPH_FILE = GRAPH_DIR / "knowledge_graph.json"

# 知识导入
IMPORT_DIR = KNOWLEDGE_DIR / "imported"
IMPORT_LOG_FILE = KNOWLEDGE_DIR / "import_log.json"

# 知识同步
SYNC_DIR = KNOWLEDGE_DIR / "sync"
SYNC_LOG_FILE = KNOWLEDGE_DIR / "sync_log.json"
SYNC_STATE_FILE = KNOWLEDGE_DIR / "sync_state.json"
```

## 错误处理

所有模块都包含完善的错误处理：
- 文件不存在时自动创建目录
- 操作失败时记录详细日志
- 返回结构化的结果字典（包含 success 字段）

## 依赖

- Python 3.8+
- 仅使用标准库，无外部依赖

## 测试

运行模块自带的测试：

```bash
# 测试知识图谱
python3 knowledge_graph.py

# 测试知识导入
python3 knowledge_importer.py

# 测试知识同步
python3 knowledge_sync.py

# 测试整个模块
python3 -c "from knowledge import *; print('✅ 所有模块加载成功')"
```

## 版本历史

### v4.0.0 (2026-03-11)
- 初始版本
- 实现知识图谱构建和查询
- 实现知识导入和去重
- 实现双向知识同步
- 与 Memory Suite v3.0 风格保持一致

## 作者

雪子助手
Memory Suite v4.0 开发团队
