"""
技术形态识别模块 - 整合版
包含：杯柄形态、双底、头肩底等常见技术形态
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class PatternResult:
    """形态识别结果"""
    pattern_name: str
    confidence: int
    direction: str
    suggestion: str
    target_price: Optional[float] = None

def detect_cup_and_handle(data: List[Dict]) -> Optional[PatternResult]:
    """识别杯柄形态"""
    if len(data) < 60:
        return None
    
    closes = [d['close'] for d in data]
    
    left_high = max(closes[:20])
    right_high = max(closes[-20:])
    
    mid_section = closes[20:len(closes)-20]
    cup_low = min(mid_section)
    
    if left_high < cup_low * 1.3 or right_high < cup_low * 1.3:
        return None
    
    cup_start_idx = closes.index(cup_low)
    
    if cup_start_idx < 15 or cup_start_idx > len(closes) - 25:
        return None
    
    recent = closes[-10:]
    handle_high = max(recent)
    handle_low = min(recent)
    
    if handle_high > cup_low * 1.15:
        return None
    
    current_price = closes[-1]
    target = right_high * 1.1
    
    return PatternResult(
        pattern_name="杯柄形态",
        confidence=75,
        direction="看涨",
        suggestion="经典看涨形态，等待突破后可考虑买入",
        target_price=target
    )

def detect_double_bottom(data: List[Dict]) -> Optional[PatternResult]:
    """识别双底形态（W底）"""
    if len(data) < 40:
        return None
    
    closes = [d['close'] for d in data]
    lows = [d['low'] for d in data]
    
    min_price = min(lows[-40:])
    
    bottom_count = 0
    bottom_prices = []
    
    for i in range(len(lows) - 40, len(lows)):
        if lows[i] < min_price * 1.05:
            bottom_count += 1
            bottom_prices.append(lows[i])
    
    if bottom_count < 2:
        return None
    
    avg_bottom = sum(bottom_prices) / len(bottom_prices)
    
    recent_highs = [d['high'] for d in data[-20:]]
    neckline = max(recent_highs)
    
    current_price = closes[-1]
    
    if current_price > neckline:
        confidence = 85
        suggestion = "已突破颈线，看涨信号明确"
    elif current_price > neckline * 0.95:
        confidence = 70
        suggestion = "接近颈线位置，关注突破信号"
    else:
        confidence = 60
        suggestion = "尚未突破颈线，继续观察"
    
    target = neckline * 1.1
    
    return PatternResult(
        pattern_name="双底形态(W底)",
        confidence=confidence,
        direction="看涨",
        suggestion=suggestion,
        target_price=target
    )

def detect_head_shoulders(data: List[Dict]) -> Optional[PatternResult]:
    """识别头肩底形态"""
    if len(data) < 50:
        return None
    
    closes = [d['close'] for d in data]
    highs = [d['high'] for d in data]
    
    left_shoulder = max(highs[:15])
    head = max(highs[15:35])
    right_shoulder = max(highs[35:])
    
    if head > left_shoulder * 1.1 and head > right_shoulder * 1.1:
        left_shoulder_low = min(closes[:15])
        head_low = min(closes[15:35])
        right_shoulder_low = min(closes[35:])
        
        if abs(left_shoulder_low - right_shoulder_low) / left_shoulder_low < 0.1:
            neckline = min(closes[15:20] + closes[30:35])
            current_price = closes[-1]
            
            if current_price > neckline:
                return PatternResult(
                    pattern_name="头肩底",
                    confidence=75,
                    direction="看涨",
                    suggestion="已突破颈线，看涨信号明确",
                    target_price=head * 1.1
                )
            else:
                return PatternResult(
                    pattern_name="头肩底",
                    confidence=65,
                    direction="看涨",
                    suggestion="等待突破颈线",
                    target_price=head * 1.1
                )
    
    return None

def detect_rising_wedge(data: List[Dict]) -> Optional[PatternResult]:
    """识别上升楔形（看跌）"""
    if len(data) < 30:
        return None
    
    highs = [d['high'] for d in data[-30:]]
    lows = [d['low'] for d in data[-30:]]
    
    high_trend = (highs[-1] - highs[0]) / 30
    low_trend = (lows[-1] - lows[0]) / 30
    
    if high_trend > 0 and low_trend > 0 and high_trend < low_trend:
        return PatternResult(
            pattern_name="上升楔形",
            confidence=65,
            direction="看跌",
            suggestion="警惕冲高回落风险",
            target_price=lows[-1] * 0.95
        )
    
    return None

def detect_falling_wedge(data: List[Dict]) -> Optional[PatternResult]:
    """识别下降楔形（看涨）"""
    if len(data) < 30:
        return None
    
    highs = [d['high'] for d in data[-30:]]
    lows = [d['low'] for d in data[-30:]]
    
    high_trend = (highs[-1] - highs[0]) / 30
    low_trend = (lows[-1] - lows[0]) / 30
    
    if high_trend < 0 and low_trend < 0 and high_trend > low_trend:
        return PatternResult(
            pattern_name="下降楔形",
            confidence=65,
            direction="看涨",
            suggestion="关注企稳反弹机会",
            target_price=highs[-1] * 1.1
        )
    
    return None

def analyze_all_patterns(data: List[Dict]) -> List[Dict]:
    """分析所有技术形态"""
    patterns = []
    
    pattern_funcs = [
        detect_cup_and_handle,
        detect_double_bottom,
        detect_head_shoulders,
        detect_rising_wedge,
        detect_falling_wedge,
    ]
    
    for func in pattern_funcs:
        result = func(data)
        if result:
            patterns.append({
                'pattern': result.pattern_name,
                'confidence': result.confidence,
                'direction': result.direction,
                'suggestion': result.suggestion,
                'target_price': result.target_price,
            })
    
    return patterns

def analyze_patterns(stock_code: str) -> Optional[PatternResult]:
    """分析单只股票的技术形态"""
    try:
        try:
            from core.data_fetcher import fetch_tencent_kline
            data = fetch_tencent_kline(stock_code, 90)
        except:
            try:
                from data_fetcher import fetch_tencent_kline
                data = fetch_tencent_kline(stock_code, 90)
            except:
                data = None
        
        if not data or len(data) < 40:
            return None
        
        patterns = []
        
        cup_result = detect_cup_and_handle(data)
        if cup_result:
            patterns.append(cup_result)
        
        double_result = detect_double_bottom(data)
        if double_result:
            patterns.append(double_result)
        
        hs_result = detect_head_shoulders(data)
        if hs_result:
            patterns.append(hs_result)
        
        if patterns:
            patterns.sort(key=lambda x: x.confidence, reverse=True)
            return patterns[0]
        
        return None
    except Exception as e:
        print(f"形态分析失败: {e}")
        return None

def format_pattern_report(result: PatternResult) -> str:
    """格式化形态分析报告"""
    emoji = "📈" if result.direction == "看涨" else "📉"
    
    lines = [
        f"  形态: {result.pattern_name} {emoji}",
        f"  置信度: {result.confidence}%",
        f"  方向: {result.direction}",
        f"  建议: {result.suggestion}",
    ]
    
    if result.target_price:
        lines.append(f"  目标价: ¥{result.target_price:.2f}")
    
    return "\n".join(lines)
