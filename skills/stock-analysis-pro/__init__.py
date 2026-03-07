"""
Stock Analysis Pro - 专业股票分析技能包
"""

from .core.deep_analysis import deep_analyze_stock, format_deep_analysis
from .core.pattern_recognition import analyze_patterns, format_pattern_report
from .core.valuation import analyze_valuation, format_valuation_report
from .core.daily_report import generate_daily_report, send_to_feishu

__version__ = "2.0.0"
__author__ = "雪子助手"

# 便捷函数
__all__ = [
    'deep_analyze',
    'scan_patterns',
    'valuation_screen',
    'generate_daily_report',
    'send_to_feishu',
]

def deep_analyze(code: str, name: str = ""):
    """
    深度分析单只股票
    
    Args:
        code: 股票代码
        name: 股票名称（可选）
    
    Returns:
        格式化分析报告字符串
    """
    result = deep_analyze_stock(code, name)
    if result:
        return format_deep_analysis(result)
    return f"无法获取 {code} 的分析数据"

def scan_patterns(codes: list):
    """
    扫描多只股票的技术形态
    
    Args:
        codes: 股票代码列表
    
    Returns:
        形态识别结果列表
    """
    results = []
    for code in codes:
        result = analyze_patterns(code, "")
        if result and result.confidence >= 60:
            results.append({
                'code': code,
                'name': result.pattern_name,
                'pattern': result.pattern_name,
                'confidence': result.confidence,
                'suggestion': result.suggestion,
            })
    return results

def valuation_screen(codes: list):
    """
    估值策略筛选
    
    Args:
        codes: 股票代码列表
    
    Returns:
        dict: {
            'pb_roe': [...],
            'peg': [...],
            'comprehensive': [...]
        }
    """
    return analyze_valuation(codes)
