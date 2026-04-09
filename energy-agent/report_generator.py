#!/usr/bin/env python3
"""
储能电价循环优化报告生成器
功能：根据优化结果生成文本/JSON/Markdown格式报告
"""
import json
from datetime import datetime
from typing import List, Dict, Any
from cycle_optimizer import CycleOptimizerResult


class ReportGenerator:
    """报告生成器"""

    def __init__(self, capacity_mwh: float = 100.0):
        """
        初始化报告生成器

        Args:
            capacity_mwh: 储能容量(MWh)，用于计算预估收益
        """
        self.capacity_mwh = capacity_mwh

    def generate_summary(self, cycles: List[CycleOptimizerResult]) -> Dict[str, Any]:
        """
        生成汇总数据

        Args:
            cycles: 循环列表

        Returns:
            包含 total_cycles, total_spread, revenue_wan 的字典
        """
        total_spread = sum(c.spread for c in cycles)
        # 价差单位是 元/MWh，除以1000转为 万元/MWh，再乘以容量
        revenue_wan = total_spread / 1000 * self.capacity_mwh

        return {
            'total_cycles': len(cycles),
            'total_spread': round(total_spread, 2),
            'revenue_wan': round(revenue_wan, 2),
            'capacity_mwh': self.capacity_mwh
        }

    def generate_text(self, cycles: List[CycleOptimizerResult]) -> str:
        """
        生成文本格式报告

        Args:
            cycles: 循环列表

        Returns:
            格式化的文本报告
        """
        if not cycles:
            return "\n❌ 没有找到值得做的循环\n"

        total_spread = sum(c.spread for c in cycles)
        revenue_wan = total_spread / 1000 * self.capacity_mwh

        lines = []
        lines.append("")
        lines.append("=" * 80)
        lines.append("⚡ 储能电价循环优化报告")
        lines.append("=" * 80)

        for i, c in enumerate(cycles, 1):
            lines.append(f"\n🔄 循环 {i}:")
            lines.append(f"   充电: {c.charge_start.strftime('%m-%d %H:%M')} ~ {c.charge_end.strftime('%H:%M')} ({c.charge_len}小时)")
            lines.append(f"         均价: {c.charge_price:.2f} 元/MWh")
            lines.append(f"   放电: {c.discharge_start.strftime('%m-%d %H:%M')} ~ {c.discharge_end.strftime('%H:%M')} ({c.discharge_len}小时)")
            lines.append(f"         均价: {c.discharge_price:.2f} 元/MWh")
            lines.append(f"   💰 价差: {c.spread:.2f} 元/MWh")

        lines.append("\n" + "-" * 80)
        lines.append("📊 汇总:")
        lines.append(f"   总循环数: {len(cycles)} 个")
        lines.append(f"   总价差: {total_spread:.2f} 元/MWh")
        lines.append(f"   预估收益({self.capacity_mwh}MWh): {revenue_wan:.2f} 万元")

        # 按天统计
        all_days = set()
        for c in cycles:
            day = c.charge_start.date()
            all_days.add(day)
        lines.append(f"\n📅 涉及天数: {len(all_days)} 天")

        return "\n".join(lines)

    def export_json(self, cycles: List[CycleOptimizerResult], output_path: str) -> str:
        """
        导出JSON格式报告

        Args:
            cycles: 循环列表
            output_path: 输出文件路径

        Returns:
            输出文件路径
        """
        summary = self.generate_summary(cycles)
        data = {
            'version': '1.0',
            'generated_at': datetime.now().isoformat(),
            'capacity_mwh': self.capacity_mwh,
            'summary': summary,
            'cycles': []
        }

        for c in cycles:
            data['cycles'].append({
                'charge_start': c.charge_start.isoformat(),
                'charge_end': c.charge_end.isoformat(),
                'charge_len': c.charge_len,
                'charge_price': round(c.charge_price, 2),
                'discharge_start': c.discharge_start.isoformat(),
                'discharge_end': c.discharge_end.isoformat(),
                'discharge_len': c.discharge_len,
                'discharge_price': round(c.discharge_price, 2),
                'spread': round(c.spread, 2)
            })

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return output_path

    def export_markdown(self, cycles: List[CycleOptimizerResult], output_path: str) -> str:
        """
        导出Markdown格式报告

        Args:
            cycles: 循环列表
            output_path: 输出文件路径

        Returns:
            输出文件路径
        """
        summary = self.generate_summary(cycles)
        total_spread = summary['total_spread']
        revenue_wan = summary['revenue_wan']

        lines = []
        lines.append("# ⚡ 储能电价循环优化报告")
        lines.append("")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**储能容量**: {self.capacity_mwh} MWh")
        lines.append("")

        lines.append("## 📊 汇总")
        lines.append("")
        lines.append(f"| 指标 | 数值 |")
        lines.append(f"|------|------|")
        lines.append(f"| 总循环数 | {len(cycles)} 个 |")
        lines.append(f"| 总价差 | {total_spread:.2f} 元/MWh |")
        lines.append(f"| 预估收益 | {revenue_wan:.2f} 万元 |")

        # 按天统计
        all_days = set()
        for c in cycles:
            all_days.add(c.charge_start.date())
        lines.append(f"| 涉及天数 | {len(all_days)} 天 |")

        if cycles:
            lines.append("")
            lines.append("## 🔄 循环详情")
            lines.append("")
            lines.append("| # | 充电时段 | 充电均价 | 放电时段 | 放电均价 | 价差 |")
            lines.append("|---|----------|----------|----------|----------|------|")

            for i, c in enumerate(cycles, 1):
                charge_period = f"{c.charge_start.strftime('%m-%d %H:%M')}~{c.charge_end.strftime('%H:%M')}"
                discharge_period = f"{c.discharge_start.strftime('%m-%d %H:%M')}~{c.discharge_end.strftime('%H:%M')}"
                lines.append(f"| {i} | {charge_period} | {c.charge_price:.2f} | {discharge_period} | {c.discharge_price:.2f} | {c.spread:.2f} |")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        return output_path


def main():
    """演示用法"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python3 report_generator.py <输出路径>")
        sys.exit(1)

    output_path = sys.argv[1]
    gen = ReportGenerator(capacity_mwh=100.0)

    # 生成空报告示例
    print(gen.generate_text([]))
    print("\n已生成报告:", output_path)


if __name__ == '__main__':
    main()
