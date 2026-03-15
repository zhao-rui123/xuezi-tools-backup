"""
技术指标模块 - 整合版
包含：MA均线、MACD、KDJ、RSI等技术指标
"""

from typing import Dict, List, Optional
import numpy as np

def calculate_ma(data: List[Dict], periods: List[int] = [5, 10, 20, 60]) -> List[Dict]:
    """计算移动平均线"""
    if len(data) < max(periods):
        return data
    
    closes = [d['close'] for d in data]
    result = []
    
    for i, d in enumerate(data):
        new_d = d.copy()
        for period in periods:
            if i >= period - 1:
                ma_value = sum(closes[i-period+1:i+1]) / period
                new_d[f'ma{period}'] = round(ma_value, 2)
        result.append(new_d)
    
    return result

def calculate_macd(data: List[Dict], fast: int = 12, slow: int = 26, signal: int = 9) -> List[Dict]:
    """计算MACD指标"""
    if len(data) < slow:
        return data
    
    closes = [d['close'] for d in data]
    
    def ema(values: List[float], period: int) -> float:
        if len(values) < period:
            return values[-1] if values else 0
        multiplier = 2 / (period + 1)
        ema_val = values[0]
        for v in values[1:]:
            ema_val = (v - ema_val) * multiplier + ema_val
        return ema_val
    
    result = []
    for i, d in enumerate(data):
        new_d = d.copy()
        if i >= slow - 1:
            ema_fast = ema(closes[:i+1], fast)
            ema_slow = ema(closes[:i+1], slow)
            dif = ema_fast - ema_slow
            
            if i >= slow + signal - 2:
                dif_values = [r.get('macd_dif', 0) for r in result[-signal:]]
                dea = sum(dif_values) / len(dif_values) if dif_values else dif
            else:
                dea = dif
            
            macd = (dif - dea) * 2
            
            new_d['macd_dif'] = round(dif, 4)
            new_d['macd_dea'] = round(dea, 4)
            new_d['macd_hist'] = round(macd, 4)
        
        result.append(new_d)
    
    return result

def calculate_kdj(data: List[Dict], n: int = 9, m1: int = 3, m2: int = 3) -> List[Dict]:
    """计算KDJ指标"""
    if len(data) < n:
        return data
    
    result = []
    k_values = []
    
    for i, d in enumerate(data):
        new_d = d.copy()
        
        if i >= n - 1:
            highs = [d['high'] for d in data[i-n+1:i+1]]
            lows = [d['low'] for d in data[i-n+1:i+1]]
            
            rsv = (d['close'] - min(lows)) / (max(highs) - min(lows)) * 100 if max(highs) > min(lows) else 50
            
            if k_values:
                k = (m1 - 1) / m1 * k_values[-1] + 1 / m1 * rsv
                d_k = (m2 - 1) / m2 * (k_values[-1] if k_values else 50) + 1 / m2 * k
            else:
                k = rsv
                d_k = rsv
            
            j = 3 * k - 2 * d_k
            
            new_d['kdj_k'] = round(k, 2)
            new_d['kdj_d'] = round(d_k, 2)
            new_d['kdj_j'] = round(j, 2)
            k_values.append(k)
        
        result.append(new_d)
    
    return result

def calculate_rsi(data: List[Dict], period: int = 14) -> List[Dict]:
    """计算RSI指标"""
    if len(data) < period + 1:
        return data
    
    closes = [d['close'] for d in data]
    result = []
    
    for i, d in enumerate(data):
        new_d = d.copy()
        
        if i >= period:
            deltas = [closes[j] - closes[j-1] for j in range(i-period+1, i+1)]
            gains = [d if d > 0 else 0 for d in deltas]
            losses = [-d if d < 0 else 0 for d in deltas]
            
            avg_gain = sum(gains) / period
            avg_loss = sum(losses) / period
            
            if avg_loss > 0:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            else:
                rsi = 100
            
            new_d[f'rsi{period}'] = round(rsi, 2)
        
        result.append(new_d)
    
    return result

def calculate_boll(data: List[Dict], period: int = 20) -> List[Dict]:
    """计算布林带指标"""
    if len(data) < period:
        return data
    
    closes = [d['close'] for d in data]
    result = []
    
    for i, d in enumerate(data):
        new_d = d.copy()
        
        if i >= period - 1:
            ma = sum(closes[i-period+1:i+1]) / period
            std = np.std(closes[i-period+1:i+1])
            
            upper = ma + 2 * std
            lower = ma - 2 * std
            
            new_d['boll_mid'] = round(ma, 2)
            new_d['boll_upper'] = round(upper, 2)
            new_d['boll_lower'] = round(lower, 2)
        
        result.append(new_d)
    
    return result

def calculate_all_indicators(data: List[Dict]) -> List[Dict]:
    """计算所有技术指标"""
    data = calculate_ma(data, [5, 10, 20, 60])
    data = calculate_macd(data)
    data = calculate_kdj(data)
    data = calculate_rsi(data, 14)
    data = calculate_boll(data)
    return data

def get_latest_indicators(data: List[Dict]) -> Dict:
    """获取最新的技术指标"""
    if not data:
        return {}
    
    latest = data[-1]
    keys = ['open', 'close', 'high', 'low', 'volume', 'ma5', 'ma10', 'ma20', 'ma60',
            'macd_dif', 'macd_dea', 'macd_hist',
            'kdj_k', 'kdj_d', 'kdj_j',
            'rsi14', 'boll_mid', 'boll_upper', 'boll_lower']
    
    result = {}
    for key in keys:
        if key in latest:
            result[key] = latest[key]
    
    return result

def check_macd_golden_cross(data: List[Dict]) -> bool:
    """检查MACD金叉"""
    if len(data) < 2:
        return False
    
    latest = data[-1]
    prev = data[-2]
    
    if 'macd_dif' not in latest or 'macd_dea' not in latest:
        return False
    
    return latest.get('macd_dif', 0) > latest.get('macd_dea', 0) and \
           prev.get('macd_dif', 0) <= prev.get('macd_dea', 0)

def check_macd_dead_cross(data: List[Dict]) -> bool:
    """检查MACD死叉"""
    if len(data) < 2:
        return False
    
    latest = data[-1]
    prev = data[-2]
    
    if 'macd_dif' not in latest or 'macd_dea' not in latest:
        return False
    
    return latest.get('macd_dif', 0) < latest.get('macd_dea', 0) and \
           prev.get('macd_dif', 0) >= prev.get('macd_dea', 0)

def check_kdj_golden_cross(data: List[Dict]) -> bool:
    """检查KDJ金叉"""
    if len(data) < 2:
        return False
    
    latest = data[-1]
    prev = data[-2]
    
    if 'kdj_k' not in latest or 'kdj_d' not in latest:
        return False
    
    return latest.get('kdj_k', 0) > latest.get('kdj_d', 0) and \
           prev.get('kdj_k', 0) <= prev.get('kdj_d', 0)

def check_kdj_dead_cross(data: List[Dict]) -> bool:
    """检查KDJ死叉"""
    if len(data) < 2:
        return False
    
    latest = data[-1]
    prev = data[-2]
    
    if 'kdj_k' not in latest or 'kdj_d' not in latest:
        return False
    
    return latest.get('kdj_k', 0) < latest.get('kdj_d', 0) and \
           prev.get('kdj_k', 0) >= prev.get('kdj_d', 0)

def check_ma_alignment(data: List[Dict]) -> bool:
    """检查均线多头排列"""
    if len(data) < 3:
        return False
    
    latest = data[-1]
    
    ma5 = latest.get('ma5', 0)
    ma10 = latest.get('ma10', 0)
    ma20 = latest.get('ma20', 0)
    
    return ma5 > ma10 > ma20 > 0

def check_volume_increase(data: List[Dict], periods: int = 5) -> bool:
    """检查成交量是否放大"""
    if len(data) < periods + 1:
        return False
    
    recent_volumes = [d.get('volume', 0) for d in data[-periods:]]
    prev_volume = data[-(periods+1)].get('volume', 0)
    
    avg_recent = sum(recent_volumes) / periods
    
    return avg_recent > prev_volume * 1.2

def get_all_signals(data: List[Dict]) -> Dict:
    """获取所有技术信号"""
    if not data:
        return {}
    
    latest = data[-1]
    
    signals = {
        'macd_golden_cross': check_macd_golden_cross(data),
        'macd_dead_cross': check_macd_dead_cross(data),
        'kdj_golden_cross': check_kdj_golden_cross(data),
        'kdj_dead_cross': check_kdj_dead_cross(data),
        'ma_alignment': check_ma_alignment(data),
        'volume_increase': check_volume_increase(data),
    }
    
    if latest.get('rsi14', 50) > 80:
        signals['rsi_overbought'] = True
    elif latest.get('rsi14', 50) < 20:
        signals['rsi_oversold'] = True
    
    return signals
