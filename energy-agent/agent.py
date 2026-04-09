#!/usr/bin/env python3
"""
储能电价循环优化Agent主入口
功能：加载电价 → 找最优循环 → 生成报告
用法：
    python3 agent.py <电价Excel> [--min-spread N] [--capacity N] [--output path]
"""
import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from core.price_loader import PriceLoader
from cycle_optimizer import CycleOptimizer, CycleOptimizerResult
from report_generator import ReportGenerator


def main():
    parser = argparse.ArgumentParser(description="储能电价循环优化Agent")
    parser.add_argument("filepath", help="电价Excel文件路径")
    parser.add_argument("--min-spread", type=float, default=100.0, help="最小价差阈值(元/MWh)")
    parser.add_argument("--capacity", type=float, default=100.0, help="储能容量(MWh)")
    parser.add_argument("--output", "-o", type=str, default=None, help="输出文件路径(JSON/MD)")
    parser.add_argument("--format", choices=["text", "json", "markdown", "all"], default="text", help="输出格式")

    args = parser.parse_args()

    # 1. 加载电价数据
    print(f"📂 加载电价数据: {args.filepath}")
    optimizer = CycleOptimizer()
    optimizer.load_excel(args.filepath)

    # 2. 优化计算
    print(f"⚙️ 开始优化（最小价差≥{args.min_spread}）...")
    cycles = optimizer.optimize(min_spread=args.min_spread)

    # 3. 生成报告
    report_gen = ReportGenerator(capacity_mwh=args.capacity)

    if args.format == "text":
        print(report_gen.generate_text(cycles))
    elif args.format == "json":
        if args.output:
            path = report_gen.export_json(cycles, args.output)
            print(f"✅ JSON已导出: {path}")
        else:
            import json
            print(json.dumps(report_gen.generate_summary(cycles), ensure_ascii=False, indent=2))
    elif args.format == "markdown":
        if args.output:
            path = report_gen.export_markdown(cycles, args.output)
            print(f"✅ Markdown已导出: {path}")
        else:
            print("❌ markdown格式需要指定 --output")
    elif args.format == "all":
        if args.output:
            base = args.output.rsplit(".", 1)[0]
            report_gen.export_json(cycles, f"{base}.json")
            report_gen.export_markdown(cycles, f"{base}.md")
            print(report_gen.generate_text(cycles))
            print(f"\n✅ 已导出: {base}.json 和 {base}.md")
        else:
            print(report_gen.generate_text(cycles))
            print(f"\n📊 汇总: {report_gen.generate_summary(cycles)}")

    # 4. 汇总打印
    summary = report_gen.generate_summary(cycles)
    print(f"\n📊 优化结果:")
    print(f"   循环数: {summary['total_cycles']} 个")
    print(f"   总价差: {summary['total_spread']} 元/MWh")
    print(f"   预估收益({args.capacity}MWh): {summary['revenue_wan']} 万元")


if __name__ == "__main__":
    main()
