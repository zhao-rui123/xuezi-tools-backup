"""
信号生成模块 (Signal Generation)
基于技术指标值生成买入/卖出信号
"""

import pandas as pd
import numpy as np

from indicators.base_funcs import REF


def generate_macd_signal(dif: pd.Series, dea: pd.Series,
                          threshold: float = 0.0) -> pd.DataFrame:
    """
    基于MACD指标的信号生成

    DIF上穿DEA -> BUY (金叉)
    DIF下穿DEA -> SELL (死叉)

    Parameters
    ----------
    dif : pd.Series
        DIF线序列
    dea : pd.Series
        DEA线序列
    threshold : float
        穿越阈值（默认0.0）

    Returns
    -------
    pd.DataFrame
        signal: 1=BUY, -1=SELL, 0=HOLD
    """
    diff = dif - dea
    prev_diff = REF(diff, 1)

    golden_cross = (prev_diff <= threshold) & (diff > threshold)
    dead_cross = (prev_diff >= -threshold) & (diff < -threshold)

    signal = pd.Series(0, index=dif.index)
    signal[golden_cross] = 1
    signal[dead_cross] = -1

    return pd.DataFrame({"signal": signal}, index=dif.index)


def generate_rsi_signal(rsi: pd.Series,
                         overbought: float = 70.0,
                         oversold: float = 30.0,
                         smooth_n: int = 2) -> pd.DataFrame:
    """
    基于RSI指标的信号生成

    RSI < oversold -> BUY (超卖买入)
    RSI > overbought -> SELL (超买卖出)

    Parameters
    ----------
    rsi : pd.Series
        RSI序列（0-100）
    overbought : float
        超买阈值（默认70）
    oversold : float
        超卖阈值（默认30）
    smooth_n : int
        信号平滑周期（默认2，过滤假信号）

    Returns
    -------
    pd.DataFrame
        signal: 1=BUY, -1=SELL, 0=HOLD
    """
    signal = pd.Series(0, index=rsi.index)

    # RSI从超卖区回升（连续smooth_n日RSI<oversold）
    rsi_oversold = rsi < oversold
    rsi_oversold_smooth = rsi_oversold.rolling(window=smooth_n, min_periods=1).min()
    signal[rsi_oversold_smooth.astype(bool) & (REF(rsi, 1) >= oversold)] = 1

    # RSI从超买区回落（连续smooth_n日RSI>overbought）
    rsi_overbought = rsi > overbought
    rsi_overbought_smooth = rsi_overbought.rolling(window=smooth_n, min_periods=1).min()
    signal[rsi_overbought_smooth.astype(bool) & (REF(rsi, 1) <= overbought)] = -1

    return pd.DataFrame({"signal": signal}, index=rsi.index)


def generate_kdj_signal(k: pd.Series, d: pd.Series, j: pd.Series,
                         oversold: float = 20.0,
                         overbought: float = 80.0) -> pd.DataFrame:
    """
    基于KDJ指标的信号生成

    K从下往上穿越D且D<oversold -> BUY (金叉超卖)
    K从上往下穿越D且D>overbought -> SELL (死叉超买)

    Parameters
    ----------
    k : pd.Series
        K值序列
    d : pd.Series
        D值序列
    j : pd.Series
        J值序列
    oversold : float
        超卖阈值（默认20）
    overbought : float
        超买阈值（默认80）

    Returns
    -------
    pd.DataFrame
        signal: 1=BUY, -1=SELL, 0=HOLD
    """
    signal = pd.Series(0, index=k.index)

    # 金叉：D值在超卖区域，K线从下穿越D线
    k_cross_up_d = (REF(k, 1) <= REF(d, 1)) & (k > d)
    kdj_buy = k_cross_up_d & (d < oversold)
    signal[kdj_buy] = 1

    # 死叉：D值在超买区域，K线从上穿越D线
    k_cross_down_d = (REF(k, 1) >= REF(d, 1)) & (k < d)
    kdj_sell = k_cross_down_d & (d > overbought)
    signal[kdj_sell] = -1

    return pd.DataFrame({"signal": signal}, index=k.index)


def generate_cci_signal(cci: pd.Series,
                        oversold: float = -100.0,
                        overbought: float = 100.0) -> pd.DataFrame:
    """
    基于CCI指标的信号生成

    CCI上穿-100 -> BUY (超卖回归)
    CCI下穿+100 -> SELL (超买回归)

    Parameters
    ----------
    cci : pd.Series
        CCI序列
    oversold : float
        超卖阈值（默认-100）
    overbought : float
        超买阈值（默认100）

    Returns
    -------
    pd.DataFrame
        signal: 1=BUY, -1=SELL, 0=HOLD
    """
    signal = pd.Series(0, index=cci.index)

    cci_buy = (REF(cci, 1) <= oversold) & (cci > oversold)
    signal[cci_buy] = 1

    cci_sell = (REF(cci, 1) >= overbought) & (cci < overbought)
    signal[cci_sell] = -1

    return pd.DataFrame({"signal": signal}, index=cci.index)


def generate_wr_signal(wr: pd.Series,
                       overbought: float = 20.0,
                       oversold: float = 80.0) -> pd.DataFrame:
    """
    基于WR指标的信号生成

    WR上穿oversold(80) -> BUY (从超卖区回升)
    WR下穿overbought(20) -> SELL (从超买区回落)

    Parameters
    ----------
    wr : pd.Series
        WR序列
    overbought : float
        超买阈值（默认20）
    oversold : float
        超卖阈值（默认80）

    Returns
    -------
    pd.DataFrame
        signal: 1=BUY, -1=SELL, 0=HOLD
    """
    signal = pd.Series(0, index=wr.index)

    wr_buy = (REF(wr, 1) <= oversold) & (wr > oversold)
    signal[wr_buy] = 1

    wr_sell = (REF(wr, 1) >= overbought) & (wr < overbought)
    signal[wr_sell] = -1

    return pd.DataFrame({"signal": signal}, index=wr.index)


def generate_roc_signal(roc: pd.Series,
                        buy_threshold: float = 5.0,
                        sell_threshold: float = -5.0) -> pd.DataFrame:
    """
    基于ROC指标的信号生成

    ROC上穿buy_threshold -> BUY
    ROC下穿sell_threshold -> SELL

    Parameters
    ----------
    roc : pd.Series
        ROC序列（百分比）
    buy_threshold : float
        买入阈值（默认5%）
    sell_threshold : float
        卖出阈值（默认-5%）

    Returns
    -------
    pd.DataFrame
        signal: 1=BUY, -1=SELL, 0=HOLD
    """
    signal = pd.Series(0, index=roc.index)

    roc_buy = (REF(roc, 1) <= buy_threshold) & (roc > buy_threshold)
    signal[roc_buy] = 1

    roc_sell = (REF(roc, 1) >= sell_threshold) & (roc < sell_threshold)
    signal[roc_sell] = -1

    return pd.DataFrame({"signal": signal}, index=roc.index)
