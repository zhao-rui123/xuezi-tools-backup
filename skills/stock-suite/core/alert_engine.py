"""
股票预警引擎 - 实时监控自选股异常信号
整合：价格突破、均线突破、异常波动、新高新低
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AlertResult:
    """预警结果"""
    code: str
    name: str
    alert_type: str
    message: str
    level: str
    data: Dict

def is_hk_stock(code: str) -> bool:
    """判断是否为港股"""
    return len(code) == 5 and code[0] in '012368'

def calculate_ma(klines: List[Dict], period: int) -> Optional[float]:
    """计算移动平均线"""
    if len(klines) < period:
        return None
    closes = [k['close'] for k in klines[-period:]]
    return sum(closes) / period

def check_price_break_ma20(stock_code: str, stock_name: str, quote: Dict, klines: List[Dict]) -> Optional[AlertResult]:
    """检查是否突破MA20"""
    ma20 = calculate_ma(klines, 20)
    if not ma20:
        return None
    
    current_price = quote.get('price', 0)
    yesterday_price = quote.get('yesterday', 0)
    
    if yesterday_price <= 0:
        return None
    
    if yesterday_price < ma20 and current_price > ma20:
        return AlertResult(
            code=stock_code,
            name=stock_name,
            alert_type="突破MA20",
            message=f"向上突破MA20均线（MA20={ma20:.2f}，现价={current_price:.2f}）",
            level="info",
            data={'ma20': ma20, 'price': current_price}
        )
    
    if yesterday_price > ma20 and current_price < ma20:
        return AlertResult(
            code=stock_code,
            name=stock_name,
            alert_type="跌破MA20",
            message=f"向下跌破MA20均线（MA20={ma20:.2f}，现价={current_price:.2f}）",
            level="warning",
            data={'ma20': ma20, 'price': current_price}
        )
    
    return None

def check_price_break_ma5(stock_code: str, stock_name: str, quote: Dict, klines: List[Dict]) -> Optional[AlertResult]:
    """检查是否突破MA5"""
    ma5 = calculate_ma(klines, 5)
    if not ma5:
        return None
    
    current_price = quote.get('price', 0)
    yesterday_price = quote.get('yesterday', 0)
    
    if yesterday_price <= 0:
        return None
    
    if yesterday_price < ma5 and current_price > ma5:
        return AlertResult(
            code=stock_code,
            name=stock_name,
            alert_type="突破MA5",
            message=f"向上突破MA5均线（MA5={ma5:.2f}，现价={current_price:.2f}）",
            level="info",
            data={'ma5': ma5, 'price': current_price}
        )
    
    if yesterday_price > ma5 and current_price < ma5:
        return AlertResult(
            code=stock_code,
            name=stock_name,
            alert_type="跌破MA5",
            message=f"向下跌破MA5均线（MA5={ma5:.2f}，现价={current_price:.2f}）",
            level="warning",
            data={'ma5': ma5, 'price': current_price}
        )
    
    return None

def check_price_change(stock_code: str, stock_name: str, quote: Dict) -> Optional[AlertResult]:
    """检查价格异常波动"""
    price = quote.get('price', 0)
    yesterday = quote.get('yesterday', 0)
    
    if yesterday <= 0:
        return None
    
    change_pct = (price - yesterday) / yesterday * 100
    
    if change_pct > 7:
        return AlertResult(
            code=stock_code,
            name=stock_name,
            alert_type="大涨提醒",
            message=f"单日涨幅 {change_pct:.2f}%",
            level="info",
            data={'change_pct': change_pct}
        )
    elif change_pct > 9.5:
        return AlertResult(
            code=stock_code,
            name=stock_name,
            alert_type="涨停提醒",
            message=f"接近涨停 {change_pct:.2f}%",
            level="warning",
            data={'change_pct': change_pct}
        )
    elif change_pct < -7:
        return AlertResult(
            code=stock_code,
            name=stock_name,
            alert_type="大跌提醒",
            message=f"单日跌幅 {abs(change_pct):.2f}%",
            level="warning",
            data={'change_pct': change_pct}
        )
    elif change_pct < -9.5:
        return AlertResult(
            code=stock_code,
            name=stock_name,
            alert_type="跌停提醒",
            message=f"接近跌停 {abs(change_pct):.2f}%",
            level="critical",
            data={'change_pct': change_pct}
        )
    
    return None

def check_new_high_low(stock_code: str, stock_name: str, quote: Dict, klines: List[Dict], days: int = 20) -> Optional[AlertResult]:
    """检查是否创近期新高/新低"""
    if len(klines) < days:
        return None
    
    current_price = quote.get('price', 0)
    if current_price <= 0:
        return None
    
    highs = [k['high'] for k in klines[-days:]]
    lows = [k['low'] for k in klines[-days:]]
    
    recent_high = max(highs)
    recent_low = min(lows)
    
    if current_price > recent_high * 0.99:
        return AlertResult(
            code=stock_code,
            name=stock_name,
            alert_type="近期新高",
            message=f"创{days}日新高（{current_price:.2f}）",
            level="info",
            data={'recent_high': recent_high}
        )
    
    if current_price < recent_low * 1.01:
        return AlertResult(
            code=stock_code,
            name=stock_name,
            alert_type="近期新低",
            message=f"创{days}日新低（{current_price:.2f}）",
            level="warning",
            data={'recent_low': recent_low}
        )
    
    return None

def check_volume_surge(stock_code: str, stock_name: str, quote: Dict) -> Optional[AlertResult]:
    """检查成交量异常"""
    price = quote.get('price', 0)
    yesterday = quote.get('yesterday', 0)
    volume = quote.get('volume', 0)
    
    if yesterday <= 0 or volume <= 0:
        return None
    
    change_pct = (price - yesterday) / yesterday * 100
    
    if abs(change_pct) > 5:
        return AlertResult(
            code=stock_code,
            name=stock_name,
            alert_type="放量波动",
            message=f"放量 {abs(change_pct):.2f}%，成交量 {volume:,} 股",
            level="info",
            data={'volume': volume, 'change_pct': change_pct}
        )
    
    return None

def run_alert_check(watchlist: List[tuple]) -> List[AlertResult]:
    """运行预警检查"""
    try:
        from core.data_fetcher import fetch_sina_quotes, fetch_tencent_kline
    except ImportError:
        try:
            from data_fetcher import fetch_sina_quotes, fetch_tencent_kline
        except ImportError:
            from .data_fetcher import fetch_sina_quotes, fetch_tencent_kline
    
    alerts = []
    codes = [c[0] for c in watchlist]
    
    quotes = fetch_sina_quotes(codes)
    
    for code, name in watchlist:
        if code not in quotes:
            continue
        
        quote = quotes[code]
        klines = fetch_tencent_kline(code, 30)
        
        if not klines:
            continue
        
        checks = [
            check_price_break_ma20(code, name, quote, klines),
            check_price_break_ma5(code, name, quote, klines),
            check_price_change(code, name, quote),
            check_new_high_low(code, name, quote, klines),
            check_volume_surge(code, name, quote),
        ]
        
        for alert in checks:
            if alert:
                alerts.append(alert)
    
    return alerts

def format_alert_report(alerts: List[AlertResult]) -> str:
    """格式化预警报告"""
    if not alerts:
        return "✅ 暂无预警信号"
    
    lines = [
        f"\n{'='*60}",
        f"🚨 股票预警报告 - {datetime.now().strftime('%H:%M')}",
        f"{'='*60}",
        f"",
    ]
    
    level_order = {'critical': 0, 'warning': 1, 'info': 2}
    alerts.sort(key=lambda x: level_order.get(x.level, 3))
    
    for alert in alerts:
        emoji = {'critical': '🔴', 'warning': '🟡', 'info': '🟢'}.get(alert.level, '⚪')
        lines.append(f"{emoji} [{alert.level.upper()}] {alert.name} ({alert.code})")
        lines.append(f"   类型: {alert.alert_type}")
        lines.append(f"   详情: {alert.message}")
        lines.append(f"")
    
    lines.append(f"{'='*60}")
    
    return "\n".join(lines)

def check_alerts(watchlist: List[tuple] = None) -> List[AlertResult]:
    """检查预警（兼容旧接口）"""
    if watchlist is None:
        try:
            from config.watchlist import WATCHLIST
            watchlist = WATCHLIST
        except ImportError:
            try:
                import sys
                import os
                config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
                sys.path.insert(0, config_path)
                from watchlist import WATCHLIST
                watchlist = WATCHLIST
            except ImportError:
                watchlist = [
                    ("002738", "中矿资源"),
                    ("002460", "赣锋锂业"),
                    ("000725", "京东方A"),
                    ("600519", "贵州茅台"),
                ]
    
    return run_alert_check(watchlist)
