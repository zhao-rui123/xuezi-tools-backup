# Stock Analysis Pro - 专业股票分析技能包

## 概述

专业级股票分析系统，支持A股+港股实时监控、技术形态识别、估值策略筛选、深度基本面分析。

## 功能特性

### 📈 实时行情监控
- **数据源融合**：新浪财经 + 雪球 + 腾讯财经
- **市场覆盖**：A股 + 港股
- **更新频率**：实时获取

### 📊 技术指标分析
| 指标 | 说明 |
|------|------|
| MA均线 | MA5/MA10/MA20 |
| RSI | 14日相对强弱指标 |
| 趋势判断 | 多头/空头/震荡 |
| 偏离度 | 当前价与MA20偏离百分比 |

### 📐 技术形态识别
| 形态 | 描述 | 信号强度 |
|------|------|---------|
| 杯柄形态 | U型底部+小幅回调+突破 | ⭐⭐⭐⭐⭐ |
| 双底(W底) | 两个相近低点+颈线突破 | ⭐⭐⭐⭐ |
| 头肩底 | 左肩/头/右肩结构 | ⭐⭐⭐⭐ |

### 💰 估值策略筛选
| 策略 | 理念 | 筛选标准 |
|------|------|---------|
| PB-ROE | 低PB+高ROE | ROE/PB 排序 |
| PEG | 成长股 | PE/增速 < 1 |
| 综合估值 | 四维度评分 | PE+PB+ROE+流动性 |

### 🔍 深度分析维度
- **盈利能力**：ROE、毛利率、净利率
- **成长性**：营收增速、利润增速、52周位置
- **财务健康**：负债率、现金流、流动比率
- **估值分位**：历史PE/PB分位、行业对比

### 🎯 三类股票差异化分析（v2.1新增）

根据股票类型自动选择分析框架：

| 股票类型 | 识别关键词 | 分析框架 | 估值方法 |
|---------|-----------|---------|---------|
| **周期股** | 锂、钴、铜、钢铁、煤炭、化工、航运 | 周期位置+供需分析 | **PB、EV/产能**（不看PE） |
| **成长股** | 半导体、芯片、新能源、生物医药 | 成长空间+PEG | **PEG、PS**（看增速） |
| **价值股** | 银行、保险、公用事业、白酒 | ROE稳定性+股息 | **PB-ROE、股息率** |

#### 周期股专项分析
- **周期位置判断**：底部/复苏/上升/顶部/下降
- **供需分析**：产能利用率、库存、下游需求
- **估值方法**：PB分位、资源量估值、重置成本
- **周期前景**：行业景气度跟踪

#### 成长股专项分析
- **成长阶段**：早期/成长期/成熟期
- **PEG估值**：PE/增速比值
- **成长空间**：渗透率、TAM分析
- **竞争优势**：技术壁垒、网络效应

#### 价值股专项分析
- **ROE质量**：连续5年ROE稳定性
- **PB-ROE得分**：ROE/PB综合评分
- **股息分析**：股息率、分红率、连续性
- **安全边际**：历史PB分位、破净分析

## 安装方法

### 方式1：ClawHub安装
```bash
clawhub install stock-analysis-pro
```

### 方式2：手动安装
1. 复制技能包到 `~/.openclaw/workspace/skills/`
2. 安装依赖：`pip install requests numpy`
3. 配置雪球Cookie（见配置章节）

## 配置说明

### 1. 雪球Cookie配置
编辑 `config/xueqiu_config.py`：

```python
XUEQIU_COOKIES = {
    'xq_a_token': '你的token',
    'xq_id_token': '你的id_token',
    'xq_is_login': '1',
}
```

**获取方法**：
1. 登录 [xueqiu.com](https://xueqiu.com)
2. F12 → Network → 找到quote.json请求
3. 右键 → Copy → Copy as cURL
4. 提取Cookie中的 `xq_a_token` 和 `xq_id_token`

### 2. 自选股配置
编辑 `config/watchlist.py`：

```python
WATCHLIST = [
    # (代码, 名称, 行业)
    ("002738", "中矿资源", "锂矿/资源"),
    ("002460", "赣锋锂业", "锂电池/新能源"),
    ("00981", "中芯国际", "半导体/芯片"),  # 港股
]
```

### 3. 定时任务配置
```bash
# 编辑 crontab
crontab -e

# 添加（工作日16:30执行）
30 16 * * 1-5 ~/.openclaw/workspace/skills/stock-analysis-pro/scripts/daily_push.sh
```

## 使用方法

### 1. 自动日报推送
每天16:30自动推送包含以下内容的报告：
- 大盘指数
- 自选股基本面
- 技术指标（MA/RSI/趋势）
- 技术形态识别
- 估值策略筛选
- 统计汇总

### 2. 单股深度分析
```python
from stock_analysis_pro import deep_analyze

result = deep_analyze("002460", "赣锋锂业")
print(result)
```

### 3. 技术形态扫描
```python
from stock_analysis_pro import scan_patterns

patterns = scan_patterns(["002460", "000725"])
for p in patterns:
    print(f"{p['name']}: {p['pattern']} (置信度{p['confidence']}%)")
```

### 4. 估值筛选
```python
from stock_analysis_pro import valuation_screen

results = valuation_screen(["002460", "000725"])
print(results['pb_roe'])  # PB-ROE策略结果
print(results['peg'])     # PEG策略结果
```

## 命令行使用

### 查看日报
```bash
# 生成并查看日报
python3 -m stock_analysis_pro daily

# 发送到飞书
python3 -m stock_analysis_pro daily --send-feishu
```

### 单股分析
```bash
# 深度分析单只股票
python3 -m stock_analysisPro analyze 002460 --name "赣锋锂业"

# 分析港股
python3 -m stock_analysis_pro analyze 00981 --name "中芯国际"
```

### 形态识别
```bash
# 扫描技术形态
python3 -m stock_analysis_pro pattern 002460

# 批量扫描
python3 -m stock_analysis_pro pattern --codes 002460,000725,00981
```

### 估值筛选
```bash
# 运行估值策略筛选
python3 -m stock_analysis_pro screen --codes 002460,000725,00981
```

## 输出示例

### 日报格式
```
📊 自选股日报 - 2026-03-07 16:30

【大盘指数】
🟢 上证指数: 4085.90 (-0.55%)

【自选股 - 基本面】
🟢 中矿资源 (002738) -1.78%
   PE:137.3(高估) PB:4.75 换手:2.6% 52周:71%

【技术分析 - 日线指标】
↔️ 中矿资源: 震荡趋势
   MA5:82.25 MA10:85.34 MA20:84.20
   ➖ RSI:45.9(正常) 📉 偏离MA20:-6.1%

【技术形态识别】
📐 中矿资源: 双底形态(W底) (85%)
   🔥 已突破颈线或即将突破

【估值策略筛选】
🏆 PB-ROE策略:
   1. ROE 5.0% / PB 1.22 = 4.09 (京东方A)
📊 综合估值:
   1. 得分105 - PE合理 | PB极低 (京东方A)

【统计】
组合平均: -1.43%
🏆 最强: 中芯国际 (+0.49%)
```

### 深度分析报告
```
🔍 深度分析报告: 京东方A (000725)
============================================================
【综合评级】买入 ⭐⭐⭐⭐
【总分】65/100

【盈利能力】30/100
   ROE 5.0% (差)

【成长性】70/100
   估值适中+趋势向上 (52周68%)

【财务健康】95/100
   资产质量高(PB低) | 流动性良好 | 盈利稳定

【估值分位】
   价格分位68% | PE合理 | PB极低
```

## 文件结构

```
stock-analysis-pro/
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
│   ├── technical_analysis.py   # 技术分析
│   ├── pattern_recognition.py  # 形态识别
│   ├── valuation.py            # 估值策略
│   └── deep_analysis.py        # 深度分析
├── scripts/
│   └── daily_push.sh           # 定时任务脚本
└── examples/
    ├── basic_usage.py          # 基础使用示例
    └── advanced_analysis.py    # 高级分析示例
```

## API参考

### 核心函数

#### `deep_analyze(code, name)`
深度分析单只股票
- **参数**: code(代码), name(名称)
- **返回**: DeepAnalysisResult对象

#### `scan_patterns(codes)`
扫描技术形态
- **参数**: codes(代码列表)
- **返回**: PatternResult列表

#### `valuation_screen(codes)`
估值策略筛选
- **参数**: codes(代码列表)
- **返回**: dict{'pb_roe': [], 'peg': [], 'comprehensive': []}

#### `generate_daily_report()`
生成日报
- **返回**: 报告字符串

## 注意事项

1. **Cookie有效期**：雪球Cookie通常1-3个月过期，需定期更新
2. **频率限制**：各API有频率限制，建议控制调用间隔
3. **数据延迟**：港股数据可能有15分钟延迟
4. **形态识别**：技术形态识别为概率性结果，置信度<60%不显示

## 更新日志

### v2.1.0 (2026-03-07)
- ✅ 新增股票类型识别模块（周期股/成长股/价值股）
- ✅ 新增周期股专项分析框架（周期位置+供需+PB估值）
- ✅ 新增成长股专项分析框架（PEG+成长空间+竞争优势）
- ✅ 新增价值股专项分析框架（PB-ROE+股息率+安全边际）
- ✅ 增强版深度分析，自动根据股票类型选择分析框架
- ✅ 周期前景分析（针对锂矿等大宗商品行业）

### v2.0.0 (2026-03-07)
- ✅ 新增技术形态识别（杯柄/双底/头肩底）
- ✅ 新增估值策略筛选（PB-ROE/PEG/综合）
- ✅ 新增深度分析模块（四维度评分）
- ✅ 支持港股数据（00981/01772）
- ✅ 集成到日报推送

### v1.0.0 (2026-03-04)
- ✅ 基础版本：新浪财经+雪球+腾讯K线
- ✅ 技术指标：MA/RSI/趋势判断
- ✅ 定时推送

## 相关技能包

- `xueqiu-stock-client` - 雪球数据客户端
- `tushare-stock-datasource` - Tushare数据源
- `stock-screener` - 股票筛选器

## 作者

雪子助手

## 许可证

MIT License
