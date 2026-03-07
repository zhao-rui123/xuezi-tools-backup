#!/usr/bin/env python3
"""
价值股专用分析模块
针对价值股的特殊分析框架：ROE稳定性、股息率、PB-ROE、安全边际
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ValueAnalysisResult:
    """价值股分析结果"""
    code: str
    name: str
    # 核心指标
    roe_assessment: str      # ROE评估
    pb_assessment: str       # PB评估
    dividend_assessment: str # 股息评估
    safety_margin: str       # 安全边际
    # 估值
    pb_roe_score: Optional[float]  # PB-ROE得分
    # 分析
    value_analysis: str      # 价值分析
    valuation_method: str    # 估值方法
    investment_strategy: str # 投资策略
    risks: List[str]         # 风险提示

def analyze_roe(roe: Optional[float], stability_years: int = 5) -> Tuple[str, int]:
    """
    分析ROE质量
    
    Returns:
        (评估, 评分)
    """
    if roe is None:
        return "ROE数据缺失", 50
    
    if roe > 20:
        return f"ROE {roe:.1f}%，优秀（持续5年则质量极高）", 90
    elif roe > 15:
        return f"ROE {roe:.1f}%，良好", 75
    elif roe > 10:
        return f"ROE {roe:.1f}%，合格", 60
    elif roe > 5:
        return f"ROE {roe:.1f}%，较弱", 45
    else:
        return f"ROE {roe:.1f}%，差", 30

def analyze_pb(pb: Optional[float], roe: Optional[float]) -> str:
    """分析PB水平"""
    if pb is None:
        return "PB数据缺失"
    
    # 结合ROE判断PB是否合理
    if roe and roe > 0:
        reasonable_pb = roe / 10  # 简化：合理PB ≈ ROE/10
        if pb < reasonable_pb * 0.8:
            return f"PB {pb:.2f}倍，低于合理水平({reasonable_pb:.1f})，可能被低估"
        elif pb < reasonable_pb * 1.2:
            return f"PB {pb:.2f}倍，接近合理水平({reasonable_pb:.1f})"
        else:
            return f"PB {pb:.2f}倍，高于合理水平({reasonable_pb:.1f})，可能偏贵"
    else:
        if pb < 1:
            return f"PB {pb:.2f}倍 < 1，破净，可能被低估"
        elif pb < 1.5:
            return f"PB {pb:.2f}倍，较低"
        elif pb < 3:
            return f"PB {pb:.2f}倍，合理"
        else:
            return f"PB {pb:.2f}倍，较高"

def calculate_pb_roe_score(pb: float, roe: float) -> Tuple[float, str]:
    """
    计算PB-ROE得分
    公式：ROE/PB，或 ROE - 要求回报率*PB
    """
    if pb <= 0 or roe <= 0:
        return 0, "PB或ROE异常，无法计算"
    
    # 方法一：ROE/PB
    score1 = roe / pb
    
    # 方法二：简化格雷厄姆公式
    # 合理价格 = EPS * (8.5 + 2g) 或简化用ROE代替
    required_return = 10  # 要求回报率10%
    score2 = roe - required_return * pb
    
    assessment = f"ROE/PB = {score1:.2f}"
    if score1 > 10:
        assessment += "，极好"
    elif score1 > 7:
        assessment += "，优秀"
    elif score1 > 5:
        assessment += "，良好"
    elif score1 > 3:
        assessment += "，一般"
    else:
        assessment += "，较差"
    
    return score1, assessment

def analyze_dividend(dividend_yield: Optional[float], 
                    payout_ratio: Optional[float],
                    years_of_dividend: int = 5) -> str:
    """分析股息"""
    if dividend_yield is None:
        return "股息率数据缺失"
    
    assessment = f"股息率 {dividend_yield:.2f}%"
    
    if dividend_yield > 5:
        assessment += "，极高（注意可持续性）"
    elif dividend_yield > 4:
        assessment += "，很高（有吸引力）"
    elif dividend_yield > 3:
        assessment += "，较高（不错）"
    elif dividend_yield > 2:
        assessment += "，中等"
    else:
        assessment += "，较低"
    
    if payout_ratio:
        if payout_ratio > 70:
            assessment += f"；分红率{payout_ratio:.0f}%较高，留存资金较少"
        elif payout_ratio < 30:
            assessment += f"；分红率{payout_ratio:.0f}%较低，公司倾向留存"
        else:
            assessment += f"；分红率{payout_ratio:.0f}%合理"
    
    assessment += f"；连续分红{years_of_dividend}年"
    
    return assessment

def calculate_safety_margin(current_pb: float, 
                           historical_avg_pb: Optional[float],
                           roe: Optional[float]) -> str:
    """计算安全边际"""
    margins = []
    
    # 基于历史PB
    if historical_avg_pb and historical_avg_pb > 0:
        pb_discount = (historical_avg_pb - current_pb) / historical_avg_pb
        if pb_discount > 0.3:
            margins.append(f"PB较历史均值低{pb_discount*100:.0f}%，安全边际较高")
        elif pb_discount > 0.1:
            margins.append(f"PB较历史均值低{pb_discount*100:.0f}%，有一定安全边际")
        elif pb_discount > -0.1:
            margins.append("PB接近历史均值，安全边际一般")
        else:
            margins.append(f"PB高于历史均值，安全边际较低")
    
    # 基于ROE的PB合理性
    if roe and roe > 0:
        fair_pb = roe / 10
        if current_pb < fair_pb * 0.8:
            margins.append(f"PB低于合理估值20%以上，安全边际较高")
        elif current_pb < fair_pb:
            margins.append(f"PB低于合理估值，有一定安全边际")
    
    # 破净判断
    if current_pb < 1:
        margins.append("破净（PB<1），如果资产质量可靠，安全边际较高")
    
    return "；".join(margins) if margins else "需要更多信息评估安全边际"

def analyze_value_stock(stock_code: str, stock_name: str,
                       sector: str, quote: Dict,
                       historical_pb: Optional[float] = None,
                       dividend_yield: Optional[float] = None,
                       payout_ratio: Optional[float] = None) -> ValueAnalysisResult:
    """
    分析价值股
    """
    pe = quote.get('pe_ttm')
    pb = quote.get('pb')
    
    # 估算ROE（如果没有直接数据）
    if pb and pe and pe > 0:
        roe = (pb / pe) * 100
    else:
        roe = None
    
    # 1. ROE评估
    roe_assessment, roe_score = analyze_roe(roe)
    
    # 2. PB评估
    pb_assessment = analyze_pb(pb, roe)
    
    # 3. PB-ROE得分
    if pb and roe and pb > 0 and roe > 0:
        pb_roe_score, pb_roe_assessment = calculate_pb_roe_score(pb, roe)
    else:
        pb_roe_score = None
        pb_roe_assessment = "数据不足"
    
    # 4. 股息评估
    dividend_assessment = analyze_dividend(dividend_yield, payout_ratio)
    
    # 5. 安全边际
    safety_margin = calculate_safety_margin(pb or 2, historical_pb, roe)
    
    # 6. 价值分析
    value_points = []
    if roe and roe > 15:
        value_points.append(f"ROE{roe:.1f}%优秀，盈利能力稳定")
    if pb and pb < 2:
        value_points.append(f"PB{pb:.2f}较低，估值合理")
    if dividend_yield and dividend_yield > 3:
        value_points.append(f"股息率{dividend_yield:.2f}%有吸引力")
    
    if value_points:
        value_analysis = "；".join(value_points)
    else:
        value_analysis = "当前估值和盈利指标一般，需进一步分析资产质量"
    
    # 7. 投资策略
    if pb_roe_score and pb_roe_score > 7:
        strategy = f"价值股策略：PB-ROE得分{pb_roe_score:.2f}优秀，ROE{roe:.1f}%且PB{pb:.2f}合理，具备安全边际，可考虑建仓。"
    elif pb_roe_score and pb_roe_score > 5:
        strategy = f"价值股策略：PB-ROE得分{pb_roe_score:.2f}良好，可持有或逢低增持。"
    elif pb and pb < 1:
        strategy = f"价值股策略：破净（PB{pb:.2f}），如果资产质量可靠可考虑，但需确认无重大风险。"
    else:
        strategy = f"价值股策略：当前估值吸引力一般（PB-ROE得分{pb_roe_score if pb_roe_score else 'N/A'}），建议等待更好买点或寻找其他标的。"
    
    # 8. 风险提示
    risks = [
        "价值陷阱风险：低估值可能是因为基本面恶化，而非被低估",
        "增长停滞风险：业务缺乏增长，长期回报有限",
        "资产质量风险：账面资产可能虚高或难以变现",
        "行业衰退风险：传统行业可能面临长期衰退",
    ]
    
    if pb and pb < 1:
        risks.append("破净风险：虽然便宜，但可能反映资产质量问题或持续亏损预期")
    
    return ValueAnalysisResult(
        code=stock_code,
        name=stock_name,
        roe_assessment=roe_assessment,
        pb_assessment=pb_assessment,
        dividend_assessment=dividend_assessment,
        safety_margin=safety_margin,
        pb_roe_score=pb_roe_score,
        value_analysis=value_analysis,
        valuation_method=f"价值股估值：PB-ROE为核心（ROE{roe if roe else 'N/A'}/PB{pb if pb else 'N/A'}={pb_roe_score if pb_roe_score else 'N/A'}），辅以股息率",
        investment_strategy=strategy,
        risks=risks
    )

def format_value_report(result: ValueAnalysisResult) -> str:
    """格式化价值股分析报告"""
    lines = [
        f"\n{'='*60}",
        f"💎 价值股专项分析: {result.name} ({result.code})",
        f"{'='*60}",
        f"",
        f"【ROE评估】",
        f"   {result.roe_assessment}",
        f"",
        f"【PB评估】",
        f"   {result.pb_assessment}",
        f"",
        f"【股息评估】",
        f"   {result.dividend_assessment}",
        f"",
        f"【估值方法】",
        f"   {result.valuation_method}",
        f"",
        f"【PB-ROE分析】",
    ]
    
    if result.pb_roe_score:
        lines.append(f"   得分：{result.pb_roe_score:.2f}")
    lines.append(f"   {result.value_analysis}")
    
    lines.extend([
        f"",
        f"【安全边际】",
        f"   {result.safety_margin}",
        f"",
        f"【投资策略】",
        f"   {result.investment_strategy}",
        f"",
        f"【风险提示】",
    ])
    
    for i, risk in enumerate(result.risks, 1):
        lines.append(f"   {i}. {risk}")
    
    lines.extend([
        f"",
        f"{'='*60}",
    ])
    
    return "\n".join(lines)

if __name__ == "__main__":
    # 测试
    test_quote = {
        'current': 35.0,
        'pe_ttm': 8.0,
        'pb': 1.2,
    }
    
    result = analyze_value_stock("600036", "招商银行", "银行", test_quote, 
                                historical_pb=1.5, dividend_yield=4.5, payout_ratio=30)
    print(format_value_report(result))
