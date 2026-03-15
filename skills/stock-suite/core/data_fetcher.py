"""
数据获取模块 - 整合版
支持：新浪财经、雪球、腾讯财经
支持：A股 + 港股实时行情
"""

import urllib.request
import requests
import json
import re
import os
from typing import Dict, List, Optional
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def is_hk_stock(code: str) -> bool:
    """判断是否为港股代码"""
    return len(code) == 5 and code[0] in '012368'

def get_config():
    """获取配置"""
    try:
        import sys
        import os
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        sys.path.insert(0, config_path)
        from xueqiu_config import XUEQIU_COOKIES, XUEQIU_HEADERS
        return XUEQIU_COOKIES, XUEQIU_HEADERS
    except ImportError:
        return {}, {}

def fetch_sina_quotes(codes: List[str]) -> Dict:
    """获取新浪财经实时行情（支持A股+港股）"""
    a_codes = [c for c in codes if not is_hk_stock(c)]
    hk_codes = [c for c in codes if is_hk_stock(c)]
    
    result = {}
    
    if a_codes:
        code_str = ",".join([f"sz{c}" if c.startswith(("0", "3")) else f"sh{c}" for c in a_codes])
        url = f"https://hq.sinajs.cn/list={code_str}"
        
        try:
            req = urllib.request.Request(url)
            req.add_header('Referer', 'https://finance.sina.com.cn')
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
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
                            'price': float(fields[3]) if fields[3] else 0,
                            'yesterday': float(fields[2]) if fields[2] else 0,
                            'open': float(fields[1]) if fields[1] else 0,
                            'high': float(fields[4]) if fields[4] else 0,
                            'low': float(fields[5]) if fields[5] else 0,
                            'volume': int(fields[8]) if fields[8] else 0,
                            'amount': float(fields[9]) if fields[9] else 0,
                            'bid1': float(fields[11]) if len(fields) > 11 and fields[11] else 0,
                            'ask1': float(fields[13]) if len(fields) > 13 and fields[13] else 0,
                        }
        except Exception as e:
            print(f"新浪A股API错误: {e}")
    
    if hk_codes:
        hk_code_str = ",".join([f"rt_hk{c}" for c in hk_codes])
        url = f"https://hq.sinajs.cn/list={hk_code_str}"
        
        try:
            req = urllib.request.Request(url)
            req.add_header('Referer', 'https://finance.sina.com.cn')
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
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
                            'open': float(fields[2]) if fields[2] else 0,
                            'high': float(fields[4]) if fields[4] else 0,
                            'low': float(fields[5]) if fields[5] else 0,
                            'volume': int(float(fields[12])) if len(fields) > 12 and fields[12] else 0,
                        }
        except Exception as e:
            print(f"新浪港股API错误: {e}")
    
    return result

def fetch_xueqiu_quotes(codes: List[str]) -> Dict:
    """获取雪球财经数据（支持A股+港股）"""
    cookies, headers = get_config()
    if not cookies:
        return {}
    
    symbols = []
    for c in codes:
        if is_hk_stock(c):
            symbols.append(c)
        elif c.startswith('6') or c.startswith('688'):
            symbols.append(f'SH{c}')
        else:
            symbols.append(f'SZ{c}')
    
    if not symbols:
        return {}
    
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
                        'market_cap': quote.get('market_cap'),
                        'float_market_cap': quote.get('float_market_cap'),
                        'roe': quote.get('roe'),
                        'gross_margin': quote.get('gross_margin'),
                        'net_margin': quote.get('net_margin'),
                        'revenue_growth': quote.get('revenue_growth'),
                        'profit_growth': quote.get('profit_growth'),
                    }
            return result
    except Exception as e:
        print(f"雪球API错误: {e}")
    return {}

def fetch_tencent_kline(stock_code: str, days: int = 60) -> Optional[List[Dict]]:
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
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        if tencent_code not in data.get('data', {}):
            return None
        
        stock_data = data['data'][tencent_code]
        kline_data = stock_data.get('qfqday', []) or stock_data.get('day', [])
        
        if len(kline_data) < 5:
            return None
        
        result = []
        for k in kline_data:
            if len(k) >= 5:
                result.append({
                    'date': k[0],
                    'open': float(k[1]),
                    'close': float(k[2]),
                    'low': float(k[3]),
                    'high': float(k[4]),
                    'volume': int(float(k[5])) if len(k) > 5 and k[5] else 0,
                    'amount': float(k[6]) if len(k) > 6 and k[6] else 0,
                })
        return result
    except Exception as e:
        print(f"腾讯K线获取失败 {stock_code}: {e}")
    return None

def fetch_monthly_kline(stock_code: str, months: int = 24) -> Optional[List[Dict]]:
    """获取月K线数据"""
    try:
        if is_hk_stock(stock_code):
            tencent_code = f"hk{stock_code}"
        elif stock_code.startswith('6') or stock_code.startswith('688'):
            tencent_code = f"sh{stock_code}"
        else:
            tencent_code = f"sz{stock_code}"
        
        url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={tencent_code},month,,,{months},qfq"
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        if tencent_code not in data.get('data', {}):
            return None
        
        stock_data = data['data'][tencent_code]
        kline_data = stock_data.get('qfqmonth', []) or stock_data.get('month', [])
        
        if len(kline_data) < 2:
            return None
        
        result = []
        for k in kline_data:
            if len(k) >= 5:
                result.append({
                    'date': k[0],
                    'open': float(k[1]),
                    'close': float(k[2]),
                    'low': float(k[3]),
                    'high': float(k[4]),
                    'volume': int(float(k[5])) if len(k) > 5 and k[5] else 0,
                })
        return result
    except Exception as e:
        print(f"获取月K线失败 {stock_code}: {e}")
    return None

def fetch_market_index(index_code: str = "sh000001") -> Optional[Dict]:
    """获取大盘指数"""
    try:
        url = f"https://hq.sinajs.cn/list={index_code}"
        req = urllib.request.Request(url)
        req.add_header('Referer', 'https://finance.sina.com.cn')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        response = urllib.request.urlopen(req, timeout=10)
        data = response.read().decode('gb2312', errors='ignore')
        
        match = re.search(r'var hq_str_\w+="([^"]*)"', data)
        if match:
            fields = match.group(1).split(',')
            if len(fields) >= 5:
                current = float(fields[1])
                yesterday = float(fields[2])
                change_pct = ((current - yesterday) / yesterday * 100) if yesterday > 0 else 0
                return {'price': current, 'change_pct': change_pct, 'name': fields[0]}
    except Exception:
        pass
    return None

def get_stock_list() -> List[Dict]:
    """获取A股股票列表（简化版）"""
    try:
        url = "https://hq.sinajs.cn/list=sh600000,sh600036,sh600519,sh601318,sh000001"
        req = urllib.request.Request(url)
        req.add_header('Referer', 'https://finance.sina.com.cn')
        req.add_header('User-Agent', 'Mozilla/5.0')
        response = urllib.request.urlopen(req, timeout=10)
        data = response.read().decode('gb2312', errors='ignore')
        
        stocks = []
        demo_codes = [
            ("600000", "浦发银行"), ("600036", "招商银行"), ("600519", "贵州茅台"),
            ("601318", "中国平安"), ("600036", "招商银行"), ("000001", "平安银行"),
            ("002460", "赣锋锂业"), ("002738", "中矿资源"), ("300750", "宁德时代"),
            ("600276", "恒瑞医药"), ("000725", "京东方A"), ("601888", "中国中免"),
        ]
        
        quotes = fetch_sina_quotes([c[0] for c in demo_codes])
        
        for code, name in demo_codes:
            if code in quotes:
                stocks.append({
                    'code': code,
                    'name': quotes[code].get('name', name),
                })
            else:
                stocks.append({'code': code, 'name': name})
        
        return stocks
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        return []

def get_realtime_quote(stock_code: str) -> Dict:
    """获取单只股票实时行情"""
    quotes = fetch_sina_quotes([stock_code])
    return quotes.get(stock_code, {})

def get_stock_kline(stock_code: str, days: int = 60) -> Optional[List[Dict]]:
    """获取股票K线数据（日线）"""
    return fetch_tencent_kline(stock_code, days)

def get_stock_monthly(stock_code: str, months: int = 24) -> Optional[List[Dict]]:
    """获取股票月K线数据"""
    return fetch_monthly_kline(stock_code, months)
