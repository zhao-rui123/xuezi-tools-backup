"""
光储一体化系统最优储能配置计算
目标：找出IRR最高的配置
"""

import numpy as np
import numpy_financial as npf

# ============================================================
# 固定参数
# ============================================================
PV_CAPACITY_KW = 1000          # 1 MW = 1000 kW
PV_COST_TOTAL = 2_000_000     # 光伏总投资 200万
PV_EFFICIENCY = 0.80          # 光伏效率(装机容量因子)
PV_DEGRADATION = 0.02        # 光伏衰减 2%/年
SUNSHINE_HOURS = 1200         # 年日照小时数(河南)
STORAGE_EFF = 0.88            # 储能充放效率(单次)
STORAGE_DEG = 0.015           # 储能衰减 1.5%/年
DOD = 0.95                    # 放电深度
ANNUAL_CYCLES = 330           # 年充放次数
DIRECT_PRICE = 0.25           # 直售电价 元/kWh
OPERATING_YEARS = 20

# 方案配置: (储能容量MWh, 储能成本万, 储能总投资万)
SCHEMES = {
    'A': {'storage_mwh': 1, 'storage_cost': 100, 'total_invest': 220},
    'B': {'storage_mwh': 2, 'storage_cost': 200, 'total_invest': 420},
    'C': {'storage_mwh': 3, 'storage_cost': 300, 'total_invest': 520},
    'D': {'storage_mwh': 4, 'storage_cost': 400, 'total_invest': 620},
}


def compute_annual_pv_generation(year: int) -> float:
    """计算第year年的光伏发电量(kWh), 考虑衰减"""
    degradation_factor = (1 - PV_DEGRADATION) ** (year - 1)
    gen = PV_CAPACITY_KW * SUNSHINE_HOURS * PV_EFFICIENCY * degradation_factor
    return gen


def compute_usable_capacity(storage_mwh: float, year: int) -> float:
    """计算第year年的储能可用容量(kWh), 考虑衰减和DOD"""
    deg_factor = (1 - STORAGE_DEG) ** (year - 1)
    return storage_mwh * 1000 * DOD * deg_factor


def compute_scheme_metrics(storage_mwh: float, total_invest_wan: float, 
                            storage_discharge_price: float) -> dict:
    """
    计算给定储能放电电价下，某个方案的20年IRR和静态回收期
    """
    annual_revenues = []
    
    for year in range(1, OPERATING_YEARS + 1):
        # 1. 光伏发电量(kWh)
        pv_gen = compute_annual_pv_generation(year)
        
        # 2. 储能最大可用容量(kWh)
        usable_cap = compute_usable_capacity(storage_mwh, year)
        
        # 3. 最大可存储能量(kWh), 考虑充放效率
        # 储能可以充电的最大量(放电侧)
        max_storage_discharge = usable_cap * ANNUAL_CYCLES
        
        # 实际储能系统能吞吐的能量受限于光伏发电量
        # 可用于储能的光伏电量 = 总发电量(简化:全部用于直接消纳+储能)
        # 储能实际放电量 = min(最大可放电量, 总发电量)
        # 这里假设年发电量足够支持储能循环
        actual_storage_discharge = min(max_storage_discharge, pv_gen)
        
        # 4. 收入计算
        # 直售收入: 余电按0.25直售 (简化: 储能充满后的余量)
        # 储能实际充电量 = actual_storage_discharge / STORAGE_EFF (充电损耗)
        # 实际用于储能充电的光伏 = actual_storage_discharge / STORAGE_EFF
        # 剩余直接消纳/直售 = pv_gen - actual_storage_discharge / STORAGE_EFF
        # 但这样算可能导致负数
        
        # 换个思路:
        # 储能每次循环: 充入 E/0.88, 放出 E, 损耗 0.136E
        # 总发电量中，储能吞吐消耗的光伏 = actual_storage_discharge / STORAGE_EFF
        # 直接消纳/直售 = pv_gen - actual_storage_discharge / STORAGE_EFF
        
        storage_charge_from_pv = actual_storage_discharge / STORAGE_EFF
        direct_pv_kwh = pv_gen - storage_charge_from_pv
        
        # 确保非负
        direct_pv_kwh = max(0, direct_pv_kwh)
        
        # 直售收入(多余电量按0.25卖)
        direct_revenue = direct_pv_kwh * DIRECT_PRICE / 10000  # 转为万
        
        # 储能放电收入(按市场化价格)
        storage_revenue = actual_storage_discharge * storage_discharge_price / 10000  # 转为万
        
        total_revenue = direct_revenue + storage_revenue
        annual_revenues.append(total_revenue)
    
    # 静态回收期
    cumulative = 0.0
    static_payback = None
    for i, rev in enumerate(annual_revenues):
        cumulative += rev
        if cumulative >= total_invest_wan and static_payback is None:
            # 线性插值
            prev = cumulative - rev
            frac = (total_invest_wan - prev) / rev
            static_payback = i + frac
            break
    
    # 计算20年IRR
    cash_flows = [-total_invest_wan] + annual_revenues
    irr = npf.irr(cash_flows)
    
    # 总收入
    total_revenue_sum = sum(annual_revenues)
    total_profit = total_revenue_sum - total_invest_wan
    
    return {
        'irr': irr,
        'static_payback': static_payback,
        'total_profit': total_profit,
        'annual_revenues': annual_revenues,
        'total_revenue_sum': total_revenue_sum,
    }


def binary_search_storage_price(target_irr: float, storage_mwh: float, 
                                  total_invest_wan: float,
                                  low: float = 0.1, high: float = 5.0,
                                  tol: float = 0.0001, max_iter: int = 100) -> float:
    """二分法反推: IRR=target_irr 时储能需要卖多少电价"""
    for _ in range(max_iter):
        mid = (low + high) / 2
        result = compute_scheme_metrics(storage_mwh, total_invest_wan, mid)
        irr = result['irr']
        
        if abs(irr - target_irr) < tol:
            return mid
        
        if irr < target_irr:
            low = mid  # 需要更高电价
        else:
            high = mid  # 需要更低电价
    
    return mid


def binary_search_price_for_payback(target_payback: float, storage_mwh: float,
                                      total_invest_wan: float,
                                      low: float = 0.1, high: float = 10.0,
                                      tol: float = 0.01, max_iter: int = 100) -> float:
    """二分法反推: 静态回收期≤target_payback时储能需要卖多少电价"""
    for _ in range(max_iter):
        mid = (low + high) / 2
        result = compute_scheme_metrics(storage_mwh, total_invest_wan, mid)
        payback = result['static_payback']
        
        if payback is None:
            # 永远收不回本，尝试更低电价（更高IRR）
            low = mid
            continue
        
        if abs(payback - target_payback) < tol:
            return mid
        
        if payback > target_payback:
            low = mid  # 需要更高电价(更高收入→更快回本)
        else:
            high = mid  # 需要更低电价
    
    # 返回mid(可能未收敛)
    result = compute_scheme_metrics(storage_mwh, total_invest_wan, mid)
    return mid


def main():
    print("=" * 80)
    print("光储一体化系统 - 最优储能配置计算")
    print("=" * 80)
    print(f"\n固定参数:")
    print(f"  光伏装机: {PV_CAPACITY_KW} kW | 光伏成本: {PV_COST_TOTAL/10000:.0f}万元")
    print(f"  光伏效率: {PV_EFFICIENCY*100:.0f}% | 光伏衰减: {PV_DEGRADATION*100:.0f}%/年")
    print(f"  日照(河南): {SUNSHINE_HOURS}h/年 | 储能充放效率: {STORAGE_EFF*100:.0f}%")
    print(f"  储能衰减: {STORAGE_DEG*100:.1f}%/年 | 放电深度: {DOD*100:.0f}%")
    print(f"  年充放次数: {ANNUAL_CYCLES}次 | 直售电价: {DIRECT_PRICE}元/kWh")
    print(f"  运行年限: {OPERATING_YEARS}年 | 不换电芯")
    print()
    
    results = {}
    
    for scheme_name, cfg in SCHEMES.items():
        sm = cfg['storage_mwh']
        ti = cfg['total_invest']
        
        # 1. 反推 IRR=10% 时储能卖电价
        price_for_irr10 = binary_search_storage_price(0.10, sm, ti, low=0.01, high=5.0)
        
        # 2. 反推 回收期≤7年 时储能卖电价
        price_for_payback7 = binary_search_price_for_payback(7.0, sm, ti, low=0.01, high=10.0)
        
        # 3. 储能卖0.6元时的IRR
        r06 = compute_scheme_metrics(sm, ti, 0.6)
        
        # 4. 储能卖0.8元时的IRR
        r08 = compute_scheme_metrics(sm, ti, 0.8)
        
        # 5. 直接消纳(储能卖0.25即等于直售电价)时的IRR
        r025 = compute_scheme_metrics(sm, ti, 0.25)
        
        results[scheme_name] = {
            'price_for_irr10': price_for_irr10,
            'price_for_payback7': price_for_payback7,
            'irr_06': r06['irr'],
            'irr_08': r08['irr'],
            'irr_025': r025['irr'],
            'payback_06': r06['static_payback'],
            'payback_08': r08['static_payback'],
            'payback_025': r025['static_payback'],
            'total_profit_06': r06['total_profit'],
            'total_profit_08': r08['total_profit'],
            'total_revenue_06': r06['total_revenue_sum'],
        }
    
    # ============================================================
    # 打印详细结果
    # ============================================================
    print("\n" + "=" * 80)
    print("【各方案逐年计算详情 - 储能卖0.6元/kWh】")
    print("=" * 80)
    
    for scheme_name, cfg in SCHEMES.items():
        sm = cfg['storage_mwh']
        ti = cfg['total_invest']
        r = compute_scheme_metrics(sm, ti, 0.6)
        
        print(f"\n方案{scheme_name} (储能{sm}MWh, 总投资{ti}万元):")
        print(f"  {'年份':>4} | {'光伏发电(kWh)':>14} | {'储能可放(kWh)':>14} | {'年收入(万元)':>12} | {'累计(万元)':>12}")
        print(f"  {'-'*4}-+-{'-'*14}-+-{'-'*14}-+-{'-'*12}-+-{'-'*12}")
        
        cum = -ti
        for year in range(1, OPERATING_YEARS + 1):
            pv_gen = compute_annual_pv_generation(year)
            usable = compute_usable_capacity(sm, year)
            max_dis = usable * ANNUAL_CYCLES
            actual_dis = min(max_dis, pv_gen)
            storage_charge_from_pv = actual_dis / STORAGE_EFF
            direct_pv = max(0, pv_gen - storage_charge_from_pv)
            direct_rev = direct_pv * DIRECT_PRICE / 10000
            storage_rev = actual_dis * 0.6 / 10000
            total_rev = direct_rev + storage_rev
            cum += total_rev
            
            if year <= 5 or year == 20:
                print(f"  {year:>4} | {pv_gen:>14,.0f} | {actual_dis:>14,.0f} | {total_rev:>12.2f} | {cum:>12.2f}")
            elif year == 6:
                print(f"  ... (中间年份省略) ... ")
        
        print(f"\n  20年总收入: {r['total_revenue_sum']:.2f}万元 | 总利润: {r['total_profit']:.2f}万元")
        print(f"  IRR: {r['irr']*100:.2f}% | 静态回收期: {r['static_payback']:.2f}年")

    # ============================================================
    # 输出汇总表格
    # ============================================================
    print("\n" + "=" * 100)
    print("【汇总表格】")
    print("=" * 100)
    print()
    header = f"| {'方案':^4} | {'储能':^6} | {'总投资':^8} | {'IRR=10%门槛':^14} | {'回收期≤7年':^14} | {'IRR(卖0.6)':^12} | {'IRR(卖0.8)':^12} | {'IRR(卖0.25)':^12} | {'推荐':^4} |"
    print(header)
    print(f"|{'-'*6}-+-{'-'*8}-+-{'-'*16}-+-{'-'*16}-+-{'-'*14}-+-{'-'*14}-+-{'-'*14}-+-{'-'*6}|")
    
    # 找出IRR最高者(在0.6和0.8电价下)
    irr_06_best = max(results.keys(), key=lambda k: results[k]['irr_06'])
    irr_08_best = max(results.keys(), key=lambda k: results[k]['irr_08'])
    
    for scheme_name in SCHEMES:
        r = results[scheme_name]
        # 判断推荐
        if r['irr_06'] > 0.10:
            recommend = "⭐" if scheme_name == irr_06_best else "✓"
        else:
            recommend = "✗"
        
        irr10_str = f"{r['price_for_irr10']:.3f}"
        pb7_str = f"{r['price_for_payback7']:.3f}" if r['price_for_payback7'] else "∞"
        irr06_str = f"{r['irr_06']*100:.2f}%"
        irr08_str = f"{r['irr_08']*100:.2f}%"
        irr025_str = f"{r['irr_025']*100:.2f}%"
        
        row = f"| {scheme_name:^4} | {SCHEMES[scheme_name]['storage_mwh']:>4}MW | {SCHEMES[scheme_name]['total_invest']:>6}万 | {irr10_str:>14} | {pb7_str:>14} | {irr06_str:>12} | {irr08_str:>12} | {irr025_str:>12} | {recommend:^4} |"
        print(row)
    
    print()
    print("=" * 100)
    print("【结论分析】")
    print("=" * 100)
    
    # IRR比较
    irr6_vals = {k: results[k]['irr_06'] for k in results}
    irr8_vals = {k: results[k]['irr_08'] for k in results}
    best_6 = max(irr6_vals, key=irr6_vals.get)
    best_8 = max(irr8_vals, key=irr8_vals.get)
    
    print(f"\n1. IRR最高配置(储能卖0.6元): 方案{best_6} = {irr6_vals[best_6]*100:.2f}%")
    print(f"2. IRR最高配置(储能卖0.8元): 方案{best_8} = {irr8_vals[best_8]*100:.2f}%")
    
    print(f"\n3. 各配置IRR对比(储能卖0.6元):")
    for k in sorted(irr6_vals.keys()):
        v = irr6_vals[k]
        bar = "█" * int(v * 100)
        print(f"   方案{k}: {v*100:6.2f}% {bar}")
    
    print(f"\n4. 各配置IRR对比(储能卖0.8元):")
    for k in sorted(irr8_vals.keys()):
        v = irr8_vals[k]
        bar = "█" * int(v * 100)
        print(f"   方案{k}: {v*100:6.2f}% {bar}")
    
    print(f"\n5. IRR=10%门槛电价(储能卖):")
    for k in sorted(results.keys()):
        v = results[k]['price_for_irr10']
        print(f"   方案{k}: {v:.3f} 元/kWh")
    
    print(f"\n6. 回收期≤7年门槛电价(储能卖):")
    for k in sorted(results.keys()):
        v = results[k]['price_for_payback7']
        print(f"   方案{k}: {v:.3f} 元/kWh (回收期{results[k]['payback_06']:.2f}年@0.6元)")
    
    # 最终推荐
    print(f"\n" + "=" * 50)
    best_scheme = best_6
    print(f"【最终推荐】: 方案{best_scheme}")
    print(f"  - 储能容量: {SCHEMES[best_scheme]['storage_mwh']} MWh")
    print(f"  - 总投资: {SCHEMES[best_scheme]['total_invest']}万元")
    print(f"  - IRR(储能卖0.6): {results[best_scheme]['irr_06']*100:.2f}%")
    print(f"  - IRR(储能卖0.8): {results[best_scheme]['irr_08']*100:.2f}%")
    print(f"  - 静态回收期(0.6): {results[best_scheme]['payback_06']:.2f}年")
    print(f"=" * 50)


if __name__ == "__main__":
    main()
