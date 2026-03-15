---
name: mx_select_stock
description: 基于东方财富的智能选股skill，支持条件选股、板块选股、股票推荐
metadata:
  openclaw:
    requires:
      bins: [curl]
    install: []
---

# 妙想智能选股skill (mx_select_stock)

通过自然语言查询进行选股，支持A股、港股、美股。

## 功能

### 1. 条件选股
- 行情指标选股（涨幅、跌幅、成交量等）
- 财务指标选股（营收、利润、市盈率等）

### 2. 板块选股
- 查询指定行业/板块内的股票
- 板块指数成分股

### 3. 股票推荐
- 根据条件推荐股票

## 使用方式

### API配置

已在mx_search中配置了API KEY，可复用。

### 调用示例

```bash
curl -X POST 'https://mkapi2.dfcfs.com/finskillshub/api/claw/stock-screen' \
  -H 'Content-Type: application/json' \
  -H 'apikey: mkt_zdTwvCWmIr9g4mHoM8sOsaK8M_ffrhinQPP-GAkhTNs' \
  --data '{"keyword": "今日涨幅2%的股票", "pageNo": 1, "pageSize": 20}'
```

### 查询示例

|类型|示例|
|----|----|
|涨幅选股|今日涨幅5%的股票、近一周涨幅10%的股票|
|财务选股|市盈率小于20的股票、净利润增长的股票|
|板块选股|新能源板块股票、AI概念股|
|推荐|推荐低估值的银行股|

## 返回说明

- 返回JSON格式的选股结果
- 包含股票代码、简称、市场、最新价、涨跌幅等
- 支持分页查询

## 数据为空

提示用户到东方财富妙想AI进行选股。

## 注意事项

- 避免大数据量查询
- 采用权威数据，避免过时信息
