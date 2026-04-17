#!/usr/bin/env python3
"""
储能电价循环优化 Agent 主入口
Usage: python3 agent.py <电价Excel文件> [选项]
"""
import argparse
import sys
import os
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent))

from cycle_optimizer import CycleOptimizer
from report_generator import ReportGenerator


def parse_args():
    parser = argparse.ArgumentParser(
        description="储能电价循环优化 Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 agent.py data.xlsx                    # 基本分析
  python3 agent.py data.xlsx --min-spread 150  # 调整最小价差
  python3 agent.py data.xlsx --capacity 50     # 50MWh 储能
  python3 agent.py data.xlsx --output ./results  # 指定输出目录
        """,
    )
    parser.add_argument("filepath", nargs="?", help="电价Excel文件路径")
    parser.add_argument(
        "--min-spread", type=float, default=100, help="最小价差阈值（元/MWh），默认100"
    )
    parser.add_argument(
        "--capacity",
        type=float,
        default=100,
        help="储能容量（MWh），默认100MWh",
    )
    parser.add_argument(
        "--output", "-o", type=str, default=None, help="输出目录，默认与输入文件同目录"
    )
    parser.add_argument(
        "--no-report", action="store_true", help="跳过详细报告生成"
    )
    parser.add_argument(
        "--charge-lens",
        type=str,
        default="2,3,4,5,6",
        help="允许的充电时长列表（逗号分隔），默认2,3,4,5,6",
    )
    parser.add_argument(
        "--discharge-lens",
        type=str,
        default="2,3,4,5,6",
        help="允许的放电时长列表（逗号分隔），默认2,3,4,5,6",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="静默模式，只输出关键结果"
    )
    return parser.parse_args()


def resolve_output_dir(filepath: str, output_dir: str = None) -> Path:
    """解析输出目录"""
    if output_dir:
        p = Path(output_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p
    return Path(filepath).parent


def main():
    args = parse_args()

    if not args.filepath:
        print("❌ 请提供电价Excel文件路径")
        print("   用法: python3 agent.py <电价Excel文件> [选项]")
        sys.exit(1)

    filepath = Path(args.filepath)
    if not filepath.exists():
        print(f"❌ 文件不存在: {filepath}")
        sys.exit(1)

    out_dir = resolve_output_dir(args.filepath, args.output)

    # 解析充放电时长参数
    charge_lens = [int(x) for x in args.charge_lens.split(",")]
    discharge_lens = [int(x) for x in args.discharge_lens.split(",")]

    if not args.quiet:
        print("=" * 60)
        print("⚡ 储能电价循环优化 Agent")
        print("=" * 60)
        print(f"📂 输入文件: {filepath}")
        print(f"📊 储能容量: {args.capacity} MWh")
        print(f"💰 最小价差: {args.min_spread} 元/MWh")
        print(f"📁 输出目录: {out_dir}")
        print()

    # ========== 优化 ==========
    optimizer = CycleOptimizer()
    optimizer.load_excel(str(filepath))

    cycles = optimizer.optimize(
        min_spread=args.min_spread,
        charge_lens=charge_lens,
        discharge_lens=discharge_lens,
    )

    # ========== 报告 ==========
    if not args.quiet:
        optimizer.print_report(cycles, capacity_mwh=args.capacity)

    if not cycles:
        print("\n❌ 未找到符合条件的充放电循环")
        sys.exit(0)

    # 汇总信息
    total_spread = sum(c["spread"] for c in cycles)
    total_profit = total_spread / 1000 * args.capacity
    days = len(set(c["charge_start"].date() for c in cycles))

    # ========== 导出文件 ==========
    base_name = filepath.stem

    json_path = out_dir / f"{base_name}_cycles.json"
    optimizer.export_json(cycles, str(json_path))
    if not args.quiet:
        print(f"\n📄 JSON导出: {json_path}")

    if not args.no_report:
        gen = ReportGenerator(cycles, capacity_mwh=args.capacity)

        summary = gen.generate_summary()
        if not args.quiet:
            print("\n" + summary)

        report_json_path = out_dir / f"{base_name}_report.json"
        report_csv_path = out_dir / f"{base_name}_report.csv"
        report_html_path = out_dir / f"{base_name}_report.html"

        gen.generate_json(str(report_json_path))
        gen.generate_csv(str(report_csv_path))
        gen.generate_html(str(report_html_path))

        if not args.quiet:
            print(f"\n📄 报告导出:")
            print(f"   JSON: {report_json_path}")
            print(f"   CSV:  {report_csv_path}")
            print(f"   HTML: {report_html_path}")

    # ========== 简洁摘要输出（供其他程序解析）==========
    print(
        f"\n✅ 分析完成 | 循环数:{len(cycles)} | "
        f"总价差:{total_spread:.1f}元/MWh | "
        f"收益:{total_profit:.2f}万元 | "
        f"涉及天数:{days}天"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
