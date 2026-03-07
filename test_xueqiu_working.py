#!/usr/bin/env python3
"""
雪球API测试 - 使用完整curl参数
"""

import requests
import json

# 从curl命令提取的完整headers和cookies
HEADERS = {
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

COOKIES = {
    'cookiesu': '841772842781365',
    'device_id': 'd30532eeec1ab76c3eb0cbcd787c258d',
    'Hm_lvt_1db88642e346389874251b5a1eded6e3': '1772842783',
    'HMACCOUNT': '7B908FD9F2E01105',
    's': 'b0125gh5d8',
    'xq_a_token': '8661982e927e023bf957bbc24b6fe85211ed4348',
    'xqat': '8661982e927e023bf957bbc24b6fe85211ed4348',
    'xq_r_token': 'a48ce0f397b2c32744404a9e435a0ab6f0b9ba59',
    'xq_id_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjM0NDE2NzY4MjYsImlzcyI6InVjIiwiZXhwIjoxNzc1NDM0ODI0LCJjdG0iOjE3NzI4NDI4MjQ3MTQsImNpZCI6ImQ5ZDBuNEFadXAifQ.R8VRuz4gcsPrDv5jFU1c9WJYmulgC33sxR5Pkig9CRB-JZU4R--VkM9_mZjuKmx7g8SsJURq4UH5za6Qe9ey4RRtlKst1iL-2bKfX1_c5hxG9x6bHugx62zSlIJKYvqnPLwQ_rzgVH7daq11lfOoCya6LlOLZKffCgUiNzOlYSJTd9-m5Vf8ESs6kw1Nmh6lSEvbYym0VuvoN0YPiap9FlgLKUkuWLf9PJvo0Lfa6FoTAO6uMLTWYzUTSsTccTzF3xWUHb-ZBQY8kU72ZeDtXt_JzTYOov6ylbCOUSXPi4pY0_qZud_B71yFapuKheKbgMMZk2qPXZkbFgLHJJntXQ',
    'xq_is_login': '1',
    'u': '3441676826',
    'is_overseas': '0',
    'Hm_lpvt_1db88642e346389874251b5a1eded6e3': '1772846511',
}

# 自选股
WATCHLIST = [
    ("002738", "中矿资源", "锂矿/资源"),
    ("002460", "赣锋锂业", "锂电池/新能源"),
    ("000792", "盐湖股份", "盐湖提锂"),
    ("002240", "盛新锂能", "锂电池材料"),
    ("000725", "京东方A", "面板/显示"),
    ("600707", "彩虹股份", "面板/显示"),
    ("688981", "中芯国际", "半导体/芯片"),
]

def test_batch_quote():
    """测试批量行情API"""
    print("="*60)
    print("雪球API测试 - 使用完整curl参数")
    print("="*60)
    
    # 构建symbol列表
    symbols = []
    for code, _, _ in WATCHLIST:
        if code.startswith('6'):
            symbols.append(f'SH{code}')
        else:
            symbols.append(f'SZ{code}')
    
    symbol_str = ','.join(symbols)
    url = f"https://stock.xueqiu.com/v5/stock/batch/quote.json?symbol={symbol_str}&extend=detail&is_delay_hk=false"
    
    print(f"\n请求URL: {url[:80]}...")
    
    try:
        response = requests.get(url, headers=HEADERS, cookies=COOKIES, timeout=15)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 雪球API连接成功!")
            
            items = data.get('data', {}).get('items', [])
            print(f"\n获取到 {len(items)} 只股票数据:")
            print("-"*60)
            
            # 存储完整数据供分析
            full_data = []
            
            for item in items:
                quote = item.get('quote', {})
                stock_info = {
                    'name': quote.get('name'),
                    'code': quote.get('code'),
                    'current': quote.get('current'),
                    'percent': quote.get('percent'),
                    'chg': quote.get('chg'),
                    'pe_ttm': quote.get('pe_ttm'),
                    'pb': quote.get('pb'),
                    'market_cap': quote.get('market_cap'),
                    'float_market_capital': quote.get('float_market_capital'),
                    'turnover_rate': quote.get('turnover_rate'),
                    'volume_ratio': quote.get('volume_ratio'),
                    'amplitude': quote.get('amplitude'),
                    'high52w': quote.get('high52w'),
                    'low52w': quote.get('low52w'),
                    'amount': quote.get('amount'),
                    'volume': quote.get('volume'),
                    'open': quote.get('open'),
                    'high': quote.get('high'),
                    'low': quote.get('low'),
                }
                full_data.append(stock_info)
                
                print(f"{stock_info['name']} ({stock_info['code']})")
                print(f"  价格: {stock_info['current']} ({stock_info['percent']:+.2f}%)")
                print(f"  PE(TTM): {stock_info['pe_ttm']}, PB: {stock_info['pb']}")
                print(f"  市值: {stock_info['market_cap']/1e8:.2f}亿" if stock_info['market_cap'] else "  市值: N/A")
                print(f"  换手率: {stock_info['turnover_rate']}%, 量比: {stock_info['volume_ratio']}")
                print()
            
            # 保存一份完整数据
            with open('/Users/zhaoruicn/.openclaw/workspace/xueqiu_sample_data.json', 'w', encoding='utf-8') as f:
                json.dump(full_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 完整数据已保存到 xueqiu_sample_data.json")
            
            return True, full_data
        else:
            print(f"❌ 请求失败: {response.text[:200]}")
            return False, None
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False, None

if __name__ == "__main__":
    success, data = test_batch_quote()
    
    print("\n" + "="*60)
    if success:
        print("✅ 雪球API测试通过! 可以开始整合到股票分析系统")
        print(f"\n雪球独有指标:")
        print("  - 市盈率(TTM) - PE_TTM")
        print("  - 市净率 - PB")
        print("  - 总市值/流通市值")
        print("  - 换手率")
        print("  - 量比")
        print("  - 振幅")
        print("  - 52周最高/最低")
    else:
        print("❌ 测试失败")
    print("="*60)
