#!/usr/bin/env python3
"""
股票自选股快速推送脚本 v2
本地获取新浪API数据，速度快
"""
import requests
import json
from datetime import datetime

# 自选股配置
SELFSELECT_STOCKS = [
    ("盛新锂能", "sz002240"),
    ("赣锋锂业", "sz002460"),
    ("国城矿业", "sz000688"),
    ("中矿资源", "sz002738"),
    ("比亚迪", "sz002594"),
]

FEISHU_APP_ID = "cli_a928644411785bdf"
FEISHU_APP_SECRET = "qmgZWQq9SQxoiKDOzzsNLfyHr8jBEyLe"
FEISHU_USER_ID = "ou_5a7b7ec0339ffe0c1d5bb6c5bc162579"

def get_stock_data(code):
    """获取股票数据"""
    url = f"http://hq.sinajs.cn/list={code}"
    resp = requests.get(url, timeout=10, headers={'Referer': 'https://finance.sina.com.cn'})
    data = resp.text.split('"')[1].split(',')
    name = data[0]
    prev_close = float(data[2])
    price = float(data[3])
    chg = price - prev_close
    pct = (chg / prev_close) * 100
    amount = int(float(data[9])) if len(data) > 9 else 0  # 成交额(万元)
    return {'name': name, 'price': price, 'chg': chg, 'pct': pct, 'amount': amount}

def get_feishu_token():
    resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}
    )
    return resp.json().get("tenant_access_token")

def send_via_broadcaster(message):
    """通过广播专员发送消息"""
    import subprocess
    cmd = [
        "python3",
        "/Users/zhaoruicn/.openclaw/workspace/agents/kilo/broadcaster.py",
        "--task", "send",
        "--message", message,
        "--target", "group"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except:
        return False

def main():
    now = datetime.now()
    title = f"📊 股票日报 {now.strftime('%Y-%m-%d %H:%M')}"
    
    lines = [title, "=" * 45, ""]
    
    for name, code in SELFSELECT_STOCKS:
        data = get_stock_data(code)
        pct = data['pct']
        emoji = "🔴" if pct > 0 else "🟢" if pct < 0 else "⚪"
        pct_str = f"+{pct:.2f}%" if pct > 0 else f"{pct:.2f}%"
        chg_str = f"+{data['chg']:.2f}" if data['chg'] > 0 else f"{data['chg']:.2f}"
        lines.append(f"{emoji} {data['name']}: {data['price']:.2f} ({pct_str})")
        lines.append(f"   涨跌: {chg_str} | 成交额: {data['amount']//10000}万")
    
    lines.extend(["", "=" * 45, "发送成功!"])
    content = "\n".join(lines)
    print(content)
    
    if send_via_broadcaster(content):
        print("✅ 飞书推送成功")
    else:
        print("❌ 飞书推送失败")

if __name__ == "__main__":
    main()
