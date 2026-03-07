#!/usr/bin/env python3
"""
Stock Analysis Pro - CLI入口
"""

import argparse
import sys
from datetime import datetime

# 添加到路径
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace/skills/stock-analysis-pro')

from core.daily_report import generate_daily_report, send_to_feishu
from core.deep_analysis import deep_analyze_stock, format_deep_analysis
from core.pattern_recognition import analyze_patterns, format_pattern_report
from core.valuation import analyze_valuation, format_valuation_report
from config.watchlist import WATCHLIST

def cmd_daily(args):
    """生成日报"""
    print("📊 生成自选股日报...")
    report = generate_daily_report()
    print(report)
    
    if args.send_feishu:
        print("\n📤 发送到飞书...")
        send_to_feishu(report)

def cmd_analyze(args):
    """深度分析单只股票"""
    code = args.code
    name = args.name or code
    
    print(f"🔍 深度分析 {name} ({code})...")
    result = deep_analyze_stock(code, name)
    
    if result:
        print(format_deep_analysis(result))
    else:
        print(f"❌ 无法获取 {code} 的数据")

def cmd_pattern(args):
    """技术形态识别"""
    if args.codes:
        codes = args.codes.split(',')
    else:
        codes = [args.code]
    
    print("📐 技术形态识别")
    print("="*60)
    
    for code in codes:
        result = analyze_patterns(code, "")
        if result and result.confidence >= 60:
            print(f"\n{code}:")
            print(format_pattern_report(result))
        else:
            print(f"\n{code}: 未识别到明显形态")

def cmd_screen(args):
    """估值策略筛选"""
    if args.codes:
        codes = args.codes.split(',')
    else:
        codes = [s[0] for s in WATCHLIST]
    
    print("💰 估值策略筛选")
    print("="*60)
    
    results = analyze_valuation(codes)
    print(format_valuation_report(results, {}))

def main():
    parser = argparse.ArgumentParser(
        description='Stock Analysis Pro - 专业股票分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 -m stock_analysis_pro daily                    # 生成日报
  python3 -m stock_analysis_pro daily --send-feishu      # 生成并发送
  python3 -m stock_analysis_pro analyze 002460           # 分析单股
  python3 -m stock_analysis_pro pattern 002460           # 形态识别
  python3 -m stock_analysis_pro screen                   # 估值筛选
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # daily 命令
    daily_parser = subparsers.add_parser('daily', help='生成日报')
    daily_parser.add_argument('--send-feishu', action='store_true', help='发送到飞书')
    daily_parser.set_defaults(func=cmd_daily)
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='深度分析')
    analyze_parser.add_argument('code', help='股票代码')
    analyze_parser.add_argument('--name', help='股票名称')
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # pattern 命令
    pattern_parser = subparsers.add_parser('pattern', help='技术形态识别')
    pattern_parser.add_argument('code', nargs='?', help='股票代码')
    pattern_parser.add_argument('--codes', help='多个代码，逗号分隔')
    pattern_parser.set_defaults(func=cmd_pattern)
    
    # screen 命令
    screen_parser = subparsers.add_parser('screen', help='估值策略筛选')
    screen_parser.add_argument('--codes', help='股票代码，逗号分隔')
    screen_parser.set_defaults(func=cmd_screen)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)

if __name__ == '__main__':
    main()
