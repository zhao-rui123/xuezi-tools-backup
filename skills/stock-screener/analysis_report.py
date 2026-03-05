"""
综合分析报告生成模块
"""
import json
from datetime import datetime
from fundamentals import analyze_stock_fundamentals


def generate_fundamental_summary(stock_code, stock_name, analysis_data):
    """
    生成基本面分析摘要
    
    Returns:
        str: 分析摘要文本
    """
    summary = []
    
    # 公司概况
    profile = analysis_data.get('profile', {})
    if profile:
        summary.append(f"## {stock_name}({stock_code}) 基本面分析")
        summary.append(f"\n**公司概况：**")
        summary.append(f"- 所属行业：{profile.get('industry', 'N/A')}")
        summary.append(f"- 上市时间：{profile.get('listing_date', 'N/A')}")
        summary.append(f"- 公司简介：{profile.get('company_profile', 'N/A')[:200]}...")
    
    # 财务指标
    financial = analysis_data.get('financial', {})
    if financial:
        summary.append(f"\n**财务指标（{financial.get('report_date', '最新')}）：**")
        summary.append(f"- ROE：{financial.get('roe', 'N/A')}%")
        summary.append(f"- 毛利率：{financial.get('gross_margin', 'N/A')}%")
        summary.append(f"- 净利率：{financial.get('net_margin', 'N/A')}%")
        summary.append(f"- 营收增长：{financial.get('revenue_growth', 'N/A')}%")
        summary.append(f"- 利润增长：{financial.get('profit_growth', 'N/A')}%")
    
    # 估值指标
    valuation = analysis_data.get('valuation', {})
    if valuation:
        summary.append(f"\n**估值指标：**")
        summary.append(f"- PE(TTM)：{valuation.get('pe_ttm', 'N/A')}")
        summary.append(f"- PB：{valuation.get('pb', 'N/A')}")
        summary.append(f"- 总市值：{valuation.get('market_cap', 'N/A')}")
    
    # 研报摘要
    reports = analysis_data.get('research_reports', [])
    if reports:
        summary.append(f"\n**最新研报（{len(reports)}篇）：**")
        for i, r in enumerate(reports[:3], 1):
            summary.append(f"{i}. [{r.get('date', 'N/A')}] {r.get('institution', 'N/A')} - {r.get('rating', 'N/A')}")
            summary.append(f"   目标价：{r.get('target_price', 'N/A')} | {r.get('summary', '')[:100]}...")
    
    return '\n'.join(summary)


def generate_investment_recommendation(screening_result, fundamental_data):
    """
    生成投资建议
    
    Returns:
        dict: 投资建议
    """
    recommendation = {
        'code': screening_result['code'],
        'name': screening_result['name'],
        'screen_date': screening_result['screen_date'],
        'technical_score': 0,
        'fundamental_score': 0,
        'overall_rating': '',
        'suggestion': ''
    }
    
    # 技术面评分（基于筛选条件）
    signals = screening_result.get('signals', {})
    tech_score = sum([
        25 if signals.get('macd_golden_cross') else 0,
        25 if signals.get('kdj_golden_cross') else 0,
        25 if signals.get('ma_alignment') else 0,
        25 if signals.get('volume_increase') else 0
    ])
    recommendation['technical_score'] = tech_score
    
    # 基本面评分
    fund_score = 0
    financial = fundamental_data.get('financial', {})
    valuation = fundamental_data.get('valuation', {})
    
    if financial:
        # ROE > 15% 加分
        roe = financial.get('roe')
        if roe and roe > 15:
            fund_score += 25
        elif roe and roe > 10:
            fund_score += 15
        
        # 利润增长 > 20% 加分
        profit_growth = financial.get('profit_growth')
        if profit_growth and profit_growth > 20:
            fund_score += 25
        elif profit_growth and profit_growth > 0:
            fund_score += 15
        
        # 毛利率 > 30% 加分
        gross = financial.get('gross_margin')
        if gross and gross > 30:
            fund_score += 25
        elif gross and gross > 20:
            fund_score += 15
    
    if valuation:
        # PE < 30 加分
        pe = valuation.get('pe_ttm')
        if pe and pe < 30:
            fund_score += 25
        elif pe and pe < 50:
            fund_score += 15
    
    recommendation['fundamental_score'] = min(fund_score, 100)
    
    # 综合评级
    total_score = (tech_score + recommendation['fundamental_score']) / 2
    
    if total_score >= 80:
        recommendation['overall_rating'] = '强烈推荐'
        recommendation['suggestion'] = '技术面和基本面俱佳，建议重点关注，可考虑建仓'
    elif total_score >= 60:
        recommendation['overall_rating'] = '推荐'
        recommendation['suggestion'] = '技术面良好，基本面尚可，建议关注'
    elif total_score >= 40:
        recommendation['overall_rating'] = '中性'
        recommendation['suggestion'] = '技术面符合要求，但基本面一般，谨慎观察'
    else:
        recommendation['overall_rating'] = '观望'
        recommendation['suggestion'] = '技术面符合，但基本面较弱，建议观望'
    
    return recommendation