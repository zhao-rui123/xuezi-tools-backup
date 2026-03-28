#!/usr/bin/env python3
"""
自选股每日推送 - V2优化版
包含完整数据：新浪实时行情 + 雪球PE/PB
"""

import os
import sys
import json
import subprocess
import urllib.request
import re
from datetime import datetime

# ============ 配置 ============
FEISHU_USER_ID = "ou_5a7b7ec0339ffe0c1d5bb6c5bc162579"

WATCHLIST = [
    ("002738", "中矿资源", "sz"),
    ("002460", "赣锋锂业", "sz"),
    ("000792", "盐湖股份", "sz"),
    ("002240", "盛新锂能", "sz"),
    ("000822", "山东海化", "sz"),
    ("600707", "彩虹股份", "sh"),
]

MARKET_INDICES = {
    "上证指数": "sh000001",
    "深证成指": "sz399001",
    "创业板指": "sz399006",
}

# 雪球配置
XUEQIU_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Referer': 'https://xueqiu.com/',
}

XUEQIU_COOKIES = {
    'xq_a_token': '8661982e927e023bf957bbc24b6fe85211ed4348',
    'xq_id_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjM0NDE2NzY4MjYsImlzcyI6InVjIiwiZXhwIjoxNzc1NDM0ODI0LCJjdG0iOjE3NzI4NDI4MjQ3MTQsImNpZCI6ImQ5ZDBuNEFadXAifQ.R8VRuz4gcsPrDv5jFU1c9WJYmulgC33sxR5Pkig9CRB-JZU4R--VkM9_mZjuKmx7g8SsJURq4UH5za6Qe9ey4RRtlKst1iL-2bKfX1_c5hxG9x6bHugx62zSlIJKYvqnPLwQ_rzgVH7daq11lfOoCya6LlOLZKffCgUiNzOlYSJTd9-m5Vf8ESs6kw1Nmh6lSEvbYym0VuvoN0YPiap9FlgLKUkuWLf9PJvo0Lfa6FoTAO6uMLTWYzUTSsTccTzF3xWUHb-ZBQY8kU72ZeDtXt_JzTYOov6ylbCOUSXPi4pY0_qZud_B71yFapuKheKbgMMZk2qPXZkbFgLHJJntXQ',
}

def fetch_sina_data(codes):
    """获取新浪财经数据"""
    code_str = ",".join([f"{prefix}{code}" for code, name, prefix in codes])
    url = f"https://hq.sinajs.cn/list={code_str}"
    
    try:
        req = urllib.request.Request(url)
        req.add_header('Referer', 'https://finance.sina.com.cn')
        response = urllib.request.urlopen(req, timeout=10)
        data = response.read().decode('gb2312', errors='ignore')
        
        result = {}
        for line in data.strip().split('\n'):
            match = re.search(r'var hq_str_(\w+)="([^"]*)"', line)
            if match:
                full_code = match.group(1)
                code = full_code[2:]
                values = match.group(2).split(',')
                if len(values) >= 10:
                    result[code] = {
                        'name': values[0],
                        'open': float(values[1]),
                        'close': float(values[2]),
                        'current': float(values[3]),
                        'high': float(values[4]),
                        'low': float(values[5]),
                        'volume': float(values[8]) / 10000,
                        'amount': float(values[9]) / 100000000,
                    }
        return result
    except Exception as e:
        print(f"新浪API错误: {e}")
        return {}

def fetch_xueqiu_data(codes):
    """获取雪球数据（PE/PB等）"""
    symbols = []
    for c in codes:
        if c.startswith('6'):
            symbols.append(f'SH{c}')
        else:
            symbols.append(f'SZ{c}')
    
    symbol_str = ','.join(symbols)
    url = f"https://stock.xueqiu.com/v5/stock/batch/quote.json?symbol={symbol_str}&extend=detail"
    
    try:
        import requests
        response = requests.get(url, headers=XUEQIU_HEADERS, cookies=XUEQIU_COOKIES, timeout=15)
        if response.status_code == 200:
            data = response.json()
            result = {}
            for item in data.get('data', {}).get('items', []):
                quote = item.get('quote', {})
                code = quote.get('code', '').replace('SH', '').replace('SZ', '')
                if code:
                    result[code] = {
                        'pe_ttm': quote.get('pe_ttm'),
                        'pb': quote.get('pb'),
                        'turnover_rate': quote.get('turnover_rate'),
                    }
            return result
    except Exception as e:
        print(f"雪球API错误: {e}")
    return {}

def generate_report():
    """生成股票报告"""
    now = datetime.now()
    date_str = now.strftime("%Y年%m月%d日")
    time_str = now.strftime("%H:%M")
    
    # 获取数据
    indices_codes = [("000001", "上证指数", "sh"), ("399001", "深证成指", "sz"), ("399006", "创业板指", "sz")]
    indices_data = fetch_sina_data(indices_codes)
    stocks_data = fetch_sina_data(WATCHLIST)
    xueqiu_data = fetch_xueqiu_data([c[0] for c in WATCHLIST])
    
    lines = []
    lines.append("=" * 60)
    lines.append(f"📊 自选股日报 - {date_str} {time_str}")
    lines.append("=" * 60)
    lines.append("")
    
    # 大盘指数
    lines.append("【大盘指数】")
    for name, code in MARKET_INDICES.items():
        if code[2:] in indices_data:
            d = indices_data[code[2:]]
            change = d['current'] - d['close']
            percent = (change / d['close']) * 100
            emoji = "🔴" if change >= 0 else "🟢"
            lines.append(f"  {emoji} {name}: {d['current']:.2f} ({change:+.2f}, {percent:+.2f}%)")
    lines.append("")
    
    # 自选股
    lines.append("【自选股表现】")
    lines.append(f"{'名称':<8} {'代码':<10} {'现价':<8} {'涨跌':<8} {'涨幅':<8} {'PE':<8} {'PB':<6}")
    lines.append("-" * 60)
    
    total_change = 0
    for code, name, prefix in WATCHLIST:
        if code in stocks_data:
            d = stocks_data[code]
            xq = xueqiu_data.get(code, {})
            change = d['current'] - d['close']
            percent = (change / d['close']) * 100
            total_change += percent
            emoji = "🔴" if change >= 0 else "🟢"
            pe = f"{xq.get('pe_ttm', 'N/A'):.1f}" if xq.get('pe_ttm') else "N/A"
            pb = f"{xq.get('pb', 'N/A'):.2f}" if xq.get('pb') else "N/A"
            lines.append(f"{emoji}{name:<6} {code:<10} {d['current']:<8.2f} {change:<+8.2f} {percent:<+8.2f}% {pe:<8} {pb:<6}")
    
    # 统计
    avg_change = total_change / len(WATCHLIST)
    lines.append("")
    lines.append("【统计】")
    lines.append(f"组合平均: {avg_change:+.2f}%")
    
    sorted_stocks = sorted(
        [(c, stocks_data.get(c[0], {})) for c in WATCHLIST],
        key=lambda x: (x[1].get('current', 0) - x[1].get('close', 0)) / x[1].get('close', 1) if x[1].get('close') else 0,
        reverse=True
    )
    if sorted_stocks:
        top = sorted_stocks[0]
        bottom = sorted_stocks[-1]
        lines.append(f"🏆 最强: {top[0][1]}")
        lines.append(f"📉 最弱: {bottom[0][1]}")
    
    lines.append("")
    lines.append("=" * 60)
    lines.append("💡 详细分析请访问: http://106.54.25.161/")
    lines.append("=" * 60)
    
    return "\n".join(lines)

def send_report(report):
    """发送报告到飞书"""
    try:
        # 使用openclaw CLI发送
        env = os.environ.copy()
        env['PATH'] = '/opt/homebrew/bin:' + env.get('PATH', '')
        
        result = subprocess.run(
            ['openclaw', 'message', 'send', '--channel', 'feishu',
             '--target', FEISHU_USER_ID,
             '--message', report],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        if result.returncode == 0:
            print("✅ 股票报告已发送")
            return True
        else:
            print(f"❌ 发送失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False

if __name__ == "__main__":
    print("生成自选股日报...")
    report = generate_report()
    print(report)
    print("\n" + "=" * 60)
    print("发送到飞书...")
    send_report(report)
