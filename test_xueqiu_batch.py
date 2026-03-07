#!/usr/bin/env python3
"""
雪球API测试 - 使用用户提供的URL格式
"""

import requests
import json

# 用户提供的完整Cookie
XUEQIU_COOKIE = 'cookiesu=841772842781365; device_id=d30532eeec1ab76c3eb0cbcd787c258d; Hm_lvt_1db88642e346389874251b5a1eded6e3=1772842783; HMACCOUNT=7B908FD9F2E01105; smidV2=2026030708194261da8f542cb226d9c43c02bc45a29cb9006c18151e1e42270; xq_is_login=1; u=3441676826; is_overseas=0; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1772844668; .thumbcache_f24b8bbe5a5934237bbc0eda20c1b6e7=kKcTLYJ/3EotJ3fm9sspILxHLejvEfAf2VTG/xJwR4+ErnolBbUQ8I8ewrgoQZNNuEeAl1Vod7C5Ci7y41cTkg%3D%3D; ssxmod_itna=1-YqUxc7DQoQwxnlDhx_xmq7Qjr3Tbq4DXDUqAQD2DIqGQGcD8OD0PIO3Dk7PEYYKDGuqKW3m0RqrqKmG5D/A7ieDZDGKQDqx0or0zDjOt4oQep4n4FA0db4vFFDZxPGtoGkGTyUEn/1l/704vDRGl9TorDB3DbqDy77Dz0reD4bdDt4DIDAYDDxDWfeGIDGYD72TbdcTDmb4FQxGyCnT4DkWN2eDgmDDBf_rQWoneDDXPFY3De4DwDYPNdp21=xqDAwhbEG4Nx0taDBdq4NxNZaCRTYcbcIMv14TOpPGuDG=TleGmCewO41aNTerRorbe=oY_0DihYDxo=D5oODK0hFB5r4YlBFBiiDx5gG5hC==xDi2wejIm7xrQ53oXShXZcXOY_QtrvlGelG4SeCQY32GsGqRGqGiGa/Ga9wsYm5lwp0Gm7Dd7hY/qq1ip7xxD; ssxmod_itna2=1-YqUxc7DQoQwxnlDhx_xmq7Qjr3Tbq4DXDUqAQD2DIqGQGcD8OD0PIO3Dk7PEYYKDGuqKW3m0RqrqKmieDAB=0DPrejQD03PoApg4CDBM4ij0AigrHeDx49Q9e75lGikuQn_v2qyW0NG4j9LNdmq5xOAXBAGjxhxNU7Yru4lio1Mhj4nrCBbKe1qv4wur4Yai/GxvqyCGig8uW=DNbvQuRRR2g0PWubdHkTuDW1LtBYKKPt/RP23T00M=TxLg5jTTb11BYTQLBRj6DwMDAgpY0K/6xNWZeTMuxwzTqDddcENUyFajwwGscTig/nq4AZ9Wy3uxEF4M4Pe7UCBM_c4wuW4Bk_uDji4YiZt9fU473mSCYPKFh7ixcWUWOHeWoTTwC7h_mLYTw4YP_q3doORhGCaxmTGji5PpFjWDv_F_WDpWzeWtwOWxqH_eQcR0bo77cIRg0ngdPqjYpqp_FYpb2wsASfi3a=GP4nwzD7dDtDb4Ayw0_FXB9iFhiOf_GCnumU_G8nmD_zYafSmhSa_HbGu4TSpEnR_2Whnf63nOi967MpGxx24vsmFrIqFI6lFLNW60WCA6QYuwgyvdFfPnzMxFfOseWfxzKx3ISvLQqjiFrz6kK96g40Y/_nEbWiYAb7q_Ie6Wndx3OG/UFeZORoE0203iAq4il_79WMpwaikbbGW4o5rRjANCGx0xViQm4qnaBAe08AI_YrFil_/Der04ehIAozG3j5/xhGtF_x7NjirCDW4dWDD'

# 解析cookie字符串为字典
def parse_cookie(cookie_str):
    cookies = {}
    for item in cookie_str.split(';'):
        if '=' in item:
            key, value = item.strip().split('=', 1)
            cookies[key] = value
    return cookies

# 自选股
WATCHLIST = [
    ("002738", "中矿资源"),
    ("002460", "赣锋锂业"),
    ("000792", "盐湖股份"),
    ("002240", "盛新锂能"),
    ("000725", "京东方A"),
    ("600707", "彩虹股份"),
    ("688981", "中芯国际"),
]

def test_batch_quote():
    """测试批量行情API"""
    print("="*60)
    print("雪球批量行情API测试")
    print("="*60)
    
    # 构建symbol列表
    symbols = []
    for code, _ in WATCHLIST:
        if code.startswith('6'):
            symbols.append(f'SH{code}')
        else:
            symbols.append(f'SZ{code}')
    
    symbol_str = ','.join(symbols)
    url = f"https://stock.xueqiu.com/v5/stock/batch/quote.json?symbol={symbol_str}&extend=detail"
    
    print(f"\n请求URL: {url[:80]}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://xueqiu.com/',
    }
    
    cookies = parse_cookie(XUEQIU_COOKIE)
    
    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=15)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功!")
            
            items = data.get('data', {}).get('items', [])
            print(f"\n获取到 {len(items)} 只股票数据:")
            print("-"*60)
            
            for item in items:
                quote = item.get('quote', {})
                name = quote.get('name', 'N/A')
                code = quote.get('code', 'N/A')
                current = quote.get('current', 0)
                percent = quote.get('percent', 0)
                pe_ttm = quote.get('pe_ttm', 'N/A')
                pb = quote.get('pb', 'N/A')
                market_cap = quote.get('market_cap', 0)
                
                print(f"{name} ({code})")
                print(f"  价格: {current} ({percent:+.2f}%)")
                print(f"  PE(TTM): {pe_ttm}, PB: {pb}")
                print(f"  市值: {market_cap/1e8:.2f}亿")
                print()
            
            return True
        else:
            print(f"❌ 失败: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

if __name__ == "__main__":
    test_batch_quote()
