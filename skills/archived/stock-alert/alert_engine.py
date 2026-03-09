#!/usr/bin/env python3
"""
股票预警系统 - 实时监控自选股异常信号
"""

import json
import urllib.request
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AlertRule:
    """预警规则"""
    name: str
    condition: str  # 条件描述
    check_func: callable
    level: str = "info"  # info/warning/critical

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

def fetch_realtime_quotes(codes: List[str]) -> Dict:
    """获取实时行情"""
    try:
        # 使用新浪财经API
        a_codes = [c for c in codes if not is_hk_stock(c)]
        hk_codes = [c for c in codes if is_hk_stock(c)]
        
        result = {}
        
        # A股
        if a_codes:
            code_str = ",".join([f"sz{c}" if c.startswith(("0", "3")) else f"sh{c}" for c in a_codes])
            url = f"https://hq.sinajs.cn/list={code_str}"
            
            req = urllib.request.Request(url)
            req.add_header('Referer', 'https://finance.sina.com.cn')
            response = urllib.request.urlopen(req, timeout=10)
            data = response.read().decode('gb2312', errors='ignore')
            
            import re
            for line in data.strip().split('\n'):
                match = re.search(r'var hq_str_(\w+)="([^"]*)"', line)
                if match:
                    code = match.group(1)[2:]
                    fields = match.group(2).split(',')
                    if len(fields) >= 33:
                        result[code] = {
                            'name': fields[0],
                            'price': float(fields[3]),
                            'yesterday': float(fields[2]),
                            'high': float(fields[4]),
                            'low': float(fields[5]),
                            'volume': int(fields[8]),
                        }
        
        # 港股
        if hk_codes:
            hk_str = ",".join([f"rt_hk{c}" for c in hk_codes])
            url = f"https://hq.sinajs.cn/list={hk_str}"
            
            req = urllib.request.Request(url)
            req.add_header('Referer', 'https://finance.sina.com.cn')
            response = urllib.request.urlopen(req, timeout=10)
            data = response.read().decode('gb2312', errors='ignore')
            
            import re
            for line in data.strip().split('\n'):
                match = re.search(r'var hq_str_rt_hk(\w+)="([^"]*)"', line)
                if match:
                    code = match.group(1)
                    fields = match.group(2).split(',')
                    if len(fields) >= 6:
                        result[code] = {
                            'name': fields[1],
                            'price': float(fields[3]) if fields[3] else 0,
                            'yesterday': float(fields[4]) if fields[4] else 0,
                            'high': float(fields[5]) if fields[5] else 0,
                            'low': float(fields[6]) if fields[6] else 0,
                            'volume': int(float(fields[12])) if len(fields) > 12 and fields[12] else 0,
                        }
        
        return result
    except Exception as e:
        print(f"获取行情失败: {e}")
        return {}

def fetch_kline_for_ma(stock_code: str, days: int = 30) -> List[Dict]:
    """获取K线数据（用于计算均线）"""
    try:
        if is_hk_stock(stock_code):
            tencent_code = f"hk{stock_code}"
        elif stock_code.startswith('6'):
            tencent_code = f"sh{stock_code}"
        else:
            tencent_code = f"sz{stock_code}"
        
        url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={tencent_code},day,,,{days},qfq"
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        if tencent_code not in data.get('data', {}):
            return []
        
        stock_data = data['data'][tencent_code]
        klines = stock_data.get('qfqday', []) or stock_data.get('day', [])
        
        result = []
        for k in klines:
            if len(k) >= 5:
                result.append({
                    'date': k[0],
                    'open': float(k[1]),
                    'close': float(k[2]),
                    'low': float(k[3]),
                    'high': float(k[4]),
                })
        return result
    except Exception as e:
        print(f"获取K线失败 {stock_code}: {e}")
        return []

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
    
    # 昨日在MA20下方，今日在上方（向上突破）
    if yesterday_price < ma20 and current_price > ma20:
        return AlertResult(
            code=stock_code,
            name=stock_name,
            alert_type="突破MA20",
            message=f"向上突破MA20均线（MA20={ma20:.2f}，现价={current_price:.2f}）",
            level="warning",
            data={'ma20': ma20, 'price': current_price}
        )
    
    # 昨日在MA20上方，今日在下方（向下跌破）
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

def check_volume_surge(stock_code: str, stock_name: str, quote: Dict) -> Optional[AlertResult]:
    """检查是否放量（需要历史数据，这里简化）"""
    # 简化为价格大幅波动时提醒
    price = quote.get('price', 0)
    yesterday = quote.get('yesterday', 0)
    
    if yesterday <= 0:
        return None
    
    change_pct = (price - yesterday) / yesterday * 100
    
    if change_pct > 5:
        return AlertResult(
            code=stock_code,
            name=stock_name,
            alert_type="大涨提醒",
            message=f"大涨 {change_pct:.2f}%",
            level="info",
            data={'change_pct': change_pct}
        )
    elif change_pct < -5:
        return AlertResult(
            code=stock_code,
            name=stock_name,
            alert_type="大跌提醒",
            message=f"大跌 {abs(change_pct):.2f}%",
            level="warning",
            data={'change_pct': change_pct}
        )
    
    return None

def check_new_high_low(stock_code: str, stock_name: str, quote: Dict, klines: List[Dict]) -> Optional[AlertResult]:
    """检查是否创近期新高/新低"""
    if len(klines) < 20:
        return None
    
    current_price = quote.get('price', 0)
    if current_price <= 0:
        return None
    
    # 20日高点/低点
    highs = [k['high'] for k in klines[-20:]]
    lows = [k['low'] for k in klines[-20:]]
    
    recent_high = max(highs)
    recent_low = min(lows)
    
    if current_price > recent_high * 0.99:  # 接近或创新高
        return AlertResult(
            code=stock_code,
            name=stock_name,
            alert_type="近期新高",
            message=f"创20日新高（{current_price:.2f}）",
            level="info",
            data={'recent_high': recent_high}
        )
    
    if current_price < recent_low * 1.01:  # 接近或创新低
        return AlertResult(
            code=stock_code,
            name=stock_name,
            alert_type="近期新低",
            message=f"创20日新低（{current_price:.2f}）",
            level="warning",
            data={'recent_low': recent_low}
        )
    
    return None

def run_alert_check(codes: List[Tuple[str, str]]) -> List[AlertResult]:
    """运行预警检查"""
    alerts = []
    
    # 获取实时行情
    quotes = fetch_realtime_quotes([c[0] for c in codes])
    
    for code, name in codes:
        if code not in quotes:
            continue
        
        quote = quotes[code]
        klines = fetch_kline_for_ma(code, 30)
        
        # 检查各种预警条件
        checks = [
            check_price_break_ma20(code, name, quote, klines),
            check_volume_surge(code, name, quote),
            check_new_high_low(code, name, quote, klines),
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
    
    # 按级别排序
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

if __name__ == "__main__":
    # 测试
    test_codes = [
        ("002738", "中矿资源"),
        ("002460", "赣锋锂业"),
    ]
    
    alerts = run_alert_check(test_codes)
    print(format_alert_report(alerts))
