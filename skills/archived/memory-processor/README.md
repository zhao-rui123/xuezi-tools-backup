# 记忆智能筛选系统 (Memory Processor)

## 功能概述

自动分析记忆文件，提取高频关键词和核心主题，生成分层记忆索引，减少未来搜索时的Token消耗。

## 核心功能

1. **月度记忆分析** - 每月自动扫描过去30天的记忆文件
2. **关键词提取** - 使用TF-IDF算法找出高频关键词
3. **主题聚类** - 将相关内容归类成主题
4. **永久记忆生成** - 提炼核心内容保存到长期记忆
5. **记忆索引更新** - 建立可快速检索的记忆地图

## 使用方法

### 手动执行分析
```bash
python3 memory_processor.py --month 2026-03
```

### 自动定时执行（推荐）
```bash
# 每月1日凌晨2点自动执行
0 2 1 * * /Users/zhaoruicn/.openclaw/workspace/skills/memory-processor/memory_processor.py
```

## 输出文件

- `memory/summary/YYYY-MM-summary.md` - 月度记忆摘要
- `memory/index/keywords.json` - 关键词索引
- `memory/index/themes.json` - 主题索引
- `memory/permanent/` - 永久记忆存档

## 技术实现

- 使用Python的jieba分词进行中文分词
- 使用TF-IDF算法提取关键词
- 使用K-means聚类识别主题
- 生成Markdown格式的记忆摘要
