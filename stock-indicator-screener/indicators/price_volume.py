import numpy as np
import pandas as pd


def VWAP(close, volume, n=1):
    """
    VWAP (成交量加权平均价)
    VWAP = SUM(CLOSE*VOLUME, N) / SUM(VOLUME, N)
    """
    close = np.asarray(close, dtype=float)
    volume = np.asarray(volume, dtype=float)

    cp = close * volume
    vwap = _sum(cp, n) / _sum(volume, n)

    return vwap


def PVT(close, volume):
    """
    PVT (价量趋势)
    PVT = CUMSUM((CLOSE-REF(CLOSE,1))/REF(CLOSE,1) * VOLUME)
    """
    close = np.asarray(close, dtype=float)
    volume = np.asarray(volume, dtype=float)

    pct_change = (close - np.roll(close, 1)) / np.roll(close, 1)
    pct_change[0] = 0

    pvt_component = pct_change * volume
    pvt = np.cumsum(pvt_component)

    return pvt


def FI(close, volume, n=13):
    """
    FI (Force Index 力指数)
    FI = (CLOSE - REF(CLOSE,1)) * VOLUME
    FIMA = EMA(FI, N)
    返回: fi, fima
    """
    close = np.asarray(close, dtype=float)
    volume = np.asarray(volume, dtype=float)

    fi = (close - np.roll(close, 1)) * volume
    fi[0] = 0

    fima = _ema(fi, n)

    return fi, fima


# ========== 内部辅助函数 ==========

def _ema(series, n):
    """计算EMA"""
    series = np.asarray(series, dtype=float)
    alpha = 2 / (n + 1)
    ema = np.zeros_like(series)
    ema[0] = series[0]
    for i in range(1, len(series)):
        ema[i] = alpha * series[i] + (1 - alpha) * ema[i - 1]
    return ema


def _sum(series, n):
    """计算移动求和"""
    series = np.asarray(series, dtype=float)
    result = np.zeros_like(series, dtype=float)
    cumsum = np.cumsum(series)
    result[:n] = cumsum[:n]
    for i in range(n, len(series)):
        result[i] = cumsum[i] - cumsum[i - n]
    return result
