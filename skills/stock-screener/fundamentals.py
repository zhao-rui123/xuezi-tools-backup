"""
基本面分析模块 - 获取行业、研报、财报数据
"""
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta


def get_industry_info(stock_code):
    """
    获取股票所属行业信息
    
    Returns:
        dict: 行业分类、行业排名等信息
    """
    try:
        # 获取行业分类
        df = ak.stock_industry_category_em()
        stock_info = df[df['代码'] == stock_code]
        
        if stock_info.empty:
            return None
        
        return {
            'industry_name': stock_info['行业'].values[0],
            'industry_code': stock_info['行业代码'].values[0] if '行业代码' in stock_info.columns else None
        }
    except Exception as e:
        print(f"获取 {stock_code} 行业信息失败: {e}")
        return None


def get_industry_stocks(industry_name):
    """
    获取同行业股票列表
    
    Returns:
        DataFrame: 同行业股票
    """
    try:
        df = ak.stock_industry_category_em()
        return df[df['行业'] == industry_name][['代码', '名称']]
    except:
        return None


def get_financial_summary(stock_code):
    """
    获取财务指标摘要
    
    Returns:
        dict: 主要财务指标
    """
    try:
        # 获取主要财务指标
        df = ak.stock_financial_analysis_indicator(symbol=stock_code)
        
        if df is None or df.empty:
            return None
        
        # 取最新一期数据
        latest = df.iloc[0]
        
        return {
            'roe': latest.get('净资产收益率(%)'),
            'roa': latest.get('总资产报酬率(%)'),
            'gross_margin': latest.get('销售毛利率(%)'),
            'net_margin': latest.get('销售净利率(%)'),
            'debt_ratio': latest.get('资产负债率(%)'),
            'eps': latest.get('每股收益(元)'),
            'revenue_growth': latest.get('营业收入同比增长率(%)'),
            'profit_growth': latest.get('净利润同比增长率(%)'),
            'report_date': latest.get('报告期')
        }
    except Exception as e:
        print(f"获取 {stock_code} 财务数据失败: {e}")
        return None


def get_valuation_metrics(stock_code):
    """
    获取估值指标
    
    Returns:
        dict: PE、PB等估值指标
    """
    try:
        # 获取实时估值数据
        df = ak.stock_a_pe(symbol=stock_code)
        
        if df is None or df.empty:
            return None
        
        latest = df.iloc[0]
        
        return {
            'pe_ttm': latest.get('滚动市盈率'),
            'pb': latest.get('市净率'),
            'ps': latest.get('市销率'),
            'pcf': latest.get('市现率'),
            'market_cap': latest.get('总市值'),
            'date': latest.get('日期')
        }
    except Exception as e:
        print(f"获取 {stock_code} 估值数据失败: {e}")
        return None


def get_research_reports(stock_code, limit=5):
    """
    获取券商研报摘要
    
    Args:
        limit: 获取最近N篇研报
    
    Returns:
        list: 研报列表
    """
    try:
        # 获取研报数据
        df = ak.stock_research_report_em(symbol=stock_code)
        
        if df is None or df.empty:
            return []
        
        # 取最近N篇
        recent = df.head(limit)
        
        reports = []
        for _, row in recent.iterrows():
            reports.append({
                'date': row.get('日期'),
                'title': row.get('报告标题'),
                'institution': row.get('机构'),
                'author': row.get('研究员'),
                'rating': row.get('评级'),
                'target_price': row.get('目标价'),
                'summary': row.get('摘要', '')[:200]  # 截取前200字
            })
        
        return reports
    except Exception as e:
        print(f"获取 {stock_code} 研报失败: {e}")
        return []


def get_company_profile(stock_code):
    """
    获取公司概况
    
    Returns:
        dict: 公司基本信息
    """
    try:
        df = ak.stock_individual_info_em(symbol=stock_code)
        
        if df is None or df.empty:
            return None
        
        # 转换为字典
        info = {}
        for _, row in df.iterrows():
            info[row['item']] = row['value']
        
        return {
            'company_name': info.get('股票简称'),
            'total_shares': info.get('总股本'),
            'float_shares': info.get('流通股'),
            'industry': info.get('行业'),
            'listing_date': info.get('上市时间'),
            'company_profile': info.get('公司简介', '')[:500]  # 截取前500字
        }
    except Exception as e:
        print(f"获取 {stock_code} 公司概况失败: {e}")
        return None


def analyze_stock_fundamentals(stock_code):
    """
    综合分析股票基本面
    
    Returns:
        dict: 完整的基本面分析
    """
    print(f"正在分析 {stock_code} 基本面...")
    
    result = {
        'code': stock_code,
        'analysis_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    # 公司概况
    profile = get_company_profile(stock_code)
    if profile:
        result['profile'] = profile
    
    # 行业信息
    industry = get_industry_info(stock_code)
    if industry:
        result['industry'] = industry
    
    # 财务指标
    financial = get_financial_summary(stock_code)
    if financial:
        result['financial'] = financial
    
    # 估值指标
    valuation = get_valuation_metrics(stock_code)
    if valuation:
        result['valuation'] = valuation
    
    # 研报
    reports = get_research_reports(stock_code)
    if reports:
        result['research_reports'] = reports
    
    return result