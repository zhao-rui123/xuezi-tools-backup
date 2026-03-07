#!/usr/bin/env python3
"""
测试港股数据获取
中芯国际港股: 00981.HK
"""

import urllib.request
import requests
import json
import re

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

def test_xueqiu_hk():
    """测试雪球港股数据"""
    print("="*60)
    print("雪球港股数据测试 - 中芯国际(00981)")
    print("="*60)
    
    # 港股代码格式: 00981
    symbol = "00981"
    url = f"https://stock.xueqiu.com/v5/stock/quote.json?symbol={symbol}&extend=detail"
    
    try:
        response = requests.get(url, headers=XUEQIU_HEADERS, cookies=XUEQIU_COOKIES, timeout=15)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and data['data'].get('quote'):
                quote = data['data']['quote']
                print("✅ 雪球港股数据获取成功!")
                print(f"\n名称: {quote.get('name')}")
                print(f"代码: {quote.get('code')}")
                print(f"当前价: {quote.get('current')}")
                print(f"涨跌幅: {quote.get('percent')}%")
                print(f"PE(TTM): {quote.get('pe_ttm')}")
                print(f"PB: {quote.get('pb')}")
                print(f"市值: {quote.get('market_cap')}")
                return True
            else:
                print(f"❌ 数据结构错误: {data}")
        else:
            print(f"❌ 请求失败: {response.text[:200]}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    return False

def test_tencent_hk():
    """测试腾讯港股K线"""
    print("\n" + "="*60)
    print("腾讯财经港股K线测试 - 中芯国际")
    print("="*60)
    
    # 腾讯港股格式
    codes_to_try = [
        "hk00981",
        "hk0981",
        "rt_hk00981",
        "rt_hk0981",
    ]
    
    for code in codes_to_try:
        url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,,,60,qfq"
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
            response = urllib.request.urlopen(req, timeout=10)
            data = json.loads(response.read().decode('utf-8'))
            
            print(f"\n尝试格式: {code}")
            print(f"响应keys: {list(data.keys())}")
            
            if data.get('data'):
                print(f"data keys: {list(data['data'].keys())}")
                if code in data['data'] and data['data'][code].get('qfqday'):
                    klines = data['data'][code]['qfqday']
                    print(f"✅ 成功! 获取到 {len(klines)} 条K线")
                    if klines:
                        latest = klines[-1]
                        print(f"最新K线: {latest}")
                    return True
        except Exception as e:
            print(f"❌ {code}: {e}")
    
    return False

def test_sina_hk():
    """测试新浪港股"""
    print("\n" + "="*60)
    print("新浪财经港股测试 - 中芯国际")
    print("="*60)
    
    # 新浪港股格式
    url = "https://hq.sinajs.cn/list=rt_hk00981"
    
    try:
        req = urllib.request.Request(url)
        req.add_header('Referer', 'https://finance.sina.com.cn')
        response = urllib.request.urlopen(req, timeout=10)
        data = response.read().decode('gb2312', errors='ignore')
        
        print(f"响应: {data[:200]}")
        
        if 'var hq_str_' in data:
            print("✅ 新浪港股API可用")
            return True
    except Exception as e:
        print(f"❌ {e}")
    return False

if __name__ == "__main__":
    xueqiu_ok = test_xueqiu_hk()
    tencent_ok = test_tencent_hk()
    sina_ok = test_sina_hk()
    
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"雪球港股: {'✅' if xueqiu_ok else '❌'}")
    print(f"腾讯港股K线: {'✅' if tencent_ok else '❌'}")
    print(f"新浪港股: {'✅' if sina_ok else '❌'}")
