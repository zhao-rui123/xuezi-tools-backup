"""
反转指标模块 (Reversal Indicators)
提供价格反转类技术指标：KDJ、RSI、CCI、WR、ROC
"""

import pandas as pd
import numpy as np

from .base_funcs import REF, MAX, MIN
from .ma_family import SMA, MA


def KDJ(high: pd.Series, low: pd.Series, close: pd.Series,
        n: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
    """
    KDJ (随机指标 / Stochastic Oscillator)

    RSV = (CLOSE - MIN(LOW,N)) / (MAX(HIGH,N) - MIN(LOW,N)) * 100
    K = SMA(RSV, M1, 1)
    D = SMA(K, M2, 1)
    J = 3*K - 2*D

    Parameters
    ----------
    high : pd.Series
        最高价序列
    low : pd.Series
        最低价序列
    close : pd.Series
        收盘价序列
    n : int
        RSV计算周期（默认9）
    m1 : int
        K平滑周期（默认3）
    m2 : int
        D平滑周期（默认3）

    Returns
    -------
    pd.DataFrame
        包含 K, D, J 三列的DataFrame
    """
    low_n = MIN(low, n)
    high_n = MAX(high, n)

    rsv = (close - low_n) / (high_n - low_n) * 100
    K = SMA(rsv, m1, 1)
    D = SMA(K, m2, 1)
    J = 3 * K - 2 * D

    return pd.DataFrame({
        "K": K,
        "D": D,
        "J": J
    }, index=close.index)


def RSI(close: pd.Series, n: int = 14) -> pd.Series:
    """
    RSI (相对强弱指标 / Relative Strength Index)

    CLOSEUP = IF(CLOSE > REF(CLOSE,1), CLOSE - REF(CLOSE,1), 0)
    CLOSEDOWN = IF(CLOSE < REF(CLOSE,1), ABS(CLOSE - REF(CLOSE,1)), 0)
    RSI = 100 * SMA(CLOSEUP,N,1) / (SMA(CLOSEUP,N,1) + SMA(CLOSEDOWN,N,1))

    Parameters
    ----------
    close : pd.Series
        收盘价序列
    n : int
        计算周期（默认14）

    Returns
    -------
    pd.Series
        RSI序列（0-100）
    """
    delta = close - REF(close, 1)

    # 使用np.where保持Series类型
    close_up = pd.Series(
        np.where(delta > 0, delta.values, 0.0),
        index=close.index
    )
    close_down = pd.Series(
        np.where(delta < 0, np.abs(delta.values), 0.0),
        index=close.index
    )

    sma_up = SMA(close_up, n, 1)
    sma_down = SMA(close_down, n, 1)

    rsi = 100 * sma_up / (sma_up + sma_down)

    return rsi


def CCI(high: pd.Series, low: pd.Series, close: pd.Series,
        n: int = 14) -> pd.Series:
    """
    CCI (顺势指标 / Commodity Channel Index)

    TP = (HIGH + LOW + CLOSE) / 3
    CCI = (TP - MA(TP,N)) / (0.015 * MA(ABS(TP-MA(TP,N)),N))

    Parameters
    ----------
    high : pd.Series
        最高价序列
    low : pd.Series
        最低价序列
    close : pd.Series
        收盘价序列
    n : int
        计算周期（默认14）

    Returns
    -------
    pd.Series
        CCI序列
    """
    tp = (high + low + close) / 3
    tp_ma = MA(tp, n)
    tp_dev = (tp - tp_ma).abs()
    tp_dev_ma = MA(tp_dev, n)

    cci = (tp - tp_ma) / (0.015 * tp_dev_ma)

    return cci


def WR(high: pd.Series, low: pd.Series, close: pd.Series,
       n: int = 14) -> pd.Series:
    """
    WR (威廉指标 / Williams %R)

    WR = 100 * (MAX(HIGH,N) - CLOSE) / (MAX(HIGH,N) - MIN(LOW,N))

    Parameters
    ----------
    high : pd.Series
        最高价序列
    low : pd.Series
        最低价序列
    close : pd.Series
        收盘价序列
    n : int
        计算周期（默认14）

    Returns
    -------
    pd.Series
        WR序列（0-100）
    """
    high_n = MAX(high, n)
    low_n = MIN(low, n)

    wr = 100 * (high_n - close) / (high_n - low_n)

    return wr


def ROC(close: pd.Series, n: int = 12) -> pd.Series:
    """
    ROC (变动率指标 / Rate of Change)

    ROC = (CLOSE - REF(CLOSE,N)) / REF(CLOSE,N) * 100

    Parameters
    ----------
    close : pd.Series
        收盘价序列
    n : int
        计算周期（默认12）

    Returns
    -------
    pd.Series
        ROC序列（百分比）
    """
    ref_close = REF(close, n)
    roc = (close - ref_close) / ref_close * 100

    return roc
