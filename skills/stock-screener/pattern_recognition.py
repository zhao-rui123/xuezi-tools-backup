"""
K线形态识别模块
"""
import pandas as pd
import numpy as np


def detect_double_top(data, tolerance=0.03):
    """
    检测双头顶部形态
    
    Args:
        tolerance: 价格差异容忍度（3%）
    
    Returns:
        dict: 双头检测结果
    """
    if len(data) < 20:
        return {'detected': False}
    
    # 找近期高点
    highs = data['high'].values
    
    # 找两个相近的高点
    recent_highs = []
    for i in range(5, len(highs) - 5):
        if highs[i] > highs[i-1] and highs[i] > highs[i-2] and \
           highs[i] > highs[i+1] and highs[i] > highs[i+2]:
            recent_highs.append((i, highs[i]))
    
    if len(recent_highs) < 2:
        return {'detected': False}
    
    # 检查最近两个高点是否形成双头
    for i in range(len(recent_highs) - 1):
        for j in range(i + 1, len(recent_highs)):
            idx1, high1 = recent_highs[i]
            idx2, high2 = recent_highs[j]
            
            # 检查价格是否相近
            price_diff = abs(high1 - high2) / high1
            
            if price_diff <= tolerance:
                # 检查中间是否有明显下跌
                middle_low = data['low'].iloc[idx1:idx2].min()
                neckline = middle_low
                
                return {
                    'detected': True,
                    'pattern': '双头顶部',
                    'first_peak': {'index': idx1, 'price': round(high1, 2)},
                    'second_peak': {'index': idx2, 'price': round(high2, 2)},
                    'neckline': round(neckline, 2),
                    'target_price': round(neckline - (high1 - neckline), 2),
                    'signal': '看跌'
                }
    
    return {'detected': False}


def detect_double_bottom(data, tolerance=0.03):
    """
    检测双底形态
    
    Returns:
        dict: 双底检测结果
    """
    if len(data) < 20:
        return {'detected': False}
    
    lows = data['low'].values
    
    # 找近期低点
    recent_lows = []
    for i in range(5, len(lows) - 5):
        if lows[i] < lows[i-1] and lows[i] < lows[i-2] and \
           lows[i] < lows[i+1] and lows[i] < lows[i+2]:
            recent_lows.append((i, lows[i]))
    
    if len(recent_lows) < 2:
        return {'detected': False}
    
    # 检查最近两个低点是否形成双底
    for i in range(len(recent_lows) - 1):
        for j in range(i + 1, len(recent_lows)):
            idx1, low1 = recent_lows[i]
            idx2, low2 = recent_lows[j]
            
            price_diff = abs(low1 - low2) / low1
            
            if price_diff <= tolerance:
                middle_high = data['high'].iloc[idx1:idx2].max()
                neckline = middle_high
                
                return {
                    'detected': True,
                    'pattern': '双底形态',
                    'first_bottom': {'index': idx1, 'price': round(low1, 2)},
                    'second_bottom': {'index': idx2, 'price': round(low2, 2)},
                    'neckline': round(neckline, 2),
                    'target_price': round(neckline + (neckline - low1), 2),
                    'signal': '看涨'
                }
    
    return {'detected': False}


def detect_head_and_shoulders(data, tolerance=0.03):
    """
    检测头肩顶形态
    
    Returns:
        dict: 头肩顶检测结果
    """
    if len(data) < 30:
        return {'detected': False}
    
    highs = data['high'].values
    
    # 找三个高点
    recent_highs = []
    for i in range(3, len(highs) - 3):
        if highs[i] > highs[i-1] and highs[i] > highs[i-2] and \
           highs[i] > highs[i+1] and highs[i] > highs[i+2]:
            recent_highs.append((i, highs[i]))
    
    if len(recent_highs) < 3:
        return {'detected': False}
    
    # 检查头肩形态
    for i in range(len(recent_highs) - 2):
        left_idx, left_shoulder = recent_highs[i]
        head_idx, head = recent_highs[i + 1]
        right_idx, right_shoulder = recent_highs[i + 2]
        
        # 头部必须高于两肩
        if head > left_shoulder and head > right_shoulder:
            # 两肩高度相近
            shoulder_diff = abs(left_shoulder - right_shoulder) / left_shoulder
            
            if shoulder_diff <= tolerance * 2:
                # 计算颈线
                neckline = min(
                    data['low'].iloc[left_idx:head_idx].min(),
                    data['low'].iloc[head_idx:right_idx].min()
                )
                
                return {
                    'detected': True,
                    'pattern': '头肩顶',
                    'left_shoulder': round(left_shoulder, 2),
                    'head': round(head, 2),
                    'right_shoulder': round(right_shoulder, 2),
                    'neckline': round(neckline, 2),
                    'target_price': round(neckline - (head - neckline), 2),
                    'signal': '强烈看跌'
                }
    
    return {'detected': False}


def detect_inverse_head_and_shoulders(data, tolerance=0.03):
    """
    检测头肩底形态
    
    Returns:
        dict: 头肩底检测结果
    """
    if len(data) < 30:
        return {'detected': False}
    
    lows = data['low'].values
    
    # 找三个低点
    recent_lows = []
    for i in range(3, len(lows) - 3):
        if lows[i] < lows[i-1] and lows[i] < lows[i-2] and \
           lows[i] < lows[i+1] and lows[i] < lows[i+2]:
            recent_lows.append((i, lows[i]))
    
    if len(recent_lows) < 3:
        return {'detected': False}
    
    # 检查头肩底形态
    for i in range(len(recent_lows) - 2):
        left_idx, left_shoulder = recent_lows[i]
        head_idx, head = recent_lows[i + 1]
        right_idx, right_shoulder = recent_lows[i + 2]
        
        # 头部必须低于两肩
        if head < left_shoulder and head < right_shoulder:
            shoulder_diff = abs(left_shoulder - right_shoulder) / left_shoulder
            
            if shoulder_diff <= tolerance * 2:
                neckline = max(
                    data['high'].iloc[left_idx:head_idx].max(),
                    data['high'].iloc[head_idx:right_idx].max()
                )
                
                return {
                    'detected': True,
                    'pattern': '头肩底',
                    'left_shoulder': round(left_shoulder, 2),
                    'head': round(head, 2),
                    'right_shoulder': round(right_shoulder, 2),
                    'neckline': round(neckline, 2),
                    'target_price': round(neckline + (neckline - head), 2),
                    'signal': '强烈看涨'
                }
    
    return {'detected': False}


def detect_triangle(data):
    """
    检测三角形整理形态
    
    Returns:
        dict: 三角形检测结果
    """
    if len(data) < 15:
        return {'detected': False}
    
    recent = data.tail(15)
    highs = recent['high'].values
    lows = recent['low'].values
    
    # 计算趋势线
    x = np.arange(len(highs))
    
    # 上轨趋势线（下降）
    high_slope = np.polyfit(x, highs, 1)[0]
    # 下轨趋势线（上升）
    low_slope = np.polyfit(x, lows, 1)[0]
    
    # 对称三角形：上轨下降，下轨上升
    if high_slope < -0.001 and low_slope > 0.001:
        return {
            'detected': True,
            'pattern': '对称三角形',
            'description': '上轨下降，下轨上升，即将选择方向',
            'signal': '观望，等待突破'
        }
    
    # 上升三角形：上轨水平，下轨上升
    if abs(high_slope) < 0.001 and low_slope > 0.001:
        return {
            'detected': True,
            'pattern': '上升三角形',
            'description': '上轨水平，下轨上升，看涨形态',
            'signal': '看涨'
        }
    
    # 下降三角形：上轨下降，下轨水平
    if high_slope < -0.001 and abs(low_slope) < 0.001:
        return {
            'detected': True,
            'pattern': '下降三角形',
            'description': '上轨下降，下轨水平，看跌形态',
            'signal': '看跌'
        }
    
    return {'detected': False}


def analyze_all_patterns(data):
    """
    分析所有K线形态
    
    Returns:
        list: 检测到的形态列表
    """
    patterns = []
    
    # 双头顶部
    double_top = detect_double_top(data)
    if double_top['detected']:
        patterns.append(double_top)
    
    # 双底
    double_bottom = detect_double_bottom(data)
    if double_bottom['detected']:
        patterns.append(double_bottom)
    
    # 头肩顶
    hns = detect_head_and_shoulders(data)
    if hns['detected']:
        patterns.append(hns)
    
    # 头肩底
    inverse_hns = detect_inverse_head_and_shoulders(data)
    if inverse_hns['detected']:
        patterns.append(inverse_hns)
    
    # 三角形
    triangle = detect_triangle(data)
    if triangle['detected']:
        patterns.append(triangle)
    
    return patterns