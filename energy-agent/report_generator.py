#!/usr/bin/env python3
"""
储能电价分析报告生成器
"""
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class ReportGenerator:
    """报告生成器"""

    def __init__(self, cycles: List[Dict] = None, capacity_mwh: float = 100):
        self.cycles = cycles or []
        self.capacity_mwh = capacity_mwh
        self.generated_at = datetime.now()

    def set_cycles(self, cycles: List[Dict]) -> "ReportGenerator":
        """设置循环数据"""
        self.cycles = cycles
        return self

    def generate_summary(self) -> str:
        """生成汇总报告（文本）"""
        if not self.cycles:
            return "❌ 没有可用的循环数据"

        lines = []
        lines.append("=" * 80)
        lines.append("⚡ 储能充放电优化报告")
        lines.append("=" * 80)
        lines.append(f"生成时间: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"储能容量: {self.capacity_mwh} MWh")
        lines.append("")

        # 基本统计
        total_cycles = len(self.cycles)
        total_spread = sum(c["spread"] for c in self.cycles)
        total_profit = total_spread / 1000 * self.capacity_mwh

        charge_prices = [c["charge_price"] for c in self.cycles]
        discharge_prices = [c["discharge_price"] for c in self.cycles]
        charge_lens = [c["charge_len"] for c in self.cycles]
        discharge_lens = [c["discharge_len"] for c in self.cycles]

        lines.append("📊 基本统计")
        lines.append("-" * 40)
        lines.append(f"  总循环数:     {total_cycles} 个")
        lines.append(f"  总价差:     {total_spread:.2f} 元/MWh")
        lines.append(f"  预估总收益:   {total_profit:.2f} 万元")
        lines.append(f"  平均价差:   {total_spread/total_cycles:.2f} 元/MWh")
        lines.append(f"  平均充电时长: {np.mean(charge_lens):.1f} 小时")
        lines.append(f"  平均放电时长: {np.mean(discharge_lens):.1f} 小时")
        lines.append("")

        # 涉及天数
        all_days = set()
        for c in self.cycles:
            all_days.add(c["charge_start"].date())
        lines.append(f"📅 涉及天数: {len(all_days)} 天")
        lines.append("")

        # 收益分层
        spreads = [c["spread"] for c in self.cycles]
        lines.append("💰 收益分层")
        lines.append("-" * 40)
        bins = [0, 100, 150, 200, 300, float("inf")]
        labels = ["<100", "100-150", "150-200", "200-300", ">300"]
        hist, _ = np.histogram(spreads, bins=bins)
        for label, count in zip(labels, hist):
            lines.append(f"  {label:>8} 元/MWh: {count:>3} 个循环")
        lines.append("")

        # 充电均价分布
        avg_charge = np.mean(charge_prices)
        lines.append("📗 充电均价统计")
        lines.append("-" * 40)
        lines.append(f"  最低充电价: {min(charge_prices):.2f} 元/MWh")
        lines.append(f"  最高充电价: {max(charge_prices):.2f} 元/MWh")
        lines.append(f"  平均充电价: {avg_charge:.2f} 元/MWh")
        lines.append("")

        # 放电均价分布
        avg_discharge = np.mean(discharge_prices)
        lines.append("📕 放电均价统计")
        lines.append("-" * 40)
        lines.append(f"  最低放电价: {min(discharge_prices):.2f} 元/MWh")
        lines.append(f"  最高放电价: {max(discharge_prices):.2f} 元/MWh")
        lines.append(f"  平均放电价: {avg_discharge:.2f} 元/MWh")
        lines.append("")

        # 智能策略建议
        lines.append("🎯 智能策略建议")
        lines.append("-" * 40)
        lines.append(f"  充电阈值: 电价低于 {avg_charge:.0f} 元/MWh 时考虑充电")
        lines.append(f"  放电阈值: 电价高于 {avg_discharge:.0f} 元/MWh 时考虑放电")
        lines.append(f"  最低价差阈值: 建议 ≥150 元/MWh")
        lines.append("")

        # 按时段统计
        charge_hour_counts = {}
        discharge_hour_counts = {}
        for c in self.cycles:
            hour = c["charge_start"].hour
            charge_hour_counts[hour] = charge_hour_counts.get(hour, 0) + 1
            d_hour = c["discharge_start"].hour
            discharge_hour_counts[d_hour] = discharge_hour_counts.get(d_hour, 0) + 1

        lines.append("🕐 充电高峰时段 (Top 5)")
        top_charge = sorted(charge_hour_counts.items(), key=lambda x: -x[1])[:5]
        for hour, count in top_charge:
            lines.append(f"  {hour:02d}:00 - {hour+1:02d}:00  {count} 次")
        lines.append("")

        lines.append("🕐 放电高峰时段 (Top 5)")
        top_discharge = sorted(discharge_hour_counts.items(), key=lambda x: -x[1])[:5]
        for hour, count in top_discharge:
            lines.append(f"  {hour:02d}:00 - {hour+1:02d}:00  {count} 次")
        lines.append("")

        lines.append("=" * 80)
        return "\n".join(lines)

    def generate_json(self, output_path: str) -> str:
        """生成JSON格式报告"""
        data = {
            "version": "1.0",
            "generated_at": self.generated_at.isoformat(),
            "capacity_mwh": self.capacity_mwh,
            "summary": {
                "total_cycles": len(self.cycles),
                "total_spread": round(sum(c["spread"] for c in self.cycles), 2),
                "total_profit_wan": round(
                    sum(c["spread"] for c in self.cycles)
                    / 1000
                    * self.capacity_mwh,
                    2,
                ),
                "avg_spread": round(
                    np.mean([c["spread"] for c in self.cycles]), 2
                ),
                "days_involved": len(
                    set(c["charge_start"].date() for c in self.cycles)
                ),
            },
            "price_stats": {
                "charge": {
                    "min": round(min(c["charge_price"] for c in self.cycles), 2),
                    "max": round(max(c["charge_price"] for c in self.cycles), 2),
                    "avg": round(np.mean([c["charge_price"] for c in self.cycles]), 2),
                },
                "discharge": {
                    "min": round(min(c["discharge_price"] for c in self.cycles), 2),
                    "max": round(max(c["discharge_price"] for c in self.cycles), 2),
                    "avg": round(
                        np.mean([c["discharge_price"] for c in self.cycles]), 2
                    ),
                },
            },
            "cycles": [
                {
                    "charge_start": c["charge_start"].isoformat(),
                    "charge_end": c["charge_end"].isoformat(),
                    "charge_len": c["charge_len"],
                    "charge_price": round(c["charge_price"], 2),
                    "discharge_start": c["discharge_start"].isoformat(),
                    "discharge_end": c["discharge_end"].isoformat(),
                    "discharge_len": c["discharge_len"],
                    "discharge_price": round(c["discharge_price"], 2),
                    "spread": round(c["spread"], 2),
                }
                for c in self.cycles
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return output_path

    def generate_csv(self, output_path: str) -> str:
        """生成CSV格式循环明细"""
        rows = []
        for i, c in enumerate(self.cycles, 1):
            rows.append({
                "序号": i,
                "充电开始": c["charge_start"].strftime("%Y-%m-%d %H:%M"),
                "充电结束": c["charge_end"].strftime("%Y-%m-%d %H:%M"),
                "充电时长(h)": c["charge_len"],
                "充电均价(元/MWh)": round(c["charge_price"], 2),
                "放电开始": c["discharge_start"].strftime("%Y-%m-%d %H:%M"),
                "放电结束": c["discharge_end"].strftime("%Y-%m-%d %H:%M"),
                "放电时长(h)": c["discharge_len"],
                "放电均价(元/MWh)": round(c["discharge_price"], 2),
                "价差(元/MWh)": round(c["spread"], 2),
            })

        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        return output_path

    def generate_html(self, output_path: str) -> str:
        """生成HTML可视化报告"""
        if not self.cycles:
            return ""

        total_spread = sum(c["spread"] for c in self.cycles)
        total_profit = total_spread / 1000 * self.capacity_mwh
        avg_charge = np.mean([c["charge_price"] for c in self.cycles])
        avg_discharge = np.mean([c["discharge_price"] for c in self.cycles])

        # 按时段统计
        hour_data = {}
        for c in self.cycles:
            hour = c["charge_start"].hour
            if hour not in hour_data:
                hour_data[hour] = {"charge": 0, "discharge": 0, "count": 0}
            hour_data[hour]["charge"] += c["charge_price"] * c["charge_len"]
            hour_data[hour]["count"] += c["charge_len"]

        bars = ""
        for h in range(24):
            count = hour_data.get(h, {}).get("count", 0)
            bar_len = int(count / max(len(self.cycles) * 4, 1) * 50)
            bars += f"<div style='margin:2px 0'><b>{h:02d}:00</b> {'█' * bar_len} <span style='color:#888'>{count}h</span></div>\n"

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>储能充放电优化报告</title>
<style>
body{{font-family:Arial,sans-serif;margin:40px;background:#f5f5f5}}
.container{{max-width:900px;margin:0 auto;background:#fff;padding:30px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.1)}}
h1{{color:#1a73e8;border-bottom:2px solid #1a73e8;padding-bottom:10px}}
.stat-grid{{display:grid;grid-template-columns:1fr 1fr;gap:15px;margin:20px 0}}
.stat-box{{background:#f8f9fa;padding:15px;border-radius:6px;border-left:4px solid #1a73e8}}
.stat-box h3{{margin:0 0 8px;color:#333}}
.stat-box .num{{font-size:2em;font-weight:bold;color:#1a73e8}}
table{{width:100%;border-collapse:collapse;margin:20px 0}}
th{{background:#1a73e8;color:#fff;padding:10px;text-align:left}}
td{{padding:8px;border-bottom:1px solid #eee}}
tr:hover{{background:#f5f5f5}}
.cycle-positive{{color:#34a853}}
.bars{{font-family:monospace;background:#f8f9fa;padding:15px;border-radius:6px}}
</style>
</head>
<body>
<div class="container">
<h1>⚡ 储能充放电优化报告</h1>
<p>生成时间: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')} | 容量: {self.capacity_mwh} MWh</p>

<div class="stat-grid">
  <div class="stat-box"><h3>总循环数</h3><div class="num">{len(self.cycles)}</div></div>
  <div class="stat-box"><h3>总价差</h3><div class="num">{total_spread:.1f}</div><small> 元/MWh</small></div>
  <div class="stat-box"><h3>预估总收益</h3><div class="num" style="color:#34a853">{total_profit:.2f}</div><small> 万元</small></div>
  <div class="stat-box"><h3>平均价差</h3><div class="num">{total_spread/len(self.cycles):.1f}</div><small> 元/MWh</small></div>
</div>

<h2>📗 充电策略</h2>
<p>充电阈值: 电价低于 <b>{avg_charge:.0f} 元/MWh</b> 时考虑充电</p>

<h2>📕 放电策略</h2>
<p>放电阈值: 电价高于 <b>{avg_discharge:.0f} 元/MWh</b> 时考虑放电</p>

<h2>🕐 24小时时段分布</h2>
<div class="bars">{bars}</div>

<h2>📋 循环明细</h2>
<table>
<tr><th>#</th><th>充电时段</th><th>充电价</th><th>放电时段</th><th>放电价</th><th>价差</th></tr>
"""

        for i, c in enumerate(self.cycles[:50], 1):
            html += f"""<tr>
<td>{i}</td>
<td>{c['charge_start'].strftime('%m-%d %H:%M')}~{c['charge_end'].strftime('%H:%M')}</td>
<td>{c['charge_price']:.1f}</td>
<td>{c['discharge_start'].strftime('%m-%d %H:%M')}~{c['discharge_end'].strftime('%H:%M')}</td>
<td>{c['discharge_price']:.1f}</td>
<td class='cycle-positive'>{c['spread']:.1f}</td>
</tr>
"""

        html += """</table>
</div>
</body>
</html>"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        return output_path


def main():
    import sys, os

    if len(sys.argv) < 2:
        print("用法: python3 report_generator.py <cycles.json> [capacity_mwh]")
        sys.exit(1)

    json_path = sys.argv[1]
    capacity = float(sys.argv[2]) if len(sys.argv) > 2 else 100

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    cycles = []
    for c in data.get("cycles", []):
        cycles.append(
            {
                "charge_start": pd.to_datetime(c["charge_start"]),
                "charge_end": pd.to_datetime(c["charge_end"]),
                "charge_len": c["charge_len"],
                "charge_price": c["charge_price"],
                "discharge_start": pd.to_datetime(c["discharge_start"]),
                "discharge_end": pd.to_datetime(c["discharge_end"]),
                "discharge_len": c["discharge_len"],
                "discharge_price": c["discharge_price"],
                "spread": c["spread"],
            }
        )

    gen = ReportGenerator(cycles, capacity)
    print(gen.generate_summary())

    base = json_path.replace(".json", "")
    gen.generate_json(base + "_report.json")
    gen.generate_csv(base + "_report.csv")
    gen.generate_html(base + "_report.html")
    print(f"\n📄 报告已导出（json/csv/html）")


if __name__ == "__main__":
    main()
