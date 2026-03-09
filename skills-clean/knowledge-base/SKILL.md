---
name: knowledge-base
description: Knowledge base management and navigation. Use when searching for project information, decisions, solutions to problems, or reference materials. Provides structured access to all curated knowledge.
---

# 知识库管理技能

## 知识库位置

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

## 使用场景

### 查找项目信息
```
读取 knowledge-base/projects/项目名称/README.md
```

### 查找决策记录
```
读取 knowledge-base/decisions/README.md
```

### 查找问题解决方案
```
读取 knowledge-base/problems/类别/README.md
```

### 查找配置参考
```
读取 knowledge-base/references/参考文档.md
```

## 快速索引

全局索引文件：`knowledge-base/INDEX.md`

包含：
- 所有项目索引
- 决策记录索引
- 问题分类索引
- 参考资料索引

## 维护规则

1. **每日记忆** → 每周整理入对应项目
2. **重要决策** → 立即记录到 decisions/
3. **踩坑记录** → 解决后立即记录到 problems/
4. **参考资料** → 获取时立即归档

## 与 MEMORY.md 的关系

- **MEMORY.md**: 快速参考、系统配置、临时记录
- **knowledge-base/**: 结构化、分类、深度知识

两者互补，MEMORY.md 保留最常用的信息，详细内容入知识库。
