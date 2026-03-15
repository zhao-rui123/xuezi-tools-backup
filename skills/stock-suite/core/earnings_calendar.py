"""
财报日历模块 - 追踪自选股财报日期和重要公告
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class EarningsEvent:
    """财报事件"""
    code: str
    name: str
    event_type: str
    event_date: str
    days_until: int
    description: str

@dataclass
class Announcement:
    """公告信息"""
    code: str
    name: str
    title: str
    date: str
    type: str

DEMO_EVENTS = [
    {'code': '002738', 'name': '中矿资源', 'event_type': '年报预约', 'days': 15, 'description': '2025年年报披露'},
    {'code': '002460', 'name': '赣锋锂业', 'event_type': '股东大会', 'days': 7, 'description': '年度股东大会'},
    {'code': '000725', 'name': '京东方A', 'event_type': '季报预约', 'days': 20, 'description': '2026年一季报披露'},
    {'code': '600519', 'name': '贵州茅台', 'event_type': '年报预约', 'days': 25, 'description': '2025年年报披露'},
    {'code': '601318', 'name': '中国平安', 'event_type': '业绩预告', 'days': 10, 'description': '2025年业绩预告'},
]

DEMO_ANNOUNCEMENTS = {
    '002738': [
        {'title': '关于2025年度利润分配预案的公告', 'date': '2026-03-01', 'type': '分红'},
        {'title': '关于控股股东增持股份计划的公告', 'date': '2026-02-25', 'type': '增减持'},
    ],
    '002460': [
        {'title': '关于投资建设锂电池项目的公告', 'date': '2026-03-05', 'type': '投资'},
        {'title': '关于2025年度业绩预告的公告', 'date': '2026-01-20', 'type': '业绩'},
    ],
    '000725': [
        {'title': '关于回购股份方案的公告', 'date': '2026-03-03', 'type': '回购'},
    ],
    '600519': [
        {'title': '关于2025年度经营情况的公告', 'date': '2026-02-28', 'type': '经营'},
    ],
}

def get_earnings_calendar_demo() -> List[EarningsEvent]:
    """获取财报日历（演示版本）"""
    today = datetime.now()
    
    events = []
    for e in DEMO_EVENTS:
        event_date = today + timedelta(days=e['days'])
        
        events.append(EarningsEvent(
            code=e['code'],
            name=e['name'],
            event_type=e['event_type'],
            event_date=event_date.strftime('%Y-%m-%d'),
            days_until=e['days'],
            description=e['description']
        ))
    
    return events

def check_upcoming_earnings(days_ahead: int = 7) -> List[EarningsEvent]:
    """检查近期财报事件"""
    all_events = get_earnings_calendar_demo()
    upcoming = [e for e in all_events if 0 <= e.days_until <= days_ahead]
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
    """获取公司公告（演示版本）"""
    announcements = []
    for a in DEMO_ANNOUNCEMENTS.get(stock_code, []):
        announcements.append(Announcement(
            code=stock_code,
            name='',
            title=a['title'],
            date=a['date'],
            type=a['type']
        ))
    
    return announcements

def check_recent_announcements(watchlist: List[tuple] = None) -> List[Announcement]:
    """检查近期公告"""
    if watchlist is None:
        watchlist = [
            ("002738", "中矿资源"),
            ("002460", "赣锋锂业"),
            ("000725", "京东方A"),
        ]
    
    all_announcements = []
    
    for code, name in watchlist:
        announcements = fetch_announcements_demo(code)
        for a in announcements:
            a.name = name
            all_announcements.append(a)
    
    all_announcements.sort(key=lambda x: x.date, reverse=True)
    return all_announcements[:10]

def format_recent_announcements(watchlist: List[tuple]) -> str:
    """格式化近期公告"""
    announcements = check_recent_announcements(watchlist)
    
    lines = [
        f"\n{'='*60}",
        f"📢 近期重要公告",
        f"{'='*60}",
        f"",
    ]
    
    if not announcements:
        lines.append("暂无重要公告")
    else:
        for a in announcements:
            emoji = {'增减持': '💰', '定增': '📈', '股权激励': '👥', '分红': '💵', '投资': '🏗️', '回购': '🔄', '业绩': '📊', '经营': '📋'}.get(a.type, '📋')
            lines.append(f"{emoji} {a.name} ({a.code})")
            lines.append(f"   {a.title}")
            lines.append(f"   日期: {a.date}")
            lines.append(f"")
    
    lines.append(f"{'='*60}")
    
    return "\n".join(lines)

def check_earnings_calendar(days_ahead: int = 7) -> List[EarningsEvent]:
    """检查财报日历（兼容旧接口）"""
    return check_upcoming_earnings(days_ahead)
