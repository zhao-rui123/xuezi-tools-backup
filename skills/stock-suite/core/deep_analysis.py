"""
深度分析模块 - 综合分析股票基本面、技术面、估值
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DeepAnalysisResult:
    """深度分析结果"""
    code: str
    name: str
    stock_type: str
    overall_score: int
    overall_rating: str
    
    profitability_score: int
    growth_score: int
    financial_health_score: int
    valuation_score: int
    
    technical_score: int
    pattern_result: Optional[Dict]
    
    details: Dict

def analyze_stock_type(code: str, name: str, quote: Dict) -> str:
    """分析股票类型"""
    from core.stock_classifier import classify_stock
    
    result = classify_stock(code, name)
    return result.stock_type

def analyze_profitability(quote: Dict) -> Dict:
    """分析盈利能力"""
    roe = quote.get('roe', 0)
    gross_margin = quote.get('gross_margin', 0)
    net_margin = quote.get('net_margin', 0)
    
    score = 0
    
    if roe and roe > 0:
        if roe > 20:
            score += 40
        elif roe > 15:
            score += 30
        elif roe > 10:
            score += 20
        elif roe > 5:
            score += 10
    
    if gross_margin and gross_margin > 30:
        score += 30
    elif gross_margin and gross_margin > 20:
        score += 20
    elif gross_margin and gross_margin > 10:
        score += 10
    
    if net_margin and net_margin > 15:
        score += 30
    elif net_margin and net_margin > 10:
        score += 20
    elif net_margin and net_margin > 5:
        score += 10
    
    rating = "优秀" if score >= 70 else "良好" if score >= 50 else "一般" if score >= 30 else "较差"
    
    return {
        'score': min(score, 100),
        'rating': rating,
        'roe': roe,
        'gross_margin': gross_margin,
        'net_margin': net_margin,
    }

def analyze_growth(quote: Dict) -> Dict:
    """分析成长性"""
    revenue_growth = quote.get('revenue_growth', 0)
    profit_growth = quote.get('profit_growth', 0)
    
    score = 0
    
    if revenue_growth and revenue_growth > 30:
        score += 50
    elif revenue_growth and revenue_growth > 20:
        score += 40
    elif revenue_growth and revenue_growth > 10:
        score += 30
    elif revenue_growth and revenue_growth > 0:
        score += 20
    
    if profit_growth and profit_growth > 30:
        score += 50
    elif profit_growth and profit_growth > 20:
        score += 40
    elif profit_growth and profit_growth > 10:
        score += 30
    elif profit_growth and profit_growth > 0:
        score += 20
    
    rating = "优秀" if score >= 70 else "良好" if score >= 50 else "一般" if score >= 30 else "较差"
    
    return {
        'score': min(score, 100),
        'rating': rating,
        'revenue_growth': revenue_growth,
        'profit_growth': profit_growth,
    }

def analyze_financial_health(quote: Dict) -> Dict:
    """分析财务健康度"""
    pb = quote.get('pb', 0)
    turnover = quote.get('turnover_rate', 0)
    
    score = 50
    
    if pb and 0 < pb < 1:
        score += 30
    elif pb and pb < 2:
        score += 20
    elif pb and pb > 5:
        score -= 20
    
    if turnover and turnover > 3:
        score += 20
    elif turnover and turnover > 1:
        score += 10
    
    rating = "优秀" if score >= 80 else "良好" if score >= 60 else "一般" if score >= 40 else "较差"
    
    return {
        'score': min(max(score, 0), 100),
        'rating': rating,
        'pb': pb,
        'turnover': turnover,
    }

def analyze_valuation(quote: Dict) -> Dict:
    """分析估值水平"""
    pe = quote.get('pe_ttm', 0)
    pb = quote.get('pb', 0)
    roe = quote.get('roe', 0)
    
    score = 50
    
    if pe and pe > 0:
        if pe < 15:
            score += 30
        elif pe < 25:
            score += 15
        elif pe < 40:
            score -= 10
        else:
            score -= 20
    
    if pb and pb > 0:
        if pb < 1:
            score += 20
        elif pb < 3:
            score += 10
        elif pb > 8:
            score -= 10
    
    if roe and pe and pe > 0:
        peg_ratio = pe / roe
        if peg_ratio < 1:
            score += 20
        elif peg_ratio < 2:
            score += 10
    
    rating = "低估" if score >= 70 else "合理" if score >= 50 else "偏高" if score >= 30 else "高估"
    
    return {
        'score': min(max(score, 0), 100),
        'rating': rating,
        'pe': pe,
        'pb': pb,
    }

def analyze_technical(code: str) -> Dict:
    """分析技术面"""
    try:
        from core.data_fetcher import fetch_tencent_kline
        from core.technical_analysis import calculate_all_indicators, get_all_signals
        from core.pattern_recognition import analyze_all_patterns
        
        data = fetch_tencent_kline(code, 60)
        if not data or len(data) < 20:
            return {'score': 50, 'rating': '数据不足', 'signals': {}, 'patterns': []}
        
        data = calculate_all_indicators(data)
        signals = get_all_signals(data)
        patterns = analyze_all_patterns(data)
        
        score = 50
        
        if signals.get('macd_golden_cross'):
            score += 15
        if signals.get('kdj_golden_cross'):
            score += 10
        if signals.get('ma_alignment'):
            score += 15
        if signals.get('volume_increase'):
            score += 10
        
        rating = "强势" if score >= 70 else "中性" if score >= 50 else "弱势"
        
        return {
            'score': min(score, 100),
            'rating': rating,
            'signals': signals,
            'patterns': patterns,
        }
    except Exception as e:
        return {'score': 50, 'rating': '分析失败', 'error': str(e)}

def deep_analyze_stock(code: str, name: str = "") -> Optional[DeepAnalysisResult]:
    """深度分析单只股票"""
    try:
        from core.data_fetcher import fetch_xueqiu_quotes, fetch_sina_quotes
        
        quote_xueqiu = {}
        try:
            quote_xueqiu = fetch_xueqiu_quotes([code])
        except:
            pass
        
        if not quote_xueqiu:
            quote_sina = fetch_sina_quotes([code])
            quote = quote_sina.get(code, {})
        else:
            quote = quote_xueqiu.get(code, {})
        
        if not name and quote.get('name'):
            name = quote['name']
        
        stock_type = analyze_stock_type(code, name, quote)
        
        profitability = analyze_profitability(quote)
        growth = analyze_growth(quote)
        financial_health = analyze_financial_health(quote)
        valuation = analyze_valuation(quote)
        technical = analyze_technical(code)
        
        fundamental_score = (profitability['score'] + growth['score'] + 
                           financial_health['score'] + valuation['score']) // 4
        
        overall_score = (fundamental_score * 0.6 + technical['score'] * 0.4)
        
        if overall_score >= 80:
            rating = "强烈推荐"
        elif overall_score >= 65:
            rating = "推荐"
        elif overall_score >= 50:
            rating = "持有"
        elif overall_score >= 35:
            rating = "谨慎"
        else:
            rating = "回避"
        
        return DeepAnalysisResult(
            code=code,
            name=name or code,
            stock_type=stock_type,
            overall_score=overall_score,
            overall_rating=rating,
            profitability_score=profitability['score'],
            growth_score=growth['score'],
            financial_health_score=financial_health['score'],
            valuation_score=valuation['score'],
            technical_score=technical['score'],
            pattern_result=technical.get('patterns', [{}])[0] if technical.get('patterns') else None,
            details={
                'profitability': profitability,
                'growth': growth,
                'financial_health': financial_health,
                'valuation': valuation,
                'technical': technical,
                'quote': quote,
            }
        )
    except Exception as e:
        print(f"深度分析失败: {e}")
        return None

def format_deep_analysis(result: DeepAnalysisResult) -> str:
    """格式化深度分析报告"""
    emoji_map = {
        "强烈推荐": "⭐⭐⭐⭐⭐",
        "推荐": "⭐⭐⭐⭐",
        "持有": "⭐⭐⭐",
        "谨慎": "⭐⭐",
        "回避": "⭐",
    }
    
    lines = [
        f"\n{'='*60}",
        f"🔍 深度分析报告: {result.name} ({result.code})",
        f"{'='*60}",
        f"【股票类型】{result.stock_type}",
        f"【综合评级】{result.overall_rating} {emoji_map.get(result.overall_rating, '')}",
        f"【总分】{result.overall_score}/100",
        f"",
        f"【盈利能力】{result.profitability_score}/100 ({result.details['profitability']['rating']})",
        f"   ROE: {result.details['profitability'].get('roe', 'N/A')}%, 毛利率: {result.details['profitability'].get('gross_margin', 'N/A')}%, 净利率: {result.details['profitability'].get('net_margin', 'N/A')}%",
        f"",
        f"【成长性】{result.growth_score}/100 ({result.details['growth']['rating']})",
        f"   营收增速: {result.details['growth'].get('revenue_growth', 'N/A')}%, 利润增速: {result.details['growth'].get('profit_growth', 'N/A')}%",
        f"",
        f"【财务健康】{result.financial_health_score}/100 ({result.details['financial_health']['rating']})",
        f"   PB: {result.details['financial_health'].get('pb', 'N/A')}, 换手率: {result.details['financial_health'].get('turnover', 'N/A')}%",
        f"",
        f"【估值水平】{result.valuation_score}/100 ({result.details['valuation']['rating']})",
        f"   PE: {result.details['valuation'].get('pe', 'N/A')}, PB: {result.details['valuation'].get('pb', 'N/A')}",
        f"",
        f"【技术分析】{result.technical_score}/100 ({result.details['technical']['rating']})",
    ]
    
    if result.pattern_result:
        lines.append(f"   形态: {result.pattern_result.get('pattern', 'N/A')} ({result.pattern_result.get('confidence', 0)}%)")
    
    signals = result.details['technical'].get('signals', {})
    signal_strs = []
    if signals.get('macd_golden_cross'):
        signal_strs.append("MACD金叉")
    if signals.get('kdj_golden_cross'):
        signal_strs.append("KDJ金叉")
    if signals.get('ma_alignment'):
        signal_strs.append("均线多头")
    
    if signal_strs:
        lines.append(f"   信号: {', '.join(signal_strs)}")
    
    lines.append(f"{'='*60}")
    
    return "\n".join(lines)

def deep_analyze(code: str, name: str = "") -> str:
    """便捷函数：深度分析"""
    result = deep_analyze_stock(code, name)
    if result:
        return format_deep_analysis(result)
    return f"无法获取 {code} 的分析数据"
