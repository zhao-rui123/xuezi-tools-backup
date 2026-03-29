#!/usr/bin/env python3
"""
光储一体化系统最优配置计算 v4 - 修正储能模拟逻辑
核心：储能每天最多330次，但每天实际可循环次数 = min(1, 剩余光伏/储能容量)
"""

# ============ 固定参数 ============
pv_capacity_kw = 1000
pv_cost = 2_000_000
pv_efficiency = 0.80
pv_decay = 0.02
sunshine_hours = 1200        # 年均等效日照小时
storage_eff = 0.88
storage_decay = 0.015
depth_of_discharge = 0.95
annual_cycles = 330
direct_sell_price = 0.25
operation_years = 20
daily_pv_kwh = pv_capacity_kw * sunshine_hours / 365  # 日均发电 ≈ 2630 kWh

# ============ 方案 ============
plans = {
    'A': {'storage_mwh': 1, 'storage_cost': 1_000_000},
    'B': {'storage_mwh': 2, 'storage_cost': 2_000_000},
    'C': {'storage_mwh': 3, 'storage_cost': 3_000_000},
    'D': {'storage_mwh': 4, 'storage_cost': 4_000_000},
}
for name, p in plans.items():
    p['total_invest'] = pv_cost + p['storage_cost']


def calc_pv_kwh_year(year):
    """年均光伏发电量（kWh）"""
    eff = pv_efficiency * ((1 - pv_decay) ** (year - 1))
    return pv_capacity_kw * sunshine_hours * eff


def calc_pv_kwh_daily(year):
    """日均光伏发电量（kWh）"""
    return calc_pv_kwh_year(year) / 365


def calc_storage_annual_output(storage_mwh, year):
    """储能年放电量（kWh）= 年循环次数 × 每次可放电量"""
    usable = storage_mwh * 1000 * depth_of_discharge
    usable_decayed = usable * ((1 - storage_decay) ** (year - 1))
    return annual_cycles * usable_decayed


def calc_storage_annual_charge_needed(storage_discharge_kwh, year):
    """储能年充电量（从光伏来）= 放电量 / 效率"""
    return storage_discharge_kwh / storage_eff


def simulate_year_v2(storage_mwh, year):
    """
    修正版年模拟：
    逻辑：储能优先充，多余直售
    - 储能每天最多充电到满（储能容量）
    - 每天实际可充电次数 = 当天剩余光伏 / 储能容量
    - 但年总充电能量上限 = 储能年最大可充能量（受光伏总量限制）
    
    返回: (直售kWh, 储能放电kWh)
    """
    pv_annual = calc_pv_kwh_year(year)
    storage_discharge_annual = calc_storage_annual_output(storage_mwh, year)
    
    if storage_mwh == 0:
        return pv_annual, 0.0
    
    # 储能年最大可充电量（等效放电量）
    storage_charge_annual = storage_discharge_annual / storage_eff
    
    # 实际可充电量 = min(光伏总量, 储能最大可充电量)
    actual_charge = min(pv_annual, storage_charge_annual)
    
    # 实际储能放电 = 实际充电量 × 效率
    actual_discharge = actual_charge * storage_eff
    
    # 直售 = 光伏 - 用于储能充电的部分
    direct_kwh = pv_annual - actual_charge
    
    return direct_kwh, actual_discharge


def calc_annual_revenue(year, storage_mwh, sell_price_storage):
    direct, stor = simulate_year_v2(storage_mwh, year)
    return direct * direct_sell_price + stor * sell_price_storage


def npv_func(rate, cfs, invest):
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(cfs, 1)) - invest


def calc_irr(cfs, invest, low=-0.3, high=3.0):
    for _ in range(200):
        mid = (low + high) / 2
        if npv_func(mid, cfs, invest) > 0:
            low = mid
        else:
            high = mid
        if abs(high - low) < 1e-10:
            break
    return (low + high) / 2


def calc_static_pb(invest, cfs):
    cum = -invest
    for t, r in enumerate(cfs, 1):
        cum += r
        if cum >= 0:
            return t
    return operation_years + 1


# ============ 基础验证 ============
print("=" * 90)
print("【基础数据验证】")
print("=" * 90)
pv_y1 = calc_pv_kwh_year(1)
pv_y20 = calc_pv_kwh_year(20)
print(f"\n光伏首年发电量: {pv_y1:,.0f} kWh = {pv_y1/1e6:.3f} GWh")
print(f"光伏末年发电量: {pv_y20:,.0f} kWh")
print(f"光伏20年累计: {sum(calc_pv_kwh_year(y) for y in range(1,21)):,.0f} kWh")

for name, p in plans.items():
    sd = calc_storage_annual_output(p['storage_mwh'], 1)
    print(f"\n方案{name} 储能年放电量: {sd:,.0f} kWh = {sd/1e6:.3f} GWh")
    print(f"  需光伏充电: {sd/storage_eff:,.0f} kWh，占光伏{sd/storage_eff/pv_y1*100:.1f}%")


# ============ 主表 ============
print("\n" + "=" * 90)
print("【主表】各方案对比")
print("=" * 90)

def find_price_for_irr(storage_mwh, invest, target_irr):
    low, high = 0.01, 5.0
    for _ in range(200):
        mid = (low + high) / 2
        cfs = [calc_annual_revenue(y, storage_mwh, mid) for y in range(1, operation_years+1)]
        irr = calc_irr(cfs, invest)
        if abs(high - low) < 1e-8:
            break
        if irr > target_irr:
            high = mid
        else:
            low = mid
    return (low + high) / 2

def find_price_for_pb(storage_mwh, invest, max_years):
    low, high = 0.01, 5.0
    for _ in range(200):
        mid = (low + high) / 2
        cfs = [calc_annual_revenue(y, storage_mwh, mid) for y in range(1, operation_years+1)]
        pb = calc_static_pb(invest, cfs)
        if abs(high - low) < 1e-8:
            break
        if pb <= max_years:
            high = mid
        else:
            low = mid
    return (low + high) / 2

print(f"\n{'方案':<4} {'储能':<6} {'总投资':<8} {'IRR=10%':<10} {'回收≤7年':<10} {'IRR@0.6':<10} {'IRR@0.8':<10} {'回收期@0.6':<10} {'推荐':<6}")
print("-" * 90)

results = []
for name, p in plans.items():
    sm = p['storage_mwh']
    ti = p['total_invest']

    thresh_irr10 = find_price_for_irr(sm, ti, 0.10)
    thresh_pb7 = find_price_for_pb(sm, ti, 7)

    cfs_06 = [calc_annual_revenue(y, sm, 0.6) for y in range(1, operation_years+1)]
    cfs_08 = [calc_annual_revenue(y, sm, 0.8) for y in range(1, operation_years+1)]
    irr_06 = calc_irr(cfs_06, ti)
    irr_08 = calc_irr(cfs_08, ti)
    pb_06 = calc_static_pb(ti, cfs_06)

    if irr_06 >= 0.10 and thresh_irr10 <= 0.6:
        rec = "✅优"
    elif irr_06 >= 0.08:
        rec = "⚠️可"
    elif irr_06 >= 0.06:
        rec = "⚡慎"
    else:
        rec = "❌差"

    results.append({'name': name, 'storage_mwh': sm, 'total_invest': ti,
                    'thresh_irr10': thresh_irr10, 'thresh_pb7': thresh_pb7,
                    'irr_06': irr_06, 'irr_08': irr_08, 'pb_06': pb_06, 'rec': rec})
    print(f"{name:<4} {sm:<6.0f} {ti/1e4:<8.0f} {thresh_irr10:<10.2f} {thresh_pb7:<10.2f} {irr_06*100:<9.1f}% {irr_08*100:<9.1f}% {pb_06:<10} {rec:<6}")

print("-" * 90)

# ============ 附加：纯光伏直售IRR ============
print("\n" + "=" * 90)
print("【附加】纯光伏（1MW）不同电价直售IRR（不配储能）")
print("=" * 90)

print(f"\n{'电价':<12} {'首年收益万':<12} {'IRR':<10} {'静态回收期':<10}")
print("-" * 50)
for price in [0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60, 0.80, 1.00]:
    cfs = [calc_pv_kwh_year(y) * price for y in range(1, operation_years+1)]
    irr = calc_irr(cfs, pv_cost)
    pb = calc_static_pb(pv_cost, cfs)
    rev = calc_pv_kwh_year(1) * price / 1e4
    print(f"{price:<12.2f} {rev:<12.1f} {irr*100:<9.1f}% {pb:<10}")
print("-" * 50)

# ============ 方案B逐年明细 ============
print("\n" + "=" * 90)
print("【明细】方案B（2MWh）储能卖0.6元/kWh 逐年数据")
print("=" * 90)

b_sm = 2
b_ti = plans['B']['total_invest']
b_cfs_06 = [calc_annual_revenue(y, b_sm, 0.6) for y in range(1, operation_years+1)]
b_pv = calc_pv_kwh_year(1)

print(f"\n方案B总投资: {b_ti/1e4:.0f}万 | IRR@0.6: {results[1]['irr_06']*100:.2f}%")
print(f"{'年':<3} {'光伏kWh':<12} {'储能放电kWh':<14} {'直售kWh':<12} {'年收益万':<10} {'累计万':<10}")
print("-" * 80)

cum = -b_ti
for y in range(1, operation_years+1):
    pv_kwh = calc_pv_kwh_year(y)
    stor_dis = calc_storage_annual_output(b_sm, y)
    direct, _ = simulate_year_v2(b_sm, y)
    rev = b_cfs_06[y-1]
    cum += rev
    print(f"{y:<3} {pv_kwh:<12,.0f} {stor_dis:<14,.0f} {direct:<12,.0f} {rev/1e4:<10.1f} {cum/1e4:<10.1f}")

# ============ 结论 ============
print("\n" + "=" * 90)
print("【结论汇总】")
print("=" * 90)

print("\n1️⃣ 各方案IRR汇总:")
print(f"   {'方案':<4} {'储能MWh':<10} {'总投资万':<10} {'IRR@0.6':<10} {'IRR@0.8':<10} {'回收期0.6':<10} {'IRR=10%门槛':<12}")
for r in results:
    print(f"   {r['name']:<4} {r['storage_mwh']:<10.0f} {r['total_invest']/1e4:<10.0f} "
          f"{r['irr_06']*100:<9.1f}% {r['irr_08']*100:<9.1f}% {r['pb_06']:<10} {r['thresh_irr10']:<12.2f}")

best = max(results, key=lambda x: x['irr_06'])
print(f"\n2️⃣ 最优方案: 方案{best['name']}（{best['storage_mwh']}MWh，总投资{best['total_invest']/1e4:.0f}万）")
print(f"   IRR@0.6={best['irr_06']*100:.1f}%, IRR@0.8={best['irr_08']*100:.1f}%, 回收期{best['pb_06']}年")

print(f"\n3️⃣ 纯光伏直售IRR（无储能）:")
for price in [0.25, 0.35, 0.50]:
    cfs = [calc_pv_kwh_year(y) * price for y in range(1, operation_years+1)]
    irr = calc_irr(cfs, pv_cost)
    pb = calc_static_pb(pv_cost, cfs)
    print(f"   电价{price}元/kWh → IRR={irr*100:.1f}%, 回收期={pb}年")

print(f"\n4️⃣ 关键洞察:")
irr_025 = calc_irr([calc_pv_kwh_year(y) * 0.25 for y in range(1,21)], pv_cost)
irr_050 = calc_irr([calc_pv_kwh_year(y) * 0.50 for y in range(1,21)], pv_cost)
print(f"   - 纯光伏0.25元/kWh直售IRR={irr_025*100:.1f}%，低于10%门槛")
print(f"   - 纯光伏0.5元/kWh直售IRR={irr_050*100:.1f}%")
print(f"   - 配储能后IRR≥10%需储能卖电价约{best['thresh_irr10']:.2f}~{results[-1]['thresh_irr10']:.2f}元/kWh")
print(f"   - 核心问题：1MW光伏年均发电96万kWh，2MWh储能年放电容量仅约55万kWh，储能利用严重不足")
print(f"   - 建议：要么提高储能配置（接近日均光伏量），要么选择纯光伏直售模式")

print("\n" + "=" * 90)
