#!/usr/bin/env python3
"""
雪球API测试 - 使用用户提供的Cookie
"""

import urllib.request
import json

# 用户提供的完整Cookie
XUEQIU_COOKIE = 'cookiesu=841772842781365; device_id=d30532eeec1ab76c3eb0cbcd787c258d; Hm_lvt_1db88642e346389874251b5a1eded6e3=1772842783; HMACCOUNT=7B908FD9F2E01105; smidV2=2026030708194261da8f542cb226d9c43c02bc45a29cb9006c18151e1e42270; xq_is_login=1; u=3441676826; is_overseas=0; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1772844668; .thumbcache_f24b8bbe5a5934237bbc0eda20c1b6e7=kKcTLYJ/3EotJ3fm9sspILxHLejvEfAf2VTG/xJwR4+ErnolBbUQ8I8ewrgoQZNNuEeAl1Vod7C5Ci7y41cTkg%3D%3D; ssxmod_itna=1-YqUxc7DQoQwxnlDhx_xmq7Qjr3Tbq4DXDUqAQD2DIqGQGcD8OD0PIO3Dk7PEYYKDGuqKW3m0RqrqKmG5D/A7ieDZDGKQDqx0or0zDjOt4oQep4n4FA0db4vFFDZxPGtoGkGTyUEn/1l/704vDRGl9TorDB3DbqDy77Dz0reD4bdDt4DIDAYDDxDWfeGIDGYD72TbdcTDmb4FQxGyCnT4DkWN2eDgmDDBf_rQWoneDDXPFY3De4DwDYPNdp21=xqDAwhbEG4Nx0taDBdq4NxNZaCRTYcbcIMv14TOpPGuDG=TleGmCewO41aNTerRorbe=oY_0DihYDxo=D5oODK0hFB5r4YlBFBiiDx5gG5hC==xDi2wejIm7xrQ53oXShXZcXOY_QtrvlGelG4SeCQY32GsGqRGqGiGa/Ga9wsYm5lwp0Gm7Dd7hY/qq1ip7xxD; ssxmod_itna2=1-YqUxc7DQoQwxnlDhx_xmq7Qjr3Tbq4DXDUqAQD2DIqGQGcD8OD0PIO3Dk7PEYYKDGuqKW3m0RqrqKmieDAB=0DPrejQD03PoApg4CDBM4ij0AigrHeDx49Q9e75lGikuQn_v2qyW0NG4j9LNdmq5xOAXBAGjxhxNU7Yru4lio1Mhj4nrCBbKe1qv4wur4Yai/GxvqyCGig8uW=DNbvQuRRR2g0PWubdHkTuDW1LtBYKKPt/RP23T00M=TxLg5jTTb11BYTQLBRj6DwMDAgpY0K/6xNWZeTMuxwzTqDddcENUyFajwwGscTig/nq4AZ9Wy3uxEF4M4Pe7UCBM_c4wuW4Bk_uDji4YiZt9fU473mSCYPKFh7ixcWUWOHeWoTTwC7h_mLYTw4YP_q3doORhGCaxmTGji5PpFjWDv_F_WDpWzeWtwOWxqH_eQcR0bo77cIRg0ngdPqjYpqp_FYpb2wsASfi3a=GP4nwzD7dDtDb4Ayw0_FXB9iFhiOf_GCnumU_G8nmD_zYafSmhSa_HbGu4TSpEnR_2Whnf63nOi967MpGxx24vsmFrIqFI6lFLNW60WCA6QYuwgyvdFfPnzMxFfOseWfxzKx3ISvLQqjiFrz6kK96g40Y/_nEbWiYAb7q_Ie6Wndx3OG/UFeZORoE0203iAq4il_79WMpwaikbbGW4o5rRjANCGx0xViQm4qnaBAe08AI_YrFil_/Der04ehIAozG3j5/xhGtF_x7NjirCDW4dWDD'

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

def get_headers():
    """获取请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://xueqiu.com/',
        'Cookie': XUEQIU_COOKIE,
    }

def fetch_xueqiu_realtime(codes):
    """获取雪球实时行情数据"""
    symbols = []
    for code in codes:
        if code.startswith('6'):
            symbols.append(f'SH{code}')
        else:
            symbols.append(f'SZ{code}')
    
    symbol_str = ','.join(symbols)
    url = f"https://stock.xueqiu.com/v5/stock/batch/quote.json?symbol={symbol_str}"
    
    try:
        req = urllib.request.Request(url, headers=get_headers())
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read().decode('utf-8'))
        return data
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def fetch_xueqiu_detail(symbol):
    """获取雪球个股详细信息"""
    url = f"https://stock.xueqiu.com/v5/stock/quote.json?symbol={symbol}&extend=detail"
    
    try:
        req = urllib.request.Request(url, headers=get_headers())
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read().decode('utf-8'))
        return data
    except Exception as e:
        print(f"❌ 详情请求失败: {e}")
        return None

def fetch_xueqiu_cashflow(symbol):
    """获取雪球资金流向"""
    url = f"https://stock.xueqiu.com/v5/stock/f10/cn/skhfst.json?symbol={symbol}"
    
    try:
        req = urllib.request.Request(url, headers=get_headers())
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read().decode('utf-8'))
        return data
    except Exception as e:
        print(f"❌ 资金流向请求失败: {e}")
        return None

def fetch_xueqiu_rating(symbol):
    """获取雪球机构评级"""
    url = f"https://stock.xueqiu.com/v5/stock/f10/cn/skrating.json?symbol={symbol}"
    
    try:
        req = urllib.request.Request(url, headers=get_headers())
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read().decode('utf-8'))
        return data
    except Exception as e:
        print(f"❌ 评级请求失败: {e}")
        return None

def test_xueqiu_apis():
    """测试雪球各API接口"""
    print("="*60)
    print("雪球API测试 - 使用用户Cookie")
    print("="*60)
    
    # 测试1: 批量实时行情
    print("\n[测试1] 批量实时行情")
    codes = [s[0] for s in WATCHLIST]
    realtime_data = fetch_xueqiu_realtime(codes)
    
    if realtime_data and realtime_data.get('data'):
        print("✅ 实时行情API可用")
        items = realtime_data['data'].get('items', [])
        print(f"   获取到 {len(items)} 只股票数据")
        
        if items:
            print("\n   示例数据 (赣锋锂业 002460):")
            for item in items:
                quote = item.get('quote', {})
                if quote.get('code') == 'SZ002460':
                    print(f"     名称: {quote.get('name')}")
                    print(f"     当前价: {quote.get('current')}")
                    print(f"     涨跌额: {quote.get('chg')}")
                    print(f"     涨跌幅: {quote.get('percent')}%")
                    print(f"     市盈率(TTM): {quote.get('pe_ttm')}")
                    print(f"     市净率: {quote.get('pb')}")
                    print(f"     总市值: {quote.get('market_cap', 0)/1e8:.2f}亿")
                    print(f"     流通市值: {quote.get('float_market_capital', 0)/1e8:.2f}亿")
                    print(f"     换手率: {quote.get('turnover_rate')}%")
                    print(f"     振幅: {quote.get('amplitude')}%")
                    print(f"     量比: {quote.get('volume_ratio')}")
                    print(f"     52周最高: {quote.get('high52w')}")
                    print(f"     52周最低: {quote.get('low52w')}")
                    break
    else:
        print("❌ 实时行情API不可用")
        if realtime_data:
            print(f"   错误: {realtime_data}")
    
    # 测试2: 个股详细信息
    print("\n[测试2] 个股详细信息")
    test_symbol = "SZ002460"  # 赣锋锂业
    detail = fetch_xueqiu_detail(test_symbol)
    if detail and detail.get('data'):
        print(f"✅ 详情API可用 - {test_symbol}")
        data = detail['data']
        quote = data.get('quote', {})
        print(f"   股息率: {quote.get('dividend_yield')}%")
        print(f"   总股本: {quote.get('total_shares', 0)/1e8:.2f}亿")
        print(f"   流通股: {quote.get('float_shares', 0)/1e8:.2f}亿")
    else:
        print("❌ 详情API不可用")
    
    # 测试3: 资金流向
    print("\n[测试3] 资金流向")
    cashflow = fetch_xueqiu_cashflow(test_symbol)
    if cashflow and cashflow.get('data'):
        print(f"✅ 资金流向API可用 - {test_symbol}")
        print(f"   数据结构: {list(cashflow['data'].keys())[:5]}")
    else:
        print("❌ 资金流向API不可用")
    
    # 测试4: 机构评级
    print("\n[测试4] 机构评级")
    rating = fetch_xueqiu_rating(test_symbol)
    if rating and rating.get('data'):
        print(f"✅ 评级API可用 - {test_symbol}")
        rating_data = rating['data']
        print(f"   数据结构: {list(rating_data.keys())}")
        # 打印评级详情
        if 'items' in rating_data:
            print(f"   评级条目数: {len(rating_data['items'])}")
    else:
        print("❌ 评级API不可用")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    test_xueqiu_apis()
