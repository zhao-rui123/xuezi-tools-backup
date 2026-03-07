#!/usr/bin/env python3
"""
财报日历 - 追踪自选股财报日期和重要公告
"""

import json
import urllib.request
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class EarningsEvent:
    """财报事件"""
    code: str
    name: str
    event_type: str  # 年报/季报/业绩预告/公告
    event_date: str
    days_until: int  # 距离今天还有几天
    description: str

@dataclass
class Announcement:
    """公告信息"""
    code: str
    name: str
    title: str
    date: str
    type: str  # 增减持/定增/股权激励/其他

def get_earnings_calendar_demo() -> List[EarningsEvent]:
    """
    获取财报日历（演示版本）
    实际应该接入东方财富或同花顺API
    """
    # 演示数据 - 实际应该实时抓取
    today = datetime.now()
    
    demo_events = [
        {
            'code': '002738',
            'name': '中矿资源',
            'event_type': '年报预约',
            'date': (today + timedelta(days=15)).strftime('%Y-%m-%d'),
            'description': '2025年年报披露'
        },
        {
            'code': '002460',
            'name': '赣锋锂业',
            'event_type': '股东大会',
            'date': (today + timedelta(days=7)).strftime('%Y-%m-%d'),
            'description': '年度股东大会'
        },
        {
            'code': '000792',
            'name': '盐湖股份',
            'event_type': '季报预约',
            'date': (today + timedelta(days=30)).strftime('%Y-%m-%d'),
            'description': '2026年一季报披露'
        },
    ]
    
    events = []
    for e in demo_events:
        event_date = datetime.strptime(e['date'], '%Y-%m-%d')
        days_until = (event_date - today).days
        
        events.append(EarningsEvent(
            code=e['code'],
            name=e['name'],
            event_type=e['event_type'],
            event_date=e['date'],
            days_until=days_until,
            description=e['description']
        ))
    
    return events

def check_upcoming_earnings(days_ahead: int = 7) -> List[EarningsEvent]:
    """检查近期财报事件"""
    all_events = get_earnings_calendar_demo()
    
    # 筛选N天内的事件
    upcoming = [e for e in all_events if 0 <= e.days_until <= days_ahead]
    
    # 按时间排序
    upcoming.sort(key=lambda x: x.days_until)
    
    return upcoming

def format_earnings_calendar(events: List[EarningsEvent]) -> str:
    """格式化财报日历"""
    if not events:
        return "📅 未来7天暂无财报事件"
    
    lines = [
        f"\n{'='*60}",
        f"📅 财报日历提醒",
        f"{'='*60}",
        f"",
    ]
    
    for e in events:
        if e.days_until == 0:
            time_str = "今天"
        elif e.days_until == 1:
            time_str = "明天"
        else:
            time_str = f"{e.days_until}天后"
        
        emoji = {'年报预约': '📊', '季报预约': '📈', '股东大会': '🏢', '业绩预告': '⚠️'}.get(e.event_type, '📋')
        
        lines.append(f"{emoji} {e.name} ({e.code})")
        lines.append(f"   事件: {e.description}")
        lines.append(f"   时间: {e.event_date} ({time_str})")
        lines.append(f"")
    
    lines.append(f"{'='*60}")
    
    return "\n".join(lines)

def fetch_announcements_demo(stock_code: str) -> List[Announcement]:
    """
    获取公司公告（演示版本）
    实际应该接入巨潮资讯网或交易所公告API
    """
    # 演示数据
    demo_announcements = {
        '002738': [
            {'title': '关于2025年度利润分配预案的公告', 'date': '2026-03-01', 'type': '分红'},
            {'title': '关于控股股东增持股份计划的公告', 'date': '2026-02-25', 'type': '增减持'},
        ],
        '002460': [
            {'title': '关于投资建设锂电池项目的公告', 'date': '2026-03-05', 'type': '投资'},
        ],
    }
    
    announcements = []
    for a in demo_announcements.get(stock_code, []):
        announcements.append(Announcement(
            code=stock_code,
            name='',  # 需要查询
            title=a['title'],
            date=a['date'],
            type=a['type']
        ))
    
    return announcements

def format_recent_announcements(codes: List[tuple]) -> str:
    """格式化近期公告"""
    lines = [
        f"\n{'='*60}",
        f"📢 近期重要公告",
        f"{'='*60}",
        f"",
    ]
    
    has_content = False
    for code, name in codes[:5]:  # 只显示前5只
        announcements = fetch_announcements_demo(code)
        if announcements:
            has_content = True
            for a in announcements[:2]:  # 每只股票最多2条
                emoji = {'增减持': '💰', '定增': '📈', '股权激励': '👥', '分红': '💵', '投资': '🏗️'}.get(a.type, '📋')
                lines.append(f"{emoji} {name} ({code})")
                lines.append(f"   {a.title}")
                lines.append(f"   日期: {a.date}")
                lines.append(f"")
    
    if not has_content:
        lines.append("暂无重要公告")
    
    lines.append(f"{'='*60}")
    
    return "\n".join(lines)

if __name__ == "__main__":
    # 测试
    watchlist = [
        ("002738", "中矿资源"),
        ("002460", "赣锋锂业"),
        ("000792", "盐湖股份"),
    ]
    
    print(format_earnings_calendar(check_upcoming_earnings(30)))
    print("\n")
    print(format_recent_announcements(watchlist))
