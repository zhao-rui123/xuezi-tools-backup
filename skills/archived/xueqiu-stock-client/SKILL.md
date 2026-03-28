# Xueqiu Stock Client - 雪球股票数据源

## 概述

雪球 API 股票数据客户端，提供实时行情、估值指标、资金流向等数据。支持A股和港股。

## 特点

- ✅ **实时行情** - 毫秒级延迟
- ✅ **估值指标** - PE(TTM)、PB、换手率、量比
- ✅ **52周数据** - 52周最高/最低价
- ✅ **A股+港股** - 全市场支持
- ✅ **无需付费** - 使用 Cookie 认证

## 使用方法

### 基础使用

```python
import requests

# 雪球API配置
XUEQIU_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'origin': 'https://xueqiu.com',
    'referer': 'https://xueqiu.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

XUEQIU_COOKIES = {
    'xq_a_token': '你的token',
    'xq_id_token': '你的id_token',
    'xq_is_login': '1',
}

# 获取实时行情
def fetch_xueqiu_data(codes):
    symbols = []
    for c in codes:
        if len(c) == 5:  # 港股
            symbols.append(c)
        elif c.startswith('6'):  # A股沪市
            symbols.append(f'SH{c}')
        else:  # A股深市
            symbols.append(f'SZ{c}')
    
    symbol_str = ','.join(symbols)
    url = f"https://stock.xueqiu.com/v5/stock/batch/quote.json?symbol={symbol_str}&extend=detail"
    
    response = requests.get(url, headers=XUEQIU_HEADERS, cookies=XUEQIU_COOKIES)
    return response.json()

# 示例
data = fetch_xueqiu_data(['002460', '00981'])  # A股+港股
```

### 完整示例

参考：`stock_feishu_push_fusion.py`

```bash
cd ~/.openclaw/workspace
python3 stock_feishu_push_fusion.py
```

## 配置

### Cookie 配置

**获取方法**：
1. 登录 [xueqiu.com](https://xueqiu.com)
2. 按 F12 打开开发者工具 → Network
3. 刷新页面，找到 `quote.json` 请求
4. 右键 → Copy → Copy as cURL (bash)
5. 提取其中的 Cookie 部分

**关键字段**：
- `xq_a_token` - 访问令牌
- `xq_id_token` - 用户ID令牌
- `xq_is_login` - 登录状态

## 数据字段

| 字段 | 说明 | 示例 |
|-----|------|------|
| symbol | 股票代码 | SZ002460 / 00981 |
| name | 股票名称 | 赣锋锂业 |
| current | 当前价格 | 65.89 |
| percent | 涨跌幅 (%) | -1.83 |
| pe_ttm | 市盈率 (TTM) | -98.1 |
| pb | 市净率 | 3.26 |
| turnover_rate | 换手率 (%) | 2.85 |
| volume_ratio | 量比 | 0.74 |
| high52w | 52周最高价 | 76.19 |
| low52w | 52周最低价 | 27.88 |
| market_cap | 总市值 | ...

## 港股支持

### 港股代码格式
- 5位数字，以0/1/2/3/6/8开头
- 示例：00981（中芯国际）、01772（赣锋锂业）

### 港股数据
雪球港股提供完整数据：
- ✅ 实时价格、涨跌幅
- ✅ PE(TTM)、PB
- ✅ 换手率、量比
- ✅ 52周最高/最低

## 与腾讯K线融合

配合腾讯财经K线API，可计算技术指标：

```python
# 获取K线数据（支持A股+港股）
def fetch_tencent_kline(stock_code):
    if is_hk_stock(stock_code):
        tencent_code = f"hk{stock_code}"
    elif stock_code.startswith('6'):
        tencent_code = f"sh{stock_code}"
    else:
        tencent_code = f"sz{stock_code}"
    
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={tencent_code},day,,,60,qfq"
    # ...
```

技术指标：
- MA5/MA10/MA20 均线
- RSI(14) 相对强弱
- 趋势判断（多头/空头/震荡）
- 偏离度计算

## 自选股配置

默认监控 8 只（6只A股 + 2只港股）：

### A股
- 中矿资源 (002738)
- 赣锋锂业 (002460)
- 盐湖股份 (000792)
- 盛新锂能 (002240)
- 京东方 A (000725)
- 彩虹股份 (600707)

### 港股
- 中芯国际 (00981)
- 赣锋锂业 (01772)

修改 `WATCHLIST` 可自定义。

## 文件结构

```
skills/xueqiu-stock-client/
├── SKILL.md                    # 本文件
├── xueqiu_client.py            # 基础客户端
└── integration/
    ├── stock_feishu_push_fusion.py    # 融合版推送（推荐）
    └── stock_analyzer_fusion.py       # 融合版分析器
```

## 注意事项

- Cookie 会过期（通常1-3个月），需定期更新
- 雪球 API 有频率限制，建议间隔 1 秒以上
- 港股数据可能有15分钟延迟
- 周末和节假日无实时行情

## 相关项目

- **股票分析系统** - `knowledge-base/projects/股票分析系统/`
- **定时任务** - `scripts/stock_daily_push.sh`

---
*创建于: 2026-03-07*  
*版本: 2.0 - 支持港股+技术指标*
