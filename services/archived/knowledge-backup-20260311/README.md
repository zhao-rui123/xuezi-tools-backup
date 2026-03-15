# 知识关联模块

知识图谱系统，用于分析知识库条目间的关联关系。

## 文件结构

```
services/knowledge/
├── knowledge_graph.py    # 核心模块
├── knowledge_graph.json  # 生成的知识图谱数据（自动导出）
└── README.md            # 本文件
```

## 功能特性

1. **条目扫描**: 自动扫描 `knowledge-base/` 目录下的所有 Markdown 文件
2. **关联分析**: 分析条目间的标签共享、关键词共享、内容相似度
3. **知识图谱**: 生成 JSON 格式的知识图谱数据
4. **智能搜索**: 支持按标签、关键词、内容搜索
5. **相关推荐**: 查询与指定条目相关的其他条目

## 使用方法

### 命令行接口

```bash
# 构建知识图谱并显示统计信息
python3 services/knowledge/knowledge_graph.py --build --stats

# 导出为 JSON 文件
python3 services/knowledge/knowledge_graph.py --build --export services/knowledge/graph.json

# 搜索关键词
python3 services/knowledge/knowledge_graph.py --build --search "储能"

# 按标签搜索
python3 services/knowledge/knowledge_graph.py --build --tag "储能"

# 查找相关条目
python3 services/knowledge/knowledge_graph.py --build --related "project_1_README" --min-strength 0.05
```

### Python API

```python
from services.knowledge.knowledge_graph import KnowledgeGraph

# 创建实例
kg = KnowledgeGraph("knowledge-base")

# 构建图谱
kg.build_graph()

# 搜索
results = kg.search("储能")

# 查找相关条目
related = kg.find_related_entries("project_1_README", min_strength=0.1)

# 导出
kg.export_to_json("graph.json")

# 获取统计
stats = kg.get_graph_stats()
```

## 数据结构

### 知识条目 (KnowledgeEntry)

```json
{
  "id": "project_1_README",
  "title": "项目知识库 - 储能工具包",
  "path": "projects/储能工具包/README.md",
  "content": "...",
  "entry_type": "project",
  "tags": ["储能", "核心项目"],
  "keywords": ["运营中", "github", "kwh"],
  "related_entries": [],
  "created_date": "2026-03-04",
  "updated_date": "2026-03-04"
}
```

### 关系 (Relationship)

```json
{
  "source_id": "project_1_README",
  "target_id": "project_4_README",
  "relation_type": "keyword_shared",
  "strength": 0.13,
  "details": {"shared_keywords": ["github", "backup"]}
}
```

## 关系类型

| 类型 | 说明 |
|------|------|
| `tag_shared` | 共享相同标签 |
| `keyword_shared` | 共享相同关键词 |
| `content_similar` | 内容相似度高 |

## 统计信息

当前知识库统计：
- 总条目数: 35
- 总关系数: 330
- 条目类型: project(7), decision(10), problem(2), reference(7), operation(5), plan(1), index(3)
- 唯一标签: 41
- 唯一关键词: 282
