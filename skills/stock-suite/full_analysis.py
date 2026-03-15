#!/usr/bin/env python3
"""
雪子股票完整分析系统
整合自有技能包 + 妙想数据
"""

import json
import subprocess
import sys

# === 1. 自有技能包：股票分类 ===
def get_stock_type(code, name, industry):
    result = subprocess.run(
        ['python3', '-c', f'''
from core.stock_classifier import classify_stock
result = classify_stock("{code}", "{name}", "{industry}")
print(result.stock_type)
print(result.analysis_framework)
print(result.valuation_method)
'''],
        capture_output=True, text=True, cwd='~/.openclaw/workspace/skills/stock-suite'.replace('~', '/Users/zhaoruicn')
    )
    lines = result.stdout.strip().split('\n')
    return {'type': lines[0], 'framework': lines[1], 'method': lines[2]} if len(lines) >= 3 else {}

# === 2. 自有技能包：技术形态 ===
def get_pattern(code):
    result = subprocess.run(
        ['python3', '__main__.py', 'pattern', code],
        capture_output=True, text=True, cwd='~/.openclaw/workspace/skills/stock-suite'.replace('~', '/Users/zhaoruicn')
    )
    return result.stdout

# === 3. 妙想数据：财务数据 ===
def get_mx_finance(code):
    import requests
    url = 'https://mkapi2.dfcfs.com/finskillshub/api/claw/query'
    headers = {
        'Content-Type': 'application/json',
        'apikey': 'mkt_zdTwvCWmIr9g4mHoM8sOsaK8M_ffrhinQPP-GAkhTNs'
    }
    data = {'toolQuery': f'{code} 市盈率 市净率 总市值'}
    
    resp = requests.post(url, json=data, headers=headers)
    items = resp.json().get('data', {}).get('dataTableDTOList', [])
    
    result = {}
    for item in items:
        table = item.get('table', {})
        name_map = item.get('nameMap', {})
        for k, v in table.items():
            col_name = name_map.get(k, k)
            if v and v[0]:
                result[col_name] = v[0]
    return result

# === 4. 妙想资讯：板块新闻 ===
def get_mx_news(keyword):
    import requests
    url = 'https://mkapi2.dfcfs.com/finskillshub/api/claw/news-search'
    headers = {
        'Content-Type': 'application/json',
        'apikey': 'mkt_zdTwvCWmIr9g4mHoM8sOsaK8M_ffrhinQPP-GAkhTNs'
    }
    data = {'query': keyword, 'pageSize': 3}
    
    resp = requests.post(url, json=data, headers=headers)
    items = resp.json().get('data', {}).get('data', [])
    
    news = []
    for item in items:
        news.append({
            'title': item.get('title', ''),
            'chunk': item.get('chunk', '')[:200]
        })
    return news

# === 完整分析流程 ===
def full_analysis(code, name, industry):
    print(f"\n{'='*50}")
    print(f"完整分析: {name} ({code})")
    print(f"{'='*50}")
    
    # 1. 股票类型（自有）
    print("\n【1. 股票类型】")
    stock_type = get_stock_type(code, name, industry)
    print(f"  类型: {stock_type.get('type', 'N/A')}")
    print(f"  分析框架: {stock_type.get('framework', 'N/A')}")
    print(f"  估值方法: {stock_type.get('method', 'N/A')}")
    
    # 2. 技术形态（自有）
    print("\n【2. 技术形态】")
    pattern = get_pattern(code)
    print(pattern)
    
    # 3. 财务数据（妙想）
    print("\n【3. 财务数据】")
    finance = get_mx_finance(code)
    for k, v in finance.items():
        print(f"  {k}: {v}")
    
    # 4. 板块资讯（妙想）
    print("\n【4. 板块资讯】")
    news = get_mx_news(industry)
    for n in news:
        print(f"  • {n['title']}")
    
    print(f"\n{'='*50}")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("用法: python3 full_analysis.py 代码 名称 行业")
        sys.exit(1)
    
    full_analysis(sys.argv[1], sys.argv[2], sys.argv[3])
