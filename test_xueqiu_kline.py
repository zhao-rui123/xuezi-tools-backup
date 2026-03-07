#!/usr/bin/env python3
"""
雪球K线数据测试
获取历史日线数据并计算技术指标
"""

import requests
import json
from datetime import datetime, timedelta

# 雪球配置
XUEQIU_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'origin': 'https://xueqiu.com',
    'referer': 'https://xueqiu.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

XUEQIU_COOKIES = {
    'xq_a_token': '8661982e927e023bf957bbc24b6fe85211ed4348',
    'xq_id_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjM0NDE2NzY4MjYsImlzcyI6InVjIiwiZXhwIjoxNzc1NDM0ODI0LCJjdG0iOjE3NzI4NDI4MjQ3MTQsImNpZCI6ImQ5ZDBuNEFadXAifQ.R8VRuz4gcsPrDv5jFU1c9WJYmulgC33sxR5Pkig9CRB-JZU4R--VkM9_mZjuKmx7g8SsJURq4UH5za6Qe9ey4RRtlKst1iL-2bKfX1_c5hxG9x6bHugx62zSlIJKYvqnPLwQ_rzgVH7daq11lfOoCya6LlOLZKffCgUiNzOlYSJTd9-m5Vf8ESs6kw1Nmh6lSEvbYym0VuvoN0YPiap9FlgLKUkuWLf9PJvo0Lfa6FoTAO6uMLTWYzUTSsTccTzF3xWUHb-ZBQY8kU72ZeDtXt_JzTYOov6ylbCOUSXPi4pY0_qZud_B71yFapuKheKbgMMZk2qPXZkbFgLHJJntXQ',
}

def fetch_kline(stock_code, period='day', count=60):
    """
    获取K线数据
    period: day/week/month
    count: 获取多少条数据
    """
    symbol = f"SH{stock_code}" if stock_code.startswith('6') else f"SZ{stock_code}"
    
    # 计算begin时间戳（获取最近count天的数据）
    end_time = int(datetime.now().timestamp() * 1000)
    begin_time = end_time - (count * 24 * 60 * 60 * 1000)  # 大约count天前
    
    # 雪球K线API
    url = f"https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol={symbol}&period={period}&count={count}&begin={begin_time}&end={end_time}&indicator=kline,ma,macd,kdj,boll,rsi"
    
    try:
        response = requests.get(url, headers=XUEQIU_HEADERS, cookies=XUEQIU_COOKIES, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"请求失败: {response.status_code}")
            print(f"响应: {response.text[:200]}")
    except Exception as e:
        print(f"异常: {e}")
    return None

def calculate_ma(closes, periods=[5, 10, 20, 60]):
    """计算移动平均线"""
    mas = {}
    for p in periods:
        if len(closes) >= p:
            mas[f'MA{p}'] = sum(closes[-p:]) / p
        else:
            mas[f'MA{p}'] = None
    return mas

def calculate_rsi(closes, period=14):
    """计算RSI指标"""
    if len(closes) < period + 1:
        return None
    
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0 for d in deltas[-period:]]
    losses = [-d if d < 0 else 0 for d in deltas[-period:]]
    
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(closes, fast=12, slow=26, signal=9):
    """计算MACD指标"""
    if len(closes) < slow:
        return None, None, None
    
    # 计算EMA
    def ema(data, period):
        multiplier = 2 / (period + 1)
        ema_values = [data[0]]
        for price in data[1:]:
            ema_values.append((price - ema_values[-1]) * multiplier + ema_values[-1])
        return ema_values
    
    ema_fast = ema(closes, fast)
    ema_slow = ema(closes, slow)
    
    macd_line = [f - s for f, s in zip(ema_fast, ema_slow)]
    signal_line = ema(macd_line, signal)
    histogram = [m - s for m, s in zip(macd_line, signal_line)]
    
    return macd_line[-1], signal_line[-1], histogram[-1]

def test_kline():
    """测试K线数据获取"""
    print("="*60)
    print("雪球K线数据测试")
    print("="*60)
    
    # 测试股票：赣锋锂业
    code = "002460"
    
    print(f"\n获取 {code} 日线数据...")
    data = fetch_kline(code, period='day', count=60)
    
    if data and data.get('data'):
        print("✅ K线数据获取成功!")
        
        items = data['data'].get('item', [])
        print(f"获取到 {len(items)} 条K线数据")
        
        # 解析K线数据
        # 格式: [timestamp, open, close, low, high, volume, amount, ...]
        klines = []
        for item in items:
            klines.append({
                'timestamp': item[0],
                'open': item[1],
                'close': item[2],
                'low': item[3],
                'high': item[4],
                'volume': item[5],
                'amount': item[6],
            })
        
        # 提取收盘价
        closes = [k['close'] for k in klines]
        
        print("\n最近5日K线:")
        for k in klines[-5:]:
            date = datetime.fromtimestamp(k['timestamp'] / 1000).strftime('%Y-%m-%d')
            print(f"  {date}: 开{k['open']:.2f} 收{k['close']:.2f} 高{k['high']:.2f} 低{k['low']:.2f} 量{k['volume']/10000:.0f}万")
        
        # 计算技术指标
        print("\n技术指标:")
        
        # 均线
        mas = calculate_ma(closes)
        current_price = closes[-1]
        print(f"\n当前价: {current_price:.2f}")
        print(f"MA5:  {mas['MA5']:.2f}" if mas['MA5'] else "MA5: N/A")
        print(f"MA10: {mas['MA10']:.2f}" if mas['MA10'] else "MA10: N/A")
        print(f"MA20: {mas['MA20']:.2f}" if mas['MA20'] else "MA20: N/A")
        print(f"MA60: {mas['MA60']:.2f}" if mas['MA60'] else "MA60: N/A")
        
        # 趋势判断
        if mas['MA5'] and mas['MA10'] and mas['MA20']:
            if current_price > mas['MA5'] > mas['MA10'] > mas['MA20']:
                trend = "多头排列 📈"
            elif current_price < mas['MA5'] < mas['MA10'] < mas['MA20']:
                trend = "空头排列 📉"
            else:
                trend = "震荡整理 ↔️"
            print(f"趋势: {trend}")
        
        # RSI
        rsi = calculate_rsi(closes)
        if rsi:
            rsi_status = "超买" if rsi > 70 else "超卖" if rsi < 30 else "正常"
            print(f"RSI(14): {rsi:.1f} ({rsi_status})")
        
        # MACD
        macd, signal, hist = calculate_macd(closes)
        if macd is not None:
            print(f"MACD: {macd:.3f} | Signal: {signal:.3f} | Histogram: {hist:.3f}")
            if hist > 0 and hist > (macd - signal) * 0.1:  # 简化判断
                print("MACD: 金叉或多头")
            elif hist < 0:
                print("MACD: 死叉或空头")
        
        return True
    else:
        print("❌ K线数据获取失败")
        if data:
            print(f"错误: {data}")
        return False

if __name__ == "__main__":
    success = test_kline()
    
    print("\n" + "="*60)
    if success:
        print("✅ K线API测试通过!")
        print("可以整合日线指标到股票分析系统")
    else:
        print("❌ K线API测试失败")
    print("="*60)
