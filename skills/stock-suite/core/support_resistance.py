"""
支撑阻力分析模块
"""

from typing import Dict, List, Optional

def find_support_resistance(data: List[Dict], lookback: int = 60) -> Dict:
    """寻找支撑位和阻力位"""
    if len(data) < 10:
        return {}
    
    data = data[-lookback:] if len(data) > lookback else data
    
    highs = [d['high'] for d in data]
    lows = [d['low'] for d in data]
    closes = [d['close'] for d in data]
    
    current_price = closes[-1]
    
    resistance_levels = []
    support_levels = []
    
    price_ranges = [
        (max(highs) * 0.95, max(highs)),
        (max(highs) * 0.90, max(highs) * 0.95),
        (max(highs) * 0.85, max(highs) * 0.90),
    ]
    
    for low_range, high_range in price_ranges:
        resistance_prices = [h for h in highs if low_range <= h <= high_range]
        if resistance_prices:
            resistance_levels.append({
                'level': max(resistance_prices),
                'strength': len(resistance_prices),
                'range': f"{low_range:.2f}-{high_range:.2f}"
            })
    
    price_ranges_s = [
        (min(lows), min(lows) * 1.05),
        (min(lows) * 1.05, min(lows) * 1.10),
        (min(lows) * 1.10, min(lows) * 1.15),
    ]
    
    for low_range, high_range in price_ranges_s:
        support_prices = [l for l in lows if low_range <= l <= high_range]
        if support_prices:
            support_levels.append({
                'level': min(support_prices),
                'strength': len(support_prices),
                'range': f"{low_range:.2f}-{high_range:.2f}"
            })
    
    nearest_resistance = None
    for r in resistance_levels:
        if r['level'] > current_price:
            nearest_resistance = r['level']
            break
    
    nearest_support = None
    for s in reversed(support_levels):
        if s['level'] < current_price:
            nearest_support = s['level']
            break
    
    return {
        'current_price': current_price,
        'resistance_levels': resistance_levels,
        'support_levels': support_levels,
        'nearest_resistance': nearest_resistance,
        'nearest_support': nearest_support,
    }

def analyze_support_resistance(data: List[Dict]) -> Dict:
    """分析支撑阻力"""
    return find_support_resistance(data)

def calculate_deviation_from_ma(data: List[Dict], ma_period: int = 20) -> float:
    """计算价格偏离MA的百分比"""
    if len(data) < ma_period:
        return 0.0
    
    closes = [d['close'] for d in data[-ma_period:]]
    ma = sum(closes) / ma_period
    current_price = closes[-1]
    
    deviation = ((current_price - ma) / ma) * 100
    return round(deviation, 2)

def get_trend_direction(data: List[Dict]) -> Dict:
    """判断趋势方向"""
    if len(data) < 20:
        return {'trend': '震荡', 'emoji': '↔️'}
    
    closes = [d['close'] for d in data]
    
    ma5 = sum(closes[-5:]) / 5
    ma10 = sum(closes[-10:]) / 10
    ma20 = sum(closes[-20:]) / 20
    current_price = closes[-1]
    
    if current_price > ma5 > ma10 > ma20:
        return {'trend': '多头', 'emoji': '📈'}
    elif current_price < ma5 < ma10 < ma20:
        return {'trend': '空头', 'emoji': '📉'}
    else:
        return {'trend': '震荡', 'emoji': '↔️'}
