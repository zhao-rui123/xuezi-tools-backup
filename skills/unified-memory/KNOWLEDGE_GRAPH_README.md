# 知识图谱构建模块

为 unified-memory 系统提供知识图谱功能，从记忆文件中提取实体、建立关系、生成可视化网络。

## 文件位置

- **主模块**: `~/.openclaw/workspace/skills/unified-memory/knowledge_graph.py`
- **图谱数据**: `~/.openclaw/workspace/memory/knowledge_graph/graph_data.json`
- **可视化页面**: `~/.openclaw/workspace/memory/knowledge_graph/knowledge_graph.html`

## 功能特性

### 1. 实体提取 (extract_entities)
自动从文本中提取以下类型的实体：
- **项目**: 小龙虾之家、储能电站、股票分析系统等
- **技术**: Python、JavaScript、React、API、GitHub 等
- **人**: 雪子等
- **公司**: 腾讯、中矿资源、赣锋锂业等
- **技能包**: stock-analysis、unified-memory 等
- **文件**: app.py、index.html 等
- **概念**: 储能、光伏、PCS、碳中和等
- **工具**: Git、Docker、Nginx 等

### 2. 关系建立 (build_relations)
自动识别实体之间的关系：
- **开发**: A 开发了 B
- **使用**: A 使用了 B
- **部署**: A 部署到 B
- **依赖**: A 依赖于 B
- **包含**: A 包含 B
- **实现**: A 实现了 B
- **管理**: A 管理 B
- **分析**: A 分析了 B
- **关联**: A 和 B 有关联（共现关系）

### 3. 可视化 (visualize_graph)
生成交互式 HTML 可视化页面，包含：
- 力导向图布局
- 实体类型颜色编码
- 关系标签显示
- 搜索功能
- 统计面板

### 4. 图谱查询 (query_graph)
支持多种查询方式：
- 按实体名称模糊查询
- 按实体类型筛选
- 按关系类型筛选
- 指定查询深度（邻居层级）

### 5. 图谱扩展 (extend_graph)
支持使用新记忆文本动态扩展图谱。

## 使用方法

### 命令行使用

```bash
cd ~/.openclaw/workspace/skills/unified-memory

# 从记忆文件构建图谱
python3 knowledge_graph.py build

# 查看统计信息
python3 knowledge_graph.py stats

# 查询实体
python3 knowledge_graph.py query --query "储能" --depth 2

# 按类型查询
python3 knowledge_graph.py query --type technology

# 生成可视化
python3 knowledge_graph.py visualize --output ~/Desktop/kg.html

# 扩展图谱
python3 knowledge_graph.py extend --file new_memory.md
```

### Python API 使用

```python
from knowledge_graph import KnowledgeGraph, build_graph_from_memories

# 加载现有图谱
kg = KnowledgeGraph()

# 从记忆文件构建
kg = build_graph_from_memories("~/.openclaw/workspace/memory")

# 提取实体
entities = kg.extract_entities("今天完成了小龙虾之家项目，使用Python开发")

# 建立关系
relations = kg.build_relations(entities, text)

# 查询图谱
results = kg.query_graph(entity_name="储能", depth=2)

# 扩展图谱
kg.extend_graph("新的记忆内容", "source.md")

# 生成可视化
kg.visualize_graph("output.html")

# 获取统计
stats = kg.get_stats()
```

## 当前图谱统计

基于 23 个记忆文件构建的初始知识图谱：

| 指标 | 数值 |
|------|------|
| 实体总数 | 112 |
| 关系总数 | 216 |
| 实体类型 | 8 种 |
| 关系类型 | 9 种 |

### 实体类型分布

| 类型 | 数量 |
|------|------|
| 文件 | 49 |
| 技术 | 28 |
| 概念 | 8 |
| 公司 | 8 |
| 工具 | 6 |
| 项目 | 6 |
| 技能包 | 6 |
| 人 | 1 |

### 关系类型分布

| 关系 | 数量 |
|------|------|
| 关联 | 223 |
| 开发 | 106 |
| 分析 | 62 |
| 实现 | 32 |
| 使用 | 30 |
| 管理 | 22 |
| 部署 | 19 |
| 包含 | 17 |
| 依赖 | 14 |

### 中心节点 (Top 5)

1. API (技术): 0.1351
2. 储能 (概念): 0.1171
3. 腾讯 (公司): 0.1171
4. feishu (技术): 0.1081
5. Git (工具): 0.0991

## 测试脚本

运行完整测试：

```bash
cd ~/.openclaw/workspace/skills/unified-memory
python3 test_knowledge_graph.py
```

测试内容包括：
1. 实体提取功能
2. 关系建立功能
3. 从记忆文件构建图谱
4. 图谱查询功能
5. 图谱扩展功能
6. 可视化生成功能

## 可视化效果

打开 `~/.openclaw/workspace/memory/knowledge_graph/knowledge_graph.html` 查看交互式知识图谱：

- **拖拽**: 移动节点
- **滚轮**: 缩放
- **点击**: 选中节点
- **搜索框**: 快速定位实体
- **图例**: 显示实体类型颜色编码
- **统计面板**: 实时显示图谱统计

## 依赖说明

- **必需**: Python 3.8+
- **可选**: 
  - `networkx`: 图结构处理（内置简化版回退）
  - `pyvis`: 高级可视化（使用 vis-network.js 简化版回退）

## 后续优化方向

1. 实体消歧：合并同义实体（如 GitHub/github）
2. 关系推理：基于已有关系推断隐含关系
3. 时序分析：追踪实体和关系的演变
4. 语义相似度：基于词向量的实体匹配
5. 自动补全：基于图谱的实体推荐
