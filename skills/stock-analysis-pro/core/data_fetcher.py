"""
数据获取模块
支持：新浪财经、雪球、腾讯财经
"""

import urllib.request
import requests
import json
import re
from typing import Dict, List, Optional

def is_hk_stock(code: str) -> bool:
    """判断是否为港股代码"""
    return len(code) == 5 and code[0] in '012368'

def fetch_sina_data(codes: List[str]) -> Dict:
    """获取新浪财经数据（支持A股+港股）"""
    a_codes = [c for c in codes if not is_hk_stock(c)]
    hk_codes = [c for c in codes if is_hk_stock(c)]
    
    result = {}
    
    # A股数据
    if a_codes:
        code_str = ",".join([f"sz{c}" if c.startswith(("0", "3")) else f"sh{c}" for c in a_codes])
        url = f"https://hq.sinajs.cn/list={code_str}"
        
        try:
            req = urllib.request.Request(url)
            req.add_header('Referer', 'https://finance.sina.com.cn')
            response = urllib.request.urlopen(req, timeout=10)
            data = response.read().decode('gb2312', errors='ignore')
            
            for line in data.strip().split('\n'):
                match = re.search(r'var hq_str_(\w+)="([^"]*)"', line)
                if match:
                    code = match.group(1)[2:]
                    fields = match.group(2).split(',')
                    if len(fields) >= 33:
                        result[code] = {
                            'name': fields[0],
                            'price': float(fields[3]),
                            'yesterday': float(fields[2]),
                        }
        except Exception as e:
            print(f"新浪A股API错误: {e}")
    
    # 港股数据
    if hk_codes:
        hk_code_str = ",".join([f"rt_hk{c}" for c in hk_codes])
        url = f"https://hq.sinajs.cn/list={hk_code_str}"
        
        try:
            req = urllib.request.Request(url)
            req.add_header('Referer', 'https://finance.sina.com.cn')
            response = urllib.request.urlopen(req, timeout=10)
            data = response.read().decode('gb2312', errors='ignore')
            
            for line in data.strip().split('\n'):
                match = re.search(r'var hq_str_rt_hk(\w+)="([^"]*)"', line)
                if match:
                    code = match.group(1)
                    fields = match.group(2).split(',')
                    if len(fields) >= 7:
                        result[code] = {
                            'name': fields[1] if fields[1] else fields[0],
                            'price': float(fields[6]) if fields[6] else 0,
                            'yesterday': float(fields[3]) if fields[3] else 0,
                        }
        except Exception as e:
            print(f"新浪港股API错误: {e}")
    
    return result

def fetch_xueqiu_data(codes: List[str], headers: Dict, cookies: Dict) -> Dict:
    """获取雪球数据"""
    symbols = []
    for c in codes:
        if is_hk_stock(c):
            symbols.append(c)
        elif c.startswith('6'):
            symbols.append(f'SH{c}')
        else:
            symbols.append(f'SZ{c}')
    
    symbol_str = ','.join(symbols)
    url = f"https://stock.xueqiu.com/v5/stock/batch/quote.json?symbol={symbol_str}&extend=detail&is_delay_hk=false"
    
    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=15)
        if response.status_code == 200:
            data = response.json()
            result = {}
            for item in data.get('data', {}).get('items', []):
                quote = item.get('quote', {})
                code = quote.get('code', '')
                if code.startswith(('SZ', 'SH')):
                    code = code[2:]
                if code:
                    result[code] = {
                        'name': quote.get('name'),
                        'current': quote.get('current'),
                        'percent': quote.get('percent', 0),
                        'pe_ttm': quote.get('pe_ttm'),
                        'pb': quote.get('pb'),
                        'turnover_rate': quote.get('turnover_rate'),
                        'volume_ratio': quote.get('volume_ratio'),
                        'high52w': quote.get('high52w'),
                        'low52w': quote.get('low52w'),
                    }
            return result
    except Exception as e:
        print(f"雪球API错误: {e}")
    return {}

def fetch_tencent_kline(stock_code: str, days: int = 60) -> Optional[Dict]:
    """获取腾讯财经K线数据"""
    try:
        if is_hk_stock(stock_code):
            tencent_code = f"hk{stock_code}"
        elif stock_code.startswith('6') or stock_code.startswith('688'):
            tencent_code = f"sh{stock_code}"
        else:
            tencent_code = f"sz{stock_code}"
        
        url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={tencent_code},day,,,{days},qfq"
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        if tencent_code not in data.get('data', {}):
            return None
        
        stock_data = data['data'][tencent_code]
        kline_data = stock_data.get('qfqday', []) or stock_data.get('day', [])
        
        if len(kline_data) < 20:
            return None
        
        closes = [float(day[2]) for day in kline_data]
        
        # 计算均线
        ma5 = sum(closes[-5:]) / 5
        ma10 = sum(closes[-10:]) / 10
        ma20 = sum(closes[-20:]) / 20
        current_price = closes[-1]
        
        # 趋势判断
        if current_price > ma5 > ma10 > ma20:
            trend = "多头"
            trend_emoji = "📈"
        elif current_price < ma5 < ma10 < ma20:
            trend = "空头"
            trend_emoji = "📉"
        else:
            trend = "震荡"
            trend_emoji = "↔️"
        
        # 计算RSI
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
        
        rsi_status = "超买" if rsi > 70 else "超卖" if rsi < 30 else "正常"
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
        print(f"腾讯K线获取失败 {stock_code}: {e}")
    return None

def fetch_market_index(index_code: str) -> Optional[Dict]:
    """获取大盘指数"""
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
                current = float(fields[1])
                yesterday = float(fields[2])
                change_pct = ((current - yesterday) / yesterday * 100) if yesterday > 0 else 0
                return {'price': current, 'change_pct': change_pct}
    except Exception:
        pass
    return None
