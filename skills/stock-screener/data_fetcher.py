"""
数据获取模块 - 使用AkShare获取A股数据
"""
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta


def get_stock_list():
    """获取A股股票列表"""
    df = ak.stock_zh_a_spot_em()
    return df[['代码', '名称']].rename(columns={'代码': 'code', '名称': 'name'})


def get_monthly_kline(stock_code, start_date=None, end_date=None):
    """
    获取股票月线数据
    
    Args:
        stock_code: 股票代码，如 "000001"
        start_date: 开始日期，格式 "YYYYMMDD"
        end_date: 结束日期，格式 "YYYYMMDD"
    
    Returns:
        DataFrame with columns: date, open, high, low, close, volume
    """
    try:
        # 获取日线数据，然后转换为月线
        if start_date is None:
            # 获取足够的历史数据（3年月线约36根）
            start_date = (datetime.now() - timedelta(days=1100)).strftime('%Y%m%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        # 获取日线数据
        df = ak.stock_zh_a_hist(
            symbol=stock_code,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"  # 前复权
        )
        
        if df is None or len(df) < 30:
            return None
        
        # 转换为月线
        df['日期'] = pd.to_datetime(df['日期'])
        df.set_index('日期', inplace=True)
        
        monthly = df.resample('ME').agg({
            '开盘': 'first',
            '最高': 'max',
            '最低': 'min',
            '收盘': 'last',
            '成交量': 'sum'
        }).reset_index()
        
        monthly.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        monthly = monthly.dropna()
        
        return monthly
    except Exception as e:
        print(f"获取 {stock_code} 数据失败: {e}")
        return None


def get_stock_basic_info(stock_code):
    """获取股票基本信息"""
    try:
        df = ak.stock_individual_info_em(symbol=stock_code)
        return df
    except:
        return None