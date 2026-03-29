"""
工商业光储一体化系统经济账计算
模式二：光储一体化分析
单位系统：kWh/元，内部统一
"""
from scipy.optimize import brentq

# ============ 基础参数 ============
pv_capacity_kW = 1000          # 光伏装机 kW
pv_cost_per_W = 2.0            # 元/W
pv_cost = pv_capacity_kW * 1000 * pv_cost_per_W  # 元

storage_capacity_kWh = 2000     # 储能容量 kWh
storage_cost_per_Wh = 1.0      # 元/Wh
storage_cost = storage_capacity_kWh * storage_cost_per_Wh * 1000  # 元

battery_replacement_cost = 0.5 * 1000 * storage_capacity_kWh  # 元 (0.5元/kWh × 2000 kWh)

total_investment = 500 * 10000  # 总投资 元

sunshine_hours_annual = 1200   # 年等效小时数 h
pv_efficiency = 0.80           # 光伏综合效率
round_trip_eff = 0.88          # 储能充放电来回效率（0.94×0.94）
single_eff = round_trip_eff ** 0.5  # 单程效率 ≈ 0.938

annual_decay_rate = 0.02       # 年衰减率（光伏+储能）
annual_cycle_count = 330      # 年充放次数
dod = 0.95                     # 放电深度
pv_sell_price = 0.25           # 光伏多余卖电价格 元/kWh
project_years = 20             # 运行年限
discount_rate = 0.05          # 折现率（用于LCOE）

# ============ 逐年计算 ============
years = list(range(1, project_years + 1))

# 1. 逐年光伏发电量（kWh）
pv_output_kWh = []
decay_pv = 1.0
for y in years:
    annual_pv = pv_capacity_kW * sunshine_hours_annual * pv_efficiency * decay_pv
    pv_output_kWh.append(annual_pv)
    decay_pv *= (1 - annual_decay_rate)

# 2. 逐年储能可充电/放电量
# 储能每次完全循环：充入 1kWh（考虑充电效率），放出 1×sqrt(0.88) kWh
# 充入/放出比 = 1/single_eff ≈ 1.066
# 即每次循环需要充入 storage_capacity*dod/single_eff kWh的光伏电，才能放出 storage_capacity*dod kWh

# 每年需要的储能充电量（kWh）
storage_charge_needed_kWh = []  # 储能每年需要从光伏充电的量
for i, y in enumerate(years):
    cap = storage_capacity_kWh * (1 - annual_decay_rate)**y
    charge_per_cycle = cap * dod / single_eff  # 每次循环需要的充电量(kWh，光伏侧)
    annual_charge = charge_per_cycle * annual_cycle_count
    storage_charge_needed_kWh.append(annual_charge)

# 3. 逐年运行模式计算
pv_to_storage_kWh = []     # 光伏充入储能的电量（kWh）
pv_direct_sell_kWh = []    # 光伏直接卖的电量（kWh）
storage_discharge_sell_kWh = []  # 储能放电卖的电量（kWh，即实际放出的净电）

for i, y in enumerate(years):
    pv_gen = pv_output_kWh[i]
    charge_needed = storage_charge_needed_kWh[i]
    
    # 充电量 = min(需要量, 光伏发电量)
    actual_charge = min(charge_needed, pv_gen)
    
    # 剩余光伏直接卖
    surplus = max(0, pv_gen - actual_charge)
    
    # 储能实际放电量（从储能系统输出的净电量）
    actual_discharge = actual_charge * single_eff
    
    pv_to_storage_kWh.append(actual_charge)
    pv_direct_sell_kWh.append(surplus)
    storage_discharge_sell_kWh.append(actual_discharge)

# ============ 打印结果 ============
print("=" * 60)
print("工商业光储一体化系统经济账计算（模式二）")
print("=" * 60)

print(f"\n【基础参数】")
print(f"  光伏装机: {pv_capacity_kW} kW = 1 MW")
print(f"  光伏成本: {pv_cost/10000:.0f} 万元 (2元/W × 1000kW)")
print(f"  储能容量: {storage_capacity_kWh} kWh = 2 MWh")
print(f"  储能成本: {storage_cost/10000:.0f} 万元 (1元/Wh × 2000kWh)")
print(f"  第10年换电芯: {battery_replacement_cost/10000:.0f} 万元")
print(f"  总投资: {total_investment/10000:.0f} 万元（含{battery_replacement_cost/10000:.0f}万备用）")
print(f"  年等效小时: {sunshine_hours_annual} h")
print(f"  光伏综合效率: {pv_efficiency*100:.0f}%")
print(f"  储能单程效率: {single_eff*100:.1f}% (来回{round_trip_eff*100:.0f}%)")
print(f"  年衰减率: {annual_decay_rate*100:.0f}%")
print(f"  年充放次数: {annual_cycle_count}")
print(f"  放电深度: {dod*100:.0f}%")
print(f"  光伏卖电价格: {pv_sell_price} 元/kWh")
print(f"  运行年限: {project_years} 年")

print(f"\n【光伏发电量】")
for i, y in enumerate(years):
    print(f"  第{y:2d}年: {pv_output_kWh[i]/10000:.2f} 万kWh  "
          f"(当年储能需充电: {storage_charge_needed_kWh[i]/10000:.2f} 万kWh)")

print(f"\n【光伏发电分配（20年汇总）】")
total_pv_gen = sum(pv_output_kWh)
total_direct_sell = sum(pv_direct_sell_kWh)
total_to_storage = sum(pv_to_storage_kWh)
total_storage_discharge = sum(storage_discharge_sell_kWh)

print(f"  光伏20年总发电量: {total_pv_gen/10000:.2f} 万kWh")
print(f"  充入储能总量: {total_to_storage/10000:.2f} 万kWh")
print(f"  储能总放电量: {total_storage_discharge/10000:.2f} 万kWh")
print(f"  直接卖电总量: {total_direct_sell/10000:.2f} 万kWh")

# 验证能量守恒
pv_used = total_to_storage + total_direct_sell
print(f"  能量守恒校验: {pv_used/10000:.2f} 万kWh (偏差 {(total_pv_gen-pv_used)/10000:.4f} 万kWh)")

# ============ 收入结构 ============
direct_ratio = total_direct_sell / total_pv_gen * 100
storage_ratio = total_storage_discharge / total_pv_gen * 100

print(f"\n【收入结构】")
print(f"  光伏→直接卖出: {total_direct_sell/10000:.2f} 万kWh ({direct_ratio:.1f}%)")
print(f"  光伏→储能→卖出: {total_storage_discharge/10000:.2f} 万kWh ({storage_ratio:.1f}%)")
print(f"  储能总放电量（20年）: {total_storage_discharge/10000:.2f} 万kWh")
print(f"  储能总循环次数（20年）: {annual_cycle_count * project_years} 次")
print(f"  平均每次循环放电: {total_storage_discharge / (annual_cycle_count * project_years):.1f} kWh")

# ============ 现金流计算函数 ============
def calculate_cashflows(storage_price):
    """
    给定储能卖电价格，计算20年现金流（元）
    """
    cashflows = [-total_investment]  # 第0年
    
    for i, y in enumerate(years):
        pv_rev = pv_direct_sell_kWh[i] * pv_sell_price  # 元
        storage_rev = storage_discharge_sell_kWh[i] * storage_price  # 元
        total_rev = pv_rev + storage_rev
        
        if y == 10:
            total_rev -= battery_replacement_cost  # 减去换电芯
        
        cashflows.append(total_rev)
    
    return cashflows

def npv(r, cashflows):
    return sum(cf / (1 + r) ** t for t, cf in enumerate(cashflows))

def calculate_irr(cashflows):
    try:
        return brentq(npv, 0.001, 3.0, args=(cashflows,))
    except:
        return None

def calculate_payback(cashflows):
    """静态回收期"""
    cumulative = 0
    for i, cf in enumerate(cashflows[1:], 1):
        cumulative += cf
        if cumulative >= 0:
            prev = cumulative - cf
            frac = -prev / cf if cf < 0 else 0
            return i - 1 + frac
    return None

# ============ LCOE计算 ============
# LCOE = 总成本现值 / 总发电量现值
replacement_cost_pv = battery_replacement_cost / (1 + discount_rate) ** 10
total_cost_pv = total_investment + replacement_cost_pv

pv_gen_pv = sum(pv_output_kWh[i] / (1 + discount_rate) ** (i + 1) for i in range(project_years))
lcoe = total_cost_pv / pv_gen_pv  # 元/kWh

print(f"\n【LCOE计算】")
print(f"  初始投资现值: {total_investment:.0f} 元 ({total_investment/10000:.2f} 万元)")
print(f"  第10年换电芯现值: {replacement_cost_pv:.0f} 元 ({replacement_cost_pv/10000:.2f} 万元)")
print(f"  总成本现值: {total_cost_pv:.0f} 元 ({total_cost_pv/10000:.2f} 万元)")
print(f"  光伏20年发电量现值: {pv_gen_pv/10000:.2f} 万kWh")
print(f"  LCOE: {lcoe:.4f} 元/kWh = {lcoe*100:.2f} 分/kWh")

# ============ 基准情况（储能卖电=0.6元/kWh）============
storage_price_benchmark = 0.60
cf_benchmark = calculate_cashflows(storage_price_benchmark)
irr_benchmark = calculate_irr(cf_benchmark)
pb_benchmark = calculate_payback(cf_benchmark)

pv_rev_total = sum(pv_direct_sell_kWh[i] * pv_sell_price for i in range(project_years))
storage_rev_total_benchmark = sum(storage_discharge_sell_kWh[i] * storage_price_benchmark for i in range(project_years))
total_rev_benchmark = pv_rev_total + storage_rev_total_benchmark

print(f"\n【基准情况】储能卖电 = {storage_price_benchmark} 元/kWh")
print(f"  光伏直接卖电收入: {pv_rev_total/10000:.2f} 万元")
print(f"  储能放电卖电收入: {storage_rev_total_benchmark/10000:.2f} 万元")
print(f"  20年总收入: {total_rev_benchmark/10000:.2f} 万元")
print(f"  净收益（含换电芯）: {(total_rev_benchmark - total_investment - battery_replacement_cost)/10000:.2f} 万元")
print(f"  IRR: {irr_benchmark*100:.2f}%" if irr_benchmark else "  IRR: 无法计算（可能亏损）")
print(f"  静态回收期: {pb_benchmark:.2f} 年" if pb_benchmark else "  静态回收期: >20年")

# 逐年现金流明细
print(f"\n  【逐年现金流明细】(储能卖电={storage_price_benchmark}元/kWh)")
print(f"  {'年':>4} {'光伏发电':>10} {'直接卖':>10} {'储能放':>10} {'储能充电':>10} {'当年收入':>12} {'累计':>12}")
cum = -total_investment
for i, y in enumerate(years):
    pv_r = pv_direct_sell_kWh[i] * pv_sell_price / 10000
    st_r = storage_discharge_sell_kWh[i] * storage_price_benchmark / 10000
    inc = pv_r + st_r
    if y == 10:
        inc -= battery_replacement_cost / 10000
    cum += inc
    print(f"  {y:>4} {pv_output_kWh[i]/10000:>10.2f} {pv_direct_sell_kWh[i]/10000:>10.2f} "
          f"{storage_discharge_sell_kWh[i]/10000:>10.2f} {pv_to_storage_kWh[i]/10000:>10.2f} "
          f"{inc:>12.2f} {cum:>12.2f}")

# ============ 敏感性分析 ============
print(f"\n【敏感性分析】")
print(f"  {'储能卖电价':>12} {'IRR':>10} {'回收期':>10} {'净收益(万)':>12}")
print("  " + "-" * 48)

for sp in [0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 1.00, 1.20, 1.50]:
    cf = calculate_cashflows(sp)
    irr = calculate_irr(cf)
    pb = calculate_payback(cf)
    net = sum(cf[1:]) / 10000
    irr_str = f"{irr*100:.2f}%" if irr else "N/A"
    pb_str = f"{pb:.2f}年" if pb else ">20年"
    print(f"  {sp:>12.2f} {irr_str:>12} {pb_str:>12} {net:>12.2f}")

# ============ 关键指标反推 ============
print(f"\n【关键指标反推】")

def find_price_for_irr(target_irr):
    def obj(sp):
        irr = calculate_irr(calculate_cashflows(sp))
        if irr is None:
            return 999
        return irr - target_irr
    try:
        return brentq(obj, 0.01, 10.0)
    except:
        return None

def find_price_for_payback(target_pb):
    def obj(sp):
        pb = calculate_payback(calculate_cashflows(sp))
        if pb is None:
            return 999
        return pb - target_pb
    try:
        return brentq(obj, 0.01, 10.0)
    except:
        return None

# IRR=10%
price_for_irr10 = find_price_for_irr(0.10)
if price_for_irr10:
    cf_irr10 = calculate_cashflows(price_for_irr10)
    irr10_verify = calculate_irr(cf_irr10)
    pb10 = calculate_payback(cf_irr10)
    print(f"  IRR=10%  → 储能卖电价需 ≥ {price_for_irr10:.4f} 元/kWh")
    print(f"    验证: IRR={irr10_verify*100:.2f}%, 静态回收期={pb10:.2f}年")
else:
    print(f"  IRR=10%  → 无法达到（系统收益过低）")

# 回收期≤7年
price_for_pb7 = find_price_for_payback(7.0)
if price_for_pb7:
    cf_pb7 = calculate_cashflows(price_for_pb7)
    irr_pb7 = calculate_irr(cf_pb7)
    print(f"  回收期≤7年  → 储能卖电价需 ≥ {price_for_pb7:.4f} 元/kWh")
    print(f"    验证: IRR={irr_pb7*100:.2f}%, 回收期={7:.2f}年")
else:
    print(f"  回收期≤7年  → 无法达到（系统收益过低）")

# IRR=8%（如果10%太高，看8%）
if price_for_irr10 is None:
    price_for_irr8 = find_price_for_irr(0.08)
    if price_for_irr8:
        cf_irr8 = calculate_cashflows(price_for_irr8)
        irr8_verify = calculate_irr(cf_irr8)
        pb8 = calculate_payback(cf_irr8)
        print(f"\n  IRR=8%  → 储能卖电价需 ≥ {price_for_irr8:.4f} 元/kWh")
        print(f"    验证: IRR={irr8_verify*100:.2f}%, 静态回收期={pb8:.2f}年")

print("\n" + "=" * 60)
print("计算完成")
print("=" * 60)
