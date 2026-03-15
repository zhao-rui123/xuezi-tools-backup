"""
技术指标计算模块
支持MACD和KDJ指标计算
"""

import logging
from typing import Optional, Tuple
from dataclasses import dataclass
import pandas as pd
import numpy as np

from config import config

logger = logging.getLogger(__name__)


@dataclass
class MACDResult:
    """MACD计算结果"""
    dif: pd.Series  # DIF线
    dea: pd.Series  # DEA线
    macd: pd.Series  # MACD柱状图
    golden_cross: bool  # 是否金叉
    dead_cross: bool  # 是否死叉


@dataclass
class KDJResult:
    """KDJ计算结果"""
    k: pd.Series  # K值
    d: pd.Series  # D值
    j: pd.Series  # J值
    golden_cross: bool  # 是否金叉
    dead_cross: bool  # 是否死叉


@dataclass
class VolumeResult:
    """成交量分析结果"""
    current_volume: float  # 当前成交量
    avg_volume: float  # 平均成交量
    volume_ratio: float  # 量比
    is_expanded: bool  # 是否放量


class TechnicalIndicators:
    """技术指标计算器"""
    
    @staticmethod
    def calculate_macd(
        df: pd.DataFrame,
        fast_period: int = None,
        slow_period: int = None,
        signal_period: int = None
    ) -> Optional[MACDResult]:
        """
        计算MACD指标
        
        MACD = DIF - DEA
        DIF = EMA(12) - EMA(26)
        DEA = EMA(DIF, 9)
        
        Args:
            df: 包含close列的DataFrame
            fast_period: 快线周期，默认使用config
            slow_period: 慢线周期，默认使用config
            signal_period: 信号线周期，默认使用config
        
        Returns:
            MACDResult对象
        """
        try:
            # 使用配置参数或传入参数
            fast = fast_period or config.MACD.fast_period
            slow = slow_period or config.MACD.slow_period
            signal = signal_period or config.MACD.signal_period
            
            close = df['close']
            
            # 计算EMA
            ema_fast = close.ewm(span=fast, adjust=False).mean()
            ema_slow = close.ewm(span=slow, adjust=False).mean()
            
            # 计算DIF
            dif = ema_fast - ema_slow
            
            # 计算DEA
            dea = dif.ewm(span=signal, adjust=False).mean()
            
            # 计算MACD柱状图
            macd = (dif - dea) * 2
            
            # 判断金叉死叉（最后两个周期）
            golden_cross = False
            dead_cross = False
            
            if len(dif) >= 2:
                # 金叉：DIF上穿DEA（昨天DIF<DEA，今天DIF>DEA）
                if dif.iloc[-2] < dea.iloc[-2] and dif.iloc[-1] > dea.iloc[-1]:
                    golden_cross = True
                # 死叉：DIF下穿DEA（昨天DIF>DEA，今天DIF<DEA）
                elif dif.iloc[-2] > dea.iloc[-2] and dif.iloc[-1] < dea.iloc[-1]:
                    dead_cross = True
            
            return MACDResult(
                dif=dif,
                dea=dea,
                macd=macd,
                golden_cross=golden_cross,
                dead_cross=dead_cross
            )
            
        except Exception as e:
            logger.error(f"计算MACD失败: {e}")
            return None
    
    @staticmethod
    def calculate_kdj(
        df: pd.DataFrame,
        n: int = None,
        m1: int = None,
        m2: int = None
    ) -> Optional[KDJResult]:
        """
        计算KDJ指标
        
        RSV = (收盘价 - N日内最低价) / (N日内最高价 - N日内最低价) * 100
        K = 2/3 * 昨日K + 1/3 * 今日RSV
        D = 2/3 * 昨日D + 1/3 * 今日K
        J = 3K - 2D
        
        Args:
            df: 包含high, low, close列的DataFrame
            n: RSV计算周期，默认使用config
            m1: K值平滑系数，默认使用config
            m2: D值平滑系数，默认使用config
        
        Returns:
            KDJResult对象
        """
        try:
            # 使用配置参数或传入参数
            period_n = n or config.KDJ.n
            smooth_m1 = m1 or config.KDJ.m1
            smooth_m2 = m2 or config.KDJ.m2
            
            high = df['high']
            low = df['low']
            close = df['close']
            
            # 计算N日内的最高价和最低价
            lowest_low = low.rolling(window=period_n).min()
            highest_high = high.rolling(window=period_n).max()
            
            # 计算RSV
            rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
            
            # 计算K值
            k = rsv.ewm(com=smooth_m1 - 1, adjust=False).mean()
            
            # 计算D值
            d = k.ewm(com=smooth_m2 - 1, adjust=False).mean()
            
            # 计算J值
            j = 3 * k - 2 * d
            
            # 判断金叉死叉（最后两个周期）
            golden_cross = False
            dead_cross = False
            
            if len(k) >= 2:
                # KDJ金叉：K上穿D（昨天K<D，今天K>D）
                if k.iloc[-2] < d.iloc[-2] and k.iloc[-1] > d.iloc[-1]:
                    golden_cross = True
                # KDJ死叉：K下穿D（昨天K>D，今天K<D）
                elif k.iloc[-2] > d.iloc[-2] and k.iloc[-1] < d.iloc[-1]:
                    dead_cross = True
            
            return KDJResult(
                k=k,
                d=d,
                j=j,
                golden_cross=golden_cross,
                dead_cross=dead_cross
            )
            
        except Exception as e:
            logger.error(f"计算KDJ失败: {e}")
            return None
    
    @staticmethod
    def analyze_volume(
        df: pd.DataFrame,
        lookback_days: int = None,
        multiplier: float = None
    ) -> Optional[VolumeResult]:
        """
        分析成交量是否放大
        
        Args:
            df: 包含volume列的DataFrame
            lookback_days: 参考历史天数，默认使用config
            multiplier: 放量倍数阈值，默认使用config
        
        Returns:
            VolumeResult对象
        """
        try:
            # 使用配置参数或传入参数
            lookback = lookback_days or config.VOLUME.lookback_days
            mult = multiplier or config.VOLUME.multiplier
            
            if len(df) < lookback + 1:
                logger.warning(f"数据不足，无法分析成交量 (需要{lookback+1}条，实际{len(df)}条)")
                return None
            
            # 当前成交量
            current_volume = df['volume'].iloc[-1]
            
            # 过去N天的平均成交量（不包含当前）
            avg_volume = df['volume'].iloc[-lookback-1:-1].mean()
            
            # 计算量比
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            # 判断是否放量
            is_expanded = volume_ratio >= mult
            
            return VolumeResult(
                current_volume=current_volume,
                avg_volume=avg_volume,
                volume_ratio=volume_ratio,
                is_expanded=is_expanded
            )
            
        except Exception as e:
            logger.error(f"分析成交量失败: {e}")
            return None
    
    @staticmethod
    def analyze_stock(
        df: pd.DataFrame,
        period: str = "monthly"
    ) -> dict:
        """
        综合分析单只股票的技术指标
        
        Args:
            df: 股票数据DataFrame
            period: 周期 (monthly/weekly)
        
        Returns:
            分析结果字典
        """
        result = {
            "period": period,
            "macd_golden_cross": False,
            "kdj_golden_cross": False,
            "volume_expanded": False,
            "volume_ratio": 0.0,
            "latest_close": 0.0,
            "latest_date": None
        }
        
        if df is None or len(df) < 26:
            logger.warning(f"数据不足，无法分析")
            return result
        
        # 计算MACD
        macd_result = TechnicalIndicators.calculate_macd(df)
        if macd_result:
            result["macd_golden_cross"] = macd_result.golden_cross
            result["macd_dif"] = macd_result.dif.iloc[-1]
            result["macd_dea"] = macd_result.dea.iloc[-1]
        
        # 计算KDJ
        kdj_result = TechnicalIndicators.calculate_kdj(df)
        if kdj_result:
            result["kdj_golden_cross"] = kdj_result.golden_cross
            result["kdj_k"] = kdj_result.k.iloc[-1]
            result["kdj_d"] = kdj_result.d.iloc[-1]
            result["kdj_j"] = kdj_result.j.iloc[-1]
        
        # 分析成交量
        volume_result = TechnicalIndicators.analyze_volume(df)
        if volume_result:
            result["volume_expanded"] = volume_result.is_expanded
            result["volume_ratio"] = volume_result.volume_ratio
            result["current_volume"] = volume_result.current_volume
        
        # 最新价格和日期
        result["latest_close"] = df['close'].iloc[-1]
        result["latest_date"] = df['date'].iloc[-1]
        
        return result


# 全局指标计算器实例
indicators = TechnicalIndicators()


if __name__ == "__main__":
    # 测试代码
    import sys
    sys.path.insert(0, '.')
    from collector import collector
    
    # 获取测试数据
    test_code = "000001"
    df = collector.get_monthly_data(test_code)
    
    if df is not None:
        print(f"分析股票 {test_code} 月线数据:")
        result = indicators.analyze_stock(df, "monthly")
        print(f"MACD金叉: {result['macd_golden_cross']}")
        print(f"KDJ金叉: {result['kdj_golden_cross']}")
        print(f"成交量放大: {result['volume_expanded']} (量比: {result['volume_ratio']:.2f})")