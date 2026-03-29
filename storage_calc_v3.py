#!/usr/bin/env python3
"""
光储一体化系统最优配置计算 v3 - 修正IRR计算
"""

import numpy as np

# ============ 固定参数 ============
pv_capacity_kw = 1000          # 1 MW = 1000 kW
pv_cost = 2_000_000           # 光伏成本 2元/W = 200万
pv_efficiency = 0.80           # 光伏效率 80%
pv_decay = 0.02               # 光伏衰减 2%/年
sunshine_hours = 1200         # 日照（河南）1200h/年
storage_eff = 0.88            # 储能充放效率 88%
storage_decay = 0.015         # 储能衰减 1.5%/年
depth_of_discharge = 0.95     # 放电深度 95%
annual_cycles = 330           # 年充放次数 330次
direct_sell_price = 0.25      # 直售电价 0.25元/kWh
operation_years = 20          # 运行年限 20年

# ============ 方案定义 ============
plans = {
    'A': {'storage_mwh': 1, 'storage_cost': 1_000_000},
    'B': {'storage_mwh': 2, 'storage_cost': 2_000_000},
    'C': {'storage_mwh': 3, 'storage_cost': 3_000_000},
    'D': {'storage_mwh': 4, 'storage_cost': 4_000_000},
}
for name, p in plans.items():
    p['total_invest'] = pv_cost + p['storage_cost']


def calc_pv_generation(year):
    eff_factor = pv_efficiency * ((1 - pv_decay) ** (year - 1))
    return pv_capacity_kw * sunshine_hours * eff_factor


def calc_storage_available_kwh(year, storage_mwh):
    """储能每年实际可放电量 = 年充放次数 × 衰减后容量 × DOD"""
    cap = storage_mwh * 1000  # kWh
    decayed = cap * ((1 - storage_decay) ** (year - 1))
    return annual_cycles * decayed * depth_of_discharge


def simulate_year(year, storage_mwh):
    """
    模拟一年：
    - 光伏发电量
    - 储能优先吸收（不会超过储能容量）
    - 多余电力直售
    返回: (直售电量kWh, 储能放电量kWh)
    """
    pv_kwh = calc_pv_generation(year)
    
    if storage_mwh == 0:
        return pv_kwh, 0.0

    storage_cap_kwh = storage_mwh * 1000  # 总容量
    usable_cap = storage_cap_kwh * depth_of_discharge  # 可用容量

    # 储能每天可充入的能量（等效）
    # 实际每次充放电：充入 storage_eff^0.5？不，直接用充放效率
    # 简化：每年储能净充入 = min(光伏发电, 最大可充)
    # 最大可充入量（经过充放效率折算后能放出的）= 可用容量 × 年充放次数
    max_storage_output = calc_storage_available_kwh(year, storage_mwh)
    
    # 实际储能放电量 = min(光伏发电, 最大可放)  （光伏优先给储能）
    # 储能实际可吸收的光伏 = min(光伏发电, 可用容量) × 充放效率
    storage_chargeable = min(pv_kwh, usable_cap)  # 直接按容量算
    storage_charged = storage_chargeable * storage_eff  # 充入并能放出的
    storage_discharged = min(storage_charged, max_storage_output)  # 实际放电
    
    # 剩余光伏直售
    direct_kwh = pv_kwh - storage_chargeable
    
    return direct_kwh, storage_discharged


def calc_annual_revenue(year, storage_mwh, sell_price_storage, sell_price_direct=None):
    if sell_price_direct is None:
        sell_price_direct = direct_sell_price
    direct_kwh, storage_dis_kwh = simulate_year(year, storage_mwh)
    return direct_kwh * sell_price_direct + storage_dis_kwh * sell_price_storage


def npv(rate, cash_flows, initial_investment):
    """计算NPV，cash_flows是每年的运营现金流列表（不包含初始投资）"""
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(cash_flows, 1)) - initial_investment


def calc_irr_bisect(total_invest, annual_cfs, years=operation_years, low=-0.5, high=2.0):
    """二分法计算IRR"""
    def npv_fn(r):
        return npv(r, annual_cfs, total_invest)
    
    # 确保边界正确
    for _ in range(200):
        mid = (low + high) / 2
        v = npv_fn(mid)
        if abs(high - low) < 1e-10:
            break
        if v > 0:
            low = mid
        else:
            high = mid
    
    irr = (low + high) / 2
    return irr


def calc_static_payback(total_invest, annual_cfs):
    """静态回收期"""
    cumulative = -total_invest
    for t, r in enumerate(annual_cfs, 1):
        cumulative += r
        if cumulative >= 0:
            return t
    return operation_years + 1


# ============ 验证基础数据 ============
print("=" * 80)
print("【基础数据验证】")
print("=" * 80)
print(f"\n光伏首年发电量: {calc_pv_generation(1):.0f} kWh = {calc_pv_generation(1)/1e6:.3f} GWh")
print(f"光伏末年发电量: {calc_pv_generation(20):.0f} kWh")
print(f"光伏二十年累计发电量: {sum(calc_pv_generation(y) for y in range(1,21)):.0f} kWh")

print(f"\n方案A 储能首年放电: {calc_storage_available_kwh(1, 1):.0f} kWh")
print(f"方案A 储能末年放电: {calc_storage_available_kwh(20, 1):.0f} kWh")

# 纯光伏直售0.25元的现金流
pv_only_cfs_025 = [calc_pv_generation(y) * 0.25 for y in range(1, operation_years + 1)]
pv_025_irr = calc_irr_bisect(pv_cost, pv_only_cfs_025)
print(f"\n纯光伏0.25元/kWh直售IRR: {pv_025_irr*100:.2f}%")
print(f"  验证: NPV@5% = {npv(0.05, pv_only_cfs_025, pv_cost)/1e4:.1f}万")
print(f"  验证: NPV@12% = {npv(0.12, pv_only_cfs_025, pv_cost)/1e4:.1f}万")

# ============ 主表计算 ============
print("\n" + "=" * 80)
print("【主表】各方案对比")
print("=" * 80)

def find_sell_price_for_irr(storage_mwh, total_invest, target_irr):
    """找到指定IRR对应的储能卖电价（二分）"""
    low, high = 0.01, 3.0
    for _ in range(200):
        mid = (low + high) / 2
        cfs = [calc_annual_revenue(y, storage_mwh, mid) for y in range(1, operation_years+1)]
        irr = calc_irr_bisect(total_invest, cfs, low=-0.5, high=2.0)
        if abs(high - low) < 1e-8:
            break
        if irr > target_irr:
            high = mid
        else:
            low = mid
    return (low + high) / 2

def find_sell_price_for_payback(storage_mwh, total_invest, max_years):
    """找到静态回收期≤N年对应的储能卖电价"""
    low, high = 0.01, 3.0
    for _ in range(200):
        mid = (low + high) / 2
        cfs = [calc_annual_revenue(y, storage_mwh, mid) for y in range(1, operation_years+1)]
        pb = calc_static_payback(total_invest, cfs)
        if abs(high - low) < 1e-8:
            break
        if pb <= max_years:
            high = mid
        else:
            low = mid
    return (low + high) / 2

header = f"{'方案':<4} {'储能\nMWh':<6} {'总投资\n万':<7} {'IRR=10%门槛\n储能卖电价':<14} {'回收期≤7年\n储能卖电价':<14} {'IRR\n(卖0.6)':<10} {'IRR\n(卖0.8)':<10} {'推荐':<6}"
print(header)
print("-" * 80)

results = []
for name, p in plans.items():
    sm = p['storage_mwh']
    ti = p['total_invest']

    # IRR=10%门槛
    thresh_irr10 = find_sell_price_for_irr(sm, ti, 0.10)

    # 回收期≤7年门槛
    thresh_pb7 = find_sell_price_for_payback(sm, ti, 7)

    # IRR @ 0.6 和 0.8
    cfs_06 = [calc_annual_revenue(y, sm, 0.6) for y in range(1, operation_years+1)]
    cfs_08 = [calc_annual_revenue(y, sm, 0.8) for y in range(1, operation_years+1)]
    irr_06 = calc_irr_bisect(ti, cfs_06)
    irr_08 = calc_irr_bisect(ti, cfs_08)

    # 静态回收期
    pb_06 = calc_static_payback(ti, cfs_06)

    # 推荐
    if irr_06 >= 0.10 and thresh_irr10 <= 0.6:
        rec = "✅优"
    elif irr_06 >= 0.08:
        rec = "⚠️可"
    elif irr_06 >= 0.06:
        rec = "⚡慎"
    else:
        rec = "❌差"

    results.append({
        'name': name, 'storage_mwh': sm, 'total_invest': ti,
        'thresh_irr10': thresh_irr10, 'thresh_pb7': thresh_pb7,
        'irr_06': irr_06, 'irr_08': irr_08, 'pb_06': pb_06, 'rec': rec
    })

    print(f"{name:<4} {sm:<6.0f} {ti/1e4:<7.0f} {thresh_irr10:<14.2f} {thresh_pb7:<14.2f} {irr_06*100:<9.1f}% {irr_08*100:<9.1f}% {rec:<6}")

print("-" * 80)

# ============ 附加：纯光伏直售IRR ============
print("\n" + "=" * 80)
print("【附加】纯光伏（1MW）不同电价直售IRR（不配储能）")
print("=" * 80)

print(f"\n{'电价':<12} {'首年年收益':<12} {'IRR':<10} {'静态回收期':<12}")
print("-" * 50)
for price in [0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60, 0.80, 1.00]:
    cfs = [calc_pv_generation(y) * price for y in range(1, operation_years+1)]
    irr = calc_irr_bisect(pv_cost, cfs)
    pb = calc_static_payback(pv_cost, cfs)
    annual_rev = calc_pv_generation(1) * price / 1e4
    print(f"{price:<12.2f} {annual_rev:<12.1f} {irr*100:<9.1f}% {pb:<12}")
print("-" * 50)

# ============ 方案B逐年明细 ============
print("\n" + "=" * 80)
print("【明细】方案B（2 MWh）储能卖0.6元/kWh 逐年数据")
print("=" * 80)

b_sm = 2
b_ti = plans['B']['total_invest']
b_cfs_06 = [calc_annual_revenue(y, b_sm, 0.6) for y in range(1, operation_years+1)]
b_pv_y1 = calc_pv_generation(1)

print(f"\n方案B总投资: {b_ti/1e4:.0f}万, 首年收益: {b_cfs_06[0]/1e4:.1f}万")
print(f"{'年':<3} {'光伏kWh':<12} {'储能可放电kWh':<16} {'直售kWh':<12} {'储能放电kWh':<14} {'收益万':<10} {'累计万':<10}")
print("-" * 85)

cumulative = -b_ti
for y in range(1, operation_years+1):
    pv_kwh = calc_pv_generation(y)
    stor_avail = calc_storage_available_kwh(y, b_sm)
    direct_kwh, stor_dis_kwh = simulate_year(y, b_sm)
    rev = b_cfs_06[y-1]
    cumulative += rev
    print(f"{y:<3} {pv_kwh:<12.0f} {stor_avail:<16.0f} {direct_kwh:<12.0f} {stor_dis_kwh:<14.0f} {rev/1e4:<10.1f} {cumulative/1e4:<10.1f}")

print(f"\n方案B IRR(卖0.6): {results[1]['irr_06']*100:.2f}% | 静态回收期: {results[1]['pb_06']}年")

# ============ 结论 ============
print("\n" + "=" * 80)
print("【结论汇总】")
print("=" * 80)

print("\n1️⃣ 各方案IRR对比（储能卖电价）:")
print(f"   {'方案':<4} {'总投资':<10} {'IRR@0.6':<12} {'IRR@0.8':<12} {'IRR@1.0':<12} {'回收期(0.6)':<12}")
for r in results:
    cfs_10 = [calc_annual_revenue(y, r['storage_mwh'], 1.0) for y in range(1, operation_years+1)]
    irr_10 = calc_irr_bisect(r['total_invest'], cfs_10)
    print(f"   {r['name']:<4} {r['total_invest']/1e4:<10.0f} {r['irr_06']*100:<11.1f}% {r['irr_08']*100:<11.1f}% {irr_10*100:<11.1f}% {r['pb_06']:<12}")

best = max(results, key=lambda x: x['irr_06'])
print(f"\n2️⃣ 最优推荐: 方案{best['name']}（{best['storage_mwh']}MWh，总投资{best['total_invest']/1e4:.0f}万）")
print(f"   IRR(储能卖0.6)={best['irr_06']*100:.1f}%, IRR(储能卖0.8)={best['irr_08']*100:.1f}%")

print(f"\n3️⃣ 纯光伏直售IRR（无储能）:")
for price in [0.25, 0.35, 0.50]:
    cfs = [calc_pv_generation(y) * price for y in range(1, operation_years+1)]
    irr = calc_irr_bisect(pv_cost, cfs)
    pb = calc_static_payback(pv_cost, cfs)
    print(f"   电价{price}元/kWh → IRR={irr*100:.1f}%, 回收期={pb}年")

print(f"\n4️⃣ 关键洞察:")
print(f"   - 纯光伏0.25元/kWh直售IRR约{calc_irr_bisect(pv_cost, pv_only_cfs_025)*100:.1f}%，低于10%门槛")
print(f"   - 纯光伏0.5元/kWh直售IRR约{calc_irr_bisect(pv_cost, [calc_pv_generation(y)*0.5 for y in range(1,21)])*100:.1f}%")
print(f"   - 配储能后IRR≥10%需储能卖电价达到约{best['thresh_irr10']:.2f}元/kWh")
print(f"   - 方案A(1MWh)总投资{best['total_invest']/1e4:.0f}万最轻，{best['thresh_irr10']:.2f}元/kWh即可IRR≥10%")

print("\n" + "=" * 80)
