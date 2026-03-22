# A股周线量化回测策略

## 策略规则

### 买入条件
- 周MACD金叉 + 周KDJ金叉（双金叉）

### 卖出条件（满足任一即卖出）
1. 买入后三个月内，单月K线涨幅>50%
2. 买入后金叉变死叉
3. 买入三个月出现亏损（浮亏）

### 仓位管理
- 初始资金: 100万
- 每个股票仓位相同（动态平衡）
- 每个周末检查并执行买入/卖出/再平衡
- 最大持仓: 20只股票
- 每次最多买入: 5只股票

## 使用方法

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行回测
```bash
python backtest.py
```

### 结果输出
- `backtest_results.json`: 详细回测结果（JSON格式）
- `trades.csv`: 交易记录（CSV格式）

## 回测结果字段说明

### backtest_results.json
- `initial_capital`: 初始资金
- `final_value`: 最终资金
- `total_return`: 总收益率(%)
- `total_trades`: 总交易次数
- `profitable_trades`: 盈利交易次数
- `losing_trades`: 亏损交易次数
- `yearly_returns`: 年度收益率
- `trades`: 交易记录列表

### trades.csv 字段
- `ts_code`: 股票代码
- `name`: 股票名称
- `buy_date`: 买入日期
- `sell_date`: 卖出日期
- `buy_price`: 买入价格
- `sell_price`: 卖出价格
- `shares`: 持股数量
- `profit`: 盈利金额
- `profit_pct`: 盈亏比例(%)
- `reason`: 卖出原因
