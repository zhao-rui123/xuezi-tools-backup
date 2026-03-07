#!/usr/bin/env python3
"""
成长股专用分析模块
针对成长股的特殊分析框架：成长空间、PEG估值、竞争优势
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class GrowthAnalysisResult:
    """成长股分析结果"""
    code: str
    name: str
    # 成长指标
    growth_stage: str        # 成长阶段：早期/成长期/成熟期
    growth_score: int        # 成长性评分
    # 估值
    peg: Optional[float]     # PEG比率
    peg_assessment: str      # PEG评估
    # 分析
    growth_analysis: str     # 成长性分析
    competitive_moat: str    # 竞争优势
    valuation_method: str    # 估值方法
    investment_strategy: str # 投资策略
    risks: List[str]         # 风险提示

def analyze_growth_stage(pe: Optional[float], revenue_growth: Optional[float],
                         market_position: str) -> Tuple[str, int]:
    """
    判断成长阶段
    
    Returns:
        (阶段, 评分)
    """
    if pe is None or pe < 0:
        # 亏损期 = 早期或困境
        if revenue_growth and revenue_growth > 30:
            return "早期（亏损扩张）", 75
        else:
            return "早期或困境", 50
    
    if pe > 50:
        # 高PE = 成长期
        if revenue_growth and revenue_growth > 30:
            return "高速成长期", 85
        else:
            return "成长期（增速放缓）", 70
    elif pe > 30:
        # 中等PE = 成长期晚期或成熟期早期
        return "成长期晚期", 65
    elif pe > 15:
        # 较低PE = 成熟期
        return "成熟期", 50
    else:
        # 低PE = 成熟期或价值股
        return "成熟期或转型期", 40

def calculate_peg(pe: float, growth_rate: float) -> Tuple[float, str]:
    """
    计算PEG并评估
    
    Returns:
        (PEG值, 评估)
    """
    if growth_rate <= 0:
        return float('inf'), "增速为负或零，不适用PEG"
    
    peg = pe / growth_rate
    
    if peg < 0.5:
        return peg, f"PEG {peg:.2f} < 0.5，极度低估（难得机会）"
    elif peg < 1:
        return peg, f"PEG {peg:.2f} < 1，低估"
    elif peg < 1.5:
        return peg, f"PEG {peg:.2f}，合理偏低估"
    elif peg < 2:
        return peg, f"PEG {peg:.2f}，合理"
    else:
        return peg, f"PEG {peg:.2f} > 2，高估"

def analyze_competitive_moat(sector: str, pe: float, pb: float) -> str:
    """
    简化版竞争优势分析
    实际应该结合更多基本面数据
    """
    moats = []
    
    # 基于行业的简化判断
    if '半导体' in sector or '芯片' in sector:
        moats.append("技术壁垒（研发投入、专利）")
    elif '软件' in sector or '互联网' in sector:
        moats.append("网络效应或用户粘性")
    elif '品牌' in sector or '消费' in sector:
        moats.append("品牌护城河")
    elif '新能源' in sector or '光伏' in sector:
        moats.append("成本优势或技术领先")
    else:
        moats.append("需要具体分析竞争优势")
    
    # 高PB可能意味着市场认可其护城河
    if pb > 3:
        moats.append(f"高PB({pb:.2f})可能反映市场对其竞争优势的认可")
    
    return "；".join(moats) if moats else "需要深入研究竞争优势"

def analyze_growth_stock(stock_code: str, stock_name: str,
                        sector: str, quote: Dict,
                        estimated_growth: Optional[float] = None) -> GrowthAnalysisResult:
    """
    分析成长股
    
    Args:
        estimated_growth: 预估未来3年盈利复合增速（%），如不提供则基于PE估算
    """
    pe = quote.get('pe_ttm')
    pb = quote.get('pb')
    
    # 1. 判断成长阶段
    # 简化：如果没有提供增速，用ROE或PE反推
    if estimated_growth is None:
        # 简化估算：假设成长股增速与PE相关
        if pe and pe > 0:
            estimated_growth = min(pe * 0.5, 50)  # 简化假设
        else:
            estimated_growth = 20
    
    growth_stage, growth_score = analyze_growth_stage(pe, estimated_growth, "")
    
    # 2. PEG估值
    if pe and pe > 0:
        peg, peg_assessment = calculate_peg(pe, estimated_growth)
    else:
        peg = None
        peg_assessment = "PE为负，不适用PEG，建议用PS或其他方法"
    
    # 3. 成长性分析
    if pe and pe > 0:
        if pe > 50:
            growth_analysis = f"PE高达{pe:.1f}倍，市场预期高增长，需要{estimated_growth:.0f}%以上增速支撑"
        elif pe > 30:
            growth_analysis = f"PE{pe:.1f}倍，市场预期中等增速，约{estimated_growth:.0f}%增速可支撑"
        else:
            growth_analysis = f"PE{pe:.1f}倍，估值相对合理，{estimated_growth:.0f}%增速可提供安全边际"
    else:
        growth_analysis = "当前亏损，处于投入期，需关注收入增速而非盈利"
    
    # 4. 竞争优势
    competitive_moat = analyze_competitive_moat(sector, pe or 0, pb or 0)
    
    # 5. 投资策略
    if peg and peg < 1:
        strategy = f"成长股策略：PEG {peg:.2f} < 1，估值合理或低估。关注公司能否维持{estimated_growth:.0f}%以上增速。"
    elif peg and peg < 2:
        strategy = f"成长股策略：PEG {peg:.2f} 合理，可持有但需警惕增速放缓。关注季度业绩是否超预期。"
    else:
        strategy = f"成长股策略：估值偏高（PEG {peg if peg else 'N/A'}），建议等待回调或确认高增长持续性后再介入。"
    
    # 6. 风险提示
    risks = [
        "增速放缓风险：高增长难以持续，导致估值下杀",
        "估值杀风险：PE从高位回落，股价大幅下跌",
        "竞争加剧风险：行业竞争恶化，市场份额被侵蚀",
        "技术迭代风险：新技术出现导致公司竞争力下降",
    ]
    
    if pe and pe > 80:
        risks.append(f"极高估值风险：PE {pe:.1f}倍，需极高增速支撑，风险较大")
    
    return GrowthAnalysisResult(
        code=stock_code,
        name=stock_name,
        growth_stage=growth_stage,
        growth_score=growth_score,
        peg=peg,
        peg_assessment=peg_assessment,
        growth_analysis=growth_analysis,
        competitive_moat=competitive_moat,
        valuation_method=f"成长股估值：PEG为主（当前PE{pe if pe else 'N/A'}/增速{estimated_growth:.0f}%），辅以PS、远期PE",
        investment_strategy=strategy,
        risks=risks
    )

def format_growth_report(result: GrowthAnalysisResult) -> str:
    """格式化成长股分析报告"""
    lines = [
        f"\n{'='*60}",
        f"🚀 成长股专项分析: {result.name} ({result.code})",
        f"{'='*60}",
        f"",
        f"【成长阶段】{result.growth_stage}",
        f"【成长性评分】{result.growth_score}/100",
        f"",
        f"【成长性分析】",
        f"   {result.growth_analysis}",
        f"",
        f"【估值方法】",
        f"   {result.valuation_method}",
        f"",
        f"【PEG估值】",
        f"   {result.peg_assessment}",
        f"",
        f"【竞争优势】",
        f"   {result.competitive_moat}",
        f"",
        f"【投资策略】",
        f"   {result.investment_strategy}",
        f"",
        f"【风险提示】",
    ]
    
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
        'current': 150.0,
        'pe_ttm': 60.0,
        'pb': 8.0,
    }
    
    result = analyze_growth_stock("300750", "宁德时代", "新能源电池", test_quote, estimated_growth=30)
    print(format_growth_report(result))
