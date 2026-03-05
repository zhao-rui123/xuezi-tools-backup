"""
卖出策略与风险控制模块
"""
import pandas as pd
from datetime import datetime
import config


def calculate_deviation_from_ma(data, ma_period=5):
    """
    计算股价偏离均线百分比
    
    Returns:
        float: 偏离百分比
    """
    if len(data) < 1:
        return None
    
    current_price = data['close'].iloc[-1]
    ma_col = f'MA{ma_period}'
    
    if ma_col not in data.columns:
        return None
    
    ma_value = data[ma_col].iloc[-1]
    
    if pd.isna(ma_value) or ma_value == 0:
        return None
    
    deviation = (current_price - ma_value) / ma_value * 100
    return round(deviation, 2)


def check_kdj_overbought(data, threshold=80):
    """
    检查KDJ是否超买
    
    Returns:
        bool: K>threshold
    """
    if len(data) < 1:
        return False
    
    k_value = data['KDJ_K'].iloc[-1]
    
    if pd.isna(k_value):
        return False
    
    return k_value > threshold


def check_kdj_bearish_cross(data):
    """
    检查KDJ死叉
    
    Returns:
        bool: 当月K<D 且 上月K>=上月D
    """
    if len(data) < 2:
        return False
    
    current_cross = data['KDJ_K'].iloc[-1] < data['KDJ_D'].iloc[-1]
    prev_cross = data['KDJ_K'].iloc[-2] >= data['KDJ_D'].iloc[-2]
    
    return current_cross and prev_cross


def check_macd_bearish_cross(data):
    """
    检查MACD死叉（月线趋势破坏信号）
    
    Returns:
        bool: 当月DIF<DEA 且 上月DIF>=上月DEA
    """
    if len(data) < 2:
        return False
    
    current_cross = data['MACD_DIF'].iloc[-1] < data['MACD_DEA'].iloc[-1]
    prev_cross = data['MACD_DIF'].iloc[-2] >= data['MACD_DEA'].iloc[-2]
    
    return current_cross and prev_cross


def check_price_below_ma(data, ma_period=20):
    """
    检查股价是否跌破均线
    
    Returns:
        bool: 收盘价 < MA
    """
    if len(data) < 1:
        return False
    
    ma_col = f'MA{ma_period}'
    if ma_col not in data.columns:
        return False
    
    return data['close'].iloc[-1] < data[ma_col].iloc[-1]


def generate_sell_signals(data):
    """
    生成卖出/减仓信号
    
    Returns:
        dict: 各类卖出信号
    """
    signals = {
        'deviation_from_ma5': calculate_deviation_from_ma(data, 5),
        'kdj_overbought': check_kdj_overbought(data),
        'kdj_bearish_cross': check_kdj_bearish_cross(data),
        'macd_bearish_cross': check_macd_bearish_cross(data),
        'price_below_ma20': check_price_below_ma(data, 20)
    }
    
    # 生成操作建议
    suggestions = []
    
    # 偏离度减仓
    deviation = signals['deviation_from_ma5']
    if deviation and deviation > 20:
        suggestions.append({
            'type': '减仓',
            'priority': '高',
            'reason': f'股价偏离5月均线{deviation}%，建议减仓1/3-1/2',
            'action': '减仓1/3-1/2，留足底仓'
        })
    elif deviation and deviation > 10:
        suggestions.append({
            'type': '减仓',
            'priority': '中',
            'reason': f'股价偏离5月均线{deviation}%，可考虑适当减仓',
            'action': '减仓1/4-1/3'
        })
    
    # KDJ超买死叉
    if signals['kdj_overbought'] and signals['kdj_bearish_cross']:
        suggestions.append({
            'type': '减仓',
            'priority': '高',
            'reason': '日线KDJ超买区(>80)且死叉',
            'action': '减仓1/3-1/2'
        })
    
    # MACD死叉（月线趋势破坏）
    if signals['macd_bearish_cross']:
        suggestions.append({
            'type': '清仓',
            'priority': '最高',
            'reason': '月线MACD死叉，趋势破坏',
            'action': '考虑清仓或大幅减仓'
        })
    
    # 跌破20月均线
    if signals['price_below_ma20']:
        suggestions.append({
            'type': '止损',
            'priority': '高',
            'reason': '股价跌破20月均线',
            'action': '触发止损，考虑离场'
        })
    
    signals['suggestions'] = suggestions
    signals['hold_recommendation'] = '持有' if not suggestions else '建议操作'
    
    return signals


def generate_buyback_strategy(current_price, ma5_value):
    """
    生成回补策略
    
    Args:
        current_price: 当前价格
        ma5_value: 5月均线值
    
    Returns:
        dict: 回补建议
    """
    if not ma5_value or ma5_value == 0:
        return None
    
    deviation = (current_price - ma5_value) / ma5_value * 100
    
    if deviation <= -10:
        return {
            'signal': '强烈回补',
            'reason': f'股价低于5月均线{abs(deviation):.1f}%，偏离度达到回补区间',
            'action': '分批回补，建议回补减仓部分的50-80%',
            'deviation': round(deviation, 2)
        }
    elif deviation <= -5:
        return {
            'signal': '可考虑回补',
            'reason': f'股价低于5月均线{abs(deviation):.1f}%',
            'action': '小仓位试探性回补',
            'deviation': round(deviation, 2)
        }
    else:
        return {
            'signal': '等待',
            'reason': f'股价接近5月均线（偏离{deviation:.1f}%），未到理想回补点',
            'action': '继续等待回踩',
            'deviation': round(deviation, 2)
        }


class PositionManager:
    """
    仓位管理器
    """
    
    @staticmethod
    def get_initial_position_limit(grade):
        """
        根据评级获取首次建仓上限
        
        Args:
            grade: 'A', 'B', 'C'
        
        Returns:
            int: 仓位上限百分比
        """
        limits = {
            'A': 30,  # A级：首次建仓不超过30%
            'B': 20,  # B级：首次建仓不超过20%
            'C': 15   # C级：首次建仓不超过15%
        }
        return limits.get(grade, 10)
    
    @staticmethod
    def get_single_stock_limit():
        """单一股票仓位上限"""
        return 30  # 单一股票不超过30%
    
    @staticmethod
    def get_total_position_by_market(market_condition='normal'):
        """
        根据市场环境调整总仓位
        
        Args:
            market_condition: 'bull', 'normal', 'bear'
        
        Returns:
            int: 建议总仓位百分比
        """
        limits = {
            'bull': 80,    # 牛市：80%
            'normal': 60,  # 震荡：60%
            'bear': 40     # 熊市：40%
        }
        return limits.get(market_condition, 60)