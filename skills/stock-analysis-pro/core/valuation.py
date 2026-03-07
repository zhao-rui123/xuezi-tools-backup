"""
估值策略筛选模块
支持：PB-ROE、PEG、综合估值评分
"""

import requests
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ValuationResult:
    """估值分析结果"""
    strategy: str
    score: float
    rank: int
    pe: Optional[float]
    pb: Optional[float]
    roe: Optional[float]
    description: str

@dataclass
class StockValuation:
    """单只股票估值数据"""
    code: str
    name: str
    pe_ttm: Optional[float]
    pb: Optional[float]
    roe: Optional[float]

def is_hk_stock(code: str) -> bool:
    return len(code) == 5 and code[0] in '012368'

def fetch_xueqiu_valuation(codes: List[str], headers: Dict, cookies: Dict) -> Dict[str, StockValuation]:
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
        response = requests.get(url, headers=headers, cookies=cookies, timeout=15)
        if response.status_code == 200:
            data = response.json()
            for item in data.get('data', {}).get('items', []):
                quote = item.get('quote', {})
                code = quote.get('code', '')
                if code.startswith(('SZ', 'SH')):
                    code = code[2:]
                
                pb = quote.get('pb')
                pe = quote.get('pe_ttm')
                roe = (pb / pe * 100) if pb and pe and pe > 0 else None
                
                result[code] = StockValuation(
                    code=code,
                    name=quote.get('name'),
                    pe_ttm=pe,
                    pb=pb,
                    roe=roe,
                )
    except Exception as e:
        print(f"获取估值数据失败: {e}")
    
    return result

def calculate_pb_roe_score(stocks: List[StockValuation]) -> List[ValuationResult]:
    """PB-ROE策略评分"""
    results = []
    
    for stock in stocks:
        if stock.pb is None or stock.roe is None or stock.pb <= 0:
            continue
        
        score = stock.roe / stock.pb
        
        results.append(ValuationResult(
            strategy="PB-ROE",
            score=round(score, 2),
            rank=0,
            pe=stock.pe_ttm,
            pb=stock.pb,
            roe=round(stock.roe, 2) if stock.roe else None,
            description=f"ROE {stock.roe:.1f}% / PB {stock.pb:.2f} = {score:.2f}"
        ))
    
    results.sort(key=lambda x: x.score, reverse=True)
    for i, r in enumerate(results):
        r.rank = i + 1
    
    return results

def calculate_peg_score(stocks: List[StockValuation]) -> List[ValuationResult]:
    """PEG策略评分"""
    results = []
    
    for stock in stocks:
        if stock.pe_ttm is None or stock.pe_ttm <= 0 or stock.roe is None:
            continue
        
        growth = stock.roe
        peg = stock.pe_ttm / growth if growth > 0 else float('inf')
        
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
            description=desc
        ))
    
    results.sort(key=lambda x: x.score, reverse=True)
    for i, r in enumerate(results):
        r.rank = i + 1
    
    return results

def calculate_comprehensive_score(stocks: List[StockValuation]) -> List[ValuationResult]:
    """综合估值评分"""
    results = []
    
    for stock in stocks:
        score = 50
        factors = []
        
        # PE评分
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
        
        # PB评分
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
        
        # ROE评分
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
            description=" | ".join(factors) if factors else "数据不足"
        ))
    
    results.sort(key=lambda x: x.score, reverse=True)
    for i, r in enumerate(results):
        r.rank = i + 1
    
    return results

def analyze_valuation(codes: List[str], headers: Dict, cookies: Dict) -> Dict[str, List[ValuationResult]]:
    """全面估值分析"""
    stock_data = fetch_xueqiu_valuation(codes, headers, cookies)
    stocks = list(stock_data.values())
    
    return {
        'pb_roe': calculate_pb_roe_score(stocks),
        'peg': calculate_peg_score(stocks),
        'comprehensive': calculate_comprehensive_score(stocks),
    }

def format_valuation_report(results: Dict[str, List[ValuationResult]], names: Dict) -> str:
    """格式化估值报告"""
    lines = ["📊 估值策略筛选"]
    
    if results.get('pb_roe'):
        lines.append("\n🏆 PB-ROE策略 (低PB+高ROE):")
        for i, r in enumerate(results['pb_roe'][:3]):
            lines.append(f"   {i+1}. {r.description}")
    
    if results.get('comprehensive'):
        lines.append("\n📈 综合估值评分:")
        for i, r in enumerate(results['comprehensive'][:3]):
            lines.append(f"   {i+1}. 得分{r.score} - {r.description}")
    
    return "\n".join(lines)
