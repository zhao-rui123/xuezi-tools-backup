#!/usr/bin/env python3
"""
增强版深度分析模块 - 支持三类股票差异化分析
"""

import sys
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace/skills/stock-analysis-pro')

from typing import Dict, Optional
from core.stock_classifier import classify_stock_by_name, get_stock_type_description, StockType
from core.cyclical_analysis import analyze_cyclical_stock, format_cyclical_report
from core.growth_analysis import analyze_growth_stock, format_growth_report
from core.value_analysis import analyze_value_stock, format_value_report
from core.deep_analysis import deep_analyze_stock as base_deep_analyze, format_deep_analysis as base_format_analysis

def enhanced_deep_analyze(stock_code: str, stock_name: str, 
                         sector: str, headers: Dict, cookies: Dict) -> Dict:
    """
    增强版深度分析
    根据股票类型自动选择分析框架
    
    Returns:
        Dict: {
            'stock_type': StockType,
            'type_description': str,
            'base_analysis': DeepAnalysisResult,  # 基础四维度分析
            'specialized_analysis': str,  # 专项分析报告
            'framework': Dict,  # 分析框架说明
        }
    """
    # 1. 识别股票类型
    stock_type = classify_stock_by_name(stock_name, sector)
    type_desc = get_stock_type_description(stock_type)
    
    # 2. 获取基础数据
    from core.data_fetcher import fetch_xueqiu_data
    quote = fetch_xueqiu_data([stock_code], headers, cookies).get(stock_code, {})
    
    # 3. 基础四维度分析（通用）
    base_analysis = base_deep_analyze(stock_code, stock_name, headers, cookies)
    
    # 4. 专项分析（根据类型）
    specialized_report = ""
    
    if stock_type == StockType.CYCLICAL:
        # 周期股专项分析
        cyclical_result = analyze_cyclical_stock(stock_code, stock_name, sector, quote)
        specialized_report = format_cyclical_report(cyclical_result)
    
    elif stock_type == StockType.GROWTH:
        # 成长股专项分析
        # 简化：使用当前PE反推预期增速
        pe = quote.get('pe_ttm')
        estimated_growth = min(pe * 0.5, 50) if pe and pe > 0 else 20
        growth_result = analyze_growth_stock(stock_code, stock_name, sector, quote, estimated_growth)
        specialized_report = format_growth_report(growth_result)
    
    elif stock_type == StockType.VALUE:
        # 价值股专项分析
        value_result = analyze_value_stock(stock_code, stock_name, sector, quote)
        specialized_report = format_value_report(value_result)
    
    elif stock_type == StockType.HYBRID:
        # 混合型：结合两种分析
        # 简化：同时做周期和成长分析
        cyclical_result = analyze_cyclical_stock(stock_code, stock_name, sector, quote)
        specialized_report = format_cyclical_report(cyclical_result)
        specialized_report += "\n\n【混合型补充分析】\n该股票兼具多种特征，建议综合运用多种分析方法。"
    
    else:
        # 未知类型：只返回基础分析
        specialized_report = "【类型未知】\n无法自动分类，建议人工判断股票类型后选择适当分析框架。"
    
    # 5. 获取分析框架说明
    from core.stock_classifier import get_analysis_framework
    framework = get_analysis_framework(stock_type)
    
    return {
        'stock_type': stock_type,
        'type_description': type_desc,
        'base_analysis': base_analysis,
        'specialized_analysis': specialized_report,
        'framework': framework,
    }

def format_enhanced_report(result: Dict) -> str:
    """格式化增强版分析报告"""
    lines = [
        f"\n{'='*70}",
        f"🔍 深度分析报告（增强版）",
        f"{'='*70}",
        f"",
        f"【股票类型识别】",
        f"   类型：{result['stock_type'].value}",
        f"   描述：{result['type_description']}",
        f"",
        f"【分析框架】",
        f"   框架：{result['framework']['name']}",
        f"   估值方法：{result['framework']['valuation_method']}",
        f"   关注重点：{result['framework']['focus']}",
        f"",
    ]
    
    # 基础四维度分析
    if result['base_analysis']:
        lines.append(base_format_analysis(result['base_analysis']))
    
    # 专项分析
    lines.extend([
        f"",
        result['specialized_analysis'],
    ])
    
    lines.extend([
        f"",
        f"{'='*70}",
    ])
    
    return "\n".join(lines)

if __name__ == "__main__":
    # 测试不同股票类型
    from config.xueqiu_config import XUEQIU_HEADERS, XUEQIU_COOKIES
    
    test_cases = [
        ("002738", "中矿资源", "锂矿/资源"),  # 周期股
        ("300750", "宁德时代", "新能源电池"),  # 成长股
        ("600036", "招商银行", "银行"),       # 价值股
    ]
    
    for code, name, sector in test_cases:
        print(f"\n{'#'*70}")
        print(f"测试: {name} ({code})")
        print(f"{'#'*70}")
        
        result = enhanced_deep_analyze(code, name, sector, XUEQIU_HEADERS, XUEQIU_COOKIES)
        print(format_enhanced_report(result))
