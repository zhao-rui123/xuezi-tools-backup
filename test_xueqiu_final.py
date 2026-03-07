#!/usr/bin/env python3
"""
雪球API测试 - 修正URL格式
"""

import urllib.request
import json

# 用户提供的完整Cookie
XUEQIU_COOKIE = 'cookiesu=841772842781365; device_id=d30532eeec1ab76c3eb0cbcd787c258d; Hm_lvt_1db88642e346389874251b5a1eded6e3=1772842783; HMACCOUNT=7B908FD9F2E01105; smidV2=2026030708194261da8f542cb226d9c43c02bc45a29cb9006c18151e1e42270; xq_is_login=1; u=3441676826; is_overseas=0; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1772844668; .thumbcache_f24b8bbe5a5934237bbc0eda20c1b6e7=kKcTLYJ/3EotJ3fm9sspILxHLejvEfAf2VTG/xJwR4+ErnolBbUQ8I8ewrgoQZNNuEeAl1Vod7C5Ci7y41cTkg%3D%3D; ssxmod_itna=1-YqUxc7DQoQwxnlDhx_xmq7Qjr3Tbq4DXDUqAQD2DIqGQGcD8OD0PIO3Dk7PEYYKDGuqKW3m0RqrqKmG5D/A7ieDZDGKQDqx0or0zDjOt4oQep4n4FA0db4vFFDZxPGtoGkGTyUEn/1l/704vDRGl9TorDB3DbqDy77Dz0reD4bdDt4DIDAYDDxDWfeGIDGYD72TbdcTDmb4FQxGyCnT4DkWN2eDgmDDBf_rQWoneDDXPFY3De4DwDYPNdp21=xqDAwhbEG4Nx0taDBdq4NxNZaCRTYcbcIMv14TOpPGuDG=TleGmCewO41aNTerRorbe=oY_0DihYDxo=D5oODK0hFB5r4YlBFBiiDx5gG5hC==xDi2wejIm7xrQ53oXShXZcXOY_QtrvlGelG4SeCQY32GsGqRGqGiGa/Ga9wsYm5lwp0Gm7Dd7hY/qq1ip7xxD; ssxmod_itna2=1-YqUxc7DQoQwxnlDhx_xmq7Qjr3Tbq4DXDUqAQD2DIqGQGcD8OD0PIO3Dk7PEYYKDGuqKW3m0RqrqKmieDAB=0DPrejQD03PoApg4CDBM4ij0AigrHeDx49Q9e75lGikuQn_v2qyW0NG4j9LNdmq5xOAXBAGjxhxNU7Yru4lio1Mhj4nrCBbKe1qv4wur4Yai/GxvqyCGig8uW=DNbvQuRRR2g0PWubdHkTuDW1LtBYKKPt/RP23T00M=TxLg5jTTb11BYTQLBRj6DwMDAgpY0K/6xNWZeTMuxwzTqDddcENUyFajwwGscTig/nq4AZ9Wy3uxEF4M4Pe7UCBM_c4wuW4Bk_uDji4YiZt9fU473mSCYPKFh7ixcWUWOHeWoTTwC7h_mLYTw4YP_q3doORhGCaxmTGji5PpFjWDv_F_WDpWzeWtwOWxqH_eQcR0bo77cIRg0ngdPqjYpqp_FYpb2wsASfi3a=GP4nwzD7dDtDb4Ayw0_FXB9iFhiOf_GCnumU_G8nmD_zYafSmhSa_HbGu4TSpEnR_2Whnf63nOi967MpGxx24vsmFrIqFI6lFLNW60WCA6QYuwgyvdFfPnzMxFfOseWfxzKx3ISvLQqjiFrz6kK96g40Y/_nEbWiYAb7q_Ie6Wndx3OG/UFeZORoE0203iAq4il_79WMpwaikbbGW4o5rRjANCGx0xViQm4qnaBAe08AI_YrFil_/Der04ehIAozG3j5/xhGtF_x7NjirCDW4dWDD'

# 自选股列表
WATCHLIST = [
    ("002460", "赣锋锂业", "锂电池/新能源"),
    ("002738", "中矿资源", "锂矿/资源"),
]

def get_headers():
    """获取请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://xueqiu.com/',
        'Cookie': XUEQIU_COOKIE,
    }

def test_single_quote():
    """测试单只股票行情"""
    print("="*60)
    print("测试雪球单只股票行情 API")
    print("="*60)
    
    # 赣锋锂业
    symbol = "SZ002460"
    url = f"https://stock.xueqiu.com/v5/stock/quote.json?symbol={symbol}&extend=detail"
    
    print(f"\n请求URL: {url}")
    
    try:
        req = urllib.request.Request(url, headers=get_headers())
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read().decode('utf-8'))
        
        print("✅ 请求成功!")
        print(f"\n响应数据:")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
        
        # 提取关键字段
        if data.get('data') and data['data'].get('quote'):
            quote = data['data']['quote']
            print("\n" + "="*60)
            print("关键指标:")
            print("="*60)
            print(f"名称: {quote.get('name')}")
            print(f"代码: {quote.get('code')}")
            print(f"当前价: {quote.get('current')}")
            print(f"涨跌幅: {quote.get('percent')}%")
            print(f"市盈率(TTM): {quote.get('pe_ttm')}")
            print(f"市净率: {quote.get('pb')}")
            print(f"总市值: {quote.get('market_cap', 0)/1e8:.2f}亿")
            print(f"换手率: {quote.get('turnover_rate')}%")
            print(f"成交额: {quote.get('amount', 0)/1e8:.2f}亿")
            print(f"振幅: {quote.get('amplitude')}%")
            print(f"量比: {quote.get('volume_ratio')}")
            print(f"52周最高: {quote.get('high52w')}")
            print(f"52周最低: {quote.get('low52w')}")
            
        return True
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_batch_quote():
    """测试批量行情"""
    print("\n" + "="*60)
    print("测试雪球批量行情 API")
    print("="*60)
    
    symbols = ["SZ002460", "SZ002738", "SH600707"]
    symbol_str = ','.join(symbols)
    url = f"https://stock.xueqiu.com/v5/stock/batch/quote.json?symbol={symbol_str}"
    
    print(f"\n请求URL: {url}")
    
    try:
        req = urllib.request.Request(url, headers=get_headers())
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read().decode('utf-8'))
        
        print("✅ 批量请求成功!")
        
        if data.get('data') and data['data'].get('items'):
            items = data['data']['items']
            print(f"\n获取到 {len(items)} 只股票数据:")
            for item in items:
                quote = item.get('quote', {})
                print(f"  - {quote.get('name')}({quote.get('code')}): {quote.get('current')} ({quote.get('percent')}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ 批量请求失败: {e}")
        return False

if __name__ == "__main__":
    success1 = test_single_quote()
    success2 = test_batch_quote()
    
    print("\n" + "="*60)
    if success1 and success2:
        print("✅ 雪球API测试全部通过!")
        print("可以开始整合到股票分析系统了")
    else:
        print("❌ 部分API测试失败")
    print("="*60)
