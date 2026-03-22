"""
A股周线量化回测策略
策略规则:
- 买入条件: 周MACD低位金叉 + 周KDJ低位金叉
  - MACD金叉时，DIF < 0
  - KDJ金叉时，K < 30
- 卖出条件（满足任一即卖出）:
  1. 累计收益率 > 20%
  2. MACD死叉 + KDJ死叉（同时）
  3. 亏损达到 5%
- 冷却期规则: 60天内买过的股票不再买入
- 仓位管理: 初始资金100万，每个股票仓位相同（动态平衡）
"""

import json
import os
from collections import defaultdict

DATA_DIR = "/opt/stock-screener-v2/cache/data/"
OUTPUT_DIR = "/opt/stock-screener-v2/backtest_results/"
INITIAL_CAPITAL = 1000000

def load_stock_data(ts_code):
    path = os.path.join(DATA_DIR, f"{ts_code}.json")
    if not os.path.exists(path): return None
    try:
        with open(path) as f: 
            data = json.load(f)
        if isinstance(data, list): return None  # 跳过stock_list.json
        return data
    except: return None

def ema(prices, n):
    if len(prices) < n: return sum(prices)/len(prices) if prices else 0
    e = sum(prices[:n])/n
    for p in prices[n:]: e = p*2/(n+1) + e*(1-2/(n+1))
    return e

def calc_kdj(closes, highs, lows, n=23):
    if len(closes) < n or len(highs) < n or len(lows) < n: return 50, 50
    h_n, l_n = max(highs[-n:]), min(lows[-n:])
    if h_n <= l_n: return 50, 50
    rsv = (closes[-1] - l_n) / (h_n - l_n) * 100
    k = d = 50
    for _ in range(3):
        k = (2*k + rsv) / 3
        d = (2*d + k) / 3
    return k, d

# 获取所有股票
files = [f.replace('.json','') for f in os.listdir(DATA_DIR) if f.endswith('.json')]

# 获取所有周
all_weeks = set()
for f in files[:3000]:
    data = load_stock_data(f)
    if not data: continue
    for d in data.get('weekly',[]):
        all_weeks.add(d.get('trade_date','')[:8])
weeks = sorted(list(all_weeks))
print(f"周期: {weeks[0]} - {weeks[-1]}, 共{len(weeks)}周")

cash = INITIAL_CAPITAL
holdings = {}
trade_log = []

for i, week in enumerate(weeks):
    # 选股
    buy_signals = []
    for f in files[:3000]:
        code = f
        data = load_stock_data(code)
        if not data: continue
        weekly = data.get('weekly',[])
        if len(weekly) < 30: continue
        
        week_data = None
        for d in weekly:
            if d.get('trade_date','').startswith(week):
                week_data = d
                break
        if not week_data: continue
        
        idx = weekly.index(week_data)
        if idx < 23: continue
        
        closes = [d['close'] for d in weekly[:idx+1]]
        highs = [d['high'] for d in weekly[:idx+1]]
        lows = [d['low'] for d in weekly[:idx+1]]
        k, d_kdj = calc_kdj(closes, highs, lows, 23)
        
        closes_prev = [d['close'] for d in weekly[:idx]]
        highs_prev = [d['high'] for d in weekly[:idx]]
        lows_prev = [d['low'] for d in weekly[:idx]]
        k_prev, d_prev = calc_kdj(closes_prev, highs_prev, lows_prev, 23)
        
        dif = ema(closes, 12) - ema(closes, 26)
        dif_prev = ema(closes_prev, 12) - ema(closes_prev, 26)
        
        # 买入条件: K<30金叉 + DIF<0金叉
        kdj_gc = k > d_kdj and k_prev <= d_prev and k < 30
        macd_gc = dif > 0 and dif_prev <= 0 and dif < 0
        macd_dc = dif <= 0 and dif_prev > 0  # 死叉
        kdj_dc = k <= d_kdj and k_prev > d_prev  # 死叉
        
        if kdj_gc and macd_gc:
            # 冷却期检查
            can_buy = True
            for h in holdings.values():
                buy_week = h['buy_date']
                if week >= buy_week and week < buy_week:
                    can_buy = False
                    break
            if can_buy:
                buy_signals.append({'code': code, 'price': week_data['close'], 'date': week})
    
    # 卖出检查
    sells = []
    for code, h in list(holdings.items()):
        data = load_stock_data(code)
        if not data: continue
        weekly = data.get('weekly',[])
        
        buy_idx = None
        for j, d in enumerate(weekly):
            if d.get('trade_date','').startswith(h['buy_date']):
                buy_idx = j
                break
        if buy_idx is None: continue
        
        current_idx = None
        for j, d in enumerate(weekly):
            if d.get('trade_date','').startswith(week):
                current_idx = j
                break
        if current_idx is None or current_idx < buy_idx: continue
        
        closes = [d['close'] for d in weekly[buy_idx:current_idx+1]]
        highs = [d['high'] for d in weekly[buy_idx:current_idx+1]]
        lows = [d['low'] for d in weekly[buy_idx:current_idx+1]]
        k, d_kdj = calc_kdj(closes, highs, lows, 23)
        
        closes_prev = [d['close'] for d in weekly[buy_idx:current_idx]]
        highs_prev = [d['high'] for d in weekly[buy_idx:current_idx]]
        lows_prev = [d['low'] for d in weekly[buy_idx:current_idx]]
        k_prev, d_prev = calc_kdj(closes_prev, highs_prev, lows_prev, 23) if closes_prev else (50, 50)
        
        dif = ema(closes, 12) - ema(closes, 26)
        dif_prev = ema(closes_prev, 12) - ema(closes_prev, 26) if closes_prev else 1
        
        profit_pct = (closes[-1] - h['buy_price']) / h['buy_price'] * 100
        
        # 卖出条件
        macd_dc = dif <= 0 and dif_prev > 0
        kdj_dc = k <= d_kdj and k_prev > d_prev
        
        should_sell = False
        reason = ""
        if profit_pct > 20:
            should_sell = True
            reason = "涨幅>20%"
        elif macd_dc and kdj_dc:
            should_sell = True
            reason = "双死叉"
        elif profit_pct < -5:
            should_sell = True
            reason = "亏损5%"
        
        if should_sell:
            sells.append({'code': code, 'price': closes[-1], 'reason': reason, 'profit_pct': profit_pct})
    
    # 执行卖出
    for s in sells:
        code = s['code']
        h = holdings.pop(code)
        proceeds = h['shares'] * s['price']
        cash += proceeds
        profit = proceeds - h['cost']
        trade_log.append({
            'ts_code': code,
            'buy_date': h['buy_date'],
            'sell_date': week,
            'buy_price': h['buy_price'],
            'sell_price': s['price'],
            'shares': h['shares'],
            'profit': profit,
            'profit_pct': s['profit_pct'],
            'reason': s['reason']
        })
    
    # 全仓买入: 只买一只
    if buy_signals and cash > 0:
        sig = buy_signals[0]  # 只买第一只
        price = sig['price']
        shares = int(cash / price / 100) * 100
        if shares > 0:
            cost = shares * price
            holdings[sig['code']] = {
                'buy_date': week,
                'buy_price': price,
                'shares': shares,
                'cost': cost
            }
            cash -= cost
            print(f"买入: {sig['code']} @ {price}")

# 最终平仓
for code, h in holdings.items():
    data = load_stock_data(code)
    if not data: continue
    weekly = data.get('weekly',[])
    if not weekly: continue
    
    last_price = weekly[-1]['close']
    proceeds = h['shares'] * last_price
    cash += proceeds
    profit = proceeds - h['cost']
    trade_log.append({
        'ts_code': code,
        'buy_date': h['buy_date'],
        'sell_date': weeks[-1],
        'buy_price': h['buy_price'],
        'sell_price': last_price,
        'shares': h['shares'],
        'profit': profit,
        'profit_pct': (last_price - h['buy_price']) / h['buy_price'] * 100,
        'reason': '最终平仓'
    })

# 统计
total_profit = sum(t['profit'] for t in trade_log)
total_return = total_profit / INITIAL_CAPITAL * 100
profitable = len([t for t in trade_log if t['profit'] > 0])
losing = len([t for t in trade_log if t['profit'] <= 0])

# 年度收益
yearly = defaultdict(float)
for t in trade_log:
    yearly[t['sell_date'][:4]] += t['profit']

print(f"\n=== 回测结果 ===")
print(f"最终收益率: {total_return:.2f}%")
print(f"总交易次数: {len(trade_log)}")
print(f"盈利: {profitable}, 亏损: {losing}")
print(f"\n年度收益率:")
for y in sorted(yearly.keys()):
    print(f"  {y}: {yearly[y]:+.0f}元 ({yearly[y]/INITIAL_CAPITAL*100:+.2f}%)")

# 保存
os.makedirs(OUTPUT_DIR, exist_ok=True)
result = {
    'initial_capital': INITIAL_CAPITAL,
    'final_value': INITIAL_CAPITAL + total_profit,
    'total_return': total_return,
    'total_trades': len(trade_log),
    'profitable_trades': profitable,
    'losing_trades': losing,
    'yearly_returns': {y: yearly[y]/INITIAL_CAPITAL*100 for y in yearly},
    'trades': trade_log
}
with open(os.path.join(OUTPUT_DIR, 'backtest_results.json'), 'w') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"\n结果已保存到 {OUTPUT_DIR}")
