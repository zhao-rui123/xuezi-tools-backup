#!/usr/bin/env python3
"""
山东2026年1-2月电力现货市场储能充放电套利分析
数据：1月(31天) + 2月(28天) = 59天 | 每日84时段(00:00-24:00)
策略：日结平衡模式 - 充电量=放电量，按RT实时价格贪心匹配
储能参数：容量1MWh，往返效率90%
"""

import openpyxl
import csv
from datetime import datetime

FILE = '/Users/zhaoruicn/.openclaw/media/inbound/2026现货---f0871cea-8bba-4c5b-9d48-0297afdd2392.xlsx'
wb = openpyxl.load_workbook(FILE, data_only=True)
ws = wb['Sheet1']
rows = list(ws.iter_rows(values_only=True))  # full sheet

# ── 找出所有日期列，按section分组 ───────────────────────────
# Section 1: rows[2] header, rows[3..26] data (24 hours), rows[27] 均值
# Section 2: rows[31] header, rows[32..55] data, rows[56] 均值
# Section 3: rows[61] header, rows[62..85] data, rows[86] 均值

SECTIONS = [
    {'header_row': 2,  'data_start': 3,  'data_end': 26,  'label': '2026年1月'},
    {'header_row': 31, 'data_start': 32, 'data_end': 55,  'label': '2026年2月'},
    {'header_row': 61, 'data_start': 62, 'data_end': 85,  'label': '2025年3月'},
]

def parse_section(sec):
    """从指定行范围提取所有日期+报价数据"""
    header = rows[sec['header_row']]
    # 找日期列 (col_idx 是 tuple 索引)
    day_cols = []
    for ci, v in enumerate(header):
        if hasattr(v, 'year'):
            day_cols.append((ci, v))  # (col_idx, datetime)
    if not day_cols:
        return []

    # 提取每日报价 (DA=col, RT=col+1)
    data = []
    for col, dt in day_cols:
        da = [float(rows[r][col] or 0) for r in range(sec['data_start'], sec['data_end']+1)]
        rt = [float(rows[r][col+1] or 0) for r in range(sec['data_start'], sec['data_end']+1)]
        data.append({'date': dt, 'da': da, 'rt': rt})
    return data

# 合并所有section
all_days = []
for sec in SECTIONS:
    sec_data = parse_section(sec)
    all_days.extend(sec_data)
    print(f"  {sec['label']}: {len(sec_data)}天")

print(f"\n总计: {len(all_days)}天")

# 时间标签
ts_label = [rows[rs][0] for rs in range(SECTIONS[0]['data_start'], SECTIONS[0]['data_end']+1)]
print(f"时段数: {len(ts_label)} (从 {ts_label[0]} 到 {ts_label[-1]})")

# ── 储能套利策略 ──────────────────────────────────────────
CAPACITY  = 1.0    # MWh
EFFICIENCY = 0.90  # 往返效率

def greedy_arbitrage(day_prices, target=CAPACITY):
    """
    贪心策略：
    1. 找RT最低的时段充电（优先低价）
    2. 找RT最高的时段放电（优先高价）
    3. 充放电量平衡 (charged = discharged = balanced)
    """
    rt = day_prices['rt']
    n  = len(rt)

    # 按时段RT价格排序索引
    c_idxs = sorted(range(n), key=lambda i: rt[i])          # 升序：最便宜先充
    d_idxs = sorted(range(n), key=lambda i: rt[i], reverse=True)  # 降序：最贵先放

    # 充电
    charge_list, charged = [], 0.0
    for idx in c_idxs:
        if charged >= target:
            break
        qty = min(CAPACITY, target - charged)
        charged += qty
        charge_list.append((idx, qty))

    # 放电
    discharge_list, discharged = [], 0.0
    for idx in d_idxs:
        if discharged >= target:
            break
        qty = min(CAPACITY, target - discharged)
        discharged += qty
        discharge_list.append((idx, qty))

    balanced = min(charged, discharged)

    # 加权均价
    def wavg(items):
        tq, tp = 0.0, 0.0
        for idx, q in items:
            tq += q
            tp += rt[idx] * q
        return tp / tq if tq > 0 else 0.0

    c_avg = wavg(charge_list)
    d_avg = wavg(discharge_list)

    # 收益: 放电收入 - 充电成本 (含效率损耗)
    # 放电balanced MWh → 需充电 balanced/EFFICIENCY MWh
    cost_mwh = balanced / EFFICIENCY
    actual_cost = 0.0
    for idx, q in charge_list:
        take = min(q, max(0, cost_mwh - actual_cost))
        if take <= 0:
            break
        actual_cost += take

    revenue = d_avg * balanced
    cost    = c_avg * actual_cost
    profit  = revenue - cost

    neg = [(i, rt[i]) for i in range(n) if rt[i] < 0]

    return {
        'date':        day_prices['date'],
        'rt':          rt,
        'charge_list': charge_list,
        'discharge_list': discharge_list,
        'balanced':    balanced,
        'c_avg':       c_avg,
        'd_avg':       d_avg,
        'revenue':     revenue,
        'cost':        cost,
        'profit':      profit,
        'neg_hours':   neg,
        'rt_max':      max(rt),
        'rt_min':      min(rt),
        'rt_avg':      sum(rt)/n,
        'da_avg':      sum(day_prices['da'])/n,
    }

# ── 执行分析 ──────────────────────────────────────────────
results = [greedy_arbitrage(d) for d in all_days]

# ── 每日明细表 ─────────────────────────────────────────────
print(f"\n{'='*76}")
print(f"{'日期':<12} {'星期':^4} | {'RT最高':>8} {'RT最低':>8} {'负h':>4} | "
      f"{'充电次':>5} {'c均':>7} | {'放电次':>5} {'d均':>7} | {'利润':>9}")
print(f"{'-'*76}")

total_profit = 0.0
for r in results:
    dow = '一二三四五六日'[r['date'].weekday()]
    ds  = r['date'].strftime('%m-%d')
    print(f"{ds:<12} {dow:^4} | {r['rt_max']:>8.1f} {r['rt_min']:>8.1f} {len(r['neg_hours']):>4d} | "
          f"{len(r['charge_list']):>5d} {r['c_avg']:>7.1f} | "
          f"{len(r['discharge_list']):>5d} {r['d_avg']:>7.1f} | {r['profit']:>9.1f}")
    total_profit += r['profit']

print(f"{'-'*76}")
total_balanced = sum(r['balanced'] for r in results)
print(f"{'合计':<17} | {'':>8} {'':>8} {'':>4} | {'':>5} {'':>7} | {'':>5} {'':>7} | {total_profit:>9.1f} 元")

# ── 月度分组小计 ──────────────────────────────────────────
print(f"\n{'='*76}")
print("月度汇总")
print(f"{'-'*76}")
months = {}
for r in results:
    key = r['date'].strftime('%Y-%m')
    if key not in months:
        months[key] = {'profit': 0, 'days': 0}
    months[key]['profit'] += r['profit']
    months[key]['days'] += 1

for key in sorted(months.keys()):
    m = months[key]
    print(f"  {key}: {m['days']}天  利润合计 {m['profit']:.0f}元  日均 {m['profit']/m['days']:.0f}元")

# ── 全局统计 ──────────────────────────────────────────────
rt_all = [p for d in all_days for p in d['rt']]
da_all = [p for d in all_days for p in d['da']]
neg_total = sum(len(r['neg_hours']) for r in results)
neg_days  = sum(1 for r in results if r['rt_min'] < 0)
high_days = sum(1 for r in results if r['rt_max'] > 500)

rt_avg_all = sum(rt_all)/len(rt_all)
da_avg_all = sum(da_all)/len(da_all)

print(f"""
╔══════════════════════════════════════════════════════════════════════════╗
║              【储能套利月度报告】山东电力现货 2026年1-2月              ║
╠══════════════════════════════════════════════════════════════════════════╣
║  数据范围:   {len(results)}天 × 84时段 = {len(results)*84}个数据点                              ║
║  ─────────────────────────────────────────────────────────────────    ║
║  📊 实时(RT)市场:                                                        ║
║     均价:    {rt_avg_all:>8.1f} 元/MWh                                         ║
║     最高价:  {max(rt_all):>8.1f} 元/MWh                                         ║
║     最低价:  {min(rt_all):>8.1f} 元/MWh  {'⚠️负电价!' if min(rt_all)<0 else ' ':>12}                    ║
║     负电价:  {neg_total:>4d} 个时段  (分布在 {neg_days} 天)                              ║
║  ─────────────────────────────────────────────────────────────────    ║
║  📊 日前(DA)市场:                                                        ║
║     均价:    {da_avg_all:>8.1f} 元/MWh                                         ║
║     最高价:  {max(da_all):>8.1f} 元/MWh                                         ║
║     最低价:  {min(da_all):>8.1f} 元/MWh                                         ║
║  ─────────────────────────────────────────────────────────────────    ║
║  📊 RT vs DA:  RT均{'高于' if rt_avg_all>da_avg_all else '低于'}DA  {rt_avg_all-da_avg_all:+.1f} 元/MWh                            ║
║  ─────────────────────────────────────────────────────────────────    ║
║  ⚡ 套利策略（1MWh储能·每日充放平衡·效率90%）:                          ║
║     月总利润:  {total_profit:>8.0f} 元                                         ║
║     日均利润:  {total_profit/len(results):>8.0f} 元                                         ║
║     年化收益:  {total_profit/len(results)*365:>8.0f} 元 (仅供参考)                            ║
║     高价天:   {high_days:>4d} 天 (>500元/MWh)                                  ║
║     负电价天: {neg_days:>4d} 天                                               ║
╚══════════════════════════════════════════════════════════════════════════╝
""")

# ── 详细充放电（前10天）───────────────────────────────
print(f"\n{'='*76}")
print("【各日充放电详细分解】前10天")
print(f"{'='*76}")

for idx, r in enumerate(results[:10]):
    dt = r['date']
    print(f"\n📅 {dt.strftime('%Y-%m-%d')} ({'一二三四五六日'[dt.weekday()]})  "
          f"RT: {r['rt_min']:.0f}~{r['rt_max']:.0f} 均{r['rt_avg']:.0f}  | DA均{r['da_avg']:.0f}")
    if r['neg_hours']:
        neg_list = ' '.join([f"{ts_label[i]}" for i,_ in r['neg_hours']])
        print(f"   ⚠️ 负电价: {neg_list}")
    print(f"   🔌 充电 {len(r['charge_list'])}次 (均{r['c_avg']:.0f}):")
    for i, (si, qty) in enumerate(r['charge_list'][:8]):
        print(f"      {ts_label[si]:>12}  充电 {qty:.3f}MWh  @ RT={r['rt'][si]:>7.1f}")
    if len(r['charge_list']) > 8:
        print(f"      ... 还有{len(r['charge_list'])-8}次")
    print(f"   ⚡ 放电 {len(r['discharge_list'])}次 (均{r['d_avg']:.0f}):")
    for i, (si, qty) in enumerate(r['discharge_list'][:8]):
        print(f"      {ts_label[si]:>12}  放电 {qty:.3f}MWh  @ RT={r['rt'][si]:>7.1f}")
    if len(r['discharge_list']) > 8:
        print(f"      ... 还有{len(r['discharge_list'])-8}次")
    print(f"   💰 利润: {r['profit']:.1f}元 | 充均{r['c_avg']:.0f}→放均{r['d_avg']:.0f} | 净差{r['d_avg']-r['c_avg']:.0f}元/MWh")

# ── TOP10 利润日 ─────────────────────────────────────────
print(f"\n{'='*76}")
print("【利润TOP10】")
print(f"{'='*76}")
top = sorted(results, key=lambda x: x['profit'], reverse=True)[:10]
for rank, r in enumerate(top, 1):
    print(f"  #{rank:2d} {r['date'].strftime('%Y-%m-%d')}  利润{r['profit']:>7.1f}元  "
          f"充均{r['c_avg']:>6.0f}→放均{r['d_avg']:>6.0f}  RT范围{r['rt_min']:.0f}~{r['rt_max']:.0f}")

# ── 充放电次数分布 ──────────────────────────────────────
from collections import Counter
ch_d = Counter(len(r['charge_list']) for r in results)
dh_d = Counter(len(r['discharge_list']) for r in results)
print(f"\n{'='*76}")
print("【充放电次数统计】")
print(f"  每日充电次数: {dict(sorted(ch_d.items()))}")
print(f"  每日放电次数: {dict(sorted(dh_d.items()))}")

# ── 保存CSV ──────────────────────────────────────────────
csv_path = '/Users/zhaoruicn/.openclaw/workspace/储能套利分析_全量.csv'
with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['日期','星期','RT最高','RT最低','RT均价','DA均价',
                '负价时段','充电次数','放电次数','充电均价','放电均价',
                '利润元','RT-DA均差','净价差'])
    for r in results:
        w.writerow([
            r['date'].strftime('%Y-%m-%d'),
            '一二三四五六日'[r['date'].weekday()],
            f"{r['rt_max']:.1f}", f"{r['rt_min']:.1f}",
            f"{r['rt_avg']:.1f}", f"{r['da_avg']:.1f}",
            len(r['neg_hours']),
            len(r['charge_list']), len(r['discharge_list']),
            f"{r['c_avg']:.1f}", f"{r['d_avg']:.1f}",
            f"{r['profit']:.2f}",
            f"{r['rt_avg']-r['da_avg']:.1f}",
            f"{r['d_avg']-r['c_avg']:.1f}",
        ])
print(f"\n✅ CSV已保存: {csv_path}")
