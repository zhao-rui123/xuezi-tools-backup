#!/usr/bin/env python3
"""
自选股每日推送 - 简化版
只使用新浪财经数据，速度快，适合定时任务
"""

import urllib.request
import re
from datetime import datetime

# 自选股列表
WATCHLIST = [
    ("002738", "中矿资源", "sz"),
    ("002460", "赣锋锂业", "sz"),
    ("000792", "盐湖股份", "sz"),
    ("002240", "盛新锂能", "sz"),
    ("000725", "京东方A", "sz"),
    ("600707", "彩虹股份", "sh"),
]

MARKET_INDICES = {
    "上证指数": "sh000001",
    "深证成指": "sz399001",
    "创业板指": "sz399006",
}

def fetch_sina_data(codes):
    """获取新浪财经数据"""
    code_str = ",".join([f"{prefix}{code}" for code, name, prefix in codes])
    url = f"https://hq.sinajs.cn/list={code_str}"
    
    try:
        req = urllib.request.Request(url)
        req.add_header('Referer', 'https://finance.sina.com.cn')
        response = urllib.request.urlopen(req, timeout=10)
        data = response.read().decode('gb2312', errors='ignore')
        
        result = {}
        for line in data.strip().split('\n'):
            match = re.search(r'var hq_str_(\w+)="([^"]*)"', line)
            if match:
                full_code = match.group(1)
                code = full_code[2:]  # 去掉sz/sh前缀
                values = match.group(2).split(',')
                if len(values) >= 10:
                    result[code] = {
                        'name': values[0],
                        'open': float(values[1]),
                        'close': float(values[2]),
                        'current': float(values[3]),
                        'high': float(values[4]),
                        'low': float(values[5]),
                        'volume': float(values[8]) / 10000,  # 万股
                        'amount': float(values[9]) / 100000000,  # 亿元
                    }
        return result
    except Exception as e:
        print(f"获取数据失败: {e}")
        return {}

def generate_report():
    """生成股票报告"""
    now = datetime.now()
    date_str = now.strftime("%Y年%m月%d日")
    time_str = now.strftime("%H:%M")
    
    # 获取指数数据
    indices_data = fetch_sina_data([
        ("000001", "上证指数", "sh"),
        ("399001", "深证成指", "sz"),
        ("399006", "创业板指", "sz"),
    ])
    
    # 获取自选股数据
    stocks_data = fetch_sina_data(WATCHLIST)
    
    lines = []
    lines.append("=" * 60)
    lines.append(f"📊 自选股日报 - {date_str} {time_str}")
    lines.append("=" * 60)
    lines.append("")
    
    # 大盘指数
    lines.append("【大盘指数】")
    for name, code in MARKET_INDICES.items():
        if code[2:] in indices_data:
            d = indices_data[code[2:]]
            change = d['current'] - d['close']
            percent = (change / d['close']) * 100
            emoji = "🔴" if change >= 0 else "🟢"
            lines.append(f"  {emoji} {name}: {d['current']:.2f} ({change:+.2f}, {percent:+.2f}%)")
    lines.append("")
    
    # 自选股
    lines.append("【自选股表现】")
    lines.append(f"{'名称':<8} {'代码':<10} {'现价':<8} {'涨跌':<8} {'涨幅':<8}")
    lines.append("-" * 50)
    
    total_change = 0
    for code, name, prefix in WATCHLIST:
        if code in stocks_data:
            d = stocks_data[code]
            change = d['current'] - d['close']
            percent = (change / d['close']) * 100
            total_change += percent
            emoji = "🔴" if change >= 0 else "🟢"
            lines.append(f"{emoji}{name:<6} {code:<10} {d['current']:<8.2f} {change:<+8.2f} {percent:<+8.2f}%")
    
    lines.append("")
    lines.append("=" * 60)
    lines.append("💡 详细分析请访问: http://106.54.25.161/")
    lines.append("=" * 60)
    
    return "\n".join(lines)

def send_to_feishu(message):
    """使用Kilo广播专员发送消息"""
    import subprocess
    try:
        result = subprocess.run(
            ['python3', '/Users/zhaoruicn/.openclaw/workspace/agents/kilo/broadcaster.py',
             '--task', 'send', '--message', message, '--target', 'user'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("✅ 股票报告已通过Kilo发送")
            return True
        else:
            print(f"❌ 发送失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False

if __name__ == "__main__":
    print("生成自选股日报...")
    report = generate_report()
    print(report)
    print("\n" + "=" * 60)
    print("发送到飞书...")
    send_to_feishu(report)
