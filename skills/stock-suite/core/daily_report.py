"""
日报生成模块
"""

from typing import Dict, List
from datetime import datetime

def get_default_watchlist() -> List[tuple]:
    """获取默认自选股列表"""
    return [
        ("002738", "中矿资源"),
        ("002460", "赣锋锂业"),
        ("000725", "京东方A"),
        ("600519", "贵州茅台"),
        ("601318", "中国平安"),
    ]

def generate_daily_report() -> str:
    """生成自选股日报"""
    try:
        from core.data_fetcher import fetch_sina_quotes, fetch_market_index
        from core.technical_analysis import get_latest_indicators, get_all_signals
        from core.data_fetcher import fetch_tencent_kline
        from core.pattern_recognition import analyze_all_patterns
        from core.valuation import analyze_comprehensive
    except ImportError:
        try:
            from data_fetcher import fetch_sina_quotes, fetch_market_index
            from technical_analysis import get_latest_indicators, get_all_signals
            from data_fetcher import fetch_tencent_kline
            from pattern_recognition import analyze_all_patterns
            from valuation import analyze_comprehensive
        except ImportError:
            from .data_fetcher import fetch_sina_quotes, fetch_market_index
            from .technical_analysis import get_latest_indicators, get_all_signals
            from .data_fetcher import fetch_tencent_kline
            from .pattern_recognition import analyze_all_patterns
            from .valuation import analyze_comprehensive
    
    watchlist = get_default_watchlist()
    codes = [c[0] for c in watchlist]
    
    lines = [
        f"📊 自选股日报 - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * 60,
    ]
    
    market = fetch_market_index("sh000001")
    if market:
        emoji = "🟢" if market['change_pct'] >= 0 else "🔴"
        lines.append(f"\n【大盘指数】")
        lines.append(f"{emoji} 上证指数: {market['price']:.2f} ({market['change_pct']:+.2f}%)")
    
    quotes = fetch_sina_quotes(codes)
    
    lines.append(f"\n【自选股行情】")
    
    changes = []
    for code, name in watchlist:
        quote = quotes.get(code, {})
        price = quote.get('price', 0)
        yesterday = quote.get('yesterday', 0)
        
        if price > 0 and yesterday > 0:
            change_pct = (price - yesterday) / yesterday * 100
            emoji = "🟢" if change_pct >= 0 else "🔴"
            lines.append(f"{emoji} {name} ({code}): ¥{price:.2f} ({change_pct:+.2f}%)")
            changes.append((change_pct, name))
    
    lines.append(f"\n【技术分析】")
    for code, name in watchlist:
        try:
            data = fetch_tencent_kline(code, 30)
            if data and len(data) >= 20:
                signals = get_all_signals(data)
                
                trend_info = {}
                closes = [d['close'] for d in data]
                ma5 = sum(closes[-5:]) / 5
                ma10 = sum(closes[-10:]) / 10
                ma20 = sum(closes[-20:]) / 20
                
                if ma5 > ma10 > ma20:
                    trend_info['trend'] = "多头"
                elif ma5 < ma10 < ma20:
                    trend_info['trend'] = "空头"
                else:
                    trend_info['trend'] = "震荡"
                
                latest = data[-1]
                rsi = latest.get('rsi14', 50)
                rsi_status = "超买" if rsi > 70 else "超卖" if rsi < 30 else "正常"
                dev = ((latest['close'] - ma20) / ma20 * 100) if ma20 > 0 else 0
                
                emoji = "📈" if trend_info['trend'] == "多头" else "📉" if trend_info['trend'] == "空头" else "↔️"
                lines.append(f"{emoji} {name}: {trend_info['trend']}趋势")
                lines.append(f"   MA5:{ma5:.2f} MA10:{ma10:.2f} MA20:{ma20:.2f}")
                lines.append(f"   RSI:{rsi:.1f}({rsi_status}) 偏离MA20:{dev:+.1f}%")
        except Exception as e:
            pass
    
    lines.append(f"\n【技术形态】")
    for code, name in watchlist:
        try:
            patterns = analyze_all_patterns(code)
            if patterns:
                p = patterns[0]
                lines.append(f"📐 {name}: {p['pattern']} ({p['confidence']}%) - {p['direction']}")
        except:
            pass
    
    if changes:
        changes.sort(key=lambda x: x[0], reverse=True)
        lines.append(f"\n【统计】")
        avg_change = sum([c[0] for c in changes]) / len(changes)
        lines.append(f"组合平均: {avg_change:+.2f}%")
        if changes:
            lines.append(f"🏆 最强: {changes[0][1]} ({changes[0][0]:+.2f}%)")
            lines.append(f"💔 最弱: {changes[-1][1]} ({changes[-1][0]:+.2f}%)")
    
    lines.append("\n" + "=" * 60)
    
    return "\n".join(lines)

def send_to_feishu(report: str, webhook_url: str = "") -> bool:
    """发送到飞书（需要配置webhook）"""
    print("飞书推送功能需要配置webhook URL")
    print(report)
    return False
