#!/usr/bin/env python3
"""
Stock Suite - 股票分析工具 CLI入口
整合了 stock-analysis-pro 和 stock-screener 的全部功能
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import (
    generate_daily_report,
    send_to_feishu,
    deep_analyze,
    analyze_patterns,
    analyze_valuation,
    check_alerts,
    check_upcoming_earnings,
    check_recent_announcements,
    get_stock_list,
    fetch_sina_quotes,
    fetch_market_index,
    format_valuation_report,
    format_alert_report,
    format_earnings_calendar,
    format_recent_announcements,
)
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
    """深度分析"""
    code = args.code
    name = args.name or code
    
    print(f"🔍 深度分析 {name} ({code})...")
    result = deep_analyze(code, name)
    print(result)


def cmd_pattern(args):
    """技术形态识别"""
    if args.codes:
        codes = args.codes.split(',')
    else:
        codes = [args.code]
    
    print("📐 技术形态识别")
    print("=" * 60)
    
    for code in codes:
        result = analyze_patterns(code)
        if result:
            print(f"\n{code}:")
            print(f"  形态: {result.pattern_name}")
            print(f"  置信度: {result.confidence}%")
            print(f"  方向: {result.direction}")
            print(f"  建议: {result.suggestion}")
        else:
            print(f"\n{code}: 未识别到明显形态")


def cmd_screen(args):
    """估值筛选"""
    if args.codes:
        codes = args.codes.split(',')
    else:
        codes = [s[0] for s in WATCHLIST]
    
    print("💰 估值策略筛选")
    print("=" * 60)
    
    results = analyze_valuation(codes)
    print(format_valuation_report(results))


def cmd_alert(args):
    """预警检查"""
    print("🚨 实时预警检查...")
    alerts = check_alerts()
    print(format_alert_report(alerts))


def cmd_earnings(args):
    """财报日历"""
    days = args.days
    print(f"📅 财报日历检查（未来{days}天）...")
    events = check_upcoming_earnings(days_ahead=days)
    print(format_earnings_calendar(events))


def cmd_announcements(args):
    """公告监控"""
    print("📢 近期公告...")
    print(format_recent_announcements(WATCHLIST))


def cmd_monitor(args):
    """统一监控面板"""
    print("=" * 60)
    print("📊 股票完整监控报告")
    print("=" * 60)
    
    print("\n🚨 实时预警检查...")
    alerts = check_alerts()
    if alerts:
        print(format_alert_report(alerts))
    else:
        print("  暂无预警信号")
    
    print("\n📅 财报日历检查...")
    events = check_upcoming_earnings(days_ahead=7)
    if events:
        print(format_earnings_calendar(events))
    else:
        print("  未来7天无财报事件")
    
    print("\n📢 近期公告...")
    print(format_recent_announcements(WATCHLIST))
    
    print("\n" + "=" * 60)
    print("✅ 监控完成")
    print("=" * 60)


def cmd_quote(args):
    """实时行情"""
    codes = args.codes.split(',') if args.codes else [s[0] for s in WATCHLIST]
    
    print("📈 实时行情")
    print("=" * 60)
    
    quotes = fetch_sina_quotes(codes)
    
    market = fetch_market_index("sh000001")
    if market:
        emoji = "🟢" if market['change_pct'] >= 0 else "🔴"
        print(f"\n{emoji} 大盘: {market['price']:.2f} ({market['change_pct']:+.2f}%)")
    
    print("\n自选股:")
    for code in codes:
        quote = quotes.get(code, {})
        price = quote.get('price', 0)
        yesterday = quote.get('yesterday', 0)
        
        if price > 0 and yesterday > 0:
            change_pct = (price - yesterday) / yesterday * 100
            emoji = "🟢" if change_pct >= 0 else "🔴"
            name = quote.get('name', code)
            print(f"{emoji} {name} ({code}): ¥{price:.2f} ({change_pct:+.2f}%)")
        else:
            print(f"⚪ {code}: 无法获取数据")


def cmd_watchlist(args):
    """查看自选股"""
    print("📋 自选股列表")
    print("=" * 60)
    for code, name, industry in WATCHLIST:
        print(f"  {code} - {name} ({industry})")


def main():
    parser = argparse.ArgumentParser(
        description='Stock Suite - 股票分析工具 v3.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m stock_suite daily                    # 生成日报
  python -m stock_suite daily --send-feishu     # 生成并发送飞书
  python -m stock_suite analyze 002460         # 深度分析
  python -m stock_suite pattern 002460         # 形态识别
  python -m stock_suite screen                  # 估值筛选
  python -m stock_suite alert                   # 预警检查
  python -m stock_suite earnings --days 7       # 财报日历
  python -m stock_suite monitor                 # 统一监控
  python -m stock_suite quote                   # 实时行情
  python -m stock_suite watchlist               # 查看自选股
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    daily_parser = subparsers.add_parser('daily', help='生成日报')
    daily_parser.add_argument('--send-feishu', action='store_true', help='发送到飞书')
    daily_parser.set_defaults(func=cmd_daily)
    
    analyze_parser = subparsers.add_parser('analyze', help='深度分析')
    analyze_parser.add_argument('code', help='股票代码')
    analyze_parser.add_argument('--name', help='股票名称')
    analyze_parser.set_defaults(func=cmd_analyze)
    
    pattern_parser = subparsers.add_parser('pattern', help='技术形态识别')
    pattern_parser.add_argument('code', nargs='?', help='股票代码')
    pattern_parser.add_argument('--codes', help='多个代码，逗号分隔')
    pattern_parser.set_defaults(func=cmd_pattern)
    
    screen_parser = subparsers.add_parser('screen', help='估值策略筛选')
    screen_parser.add_argument('--codes', help='股票代码，逗号分隔')
    screen_parser.set_defaults(func=cmd_screen)
    
    alert_parser = subparsers.add_parser('alert', help='预警检查')
    alert_parser.set_defaults(func=cmd_alert)
    
    earnings_parser = subparsers.add_parser('earnings', help='财报日历')
    earnings_parser.add_argument('--days', type=int, default=7, help='提前天数')
    earnings_parser.set_defaults(func=cmd_earnings)
    
    announcements_parser = subparsers.add_parser('announcements', help='公告监控')
    announcements_parser.set_defaults(func=cmd_announcements)
    
    monitor_parser = subparsers.add_parser('monitor', help='统一监控面板')
    monitor_parser.set_defaults(func=cmd_monitor)
    
    quote_parser = subparsers.add_parser('quote', help='实时行情')
    quote_parser.add_argument('--codes', help='股票代码，逗号分隔')
    quote_parser.set_defaults(func=cmd_quote)
    
    watchlist_parser = subparsers.add_parser('watchlist', help='查看自选股')
    watchlist_parser.set_defaults(func=cmd_watchlist)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()
