#!/usr/bin/env python3
"""
股票深度分析模块 - 增强版
补充：盈利能力、成长性、财务健康、估值分位
"""

import urllib.request
import requests
import json
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# 配置
XUEQIU_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'origin': 'https://xueqiu.com',
    'referer': 'https://xueqiu.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

XUEQIU_COOKIES = {
    'xq_a_token': '8661982e927e023bf957bbc24b6fe85211ed4348',
    'xq_id_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjM0NDE2NzY4MjYsImlzcyI6InVjIiwiZXhwIjoxNzc1NDM0ODI0LCJjdG0iOjE3NzI4NDI4MjQ3MTQsImNpZCI6ImQ5ZDBuNEFadXAifQ.R8VRuz4gcsPrDv5jFU1c9WJYmulgC33sxR5Pkig9CRB-JZU4R--VkM9_mZjuKmx7g8SsJURq4UH5za6Qe9ey4RRtlKst1iL-2bKfX1_c5hxG9x6bHugx62zSlIJKYvqnPLwQ_rzgVH7daq11lfOoCya6LlOLZKffCgUiNzOlYSJTd9-m5Vf8ESs6kw1Nmh6lSEvbYym0VuvoN0YPiap9FlgLKUkuWLf9PJvo0Lfa6FoTAO6uMLTWYzUTSsTccTzF3xWUHb-ZBQY8kU72ZeDtXt_JzTYOov6ylbCOUSXPi4pY0_qZud_B71yFapuKheKbgMMZk2qPXZkbFgLHJJntXQ',
}

@dataclass
class DeepAnalysisResult:
    """深度分析结果"""
    code: str
    name: str
    # 盈利能力
    profitability_score: int
    profitability_desc: str
    # 成长性
    growth_score: int
    growth_desc: str
    # 财务健康
    financial_health_score: int
    financial_health_desc: str
    # 估值分位
    valuation_percentile: Optional[float]
    valuation_desc: str
    # 综合
    total_score: int
    rating: str  # 强烈买入/买入/持有/卖出/强烈卖出

def is_hk_stock(code: str) -> bool:
    return len(code) == 5 and code[0] in '012368'

def fetch_stock_data(code: str) -> Dict:
    """获取股票数据"""
    symbol = code if is_hk_stock(code) else (f'SH{code}' if code.startswith('6') else f'SZ{code}')
    url = f"https://stock.xueqiu.com/v5/stock/quote.json?symbol={symbol}&extend=detail"
    
    try:
        response = requests.get(url, headers=XUEQIU_HEADERS, cookies=XUEQIU_COOKIES, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('quote', {})
    except Exception as e:
        print(f"获取数据失败 {code}: {e}")
    return {}

def analyze_profitability(quote: Dict) -> Tuple[int, str]:
    """
    盈利能力分析
    基于PE、PB估算ROE
    """
    pe = quote.get('pe_ttm')
    pb = quote.get('pb')
    
    if not pe or not pb:
        return 50, "数据不足"
    
    # 估算ROE
    roe = (pb / pe * 100) if pe > 0 else 0
    
    if pe < 0:
        score = 20
        desc = f"亏损股 (PE为负)"
    elif roe > 20:
        score = 90
        desc = f"ROE {roe:.1f}% (优秀)"
    elif roe > 15:
        score = 75
        desc = f"ROE {roe:.1f}% (良好)"
    elif roe > 10:
        score = 60
        desc = f"ROE {roe:.1f}% (一般)"
    elif roe > 5:
        score = 45
        desc = f"ROE {roe:.1f}% (较弱)"
    else:
        score = 30
        desc = f"ROE {roe:.1f}% (差)"
    
    return score, desc

def analyze_growth(quote: Dict) -> Tuple[int, str]:
    """
    成长性分析
    基于PE、52周位置判断
    """
    pe = quote.get('pe_ttm')
    high52w = quote.get('high52w')
    low52w = quote.get('low52w')
    current = quote.get('current')
    
    if not all([high52w, low52w, current]) or high52w <= low52w:
        return 50, "数据不足"
    
    # 52周位置
    position = (current - low52w) / (high52w - low52w)
    
    # 结合PE判断成长性
    if pe and pe > 0:
        if pe < 20 and position > 0.7:
            score = 85
            desc = f"估值合理+高位运行，成长性好 (52周{position*100:.0f}%)"
        elif pe < 30 and position > 0.5:
            score = 70
            desc = f"估值适中+趋势向上 (52周{position*100:.0f}%)"
        elif position > 0.8:
            score = 60
            desc = f"高位运行但估值偏高 (52周{position*100:.0f}%)"
        elif position < 0.3:
            score = 40
            desc = f"低位运行，可能增长乏力 (52周{position*100:.0f}%)"
        else:
            score = 50
            desc = f"走势平稳 (52周{position*100:.0f}%)"
    else:
        score = 40
        desc = f"亏损中，成长性待观察 (52周{position*100:.0f}%)"
    
    return score, desc

def analyze_financial_health(quote: Dict) -> Tuple[int, str]:
    """
    财务健康分析
    基于市净率、换手率综合判断
    """
    pb = quote.get('pb')
    turnover = quote.get('turnover_rate')
    pe = quote.get('pe_ttm')
    
    score = 50
    factors = []
    
    # PB判断
    if pb:
        if pb < 2:
            score += 20
            factors.append("资产质量高(PB低)")
        elif pb < 4:
            score += 10
            factors.append("资产质量正常")
        else:
            score -= 10
            factors.append("资产溢价高")
    
    # 换手率判断（流动性）
    if turnover:
        if 1 < turnover < 10:
            score += 15
            factors.append("流动性良好")
        elif turnover > 10:
            score += 5
            factors.append("流动性高但可能波动大")
        else:
            factors.append("流动性较低")
    
    # 盈利状况
    if pe:
        if pe < 0:
            score -= 15
            factors.append("当前亏损")
        elif pe < 50:
            score += 10
            factors.append("盈利稳定")
    
    score = max(20, min(95, score))
    
    return score, " | ".join(factors) if factors else "数据不足"

def analyze_valuation_percentile(quote: Dict) -> Tuple[Optional[float], str]:
    """
    估值分位分析
    基于52周位置估算
    """
    high52w = quote.get('high52w')
    low52w = quote.get('low52w')
    current = quote.get('current')
    pe = quote.get('pe_ttm')
    pb = quote.get('pb')
    
    if not all([high52w, low52w, current]) or high52w <= low52w:
        return None, "数据不足"
    
    # 价格分位
    price_percentile = (current - low52w) / (high52w - low52w) * 100
    
    desc_parts = [f"价格分位{price_percentile:.0f}%"]
    
    # PE分位（简化估算）
    if pe:
        if pe < 0:
            desc_parts.append("PE为负(亏损)")
        elif pe < 15:
            desc_parts.append("PE极低(历史低位)")
        elif pe < 30:
            desc_parts.append("PE合理")
        elif pe < 50:
            desc_parts.append("PE偏高")
        else:
            desc_parts.append("PE极高")
    
    # PB分位
    if pb:
        if pb < 1.5:
            desc_parts.append("PB极低")
        elif pb < 3:
            desc_parts.append("PB合理")
        else:
            desc_parts.append("PB偏高")
    
    return price_percentile, " | ".join(desc_parts)

def calculate_rating(total_score: int) -> str:
    """根据总分给出评级"""
    if total_score >= 80:
        return "强烈买入 ⭐⭐⭐⭐⭐"
    elif total_score >= 65:
        return "买入 ⭐⭐⭐⭐"
    elif total_score >= 50:
        return "持有 ⭐⭐⭐"
    elif total_score >= 35:
        return "卖出 ⭐⭐"
    else:
        return "强烈卖出 ⭐"

def deep_analyze_stock(code: str, name: str = "") -> Optional[DeepAnalysisResult]:
    """
    深度分析单只股票
    """
    quote = fetch_stock_data(code)
    if not quote:
        return None
    
    name = name or quote.get('name', code)
    
    # 各维度分析
    prof_score, prof_desc = analyze_profitability(quote)
    growth_score, growth_desc = analyze_growth(quote)
    health_score, health_desc = analyze_financial_health(quote)
    val_percentile, val_desc = analyze_valuation_percentile(quote)
    
    # 总分
    total = int((prof_score + growth_score + health_score) / 3)
    
    return DeepAnalysisResult(
        code=code,
        name=name,
        profitability_score=prof_score,
        profitability_desc=prof_desc,
        growth_score=growth_score,
        growth_desc=growth_desc,
        financial_health_score=health_score,
        financial_health_desc=health_desc,
        valuation_percentile=val_percentile,
        valuation_desc=val_desc,
        total_score=total,
        rating=calculate_rating(total)
    )

def format_deep_analysis(result: DeepAnalysisResult) -> str:
    """格式化深度分析报告"""
    stars = "⭐" * (result.total_score // 20 + 1)
    
    lines = [
        f"\n{'='*60}",
        f"🔍 深度分析报告: {result.name} ({result.code})",
        f"{'='*60}",
        f"",
        f"【综合评级】{result.rating}",
        f"【总分】{result.total_score}/100 {stars}",
        f"",
        f"【盈利能力】{result.profitability_score}/100",
        f"   {result.profitability_desc}",
        f"",
        f"【成长性】{result.growth_score}/100",
        f"   {result.growth_desc}",
        f"",
        f"【财务健康】{result.financial_health_score}/100",
        f"   {result.financial_health_desc}",
        f"",
        f"【估值分位】",
        f"   {result.valuation_desc}",
        f"",
        f"{'='*60}",
    ]
    
    return "\n".join(lines)

if __name__ == "__main__":
    # 测试
    test_codes = [
        ("002460", "赣锋锂业"),
        ("000725", "京东方A"),
        ("00981", "中芯国际"),
    ]
    
    for code, name in test_codes:
        result = deep_analyze_stock(code, name)
        if result:
            print(format_deep_analysis(result))
