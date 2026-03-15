---
name: stock-suite
description: |
  股票分析工具 v3.0 (整合版)
  整合了 stock-analysis-pro 和 stock-screener 的全部功能
  支持：实时行情、技术分析、形态识别、估值分析、深度分析、预警监控
---

# Stock Suite - 股票分析工具 v3.0

专业级股票分析系统，整合了原 stock-analysis-pro 和 stock-screener 的全部功能。

## 功能特性

### 📈 实时行情监控
- **数据源**：新浪财经 + 雪球财经
- **市场覆盖**：A股 + 港股
- **更新频率**：实时获取

### 📊 技术指标分析
| 指标 | 说明 |
|------|------|
| MA均线 | MA5/MA10/MA20/MA60 |
| MACD | DIF/DEA/柱状图 |
| KDJ | K/D/J值 |
| RSI | 14日相对强弱指标 |
| 布林带 | 上轨/中轨/下轨 |

### 📐 技术形态识别
| 形态 | 描述 | 信号强度 |
|------|------|---------|
| 杯柄形态 | U型底部+小幅回调+突破 | ⭐⭐⭐⭐⭐ |
| 双底(W底) | 两个相近低点+颈线突破 | ⭐⭐⭐⭐ |
| 头肩底 | 左肩/头/右肩结构 | ⭐⭐⭐⭐ |
| 上升楔形 | 收敛上行（看跌） | ⭐⭐⭐ |
| 下降楔形 | 收敛下行（看涨） | ⭐⭐⭐ |

### 💰 估值策略筛选
| 策略 | 理念 | 筛选标准 |
|------|------|---------|
| PB-ROE | 低PB+高ROE | ROE/PB 排序 |
| PEG | 成长股 | PE/增速 < 1 |
| 综合估值 | 四维度评分 | PE+PB+ROE+流动性 |

### 🔍 深度分析
- **盈利能力**：ROE、毛利率、净利率
- **成长性**：营收增速、利润增速
- **财务健康**：PB、换手率
- **估值分位**：PE、PB历史分位
- **技术分析**：趋势、信号、形态

### 🚨 实时预警
- 价格突破MA5/MA20
- 异常涨跌幅（大涨/大跌/涨停/跌停）
- 成交量异常放大
- 创新高/新低

### 📅 财报日历
- 年报/季报披露日期
- 股东大会
- 业绩预告
- 重要公告提醒

### 📋 股票分类分析
根据股票类型自动选择分析框架：

| 股票类型 | 识别关键词 | 估值方法 |
|---------|-----------|---------|
| **周期股** | 锂、钴、铜、钢铁、煤炭 | PB分位 |
| **成长股** | 半导体、芯片、新能源 | PEG、PS |
| **价值股** | 银行、保险、公用事业 | PB-ROE、股息率 |

## 安装方法

### 方式1：复制到OpenClaw
```bash
cp -r stock-suite ~/.openclaw/workspace/skills/
```

### 方式2：手动安装
1. 复制到技能目录
2. 安装依赖：`pip install requests numpy`

## 配置说明

### 1. 雪球Cookie配置（可选）
编辑 `config/xueqiu_config.py`：
```python
XUEQIU_COOKIES = {
    'xq_a_token': '你的token',
    'xq_id_token': '你的id_token',
}
```

### 2. 自选股配置
编辑 `config/watchlist.py`：
```python
WATCHLIST = [
    ("002738", "中矿资源", "锂矿/资源"),
    ("002460", "赣锋锂业", "锂电池/新能源"),
]
```

## 使用方法

### 命令行使用

```bash
# 生成日报
python -m stock_suite daily

# 生成并发送飞书
python -m stock_suite daily --send-feishu

# 深度分析单只股票
python -m stock_suite analyze 002460 --name "赣锋锂业"

# 技术形态识别
python -m stock_suite pattern 002460
python -m stock_suite pattern --codes 002460,000725

# 估值策略筛选
python -m stock_suite screen
python -m stock_suite screen --codes 002460,000725

# 预警检查
python -m stock_suite alert

# 财报日历
python -m stock_suite earnings --days 7

# 统一监控面板
python -m stock_suite monitor

# 实时行情
python -m stock_suite quote
python -m stock_suite quote --codes 002460,000725

# 查看自选股
python -m stock_suite watchlist
```

### Python API使用

```python
from stock_suite import deep_analyze, check_alerts, generate_daily_report

# 深度分析
result = deep_analyze("002460", "赣锋锂业")
print(result)

# 预警检查
alerts = check_alerts()
for alert in alerts:
    print(f"{alert.code}: {alert.message}")

# 生成日报
report = generate_daily_report()
print(report)
```

## 输出示例

### 深度分析报告
```
🔍 深度分析报告: 赣锋锂业 (002460)
============================================================
【股票类型】周期股
【综合评级】推荐 ⭐⭐⭐⭐
【总分】72/100

【盈利能力】65/100 (良好)
   ROE: 15.2%, 毛利率: 35.5%, 净利率: 12.3%

【成长性】80/100 (优秀)
   营收增速: 45.2%, 利润增速: 38.5%

【财务健康】75/100 (良好)
   PB: 3.2, 换手率: 2.5%

【估值水平】65/100 (合理)
   PE: 18.5, PB: 3.2

【技术分析】75/100 (强势)
   形态: 双底形态(W底) (80%)
   信号: MACD金叉, KDJ金叉, 均线多头
```

### 统一监控面板
```
============================================================
📊 股票完整监控报告
============================================================

🚨 实时预警检查...
============================================================
🟢 [INFO] 赣锋锂业 (002460)
   类型: 近期新高
   详情: 创20日新高（85.50）

📅 财报日历检查...
============================================================
📊 赣锋锂业 (002460)
   事件: 年度股东大会
   时间: 2026-03-20 (7天后)

============================================================
✅ 监控完成
```

## 文件结构

```
stock-suite/
├── SKILL.md                    # 本文件
├── __init__.py                 # 包入口
├── __main__.py                 # CLI入口
├── config/
│   ├── __init__.py
│   ├── xueqiu_config.py        # 雪球配置
│   └── watchlist.py            # 自选股配置
├── core/
│   ├── __init__.py
│   ├── data_fetcher.py         # 数据获取
│   ├── technical_analysis.py   # 技术指标
│   ├── pattern_recognition.py  # 形态识别
│   ├── support_resistance.py   # 支撑阻力
│   ├── stock_classifier.py     # 股票分类
│   ├── valuation.py            # 估值分析
│   ├── alert_engine.py         # 预警引擎
│   ├── earnings_calendar.py    # 财报日历
│   ├── deep_analysis.py        # 深度分析
│   └── daily_report.py         # 日报生成
└── scripts/
    └── (定时任务脚本)
```

## 更新日志

### v3.0.0 (2026-03-12)
- ✅ 整合 stock-analysis-pro 和 stock-screener
- ✅ 新增统一CLI入口
- ✅ 新增股票分类器（周期股/成长股/价值股）
- ✅ 新增统一监控面板
- ✅ 优化代码结构和兼容性
- ✅ 支持 OpenClaw

### v2.0 (原 stock-analysis-pro)
- ✅ 技术形态识别
- ✅ 估值策略筛选
- ✅ 深度分析模块

### v2.0 (原 stock-screener)
- ✅ 预警系统
- ✅ 财报日历

## 注意事项

1. **Cookie有效期**：雪球Cookie通常1-3个月过期
2. **频率限制**：各API有频率限制，建议控制调用间隔
3. **数据延迟**：港股数据可能有15分钟延迟
4. **形态识别**：技术形态识别为概率性结果

## 作者

雪子助手

## 许可证

MIT License
