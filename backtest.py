"""
A股周线量化回测策略
策略规则:
- 买入条件: 周MACD金叉 + 周KDJ金叉（双金叉）
- 卖出条件（满足任一即卖出）:
  1. 买入后三个月内，单月K线涨幅>50%
  2. 买入后金叉变死叉
  3. 买入三个月出现亏损（浮亏）
- 仓位管理: 初始资金100万，每个股票仓位相同（动态平衡）
"""

import json
import os
import glob
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# 配置
DATA_DIR = "/opt/stock-screener-v2/cache/data/"
OUTPUT_DIR = "/opt/stock-screener-v2/backtest_results/"
INITIAL_CAPITAL = 1000000  # 初始资金100万
MAX_HOLDING_MONTHS = 3  # 最大持有月份

def load_stock_data(ts_code):
    """加载单只股票数据"""
    file_path = os.path.join(DATA_DIR, f"{ts_code}.json")
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"加载 {ts_code} 失败: {e}")
        return None

def calculate_ema(prices, period):
    """计算EMA"""
    if len(prices) < period:
        return []
    ema = []
    multiplier = 2 / (period + 1)
    
    # 使用SMA作为初始值
    sma = sum(prices[:period]) / period
    ema = [sma] * period
    
    for i in range(period, len(prices)):
        ema_value = (prices[i] - ema[-1]) * multiplier + ema[-1]
        ema.append(ema_value)
    
    return ema

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """计算MACD指标"""
    if len(prices) < slow:
        return [], [], []
    
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    
    # 对齐数据
    start_idx = slow - 1
    macd_line = []
    for i in range(start_idx, len(prices)):
        macd_line.append(ema_fast[i] - ema_slow[i])
    
    # 计算signal线
    if len(macd_line) < signal:
        return [], [], []
    
    signal_line = calculate_ema(macd_line, signal)
    
    # 计算histogram
    histogram = []
    for i in range(len(macd_line)):
        if i < len(signal_line):
            histogram.append(macd_line[i] - signal_line[i])
        else:
            histogram.append(0)
    
    return macd_line, signal_line, histogram

def calculate_kdj(highs, lows, closes, n=9, m1=3, m2=3):
    """计算KDJ指标"""
    if len(closes) < n:
        return [], [], []
    
    kdj_k = []
    kdj_d = []
    kdj_j = []
    
    for i in range(len(closes)):
        if i < n - 1:
            kdj_k.append(50)
            kdj_d.append(50)
            kdj_j.append(50)
        else:
            # 计算n日内最低价和最高价
            low_n = min(lows[i-n+1:i+1])
            high_n = max(highs[i-n+1:i+1])
            
            if high_n == low_n:
                rsv = 50
            else:
                rsv = (closes[i] - low_n) / (high_n - low_n) * 100
            
            # K值
            if i == n - 1:
                k = (2/3) * 50 + (1/3) * rsv
            else:
                k = (2/3) * kdj_k[-1] + (1/3) * rsv
            
            # D值
            if i == n - 1:
                d = (2/3) * 50 + (1/3) * k
            else:
                d = (2/3) * kdj_d[-1] + (1/3) * k
            
            # J值
            j = 3 * k - 2 * d
            
            kdj_k.append(k)
            kdj_d.append(d)
            kdj_j.append(j)
    
    return kdj_k, kdj_d, kdj_j

def get_weekly_indicators(weekly_data):
    """计算周线MACD和KDJ"""
    if not weekly_data or len(weekly_data) < 34:  # 需要足够的数据计算MACD
        return [], [], [], [], [], [], []
    
    # 按日期排序（从旧到新）
    sorted_data = sorted(weekly_data, key=lambda x: x['trade_date'])
    
    closes = [d['close'] for d in sorted_data]
    highs = [d['high'] for d in sorted_data]
    lows = [d['low'] for d in sorted_data]
    
    # 计算MACD
    macd_line, signal_line, histogram = calculate_macd(closes)
    
    # 计算KDJ
    kdj_k, kdj_d, kdj_j = calculate_kdj(highs, lows, closes)
    
    return macd_line, signal_line, histogram, kdj_k, kdj_d, kdj_j, sorted_data

def check_weekly_golden_cross(macd_line, kdj_k, kdj_d):
    """检查周线双金叉"""
    if len(macd_line) < 2 or len(kdj_k) < 2 or len(kdj_d) < 2:
        return False, ""
    
    # 当前金叉判断
    # MACD金叉: MACD线从负转正
    prev_macd = macd_line[-2]
    curr_macd = macd_line[-1]
    
    # KDJ金叉: K线从下往上穿越D线
    prev_k = kdj_k[-2]
    curr_k = kdj_k[-1]
    prev_d = kdj_d[-2]
    curr_d = kdj_d[-1]
    
    # 判断条件
    macd_golden = (prev_macd < 0 and curr_macd > 0)
    kdj_golden = (prev_k < prev_d and curr_k > curr_d)
    
    reason = ""
    if macd_golden and kdj_golden:
        reason = "周线双金叉"
    elif macd_golden:
        reason = "周线MACD金叉"
    elif kdj_golden:
        reason = "周线KDJ金叉"
    
    return (macd_golden and kdj_golden), reason

def check_death_cross(macd_line):
    """检查死叉（MACD从正转负）"""
    if len(macd_line) < 2:
        return False
    
    prev_macd = macd_line[-2]
    curr_macd = macd_line[-1]
    
    return prev_macd > 0 and curr_macd < 0

def run_backtest():
    """运行回测"""
    print("="*60)
    print("A股周线量化回测策略")
    print("="*60)
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 获取所有股票文件
    stock_files = glob.glob(os.path.join(DATA_DIR, "*.json"))
    print(f"发现 {len(stock_files)} 只股票")
    
    # 存储所有交易记录
    trades = []
    positions = {}  # 当前持仓 {ts_code: {'shares': 数量, 'cost': 成本, 'buy_date': 买入日期}}
    capital = INITIAL_CAPITAL
    yearly_returns = defaultdict(float)  # 年度收益率
    
    # 获取所有交易日期（周）
    all_weeks = set()
    for f in stock_files[:500]:  # 用500只股票获取日期范围
        data = load_stock_data(os.path.basename(f).replace('.json', ''))
        if data and 'weekly' in data:
            for w in data['weekly']:
                all_weeks.add(w['trade_date'])
    
    sorted_weeks = sorted(list(all_weeks))
    print(f"回测周期: {sorted_weeks[0]} 到 {sorted_weeks[-1]}")
    
    # 重新处理所有股票
    stock_data_cache = {}
    print("加载股票数据...")
    for i, f in enumerate(stock_files):
        ts_code = os.path.basename(f).replace('.json', '')
        data = load_stock_data(ts_code)
        if data and 'weekly' in data and data['weekly']:
            stock_data_cache[ts_code] = data
        if (i + 1) % 1000 == 0:
            print(f"已加载 {i+1}/{len(stock_files)}")
    
    print(f"成功加载 {len(stock_data_cache)} 只股票数据")
    
    # 按周回测
    print("\n开始回测...")
    for week_idx, trade_date in enumerate(sorted_weeks):
        if week_idx < 26:  # 跳过前面几周，等待技术指标稳定
            continue
            
        current_year = trade_date[:4]
        
        # 检查卖出条件
        positions_to_close = []
        for ts_code, pos in list(positions.items()):
            if ts_code not in stock_data_cache:
                continue
            
            data = stock_data_cache[ts_code]
            weekly_data = data.get('weekly', [])
            monthly_data = data.get('monthly', [])
            
            # 找到当前周在周线数据中的位置
            week_idx_in_data = -1
            for i, w in enumerate(weekly_data):
                if w['trade_date'] == trade_date:
                    week_idx_in_data = i
                    break
            
            if week_idx_in_data < 1:
                continue
            
            # 计算从买入到现在的技术指标
            recent_weeks = weekly_data[:week_idx_in_data+1]
            macd_line, signal_line, histogram, kdj_k, kdj_d, kdj_j, sorted_week = get_weekly_indicators(recent_weeks)
            
            if not macd_line:
                continue
            
            # 卖出条件1: 金叉变死叉
            if check_death_cross(macd_line):
                positions_to_close.append((ts_code, '死叉'))
                continue
            
            # 计算持有月份
            buy_date = pos['buy_date']
            buy_year = int(buy_date[:4])
            buy_month = int(buy_date[4:6])
            curr_year = int(trade_date[:4])
            curr_month = int(trade_date[4:6])
            months_held = (curr_year - buy_year) * 12 + (curr_month - buy_month)
            
            # 卖出条件2: 三个月后浮亏
            if months_held >= MAX_HOLDING_MONTHS:
                current_price = weekly_data[week_idx_in_data]['close']
                cost_price = pos['cost']
                if current_price < cost_price:
                    positions_to_close.append((ts_code, '浮亏'))
                    continue
            
            # 卖出条件3: 三个月内单月涨幅>50%
            if months_held < MAX_HOLDING_MONTHS:
                for m in monthly_data:
                    m_date = m['trade_date']
                    m_year = int(m_date[:4])
                    m_month = int(m_date[4:6])
                    
                    # 检查是否在持有期间
                    if (m_year > buy_year or (m_year == buy_year and m_month >= buy_month)) and \
                       (m_year < curr_year or (m_year == curr_year and m_month <= curr_month)):
                        if m['pct_chg'] > 50:  # 月涨幅>50%
                            positions_to_close.append((ts_code, f'月涨幅{m["pct_chg"]:.1f}%'))
                            break
        
        # 执行卖出
        for ts_code, reason in positions_to_close:
            if ts_code not in positions:
                continue
            
            data = stock_data_cache[ts_code]
            weekly_data = data.get('weekly', [])
            
            # 找到当前周收盘价
            current_price = None
            for w in weekly_data:
                if w['trade_date'] == trade_date:
                    current_price = w['close']
                    break
            
            if current_price is None:
                continue
            
            pos = positions[ts_code]
            shares = pos['shares']
            cost = pos['cost']
            
            sell_value = shares * current_price
            profit = sell_value - pos['shares'] * cost
            profit_pct = (current_price - cost) / cost * 100
            
            trades.append({
                'ts_code': ts_code,
                'name': data.get('name', ''),
                'buy_date': pos['buy_date'],
                'sell_date': trade_date,
                'buy_price': cost,
                'sell_price': current_price,
                'shares': shares,
                'profit': profit,
                'profit_pct': profit_pct,
                'reason': reason
            })
            
            capital += sell_value
            del positions[ts_code]
            
            print(f"卖出 {ts_code} {data.get('name', '')} @ {current_price:.2f}, 原因: {reason}, 盈利: {profit:.2f} ({profit_pct:.1f}%)")
        
        # 检查买入条件
        max_positions = 20
        if len(positions) < max_positions:
            # 计算每只股票可用资金
            available_capital = capital / max(1, max_positions - len(positions))
            
            candidates = []
            for ts_code, data in stock_data_cache.items():
                if ts_code in positions:
                    continue
                
                weekly_data = data.get('weekly', [])
                if not weekly_data:
                    continue
                
                # 找到当前周
                week_idx_in_data = -1
                for i, w in enumerate(weekly_data):
                    if w['trade_date'] == trade_date:
                        week_idx_in_data = i
                        break
                
                if week_idx_in_data < 1:
                    continue
                
                recent_weeks = weekly_data[:week_idx_in_data+1]
                macd_line, signal_line, histogram, kdj_k, kdj_d, kdj_j, sorted_week = get_weekly_indicators(recent_weeks)
                
                if not macd_line or len(macd_line) < 2:
                    continue
                
                is_golden, reason = check_weekly_golden_cross(macd_line, kdj_k, kdj_d)
                
                if is_golden:
                    current_price = weekly_data[week_idx_in_data]['close']
                    candidates.append({
                        'ts_code': ts_code,
                        'name': data.get('name', ''),
                        'price': current_price,
                        'reason': reason
                    })
            
            # 买入候选股票
            for candidate in candidates[:5]:  # 最多买5只
                ts_code = candidate['ts_code']
                price = candidate['price']
                
                if price <= 0:
                    continue
                
                shares = int(available_capital / price / 100) * 100  # 整手买入
                if shares < 100:
                    continue
                
                cost = price
                positions[ts_code] = {
                    'shares': shares,
                    'cost': cost,
                    'buy_date': trade_date
                }
                
                capital -= shares * price
                
                print(f"买入 {ts_code} {candidate['name']} @ {price:.2f}, 数量: {shares}, 原因: {candidate['reason']}")
        
        # 记录年度收益率
        if positions:
            current_value = 0
            for ts_code, pos in positions.items():
                if ts_code in stock_data_cache:
                    weekly_data = stock_data_cache[ts_code].get('weekly', [])
                    if weekly_data:
                        current_price = None
                        for w in weekly_data:
                            if w['trade_date'] == trade_date:
                                current_price = w['close']
                                break
                        if current_price:
                            current_value += pos['shares'] * current_price
            
            total_value = capital + current_value
            yearly_returns[current_year] = (total_value - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
    
    # 最终平仓
    print("\n最终平仓...")
    for ts_code, pos in list(positions.items()):
        if ts_code not in stock_data_cache:
            continue
        
        data = stock_data_cache[ts_code]
        weekly_data = data.get('weekly', [])
        
        if weekly_data:
            final_price = weekly_data[-1]['close']
            sell_value = pos['shares'] * final_price
            profit = sell_value - pos['shares'] * pos['cost']
            profit_pct = (final_price - pos['cost']) / pos['cost'] * 100
            
            trades.append({
                'ts_code': ts_code,
                'name': data.get('name', ''),
                'buy_date': pos['buy_date'],
                'sell_date': '最终平仓',
                'buy_price': pos['cost'],
                'sell_price': final_price,
                'shares': pos['shares'],
                'profit': profit,
                'profit_pct': profit_pct,
                'reason': '最终平仓'
            })
            
            capital += sell_value
    
    # 输出结果
    print("\n" + "="*60)
    print("回测结果")
    print("="*60)
    
    final_value = capital
    total_return = (final_value - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
    
    print(f"初始资金: {INITIAL_CAPITAL:,.2f}")
    print(f"最终资金: {final_value:,.2f}")
    print(f"总收益率: {total_return:.2f}%")
    print(f"总交易次数: {len(trades)}")
    
    # 统计盈利交易
    profitable_trades = [t for t in trades if t['profit'] > 0]
    losing_trades = [t for t in trades if t['profit'] <= 0]
    
    print(f"\n盈利交易: {len(profitable_trades)}")
    print(f"亏损交易: {len(losing_trades)}")
    
    if trades:
        avg_profit = sum(t['profit'] for t in trades) / len(trades)
        print(f"平均收益: {avg_profit:.2f}")
    
    # 年度收益率
    print("\n年度收益率:")
    for year in sorted(yearly_returns.keys()):
        print(f"  {year}: {yearly_returns[year]:.2f}%")
    
    # 保存结果
    results = {
        'initial_capital': INITIAL_CAPITAL,
        'final_value': final_value,
        'total_return': total_return,
        'total_trades': len(trades),
        'profitable_trades': len(profitable_trades),
        'losing_trades': len(losing_trades),
        'yearly_returns': dict(yearly_returns),
        'trades': trades
    }
    
    # 保存JSON
    with open(os.path.join(OUTPUT_DIR, 'backtest_results.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 保存交易记录CSV
    if trades:
        df = pd.DataFrame(trades)
        df.to_csv(os.path.join(OUTPUT_DIR, 'trades.csv'), index=False, encoding='utf-8-sig')
    
    print(f"\n结果已保存到: {OUTPUT_DIR}")
    
    return results

if __name__ == "__main__":
    results = run_backtest()
