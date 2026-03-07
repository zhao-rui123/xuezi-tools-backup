#!/usr/bin/env python3
"""
雪球API测试 - 带认证信息
"""

import urllib.request
import json

def fetch_xueqiu_with_auth():
    """尝试不同方式获取雪球数据"""
    
    # 方法1: 添加更多 headers
    url = "https://stock.xueqiu.com/v5/stock/batch/quote.json?symbol=SH600000,SZ000001"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://xueqiu.com/',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read().decode('utf-8'))
        print("✅ 方法1成功")
        print(f"   数据: {data.keys()}")
        return data
    except Exception as e:
        print(f"❌ 方法1失败: {e}")
    
    # 方法2: 尝试单个股票详情
    url2 = "https://stock.xueqiu.com/v5/stock/quote.json?symbol=SH600000&extend=detail"
    try:
        req = urllib.request.Request(url2, headers=headers)
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read().decode('utf-8'))
        print("✅ 方法2成功")
        return data
    except Exception as e:
        print(f"❌ 方法2失败: {e}")
    
    # 方法3: 尝试手机版API
    url3 = "https://stock.xueqiu.com/v5/stock/app/stock/SH600000/quote.json"
    headers_m = headers.copy()
    headers_m['User-Agent'] = 'Xueqiu iPhone 14.0'
    try:
        req = urllib.request.Request(url3, headers=headers_m)
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read().decode('utf-8'))
        print("✅ 方法3成功")
        return data
    except Exception as e:
        print(f"❌ 方法3失败: {e}")
    
    return None

if __name__ == "__main__":
    print("测试雪球API不同接入方式...")
    fetch_xueqiu_with_auth()
