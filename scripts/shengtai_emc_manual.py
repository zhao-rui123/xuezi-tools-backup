#!/usr/bin/env python3
"""
盛泰药业 EMC模式：手动精确计算
- 储能: 3.75MW/7.5MWh (15台×0.5MWh)
- 光伏: 2MWp
- 山东分时电价: 峰0.92/平0.64/谷0.31
- EMC投资方分成: 90%
- VPP年收益: 32万元
- CAPEX: 储能1200万 + 光伏800万 = 2000万
- 年运维: 2000万×1.5% = 30万
- 放电效率: 85%
"""
years = 15
discount = 0.08
storage_mwh = 7.5
storage_mw = 3.75
pv_mwp = 2.0

# 放电量估算 (每天2次循环，年600次)
daily_discharge = storage_mwh * 2  # 15MWh/day
annual_discharge_mwh = daily_discharge * 300  # 实际运营300天

# 峰谷价差套利 (谷0.31充, 峰0.92放, 85%效率)
avg_spread = 0.92 - 0.31  # = 0.61元/kWh
gross_annual = annual_discharge_mwh * 1000 * avg_spread  # 总套利收益(未分成)
emc_investor_share = gross_annual * 0.90  # 投资方90% = 2,745,000元

# 光伏自发自用 (2MWp, 年均1777MWh, 替代平段0.64元)
pv_annual_kwh = 1777000  # 估算
pv_saving = pv_annual_kwh * 0.64  # 1,137,280元

# VPP收益
vpp_revenue = 320000

# 年总收入 (投资方)
annual_revenue = emc_investor_share + pv_saving + vpp_revenue
print(f"年总收入(投资方): {annual_revenue:,.0f} 元 = {annual_revenue/10000:.1f} 万")

# 年运维成本
opex_annual = 20000000 * 0.015  # 30万
net_annual = annual_revenue - opex_annual
print(f"年运维成本: {opex_annual:,.0f} 元")
print(f"年均净收益: {net_annual:,.0f} 元 = {net_annual/10000:.1f} 万")

# DCF IRR 计算
capex = 20000000  # 2000万
cashflows = [-capex] + [net_annual] * years

# IRR 迭代计算
def npv_at_rate(r):
    return sum(cf / (1+r)**t for t, cf in enumerate(cashflows))

# 牛顿法求IRR
r = 0.10
for _ in range(100):
    npv = npv_at_rate(r)
    d_npv = sum(-t * cf / (1+r)**(t+1) for t, cf in enumerate(cashflows))
    if abs(d_npv) < 1e-10: break
    r -= npv / d_npv
    if r < 0 or r > 1: r = 0.10

print(f"\nIRR: {r*100:.2f}%")

# 回收期
cum = -capex
for t, cf in enumerate(cashflows[1:], 1):
    cum += cf
    if cum >= 0:
        print(f"回收期: {t}年 {(1-cum/cf):.0f}个月")
        break

# NPV
npv = npv_at_rate(discount)
print(f"NPV (8%折现率): {npv/10000:.1f} 万元")

print(f"\n=== 敏感性分析 ===")
for capex_multiplier in [0.8, 0.9, 1.0, 1.1, 1.2]:
    cap = capex * capex_multiplier
    cfs = [-cap] + [net_annual] * years
    r_test = 0.10
    for _ in range(100):
        np = sum(cf/(1+r_test)**t for t,cf in enumerate(cfs))
        d = sum(-t*cf/(1+r_test)**(t+1) for t,cf in enumerate(cfs))
        if abs(d)<1e-10: break
        r_test -= np/d
        if r_test<0 or r_test>1: r_test=0.10
    print(f"  CAPEX×{capex_multiplier:.1f}: IRR={r_test*100:.1f}% (CAPEX={cap/10000:.0f}万)")