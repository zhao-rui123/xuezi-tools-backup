#!/usr/bin/env python3
"""
股票监控系统 (Stock Monitor)
整合: 预警系统 + 财报日历

功能:
1. 实时预警 (价格突破、均线突破、异常波动、新高新低)
2. 财报日历 (财报日期、业绩预警、公告提醒)
3. 统一监控面板

作者: 雪子助手
版本: 2.0.0 (整合版)
日期: 2026-03-09
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from alert_engine import check_alerts, format_alert_report
from earnings_calendar import check_upcoming_earnings, format_earnings_calendar, check_recent_announcements


def full_monitoring_report():
    """生成完整监控报告"""
    print("=" * 60)
    print("📊 股票完整监控报告")
    print("=" * 60)
    
    # 1. 预警检查
    print("\n🚨 实时预警检查...")
    alerts = check_alerts()
    if alerts:
        print(format_alert_report(alerts))
    else:
        print("  暂无预警信号")
    
    # 2. 财报日历
    print("\n📅 财报日历检查...")
    earnings = check_upcoming_earnings(days_ahead=7)
    if earnings:
        print(format_earnings_calendar(earnings))
    else:
        print("  未来7天无财报事件")
    
    # 3. 公告监控
    print("\n📢 近期公告检查...")
    announcements = check_recent_announcements()
    if announcements:
        for ann in announcements[:5]:
            print(f"  • {ann['stock']}: {ann['title'][:40]}...")
    else:
        print("  暂无重要公告")
    
    print("\n" + "=" * 60)
    print("✅ 监控完成")
    print("=" * 60)


def quick_alert_check():
    """快速预警检查"""
    alerts = check_alerts()
    if alerts:
        print(format_alert_report(alerts))
        return True
    else:
        print("✅ 无预警信号")
        return False


def earnings_reminder(days_ahead=7):
    """财报提醒"""
    earnings = check_upcoming_earnings(days_ahead=days_ahead)
    if earnings:
        print(format_earnings_calendar(earnings))
        return True
    else:
        print(f"✅ 未来{days_ahead}天无财报事件")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="股票监控系统")
    parser.add_argument("--full", action="store_true", help="完整监控报告")
    parser.add_argument("--alert", action="store_true", help="仅预警检查")
    parser.add_argument("--earnings", action="store_true", help="仅财报检查")
    parser.add_argument("--days", type=int, default=7, help="财报提前天数")
    
    args = parser.parse_args()
    
    if args.alert:
        quick_alert_check()
    elif args.earnings:
        earnings_reminder(days_ahead=args.days)
    else:
        full_monitoring_report()
