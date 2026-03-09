#!/usr/bin/env python3
import akshare as ak
from datetime import datetime

# 自选股列表
stocks = [
    ('002738', '中矿资源', '锂矿/资源'),
    ('002460', '赣锋锂业', '锂电池/新能源'),
    ('000792', '盐湖股份', '盐湖提锂'),
    ('002240', '盛新锂能', '锂电池材料'),
    ('000725', '京东方A', '面板/显示'),
    ('600707', '彩虹股份', '面板/显示'),
]

print('📊 自选股实时行情 -', datetime.now().strftime('%Y-%m-%d %H:%M'))
print('=' * 70)
print(f"{'代码':<8} {'名称':<8} {'板块':<12} {'现价':<8} {'涨跌':<8} {'成交额':<10}")
print('-' * 70)

# 获取全部A股行情
try:
    df = ak.stock_zh_a_spot_em()
    for code, name, sector in stocks:
        row = df[df['代码'] == code]
        if not row.empty:
            price = float(row['最新价'].values[0])
            change_pct = float(row['涨跌幅'].values[0])
            amount = float(row['成交额'].values[0]) / 10000  # 万元
            print(f"{code:<8} {name:<8} {sector:<12} ¥{price:<7.2f} {change_pct:+.2f}%   {amount:.0f}万")
except Exception as e:
    print(f'获取失败: {e}')
