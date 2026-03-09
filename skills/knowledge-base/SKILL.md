---
name: knowledge-base
description: Knowledge base management and navigation. Use when searching for project information, decisions, solutions to problems, or reference materials. Provides structured access to all curated knowledge. Integrated with unified-memory and self-improvement systems.
---

# 知识库管理技能 v2.0

> **与统一记忆系统和自我进化系统深度整合的三层知识架构**

## 📐 三层知识架构

```
┌─────────────────────────────────────────────────────────────┐
│                     第三层：自我进化层                        │
│                   (self-improvement)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 模式识别     │  │ 目标关联     │  │ 持续优化     │      │
│  │ 从知识发现   │  │ 项目→目标    │  │ 自动化建议   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                     第二层：知识沉淀层                        │
│                     (knowledge-base)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ projects/    │  │ decisions/   │  │ problems/    │      │
│  │ 项目知识库   │  │ 决策记录     │  │ 问题方案     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │
          ▲                 ▲                 ▲
          │                 │                 │
┌─────────────────────────────────────────────────────────────┐
│                     第一层：日常记忆层                        │
│                     (unified-memory)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 每日记忆     │  │ 对话记录     │  │ 知识图谱     │      │
│  │ memory/*.md  │  │ Recall       │  │ Graph        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 📁 知识库位置

```
~/.openclaw/workspace/knowledge-base/
```

## 目录结构

| 目录 | 用途 | 示例 |
|------|------|------|
| `projects/` | 项目知识库 | 储能工具包、股票分析系统 |
| `decisions/` | 重要决策记录 | 技术选型、方案确定 |
| `problems/` | 问题与解决方案 | OpenClaw故障、服务器问题 |
| `references/` | 参考资料 | API文档、配置指南 |
| `templates/` | 知识模板 | 项目模板、决策模板 |

## 🔗 与统一记忆系统的整合

### 数据流向

```
daily memory → unified-memory → knowledge-base
     ↓               ↓                ↓
  原始记录      分析/检索/图谱     结构化沉淀
```

### 整合功能

| 功能 | unified-memory | knowledge-base |
|------|----------------|----------------|
| **存储** | 临时记忆、对话记录 | 结构化知识、项目文档 |
| **检索** | 快速全文搜索 | 分类导航、索引 |
| **分析** | 主题提取、知识图谱 | 项目进展、决策追踪 |
| **时效** | 近期为主(30天) | 永久保存 |

### 自动同步流程

```bash
# 处理昨日记忆，提取知识
python3 scripts/knowledge_memory_integration.py process-memory --date 2026-03-08

# 同步到知识库
python3 scripts/knowledge_memory_integration.py sync-kb

# 完整每日同步
python3 scripts/knowledge_memory_integration.py daily-sync
```

### 同步规则

| 记忆类型 | 目标位置 | 触发条件 |
|---------|---------|---------|
| 项目进展 | `projects/项目名/CHANGELOG.md` | 检测到完成/实现/部署 |
| 重要决策 | `decisions/YYYY-MM-DD-标题.md` | 检测到[DECISION]标记 |
| 问题解决 | `problems/YYYY-MM-DD-标题.md` | 检测到问题+解决 |
| 参考资料 | `references/类别/文档.md` | 手动归档 |

## 🧬 与自我进化系统的整合

### 联动机制

```
knowledge-base → self-improvement
       ↓                ↓
  项目更新      长期目标进度更新
  决策记录      学习模式识别
  问题方案      错误预防优化
```

### 联动场景

| 场景 | 知识库变化 | 自我进化响应 |
|------|-----------|-------------|
| 项目完成里程碑 | 更新 CHANGELOG | 更新目标进度 |
| 记录决策 | 新建决策文档 | 识别决策模式 |
| 解决问题 | 新建问题方案 | 学习错误预防 |
| 高频主题 | INDEX更新 | 生成优化建议 |

### 联动命令

```bash
# 将知识库联动到自我进化
python3 scripts/knowledge_memory_integration.py link-evolution
```

## 🚀 使用场景

### 场景1：每日知识整理（自动化）

```bash
# 添加到 crontab，每天 01:00 执行
0 1 * * * /usr/bin/python3 ~/.openclaw/workspace/skills/knowledge-base/scripts/knowledge_memory_integration.py daily-sync
```

**效果**：
- 自动分析昨日记忆
- 提取项目更新、决策、问题
- 自动归档到知识库对应位置
- 更新长期目标进度

### 场景2：项目进展追踪

```bash
# 查看项目自动同步的更新
cat knowledge-base/projects/储能工具包/CHANGELOG.md
```

**内容示例**：
```markdown
# 储能工具包 更新日志

## 2026-03-08
- 完成电价查询模块优化，支持循环次数计算
- 新增31省份数据导入功能

## 2026-03-07
- 修复四川电价数据错误
- 部署到生产环境
```

### 场景3：决策追溯

```bash
# 查找历史决策
ls -la knowledge-base/decisions/ | grep 飞书
```

**快速参考**：
```markdown
# 决策记录

**日期**: 2026-03-04
**决策**: 飞书文件发送路径规范
**详情**: 确定使用 workspace 目录发送文件，/tmp 目录会失败
**关键词**: 飞书, 文件发送, 路径规范
```

### 场景4：问题知识库

```bash
# 搜索历史问题解决方案
grep -r "API超时" knowledge-base/problems/
```

## 📊 知识流转监控

### 查看知识流动记录

```bash
# 查看最近的知识提取
cat ~/.openclaw/workspace/memory/evolution/knowledge_flow.json | jq '.[-10:]'
```

### 知识库统计

```bash
# 统计各类型知识数量
find knowledge-base/projects -name "*.md" | wc -l    # 项目数
find knowledge-base/decisions -name "*.md" | wc -l   # 决策数
find knowledge-base/problems -name "*.md" | wc -l    # 问题数
```

## 🔄 整合工作流程

### 日常流程

```
1. 日常对话/工作
   ↓
2. 自动记录到 unified-memory
   ↓
3. 每日凌晨自动分析记忆 → 提取知识
   ↓
4. 同步到 knowledge-base 对应位置
   ↓
5. 更新 self-improvement 目标进度
   ↓
6. 生成知识同步报告
```

### 手动整理流程

```
1. 读取 memory/YYYY-MM-DD.md
   ↓
2. 识别需要沉淀的内容
   ↓
3. 手动整理入 knowledge-base/
   ↓
4. 更新 INDEX.md
   ↓
5. 存储到 unified-memory（重要度: 0.9）
```

## 🛠️ 命令参考

### knowledge_memory_integration.py

```bash
# 处理特定日期记忆
python3 scripts/knowledge_memory_integration.py process-memory --date 2026-03-08

# 同步到知识库（试运行）
python3 scripts/knowledge_memory_integration.py sync-kb --dry-run

# 正式同步到知识库
python3 scripts/knowledge_memory_integration.py sync-kb

# 联动自我进化
python3 scripts/knowledge_memory_integration.py link-evolution

# 完整每日同步
python3 scripts/knowledge_memory_integration.py daily-sync
```

## 📈 数据存储

| 文件 | 内容 | 位置 |
|------|------|------|
| `knowledge_flow.json` | 知识流动记录 | `memory/evolution/` |
| `pending_kb_updates.json` | 待同步知识 | `memory/evolution/` |
| 项目CHANGELOG | 项目更新历史 | `knowledge-base/projects/项目名/` |
| 决策记录 | 重要决策 | `knowledge-base/decisions/` |
| 问题方案 | 踩坑记录 | `knowledge-base/problems/` |

## 📝 维护规则

### 自动维护（推荐）

1. **每日记忆** → 自动分析 → 自动归档
2. **重要决策** → 标记[DECISION] → 自动提取
3. **踩坑记录** → 标记问题/解决 → 自动归档

### 手动维护（补充）

1. **复杂项目** → 手动编写 README.md
2. **参考资料** → 手动整理归档
3. **知识库索引** → 每周检查更新 INDEX.md

## 🎯 最佳实践

1. **使用标记**: 在记忆中使用 `[DECISION]`、`[PROJECT]` 等标记便于自动提取
2. **定期回顾**: 每周查看知识库 INDEX.md，确保信息完整
3. **关键词规范**: 使用统一的关键词便于关联检索
4. **及时同步**: 重要决策和问题解决后立即触发同步

## 🔮 未来扩展

- [ ] 知识库语义搜索（基于向量嵌入）
- [ ] 自动知识图谱构建
- [ ] 跨项目知识关联发现
- [ ] 知识过时自动提醒
- [ ] 基于知识库的主动建议

---

*三层知识架构，让知识自动流动、持续进化* 🧠✨
