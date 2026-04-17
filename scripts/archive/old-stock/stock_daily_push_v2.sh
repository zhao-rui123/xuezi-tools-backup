#!/bin/bash
# 自选股每日推送脚本 v2 - 简化版
# 工作日下午16:30自动执行

cd /Users/zhaoruicn/.openclaw/workspace

echo "[$(date)] 开始生成股票报告..."

# 生成简单报告（使用新浪财经数据）
python3 << 'PYTHON_EOF'
import json
import urllib.request
from datetime import datetime

# 自选股列表
WATCHLIST = [
    ("002738", "中矿资源"),
    ("002460", "赣锋锂业"),
    ("000792", "盐湖股份"),
    ("002240", "盛新锂能"),
    ("000725", "京东方A"),
    ("600707", "彩虹股份"),
]

def get_sina_stock_data(code):
    """从新浪财经获取股票数据"""
    try:
        # 判断市场
        if code.startswith('6'):
            sina_code = f"sh{code}"
        else:
            sina_code = f"sz{code}"
        
        url = f"https://hq.sinajs.cn/list={sina_code}"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://finance.sina.com.cn'
        })
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode('gb2312', errors='ignore')
        
        # 解析数据
        if 'var hq_str_' in data:
            content = data.split('"')[1]
            parts = content.split(',')
            if len(parts) >= 32:
                name = parts[0]
                current = float(parts[3])
                prev_close = float(parts[2])
                change = current - prev_close
                change_pct = (change / prev_close) * 100 if prev_close > 0 else 0
                
                return {
                    'name': name,
                    'current': current,
                    'change': change,
                    'change_pct': change_pct
                }
    except Exception as e:
        print(f"获取 {code} 数据失败: {e}")
    return None

# 生成报告
print("📊 自选股收盘报告")
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

total_change = 0
results = []

for code, name in WATCHLIST:
    data = get_sina_stock_data(code)
    if data:
        emoji = "🔴" if data['change'] >= 0 else "🟢"
        results.append({
            'name': name,
            'code': code,
            'current': data['current'],
            'change': data['change'],
            'change_pct': data['change_pct'],
            'emoji': emoji
        })
        total_change += data['change_pct']

# 排序
results.sort(key=lambda x: x['change_pct'], reverse=True)

# 输出
for r in results:
    print(f"{r['emoji']} {r['name']} ({r['code']}): {r['current']:.2f} ({r['change']:+.2f}, {r['change_pct']:+.2f}%)")

if results:
    avg = total_change / len(results)
    print(f"\n平均涨跌幅: {avg:+.2f}%")
    print(f"🏆 最强: {results[0]['name']} ({results[0]['change_pct']:+.2f}%)")
    print(f"📉 最弱: {results[-1]['name']} ({results[-1]['change_pct']:+.2f}%)")

PYTHON_EOF

echo "[$(date)] 股票报告生成完成"
