"""
技术指标计算服务 - MACD/KDJ
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from config import settings
from utils.logger import logger


@dataclass
class MACDResult:
    """MACD计算结果"""
    dif: pd.Series
    dea: pd.Series  
    macd: pd.Series
    golden_cross: bool  # 金叉
    dead_cross: bool    # 死叉
    

@dataclass
class KDJResult:
    """KDJ计算结果"""
    k: pd.Series
    d: pd.Series
    j: pd.Series
    golden_cross: bool  # 金叉
    dead_cross: bool    # 死叉


class IndicatorService:
    """技术指标服务"""
    
    @staticmethod
    def calculate_macd(close: pd.Series, fast: int = None, 
                       slow: int = None, signal: int = None) -> MACDResult:
        """
        计算MACD指标
        
        Args:
            close: 收盘价序列
            fast: 快线周期，默认使用配置
            slow: 慢线周期，默认使用配置
            signal: 信号线周期，默认使用配置
        
        Returns:
            MACDResult: MACD计算结果
        """
        try:
            # 使用配置参数或默认值
            fast = fast or settings.MACD_FAST
            slow = slow or settings.MACD_SLOW
            signal = signal or settings.MACD_SIGNAL
            
            # 计算EMA
            ema_fast = close.ewm(span=fast, adjust=False).mean()
            ema_slow = close.ewm(span=slow, adjust=False).mean()
            
            # DIF = EMA(fast) - EMA(slow)
            dif = ema_fast - ema_slow
            
            # DEA = EMA(DIF, signal)
            dea = dif.ewm(span=signal, adjust=False).mean()
            
            # MACD = 2 * (DIF - DEA)
            macd = 2 * (dif - dea)
            
            # 判断金叉死叉
            golden_cross = False
            dead_cross = False
            
            if len(dif) >= 2 and len(dea) >= 2:
                # 金叉：昨天DIF<DEA，今天DIF>DEA
                if dif.iloc[-2] < dea.iloc[-2] and dif.iloc[-1] > dea.iloc[-1]:
                    golden_cross = True
                # 死叉：昨天DIF>DEA，今天DIF<DEA
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
            return MACDResult(
                dif=pd.Series(),
                dea=pd.Series(),
                macd=pd.Series(),
                golden_cross=False,
                dead_cross=False
            )
    
    @staticmethod
    def calculate_kdj(high: pd.Series, low: pd.Series, close: pd.Series,
                      n: int = None, m1: int = None, m2: int = None) -> KDJResult:
        """
        计算KDJ指标
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            n: RSV周期，默认使用配置
            m1: K平滑系数，默认使用配置
            m2: D平滑系数，默认使用配置
        
        Returns:
            KDJResult: KDJ计算结果
        """
        try:
            # 使用配置参数或默认值
            n = n or settings.KDJ_N
            m1 = m1 or settings.KDJ_M1
            m2 = m2 or settings.KDJ_M2
            
            # 计算RSV
            # RSV = (收盘价 - N日内最低价) / (N日内最高价 - N日内最低价) * 100
            lowest_low = low.rolling(window=n, min_periods=1).min()
            highest_high = high.rolling(window=n, min_periods=1).max()
            
            # 避免除以0
            rsv = 100 * (close - lowest_low) / (highest_high - lowest_low)
            rsv = rsv.fillna(50)
            
            # 计算K值
            k = pd.Series(index=close.index, dtype=float)
            k.iloc[0] = 50
            for i in range(1, len(rsv)):
                k.iloc[i] = (m1 - 1) / m1 * k.iloc[i-1] + 1 / m1 * rsv.iloc[i]
            
            # 计算D值
            d = pd.Series(index=close.index, dtype=float)
            d.iloc[0] = 50
            for i in range(1, len(k)):
                d.iloc[i] = (m2 - 1) / m2 * d.iloc[i-1] + 1 / m2 * k.iloc[i]
            
            # 计算J值
            j = 3 * k - 2 * d
            
            # 判断金叉死叉
            golden_cross = False
            dead_cross = False
            
            if len(k) >= 2 and len(d) >= 2:
                # 金叉：昨天K<D，今天K>D
                if k.iloc[-2] < d.iloc[-2] and k.iloc[-1] > d.iloc[-1]:
                    golden_cross = True
                # 死叉：昨天K>D，今天K<D
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
            return KDJResult(
                k=pd.Series(),
                d=pd.Series(),
                j=pd.Series(),
                golden_cross=False,
                dead_cross=False
            )
    
    @staticmethod
    def calculate_ma(close: pd.Series, period: int) -> pd.Series:
        """计算移动平均线"""
        return close.rolling(window=period, min_periods=1).mean()
    
    @staticmethod
    def calculate_volume_ratio(volume: pd.Series, period: int = 5) -> float:
        """
        计算成交量放大倍数
        
        Args:
            volume: 成交量序列
            period: 平均周期
        
        Returns:
            成交量放大倍数
        """
        try:
            if len(volume) < period + 1:
                return 1.0
            
            # 今日成交量
            today_volume = volume.iloc[-1]
            
            # 前period日平均成交量
            avg_volume = volume.iloc[-(period+1):-1].mean()
            
            if avg_volume == 0:
                return 1.0
            
            return today_volume / avg_volume
            
        except Exception as e:
            logger.error(f"计算成交量放大倍数失败: {e}")
            return 1.0
    
    @staticmethod
    def is_price_volume_rise(df: pd.DataFrame, price_change_threshold: float = 0.03) -> bool:
        """
        判断是否量价齐升
        
        Args:
            df: 包含价格、成交量数据的DataFrame
            price_change_threshold: 涨幅阈值
        
        Returns:
            是否量价齐升
        """
        try:
            if len(df) < 2:
                return False
            
            # 计算今日涨幅
            price_change = (df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]
            
            # 计算成交量放大倍数
            volume_ratio = IndicatorService.calculate_volume_ratio(df['volume'])
            
            # 量价齐升：价格上涨且成交量放大
            return price_change >= price_change_threshold and volume_ratio >= settings.MIN_VOLUME_RATIO
            
        except Exception as e:
            logger.error(f"判断量价齐升失败: {e}")
            return False
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> Dict:
        """
        计算所有技术指标
        
        Args:
            df: K线数据DataFrame
        
        Returns:
            指标结果字典
        """
        try:
            if df.empty or len(df) < 30:
                return {}
            
            # MACD
            macd_result = IndicatorService.calculate_macd(df['close'])
            
            # KDJ
            kdj_result = IndicatorService.calculate_kdj(df['high'], df['low'], df['close'])
            
            # 成交量放大
            volume_ratio = IndicatorService.calculate_volume_ratio(df['volume'])
            
            # 量价齐升
            price_volume_rise = IndicatorService.is_price_volume_rise(df)
            
            # 最新价格变化
            price_change = 0
            if len(df) >= 2:
                price_change = (df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]
            
            return {
                'macd_golden_cross': macd_result.golden_cross,
                'macd_dead_cross': macd_result.dead_cross,
                'macd_dif': round(macd_result.dif.iloc[-1], 4) if len(macd_result.dif) > 0 else 0,
                'macd_dea': round(macd_result.dea.iloc[-1], 4) if len(macd_result.dea) > 0 else 0,
                'macd_value': round(macd_result.macd.iloc[-1], 4) if len(macd_result.macd) > 0 else 0,
                
                'kdj_golden_cross': kdj_result.golden_cross,
                'kdj_dead_cross': kdj_result.dead_cross,
                'kdj_k': round(kdj_result.k.iloc[-1], 2) if len(kdj_result.k) > 0 else 0,
                'kdj_d': round(kdj_result.d.iloc[-1], 2) if len(kdj_result.d) > 0 else 0,
                'kdj_j': round(kdj_result.j.iloc[-1], 2) if len(kdj_result.j) > 0 else 0,
                
                'volume_ratio': round(volume_ratio, 2),
                'price_volume_rise': price_volume_rise,
                'price_change_pct': round(price_change * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"计算所有指标失败: {e}")
            return {}


# 全局指标服务实例
indicator_service = IndicatorService()