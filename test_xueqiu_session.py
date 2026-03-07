#!/usr/bin/env python3
"""
雪球API - 先获取session再请求
"""

import requests
import json

def get_xueqiu_session():
    """先访问首页获取session"""
    session = requests.Session()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    # 先访问首页
    print("访问雪球首页获取session...")
    try:
        resp = session.get('https://xueqiu.com', headers=headers, timeout=10)
        print(f"首页状态: {resp.status_code}")
        print(f"获取到的cookies: {session.cookies.get_dict()}")
    except Exception as e:
        print(f"访问首页失败: {e}")
    
    return session

def test_with_session(session):
    """使用session请求API"""
    print("\n" + "="*60)
    print("使用session请求API")
    print("="*60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://xueqiu.com/',
    }
    
    symbol = "SZ002460"
    url = f"https://stock.xueqiu.com/v5/stock/quote.json?symbol={symbol}&extend=detail"
    
    try:
        response = session.get(url, headers=headers, timeout=15)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功!")
            quote = data.get('data', {}).get('quote', {})
            print(f"\n{quote.get('name')} ({quote.get('code')})")
            print(f"  当前价: {quote.get('current')}")
            print(f"  涨跌幅: {quote.get('percent')}%")
            print(f"  PE(TTM): {quote.get('pe_ttm')}")
            print(f"  PB: {quote.get('pb')}")
            return True
        else:
            print(f"❌ 失败: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

if __name__ == "__main__":
    session = get_xueqiu_session()
    test_with_session(session)
