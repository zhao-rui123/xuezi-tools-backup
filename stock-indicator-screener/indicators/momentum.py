"""
动量指标模块 (Momentum Indicators)
提供价格动量/趋势类技术指标
"""

import pandas as pd
import numpy as np

from .base_funcs import REF
from .ma_family import MA, EMA


def MACD(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """
    MACD (Moving Average Convergence Divergence) - 指数平滑异同移动平均线

    DIF = EMA(close, fast) - EMA(close, slow)
    DEA = EMA(DIF, signal)
    BAR = 2 * (DIF - DEA)

    Parameters
    ----------
    close : pd.Series
        收盘价序列
    fast : int
        快线EMA周期（默认12）
    slow : int
        慢线EMA周期（默认26）
    signal : int
        信号线EMA周期（默认9）

    Returns
    -------
    pd.DataFrame
        包含 DIF, DEA, BAR 三列的DataFrame
    """
    ema_fast = EMA(close, fast)
    ema_slow = EMA(close, slow)

    DIF = ema_fast - ema_slow
    DEA = EMA(DIF, signal)
    BAR = 2 * (DIF - DEA)

    return pd.DataFrame({
        "DIF": DIF,
        "DEA": DEA,
        "BAR": BAR
    }, index=close.index)


def DPO(close: pd.Series, n: int = 20) -> pd.Series:
    """
    DPO (Detrended Price Oscillator) - 去势价格摆动指标

    DPO = CLOSE - REF(MA(CLOSE, N), N/2+1)

    Parameters
    ----------
    close : pd.Series
        收盘价序列
    n : int
        周期（默认20）

    Returns
    -------
    pd.Series
        DPO序列
    """
    ma = MA(close, n)
    shift_n = int(n / 2) + 1
    return close - REF(ma, shift_n)


def PO(close: pd.Series, n1: int = 9, n2: int = 26) -> pd.Series:
    """
    PO (Price Oscillator) - 价格摆动指标

    PO = (EMA(close, n1) - EMA(close, n2)) / EMA(close, n2) * 100

    Parameters
    ----------
    close : pd.Series
        收盘价序列
    n1 : int
        短期EMA周期（默认9）
    n2 : int
        长期EMA周期（默认26）

    Returns
    -------
    pd.Series
        PO序列（百分比）
    """
    ema_short = EMA(close, n1)
    ema_long = EMA(close, n2)
    return (ema_short - ema_long) / ema_long * 100


def TRIX(close: pd.Series, n: int = 20) -> pd.Series:
    """
    TRIX (Triple Exponential Moving Average) - 三重指数平滑平均

    TRIX = (EMA(EMA(EMA(CLOSE, N), N), N) - REF(EMA(EMA(EMA(CLOSE, N), N), N), 1))
           / REF(EMA(EMA(EMA(CLOSE, N), N), N), 1)

    Parameters
    ----------
    close : pd.Series
        收盘价序列
    n : int
        周期（默认20）

    Returns
    -------
    pd.Series
        TRIX序列
    """
    ema1 = EMA(close, n)
    ema2 = EMA(ema1, n)
    ema3 = EMA(ema2, n)

    trix = (ema3 - REF(ema3, 1)) / REF(ema3, 1)
    return trix


def OSC(close: pd.Series, n: int = 40, m: int = 20) -> pd.DataFrame:
    """
    OSC (Price Oscillator) - 价格摆动指标

    OSC = CLOSE - MA(CLOSE, N)
    OSCMA = MA(OSC, M)

    Parameters
    ----------
    close : pd.Series
        收盘价序列
    n : int
        MA周期（默认40）
    m : int
        OSC的MA周期（默认20）

    Returns
    -------
    pd.DataFrame
        包含 OSC, OSCMA 两列的DataFrame
    """
    osc = close - MA(close, n)
    oscma = MA(osc, m)

    return pd.DataFrame({
        "OSC": osc,
        "OSCMA": oscma
    }, index=close.index)


def PPO(close: pd.Series, n1: int = 12, n2: int = 26, n3: int = 9) -> pd.DataFrame:
    """
    PPO (Percent Price Oscillator) - 价格摆动指标（百分比版）

    PPO = (EMA(close, n1) - EMA(close, n2)) / EMA(close, n2)
    Signal = EMA(PPO, n3)
    Histogram = PPO - Signal

    Parameters
    ----------
    close : pd.Series
        收盘价序列
    n1 : int
        快线EMA周期（默认12）
    n2 : int
        慢线EMA周期（默认26）
    n3 : int
        信号线EMA周期（默认9）

    Returns
    -------
    pd.DataFrame
        包含 PPO, Signal, Histogram 三列的DataFrame
    """
    ema_fast = EMA(close, n1)
    ema_slow = EMA(close, n2)

    PPO_val = (ema_fast - ema_slow) / ema_slow
    Signal = EMA(PPO_val, n3)
    Histogram = PPO_val - Signal

    return pd.DataFrame({
        "PPO": PPO_val,
        "Signal": Signal,
        "Histogram": Histogram
    }, index=close.index)


def TSI(close: pd.Series, n1: int = 25, n2: int = 13) -> pd.Series:
    """
    TSI (True Strength Index) - 真实强度指数

    TSI = EMA(EMA(CLOSE-REF(CLOSE,1), N1), N2)
          / EMA(EMA(ABS(CLOSE-REF(CLOSE,1)), N1), N2) * 100

    Parameters
    ----------
    close : pd.Series
        收盘价序列
    n1 : int
        第一层EMA周期（默认25）
    n2 : int
        第二层EMA周期（默认13）

    Returns
    -------
    pd.Series
        TSI序列
    """
    price_change = close - REF(close, 1)
    abs_change = price_change.abs()

    double_smoothed = EMA(EMA(price_change, n1), n2)
    abs_double_smoothed = EMA(EMA(abs_change, n1), n2)

    tsi = double_smoothed / abs_double_smoothed * 100
    return tsi
