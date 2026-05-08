#!/usr/bin/env python3
"""
经济最优方案扫描器 — 自动测试 PV × 储能组合，按 IRR/NPV 排序输出最优。

用法:
  python3 scripts/econ_scan.py <输入文件.json> [--fuel 0.30] [--target irr]

输出:
  - 控制台打印排序结果
  - 可选：输出最优方案的JSON
"""

from energy_solution_agent.engine import analyze_project
import json, sys, argparse

def run_config(data: dict) -> dict:
    """运行单个配置，返回关键指标"""
    result = analyze_project(data)
    r0, r1 = result[0], result[1]
    rec, sim = r0['recommended_solution'], r0['simulation_results']
    fin = r0['financial_results']
    cycles = r1['annual_dispatch'].get('storage_equivalent_full_cycles_per_year', 0)
    return {
        'pv_mwp': rec['pv_mwp'],
        'wind_mw': rec['wind_mw'],
        'storage_mw': rec['storage_power_mw'],
        'storage_mwh': rec['storage_energy_mwh'],
        'pv_gen_mwh': sim['annual_pv_generation_mwh'],
        'wind_gen_mwh': sim['annual_wind_generation_mwh'],
        'discharge_mwh': sim['annual_storage_discharge_mwh'],
        'grid_purchase_mwh': sim['annual_grid_purchase_mwh'],
        'coverage_pct': round(sim['coverage_ratio'] * 100, 1),
        'cycles': round(cycles, 1),
        'capex': fin['capex_total'],
        'annual_opex': fin['opex_annual'],
        'annual_revenue': fin['annual_savings_or_revenue'],
        'irr': fin.get('irr'),
        'npv': fin.get('npv'),
        'payback_years': fin.get('payback_years'),
    }

def main():
    parser = argparse.ArgumentParser(description='经济最优方案扫描器')
    parser.add_argument('input', help='输入JSON文件路径')
    parser.add_argument('--fuel', type=float, default=None, help='燃料成本 USD/kWh')
    parser.add_argument('--target', default='irr', choices=['irr', 'npv'], help='优化目标')
    parser.add_argument('--areas', type=str, default='50000,100000,200000,330000',
                        help='PV面积(m²)逗号分隔')
    parser.add_argument('--storage', type=str, default='0/0,10/20,15/30,20/35,25/50,51/102',
                        help='储能候选 功率kW/能量kWh，逗号分隔')
    args = parser.parse_args()

    with open(args.input) as f:
        base = json.load(f)

    if args.fuel is not None:
        base['market_data']['fuel_cost_per_kwh'] = args.fuel

    areas = [int(x) for x in args.areas.split(',')]
    storage_opts = []
    for s in args.storage.split(','):
        parts = s.strip().split('/')
        if len(parts) == 2:
            storage_opts.append((float(parts[0]), float(parts[1])))

    results = []
    total = len(areas) * len(storage_opts)
    count = 0

    print(f'扫描 {len(areas)} 个PV面积 × {len(storage_opts)} 个储能 = {total} 组合')
    print(f'燃料成本: ${args.fuel or base.get("market_data",{}).get("fuel_cost_per_kwh",0):.2f}/kWh')
    print('=' * 120)

    for area in areas:
        for pwr, ene in storage_opts:
            count += 1
            data = json.loads(json.dumps(base))  # deep copy
            data['resource_data']['solar']['available_area_m2'] = area
            if pwr <= 0 or ene <= 0:
                data['equipment']['storage']['power_candidate_kw'] = []
                data['equipment']['storage']['energy_candidate_kwh'] = []
            else:
                data['equipment']['storage']['power_candidate_kw'] = [pwr]
                data['equipment']['storage']['energy_candidate_kwh'] = [ene]

            try:
                r = run_config(data)
                results.append(r)
                pv = r['pv_mwp']
                st = f"{r['storage_mw']:.0f}/{r['storage_mwh']:.0f}"
                print(f'  [{count:>3}/{total}] PV {pv:>5.1f}MWp  储 {st:>7}  '
                      f'覆盖{r["coverage_pct"]:>4.1f}%  循环{r["cycles"]:>4.0f}  '
                      f'IRR {r["irr"]*100 if r["irr"] else 0:>5.1f}%  '
                      f'NPV {r["npv"]/1e8 if r["npv"] else 0:>5.1f}亿')
            except Exception as e:
                print(f'  [{count:>3}/{total}] PV {area/6600:.1f}MWp 储 {pwr:.0f}/{ene:.0f} ❌ {e}')

    # 排序
    target_key = 'irr' if args.target == 'irr' else 'npv'
    results.sort(key=lambda x: (x.get(target_key) or 0), reverse=True)

    print()
    print('=' * 120)
    print(f'🏆 按{args.target.upper()}排序 TOP 5:')
    print('-' * 120)
    print(f'{"排名":>4} | {"方案":>35} | {"覆盖":>6} | {"循环":>5} | {"IRR":>6} | {"NPV":>12}')
    print('-' * 120)
    for i, r in enumerate(results[:5]):
        st = f"{r['pv_mwp']:.1f}MWp+{r['storage_mw']:.0f}/{r['storage_mwh']:.0f}MWh"
        irr_str = f"{r['irr']*100:.2f}%" if r['irr'] else 'N/A'
        npv_str = f"{r['npv']/1e8:.2f}亿" if r['npv'] else 'N/A'
        print(f'{i+1:>4} | {st:>35} | {r["coverage_pct"]:>5.1f}% | {r["cycles"]:>5.0f} | {irr_str:>6} | {npv_str:>10}')

    # 输出最优方案JSON
    best = results[0]
    out_path = f'{args.input.replace(".json", "")}_optimal.json'
    with open(out_path, 'w') as f:
        json.dump(best, f, indent=2, ensure_ascii=False)
    print(f'\n最优方案已保存: {out_path}')

if __name__ == '__main__':
    main()
