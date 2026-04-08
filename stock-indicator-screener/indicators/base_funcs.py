"""
基础函数模块
提供通达信风格的基础序列操作函数
"""

import pandas as pd
import numpy as np


def REF(series: pd.Series, n: int) -> pd.Series:
    """
    N天前X的值（向过去偏移N天）

    Parameters
    ----------
    series : pd.Series
        输入序列
    n : int
        向过去偏移的天数

    Returns
    -------
    pd.Series
        向过去偏移N天的序列
    """
    return series.shift(n)


def IF(condition: pd.Series, a, b) -> pd.Series:
    """
    条件选择：COND为真取A，否则取B

    Parameters
    ----------
    condition : pd.Series
        条件序列（布尔值）
    a : pd.Series or scalar
        条件为真时的值
    b : pd.Series or scalar
        条件为假时的值

    Returns
    -------
    pd.Series
        条件选择结果
    """
    return np.where(condition, a, b)


def SUM(series: pd.Series, n: int) -> pd.Series:
    """
    过去N天求和（滚动窗口求和）

    Parameters
    ----------
    series : pd.Series
        输入序列
    n : int
        滚动窗口大小

    Returns
    -------
    pd.Series
        过去N天的和
    """
    return series.rolling(window=n, min_periodes=1).sum()


def MAX(series: pd.Series, n: int) -> pd.Series:
    """
    过去N天最大值

    Parameters
    ----------
    series : pd.Series
        输入序列
    n : int
        滚动窗口大小

    Returns
    -------
    pd.Series
        过去N天的最大值
    """
    return series.rolling(window=n, min_periods=1).max()


def MIN(series: pd.Series, n: int) -> pd.Series:
    """
    过去N天最小值

    Parameters
    ----------
    series : pd.Series
        输入序列
    n : int
        滚动窗口大小

    Returns
    -------
    pd.Series
        过去N天的最小值
    """
    return series.rolling(window=n, min_periods=1).min()


def ABS(series: pd.Series) -> pd.Series:
    """
    绝对值

    Parameters
    ----------
    series : pd.Series
        输入序列

    Returns
    -------
    pd.Series
        绝对值序列
    """
    return series.abs()


def CUMSUM(series: pd.Series) -> pd.Series:
    """
    累积求和

    Parameters
    ----------
    series : pd.Series
        输入序列

    Returns
    -------
    pd.Series
        累积和序列
    """
    return series.cumsum()
