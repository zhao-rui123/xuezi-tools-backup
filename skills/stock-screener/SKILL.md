---
name: stock-screener
description: |
  股票筛选和分析工具，支持技术指标、基本面分析、形态识别、实时预警、财报日历等。
  v2.0 整合: 预警系统 + 财报日历
---

# Stock Screener - 股票筛选器 v2.0

股票分析和筛选工具，提供多维度股票分析能力。

## 功能特性

### 分析功能
- **技术分析**：支撑阻力、形态识别、技术指标
- **基本面分析**：财务数据、估值指标
- **周期性分析**：行业周期、季节性规律
- **策略回测**：买卖点策略验证

### 监控功能 ⭐NEW v2.0
- **实时预警**：价格突破、均线突破、异常波动、新高新低
- **财报日历**：财报披露日期、业绩预警、公告提醒
- **统一监控**：整合预警和财报的监控面板

### Web界面
可视化展示分析结果

## 使用方法

### 分析功能
```bash
python screener.py
python full_analysis.py <stock_code>
```

### 监控功能 ⭐NEW v2.0

#### 完整监控报告
```bash
python stock_monitor.py
```

#### 仅预警检查
```bash
python stock_monitor.py --alert
```

#### 仅财报检查
```bash
python stock_monitor.py --earnings --days 7
```

### Web界面
```bash
cd web
pip install -r requirements.txt
python app.py
```

## 文件说明

| 文件 | 功能 |
|------|------|
| screener.py | 主筛选器 |
| full_analysis.py | 完整分析报告 |
| stock_monitor.py | 统一监控面板 ⭐NEW |
| alert_engine.py | 预警引擎 ⭐NEW |
| earnings_calendar.py | 财报日历 ⭐NEW |
| technical_indicators.py | 技术指标计算 |
| pattern_recognition.py | 形态识别 |
| support_resistance.py | 支撑阻力分析 |
| fundamentals.py | 基本面分析 |
| cyclical_analysis.py | 周期性分析 |
| sell_strategy.py | 卖出策略 |
| analysis_report.py | 报告生成 |
| data_fetcher.py | 数据获取 |

## 更新日志

### v2.0 (2026-03-09)
- ✅ 整合 stock-alert 预警系统
- ✅ 整合 stock-earnings-calendar 财报日历
- ✅ 新增 stock_monitor.py 统一监控面板
- ✅ 支持命令行参数控制监控范围

### v1.0
- 初始版本，基础筛选分析功能
