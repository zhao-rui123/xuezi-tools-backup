#!/usr/bin/env python3
"""
自选股每日推送 - V3完整版
包含：新浪实时行情 + 雪球PE/PB + 技术分析(MA/RSI/趋势)
"""

import os
import sys
import json
import subprocess
import urllib.request
import re
from datetime import datetime

# 导入形态识别模块
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace')
from stock_pattern_recognition import analyze_patterns

# ============ 配置 ============
FEISHU_USER_ID = "ou_5a7b7ec0339ffe0c1d5bb6c5bc162579"

WATCHLIST = [
    ("002594", "比亚迪", "sz", "新能源汽车"),
    ("002460", "赣锋锂业", "sz", "锂电池/新能源"),
    ("002240", "盛新锂能", "sz", "锂电池材料"),
    ("600707", "彩虹股份", "sh", "面板/显示"),
    ("000725", "京东方A", "sz", "面板/显示"),
    ("000688", "国城矿业", "sz", "有色金属"),
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
    codes_only = [c[0] for c in codes]
    code_str = ",".join([f"{c[2]}{c[0]}" for c in codes])
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
                        'high52w': quote.get('high52w'),
                        'low52w': quote.get('low52w'),
                    }
            return result
    except Exception as e:
        print(f"雪球API错误: {e}")
    return {}

def fetch_tech_indicators(stock_code):
    """获取技术指标（MA/RSI）"""
    try:
        # 转换代码格式
        if stock_code.startswith('6'):
            tencent_code = f"sh{stock_code}"
        else:
            tencent_code = f"sz{stock_code}"
        
        # 获取最近60天日线数据
        url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={tencent_code},day,,,60,qfq"
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        kline_key = f"{tencent_code}"
        if kline_key not in data.get('data', {}):
            return None
        
        stock_data = data['data'][kline_key]
        kline_data = stock_data.get('qfqday', []) or stock_data.get('day', [])
        
        if len(kline_data) < 20:
            return None
        
        # 提取收盘价
        closes = [float(day[2]) for day in kline_data]
        
        # 计算均线
        ma5 = sum(closes[-5:]) / 5
        ma10 = sum(closes[-10:]) / 10
        ma20 = sum(closes[-20:]) / 20
        current_price = closes[-1]
        
        # 判断趋势
        if current_price > ma5 > ma10 > ma20:
            trend = "多头"
            trend_emoji = "📈"
        elif current_price < ma5 < ma10 < ma20:
            trend = "空头"
            trend_emoji = "📉"
        else:
            trend = "震荡"
            trend_emoji = "↔️"
        
        # 计算RSI (14日)
        rsi = 50
        if len(closes) >= 15:
            deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
            gains = [d if d > 0 else 0 for d in deltas[-14:]]
            losses = [-d if d < 0 else 0 for d in deltas[-14:]]
            avg_gain = sum(gains) / 14
            avg_loss = sum(losses) / 14
            if avg_loss > 0:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
        
        # RSI状态
        if rsi > 70:
            rsi_status = "超买"
        elif rsi < 30:
            rsi_status = "超卖"
        else:
            rsi_status = "正常"
        
        # 计算偏离度
        deviation = ((current_price - ma20) / ma20 * 100) if ma20 > 0 else 0
        
        return {
            'ma5': ma5,
            'ma10': ma10,
            'ma20': ma20,
            'trend': trend,
            'trend_emoji': trend_emoji,
            'rsi': rsi,
            'rsi_status': rsi_status,
            'deviation': deviation,
        }
    except Exception as e:
        print(f"技术指标获取失败 {stock_code}: {e}")
    return None

def get_valuation_label(pe):
    """获取估值标签"""
    if pe is None:
        return "N/A"
    if pe < 0:
        return "亏损"
    if pe < 15:
        return "极低"
    if pe < 25:
        return "偏低"
    if pe < 40:
        return "合理"
    if pe < 60:
        return "偏高"
    return "极高"

def generate_report():
    """生成股票报告"""
    now = datetime.now()
    date_str = now.strftime("%Y年%m月%d日")
    time_str = now.strftime("%H:%M")
    
    # 获取数据
    indices_codes = [("000001", "上证指数", "sh", ""), ("399001", "深证成指", "sz", ""), ("399006", "创业板指", "sz", "")]
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
    
    # 自选股基本面
    lines.append("【自选股 - 基本面】")
    for code, name, prefix, sector in WATCHLIST:
        if code in stocks_data:
            d = stocks_data[code]
            xq = xueqiu_data.get(code, {})
            change = d['current'] - d['close']
            percent = (change / d['close']) * 100
            emoji = "🔴" if change >= 0 else "🟢"
            pe = xq.get('pe_ttm')
            pb = xq.get('pb')
            turnover = xq.get('turnover_rate')
            high52w = xq.get('high52w')
            low52w = xq.get('low52w')
            
            pe_str = f"{pe:.1f}" if pe else "N/A"
            pb_str = f"{pb:.2f}" if pb else "N/A"
            turnover_str = f"{turnover:.1f}%" if turnover else "N/A"
            
            # 计算52周位置
            position = None
            if high52w and low52w and high52w > low52w:
                position = (d['current'] - low52w) / (high52w - low52w) * 100
            pos_str = f"{position:.0f}%" if position else "N/A"
            
            valuation = get_valuation_label(pe)
            
            lines.append(f"{emoji} {name} ({code}) {percent:+.2f}%")
            lines.append(f"   PE:{pe_str}({valuation}) PB:{pb_str} 换手:{turnover_str} 52周:{pos_str}")
    
    # 技术分析
    lines.append("")
    lines.append("【技术分析 - 日线指标】")
    for code, name, prefix, sector in WATCHLIST:
        tech = fetch_tech_indicators(code)
        if tech:
            emoji = tech['trend_emoji']
            rsi_emoji = "🔥" if tech['rsi'] > 70 else "❄️" if tech['rsi'] < 30 else "➖"
            dev_emoji = "📈" if tech['deviation'] > 5 else "📉" if tech['deviation'] < -5 else "➖"
            
            lines.append(f"{emoji} {name}: {tech['trend']}趋势")
            lines.append(f"   MA5:{tech['ma5']:.2f} MA10:{tech['ma10']:.2f} MA20:{tech['ma20']:.2f}")
            lines.append(f"   {rsi_emoji} RSI:{tech['rsi']:.1f}({tech['rsi_status']}) {dev_emoji} 偏离MA20:{tech['deviation']:+.1f}%")
        else:
            lines.append(f"⚪ {name}: 技术指标暂不可用")
    
    # K线形态识别
    lines.append("")
    lines.append("【K线形态识别】")
    pattern_found = False
    for code, name, prefix, sector in WATCHLIST:
        pattern = analyze_patterns(code, name)
        if pattern and pattern.confidence >= 60:
            pattern_found = True
            emoji = "📐" if pattern.direction == "bullish" else "📉"
            lines.append(f"{emoji} {name}: {pattern.pattern_name} ({pattern.confidence}%)")
            lines.append(f"   {pattern.suggestion}")
    if not pattern_found:
        lines.append("   暂无明确技术形态信号")
    
    # 统计
    total_change = 0
    count = 0
    for code, name, prefix, sector in WATCHLIST:
        if code in stocks_data:
            d = stocks_data[code]
            percent = (d['current'] - d['close']) / d['close'] * 100
            total_change += percent
            count += 1
    
    if count > 0:
        avg_change = total_change / count
        lines.append("")
        lines.append("【统计】")
        lines.append(f"组合平均: {avg_change:+.2f}%")
        
        # 排序找最强最弱
        stock_percents = []
        for code, name, prefix, sector in WATCHLIST:
            if code in stocks_data:
                d = stocks_data[code]
                percent = (d['current'] - d['close']) / d['close'] * 100
                stock_percents.append((name, percent))
        
        if stock_percents:
            stock_percents.sort(key=lambda x: x[1], reverse=True)
            lines.append(f"🏆 最强: {stock_percents[0][0]} ({stock_percents[0][1]:+.2f}%)")
            lines.append(f"📉 最弱: {stock_percents[-1][0]} ({stock_percents[-1][1]:+.2f}%)")
    
    lines.append("")
    lines.append("=" * 60)
    lines.append("💡 详细分析请访问: http://106.54.25.161/")
    lines.append("=" * 60)
    
    return "\n".join(lines)

def send_report(report):
    """发送报告到飞书"""
    try:
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
