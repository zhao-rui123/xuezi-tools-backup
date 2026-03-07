#!/usr/bin/env python3
"""
雪球API测试 - 使用requests库
"""

import requests
import json

# 用户提供的完整Cookie
XUEQIU_COOKIE = 'cookiesu=841772842781365; device_id=d30532eeec1ab76c3eb0cbcd787c258d; Hm_lvt_1db88642e346389874251b5a1eded6e3=1772842783; HMACCOUNT=7B908FD9F2E01105; smidV2=2026030708194261da8f542cb226d9c43c02bc45a29cb9006c18151e1e42270; xq_is_login=1; u=3441676826; is_overseas=0; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1772844668; .thumbcache_f24b8bbe5a5934237bbc0eda20c1b6e7=kKcTLYJ/3EotJ3fm9sspILxHLejvEfAf2VTG/xJwR4+ErnolBbUQ8I8ewrgoQZNNuEeAl1Vod7C5Ci7y41cTkg%3D%3D; ssxmod_itna=1-YqUxc7DQoQwxnlDhx_xmq7Qjr3Tbq4DXDUqAQD2DIqGQGcD8OD0PIO3Dk7PEYYKDGuqKW3m0RqrqKmG5D/A7ieDZDGKQDqx0or0zDjOt4oQep4n4FA0db4vFFDZxPGtoGkGTyUEn/1l/704vDRGl9TorDB3DbqDy77Dz0reD4bdDt4DIDAYDDxDWfeGIDGYD72TbdcTDmb4FQxGyCnT4DkWN2eDgmDDBf_rQWoneDDXPFY3De4DwDYPNdp21=xqDAwhbEG4Nx0taDBdq4NxNZaCRTYcbcIMv14TOpPGuDG=TleGmCewO41aNTerRorbe=oY_0DihYDxo=D5oODK0hFB5r4YlBFBiiDx5gG5hC==xDi2wejIm7xrQ53oXShXZcXOY_QtrvlGelG4SeCQY32GsGqRGqGiGa/Ga9wsYm5lwp0Gm7Dd7hY/qq1ip7xxD; ssxmod_itna2=1-YqUxc7DQoQwxnlDhx_xmq7Qjr3Tbq4DXDUqAQD2DIqGQGcD8OD0PIO3Dk7PEYYKDGuqKW3m0RqrqKmieDAB=0DPrejQD03PoApg4CDBM4ij0AigrHeDx49Q9e75lGikuQn_v2qyW0NG4j9LNdmq5xOAXBAGjxhxNU7Yru4lio1Mhj4nrCBbKe1qv4wur4Yai/GxvqyCGig8uW=DNbvQuRRR2g0PWubdHkTuDW1LtBYKKPt/RP23T00M=TxLg5jTTb11BYTQLBRj6DwMDAgpY0K/6xNWZeTMuxwzTqDddcENUyFajwwGscTig/nq4AZ9Wy3uxEF4M4Pe7UCBM_c4wuW4Bk_uDji4YiZt9fU473mSCYPKFh7ixcWUWOHeWoTTwC7h_mLYTw4YP_q3doORhGCaxmTGji5PpFjWDv_F_WDpWzeWtwOWxqH_eQcR0bo77cIRg0ngdPqjYpqp_FYpb2wsASfi3a=GP4nwzD7dDtDb4Ayw0_FXB9iFhiOf_GCnumU_G8nmD_zYafSmhSa_HbGu4TSpEnR_2Whnf63nOi967MpGxx24vsmFrIqFI6lFLNW60WCA6QYuwgyvdFfPnzMxFfOseWfxzKx3ISvLQqjiFrz6kK96g40Y/_nEbWiYAb7q_Ie6Wndx3OG/UFeZORoE0203iAq4il_79WMpwaikbbGW4o5rRjANCGx0xViQm4qnaBAe08AI_YrFil_/Der04ehIAozG3j5/xhGtF_x7NjirCDW4dWDD'

def test_with_requests():
    """使用requests库测试"""
    print("="*60)
    print("使用requests库测试雪球API")
    print("="*60)
    
    # 解析cookie字符串为字典
    cookies = {}
    for item in XUEQIU_COOKIE.split(';'):
        if '=' in item:
            key, value = item.strip().split('=', 1)
            cookies[key] = value
    
    print(f"\nCookie keys: {list(cookies.keys())}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://xueqiu.com/',
    }
    
    # 测试单只股票
    symbol = "SZ002460"
    url = f"https://stock.xueqiu.com/v5/stock/quote.json?symbol={symbol}&extend=detail"
    
    print(f"\n请求URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=15)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 请求成功!")
            print(f"\n响应数据预览:")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:1500])
            
            if data.get('data') and data['data'].get('quote'):
                quote = data['data']['quote']
                print("\n" + "="*60)
                print("关键指标:")
                print("="*60)
                print(f"名称: {quote.get('name')}")
                print(f"当前价: {quote.get('current')}")
                print(f"涨跌幅: {quote.get('percent')}%")
                print(f"市盈率(TTM): {quote.get('pe_ttm')}")
                print(f"市净率: {quote.get('pb')}")
            return True
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

def test_without_cookie():
    """测试不带Cookie是否能访问"""
    print("\n" + "="*60)
    print("测试不带Cookie访问")
    print("="*60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': '*/*',
        'Referer': 'https://xueqiu.com/',
    }
    
    symbol = "SZ002460"
    url = f"https://stock.xueqiu.com/v5/stock/quote.json?symbol={symbol}&extend=detail"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 无需Cookie也能访问!")
            print(f"响应: {response.text[:500]}")
            return True
        else:
            print(f"❌ 需要Cookie认证")
            return False
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

if __name__ == "__main__":
    test_with_requests()
    test_without_cookie()
