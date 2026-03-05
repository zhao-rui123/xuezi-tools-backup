"""
支撑压力位与趋势线分析模块
"""
import pandas as pd
import numpy as np
from scipy import stats


def find_support_resistance(data, window=10, tolerance=0.02):
    """
    寻找支撑压力位
    
    Args:
        window: 窗口大小
        tolerance: 价格差异容忍度
    
    Returns:
        dict: 支撑压力位信息
    """
    if len(data) < window * 2:
        return {'supports': [], 'resistances': []}
    
    highs = data['high'].values
    lows = data['low'].values
    closes = data['close'].values
    current_price = closes[-1]
    
    # 找局部高点（压力位候选）
    resistances = []
    for i in range(window, len(highs) - window):
        if highs[i] == max(highs[i-window:i+window+1]):
            resistances.append(highs[i])
    
    # 找局部低点（支撑位候选）
    supports = []
    for i in range(window, len(lows) - window):
        if lows[i] == min(lows[i-window:i+window+1]):
            supports.append(lows[i])
    
    # 合并相近的价格水平
    def merge_levels(levels, tolerance):
        if not levels:
            return []
        levels = sorted(levels, reverse=True)
        merged = []
        current_group = [levels[0]]
        
        for price in levels[1:]:
            if abs(price - current_group[0]) / current_group[0] <= tolerance:
                current_group.append(price)
            else:
                merged.append(np.mean(current_group))
                current_group = [price]
        
        merged.append(np.mean(current_group))
        return merged
    
    supports = merge_levels(supports, tolerance)
    resistances = merge_levels(resistances, tolerance)
    
    # 过滤掉过期的水平（距离当前价格太远）
    valid_range = 0.3  # 30%范围
    supports = [s for s in supports if s > current_price * (1 - valid_range)]
    resistances = [r for r in resistances if r < current_price * (1 + valid_range)]
    
    # 找出最重要的支撑压力位（最接近当前价格的）
    nearest_support = max([s for s in supports if s < current_price], default=None)
    nearest_resistance = min([r for r in resistances if r > current_price], default=None)
    
    return {
        'supports': [{'price': round(s, 2), 'distance': round((current_price - s) / current_price * 100, 2)} for s in supports[:3]],
        'resistances': [{'price': round(r, 2), 'distance': round((r - current_price) / current_price * 100, 2)} for r in resistances[:3]],
        'nearest_support': round(nearest_support, 2) if nearest_support else None,
        'nearest_resistance': round(nearest_resistance, 2) if nearest_resistance else None,
        'current_price': round(current_price, 2)
    }


def calculate_trend_lines(data):
    """
    计算趋势线
    
    Returns:
        dict: 趋势线信息
    """
    if len(data) < 20:
        return {}
    
    closes = data['close'].values
    x = np.arange(len(closes))
    
    # 短期趋势（最近20根）
    short_term = closes[-20:]
    x_short = np.arange(20)
    slope_short, intercept_short, r_value_short, _, _ = stats.linregress(x_short, short_term)
    
    # 中期趋势（最近60根）
    if len(closes) >= 60:
        mid_term = closes[-60:]
        x_mid = np.arange(60)
        slope_mid, intercept_mid, r_value_mid, _, _ = stats.linregress(x_mid, mid_term)
    else:
        slope_mid, intercept_mid, r_value_mid = slope_short, intercept_short, r_value_short
    
    # 长期趋势（全部）
    slope_long, intercept_long, r_value_long, _, _ = stats.linregress(x, closes)
    
    def get_trend_strength(r_value, slope):
        """判断趋势强度"""
        if abs(r_value) < 0.3:
            return '无趋势'
        elif slope > 0:
            return '上升趋势' if r_value > 0.7 else '弱上升'
        else:
            return '下降趋势' if r_value > 0.7 else '弱下降'
    
    def get_trend_angle(slope, avg_price):
        """计算趋势角度"""
        angle = np.degrees(np.arctan(slope / avg_price * 100))
        return round(angle, 2)
    
    avg_price = np.mean(closes)
    
    return {
        'short_term': {
            'slope': round(slope_short, 4),
            'angle': get_trend_angle(slope_short, avg_price),
            'strength': abs(r_value_short),
            'trend': get_trend_strength(r_value_short, slope_short)
        },
        'mid_term': {
            'slope': round(slope_mid, 4),
            'angle': get_trend_angle(slope_mid, avg_price),
            'strength': abs(r_value_mid),
            'trend': get_trend_strength(r_value_mid, slope_mid)
        },
        'long_term': {
            'slope': round(slope_long, 4),
            'angle': get_trend_angle(slope_long, avg_price),
            'strength': abs(r_value_long),
            'trend': get_trend_strength(r_value_long, slope_long)
        }
    }


def calculate_pivot_points(data):
    """
    计算枢轴点（Pivot Points）
    
    Returns:
        dict: 枢轴点及支撑压力位
    """
    if len(data) < 2:
        return {}
    
    last = data.iloc[-1]
    prev = data.iloc[-2]
    
    high = prev['high']
    low = prev['low']
    close = prev['close']
    
    # 经典枢轴点
    pivot = (high + low + close) / 3
    
    # 支撑位
    s1 = 2 * pivot - high
    s2 = pivot - (high - low)
    s3 = low - 2 * (high - pivot)
    
    # 压力位
    r1 = 2 * pivot - low
    r2 = pivot + (high - low)
    r3 = high + 2 * (pivot - low)
    
    current = last['close']
    
    return {
        'pivot': round(pivot, 2),
        'supports': [
            {'level': 'S1', 'price': round(s1, 2), 'distance': round((current - s1) / current * 100, 2)},
            {'level': 'S2', 'price': round(s2, 2), 'distance': round((current - s2) / current * 100, 2)},
            {'level': 'S3', 'price': round(s3, 2), 'distance': round((current - s3) / current * 100, 2)}
        ],
        'resistances': [
            {'level': 'R1', 'price': round(r1, 2), 'distance': round((r1 - current) / current * 100, 2)},
            {'level': 'R2', 'price': round(r2, 2), 'distance': round((r2 - current) / current * 100, 2)},
            {'level': 'R3', 'price': round(r3, 2), 'distance': round((r3 - current) / current * 100, 2)}
        ]
    }


def calculate_fibonacci_levels(data):
    """
    计算斐波那契回撤位
    
    Returns:
        dict: 斐波那契回撤位
    """
    if len(data) < 20:
        return {}
    
    recent = data.tail(60)  # 最近60根
    high = recent['high'].max()
    low = recent['low'].min()
    current = data['close'].iloc[-1]
    
    diff = high - low
    
    levels = {
        '0%': high,
        '23.6%': high - 0.236 * diff,
        '38.2%': high - 0.382 * diff,
        '50%': high - 0.5 * diff,
        '61.8%': high - 0.618 * diff,
        '78.6%': high - 0.786 * diff,
        '100%': low
    }
    
    # 找出当前价格所在的区间
    current_zone = None
    sorted_levels = sorted(levels.items(), key=lambda x: x[1], reverse=True)
    for i in range(len(sorted_levels) - 1):
        if sorted_levels[i+1][1] <= current <= sorted_levels[i][1]:
            current_zone = f"{sorted_levels[i][0]} - {sorted_levels[i+1][0]}"
            break
    
    return {
        'levels': {k: round(v, 2) for k, v in levels.items()},
        'current_zone': current_zone,
        'high': round(high, 2),
        'low': round(low, 2)
    }


def analyze_support_resistance(data):
    """
    完整的支撑压力分析
    
    Returns:
        dict: 完整的支撑压力信息
    """
    sr_levels = find_support_resistance(data)
    trend_lines = calculate_trend_lines(data)
    pivot_points = calculate_pivot_points(data)
    fibonacci = calculate_fibonacci_levels(data)
    
    # 生成交易建议
    current_price = data['close'].iloc[-1]
    suggestions = []
    
    # 基于最近支撑压力的建议
    if sr_levels['nearest_support']:
        distance = (current_price - sr_levels['nearest_support']) / current_price * 100
        if distance < 3:
            suggestions.append({
                'type': '买入机会',
                'reason': f'价格接近支撑位 ¥{sr_levels["nearest_support"]}，距离仅{distance:.1f}%',
                'priority': '高'
            })
    
    if sr_levels['nearest_resistance']:
        distance = (sr_levels['nearest_resistance'] - current_price) / current_price * 100
        if distance < 3:
            suggestions.append({
                'type': '卖出机会',
                'reason': f'价格接近压力位 ¥{sr_levels["nearest_resistance"]}，距离仅{distance:.1f}%',
                'priority': '高'
            })
    
    # 基于趋势的建议
    if trend_lines.get('short_term'):
        short_trend = trend_lines['short_term']
        if short_trend['trend'] == '上升趋势' and short_trend['strength'] > 0.8:
            suggestions.append({
                'type': '趋势跟随',
                'reason': '短期上升趋势强劲，支撑位可能有效',
                'priority': '中'
            })
        elif short_trend['trend'] == '下降趋势' and short_trend['strength'] > 0.8:
            suggestions.append({
                'type': '风险提示',
                'reason': '短期下降趋势强劲，压力位可能有效',
                'priority': '中'
            })
    
    return {
        'support_resistance_levels': sr_levels,
        'trend_lines': trend_lines,
        'pivot_points': pivot_points,
        'fibonacci': fibonacci,
        'suggestions': suggestions
    }