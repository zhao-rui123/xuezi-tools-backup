# Stock Analysis Pro 技能包文档

> 专业股票分析系统 - A股+港股实时监控、技术形态识别、估值策略筛选、深度基本面分析

---

## 📋 技能包信息

| 属性 | 值 |
|------|-----|
| **名称** | stock-analysis-pro |
| **版本** | v2.0.0 |
| **作者** | 雪子助手 |
| **位置** | `skills/stock-analysis-pro/` |
| **更新时间** | 2026-03-07 |

---

## 🎯 核心功能

### 1. 实时行情监控
- **数据源**: 新浪财经 + 雪球 + 腾讯财经（三源融合）
- **市场覆盖**: A股 + 港股
- **更新频率**: 实时获取

### 2. 技术指标分析
| 指标 | 说明 |
|------|------|
| MA均线 | MA5/MA10/MA20 |
| RSI | 14日相对强弱指标（超买>70/超卖<30） |
| 趋势判断 | 多头/空头/震荡 |
| 偏离度 | 当前价与MA20偏离百分比 |

### 3. 技术形态识别
| 形态 | 信号强度 | 应用场景 |
|------|---------|---------|
| **杯柄形态** | ⭐⭐⭐⭐⭐ | 底部反转突破 |
| **双底(W底)** | ⭐⭐⭐⭐ | 双底支撑确认 |
| **头肩底** | ⭐⭐⭐⭐ | 复杂底部反转 |

### 4. 估值策略筛选
| 策略 | 理念 | 筛选标准 |
|------|------|---------|
| **PB-ROE** | 低PB+高ROE | ROE/PB 排序 |
| **PEG** | 成长股 | PE/盈利增速 < 1 |
| **综合估值** | 四维度评分 | PE+PB+ROE+流动性 |

### 5. 深度分析四维度
- 💰 **盈利能力** - ROE估算、PE/PB评估
- 📈 **成长性** - 52周位置、趋势判断
- 🏦 **财务健康** - 资产质量、流动性、盈利状况
- 📉 **估值分位** - 价格/PE/PB历史分位

---

## 📁 文件结构

```
skills/stock-analysis-pro/
├── SKILL.md                    # 技能包主文档
├── __init__.py                 # 包入口（便捷函数）
├── __main__.py                 # CLI命令行工具
│
├── config/                     # 配置文件
│   ├── xueqiu_config.py        # 雪球Cookie配置
│   └── watchlist.py            # 自选股配置
│
├── core/                       # 核心模块
│   ├── data_fetcher.py         # 数据获取（新浪/雪球/腾讯）
│   ├── pattern_recognition.py  # 技术形态识别
│   ├── valuation.py            # 估值策略筛选
│   ├── deep_analysis.py        # 深度四维度分析
│   └── daily_report.py         # 日报生成
│
└── scripts/
    └── daily_push.sh           # 定时任务脚本
```

---

## 🚀 使用方法

### 方式1: CLI命令行

```bash
cd ~/.openclaw/workspace/skills/stock-analysis-pro

# 生成日报
python3 -m stock_analysis_pro daily

# 生成并发送到飞书
python3 -m stock_analysis_pro daily --send-feishu

# 深度分析单只股票
python3 -m stock_analysis_pro analyze 002460 --name "赣锋锂业"

# 技术形态识别
python3 -m stock_analysis_pro pattern 002460

# 估值策略筛选
python3 -m stock_analysis_pro screen --codes 002460,000725,00981
```

### 方式2: Python导入

```python
from stock_analysis_pro import deep_analyze, scan_patterns, valuation_screen

# 深度分析（返回格式化报告）
report = deep_analyze("002460", "赣锋锂业")
print(report)

# 批量扫描形态
patterns = scan_patterns(["002460", "000725", "00981"])
for p in patterns:
    print(f"{p['name']}: {p['pattern']} (置信度{p['confidence']}%)")

# 估值筛选
results = valuation_screen(["002460", "000725"])
print(results['pb_roe'])      # PB-ROE策略结果
print(results['comprehensive']) # 综合估值结果
```

### 方式3: 定时任务

```bash
# 编辑 crontab
crontab -e

# 添加（工作日16:30执行，港股收盘后）
30 16 * * 1-5 ~/.openclaw/workspace/skills/stock-analysis-pro/scripts/daily_push.sh
```

---

## ⚙️ 配置说明

### 1. 自选股配置

**文件**: `config/watchlist.py`

```python
WATCHLIST = [
    # A股 (6位代码)
    ("002738", "中矿资源", "锂矿/资源"),
    ("002460", "赣锋锂业", "锂电池/新能源"),
    ("000792", "盐湖股份", "盐湖提锂"),
    ("002240", "盛新锂能", "锂电池材料"),
    ("000725", "京东方A", "面板/显示"),
    ("600707", "彩虹股份", "面板/显示"),
    
    # 港股 (5位代码)
    ("00981", "中芯国际", "半导体/芯片"),
    ("01772", "赣锋锂业", "锂电池/新能源"),
]
```

### 2. 雪球Cookie配置

**文件**: `config/xueqiu_config.py`

```python
XUEQIU_COOKIES = {
    'xq_a_token': '你的token',
    'xq_id_token': '你的id_token',
    'xq_is_login': '1',
}
```

**获取方法**:
1. 登录 [xueqiu.com](https://xueqiu.com)
2. F12 → Network → 找到 `quote.json` 请求
3. 右键 → Copy → Copy as cURL (bash)
4. 提取 `xq_a_token` 和 `xq_id_token`

---

## 📊 输出示例

### 日报格式
```
📊 自选股日报 - 2026-03-07 16:30

【大盘指数】
🟢 上证指数: 4085.90 (-0.55%)
🟢 深证成指: 14015.54 (-0.52%)

【自选股 - 基本面】
🟢 中矿资源 (002738) -1.78%
   PE:137.3(高估) PB:4.75 换手:2.6% 52周:71%
🔴 中芯国际 (00981) +0.49%
   PE:110.0(高估) PB:2.95 换手:1.2% 52周:44%

【技术分析 - 日线指标】
↔️ 中矿资源: 震荡趋势
   MA5:82.25 MA10:85.34 MA20:84.20
   ➖ RSI:45.9(正常) 📉 偏离MA20:-6.1%
📉 中芯国际: 空头趋势
   MA5:62.34 MA10:65.77 MA20:67.55
   ❄️ RSI:28.3(超卖) 📉 偏离MA20:-8.5%

【技术形态识别】
📐 赣锋锂业: 双底形态(W底) (85%)
   🔥 已突破颈线或即将突破
📐 盐湖股份: 双底形态(W底) (85%)
   🔥 已突破颈线或即将突破

【估值策略筛选】
🏆 PB-ROE策略:
   1. ROE 5.0% / PB 1.22 = 4.09 (京东方A)
   2. ROE 14.7% / PB 4.74 = 3.09 (盐湖股份)
📊 综合估值:
   1. 得分105 - PE合理 | PB极低 | ROE较低 (京东方A)

【统计】
组合平均: -1.43%
🏆 最强: 中芯国际 (+0.49%)
📉 最弱: 彩虹股份 (-4.14%)
```

### 深度分析报告
```
============================================================
🔍 深度分析报告: 京东方A (000725)
============================================================
【综合评级】买入 ⭐⭐⭐⭐
【总分】65/100 ⭐⭐⭐⭐

【盈利能力】30/100
   ROE 5.0% (差)

【成长性】70/100
   估值适中+趋势向上 (52周68%)

【财务健康】95/100
   资产质量高(PB低) | 流动性良好 | 盈利稳定

【估值分位】
   价格分位68% | PE合理 | PB极低

============================================================
```

---

## 🔧 API参考

### 便捷函数

| 函数 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `deep_analyze(code, name)` | code, name | str | 深度分析报告 |
| `scan_patterns(codes)` | codes(list) | list[dict] | 形态识别结果 |
| `valuation_screen(codes)` | codes(list) | dict | 估值筛选结果 |
| `generate_daily_report()` | 无 | str | 生成日报 |

### 核心模块

| 模块 | 功能 |
|------|------|
| `core.data_fetcher` | 多源数据获取 |
| `core.pattern_recognition` | 技术形态识别 |
| `core.valuation` | 估值策略计算 |
| `core.deep_analysis` | 四维度深度分析 |
| `core.stock_classifier` | 股票类型识别（新增） |
| `core.cyclical_analysis` | 周期股专项分析（新增） |
| `core.growth_analysis` | 成长股专项分析（新增） |
| `core.value_analysis` | 价值股专项分析（新增） |
| `core.enhanced_analysis` | 增强版分析（新增） |
| `core.daily_report` | 日报生成与推送 |

---

## 📝 更新日志

### v2.1.0 (2026-03-07) - 三类股票差异化分析
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
- ✅ 支持港股数据
- ✅ 完整技能包封装

### v1.0.0 (2026-03-04)
- ✅ 基础版本：新浪+雪球+腾讯K线
- ✅ 技术指标：MA/RSI/趋势判断
- ✅ 定时推送

---

## 🔗 相关资源

- **项目文档**: [股票分析系统](../projects/股票分析系统/README.md)
- **方正证券报告**: [OpenClaw赋能金融投研17案例](../reports/方正证券_OpenClaw金融投研_17案例.pdf)
- **技能包位置**: `skills/stock-analysis-pro/`

---

## ⚠️ 注意事项

1. **Cookie有效期**: 雪球Cookie通常1-3个月过期，需定期更新
2. **频率限制**: API有频率限制，避免频繁调用
3. **港股延迟**: 港股数据可能有15分钟延迟
4. **形态识别**: 置信度<60%的形态不显示
5. **定时任务**: 建议16:30执行（港股16:10收盘后）

---

*文档更新时间: 2026-03-07*
