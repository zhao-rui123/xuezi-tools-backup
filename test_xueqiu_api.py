#!/usr/bin/env python3
"""
雪球API测试与数据融合方案
测试雪球API可用性和数据结构
"""

import urllib.request
import json
from datetime import datetime

# 自选股列表
WATCHLIST = [
    ("002738", "中矿资源", "锂矿/资源"),
    ("002460", "赣锋锂业", "锂电池/新能源"),
    ("000792", "盐湖股份", "盐湖提锂"),
    ("002240", "盛新锂能", "锂电池材料"),
    ("000725", "京东方A", "面板/显示"),
    ("600707", "彩虹股份", "面板/显示"),
    ("688981", "中芯国际", "半导体/芯片"),
]

def get_xueqiu_token():
    """获取雪球访问token（从cookie中提取）"""
    # 雪球需要 cookies 中的 xq_a_token
    # 这里使用一个示例token，实际使用时可能需要从浏览器获取
    return None

def fetch_xueqiu_realtime(codes):
    """获取雪球实时行情数据"""
    # 雪球API格式: https://stock.xueqiu.com/v5/stock/batch/quote.json?symbol=SH600000,SZ000001
    symbols = []
    for code in codes:
        if code.startswith('6'):
            symbols.append(f'SH{code}')
        else:
            symbols.append(f'SZ{code}')
    
    symbol_str = ','.join(symbols)
    url = f"https://stock.xueqiu.com/v5/stock/batch/quote.json?symbol={symbol_str}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        return data
    except Exception as e:
        print(f"雪球API请求失败: {e}")
        return None

def fetch_xueqiu_detail(code):
    """获取雪球个股详细信息（PE/PB/市值等）"""
    symbol = f'SH{code}' if code.startswith('6') else f'SZ{code}'
    url = f"https://stock.xueqiu.com/v5/stock/f10/cn/skratio.json?symbol={symbol}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        return data
    except Exception as e:
        print(f"雪球详情API请求失败: {e}")
        return None

def fetch_xueqiu_cashflow(code):
    """获取雪球资金流向数据"""
    symbol = f'SH{code}' if code.startswith('6') else f'SZ{code}'
    url = f"https://stock.xueqiu.com/v5/stock/f10/cn/skhfst.json?symbol={symbol}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        return data
    except Exception as e:
        print(f"雪球资金流向API请求失败: {e}")
        return None

def fetch_xueqiu_rating(code):
    """获取雪球机构评级数据"""
    symbol = f'SH{code}' if code.startswith('6') else f'SZ{code}'
    url = f"https://stock.xueqiu.com/v5/stock/f10/cn/skrating.json?symbol={symbol}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        return data
    except Exception as e:
        print(f"雪球评级API请求失败: {e}")
        return None

def test_xueqiu_apis():
    """测试雪球各API接口"""
    print("="*60)
    print("雪球API测试开始")
    print("="*60)
    
    # 测试1: 批量实时行情
    print("\n[测试1] 批量实时行情")
    codes = [s[0] for s in WATCHLIST[:3]]  # 先测试3只
    realtime_data = fetch_xueqiu_realtime(codes)
    if realtime_data and realtime_data.get('data'):
        print("✅ 实时行情API可用")
        items = realtime_data['data'].get('items', [])
        print(f"   获取到 {len(items)} 只股票数据")
        if items:
            item = items[0]
            quote = item.get('quote', {})
            print(f"   示例 - {quote.get('name')}:")
            print(f"     当前价: {quote.get('current')}")
            print(f"     涨跌幅: {quote.get('percent')}%")
            print(f"     市盈率(TTM): {quote.get('pe_ttm')}")
            print(f"     市净率: {quote.get('pb')}")
            print(f"     总市值: {quote.get('market_cap')}")
            print(f"     换手率: {quote.get('turnover_rate')}%")
    else:
        print("❌ 实时行情API不可用")
    
    # 测试2: 个股详细信息
    print("\n[测试2] 个股详细信息（PE/PB等）")
    test_code = "002460"  # 赣锋锂业
    detail = fetch_xueqiu_detail(test_code)
    if detail and detail.get('data'):
        print(f"✅ 详情API可用 - {test_code}")
        # 打印数据结构
        print(f"   数据结构: {list(detail['data'].keys())[:5]}")
    else:
        print("❌ 详情API不可用")
    
    # 测试3: 资金流向
    print("\n[测试3] 资金流向")
    cashflow = fetch_xueqiu_cashflow(test_code)
    if cashflow and cashflow.get('data'):
        print(f"✅ 资金流向API可用 - {test_code}")
    else:
        print("❌ 资金流向API不可用")
    
    # 测试4: 机构评级
    print("\n[测试4] 机构评级")
    rating = fetch_xueqiu_rating(test_code)
    if rating and rating.get('data'):
        print(f"✅ 评级API可用 - {test_code}")
        rating_data = rating['data']
        print(f"   数据结构: {list(rating_data.keys())[:5]}")
    else:
        print("❌ 评级API不可用")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    test_xueqiu_apis()
