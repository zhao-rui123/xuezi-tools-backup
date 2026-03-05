"""
完整技术指标计算模块 - 包含所有常用指标
"""
import pandas as pd
import numpy as np
import config


def calculate_all_indicators(data):
    """
    计算所有技术指标
    
    Returns:
        DataFrame: 包含所有指标的数据
    """
    # 基础均线
    data = calculate_moving_averages(data)
    
    # MACD
    data = calculate_macd(data)
    
    # KDJ
    data = calculate_kdj(data)
    
    # RSI
    data = calculate_rsi(data)
    
    # BOLL
    data = calculate_bollinger(data)
    
    # 成交量指标
    data = calculate_volume_indicators(data)
    
    # 趋势指标
    data = calculate_trend_indicators(data)
    
    return data


def calculate_moving_averages(data):
    """计算多条均线"""
    for period in [5, 10, 20, 30, 60, 120, 250]:
        data[f'MA{period}'] = data['close'].rolling(window=period).mean()
    return data


def calculate_macd(data, fast=config.MACD_FAST, slow=config.MACD_SLOW, signal=config.MACD_SIGNAL):
    """计算MACD"""
    ema_fast = data['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = data['close'].ewm(span=slow, adjust=False).mean()
    
    data['MACD_DIF'] = ema_fast - ema_slow
    data['MACD_DEA'] = data['MACD_DIF'].ewm(span=signal, adjust=False).mean()
    data['MACD_HIST'] = 2 * (data['MACD_DIF'] - data['MACD_DEA'])
    
    return data


def calculate_kdj(data, n=config.KDJ_N, m1=config.KDJ_M1, m2=config.KDJ_M2):
    """计算KDJ"""
    low_list = data['low'].rolling(window=n, min_periods=n).min()
    high_list = data['high'].rolling(window=n, min_periods=n).max()
    
    rsv = (data['close'] - low_list) / (high_list - low_list) * 100
    
    data['KDJ_K'] = rsv.ewm(alpha=1/m1, adjust=False).mean()
    data['KDJ_D'] = data['KDJ_K'].ewm(alpha=1/m2, adjust=False).mean()
    data['KDJ_J'] = 3 * data['KDJ_K'] - 2 * data['KDJ_D']
    
    return data


def calculate_rsi(data, periods=[6, 12, 24]):
    """计算RSI"""
    for period in periods:
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        data[f'RSI{period}'] = 100 - (100 / (1 + rs))
    
    return data


def calculate_bollinger(data, period=20, std_dev=2):
    """计算布林带"""
    data['BOLL_MID'] = data['close'].rolling(window=period).mean()
    data['BOLL_STD'] = data['close'].rolling(window=period).std()
    data['BOLL_UP'] = data['BOLL_MID'] + (data['BOLL_STD'] * std_dev)
    data['BOLL_DOWN'] = data['BOLL_MID'] - (data['BOLL_STD'] * std_dev)
    
    return data


def calculate_volume_indicators(data):
    """计算成交量指标"""
    # 成交量均线
    data['VOL_MA5'] = data['volume'].rolling(window=5).mean()
    data['VOL_MA10'] = data['volume'].rolling(window=10).mean()
    
    # 量比
    data['VOL_RATIO'] = data['volume'] / data['volume'].rolling(window=5).mean()
    
    # OBV
    data['OBV'] = (np.sign(data['close'].diff()) * data['volume']).cumsum()
    
    return data


def calculate_trend_indicators(data):
    """计算趋势指标"""
    # ATR (平均真实波幅)
    high_low = data['high'] - data['low']
    high_close = np.abs(data['high'] - data['close'].shift())
    low_close = np.abs(data['low'] - data['close'].shift())
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    data['ATR14'] = true_range.rolling(14).mean()
    
    # CCI (商品通道指数)
    tp = (data['high'] + data['low'] + data['close']) / 3
    data['CCI'] = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).std())
    
    # DMI/ADX
    data = calculate_dmi(data)
    
    return data


def calculate_dmi(data, period=14):
    """计算DMI指标"""
    # +DM和-DM
    plus_dm = data['high'].diff()
    minus_dm = data['low'].diff(-1).abs()
    
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
    
    # TR
    tr1 = data['high'] - data['low']
    tr2 = abs(data['high'] - data['close'].shift())
    tr3 = abs(data['low'] - data['close'].shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # 平滑
    atr = tr.rolling(period).mean()
    plus_di = 100 * plus_dm.rolling(period).mean() / atr
    minus_di = 100 * minus_dm.rolling(period).mean() / atr
    
    # DX和ADX
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(period).mean()
    
    data['PLUS_DI'] = plus_di
    data['MINUS_DI'] = minus_di
    data['ADX'] = adx
    
    return data


def get_all_signals(data):
    """
    获取所有信号状态
    
    Returns:
        dict: 所有信号
    """
    if len(data) < 2:
        return {}
    
    current = data.iloc[-1]
    prev = data.iloc[-2]
    
    signals = {
        # MACD信号
        'macd_golden_cross': current['MACD_DIF'] > current['MACD_DEA'] and prev['MACD_DIF'] <= prev['MACD_DEA'],
        'macd_bearish_cross': current['MACD_DIF'] < current['MACD_DEA'] and prev['MACD_DIF'] >= prev['MACD_DEA'],
        'macd_above_zero': current['MACD_DIF'] > 0,
        
        # KDJ信号
        'kdj_golden_cross': current['KDJ_K'] > current['KDJ_D'] and prev['KDJ_K'] <= prev['KDJ_D'],
        'kdj_bearish_cross': current['KDJ_K'] < current['KDJ_D'] and prev['KDJ_K'] >= prev['KDJ_D'],
        'kdj_overbought': current['KDJ_K'] > 80,
        'kdj_oversold': current['KDJ_K'] < 20,
        
        # RSI信号
        'rsi_overbought': current.get('RSI14', 0) > 70,
        'rsi_oversold': current.get('RSI14', 0) < 30,
        
        # 均线信号
        'ma_bullish': current['MA5'] > current['MA10'] > current['MA20'],
        'ma_bearish': current['MA5'] < current['MA10'] < current['MA20'],
        'price_above_ma60': current['close'] > current.get('MA60', 0),
        'price_above_ma250': current['close'] > current.get('MA250', 0),
        
        # 布林带信号
        'price_above_boll_up': current['close'] > current.get('BOLL_UP', float('inf')),
        'price_below_boll_down': current['close'] < current.get('BOLL_DOWN', 0),
        
        # DMI信号
        'dmi_bullish': current.get('PLUS_DI', 0) > current.get('MINUS_DI', 0),
        'adx_strong': current.get('ADX', 0) > 25,
        
        # 成交量信号
        'volume_increase': current['volume'] > current.get('VOL_MA5', 0) * 1.5,
        'volume_decrease': current['volume'] < current.get('VOL_MA5', 0) * 0.7
    }
    
    return signals


def get_latest_all_indicators(data):
    """获取最新所有指标值"""
    if len(data) < 1:
        return None
    
    latest = data.iloc[-1]
    
    return {
        # 价格
        'close': round(latest['close'], 2),
        'open': round(latest['open'], 2),
        'high': round(latest['high'], 2),
        'low': round(latest['low'], 2),
        
        # 均线
        'ma5': round(latest['MA5'], 2) if not pd.isna(latest['MA5']) else None,
        'ma10': round(latest['MA10'], 2) if not pd.isna(latest['MA10']) else None,
        'ma20': round(latest['MA20'], 2) if not pd.isna(latest['MA20']) else None,
        'ma30': round(latest['MA30'], 2) if not pd.isna(latest.get('MA30')) else None,
        'ma60': round(latest['MA60'], 2) if not pd.isna(latest.get('MA60')) else None,
        'ma120': round(latest['MA120'], 2) if not pd.isna(latest.get('MA120')) else None,
        'ma250': round(latest['MA250'], 2) if not pd.isna(latest.get('MA250')) else None,
        
        # MACD
        'macd_dif': round(latest['MACD_DIF'], 4) if not pd.isna(latest['MACD_DIF']) else None,
        'macd_dea': round(latest['MACD_DEA'], 4) if not pd.isna(latest['MACD_DEA']) else None,
        'macd_hist': round(latest['MACD_HIST'], 4) if not pd.isna(latest['MACD_HIST']) else None,
        
        # KDJ
        'kdj_k': round(latest['KDJ_K'], 2) if not pd.isna(latest['KDJ_K']) else None,
        'kdj_d': round(latest['KDJ_D'], 2) if not pd.isna(latest['KDJ_D']) else None,
        'kdj_j': round(latest['KDJ_J'], 2) if not pd.isna(latest['KDJ_J']) else None,
        
        # RSI
        'rsi6': round(latest.get('RSI6'), 2) if not pd.isna(latest.get('RSI6')) else None,
        'rsi12': round(latest.get('RSI12'), 2) if not pd.isna(latest.get('RSI12')) else None,
        'rsi24': round(latest.get('RSI24'), 2) if not pd.isna(latest.get('RSI24')) else None,
        
        # 布林带
        'boll_up': round(latest.get('BOLL_UP'), 2) if not pd.isna(latest.get('BOLL_UP')) else None,
        'boll_mid': round(latest.get('BOLL_MID'), 2) if not pd.isna(latest.get('BOLL_MID')) else None,
        'boll_down': round(latest.get('BOLL_DOWN'), 2) if not pd.isna(latest.get('BOLL_DOWN')) else None,
        
        # DMI
        'plus_di': round(latest.get('PLUS_DI'), 2) if not pd.isna(latest.get('PLUS_DI')) else None,
        'minus_di': round(latest.get('MINUS_DI'), 2) if not pd.isna(latest.get('MINUS_DI')) else None,
        'adx': round(latest.get('ADX'), 2) if not pd.isna(latest.get('ADX')) else None,
        
        # 成交量
        'volume': int(latest['volume']),
        'vol_ma5': int(latest.get('VOL_MA5', 0)) if not pd.isna(latest.get('VOL_MA5')) else None,
        'vol_ratio': round(latest.get('VOL_RATIO', 0), 2) if not pd.isna(latest.get('VOL_RATIO')) else None,
        
        # CCI
        'cci': round(latest.get('CCI'), 2) if not pd.isna(latest.get('CCI')) else None,
        
        # ATR
        'atr14': round(latest.get('ATR14'), 2) if not pd.isna(latest.get('ATR14')) else None
    }