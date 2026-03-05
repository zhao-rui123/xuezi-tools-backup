---
name: stock-screener
description: |
  股票筛选和分析工具，支持技术指标、基本面分析、形态识别等。
---

# Stock Screener - 股票筛选器

股票分析和筛选工具，提供多维度股票分析能力。

## 功能特性

- **技术分析**：支撑阻力、形态识别、技术指标
- **基本面分析**：财务数据、估值指标
- **周期性分析**：行业周期、季节性规律
- **策略回测**：买卖点策略验证
- **Web界面**：可视化展示分析结果

## 使用方法

### 命令行
```bash
python screener.py
python full_analysis.py <stock_code>
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
| technical_indicators.py | 技术指标计算 |
| pattern_recognition.py | 形态识别 |
| support_resistance.py | 支撑阻力分析 |
| fundamentals.py | 基本面分析 |
| cyclical_analysis.py | 周期性分析 |
| sell_strategy.py | 卖出策略 |
| analysis_report.py | 报告生成 |
| data_fetcher.py | 数据获取 |
