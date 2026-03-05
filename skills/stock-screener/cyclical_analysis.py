"""
周期股预期差分析模块
"""
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta


def get_pe_history(stock_code, years=5):
    """
    获取历史PE数据
    
    Returns:
        dict: PE统计信息
    """
    try:
        # 获取历史估值数据
        df = ak.stock_a_pe(symbol=stock_code)
        
        if df is None or df.empty:
            return None
        
        # 计算PE分位点
        pe_values = df['滚动市盈率'].dropna()
        
        if len(pe_values) < 100:
            return None
        
        current_pe = pe_values.iloc[0]
        pe_min = pe_values.min()
        pe_max = pe_values.max()
        pe_median = pe_values.median()
        
        # 计算当前PE在历史中的分位点
        pe_percentile = (pe_values < current_pe).mean() * 100
        
        return {
            'current_pe': round(current_pe, 2),
            'pe_min': round(pe_min, 2),
            'pe_max': round(pe_max, 2),
            'pe_median': round(pe_median, 2),
            'pe_percentile': round(pe_percentile, 2),
            'is_low_pe': pe_percentile < 30  # PE分位点<30%认为是低位
        }
    except Exception as e:
        print(f"获取 {stock_code} PE历史失败: {e}")
        return None


def get_price_decline_from_high(stock_code, months=24):
    """
    计算股价从高点跌幅
    
    Returns:
        dict: 跌幅信息
    """
    try:
        # 获取历史数据
        start_date = (datetime.now() - timedelta(days=months*30)).strftime('%Y%m%d')
        end_date = datetime.now().strftime('%Y%m%d')
        
        df = ak.stock_zh_a_hist(
            symbol=stock_code,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"
        )
        
        if df is None or df.empty:
            return None
        
        current_price = df['收盘'].iloc[-1]
        high_price = df['最高'].max()
        
        if high_price == 0:
            return None
        
        decline_pct = (high_price - current_price) / high_price * 100
        
        return {
            'current_price': round(current_price, 2),
            'high_price': round(high_price, 2),
            'decline_pct': round(decline_pct, 2),
            'is_deep_decline': decline_pct > 50  # 跌幅>50%认为是深度调整
        }
    except Exception as e:
        print(f"获取 {stock_code} 价格跌幅失败: {e}")
        return None


def get_profit_forecast(stock_code):
    """
    获取盈利预测数据（市场预期）
    
    Returns:
        dict: 盈利预测信息
    """
    try:
        df = ak.stock_profit_forecast_em(symbol=stock_code)
        
        if df is None or df.empty:
            return None
        
        latest = df.iloc[0]
        
        return {
            'forecast_eps': latest.get('预测每股收益'),
            'forecast_profit': latest.get('预测净利润'),
            'forecast_pe': latest.get('预测市盈率'),
            'institution_count': latest.get('机构数'),
            'rating': latest.get('综合评级')
        }
    except:
        return None


def analyze_expectation_gap(stock_code, stock_name):
    """
    分析周期股预期差
    
    Returns:
        dict: 预期差分析结果
    """
    print(f"分析 {stock_code} {stock_name} 预期差...")
    
    result = {
        'code': stock_code,
        'name': stock_name,
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'is_cyclical_opportunity': False,
        'score': 0  # 预期差评分 0-100
    }
    
    # 1. PE历史位置
    pe_info = get_pe_history(stock_code)
    if pe_info:
        result['pe_analysis'] = pe_info
        if pe_info['is_low_pe']:
            result['score'] += 30
            result['is_cyclical_opportunity'] = True
    
    # 2. 股价跌幅
    price_info = get_price_decline_from_high(stock_code)
    if price_info:
        result['price_analysis'] = price_info
        if price_info['is_deep_decline']:
            result['score'] += 30
            result['is_cyclical_opportunity'] = True
    
    # 3. 盈利预测
    forecast = get_profit_forecast(stock_code)
    if forecast:
        result['profit_forecast'] = forecast
    
    # 综合判断
    if result['score'] >= 60:
        result['opportunity_level'] = '高'
        result['suggestion'] = '典型的周期股预期差机会，建议深入研究基本面'
    elif result['score'] >= 30:
        result['opportunity_level'] = '中'
        result['suggestion'] = '存在一定的预期差，可关注'
    else:
        result['opportunity_level'] = '低'
        result['suggestion'] = '预期差不明显'
    
    return result


def screen_cyclical_stocks(stock_list, min_score=30):
    """
    筛选周期股预期差机会
    
    Args:
        stock_list: 股票列表
        min_score: 最低评分
    
    Returns:
        list: 符合条件的周期股
    """
    results = []
    
    for _, row in stock_list.iterrows():
        code = row['code']
        name = row['name']
        
        analysis = analyze_expectation_gap(code, name)
        
        if analysis['score'] >= min_score:
            results.append(analysis)
            print(f"✓ {code} {name} - 预期差评分: {analysis['score']}")
    
    return results