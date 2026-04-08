import numpy as np
import pandas as pd


def OBV(close, volume):
    """
    OBV (能量潮)
    OBV = CUMSUM(IF(CLOSE>REF(CLOSE,1), VOLUME, IF(CLOSE<REF(CLOSE,1), -VOLUME, 0)))
    """
    close = np.asarray(close, dtype=float)
    volume = np.asarray(volume, dtype=float)

    diff = np.where(close > np.roll(close, 1), volume,
                    np.where(close < np.roll(close, 1), -volume, 0))
    diff[0] = 0

    obv = np.cumsum(diff)
    return obv


def PVO(volume, n1=12, n2=26, n3=9):
    """
    PVO (成交量摆动)
    PVO = (EMA(VOLUME,N1) - EMA(VOLUME,N2)) / EMA(VOLUME,N2) * 100
    返回: pvo, signal, histogram
    """
    volume = np.asarray(volume, dtype=float)

    ema1 = _ema(volume, n1)
    ema2 = _ema(volume, n2)

    pvo = (ema1 - ema2) / ema2 * 100
    signal = _ema(pvo, n3)
    histogram = pvo - signal

    return pvo, signal, histogram


def MFI(high, low, close, volume, n=14):
    """
    MFI (资金流量指标)
    MF = TYPICAL_PRICE * VOLUME
    正资金流/负资金流
    MFI = 100 - 100/(1 + 正MF/负MF)
    """
    high = np.asarray(high, dtype=float)
    low = np.asarray(low, dtype=float)
    close = np.asarray(close, dtype=float)
    volume = np.asarray(volume, dtype=float)

    typical = (high + low + close) / 3
    mf = typical * volume

    mf_pos = np.where(typical > np.roll(typical, 1), mf, 0)
    mf_neg = np.where(typical < np.roll(typical, 1), mf, 0)
    mf_pos[0] = 0
    mf_neg[0] = 0

    mf_pos_sum = _sum(mf_pos, n)
    mf_neg_sum = _sum(mf_neg, n)

    mfi = np.where(mf_neg_sum == 0, 100,
                   100 - 100 / (1 + mf_pos_sum / np.maximum(mf_neg_sum, 1e-10)))

    return mfi


def VR(close, volume, n=24):
    """
    VR (成交量变异率)
    AV = IF(CLOSE>REF(CLOSE,1), VOLUME, 0)
    BV = IF(CLOSE<REF(CLOSE,1), VOLUME, 0)
    CV = IF(CLOSE=REF(CLOSE,1), VOLUME, 0)
    VR = (AV + CV/2) / (BV + CV/2) * 100
    """
    close = np.asarray(close, dtype=float)
    volume = np.asarray(volume, dtype=float)

    av = np.where(close > np.roll(close, 1), volume, 0)
    bv = np.where(close < np.roll(close, 1), volume, 0)
    cv = np.where(close == np.roll(close, 1), volume, 0)
    av[0] = 0
    bv[0] = 0
    cv[0] = 0

    av_sum = _sum(av, n)
    bv_sum = _sum(bv, n)
    cv_sum = _sum(cv, n)

    vr = np.where((bv_sum + cv_sum / 2) == 0, np.nan,
                  (av_sum + cv_sum / 2) / (bv_sum + cv_sum / 2) * 100)

    return vr


def CMF(high, low, close, volume, n=20):
    """
    CMF (蔡金货币流量)
    CMF = SUM(((CLOSE-LOW)-(HIGH-CLOSE))/(HIGH-LOW)*VOLUME, N) / SUM(VOLUME,N)
    """
    high = np.asarray(high, dtype=float)
    low = np.asarray(low, dtype=float)
    close = np.asarray(close, dtype=float)
    volume = np.asarray(volume, dtype=float)

    hl_diff = high - low
    hl_diff = np.where(hl_diff == 0, 1e-10, hl_diff)

    money_flow_multiplier = ((close - low) - (high - close)) / hl_diff
    money_flow_volume = money_flow_multiplier * volume

    cmf = _sum(money_flow_volume, n) / _sum(volume, n)

    return cmf


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
