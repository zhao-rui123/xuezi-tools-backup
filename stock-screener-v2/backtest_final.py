#!/usr/bin/env python3
"""
A股周线量化回测策略
策略：双金叉买入（周MACD金叉 + 周KDJ金叉）
卖出条件：
    1. 买入后三个月内，单月K线涨幅>50%
    2. 买入后金叉变死叉
    3. 买入三个月出现亏损（浮亏）
"""

import os
import sys
import json
import pickle
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd

# 激活虚拟环境
VENV_SITE_PACKAGES = os.path.expanduser("~/.openclaw/workspace/venv/lib/python3.14/site-packages")
if VENV_SITE_PACKAGES not in sys.path:
    sys.path.insert(0, VENV_SITE_PACKAGES)

import baostock as bs
from tqdm import tqdm

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 配置路径
BASE_DIR = os.path.expanduser("~/.openclaw/workspace/stock-screener-v2")
CACHE_DIR = os.path.join(BASE_DIR, "cache/data")
BACKTEST_DIR = os.path.join(BASE_DIR, "backtest_results")
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(BACKTEST_DIR, exist_ok=True)

# 策略参数
INITIAL_CAPITAL = 1_000_000  # 初始资金100万
MACD_FAST, MACD_SLOW, MACD_SIGNAL = 12, 26, 9  # MACD参数
KDJ_N, KDJ_M1, KDJ_M2 = 23, 3, 3  # KDJ参数


def get_a_stock_list() -> List[str]:
    """获取A股股票列表"""
    cache_file = os.path.join(CACHE_DIR, "a_stock_list.pkl")
    
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    logger.info("获取A股股票列表...")
    lg = bs.login()
    
    rs = bs.query_stock_basic()
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    df = pd.DataFrame(data_list, columns=rs.fields)
    bs.logout()
    
    # 过滤：sh.6开头是上海A股，sz.0/3开头是深圳A股
    a_stock = df[df['code'].str.match(r'^sh\.[6]|sz\.[03]')]
    stock_codes = a_stock['code'].tolist()
    
    with open(cache_file, 'wb') as f:
        pickle.dump(stock_codes, f)
    
    logger.info(f"获取到 {len(stock_codes)} 只A股")
    return stock_codes


def get_weekly_data(stock_code: str) -> Optional[pd.DataFrame]:
    """获取股票的周K线数据"""
    cache_file = os.path.join(CACHE_DIR, f"{stock_code.replace('.', '_')}_weekly.pkl")
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'rb') as f:
                df = pickle.load(f)
                if isinstance(df, pd.DataFrame) and len(df) > 0:
                    return df
        except Exception as e:
            logger.warning(f"读取缓存失败 {stock_code}: {e}")
    
    try:
        rs = bs.query_history_k_data_plus(
            stock_code,
            'date,open,high,low,close,volume',
            start_date='20150101',
            end_date=datetime.now().strftime('%Y%m%d'),
            frequency='w',
            adjustflag='3'
        )
        
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        
        if not data_list:
            return None
            
        df = pd.DataFrame(data_list, columns=rs.fields)
        
        # 数据类型转换
        df['date'] = pd.to_datetime(df['date'])
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = df.dropna().sort_values('date').reset_index(drop=True)
        
        if len(df) > 60:  # 至少60周数据
            with open(cache_file, 'wb') as f:
                pickle.dump(df, f)
            return df
            
    except Exception as e:
        pass
    
    return None


def calculate_macd(df: pd.DataFrame) -> pd.DataFrame:
    """计算MACD指标"""
    if len(df) < MACD_SLOW:
        return df
    
    df = df.copy()
    close = df['close'].values
    
    # 计算EMA
    ema_fast = pd.Series(close).ewm(span=MACD_FAST, adjust=False).mean()
    ema_slow = pd.Series(close).ewm(span=MACD_SLOW, adjust=False).mean()
    
    # DIF
    df['macd_dif'] = ema_fast - ema_slow
    # DEA
    df['macd_dea'] = df['macd_dif'].ewm(span=MACD_SIGNAL, adjust=False).mean()
    # MACD柱
    df['macd_hist'] = (df['macd_dif'] - df['macd_dea']) * 2
    
    return df


def calculate_kdj(df: pd.DataFrame) -> pd.DataFrame:
    """计算KDJ指标"""
    if len(df) < KDJ_N:
        return df
    
    df = df.copy()
    low_n = df['low'].rolling(window=KDJ_N).min()
    high_n = df['high'].rolling(window=KDJ_N).max()
    
    rsv = (df['close'] - low_n) / (high_n - low_n) * 100
    rsv = rsv.fillna(50)
    
    df['kdj_k'] = rsv.ewm(com=(KDJ_M1 - 1), adjust=False).mean()
    df['kdj_d'] = df['kdj_k'].ewm(com=(KDJ_M2 - 1), adjust=False).mean()
    df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']
    
    return df


def get_signal(df: pd.DataFrame, idx: int) -> Tuple[bool, bool]:
    """获取某一周的双金叉信号"""
    if idx < 2:
        return False, False
    
    # MACD金叉：DIF从下方穿过DEA
    macd_golden = df['macd_dif'].iloc[idx-1] < df['macd_dea'].iloc[idx-1] and \
                  df['macd_dif'].iloc[idx] > df['macd_dea'].iloc[idx]
    
    # KDJ金叉：K从下方穿过D
    kdj_golden = df['kdj_k'].iloc[idx-1] < df['kdj_d'].iloc[idx-1] and \
                 df['kdj_k'].iloc[idx] > df['kdj_d'].iloc[idx]
    
    return macd_golden, kdj_golden


def check_death_cross(df: pd.DataFrame, idx: int) -> bool:
    """检查是否死叉"""
    if idx < 1:
        return False
    
    # MACD死叉
    macd_dead = df['macd_dif'].iloc[idx-1] > df['macd_dea'].iloc[idx-1] and \
                df['macd_dif'].iloc[idx] < df['macd_dea'].iloc[idx]
    
    # KDJ死叉
    kdj_dead = df['kdj_k'].iloc[idx-1] > df['kdj_d'].iloc[idx-1] and \
               df['kdj_k'].iloc[idx] < df['kdj_d'].iloc[idx]
    
    return macd_dead or kdj_dead


class Backtester:
    def __init__(self):
        self.cash = INITIAL_CAPITAL
        self.positions = {}
        self.portfolio_value = []
        self.trades = []
        
    def buy(self, stock_code: str, price: float, date: str, week_idx: int):
        """买入股票"""
        num_positions = len(self.positions) + 1
        position_value = self.cash / num_positions
        
        shares = int(position_value / price)
        cost = shares * price
        
        if cost > self.cash:
            shares = int(self.cash / price)
            cost = shares * price
        
        if shares > 0:
            self.cash -= cost
            self.positions[stock_code] = {
                'shares': shares,
                'buy_price': price,
                'buy_date': date,
                'buy_idx': week_idx,
            }
            self.trades.append({
                'type': 'buy',
                'stock': stock_code,
                'price': price,
                'shares': shares,
                'date': date
            })
    
    def sell(self, stock_code: str, price: float, reason: str):
        """卖出股票"""
        if stock_code not in self.positions:
            return
        
        position = self.positions[stock_code]
        revenue = position['shares'] * price
        self.cash += revenue
        
        profit = (price - position['buy_price']) / position['buy_price'] * 100
        
        self.trades.append({
            'type': 'sell',
            'stock': stock_code,
            'price': price,
            'shares': position['shares'],
            'date': str(date),
            'reason': reason,
            'profit_pct': profit
        })
        
        del self.positions[stock_code]
    
    def get_portfolio_value(self, prices: Dict[str, float]) -> float:
        """计算当前组合市值"""
        positions_value = sum(
            pos['shares'] * prices.get(stock, pos['buy_price'])
            for stock, pos in self.positions.items()
        )
        return self.cash + positions_value
    
    def record_weekly(self, date, prices: Dict[str, float]):
        """记录每周组合价值"""
        value = self.get_portfolio_value(prices)
        if isinstance(date, str):
            year = pd.to_datetime(date).year
        else:
            year = date.year
        self.portfolio_value.append({
            'date': str(date),
            'value': value,
            'year': year
        })
    
    def calculate_returns(self):
        """计算收益率"""
        if not self.portfolio_value:
            return 0, 0, {}
        
        start_value = self.portfolio_value[0]['value']
        end_value = self.portfolio_value[-1]['value']
        
        total_return = (end_value - start_value) / start_value * 100
        
        # 计算最大回撤
        peak = start_value
        max_drawdown = 0
        for record in self.portfolio_value:
            if record['value'] > peak:
                peak = record['value']
            drawdown = (peak - record['value']) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # 计算年度收益率
        yearly_returns = {}
        year_data = {}
        
        for record in self.portfolio_value:
            year = record['year']
            if year not in year_data:
                year_data[year] = record['value']
        
        years = sorted(year_data.keys())
        for i, year in enumerate(years):
            if i == 0:
                yearly_returns[year] = (year_data[year] - start_value) / start_value * 100
            else:
                prev_year = years[i-1]
                yearly_returns[year] = (year_data[year] - year_data[prev_year]) / year_data[prev_year] * 100
        
        return total_return, -max_drawdown, yearly_returns


def run_backtest():
    """运行回测"""
    logger.info("=" * 50)
    logger.info("A股周线双金叉策略回测")
    logger.info("=" * 50)
    
    # 获取股票列表
    stock_codes = get_a_stock_list()
    logger.info(f"共 {len(stock_codes)} 只股票")
    
    if not stock_codes:
        logger.error("无法获取股票列表")
        return
    
    # 初始化回测器
    backtester = Backtester()
    
    # 加载周K线数据
    logger.info("加载周K线数据...")
    stock_weekly_data = {}
    
    # 使用采样，先测试一部分
    sample_codes = stock_codes[:500]  # 500只测试
    
    for code in tqdm(sample_codes, desc="加载数据"):
        df = get_weekly_data(code)
        if df is not None and len(df) > 60:
            df = calculate_macd(df)
            df = calculate_kdj(df)
            stock_weekly_data[code] = df
    
    logger.info(f"成功加载 {len(stock_weekly_data)} 只股票数据")
    
    if not stock_weekly_data:
        logger.error("没有加载到任何股票数据")
        return
    
    # 找到所有股票数据的公共日期范围
    all_dates = set()
    for df in stock_weekly_data.values():
        all_dates.update(df['date'].tolist())
    
    sorted_dates = sorted(all_dates)
    
    # 找到最早日期
    start_date = sorted_dates[0]
    logger.info(f"回测开始日期: {start_date}")
    logger.info(f"共 {len(sorted_dates)} 周")
    
    # 按周遍历
    logger.info("开始回测...")
    
    current_prices = {}
    
    for week_idx, week_date in enumerate(sorted_dates):
        week_date_str = week_date.strftime('%Y-%m-%d')
        
        # 更新当前价格
        for code, df in stock_weekly_data.items():
            if week_date in df['date'].values:
                idx = df[df['date'] == week_date].index[0]
                current_prices[code] = df.loc[idx, 'close']
        
        # 检查是否需要卖出
        sell_list = []
        for code, position in list(backtester.positions.items()):
            if code not in stock_weekly_data:
                continue
            
            df = stock_weekly_data[code]
            if week_date not in df['date'].values:
                continue
            
            idx = df[df['date'] == week_date].index[0]
            current_price = df.loc[idx, 'close']
            buy_price = position['buy_price']
            
            # 条件2：买入后金叉变死叉
            if idx > position['buy_idx']:
                if check_death_cross(df, idx):
                    sell_list.append((code, current_price, '死叉'))
                    continue
            
            # 条件3：买入三个月出现亏损（浮亏）
            weeks_held = week_idx - position['buy_idx']
            if weeks_held >= 12:
                if current_price < buy_price:
                    sell_list.append((code, current_price, '浮亏'))
        
        # 执行卖出
        for code, price, reason in sell_list:
            backtester.sell(code, price, reason)
        
        # 检查买入信号
        buy_signals = []
        for code, df in stock_weekly_data.items():
            if code in backtester.positions:
                continue
            
            if week_date not in df['date'].values:
                continue
            
            idx = df[df['date'] == week_date].index[0]
            
            if idx < 60:
                continue
            
            macd_golden, kdj_golden = get_signal(df, idx)
            
            if macd_golden and kdj_golden:
                buy_signals.append((code, df.loc[idx, 'close'], week_date_str))
        
        # 执行买入
        for code, price, date in buy_signals[:5]:
            backtester.buy(code, price, date, week_idx)
        
        # 记录每周组合价值
        backtester.record_weekly(week_date, current_prices)
    
    # 计算结果
    total_return, max_drawdown, yearly_returns = backtester.calculate_returns()
    
    # 输出结果
    logger.info("=" * 50)
    logger.info("回测结果")
    logger.info("=" * 50)
    logger.info(f"最终收益率: {total_return:.2f}%")
    logger.info(f"最大回撤: {-max_drawdown:.2f}%")
    logger.info(f"年度收益率: {yearly_returns}")
    logger.info(f"总交易次数: {len(backtester.trades)}")
    
    # 保存结果
    result = {
        'final_return': f"{total_return:.2f}%",
        'max_drawdown': f"{-max_drawdown:.2f}%",
        'yearly_returns': {str(k): f"{v:.2f}%" for k, v in yearly_returns.items()},
        'total_trades': len(backtester.trades)
    }
    
    result_file = os.path.join(BACKTEST_DIR, "backtest_result.json")
    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    logger.info(f"结果已保存到: {result_file}")
    
    return result


if __name__ == "__main__":
    run_backtest()
