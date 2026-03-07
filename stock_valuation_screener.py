#!/usr/bin/env python3
"""
股票估值策略筛选模块
支持：PB-ROE、PEG、股息率、综合估值评分
"""

import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# 雪球配置（复用主配置）
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
class ValuationResult:
    """估值分析结果"""
    strategy: str      # 策略名称
    score: float       # 得分
    rank: int          # 排名
    pe: Optional[float]
    pb: Optional[float]
    roe: Optional[float]
    dividend_yield: Optional[float]
    description: str   # 描述

@dataclass
class StockValuation:
    """单只股票估值数据"""
    code: str
    name: str
    pe_ttm: Optional[float]
    pb: Optional[float]
    market_cap: Optional[float]
    turnover_rate: Optional[float]
    # 衍生指标
    roe: Optional[float] = None  # 需要从其他数据源获取
    dividend_yield: Optional[float] = None
    growth_rate: Optional[float] = None  # 盈利增速

def is_hk_stock(code: str) -> bool:
    """判断是否为港股"""
    return len(code) == 5 and code[0] in '012368'

def fetch_xueqiu_valuation(codes: List[str]) -> Dict[str, StockValuation]:
    """从雪球获取估值数据"""
    symbols = []
    for c in codes:
        if is_hk_stock(c):
            symbols.append(c)
        elif c.startswith('6'):
            symbols.append(f'SH{c}')
        else:
            symbols.append(f'SZ{c}')
    
    symbol_str = ','.join(symbols)
    url = f"https://stock.xueqiu.com/v5/stock/batch/quote.json?symbol={symbol_str}&extend=detail"
    
    result = {}
    try:
        response = requests.get(url, headers=XUEQIU_HEADERS, cookies=XUEQIU_COOKIES, timeout=15)
        if response.status_code == 200:
            data = response.json()
            for item in data.get('data', {}).get('items', []):
                quote = item.get('quote', {})
                code = quote.get('code', '')
                if code.startswith(('SZ', 'SH')):
                    code = code[2:]
                
                # 估算ROE = PB / PE (简化)
                pb = quote.get('pb')
                pe = quote.get('pe_ttm')
                roe = (pb / pe * 100) if pb and pe and pe > 0 else None
                
                result[code] = StockValuation(
                    code=code,
                    name=quote.get('name'),
                    pe_ttm=pe,
                    pb=pb,
                    market_cap=quote.get('market_cap'),
                    turnover_rate=quote.get('turnover_rate'),
                    roe=roe,
                )
    except Exception as e:
        print(f"获取估值数据失败: {e}")
    
    return result

def calculate_pb_roe_score(stocks: List[StockValuation]) -> List[ValuationResult]:
    """
    PB-ROE策略评分
    理念：低PB + 高ROE = 价值股
    公式：得分 = ROE / PB
    """
    results = []
    
    for stock in stocks:
        if stock.pb is None or stock.roe is None or stock.pb <= 0:
            continue
        
        # PB-ROE得分
        score = stock.roe / stock.pb
        
        results.append(ValuationResult(
            strategy="PB-ROE",
            score=round(score, 2),
            rank=0,
            pe=stock.pe_ttm,
            pb=stock.pb,
            roe=round(stock.roe, 2) if stock.roe else None,
            dividend_yield=None,
            description=f"ROE {stock.roe:.1f}% / PB {stock.pb:.2f} = {score:.2f}"
        ))
    
    # 排序
    results.sort(key=lambda x: x.score, reverse=True)
    for i, r in enumerate(results):
        r.rank = i + 1
    
    return results

def calculate_peg_score(stocks: List[StockValuation]) -> List[ValuationResult]:
    """
    PEG策略评分
    理念：PE / 盈利增速 < 1 为低估
    注意：这里简化处理，使用ROE作为增速代理
    """
    results = []
    
    for stock in stocks:
        if stock.pe_ttm is None or stock.pe_ttm <= 0 or stock.roe is None:
            continue
        
        # 简化：假设增速 ≈ ROE
        growth = stock.roe
        peg = stock.pe_ttm / growth if growth > 0 else float('inf')
        
        # PEG < 1 得高分
        if peg < 1:
            score = 100 - peg * 50
            desc = f"PEG {peg:.2f} < 1 (低估)"
        elif peg < 2:
            score = 50 - (peg - 1) * 25
            desc = f"PEG {peg:.2f} (合理)"
        else:
            score = max(0, 25 - (peg - 2) * 5)
            desc = f"PEG {peg:.2f} (偏高)"
        
        results.append(ValuationResult(
            strategy="PEG",
            score=round(score, 1),
            rank=0,
            pe=stock.pe_ttm,
            pb=stock.pb,
            roe=round(stock.roe, 2) if stock.roe else None,
            dividend_yield=None,
            description=desc
        ))
    
    results.sort(key=lambda x: x.score, reverse=True)
    for i, r in enumerate(results):
        r.rank = i + 1
    
    return results

def calculate_comprehensive_valuation(stocks: List[StockValuation]) -> List[ValuationResult]:
    """
    综合估值评分
    综合PE、PB、ROE多个维度
    """
    results = []
    
    for stock in stocks:
        score = 50  # 基础分
        factors = []
        
        # PE评分 (30分)
        if stock.pe_ttm:
            if stock.pe_ttm < 0:
                score += 0
                factors.append("亏损")
            elif stock.pe_ttm < 15:
                score += 30
                factors.append("PE极低")
            elif stock.pe_ttm < 30:
                score += 20
                factors.append("PE合理")
            elif stock.pe_ttm < 50:
                score += 10
                factors.append("PE偏高")
            else:
                score += 0
                factors.append("PE极高")
        
        # PB评分 (30分)
        if stock.pb:
            if stock.pb < 1.5:
                score += 30
                factors.append("PB极低")
            elif stock.pb < 3:
                score += 20
                factors.append("PB合理")
            elif stock.pb < 5:
                score += 10
                factors.append("PB偏高")
            else:
                score += 0
                factors.append("PB极高")
        
        # ROE评分 (20分)
        if stock.roe:
            if stock.roe > 20:
                score += 20
                factors.append("ROE优秀")
            elif stock.roe > 15:
                score += 15
                factors.append("ROE良好")
            elif stock.roe > 10:
                score += 10
                factors.append("ROE一般")
            elif stock.roe > 0:
                score += 5
                factors.append("ROE较低")
            else:
                score += 0
                factors.append("ROE为负")
        
        results.append(ValuationResult(
            strategy="综合估值",
            score=round(score, 1),
            rank=0,
            pe=stock.pe_ttm,
            pb=stock.pb,
            roe=round(stock.roe, 2) if stock.roe else None,
            dividend_yield=None,
            description=" | ".join(factors) if factors else "数据不足"
        ))
    
    results.sort(key=lambda x: x.score, reverse=True)
    for i, r in enumerate(results):
        r.rank = i + 1
    
    return results

def analyze_valuation(codes: List[str], names: Dict[str, str] = None) -> Dict[str, List[ValuationResult]]:
    """
    全面估值分析
    返回各策略的评分排名
    """
    # 获取数据
    stock_data = fetch_xueqiu_valuation(codes)
    stocks = list(stock_data.values())
    
    return {
        'pb_roe': calculate_pb_roe_score(stocks),
        'peg': calculate_peg_score(stocks),
        'comprehensive': calculate_comprehensive_valuation(stocks),
    }

def format_valuation_report(results: Dict[str, List[ValuationResult]], names: Dict[str, str]) -> str:
    """格式化估值报告"""
    lines = ["📊 估值策略筛选"]
    
    # PB-ROE策略
    if results.get('pb_roe'):
        lines.append("\n🏆 PB-ROE策略 (低PB+高ROE):")
        for i, r in enumerate(results['pb_roe'][:3]):
            lines.append(f"   {i+1}. {r.description}")
    
    # PEG策略
    if results.get('peg'):
        lines.append("\n🌱 PEG策略 (成长股):")
        for i, r in enumerate(results['peg'][:3]):
            if r.score > 50:
                lines.append(f"   {i+1}. {r.description}")
    
    # 综合评分
    if results.get('comprehensive'):
        lines.append("\n📈 综合估值评分:")
        for i, r in enumerate(results['comprehensive'][:3]):
            lines.append(f"   {i+1}. 得分{r.score} - {r.description}")
    
    return "\n".join(lines)

if __name__ == "__main__":
    # 测试
    test_codes = ["002460", "002738", "000792", "000725", "600707", "00981", "01772"]
    results = analyze_valuation(test_codes)
    
    print("估值策略测试:")
    print(format_valuation_report(results, {}))
