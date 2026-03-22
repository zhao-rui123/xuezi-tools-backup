#!/usr/bin/env python3
"""
Tushare 数据接口封装
使用定制版API：http://lianghua.nanyangqiankun.top
"""
import os

TOKEN = os.getenv("TUSHARE_TOKEN", "d8d89556f8638c1d83426b6038fc04ea96b5da04841a07d99706f10027f3")

def get_pro():
    """获取pro接口"""
    import tushare as ts
    pro = ts.pro_api(TOKEN)
    pro._DataApi__token = TOKEN
    pro._DataApi__http_url = 'http://lianghua.nanyangqiankun.top'
    return pro

def get_stock_daily(ts_code: str, start_date: str, end_date: str):
    """获取股票日线数据"""
    pro = get_pro()
    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    return df

def get_stock_basic():
    """获取股票列表"""
    pro = get_pro()
    df = pro.stock_basic(list_status='L')
    return df

if __name__ == "__main__":
    # 测试
    print(get_stock_basic().head())
