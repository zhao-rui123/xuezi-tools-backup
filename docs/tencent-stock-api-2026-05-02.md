# 腾讯财经API股票数据获取说明

## 📊 数据库位置
- **路径**：`/Volumes/cu/ocu/stock-screener/cache/tencent_cache.db`
- **格式**：SQLite
- **总股票数**：约5,826只

---

## 🔌 API地址

### 实时行情
```
http://qt.gtimg.cn/q=sz002594,sh600007
```
- 批量查询，逗号分隔
- 返回GBK编码
- 每批最多5只（防封IP）

### 历史K线
```
https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get
```
- 参数格式：`_var=kline_dayqfq&param={tencent_code},day,,800,qfq`
- 固定拉800天（前复权）
- 返回JSONP格式

---

## 📐 代码格式转换

| 标准格式 | 腾讯格式 |
|----------|----------|
| 002594.SZ | sz002594 |
| 600007.SH | sh600007 |
| 00981.HK | hk00981 |
| AAPL.US | usAAPL |

---

## 🔄 获取历史K线核心代码

```python
import urllib.request
import re
import json

def get_history_kline(tencent_code: str, period: str = 'day') -> pd.DataFrame:
    """
    获取历史K线数据（前复权）
    period: day/week/month
    """
    # 固定拉800天
    url = f"https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get?_var=kline_{period}qfq&param={tencent_code},{period},,,800,qfq"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        text = resp.read().decode('gbk', errors='replace')
    
    # 解析JSONP
    json_text = re.sub(r'^[^=]+=', '', text.strip())
    data = json.loads(json_text)
    
    # 取前复权数据
    day_data = data['data'][tencent_code].get('qfqday') or data['data'][tencent_code].get('day', [])
    
    records = []
    for item in day_data:
        if len(item) >= 6:
            records.append({
                'trade_date': item[0],   # 日期
                'open': float(item[1]),  # 开盘
                'close': float(item[2]), # 收盘
                'low': float(item[3]),   # 最低
                'high': float(item[4]),  # 最高
                'volume': int(float(item[5])),  # 成交量
            })
    
    return pd.DataFrame(records)
```

---

## 💾 缓存策略

| 缓存类型 | 有效期 | 说明 |
|----------|--------|------|
| 实时行情 | 24小时 | 批量缓存 |
| 历史K线 | 24小时 | 每次拉800天，后续从本地SQLite读 |

**缓存数据库**：`tencent_cache.db`
- 表：`data_cache`
- 存储方式：pickle序列化DataFrame
- 清理：自动清理过期数据

---

## 🚦 速率控制

- 每批5只股票
- 批次间延时0.5秒
- 最大重试3次
- 超时15秒

---

## 🔧 常用命令

### 增量更新（推荐）
```bash
python3 /Volumes/cu/ocu/stock-screener/incremental_update.py
```
- 只更新最新日期 < '2026-04-10' 的股票
- 耗时：约5-10分钟

### 全量更新（首次/损坏时）
```bash
python3 /Volumes/cu/ocu/stock-screener/download_all_stocks.py
```
- 重新下载全部5,826只股票
- 耗时：约6小时（不推荐）

### 运行选股
```bash
cd /Volumes/cu/ocu/stock-screener
python3 run_screener.py
```

---

## 📁 核心文件

| 文件 | 说明 |
|------|------|
| `data_source.py` | 腾讯API封装（类TencentDataSource） |
| `parsers/tencent_parser.py` | 解析器 |
| `incremental_update.py` | 增量更新脚本 |
| `download_all_stocks.py` | 全量下载 |
| `run_screener.py` | 选股程序入口 |
| `strategies/strategy_b_final.py` | 策略B v5 |

---

## ⚠️ 注意事项

1. **编码**：返回GBK，需要转换
2. **前复权**：参数带`qfq`，已处理
3. **格式混用**：数据库里有`sh600007`也有`600007.SH`，解析时需统一处理
4. **封IP风险**：批量请求要控制频率