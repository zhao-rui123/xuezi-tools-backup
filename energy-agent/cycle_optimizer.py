#!/usr/bin/env python3
"""
储能充放电循环优化器
核心：给定电价序列，找出收益最大的不重叠循环组合
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class CycleOptimizer:
    """循环优化器"""
    
    def __init__(self):
        self.hourly_prices = []  # [(datetime, price), ...]
    
    def load_excel(self, filepath):
        """加载Excel格式电价数据"""
        print(f"📂 加载: {filepath}")
        df = pd.read_excel(filepath, header=None)
        
        # 收集所有小时级别的电价（跨多天）
        all_prices = []
        
        col_idx = 1
        while col_idx < df.shape[1]:
            date_val = df.iloc[2, col_idx]
            if pd.notna(date_val) and '日前' not in str(date_val):
                try:
                    date = pd.to_datetime(date_val)
                    # 实时电价列
                    real_prices = pd.to_numeric(df.iloc[3:, col_idx+1].values, errors='coerce')
                    
                    for hour_idx, price in enumerate(real_prices):
                        if not np.isnan(price):
                            dt = date + timedelta(hours=hour_idx)
                            all_prices.append((dt, price))
                except:
                    pass
                col_idx += 2
            else:
                col_idx += 1
        
        # 按时间排序
        all_prices.sort(key=lambda x: x[0])
        self.hourly_prices = all_prices
        
        print(f"✅ 加载了 {len(self.hourly_prices)} 个小时数据")
        print(f"   时间范围: {self.hourly_prices[0][0]} ~ {self.hourly_prices[-1][0]}")
        return self
    
    def find_all_cycles(self, min_spread=50):
        """
        找出所有可能的充放电循环
        规则：
        - 充电在低价区间（连续几小时均价低）
        - 放电在高价位
        - 充电时长通常2-6小时
        - 放电时长通常2-6小时
        - 允许跨天：今天充，明天放
        """
        if not self.hourly_prices:
            return []
        
        prices = [p for _, p in self.hourly_prices]
        times = [t for t, _ in self.hourly_prices]
        n = len(prices)
        
        all_cycles = []
        
        # 滑动窗口：尝试不同的充电时长和放电时长
        for charge_len in [2, 3, 4, 5, 6]:  # 充电时长2-6小时
            for discharge_len in [2, 3, 4, 5, 6]:  # 放电时长2-6小时
                # 遍历每个可能的起始点
                for start_idx in range(n - charge_len - discharge_len):
                    # 充电时段
                    charge_prices = prices[start_idx:start_idx + charge_len]
                    charge_start = times[start_idx]
                    charge_end = times[start_idx + charge_len - 1]
                    avg_charge = np.mean(charge_prices)
                    
                    # 放电时段（紧接充电之后）
                    discharge_start_idx = start_idx + charge_len
                    discharge_end_idx = discharge_start_idx + discharge_len
                    if discharge_end_idx > n:
                        continue
                    
                    discharge_prices = prices[discharge_start_idx:discharge_end_idx]
                    discharge_start = times[discharge_start_idx]
                    discharge_end = times[discharge_end_idx - 1]
                    avg_discharge = np.mean(discharge_prices)
                    
                    spread = avg_discharge - avg_charge
                    
                    # 只保留有正收益且价差足够的
                    if spread >= min_spread:
                        all_cycles.append({
                            'charge_start': charge_start,
                            'charge_end': charge_end,
                            'charge_len': charge_len,
                            'charge_price': avg_charge,
                            'discharge_start': discharge_start,
                            'discharge_end': discharge_end,
                            'discharge_len': discharge_len,
                            'discharge_price': avg_discharge,
                            'spread': spread,
                            'profit_per_mwh': spread
                        })
        
        print(f"   找到 {len(all_cycles)} 个候选循环（价差≥{min_spread}）")
        return all_cycles
    
    def select_non_overlapping_cycles(self, cycles):
        """
        选择不重叠的最优循环组合
        使用贪心算法：按结束时间排序，依次选择不重叠的
        """
        if not cycles:
            return []
        
        # 按放电结束时间排序
        sorted_cycles = sorted(cycles, key=lambda x: x['discharge_end'])
        
        selected = []
        current_end = datetime(1970, 1, 1)  # 上一个选中循环的结束时间
        
        for cycle in sorted_cycles:
            # 检查是否与当前选中的循环重叠
            if cycle['charge_start'] > current_end:
                selected.append(cycle)
                current_end = cycle['discharge_end']
        
        return selected
    
    def optimize(self, min_spread=100):
        """
        主优化流程
        """
        # 1. 找所有候选循环
        all_cycles = self.find_all_cycles(min_spread=min_spread)
        
        # 2. 选择不重叠的最优组合
        selected = self.select_non_overlapping_cycles(all_cycles)
        
        # 3. 按收益排序
        selected.sort(key=lambda x: x['spread'], reverse=True)
        
        return selected
    
    def print_report(self, cycles):
        """打印报告"""
        if not cycles:
            print("\n❌ 没有找到值得做的循环")
            return
        
        print("\n" + "=" * 80)
        print("⚡ 最优充放电循环方案")
        print("=" * 80)
        
        total_profit = 0
        for i, c in enumerate(cycles, 1):
            print(f"\n🔄 循环 {i}:")
            print(f"   充电: {c['charge_start'].strftime('%m-%d %H:%M')} ~ {c['charge_end'].strftime('%H:%M')} ({c['charge_len']}小时)")
            print(f"         均价: {c['charge_price']:.2f} 元/MWh")
            print(f"   放电: {c['discharge_start'].strftime('%m-%d %H:%M')} ~ {c['discharge_end'].strftime('%H:%M')} ({c['discharge_len']}小时)")
            print(f"         均价: {c['discharge_price']:.2f} 元/MWh")
            print(f"   💰 价差: {c['spread']:.2f} 元/MWh")
            total_profit += c['spread']
        
        print("\n" + "-" * 80)
        print(f"📊 汇总:")
        print(f"   总循环数: {len(cycles)} 个")
        print(f"   总价差: {total_profit:.2f} 元/MWh")
        print(f"   假设100MWh容量：总收益 {total_profit/1000*100:.2f} 万元")
        
        # 按天统计
        print(f"\n📅 涉及天数:")
        all_days = set()
        for c in cycles:
            day = c['charge_start'].date()
            all_days.add(day)
        print(f"   {len(all_days)} 天")
    
    def export_json(self, cycles, output_path):
        """导出JSON"""
        data = {
            'version': '1.0',
            'generated_at': datetime.now().isoformat(),
            'total_cycles': len(cycles),
            'total_spread': sum(c['spread'] for c in cycles),
            'cycles': []
        }
        
        for c in cycles:
            data['cycles'].append({
                'charge_start': c['charge_start'].isoformat(),
                'charge_end': c['charge_end'].isoformat(),
                'charge_len': c['charge_len'],
                'charge_price': round(c['charge_price'], 2),
                'discharge_start': c['discharge_start'].isoformat(),
                'discharge_end': c['discharge_end'].isoformat(),
                'discharge_len': c['discharge_len'],
                'discharge_price': round(c['discharge_price'], 2),
                'spread': round(c['spread'], 2)
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return output_path


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python3 cycle_optimizer.py <电价Excel文件> [最小价差]")
        sys.exit(1)
    
    filepath = sys.argv[1]
    min_spread = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    
    optimizer = CycleOptimizer()
    optimizer.load_excel(filepath)
    
    # 优化
    cycles = optimizer.optimize(min_spread=min_spread)
    
    # 报告
    optimizer.print_report(cycles)
    
    # 导出
    json_path = filepath.replace('.xlsx', '_cycles.json')
    optimizer.export_json(cycles, json_path)
    print(f"\n📄 已导出: {json_path}")


if __name__ == '__main__':
    main()
