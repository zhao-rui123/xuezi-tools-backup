#!/usr/bin/env python3
"""
KDJ+MACD 选股策略回测程序
- 买入：KDJ金叉(K<30) + MACD金叉
- 卖出：涨20% 或 双死叉 或 亏5%
- 全仓买入
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import tushare as ts

# Tushare Token - 使用代理
TUSHARE_TOKEN = "6d8f34a35c3b6a3c80e529f4ebcf11e707ff71c066062d5c4619eb35e5d9"
TUSHARE_URL = "http://lianghua.nanyangqiankun.top"

# 回测参数
INITIAL_CAPITAL = 100000  # 初始资金10万
START_DATE = "20200101"
END_DATE = "20250316"

# 策略参数
KDJ_OVERSOLD = 30  # KDJ超卖阈值
TAKE_PROFIT = 0.20  # 止盈20%
STOP_LOSS = -0.05  # 止损5%


def calculate_kdj(df: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
    df = df.copy()
    low_min = df['low'].rolling(window=n, min_periods=1).min()
    high_max = df['high'].rolling(window=n, min_periods=1).max()
    rsv = (df['close'] - low_min) / (high_max - low_min) * 100
    rsv = rsv.fillna(50)
    df['k'] = rsv.ewm(alpha=1/m1, adjust=False).mean()
    df['d'] = df['k'].ewm(alpha=1/m2, adjust=False).mean()
    df['j'] = 3 * df['k'] - 2 * df['d']
    return df


def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    df = df.copy()
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    df['dif'] = ema_fast - ema_slow
    df['dea'] = df['dif'].ewm(span=signal, adjust=False).mean()
    df['macd'] = 2 * (df['dif'] - df['dea'])
    return df


def backtest_stock(ts_code: str, pro) -> Dict:
    try:
        df = pro.daily(ts_code=ts_code, start_date=START_DATE, end_date=END_DATE)
        if df is None or df.empty:
            return None
        
        df = df.sort_values('trade_date', ascending=True).reset_index(drop=True)
        df.columns = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 
                     'pre_close', 'change', 'pct_chg', 'vol', 'amount']
        
        df = calculate_kdj(df)
        df = calculate_macd(df)
        
        cash = INITIAL_CAPITAL
        shares = 0
        position_price = 0
        trades = []
        
        for i in range(1, len(df)):
            prev_row = df.iloc[i-1]
            row = df.iloc[i]
            current_price = row['close']
            current_date = row['trade_date']
            
            if shares == 0:
                # 买入：KDJ金叉(K<30) + MACD金叉
                kdj_golden = (prev_row['k'] <= prev_row['d']) and (row['k'] > row['d']) and (row['k'] < KDJ_OVERSOLD)
                macd_golden = (prev_row['dif'] <= prev_row['dea']) and (row['dif'] > row['dea'])
                
                if kdj_golden and macd_golden:
                    shares = int(cash / current_price)
                    position_price = current_price
                    cash = cash - shares * current_price
                    trades.append({'date': current_date, 'action': 'BUY', 'price': current_price, 'shares': shares})
            else:
                profit_ratio = (current_price - position_price) / position_price
                
                # 卖出：涨20% 或 双死叉 或 亏5%
                kdj_death = (prev_row['k'] > prev_row['d']) and (row['k'] <= row['d'])
                macd_death = (prev_row['dif'] > prev_row['dea']) and (row['dif'] <= row['dea'])
                
                should_sell = (profit_ratio >= TAKE_PROFIT) or (kdj_death and macd_death) or (profit_ratio <= STOP_LOSS)
                
                if should_sell:
                    cash = cash + shares * current_price
                    trades.append({'date': current_date, 'action': 'SELL', 'price': current_price, 'shares': shares, 'profit_ratio': profit_ratio})
                    shares = 0
                    position_price = 0
        
        if shares > 0:
            final_price = df.iloc[-1]['close']
            cash = cash + shares * final_price
        
        total_return = (cash - INITIAL_CAPITAL) / INITIAL_CAPITAL
        
        return {
            'ts_code': ts_code,
            'initial_capital': INITIAL_CAPITAL,
            'final_value': cash,
            'total_return': total_return,
            'trades': trades
        }
        
    except Exception as e:
        print(f"回测 {ts_code} 失败: {e}")
        return None


def main():
    # 初始化Tushare
    ts.set_token(TUSHARE_TOKEN)
    pro = ts.pro_api()
    pro._DataApi__http_url = TUSHARE_URL
    
    # 备用股票列表
    stock_list = [
        '600000.SH', '600036.SH', '600030.SH', '600016.SH', '600519.SH',
        '000001.SZ', '000002.SZ', '000333.SZ', '000651.SZ', '000858.SZ',
        '600887.SH', '600276.SH', '600585.SH', '600690.SH', '600309.SH',
        '601857.SH', '601888.SH', '601318.SH', '601166.SH', '600028.SH',
        '000063.SZ', '000725.SZ', '000768.SZ', '000732.SZ', '600050.SH',
        '600004.SH', '600009.SH', '600010.SH', '600011.SH', '600015.SH',
        '600018.SH', '600019.SH', '600031.SH', '600048.SH', '600104.SH',
        '600109.SH', '600111.SH', '600150.SH', '600170.SH', '600176.SH',
        '600177.SH', '600183.SH', '600196.SH', '600406.SH', '600547.SH',
        '600570.SH', '600585.SH', '600690.SH', '600703.SH', '600745.SH',
        '600809.SH', '600837.SH', '600887.SH', '600893.SH'
    ]
    
    print(f"开始回测 {len(stock_list)} 只股票...")
    
    results = []
    total_return_list = []
    
    for i, ts_code in enumerate(stock_list):
        if (i + 1) % 10 == 0:
            print(f"进度: {i+1}/{len(stock_list)}")
        
        result = backtest_stock(ts_code, pro)
        if result:
            results.append(result)
            if result['total_return'] != 0:
                total_return_list.append(result['total_return'])
    
    # 汇总统计
    if not results:
        print("没有有效的回测结果")
        return
    
    # 按收益率排序
    results.sort(key=lambda x: x['total_return'], reverse=True)
    
    # 计算统计数据
    avg_return = np.mean(total_return_list) if total_return_list else 0
    max_return = max(total_return_list) if total_return_list else 0
    min_return = min(total_return_list) if total_return_list else 0
    
    # 计算最大回撤（简化）
    all_returns = sorted([r['total_return'] for r in results])
    max_drawdown = all_returns[0] - all_returns[-1] if len(all_returns) > 1 else 0
    
    # 计算年度收益率（假设5年）
    years = 5.2
    annual_return = ((1 + avg_return) ** (1/years) - 1) if avg_return > -1 else -1
    
    summary = {
        'strategy': 'KDJ金叉(K<30)+MACD金叉 买入, 涨20%/双死叉/亏5% 卖出',
        'period': f'{START_DATE} - {END_DATE}',
        'initial_capital': INITIAL_CAPITAL,
        'stocks_tested': len(stock_list),
        'stocks_with_trades': len(results),
        'average_return': round(avg_return * 100, 2),
        'max_return': round(max_return * 100, 2),
        'min_return': round(min_return * 100, 2),
        'max_drawdown': round(max_drawdown * 100, 2),
        'annual_return': round(annual_return * 100, 2),
        'top_performers': results[:5]
    }
    
    # 保存结果
    output_path = '/Users/zhaoruicn/.openclaw/workspace/stock-screener-v2/backtest_results/backtest_results.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*50)
    print("回测结果摘要")
    print("="*50)
    print(f"策略: {summary['strategy']}")
    print(f"回测周期: {summary['period']}")
    print(f"测试股票数: {summary['stocks_tested']}")
    print(f"有交易的股票数: {summary['stocks_with_trades']}")
    print(f"平均收益率: {summary['average_return']}%")
    print(f"最大收益率: {summary['max_return']}%")
    print(f"最小收益率: {summary['min_return']}%")
    print(f"最大回撤: {summary['max_drawdown']}%")
    print(f"年化收益率: {summary['annual_return']}%")
    print(f"\n结果已保存到: {output_path}")


if __name__ == '__main__':
    main()
