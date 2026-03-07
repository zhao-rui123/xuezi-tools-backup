#!/usr/bin/env python3
"""
周期股专用分析模块
针对周期股的特殊分析框架：周期位置判断、供需分析、正确估值方法
"""

import urllib.request
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class CyclicalAnalysisResult:
    """周期股分析结果"""
    code: str
    name: str
    # 周期位置
    cycle_position: str      # 底部/复苏/上升/顶部/下降
    cycle_confidence: int    # 判断置信度
    # 估值（周期股方法）
    pb_assessment: str       # PB评估
    pb_percentile: Optional[float]  # PB历史分位
    resource_value: Optional[str]   # 资源量估值
    # 分析
    cycle_analysis: str      # 周期分析
    valuation_method: str    # 估值方法说明
    investment_strategy: str # 投资策略
    risks: List[str]         # 风险提示

def is_hk_stock(code: str) -> bool:
    return len(code) == 5 and code[0] in '012368'

def fetch_kline_for_pb_history(stock_code: str, days: int = 500) -> List[Dict]:
    """获取历史K线数据（用于计算PB分位）"""
    try:
        if is_hk_stock(stock_code):
            tencent_code = f"hk{stock_code}"
        elif stock_code.startswith('6'):
            tencent_code = f"sh{stock_code}"
        else:
            tencent_code = f"sz{stock_code}"
        
        url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={tencent_code},day,,,{days},qfq"
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        if tencent_code not in data.get('data', {}):
            return []
        
        stock_data = data['data'][tencent_code]
        klines = stock_data.get('qfqday', []) or stock_data.get('day', [])
        
        result = []
        for k in klines:
            if len(k) >= 5:
                result.append({
                    'date': k[0],
                    'close': float(k[2]),
                })
        return result
    except Exception as e:
        print(f"获取历史数据失败 {stock_code}: {e}")
        return []

def analyze_cycle_position(stock_code: str, stock_name: str, 
                          pe: Optional[float], pb: Optional[float],
                          current: Optional[float], high52w: Optional[float], 
                          low52w: Optional[float]) -> Tuple[str, int, str]:
    """
    分析周期位置
    基于PE、PB、价格位置综合判断
    
    Returns:
        (周期位置, 置信度, 分析说明)
    """
    # 默认未知
    position = "不明"
    confidence = 50
    analysis = "数据不足，无法判断周期位置"
    
    # 周期股特征：PE低时可能是顶部，PE高时可能是底部（盈利波动导致）
    # 所以用PB和价格位置更可靠
    
    scores = []
    reasons = []
    
    # 1. 基于PE的判断（反向指标）
    if pe is not None:
        if pe < 0:
            # 亏损，可能是周期底部或顶部
            scores.append(("可能底部或顶部", 40))
            reasons.append("当前亏损（PE为负），可能是周期底部（价格低迷）或周期顶部刚转亏损")
        elif pe < 10:
            scores.append(("可能顶部", 60))
            reasons.append(f"PE仅{pe:.1f}倍，极低，可能是周期顶部盈利高峰")
        elif pe > 50:
            scores.append(("可能底部", 60))
            reasons.append(f"PE高达{pe:.1f}倍，极高，可能是周期底部亏损或微利")
        else:
            scores.append(("中部区域", 50))
            reasons.append(f"PE{pe:.1f}倍，处于中等水平")
    
    # 2. 基于PB的判断（更可靠）
    if pb is not None:
        # 需要历史PB分位，这里简化处理
        if pb < 1.5:
            scores.append(("可能底部", 70))
            reasons.append(f"PB仅{pb:.2f}倍，较低，可能处于估值底部")
        elif pb > 4:
            scores.append(("可能顶部", 70))
            reasons.append(f"PB高达{pb:.2f}倍，较高，可能处于估值顶部")
        else:
            scores.append(("中部区域", 50))
            reasons.append(f"PB{pb:.2f}倍，处于中等水平")
    
    # 3. 基于52周价格位置
    if all([current, high52w, low52w]) and high52w > low52w:
        price_pos = (current - low52w) / (high52w - low52w)
        if price_pos < 0.3:
            scores.append(("可能底部", 65))
            reasons.append(f"价格处于52周{price_pos*100:.0f}%低位，可能是周期底部")
        elif price_pos > 0.8:
            scores.append(("可能顶部", 65))
            reasons.append(f"价格处于52周{price_pos*100:.0f}%高位，可能是周期顶部")
        else:
            scores.append(("中部震荡", 50))
            reasons.append(f"价格处于52周{price_pos*100:.0f}%中位")
    
    # 综合判断
    if not scores:
        return position, confidence, analysis
    
    # 统计各位置出现次数
    from collections import Counter
    positions = [s[0] for s in scores]
    position_counts = Counter(positions)
    most_common = position_counts.most_common(1)[0]
    
    position = most_common[0]
    # 置信度基于一致性
    consistency = most_common[1] / len(positions)
    avg_confidence = sum(s[1] for s in scores) / len(scores)
    confidence = int(avg_confidence * (0.5 + 0.5 * consistency))
    
    analysis = "；".join(reasons)
    
    return position, confidence, analysis

def get_lithium_industry_outlook() -> str:
    """
    锂矿行业周期前景分析
    基于公开信息的行业判断
    """
    # 这是一个简化版本，实际应该接入行业数据API
    outlook = """
【锂矿行业周期分析】

1. 供给端：
   - 澳洲矿山：Greenbushes、Pilbara等扩产，2024-2025年产能大量释放
   - 南美盐湖：智利、阿根廷项目投产中
   - 非洲矿山：津巴布韦、马里等新产能
   - 中国盐湖：青海、西藏开发加速
   
2. 需求端：
   - 新能源车：增速放缓但仍保持增长
   - 储能：增速较快但基数较小
   - 消费电子：平稳
   
3. 价格判断：
   - 2024年碳酸锂价格从60万→10万，已大幅下跌
   - 当前价格（假设15万）可能接近或略高于成本支撑
   - 2025-2026年：取决于新能源车增速vs产能释放速度
   
4. 周期位置判断：
   - 可能处于：下降期末期→底部震荡期
   - 关注信号：价格企稳、产能出清、库存去化
    """
    return outlook

def analyze_cyclical_stock(stock_code: str, stock_name: str, 
                          sector: str, quote: Dict) -> CyclicalAnalysisResult:
    """
    分析周期股
    """
    pe = quote.get('pe_ttm')
    pb = quote.get('pb')
    current = quote.get('current')
    high52w = quote.get('high52w')
    low52w = quote.get('low52w')
    market_cap = quote.get('market_cap')
    
    # 1. 周期位置判断
    position, confidence, cycle_analysis = analyze_cycle_position(
        stock_code, stock_name, pe, pb, current, high52w, low52w
    )
    
    # 2. PB评估（周期股核心估值指标）
    if pb:
        if pb < 1.5:
            pb_assessment = f"PB {pb:.2f}倍，较低，估值有安全边际"
        elif pb < 3:
            pb_assessment = f"PB {pb:.2f}倍，中等，估值合理"
        else:
            pb_assessment = f"PB {pb:.2f}倍，较高，估值偏贵"
    else:
        pb_assessment = "PB数据缺失"
    
    # 简化计算PB分位（基于52周价格估算）
    pb_percentile = None
    if all([current, high52w, low52w]) and high52w > low52w:
        # 简化假设：价格分位≈PB分位
        pb_percentile = (current - low52w) / (high52w - low52w) * 100
    
    # 3. 资源量估值（如果是资源型企业）
    resource_value = None
    if '锂' in sector or '矿' in sector:
        resource_value = "需要公司资源储量数据计算"
    
    # 4. 投资策略
    if "底部" in position:
        strategy = "周期股策略：可能处于周期底部区域，可考虑分批左侧布局。但需要确认：1)价格是否企稳；2)产能是否开始出清；3)需求是否有改善迹象。"
    elif "顶部" in position:
        strategy = "周期股策略：可能处于周期顶部区域，应考虑减仓。即使PE看起来很低（盈利高峰），也要警惕周期下行风险。"
    else:
        strategy = "周期股策略：周期位置不明或处于中部，建议观望。等待周期方向明确后再做决策。"
    
    # 5. 风险提示
    risks = [
        "周期判断错误风险：周期位置判断可能错误，实际周期方向与预期相反",
        "产品价格暴跌风险：大宗商品价格波动大，可能大幅下跌",
        "产能过剩风险：行业产能扩张过快，导致价格战",
        "需求下滑风险：下游需求不及预期",
    ]
    
    if "锂" in sector:
        risks.append("碳酸锂价格特别风险：锂价波动极大，2023-2024年已从60万跌至10万")
    
    return CyclicalAnalysisResult(
        code=stock_code,
        name=stock_name,
        cycle_position=position,
        cycle_confidence=confidence,
        pb_assessment=pb_assessment,
        pb_percentile=pb_percentile,
        resource_value=resource_value,
        cycle_analysis=cycle_analysis,
        valuation_method="周期股估值：不看PE，看PB、EV/产能、资源量估值、重置成本",
        investment_strategy=strategy,
        risks=risks
    )

def format_cyclical_report(result: CyclicalAnalysisResult) -> str:
    """格式化周期股分析报告"""
    lines = [
        f"\n{'='*60}",
        f"🔶 周期股专项分析: {result.name} ({result.code})",
        f"{'='*60}",
        f"",
        f"【周期位置判断】{result.cycle_position} (置信度{result.cycle_confidence}%)",
        f"",
        f"周期分析：",
        f"   {result.cycle_analysis}",
        f"",
        f"【估值方法】",
        f"   {result.valuation_method}",
        f"",
        f"【PB评估】",
        f"   {result.pb_assessment}",
    ]
    
    if result.pb_percentile:
        lines.append(f"   估算PB分位: {result.pb_percentile:.0f}%")
    
    if result.resource_value:
        lines.extend([
            f"",
            f"【资源量估值】",
            f"   {result.resource_value}",
        ])
    
    # 行业前景（如果是锂矿）
    if '锂' in result.name or '矿' in result.name:
        lines.extend([
            f"",
            get_lithium_industry_outlook(),
        ])
    
    lines.extend([
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
        'current': 79.07,
        'pe_ttm': 137.3,
        'pb': 4.75,
        'high52w': 100.86,
        'low52w': 26.62,
    }
    
    result = analyze_cyclical_stock("002738", "中矿资源", "锂矿/资源", test_quote)
    print(format_cyclical_report(result))
