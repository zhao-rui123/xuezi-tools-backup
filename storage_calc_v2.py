#!/usr/bin/env python3
"""
光储一体化系统最优配置计算
修正总投资金额（光伏200万 + 储能100万/MWh）
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
# 修正后的总投资 = 光伏200万 + 储能成本（100万/MWh）
plans = {
    'A': {'storage_mwh': 1, 'storage_cost': 1_000_000},
    'B': {'storage_mwh': 2, 'storage_cost': 2_000_000},
    'C': {'storage_mwh': 3, 'storage_cost': 3_000_000},
    'D': {'storage_mwh': 4, 'storage_cost': 4_000_000},
}

for name, p in plans.items():
    p['total_invest'] = pv_cost + p['storage_cost']


def calc_pv_generation(year, pv_kw=pv_capacity_kw):
    """逐年光伏发电量（kWh），考虑效率和衰减"""
    eff_factor = pv_efficiency * ((1 - pv_decay) ** (year - 1))
    return pv_kw * sunshine_hours * eff_factor


def calc_storage_capacity(year, storage_mwh):
    """储能实际可用容量（考虑衰减和放电深度）"""
    cap = storage_mwh * 1000  # kWh
    decayed = cap * ((1 - storage_decay) ** (year - 1))
    return decayed * depth_of_discharge


def simulate_year(year, storage_mwh, sell_price_storage):
    """
    模拟一年收益
    返回: (直售电量kWh, 储能放电收益)
    """
    pv_kwh = calc_pv_generation(year)
    storage_cap_kwh = calc_storage_capacity(year, storage_mwh)  # 可用容量

    if storage_mwh == 0:
        # 纯光伏，全部直售
        direct_kwh = pv_kwh
        storage_discharge_kwh = 0
    else:
        # 储能优先充满
        storage_chargeable = storage_cap_kwh * annual_cycles  # 最大可充放电总量
        storage_input = min(pv_kwh, storage_chargeable / storage_eff)  # 实际充入量
        storage_output = storage_input * storage_eff  # 实际放出量
        direct_kwh = max(0, pv_kwh - storage_input / storage_eff)  # 剩余直售

        # 储能每年实际放电量 = 330次 × 衰减后容量（每次放满DOD）
        storage_discharge_kwh = annual_cycles * calc_storage_capacity(year, storage_mwh)

    return direct_kwh, storage_discharge_kwh


def calc_annual_revenue(year, storage_mwh, sell_price_storage, sell_price_direct=None):
    """计算年度总收入"""
    if sell_price_direct is None:
        sell_price_direct = direct_sell_price
    direct_kwh, storage_discharge_kwh = simulate_year(year, storage_mwh, sell_price_storage)
    revenue = direct_kwh * sell_price_direct + storage_discharge_kwh * sell_price_storage
    return revenue


def calc_irr(total_invest, annual_revenues, years=operation_years):
    """二分法计算IRR"""
    def npv(rate):
        return sum(r / (1 + rate) ** t for t, r in enumerate(annual_revenues)) - total_invest

    low, high = -0.99, 10.0
    for _ in range(100):
        mid = (low + high) / 2
        if npv(mid) > 0:
            high = mid
        else:
            low = mid
        if abs(high - low) < 1e-8:
            break
    irr = (low + high) / 2
    return irr


def calc_static_payback(total_invest, annual_revenues):
    """静态回收期（累计现金流首次为正的年份）"""
    cumulative = -total_invest
    for t, r in enumerate(annual_revenues, 1):
        cumulative += r
        if cumulative >= 0:
            return t
    return f">{operation_years}"


def calc_irr_for_sell_price(storage_mwh, total_invest, sell_price, sell_price_direct=None):
    """给定储能卖电价，计算IRR"""
    if sell_price_direct is None:
        sell_price_direct = direct_sell_price
    revenues = [calc_annual_revenue(y, storage_mwh, sell_price, sell_price_direct) for y in range(1, operation_years + 1)]
    return calc_irr(total_invest, revenues)


def find_threshold_sell_price(storage_mwh, total_invest, target_irr=0.10):
    """找到IRR=target_irr时对应的储能卖电价（二分法）"""
    low, high = 0.01, 5.0
    for _ in range(100):
        mid = (low + high) / 2
        irr = calc_irr_for_sell_price(storage_mwh, total_invest, mid)
        if irr > target_irr:
            high = mid
        else:
            low = mid
        if abs(high - low) < 1e-6:
            break
    return (low + high) / 2


def find_payback_sell_price(storage_mwh, total_invest, max_years=7):
    """找到静态回收期≤max_years时对应的储能卖电价（二分法）"""
    low, high = 0.01, 5.0
    for _ in range(100):
        mid = (low + high) / 2
        irr = calc_irr_for_sell_price(storage_mwh, total_invest, mid)
        payback = calc_static_payback(total_invest,
            [calc_annual_revenue(y, storage_mwh, mid) for y in range(1, operation_years + 1)])
        if isinstance(payback, str) or payback > max_years:
            low = mid
        else:
            high = mid
        if abs(high - low) < 1e-6:
            break
    return (low + high) / 2


# ============ 附加：纯光伏直售IRR（不同电价） ============
def calc_pv_only_irr(sell_price):
    """纯光伏（不配储能）按sell_price全量直售的IRR"""
    revenues = [calc_pv_generation(y) * sell_price for y in range(1, operation_years + 1)]
    return calc_irr(pv_cost, revenues)


# ============ 输出表格 ============
print("=" * 100)
print("光储一体化系统最优配置计算结果")
print("=" * 100)
print(f"\n固定参数:")
print(f"  光伏装机: {pv_capacity_kw/1000} MW = {pv_capacity_kw} kW")
print(f"  光伏成本: {pv_cost/1e4:.0f}万 ({pv_cost}元)")
print(f"  光伏效率: {pv_efficiency*100:.0f}%, 衰减: {pv_decay*100:.1f}%/年")
print(f"  日照: {sunshine_hours}h/年")
print(f"  储能充放效率: {storage_eff*100:.0f}%, 衰减: {storage_decay*100:.1f}%/年")
print(f"  放电深度: {depth_of_discharge*100:.0f}%, 年充放次数: {annual_cycles}")
print(f"  直售电价: {direct_sell_price}元/kWh, 运行年限: {operation_years}年")

print("\n" + "=" * 100)
print("【主表】各方案对比")
print("=" * 100)

header = f"{'方案':<4} {'储能(MWh)':<10} {'总投资(万)':<10} {'IRR=10%门槛\n储能卖电价':<14} {'回收期≤7年\n储能卖电价':<14} {'IRR(卖0.6元)':<12} {'IRR(卖0.8元)':<12} {'推荐':<6}"
print(header)
print("-" * 100)

results = []
for name, p in plans.items():
    storage_mwh = p['storage_mwh']
    total_invest = p['total_invest']

    # IRR=10%门槛（储能卖电价）
    threshold_price_irr10 = find_threshold_sell_price(storage_mwh, total_invest, 0.10)

    # 回收期≤7年门槛（储能卖电价）
    threshold_price_payback7 = find_payback_sell_price(storage_mwh, total_invest, 7)

    # IRR(卖0.6元)
    irr_06 = calc_irr_for_sell_price(storage_mwh, total_invest, 0.6)

    # IRR(卖0.8元)
    irr_08 = calc_irr_for_sell_price(storage_mwh, total_invest, 0.8)

    # 推荐（综合判断）
    if irr_06 >= 0.10 and threshold_price_irr10 <= 0.6:
        rec = "✅ 优"
    elif irr_06 >= 0.08:
        rec = "⚠️ 可"
    else:
        rec = "❌ 差"

    results.append({
        'name': name,
        'storage_mwh': storage_mwh,
        'total_invest': total_invest,
        'threshold_price_irr10': threshold_price_irr10,
        'threshold_price_payback7': threshold_price_payback7,
        'irr_06': irr_06,
        'irr_08': irr_08,
        'rec': rec
    })

    print(f"{name:<4} {storage_mwh:<10.0f} {total_invest/1e4:<10.0f} {threshold_price_irr10:<14.2f} {threshold_price_payback7:<14.2f} {irr_06*100:<11.1f}% {irr_08*100:<11.1f}% {rec:<6}")

print("-" * 100)

# ============ 附加：纯光伏直售IRR ============
print("\n" + "=" * 100)
print("【附加】纯光伏（1MW）不同电价直售IRR（不配储能）")
print("=" * 100)

# 纯光伏年发电量（第一年，供参考）
pv_y1 = calc_pv_generation(1)
print(f"\n纯光伏年发电量（首年）: {pv_y1:.0f} kWh = {pv_y1/1e6:.2f} GWh")
print(f"纯光伏总投资: {pv_cost/1e4:.0f}万")

pv_only_prices = [0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60, 0.80, 1.00]
print(f"\n{'电价(元/kWh)':<14} {'年收益(万)':<12} {'IRR':<10} {'静态回收期':<12}")
print("-" * 50)
for price in pv_only_prices:
    irr = calc_pv_only_irr(price)
    annual_rev = pv_y1 * price / 1e4
    payback = calc_static_payback(pv_cost, [calc_pv_generation(y) * price for y in range(1, operation_years + 1)])
    print(f"{price:<14.2f} {annual_rev:<12.1f} {irr*100:<9.1f}% {str(payback):<12}")

print("-" * 50)

# ============ 逐年数据明细（方案B为例） ============
print("\n" + "=" * 100)
print("【明细】方案B（2 MWh储能）逐年数据")
print("=" * 100)

b_storage = 2
b_invest = plans['B']['total_invest']
print(f"\n{'年份':<4} {'光伏发电\n(kWh)':<14} {'储能可用\n容量(kWh)':<14} {'直售电量\n(kWh)':<14} {'储能放电\n(kWh)':<14} {'总收入\n(万元)':<10}")
print("-" * 100)

cumulative = -b_invest
for y in range(1, operation_years + 1):
    pv_kwh = calc_pv_generation(y)
    storage_cap = calc_storage_capacity(y, b_storage)
    direct_kwh, storage_dis_kwh = simulate_year(y, b_storage, 0.6)
    # 用0.6元/kWh储能卖电价计算
    rev = direct_kwh * direct_sell_price + storage_dis_kwh * 0.6
    cumulative += rev
    print(f"{y:<4} {pv_kwh:<14.0f} {storage_cap:<14.0f} {direct_kwh:<14.0f} {storage_dis_kwh:<14.0f} {rev/1e4:<10.1f}")

print(f"\n方案B总投资: {b_invest/1e4:.0f}万 | 方案B IRR(储能卖0.6): {results[1]['irr_06']*100:.1f}%")

# ============ 结论 ============
print("\n" + "=" * 100)
print("【结论】")
print("=" * 100)

best_plan = max(results, key=lambda x: x['irr_06'])
print(f"\n1. 各方案IRR(储能卖0.6元/kWh):")
for r in results:
    print(f"   方案{r['name']}: {r['irr_06']*100:.1f}% (总投资{r['total_invest']/1e4:.0f}万)")

print(f"\n2. 最优方案: 方案{best_plan['name']}（储能{best_plan['storage_mwh']}MWh，总投资{best_plan['total_invest']/1e4:.0f}万）")

print(f"\n3. 纯光伏直售IRR对比:")
for price in [0.25, 0.35, 0.50]:
    irr = calc_pv_only_irr(price)
    print(f"   电价{price}元/kWh → IRR={irr*100:.1f}%")

print(f"\n4. 关键发现:")
print(f"   - 纯光伏0.25元/kWh直售IRR约{calc_pv_only_irr(0.25)*100:.1f}%，低于10%门槛")
print(f"   - 纯光伏0.5元/kWh直售IRR约{calc_pv_only_irr(0.5)*100:.1f}%")
print(f"   - 配储能后，储能卖电价需达到约{best_plan['threshold_price_irr10']:.2f}元/kWh才能IRR≥10%")
print(f"   - 储能回收期对卖电价极为敏感，建议重点评估当地峰谷电价差")

print("\n" + "=" * 100)
