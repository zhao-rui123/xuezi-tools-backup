#!/usr/bin/env python3
"""
自选股分析器 - 新浪财经 + 雪球 融合版
作者: 雪子助手
功能: 实时行情 + 详细估值指标 + 智能分析
"""

import urllib.request
import requests
import json
import re
from datetime import datetime
from typing import Dict, List, Optional

# ============ 雪球API配置 ============
XUEQIU_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'origin': 'https://xueqiu.com',
    'priority': 'u=1, i',
    'referer': 'https://xueqiu.com/',
    'sec-ch-ua': '"Not:A-Brand";v="99", "Microsoft Edge";v="145", "Chromium";v="145"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0',
}

XUEQIU_COOKIES = {
    'cookiesu': '841772842781365',
    'device_id': 'd30532eeec1ab76c3eb0cbcd787c258d',
    'xq_a_token': '8661982e927e023bf957bbc24b6fe85211ed4348',
    'xqat': '8661982e927e023bf957bbc24b6fe85211ed4348',
    'xq_r_token': 'a48ce0f397b2c32744404a9e435a0ab6f0b9ba59',
    'xq_id_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjM0NDE2NzY4MjYsImlzcyI6InVjIiwiZXhwIjoxNzc1NDM0ODI0LCJjdG0iOjE3NzI4NDI4MjQ3MTQsImNpZCI6ImQ5ZDBuNEFadXAifQ.R8VRuz4gcsPrDv5jFU1c9WJYmulgC33sxR5Pkig9CRB-JZU4R--VkM9_mZjuKmx7g8SsJURq4UH5za6Qe9ey4RRtlKst1iL-2bKfX1_c5hxG9x6bHugx62zSlIJKYvqnPLwQ_rzgVH7daq11lfOoCya6LlOLZKffCgUiNzOlYSJTd9-m5Vf8ESs6kw1Nmh6lSEvbYym0VuvoN0YPiap9FlgLKUkuWLf9PJvo0Lfa6FoTAO6uMLTWYzUTSsTccTzF3xWUHb-ZBQY8kU72ZeDtXt_JzTYOov6ylbCOUSXPi4pY0_qZud_B71yFapuKheKbgMMZk2qPXZkbFgLHJJntXQ',
    'xq_is_login': '1',
    'u': '3441676826',
}

# ============ 自选股配置 ============
WATCHLIST = [
    ("002738", "中矿资源", "锂矿/资源"),
    ("002460", "赣锋锂业", "锂电池/新能源"),
    ("000792", "盐湖股份", "盐湖提锂"),
    ("002240", "盛新锂能", "锂电池材料"),
    ("000725", "京东方A", "面板/显示"),
    ("600707", "彩虹股份", "面板/显示"),
    ("688981", "中芯国际", "半导体/芯片"),
]

MARKET_INDICES = {
    "上证指数": "sh000001",
    "深证成指": "sz399001",
    "创业板指": "sz399006",
}

# ============ 数据获取 ============

def fetch_sina_data(codes: List[str]) -> Dict:
    """从新浪财经获取实时数据（价格、成交量等）"""
    code_str = ",".join([
        f"sz{c}" if c.startswith(("0", "3")) else f"sh{c}"
        for c in codes
    ])
    
    url = f"https://hq.sinajs.cn/list={code_str}"
    
    try:
        req = urllib.request.Request(url)
        req.add_header('Referer', 'https://finance.sina.com.cn')
        response = urllib.request.urlopen(req, timeout=10)
        data = response.read().decode('gb2312', errors='ignore')
        return parse_sina_data(data)
    except Exception as e:
        print(f"新浪API错误: {e}")
        return {}

def parse_sina_data(data: str) -> Dict:
    """解析新浪返回的数据"""
    result = {}
    for line in data.strip().split('\n'):
        match = re.search(r'var hq_str_(\w+)="([^"]*)"', line)
        if match:
            code_key = match.group(1)
            code = code_key[2:]
            fields = match.group(2).split(',')
            
            if len(fields) >= 33:
                result[code] = {
                    'name': fields[0],
                    'open': float(fields[1]),
                    'yesterday_close': float(fields[2]),
                    'price': float(fields[3]),
                    'high': float(fields[4]),
                    'low': float(fields[5]),
                    'volume': int(float(fields[8])),
                    'amount': float(fields[9]),
                }
    return result

def fetch_xueqiu_data(codes: List[str]) -> Dict:
    """从雪球获取详细数据（PE/PB/换手率等）"""
    symbols = []
    for code in codes:
        if code.startswith('6'):
            symbols.append(f'SH{code}')
        else:
            symbols.append(f'SZ{code}')
    
    symbol_str = ','.join(symbols)
    url = f"https://stock.xueqiu.com/v5/stock/batch/quote.json?symbol={symbol_str}&extend=detail&is_delay_hk=false"
    
    try:
        response = requests.get(url, headers=XUEQIU_HEADERS, cookies=XUEQIU_COOKIES, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return parse_xueqiu_data(data)
    except Exception as e:
        print(f"雪球API错误: {e}")
    return {}

def parse_xueqiu_data(data: Dict) -> Dict:
    """解析雪球返回的数据"""
    result = {}
    items = data.get('data', {}).get('items', [])
    
    for item in items:
        quote = item.get('quote', {})
        code = quote.get('code', '')
        # 雪球code可能是 "SZ002460" 或 "002460"，统一处理
        if code.startswith(('SZ', 'SH')):
            code = code[2:]
        if code:
            result[code] = {
                'name': quote.get('name'),
                'current': quote.get('current'),
                'percent': quote.get('percent'),
                'chg': quote.get('chg'),
                'pe_ttm': quote.get('pe_ttm'),
                'pb': quote.get('pb'),
                'market_cap': quote.get('market_cap'),
                'turnover_rate': quote.get('turnover_rate'),
                'volume_ratio': quote.get('volume_ratio'),
                'amplitude': quote.get('amplitude'),
                'high52w': quote.get('high52w'),
                'low52w': quote.get('low52w'),
            }
    return result

def fetch_market_index(index_code: str) -> Optional[Dict]:
    """获取大盘指数数据"""
    try:
        url = f"https://hq.sinajs.cn/list={index_code}"
        req = urllib.request.Request(url)
        req.add_header('Referer', 'https://finance.sina.com.cn')
        response = urllib.request.urlopen(req, timeout=10)
        data = response.read().decode('gb2312', errors='ignore')

        match = re.search(r'var hq_str_\w+="([^"]*)"', data)
        if match:
            fields = match.group(1).split(',')
            if len(fields) >= 5:
                name = fields[0]
                current = float(fields[1])
                yesterday = float(fields[2])
                change = current - yesterday
                change_pct = (change / yesterday * 100) if yesterday > 0 else 0
                
                return {
                    'name': name,
                    'price': current,
                    'change': change,
                    'change_pct': change_pct,
                }
    except Exception:
        pass
    return None

# ============ 数据分析 ============

def analyze_stock(code: str, sina_data: Dict, xueqiu_data: Dict) -> Dict:
    """综合分析一只股票"""
    analysis = {
        'code': code,
        'name': '',
        'price': 0,
        'change_pct': 0,
        'pe_ttm': None,
        'pb': None,
        'turnover_rate': None,
        'volume_ratio': None,
        'position_52w': None,  # 52周位置（0-100%）
        'valuation': None,  # 估值判断
    }
    
    # 合并新浪和雪球数据
    if code in sina_data:
        sina = sina_data[code]
        analysis['name'] = sina['name']
        analysis['price'] = sina['price']
        analysis['yesterday_close'] = sina['yesterday_close']
        analysis['high'] = sina['high']
        analysis['low'] = sina['low']
        analysis['volume'] = sina['volume']
        analysis['amount'] = sina['amount']
    
    if code in xueqiu_data:
        xq = xueqiu_data[code]
        analysis['name'] = xq.get('name', analysis['name'])
        analysis['price'] = xq.get('current', analysis['price'])
        analysis['change_pct'] = xq.get('percent', 0)
        analysis['pe_ttm'] = xq.get('pe_ttm')
        analysis['pb'] = xq.get('pb')
        analysis['market_cap'] = xq.get('market_cap')
        analysis['turnover_rate'] = xq.get('turnover_rate')
        analysis['volume_ratio'] = xq.get('volume_ratio')
        analysis['amplitude'] = xq.get('amplitude')
        analysis['high52w'] = xq.get('high52w')
        analysis['low52w'] = xq.get('low52w')
        
        # 计算52周位置
        if xq.get('high52w') and xq.get('low52w') and xq.get('current'):
            high = xq['high52w']
            low = xq['low52w']
            current = xq['current']
            if high > low:
                analysis['position_52w'] = (current - low) / (high - low) * 100
        
        # 估值判断
        pe = xq.get('pe_ttm')
        if pe is not None:
            if pe < 0:
                analysis['valuation'] = '亏损'
            elif pe < 15:
                analysis['valuation'] = '低估'
            elif pe < 30:
                analysis['valuation'] = '合理'
            elif pe < 50:
                analysis['valuation'] = '偏高'
            else:
                analysis['valuation'] = '高估'
    
    return analysis

def generate_report():
    """生成分析报告"""
    print("="*70)
    print(f"自选股分析报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)
    
    codes = [s[0] for s in WATCHLIST]
    
    # 获取数据
    print("\n📊 正在获取数据...")
    sina_data = fetch_sina_data(codes)
    xueqiu_data = fetch_xueqiu_data(codes)
    
    # 分析每只股票
    print("\n" + "="*70)
    print("个股分析")
    print("="*70)
    
    total_change = 0
    stock_analyses = []
    
    for code, name, sector in WATCHLIST:
        analysis = analyze_stock(code, sina_data, xueqiu_data)
        stock_analyses.append(analysis)
        total_change += analysis['change_pct']
        
        # 显示
        change_str = f"{analysis['change_pct']:+.2f}%"
        pe_str = f"{analysis['pe_ttm']:.1f}" if analysis['pe_ttm'] else "N/A"
        pb_str = f"{analysis['pb']:.2f}" if analysis['pb'] else "N/A"
        turnover_str = f"{analysis['turnover_rate']:.2f}%" if analysis['turnover_rate'] else "N/A"
        pos_str = f"{analysis['position_52w']:.0f}%" if analysis['position_52w'] else "N/A"
        
        # 涨跌颜色标识
        change_emoji = "🔴" if analysis['change_pct'] > 0 else "🟢" if analysis['change_pct'] < 0 else "⚪"
        
        print(f"\n{change_emoji} {analysis['name']} ({code}) - {sector}")
        print(f"   现价: ¥{analysis['price']:.2f}  |  涨跌: {change_str}")
        print(f"   PE: {pe_str} ({analysis['valuation'] or 'N/A'})  |  PB: {pb_str}")
        print(f"   换手: {turnover_str}  |  量比: {analysis['volume_ratio'] or 'N/A'}")
        print(f"   52周位置: {pos_str}")
    
    # 大盘指数
    print("\n" + "="*70)
    print("大盘指数")
    print("="*70)
    
    for name, code in MARKET_INDICES.items():
        index_data = fetch_market_index(code)
        if index_data:
            change_str = f"{index_data['change_pct']:+.2f}%"
            emoji = "🔴" if index_data['change_pct'] > 0 else "🟢"
            print(f"{emoji} {name}: {index_data['price']:.2f} ({change_str})")
    
    # 汇总统计
    print("\n" + "="*70)
    print("组合统计")
    print("="*70)
    avg_change = total_change / len(WATCHLIST)
    avg_emoji = "🔴" if avg_change > 0 else "🟢"
    print(f"{avg_emoji} 平均涨跌幅: {avg_change:+.2f}%")
    
    # 今日最强/最弱
    sorted_stocks = sorted(stock_analyses, key=lambda x: x['change_pct'], reverse=True)
    print(f"\n🏆 今日最强: {sorted_stocks[0]['name']} ({sorted_stocks[0]['change_pct']:+.2f}%)")
    print(f"📉 今日最弱: {sorted_stocks[-1]['name']} ({sorted_stocks[-1]['change_pct']:+.2f}%)")
    
    # 估值分布
    print("\n估值分布:")
    valuation_counts = {}
    for sa in stock_analyses:
        v = sa['valuation'] or '未知'
        valuation_counts[v] = valuation_counts.get(v, 0) + 1
    for v, count in valuation_counts.items():
        print(f"   {v}: {count}只")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    generate_report()
