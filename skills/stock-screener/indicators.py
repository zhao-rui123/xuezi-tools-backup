"""
技术指标计算模块
"""
import pandas as pd
import numpy as np
import config


def calculate_ma(data, periods):
    """
    计算移动平均线
    
    Args:
        data: DataFrame with 'close' column
        periods: list of periods, e.g., [5, 10, 20]
    
    Returns:
        DataFrame with MA columns
    """
    for period in periods:
        data[f'MA{period}'] = data['close'].rolling(window=period).mean()
    return data


def calculate_macd(data, fast=config.MACD_FAST, slow=config.MACD_SLOW, signal=config.MACD_SIGNAL):
    """
    计算MACD指标
    
    Args:
        data: DataFrame with 'close' column
        fast, slow, signal: MACD参数
    
    Returns:
        DataFrame with MACD columns
    """
    ema_fast = data['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = data['close'].ewm(span=slow, adjust=False).mean()
    
    data['MACD_DIF'] = ema_fast - ema_slow
    data['MACD_DEA'] = data['MACD_DIF'].ewm(span=signal, adjust=False).mean()
    data['MACD_HIST'] = 2 * (data['MACD_DIF'] - data['MACD_DEA'])
    
    return data


def calculate_kdj(data, n=config.KDJ_N, m1=config.KDJ_M1, m2=config.KDJ_M2):
    """
    计算KDJ指标
    
    Args:
        data: DataFrame with 'high', 'low', 'close' columns
        n, m1, m2: KDJ参数
    
    Returns:
        DataFrame with KDJ columns
    """
    low_list = data['low'].rolling(window=n, min_periods=n).min()
    high_list = data['high'].rolling(window=n, min_periods=n).max()
    
    rsv = (data['close'] - low_list) / (high_list - low_list) * 100
    
    data['KDJ_K'] = rsv.ewm(alpha=1/m1, adjust=False).mean()
    data['KDJ_D'] = data['KDJ_K'].ewm(alpha=1/m2, adjust=False).mean()
    data['KDJ_J'] = 3 * data['KDJ_K'] - 2 * data['KDJ_D']
    
    return data


def check_macd_golden_cross(data):
    """
    检查MACD金叉
    
    Returns:
        bool: 最新一个月是否金叉
    """
    if len(data) < 2:
        return False
    
    # 当月DIF > DEA 且 上月DIF <= 上月DEA
    current_cross = data['MACD_DIF'].iloc[-1] > data['MACD_DEA'].iloc[-1]
    prev_cross = data['MACD_DIF'].iloc[-2] <= data['MACD_DEA'].iloc[-2]
    
    return current_cross and prev_cross


def check_kdj_golden_cross(data, buy_zone=config.KDJ_BUY_ZONE):
    """
    检查KDJ金叉且在买入区域
    
    Args:
        buy_zone: K值上限，默认50
    
    Returns:
        bool: 是否满足条件
    """
    if len(data) < 2:
        return False
    
    # 当月K > D 且 上月K <= 上月D
    current_cross = data['KDJ_K'].iloc[-1] > data['KDJ_D'].iloc[-1]
    prev_cross = data['KDJ_K'].iloc[-2] <= data['KDJ_D'].iloc[-2]
    
    # K值在买入区域
    in_zone = data['KDJ_K'].iloc[-1] < buy_zone
    
    return current_cross and prev_cross and in_zone


def check_ma_alignment(data):
    """
    检查均线多头排列
    
    Returns:
        bool: 5月 > 10月 > 20月
    """
    if len(data) < 1:
        return False
    
    ma5 = data['MA5'].iloc[-1]
    ma10 = data['MA10'].iloc[-1]
    ma20 = data['MA20'].iloc[-1]
    
    # 检查是否有NaN
    if pd.isna(ma5) or pd.isna(ma10) or pd.isna(ma20):
        return False
    
    return ma5 > ma10 > ma20


def check_volume_increase(data, ratio=config.VOLUME_RATIO):
    """
    检查成交量放大
    
    Args:
        ratio: 放大倍数
    
    Returns:
        bool: 当月成交量 > 前3月平均 * ratio
    """
    if len(data) < 4:
        return False
    
    current_volume = data['volume'].iloc[-1]
    prev_3m_avg = data['volume'].iloc[-4:-1].mean()
    
    if pd.isna(prev_3m_avg) or prev_3m_avg == 0:
        return False
    
    return current_volume > prev_3m_avg * ratio


def get_latest_indicators(data):
    """获取最新指标值"""
    if len(data) < 1:
        return None
    
    latest = data.iloc[-1]
    return {
        'close': round(latest['close'], 2),
        'ma5': round(latest['MA5'], 2) if not pd.isna(latest['MA5']) else None,
        'ma10': round(latest['MA10'], 2) if not pd.isna(latest['MA10']) else None,
        'ma20': round(latest['MA20'], 2) if not pd.isna(latest['MA20']) else None,
        'macd_dif': round(latest['MACD_DIF'], 4) if not pd.isna(latest['MACD_DIF']) else None,
        'macd_dea': round(latest['MACD_DEA'], 4) if not pd.isna(latest['MACD_DEA']) else None,
        'kdj_k': round(latest['KDJ_K'], 2) if not pd.isna(latest['KDJ_K']) else None,
        'kdj_d': round(latest['KDJ_D'], 2) if not pd.isna(latest['KDJ_D']) else None,
        'kdj_j': round(latest['KDJ_J'], 2) if not pd.isna(latest['KDJ_J']) else None,
        'volume': int(latest['volume'])
    }