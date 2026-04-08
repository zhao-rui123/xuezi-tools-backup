"""
移动平均族模块
提供各种移动平均线指标
"""

import pandas as pd
import numpy as np

from .base_funcs import REF, SUM


def MA(close: pd.Series, n: int) -> pd.Series:
    """
    简单移动平均 (Simple Moving Average)
    MA(X,N) = SUM(X,N) / N

    Parameters
    ----------
    close : pd.Series
        收盘价序列
    n : int
        周期

    Returns
    -------
    pd.Series
        N日简单移动平均
    """
    return close.rolling(window=n, min_periods=1).mean()


def EMA(close: pd.Series, n: int) -> pd.Series:
    """
    指数移动平均 (Exponential Moving Average)
    EMA = 2/(N+1) * X + (N-1)/(N+1) * REF(EMA, 1)

    Parameters
    ----------
    close : pd.Series
        收盘价序列
    n : int
        周期

    Returns
    -------
    pd.Series
        N日指数移动平均
    """
    return close.ewm(span=n, adjust=False, min_periods=1).mean()


def SMA(close: pd.Series, n: int, m: int) -> pd.Series:
    """
    平滑移动平均 (Smoothed Moving Average)
    SMA = M/N * X + (N-M)/N * REF(SMA, 1)

    Parameters
    ----------
    close : pd.Series
        收盘价序列
    n : int
        周期
    m : int
        平滑系数

    Returns
    -------
    pd.Series
        平滑移动平均
    """
    alpha = m / n
    return close.ewm(alpha=alpha, adjust=False, min_periods=1).mean()


def WMA(close: pd.Series, n: int) -> pd.Series:
    """
    加权移动平均 (Weighted Moving Average)
    WMA = (N*CLOSE + (N-1)*REF(CLOSE,1) + ... + 1*REF(CLOSE,N-1)) / (1+2+...+N)

    Parameters
    ----------
    close : pd.Series
        收盘价序列
    n : int
        周期

    Returns
    -------
    pd.Series
        N日加权移动平均
    """
    weights = np.arange(1, n + 1)
    return close.rolling(window=n, min_periods=1).apply(
        lambda x: np.dot(x, weights[:len(x)]) / weights[:len(x)].sum(),
        raw=True
    )


def DMA(close: pd.Series, a: float) -> pd.Series:
    """
    动态移动平均 (Dynamic Moving Average)
    DMA = a * X + (1-a) * REF(DMA, 1)

    Parameters
    ----------
    close : pd.Series
        收盘价序列
    a : float
        动态系数 (0 < a < 1)

    Returns
    -------
    pd.Series
        动态移动平均
    """
    return close.ewm(alpha=a, adjust=False, min_periods=1).mean()


def TMA(close: pd.Series, n: int) -> pd.Series:
    """
    三角移动平均 (Triangular Moving Average)
    TMA = MA(MA(CLOSE, N), N)

    Parameters
    ----------
    close : pd.Series
        收盘价序列
    n : int
        周期

    Returns
    -------
    pd.Series
        N日三角移动平均
    """
    first_ma = MA(close, n)
    return MA(first_ma, n)


def DEMA(close: pd.Series, n: int) -> pd.Series:
    """
    双指数移动平均 (Double Exponential Moving Average)
    DEMA = 2 * EMA(CLOSE, N) - EMA(EMA(CLOSE, N), N)

    Parameters
    ----------
    close : pd.Series
        收盘价序列
    n : int
        周期

    Returns
    -------
    pd.Series
        N日双指数移动平均
    """
    ema1 = EMA(close, n)
    ema2 = EMA(ema1, n)
    return 2 * ema1 - ema2


def KAMA(close: pd.Series, n: int = 10, n1: int = 2, n2: int = 30) -> pd.Series:
    """
    自适应移动平均 (Kaufman Adaptive Moving Average)
    ER = |CLOSE - REF(CLOSE,N)| / SUM(|CLOSE - REF(CLOSE,1)|, N)
    SMOOTH = ER * (2/(N1+1) - 2/(N2+1)) + 2/(N2+1)
    COF = SMOOTH * SMOOTH
    KAMA = COF * CLOSE + (1-COF) * REF(KAMA, 1)

    Parameters
    ----------
    close : pd.Series
        收盘价序列
    n : int
        效率比计算周期（默认10）
    n1 : int
        快速EMA周期（默认2）
    n2 : int
        慢速EMA周期（默认30）

    Returns
    -------
    pd.Series
        自适应移动平均
    """
    # 效率比 (Efficiency Ratio)
    change = (close - REF(close, n)).abs()
    volatility = SUM((close - REF(close, 1)).abs(), n)
    ER = change / volatility

    # 平滑常数
    fast_alpha = 2 / (n1 + 1)
    slow_alpha = 2 / (n2 + 1)
    SMOOTH = ER * (fast_alpha - slow_alpha) + slow_alpha
    COF = SMOOTH * SMOOTH

    # KAMA递推计算
    kama = close.copy()
    kama.iloc[:] = close.iloc[0]  # 初始化

    for i in range(1, len(close)):
        kama.iloc[i] = COF.iloc[i] * close.iloc[i] + (1 - COF.iloc[i]) * kama.iloc[i - 1]

    return kama
