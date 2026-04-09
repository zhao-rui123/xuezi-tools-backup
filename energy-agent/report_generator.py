#!/usr/bin/env python3
"""
储能电价分析报告生成器
输入：CycleOptimizerResult列表 或 PriceLoader数据
输出：格式化报告（控制台/Markdown/JSON）
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import json

@dataclass
class CycleOptimizerResult:
    charge_start: datetime
    charge_end: datetime
    charge_len: int
    charge_price: float
    discharge_start: datetime
    discharge_end: datetime
    discharge_len: int
    discharge_price: float
    spread: float
    profit_per_mwh: float

class ReportGenerator:
    """报告生成器"""

    def __init__(self, capacity_mwh: float = 100.0):
        self.capacity_mwh = capacity_mwh

    def generate_text(self, cycles: List[CycleOptimizerResult]) -> str:
        """生成文本格式报告"""
        if not cycles:
            return "❌ 没有找到值得做的循环"

        lines = []
        lines.append("\n" + "=" * 80)
        lines.append("⚡ 最优充放电循环方案")
        lines.append("=" * 80)

        total_profit = 0.0
        for i, c in enumerate(cycles, 1):
            lines.append(f"\n🔄 循环 {i}:")
            lines.append(f"   充电: {c.charge_start.strftime('%m-%d %H:%M')} ~ {c.charge_end.strftime('%H:%M')} ({c.charge_len}小时)")
            lines.append(f"         均价: {c.charge_price:.2f} 元/MWh")
            lines.append(f"   放电: {c.discharge_start.strftime('%m-%d %H:%M')} ~ {c.discharge_end.strftime('%H:%M')} ({c.discharge_len}小时)")
            lines.append(f"         均价: {c.discharge_price:.2f} 元/MWh")
            lines.append(f"   💰 价差: {c.spread:.2f} 元/MWh")
            total_profit += c.spread

        lines.append("\n" + "-" * 80)
        lines.append(f"📊 汇总:")
        lines.append(f"   总循环数: {len(cycles)} 个")
        lines.append(f"   总价差: {total_profit:.2f} 元/MWh")
        lines.append(f"   假设{self.capacity_mwh}MWh容量：总收益 {total_profit/1000*self.capacity_mwh:.2f} 万元")

        # 按天统计
        all_days = set()
        for c in cycles:
            all_days.add(c.charge_start.date())
        lines.append(f"\n📅 涉及天数: {len(all_days)} 天")

        return "\n".join(lines)

    def generate_summary(self, cycles: List[CycleOptimizerResult]) -> dict:
        """生成汇总数据字典"""
        if not cycles:
            return {"total_cycles": 0, "total_spread": 0, "revenue_wan": 0}

        total_spread = sum(c.spread for c in cycles)
        all_days = set(c.charge_start.date() for c in cycles)

        return {
            "total_cycles": len(cycles),
            "total_spread": round(total_spread, 2),
            "revenue_wan": round(total_spread / 1000 * self.capacity_mwh, 2),
            "days_involved": len(all_days),
            "avg_spread": round(total_spread / len(cycles), 2) if cycles else 0,
            "capacity_mwh": self.capacity_mwh
        }

    def export_json(self, cycles: List[CycleOptimizerResult], output_path: str) -> str:
        """导出JSON格式报告"""
        data = {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "capacity_mwh": self.capacity_mwh,
            "summary": self.generate_summary(cycles),
            "cycles": [
                {
                    "charge_start": c.charge_start.isoformat(),
                    "charge_end": c.charge_end.isoformat(),
                    "charge_len": c.charge_len,
                    "charge_price": round(c.charge_price, 2),
                    "discharge_start": c.discharge_start.isoformat(),
                    "discharge_end": c.discharge_end.isoformat(),
                    "discharge_len": c.discharge_len,
                    "discharge_price": round(c.discharge_price, 2),
                    "spread": round(c.spread, 2)
                }
                for c in cycles
            ]
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return output_path

    def export_markdown(self, cycles: List[CycleOptimizerResult], output_path: str) -> str:
        """导出Markdown格式报告"""
        lines = []
        lines.append("# ⚡ 储能充放电循环方案报告\n")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append(f"**储能容量**: {self.capacity_mwh} MWh\n")

        summary = self.generate_summary(cycles)
        lines.append(f"**总循环数**: {summary['total_cycles']}\n")
        lines.append(f"**总价差**: {summary['total_spread']} 元/MWh\n")
        lines.append(f"**预估收益**: {summary['revenue_wan']} 万元\n")

        lines.append("\n## 📋 循环明细\n")
        lines.append("| 序号 | 充电开始 | 充电结束 | 充电时长 | 充电均价 | 放电开始 | 放电结束 | 放电时长 | 放电均价 | 价差 |")
        lines.append("|------|----------|----------|----------|----------|----------|----------|----------|----------|------|")

        for i, c in enumerate(cycles, 1):
            lines.append(
                f"| {i} | {c.charge_start.strftime('%m-%d %H:%M')} | {c.charge_end.strftime('%H:%M')} | "
                f"{c.charge_len}h | {c.charge_price:.2f} | {c.discharge_start.strftime('%m-%d %H:%M')} | "
                f"{c.discharge_end.strftime('%H:%M')} | {c.discharge_len}h | {c.discharge_price:.2f} | {c.spread:.2f} |"
            )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return output_path


def main():
    """简单测试"""
    from datetime import datetime, timedelta

    # Mock数据测试
    cycles = [
        CycleOptimizerResult(
            charge_start=datetime(2026, 4, 1, 0, 0),
            charge_end=datetime(2026, 4, 1, 5, 0),
            charge_len=5,
            charge_price=200.0,
            discharge_start=datetime(2026, 4, 1, 6, 0),
            discharge_end=datetime(2026, 4, 1, 11, 0),
            discharge_len=5,
            discharge_price=450.0,
            spread=250.0,
            profit_per_mwh=250.0
        )
    ]

    gen = ReportGenerator(capacity_mwh=100)
    print(gen.generate_text(cycles))
    print("\n📊 汇总:", gen.generate_summary(cycles))


if __name__ == "__main__":
    main()
