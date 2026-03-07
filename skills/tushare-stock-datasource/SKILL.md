---
name: tushare-stock-datasource
description: 基于 Tushare Pro 的专业股票数据源，替代新浪财经，提供更稳定的实时行情、财务数据和技术指标。支持A股、港股、美股。
metadata:
  openclaw:
    requires:
      bins: [python3]
    install:
      - id: python-packages
        kind: pip
        packages: [tushare, pandas, numpy]
---

# Multi-Source Stock Datasource

## 概述

多数据源股票客户端，**优先使用免费接口**，Tushare作为备选。支持自动切换数据源，确保数据稳定获取。

## 数据源对比

| 数据源 | 费用 | 稳定性 | 优先级 |
|-------|------|--------|--------|
| **新浪财经** | 免费 | 中等 | 1 |
| **东方财富** | 免费 | 高 | 2 |
| **Tushare Pro** | 积分制/付费 | 专业级 | 3 |

## 使用方法

### 推荐：多数据源客户端（自动切换）

```python
import asyncio
from skills.tushare_stock_datasource.multi_source_client import MultiSourceStockClient

client = MultiSourceStockClient(preferred_source="sina")

# 获取行情（自动切换数据源）
async def get_data():
    quotes = await client.get_quotes()
    print(client.format_report(quotes))

asyncio.run(get_data())
```

### 直接使用东方财富（更稳定）

```python
from skills.tushare_stock_datasource.multi_source_client import EastMoneyDataSource

datasource = EastMoneyDataSource()
quotes = await datasource.get_quotes(["002460", "002738"])
```

### 使用Tushare（如果有Token）

```python
from skills.tushare_stock_datasource.tushare_client import TushareStockClient

client = TushareStockClient(token="your_token")
quote = client.get_realtime_quote("002460.SZ")
```

## 命令行测试

```bash
cd ~/.openclaw/workspace && source venv/bin/activate
python3 skills/tushare-stock-datasource/multi_source_client.py
```

## 自选股配置

默认监控7只自选股：
- 赣锋锂业 (002460)
- 中矿资源 (002738)
- 盐湖股份 (000792)
- 盛新锂能 (002240)
- 京东方A (000725)
- 彩虹股份 (600707)
- 中芯国际 (688981)

修改 `multi_source_client.py` 中的 `WATCHLIST` 变量可自定义。

## 数据字段

| 字段 | 说明 |
|-----|------|
| code | 股票代码 |
| name | 股票名称 |
| price | 当前价格 |
| change | 涨跌额 |
| pct_change | 涨跌幅(%) |
| volume | 成交量 |
| amount | 成交金额(万) |
| high | 最高价 |
| low | 最低价 |
| open | 开盘价 |
| prev_close | 昨收价 |
| source | 数据来源 |

## 与现有系统集成

替换现有股票分析代码：

```python
# 旧代码
from stock_analyzer_pro import fetch_sina_data

# 新代码
import asyncio
from skills.tushare_stock_datasource.multi_source_client import MultiSourceStockClient

client = MultiSourceStockClient()
quotes = asyncio.run(client.get_quotes())
```

## 文件结构

```
skills/tushare-stock-datasource/
├── SKILL.md                    # 本文件
├── multi_source_client.py      # 多数据源客户端（推荐）
├── tushare_client.py          # Tushare客户端（备选）
└── __init__.py                # 模块初始化
```

## 注意事项

- **新浪财经**：免费但偶尔不稳定，周末可能无数据
- **东方财富**：免费且稳定，推荐优先使用
- **Tushare**：需要积分，新用户积分有限，适合作为备选

## 更新计划

- [x] 支持多数据源自动切换
- [x] 集成东方财富免费接口
- [ ] 集成到股票日报推送脚本
- [ ] 添加历史K线数据获取
- [ ] 支持港股/美股数据
