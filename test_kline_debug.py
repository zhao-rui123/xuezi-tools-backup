#!/usr/bin/env python3
"""
雪球K线数据测试 - 调试版
"""

import requests
import json
from datetime import datetime

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

def test_kline():
    code = "002460"
    symbol = f"SH{code}" if code.startswith('6') else f"SZ{code}"
    
    # 尝试不同的API格式
    # 格式1: 只用count
    url = f"https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol={symbol}&period=day&count=60"
    
    print(f"请求URL: {url}")
    
    try:
        response = requests.get(url, headers=XUEQIU_HEADERS, cookies=XUEQIU_COOKIES, timeout=15)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n数据结构: {list(data.keys())}")
            
            if data.get('data'):
                print(f"data字段: {list(data['data'].keys())}")
                
                # 检查item字段
                items = data['data'].get('item')
                if items:
                    print(f"\n获取到 {len(items)} 条数据")
                    print(f"第一条数据: {items[0]}")
                else:
                    print("\n没有item数据")
                    print(f"data内容: {data['data']}")
            else:
                print(f"错误: {data}")
    except Exception as e:
        print(f"异常: {e}")

if __name__ == "__main__":
    test_kline()
