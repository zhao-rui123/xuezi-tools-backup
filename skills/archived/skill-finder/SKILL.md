---
name: skill-finder
description: 技能搜索助手 - 自动搜索和推荐ClawHub技能包，根据需求智能匹配
metadata:
  openclaw:
    requires:
      bins: [python3, clawhub]
---

# Skill Finder - 技能搜索助手

## 功能概述

解决"不知道装什么技能"的痛点：
- 🔍 根据需求自动搜索ClawHub
- 💡 智能推荐相关技能包
- 📊 显示评分和描述
- ✅ 检查已安装技能

## 使用方法

### 根据需求推荐

```bash
cd ~/.openclaw/workspace/skills/skill-finder
python3 skill_finder.py "股票分析"
python3 skill_finder.py "天气查询"
python3 skill_finder.py "PDF处理"
```

### 搜索特定关键词

```bash
python3 skill_finder.py search github
python3 skill_finder.py search weather
```

### 列出已安装技能

```bash
python3 skill_finder.py list
```

## 输出示例

```
======================================================================
🔍 技能包推荐: 股票分析
======================================================================

找到 8 个可能相关的技能包:

1. stock-analysis-pro (4.5★)
   专业股票分析系统，支持技术分析和基本面分析

2. tavily-stock-search (3.8★)
   股票信息搜索和监控

3. market-monitor (3.5★)
   市场监控和预警

💡 安装命令示例:
   clawhub install stock-analysis-pro
======================================================================
```

## 关键词映射

内置关键词自动映射：
- `股票` → stock, finance, market
- `天气` → weather, forecast
- `搜索` → search, tavily, web
- `GitHub` → github, git
- `文档` → doc, pdf, office
- `备份` → backup, sync

## 与手动搜索对比

| 方式 | 优点 | 缺点 |
|------|------|------|
| 手动搜索 | 精确 | 需要知道关键词 |
| **Skill Finder** | 智能推荐 | 依赖关键词映射 |

## 未来计划

- [ ] 根据已安装技能推荐相关技能
- [ ] 显示技能包使用统计
- [ ] 一键安装推荐技能
