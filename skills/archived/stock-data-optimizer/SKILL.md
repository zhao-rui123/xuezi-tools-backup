---
name: stock-data-optimizer
description: Token 优化的股票数据获取和筛选系统，基于 Tushare Pro API，支持缓存、数据压缩、分批处理，大幅降低 Token 消耗。
---

# Stock Data Optimizer - Token 优化股票数据系统

## 核心特性

- ✅ **数据缓存** - 每日自动更新，避免重复调用
- ✅ **Token 压缩** - 数据格式优化，节省 70%+ Token
- ✅ **分批处理** - 大请求拆分，避免超限
- ✅ **预计算** - 服务端提前计算指标

## 三种方案

### 方案 A: 轻量级筛选 (推荐)
- **Token**: 0
- **响应**: <100ms
- **用途**: 实时筛选、快速查询

### 方案 B: 智能分析
- **Token**: 2000-4000
- **响应**: 2-5s
- **用途**: 深度分析、投资建议

### 方案 C: 批量报告
- **Token**: 10000+
- **响应**: 异步
- **用途**: 每日收盘报告

## 快速开始

```python
from core.stock_screener import StockScreener

screener = StockScreener()

# 方案 A: 0 Token 筛选
result = screener.screen_stocks()
print(f"筛选结果: {result['filtered']} 只股票")

# 方案 B: 低 Token 分析
compressed = screener.analyze_stocks(result['stocks'])
prompt = screener.generate_prompt(compressed, "recommend")
# 发送给大模型...
```

## 定时任务

```bash
# 每日更新数据
0 15 * * * python3 scripts/daily_update.py
```

## 目录结构

```
stock-data-optimizer/
├── config/
│   └── config.py          # 配置文件
├── core/
│   ├── data_fetcher.py    # 数据获取
│   ├── token_optimizer.py # Token 优化
│   └── stock_screener.py  # 股票筛选
├── scripts/
│   └── daily_update.py    # 每日更新
├── data/
│   └── cache/             # 缓存数据
└── SKILL.md               # 本文件
```

## Token 消耗对比

| 方案 | 单次Token | 每日总Token | 成本 |
|------|----------|------------|------|
| 无优化 | 8000 | 800,000 | 高 |
| 方案A | 0 | 0 | 无 |
| 方案B | 3000 | 30,000 | 低 |
| 方案C | 10000 | 10,000 | 低 |

## 依赖

```bash
pip install tushare pandas
```

## API 配置

```python
TUSHARE_CONFIG = {
    "token": "your_token",
    "http_url": "http://lianghua.nanyangqiankun.top",
}
```

---
*设计实现: 2026-03-13*
