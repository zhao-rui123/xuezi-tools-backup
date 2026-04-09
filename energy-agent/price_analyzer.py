#!/usr/bin/env python3
"""
储能电价智能分析引擎
输入: 电价数据(Excel/CSV)
输出: 最优充放电策略
"""
import pandas as pd
import numpy as np
from datetime import datetime, time
import json
import sys

class ElectricityPriceAnalyzer:
    """电价智能分析器"""
    
    def __init__(self):
        self.data = None
        self.price_by_date = {}
        self.strategy = {}
    
    def load_excel(self, filepath):
        """加载Excel格式电价数据"""
        print(f"📂 加载数据: {filepath}")
        df = pd.read_excel(filepath, header=None)
        
        # 提取时段标签
        periods = df.iloc[3:, 0].values  # "00:00-01:00"格式
        
        # 按列解析每天的数据
        col_idx = 1
        while col_idx < df.shape[1]:
            date_val = df.iloc[2, col_idx]  # 第三行是日期
            if pd.notna(date_val) and '日前' not in str(date_val):
                try:
                    date = pd.to_datetime(date_val).date()
                    # 日前电价和实时电价
                    ahead = pd.to_numeric(df.iloc[3:, col_idx].values, errors='coerce')
                    real = pd.to_numeric(df.iloc[3:, col_idx+1].values, errors='coerce')
                    
                    self.price_by_date[date] = {
                        'period': periods,
                        'ahead': ahead,
                        'real': real
                    }
                except:
                    pass
                col_idx += 2
            else:
                col_idx += 1
        
        print(f"✅ 加载了 {len(self.price_by_date)} 天数据")
        return self
    
    def find_valleys(self, prices, periods, top_n=4):
        """找低价时段（充电时机）"""
        valid_idx = ~np.isnan(prices)
        if valid_idx.sum() == 0:
            return []
        
        prices_valid = prices[valid_idx]
        periods_valid = periods[valid_idx]
        
        # 排序找最低的N个
        sorted_idx = np.argsort(prices_valid)[:top_n]
        valleys = []
        for idx in sorted_idx:
            valleys.append({
                'hour': periods_valid[idx],
                'price': float(prices_valid[idx]),
                'index': int(np.where(valid_idx)[0][idx])
            })
        return sorted(valleys, key=lambda x: x['index'])
    
    def find_peaks(self, prices, periods, top_n=4):
        """找高价时段（放电时机）"""
        valid_idx = ~np.isnan(prices)
        if valid_idx.sum() == 0:
            return []
        
        prices_valid = prices[valid_idx]
        periods_valid = periods[valid_idx]
        
        # 排序找最高的N个
        sorted_idx = np.argsort(prices_valid)[-top_n:][::-1]
        peaks = []
        for idx in sorted_idx:
            peaks.append({
                'hour': periods_valid[idx],
                'price': float(prices_valid[idx]),
                'index': int(np.where(valid_idx)[0][idx])
            })
        return sorted(peaks, key=lambda x: x['index'])
    
    def match_cycles(self, valleys, peaks, min_spread=0):
        """
        智能匹配充放电周期
        原则：低价充电 → 高价放电 → 配对
        """
        cycles = []
        used_valleys = set()
        used_peaks = set()
        
        # 先按时间顺序处理每个峰值
        for peak in peaks:
            if peak['index'] in used_peaks:
                continue
            
            # 找这个峰值之前的最近低价
            candidates = [v for v in valleys 
                         if v['index'] < peak['index'] 
                         and v['index'] not in used_valleys]
            
            if candidates:
                valley = candidates[-1]  # 最近的那个
                spread = peak['price'] - valley['price']
                
                if spread >= min_spread:
                    cycles.append({
                        'charge': valley,
                        'discharge': peak,
                        'spread': spread,
                        'profit_per_mwh': spread  # 元/MWh
                    })
                    used_valleys.add(valley['index'])
                    used_peaks.add(peak['index'])
        
        return cycles
    
    def analyze_day(self, date, use_realtime=True):
        """分析单天的最优策略"""
        day_data = self.price_by_date.get(date)
        if not day_data:
            return None
        
        prices = day_data['real'] if use_realtime else day_data['ahead']
        periods = day_data['period']
        
        # 找峰谷
        valleys = self.find_valleys(prices, periods)
        peaks = self.find_peaks(prices, periods)
        
        # 匹配周期
        cycles = self.match_cycles(valleys, peaks, min_spread=100)
        
        return {
            'date': str(date),
            'valleys': valleys,
            'peaks': peaks,
            'cycles': cycles,
            'total_spread': sum(c['spread'] for c in cycles),
            'num_cycles': len(cycles)
        }
    
    def analyze_all(self, use_realtime=True):
        """分析所有天"""
        results = []
        for date in sorted(self.price_by_date.keys()):
            day_result = self.analyze_day(date, use_realtime)
            if day_result and day_result['num_cycles'] > 0:
                results.append(day_result)
        return results
    
    def generate_report(self, results, capacity_mwh=100):
        """生成分析报告"""
        if not results:
            return "没有找到有效的充放电策略"
        
        report = []
        report.append("=" * 70)
        report.append("⚡ 储能充放电智能分析报告")
        report.append("=" * 70)
        report.append(f"\n📊 数据概览")
        report.append(f"   分析天数: {len(results)} 天")
        report.append(f"   储能容量: {capacity_mwh} MWh")
        report.append(f"   数据类型: 实时电价")
        
        # 统计
        total_cycles = sum(r['num_cycles'] for r in results)
        total_spread = sum(r['total_spread'] for r in results)
        avg_spread = total_spread / total_cycles if total_cycles > 0 else 0
        
        report.append(f"\n💰 收益统计")
        report.append(f"   总充放电次数: {total_cycles} 次")
        report.append(f"   日均次数: {total_cycles/len(results):.1f} 次")
        report.append(f"   平均价差: {avg_spread:.2f} 元/MWh")
        report.append(f"   预估月收益: {total_spread/len(results)*30/1000*capacity_mwh:.2f} 万元")
        
        # 充电时段分析
        all_charge_hours = []
        for r in results:
            for c in r['cycles']:
                all_charge_hours.append(c['charge']['hour'])
        
        report.append(f"\n📗 充电时段推荐 (Top 5)")
        hour_counts = pd.Series(all_charge_hours).value_counts().head(5)
        for hour, count in hour_counts.items():
            report.append(f"   {hour}: 出现 {count} 次 ({count/len(results)*100:.0f}%)")
        
        # 放电时段分析
        all_discharge_hours = []
        for r in results:
            for c in r['cycles']:
                all_discharge_hours.append(c['discharge']['hour'])
        
        report.append(f"\n📕 放电时段推荐 (Top 5)")
        hour_counts = pd.Series(all_discharge_hours).value_counts().head(5)
        for hour, count in hour_counts.items():
            report.append(f"   {hour}: 出现 {count} 次 ({count/len(results)*100:.0f}%)")
        
        # 收集所有充放电价格
        charge_prices = []
        discharge_prices = []
        for r in results:
            for c in r['cycles']:
                charge_prices.append(c['charge']['price'])
                discharge_prices.append(c['discharge']['price'])
        
        avg_charge = int(np.mean(charge_prices)) if charge_prices else 0
        avg_discharge = int(np.mean(discharge_prices)) if discharge_prices else 0
        
        report.append(f"\n🎯 智能策略规则")
        report.append(f"   1. 充电条件: 电价低于 {avg_charge} 元/MWh 时考虑充电")
        report.append(f"   2. 放电条件: 电价高于 {avg_discharge} 元/MWh 时考虑放电")
        report.append(f"   3. 最低价差阈值: 建议 ≥150 元/MWh")
        
        return "\n".join(report)
    
    def export_strategy_json(self, results, output_path):
        """导出策略JSON供Agent使用"""
        strategy = {
            'version': '1.0',
            'generated_at': datetime.now().isoformat(),
            'data_summary': {
                'days_analyzed': len(results),
                'total_cycles': sum(r['num_cycles'] for r in results)
            },
            'rules': {
                'charge_condition': 'price_below_threshold',
                'discharge_condition': 'price_above_threshold',
                'min_spread_threshold': 150
            },
            'daily_strategies': []
        }
        
        for r in results:
            for c in r['cycles']:
                strategy['daily_strategies'].append({
                    'date': r['date'],
                    'charge_time': c['charge']['hour'],
                    'charge_price': c['charge']['price'],
                    'discharge_time': c['discharge']['hour'],
                    'discharge_price': c['discharge']['price'],
                    'spread': c['spread']
                })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(strategy, f, ensure_ascii=False, indent=2)
        
        return output_path


def main():
    if len(sys.argv) < 2:
        print("用法: python3 price_analyzer.py <电价Excel文件>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    analyzer = ElectricityPriceAnalyzer()
    analyzer.load_excel(filepath)
    
    # 分析（使用实时电价）
    results = analyzer.analyze_all(use_realtime=True)
    
    # 生成报告
    report = analyzer.generate_report(results)
    print(report)
    
    # 导出策略JSON
    json_path = filepath.replace('.xlsx', '_strategy.json')
    analyzer.export_strategy_json(results, json_path)
    print(f"\n📄 策略已导出: {json_path}")


if __name__ == '__main__':
    main()
