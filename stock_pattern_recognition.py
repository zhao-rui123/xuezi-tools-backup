#!/usr/bin/env python3
"""
股票技术形态识别模块
支持：杯柄形态、头肩底/顶、双底/双顶、三角形整理
"""

import urllib.request
import json
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class PatternResult:
    """形态识别结果"""
    pattern_name: str  # 形态名称
    confidence: float  # 置信度 0-100
    direction: str     # 方向：bullish(看涨)/bearish(看跌)/neutral(中性)
    key_levels: Dict   # 关键价位
    description: str   # 描述
    suggestion: str    # 建议

def fetch_kline_data(stock_code: str, days: int = 120) -> List[Dict]:
    """获取K线数据"""
    try:
        # 判断市场
        if len(stock_code) == 5 and stock_code[0] in '012368':  # 港股
            tencent_code = f"hk{stock_code}"
        elif stock_code.startswith('6') or stock_code.startswith('688'):
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
        
        # 解析K线 [日期, 开盘, 收盘, 最低, 最高, 成交量]
        result = []
        for k in klines:
            if len(k) >= 5:
                result.append({
                    'date': k[0],
                    'open': float(k[1]),
                    'close': float(k[2]),
                    'low': float(k[3]),
                    'high': float(k[4]),
                })
        return result
    except Exception as e:
        print(f"获取K线数据失败 {stock_code}: {e}")
        return []

def detect_cup_handle(closes: List[float], highs: List[float], lows: List[float]) -> Optional[PatternResult]:
    """
    识别杯柄形态
    特征：U型底部（杯）+ 小幅回调（柄）+ 突破
    """
    if len(closes) < 60:
        return None
    
    # 找最近的高点作为参考
    recent_high = max(highs[-60:])
    recent_high_idx = len(highs) - 60 + highs[-60:].index(recent_high)
    
    # 找杯底（U型底部）
    window = closes[recent_high_idx-30:recent_high_idx+10] if recent_high_idx > 30 else closes[:40]
    if len(window) < 30:
        return None
    
    cup_bottom = min(window)
    cup_bottom_idx = closes.index(cup_bottom) if cup_bottom in closes else -1
    
    if cup_bottom_idx < 0:
        return None
    
    # 计算杯深
    cup_depth = (recent_high - cup_bottom) / recent_high
    
    # 杯深应在15%-35%之间
    if not (0.15 <= cup_depth <= 0.50):
        return None
    
    # 找柄部（杯底后的回调）
    handle_start = cup_bottom_idx + 5
    if handle_start >= len(closes) - 5:
        return None
    
    handle_window = closes[handle_start:min(handle_start+20, len(closes))]
    handle_high = max(handle_window)
    handle_low = min(handle_window)
    
    # 柄部回撤应在5%-15%
    handle_retrace = (handle_high - handle_low) / handle_high
    if not (0.03 <= handle_retrace <= 0.20):
        return None
    
    # 当前位置判断
    current = closes[-1]
    breakout_level = recent_high
    
    if current > breakout_level * 0.98:
        status = "🔥 即将突破或已突破"
        confidence = min(90, 70 + (current/breakout_level - 1) * 100)
    elif current > handle_low * 1.02:
        status = "⏳ 柄部整理中"
        confidence = 60
    else:
        status = "❌ 形态已破坏"
        return None
    
    return PatternResult(
        pattern_name="杯柄形态",
        confidence=round(confidence, 1),
        direction="bullish",
        key_levels={
            'cup_bottom': round(cup_bottom, 2),
            'cup_depth': f"{cup_depth*100:.1f}%",
            'handle_retrace': f"{handle_retrace*100:.1f}%",
            'breakout_level': round(breakout_level, 2),
        },
        description=f"U型杯深{cup_depth*100:.1f}%，柄部回撤{handle_retrace*100:.1f}%",
        suggestion=f"{status}，突破位¥{breakout_level:.2f}"
    )

def detect_double_bottom(closes: List[float], lows: List[float]) -> Optional[PatternResult]:
    """
    识别双底形态 (W底)
    """
    if len(closes) < 50:
        return None
    
    # 简化算法：找两个相近的低点
    recent_lows = lows[-50:]
    
    # 找局部低点
    local_mins = []
    for i in range(2, len(recent_lows)-2):
        if recent_lows[i] < recent_lows[i-1] and recent_lows[i] < recent_lows[i+1]:
            local_mins.append((i, recent_lows[i]))
    
    if len(local_mins) < 2:
        return None
    
    # 找两个相近的低点（误差5%以内）
    best_pair = None
    best_diff = float('inf')
    
    for i in range(len(local_mins)):
        for j in range(i+1, len(local_mins)):
            diff = abs(local_mins[i][1] - local_mins[j][1]) / local_mins[i][1]
            if diff < best_diff and diff < 0.05:  # 5%误差
                best_diff = diff
                best_pair = (local_mins[i], local_mins[j])
    
    if not best_pair:
        return None
    
    bottom1, bottom2 = best_pair
    neckline = max(closes[-50:]) * 0.95  # 简化的颈线
    current = closes[-1]
    
    confidence = min(85, 60 + (1 - best_diff) * 100)
    
    if current > neckline * 0.98:
        status = "🔥 已突破颈线或即将突破"
    elif current > bottom2[1] * 1.05:
        status = "⏳ 右底形成中"
    else:
        status = "📉 可能继续探底"
    
    return PatternResult(
        pattern_name="双底形态(W底)",
        confidence=round(confidence, 1),
        direction="bullish",
        key_levels={
            'bottom1': round(bottom1[1], 2),
            'bottom2': round(bottom2[1], 2),
            'neckline': round(neckline, 2),
        },
        description=f"双底误差{best_diff*100:.1f}%，颈线¥{neckline:.2f}",
        suggestion=status
    )

def detect_head_shoulder(closes: List[float], highs: List[float], lows: List[float]) -> Optional[PatternResult]:
    """
    识别头肩底形态
    简化版本
    """
    if len(closes) < 60:
        return None
    
    # 找三个低点：左肩、头、右肩
    recent_lows = lows[-60:]
    
    # 找局部低点
    local_mins = []
    for i in range(3, len(recent_lows)-3):
        if recent_lows[i] < recent_lows[i-1] and recent_lows[i] < recent_lows[i+1]:
            local_mins.append((i, recent_lows[i]))
    
    if len(local_mins) < 3:
        return None
    
    # 找中间最低（头），两边较高（肩）
    for i in range(1, len(local_mins)-1):
        head = local_mins[i]
        left_shoulder = local_mins[i-1]
        right_shoulder = local_mins[i+1]
        
        # 头应该比两肩低
        if head[1] < left_shoulder[1] and head[1] < right_shoulder[1]:
            # 两肩高度相近（10%误差）
            shoulder_diff = abs(left_shoulder[1] - right_shoulder[1]) / left_shoulder[1]
            if shoulder_diff < 0.10:
                neckline = max(highs[-60:]) * 0.95
                current = closes[-1]
                
                confidence = min(80, 60 + (1 - shoulder_diff) * 100)
                
                return PatternResult(
                    pattern_name="头肩底形态",
                    confidence=round(confidence, 1),
                    direction="bullish",
                    key_levels={
                        'left_shoulder': round(left_shoulder[1], 2),
                        'head': round(head[1], 2),
                        'right_shoulder': round(right_shoulder[1], 2),
                        'neckline': round(neckline, 2),
                    },
                    description=f"左肩¥{left_shoulder[1]:.2f}，头¥{head[1]:.2f}，右肩¥{right_shoulder[1]:.2f}",
                    suggestion="🔥 看涨反转形态，关注颈线突破" if current > neckline * 0.98 else "⏳ 观察右肩形成"
                )
    
    return None

def analyze_patterns(stock_code: str, stock_name: str) -> Optional[PatternResult]:
    """
    分析股票技术形态
    返回最可信的形态
    """
    klines = fetch_kline_data(stock_code, days=120)
    if len(klines) < 60:
        return None
    
    closes = [k['close'] for k in klines]
    highs = [k['high'] for k in klines]
    lows = [k['low'] for k in klines]
    
    # 检测各种形态
    patterns = []
    
    cup = detect_cup_handle(closes, highs, lows)
    if cup:
        patterns.append(cup)
    
    double_bottom = detect_double_bottom(closes, lows)
    if double_bottom:
        patterns.append(double_bottom)
    
    hs = detect_head_shoulder(closes, highs, lows)
    if hs:
        patterns.append(hs)
    
    if not patterns:
        return None
    
    # 返回置信度最高的形态
    return max(patterns, key=lambda x: x.confidence)

def format_pattern_report(result: PatternResult) -> str:
    """格式化形态报告"""
    emoji = "📈" if result.direction == "bullish" else "📉" if result.direction == "bearish" else "➖"
    
    lines = [
        f"{emoji} {result.pattern_name} (置信度{result.confidence}%)",
        f"   {result.description}",
        f"   建议: {result.suggestion}",
    ]
    return "\n".join(lines)

if __name__ == "__main__":
    # 测试
    test_codes = [
        ("002460", "赣锋锂业"),
        ("00981", "中芯国际"),
    ]
    
    for code, name in test_codes:
        print(f"\n{'='*50}")
        print(f"分析: {name} ({code})")
        print('='*50)
        
        result = analyze_patterns(code, name)
        if result:
            print(format_pattern_report(result))
        else:
            print("未识别到明显技术形态")
