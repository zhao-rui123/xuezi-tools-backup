"""
估值分析模块 - PB-ROE、PEG、综合估值
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ValuationResult:
    """估值分析结果"""
    score: float
    rank: int
    pe: Optional[float]
    pb: Optional[float]
    roe: Optional[float]
    peg: Optional[float]
    rating: str
    description: str

def analyze_pb_roe(stock_code: str, quote: Dict) -> ValuationResult:
    """PB-ROE估值分析"""
    pb = quote.get('pb')
    roe = quote.get('roe')
    
    if not pb or not roe or pb <= 0 or roe <= 0:
        return ValuationResult(
            score=0,
            rank=0,
            pe=None,
            pb=pb,
            roe=roe,
            peg=None,
            rating="无法评估",
            description="数据不足"
        )
    
    score = roe / pb * 100
    
    if score > 5:
        rating = "低估"
        desc = "ROE/PB比值较高，性价比好"
    elif score > 3:
        rating = "合理"
        desc = "ROE/PB比值适中"
    else:
        rating = "偏高"
        desc = "ROE/PB比值较低"
    
    return ValuationResult(
        score=round(score, 2),
        rank=0,
        pe=None,
        pb=pb,
        roe=roe,
        peg=None,
        rating=rating,
        description=desc
    )

def analyze_peg(stock_code: str, quote: Dict) -> ValuationResult:
    """PEG估值分析"""
    pe = quote.get('pe_ttm')
    profit_growth = quote.get('profit_growth')
    
    if not pe or not profit_growth:
        return ValuationResult(
            score=0,
            rank=0,
            pe=pe,
            pb=None,
            roe=None,
            peg=None,
            rating="无法评估",
            description="数据不足"
        )
    
    if profit_growth <= 0:
        peg = None
        score = 0
        rating = "负增长"
        desc = "利润负增长，无法用PEG评估"
    else:
        peg = pe / profit_growth
        
        if peg < 0.5:
            score = 100
            rating = "严重低估"
            desc = "PEG < 0.5，极具吸引力"
        elif peg < 1:
            score = 80
            rating = "低估"
            desc = "PEG < 1，有投资价值"
        elif peg < 1.5:
            score = 60
            rating = "合理"
            desc = "PEG 1-1.5，合理区间"
        elif peg < 2:
            score = 40
            rating = "偏高"
            desc = "PEG 1.5-2，估值偏高"
        else:
            score = 20
            rating = "高估"
            desc = "PEG > 2，估值较高"
    
    return ValuationResult(
        score=score,
        rank=0,
        pe=pe,
        pb=None,
        roe=None,
        peg=round(peg, 2) if peg else None,
        rating=rating,
        description=desc
    )

def analyze_comprehensive(quote: Dict) -> ValuationResult:
    """综合估值分析"""
    pe = quote.get('pe_ttm')
    pb = quote.get('pb')
    roe = quote.get('roe')
    turnover = quote.get('turnover_rate', 0)
    
    if not pe or not pb:
        return ValuationResult(
            score=0,
            rank=0,
            pe=pe,
            pb=pb,
            roe=roe,
            peg=None,
            rating="无法评估",
            description="数据不足"
        )
    
    score = 0
    details = []
    
    if pe:
        if pe < 0:
            score -= 20
            details.append("亏损")
        elif pe < 15:
            score += 30
            details.append("PE低")
        elif pe < 30:
            score += 15
            details.append("PE合理")
        else:
            score -= 10
            details.append("PE高")
    
    if pb:
        if pb < 1:
            score += 25
            details.append("破净")
        elif pb < 3:
            score += 15
            details.append("PB合理")
        elif pb < 5:
            score += 5
            details.append("PB偏高")
        else:
            score -= 10
            details.append("PB高")
    
    if roe and roe > 0:
        if roe > 20:
            score += 25
            details.append("ROE优秀")
        elif roe > 10:
            score += 15
            details.append("ROE良好")
        else:
            score += 5
            details.append("ROE一般")
    
    if turnover and turnover > 5:
        score += 10
        details.append("流动性好")
    
    if score >= 80:
        rating = "低估"
        desc = "综合评分高，投资价值明显"
    elif score >= 60:
        rating = "合理"
        desc = "综合评分适中，估值合理"
    elif score >= 40:
        rating = "偏高"
        desc = "综合评分偏低，估值偏高"
    else:
        rating = "高估"
        desc = "综合评分低，估值较高"
    
    return ValuationResult(
        score=score,
        rank=0,
        pe=pe,
        pb=pb,
        roe=roe,
        peg=None,
        rating=rating,
        description=desc
    )

def analyze_valuation(codes: List[str]) -> Dict:
    """批量估值分析"""
    try:
        from core.data_fetcher import fetch_xueqiu_quotes
        quotes = fetch_xueqiu_quotes(codes)
    except:
        try:
            from data_fetcher import fetch_xueqiu_quotes
            quotes = fetch_xueqiu_quotes(codes)
        except:
            quotes = {}
    
    results = {
        'pb_roe': [],
        'peg': [],
        'comprehensive': [],
    }
    
    for code in codes:
        quote = quotes.get(code, {})
        
        pb_roe_result = analyze_pb_roe(code, quote)
        results['pb_roe'].append({
            'code': code,
            'name': quote.get('name', code),
            'pb': pb_roe_result.pb,
            'roe': pb_roe_result.roe,
            'score': pb_roe_result.score,
            'rating': pb_roe_result.rating,
        })
        
        peg_result = analyze_peg(code, quote)
        results['peg'].append({
            'code': code,
            'name': quote.get('name', code),
            'pe': peg_result.pe,
            'peg': peg_result.peg,
            'score': peg_result.score,
            'rating': peg_result.rating,
        })
        
        comp_result = analyze_comprehensive(quote)
        results['comprehensive'].append({
            'code': code,
            'name': quote.get('name', code),
            'pe': comp_result.pe,
            'pb': comp_result.pb,
            'roe': comp_result.roe,
            'score': comp_result.score,
            'rating': comp_result.rating,
        })
    
    results['pb_roe'].sort(key=lambda x: x['score'], reverse=True)
    results['peg'].sort(key=lambda x: x['score'], reverse=True)
    results['comprehensive'].sort(key=lambda x: x['score'], reverse=True)
    
    return results

def format_valuation_report(results: Dict) -> str:
    """格式化估值报告"""
    lines = []
    
    lines.append("\n🏆 PB-ROE策略排名:")
    for i, r in enumerate(results.get('pb_roe', [])[:5], 1):
        lines.append(f"  {i}. {r['name']} ({r['code']}) - ROE: {r.get('roe', 'N/A')}%, PB: {r.get('pb', 'N/A')}, 得分: {r.get('score', 0)}")
    
    lines.append("\n📊 PEG策略排名:")
    for i, r in enumerate(results.get('peg', [])[:5], 1):
        lines.append(f"  {i}. {r['name']} ({r['code']}) - PE: {r.get('pe', 'N/A')}, PEG: {r.get('peg', 'N/A')}, 得分: {r.get('score', 0)}")
    
    lines.append("\n💡 综合估值排名:")
    for i, r in enumerate(results.get('comprehensive', [])[:5], 1):
        lines.append(f"  {i}. {r['name']} ({r['code']}) - 得分: {r.get('score', 0)}, 评级: {r.get('rating', 'N/A')}")
    
    return "\n".join(lines)
