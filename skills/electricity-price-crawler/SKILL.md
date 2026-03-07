---
name: electricity-price-crawler
description: 自动抓取各省发改委最新电价文件，更新储能项目测算系统的电价数据。支持定时任务和手动触发。
metadata:
  openclaw:
    requires:
      bins: [python3]
    install:
      - id: python-packages
        kind: pip
        packages: [httpx, beautifulsoup4, playwright]
---

# Electricity Price Crawler

## 概述

自动抓取各省发改委/电网公司发布的最新电价政策文件，提取分时电价数据，更新储能项目测算系统。

## 功能

- **省份覆盖**: 31个省份 + 新疆生产建设兵团
- **数据源**: 各省发改委官网、电网公司官网
- **数据类型**: 分时电价、容量电价、输配电价
- **更新方式**: 手动触发 / 定时任务（每月1日）
- **数据验证**: 自动验证数据完整性

## 使用方法

### 手动更新单个省份

```bash
python3 ~/.openclaw/workspace/skills/electricity-price-crawler/crawler.py --province 河南 --year 2026
```

### 更新所有省份

```bash
python3 ~/.openclaw/workspace/skills/electricity-price-crawler/crawler.py --all --year 2026
```

### 查看支持的数据源

```bash
python3 ~/.openclaw/workspace/skills/electricity-price-crawler/crawler.py --list-sources
```

### 测试数据抓取（不保存）

```bash
python3 ~/.openclaw/workspace/skills/electricity-price-crawler/crawler.py --province 山东 --dry-run
```

## 数据结构

抓取的数据保存为 JSON 格式：

```json
{
  "province": "河南",
  "year": 2026,
  "month": 2,
  "source_url": "https://...",
  "fetch_time": "2026-03-07T08:00:00",
  "time_of_use": {
    "peak": {"hours": ["08:00-12:00", "18:00-22:00"], "price": 1.0894},
    "valley": {"hours": ["00:00-08:00"], "price": 0.3121},
    "flat": {"hours": ["12:00-18:00", "22:00-24:00"], "price": 0.7008}
  },
  "capacity_price": 32.0,
  "transmission_price": 0.15
}
```

## 数据源配置

在 `~/.openclaw/workspace/skills/electricity-price-crawler/sources.json` 中配置各省份数据源。

## 注意事项

- 部分省份网站有反爬机制，使用 Playwright 模拟浏览器行为
- 数据抓取后需要人工确认价格准确性
- 建议每月1日自动执行，配合人工复核
