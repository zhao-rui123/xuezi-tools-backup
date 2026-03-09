---
name: stock-analysis-suite
description: |
  股票分析完整套件 - 整合股票筛选、深度分析、数据源、客户端
  一站式股票分析解决方案
version: 1.0.0
---

# 股票分析套件 (Stock Analysis Suite)

一站式股票分析解决方案，整合筛选、分析、数据、监控全流程。

## 包含组件

| 组件 | 功能 | 路径 |
|------|------|------|
| **stock-screener** | 股票筛选和技术分析 | `../stock-screener/` |
| **stock-analysis-pro** | 深度分析和报告 | `../stock-analysis-pro/` |
| **tushare-stock-datasource** | 专业数据源 | `../tushare-stock-datasource/` |
| **xueqiu-stock-client** | 雪球客户端 | `../xueqiu-stock-client/` |

## 快速开始

### 完整分析流程
```bash
cd ~/.openclaw/workspace/skills/suites/stock-analysis-suite

# 1. 筛选股票
python3 ../stock-screener/screener.py

# 2. 深度分析
python3 ../stock-analysis-pro/stock_analyzer.py

# 3. 获取实时数据
python3 ../tushare-stock-datasource/tushare_client.py

# 4. 查看雪球资讯
python3 ../xueqiu-stock-client/xueqiu_client.py
```

### 一键完整分析
```bash
python3 suite_runner.py --full-analysis
```

## 功能特性

### 📊 筛选功能 (stock-screener)
- 技术指标筛选 (MACD、KDJ、MA)
- 形态识别 (杯柄、双底、头肩底)
- 支撑阻力分析
- 实时预警 (价格突破、均线突破)
- 财报日历追踪

### 📈 深度分析 (stock-analysis-pro)
- 基本面分析 (PE、PB、ROE)
- 技术面综合评分
- 估值策略 (PB-ROE、PEG)
- 技术形态识别
- 自动报告生成

### 📡 数据服务 (tushare-stock-datasource)
- A股实时行情
- 历史K线数据
- 财务数据
- 技术指标数据
- 稳定的API服务

### 📱 资讯客户端 (xueqiu-stock-client)
- 雪球热股追踪
- 个股资讯获取
- 社区情绪分析
- 实时公告监控

## 自选股配置

编辑 `config/watchlist.json`:
```json
{
  "stocks": [
    {"code": "002738", "name": "中矿资源", "market": "A股"},
    {"code": "002460", "name": "赣锋锂业", "market": "A股"},
    {"code": "000792", "name": "盐湖股份", "market": "A股"},
    {"code": "000725", "name": "京东方A", "market": "A股"},
    {"code": "600707", "name": "彩虹股份", "market": "A股"},
    {"code": "00981", "name": "中芯国际", "market": "港股"}
  ]
}
```

## 定时任务

```bash
# 每日收盘后分析 (16:30)
30 16 * * 1-5 ~/.openclaw/workspace/skills/suites/stock-analysis-suite/daily_analysis.sh

# 实时监控 (交易时段每30分钟)
*/30 9-15 * * 1-5 ~/.openclaw/workspace/skills/suites/stock-analysis-suite/monitor.sh
```

## 目录结构

```
stock-analysis-suite/
├── SKILL.md              # 本文档
├── suite_runner.py       # 套件统一入口
├── config/
│   └── watchlist.json    # 自选股配置
├── scripts/
│   ├── daily_analysis.sh # 每日分析脚本
│   └── monitor.sh        # 实时监控脚本
└── reports/              # 生成报告目录
```

## 使用示例

### 单股票深度分析
```python
from suite_runner import analyze_stock

result = analyze_stock("002738")
print(result['report'])
```

### 批量筛选
```python
from suite_runner import batch_screen

stocks = batch_screen(criteria={'rsi': {'min': 30, 'max': 70}})
```

### 生成组合报告
```bash
python3 suite_runner.py --portfolio-report
```

## 更新日志

### v1.0.0 (2026-03-09)
- ✅ 创建股票分析套件
- ✅ 整合4个股票相关技能包
- ✅ 统一入口和配置

---
*股票分析一站式解决方案*
