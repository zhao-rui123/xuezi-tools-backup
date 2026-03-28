#!/usr/bin/env python3
"""
东方财富API股票筛选+推送脚本
使用curl发送HTTP请求
"""
import subprocess
import json
import re
from datetime import datetime

API_KEY = "mkt_zdTwvCWmIr9g4mHoM8sOsaK8M_ffrhinQPP-GAkhTNs"

def screen_stocks(keyword: str):
    """调用东方财富妙想API选股"""
    cmd = [
        "curl", "-s", "-X", "POST",
        "https://mkapi2.dfcfs.com/finskillshub/api/claw/stock-screen",
        "-H", "Content-Type: application/json",
        "-H", f"apikey: {API_KEY}",
        "--data", f'{{"keyword": "{keyword}", "pageNo": 1, "pageSize": 30}}'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    try:
        data = json.loads(result.stdout)
        return data.get("data", {}).get("data", {})
    except:
        return {}

def parse_results(data: dict) -> list:
    """解析选股结果"""
    text = data.get("partialResults", "")
    results = []
    for line in text.split("\n"):
        if "|" in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 3 and parts[0].isdigit():
                results.append(f"{parts[0]}. {parts[1]} {parts[2]}")
    return results

def send_to_feishu(message: str):
    """发送到飞书"""
    cmd = [
        "openclaw", "message", "send", "--channel", "feishu",
        "--target", "oc_b14195eb990ab57ea573e696758ae3d5",
        "--message", message
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.returncode == 0

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始东方财富选股...")
    
    # 筛选周线（增加"非近期强势股"过滤，排除短线干扰）
    print("正在筛选周线...")
    weekly_data = screen_stocks("周线MACD金叉且KDJ金叉且放量且非近期强势股")
    weekly_count = weekly_data.get("securityCount", 0)
    weekly_results = parse_results(weekly_data)
    
    # 筛选月线（不加强势股过滤，保留更多选项）
    print("正在筛选月线...")
    monthly_data = screen_stocks("月线MACD金叉且KDJ金叉且放量")
    monthly_count = monthly_data.get("securityCount", 0)
    monthly_results = parse_results(monthly_data)
    
    # 构建消息
    msg = f"📈 股票筛选结果 ({datetime.now().strftime('%Y-%m-%d')})\n\n"
    msg += f"🌙 月线MACD+KDJ金叉+放量: {monthly_count}只\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    for r in monthly_results[:10]:
        msg += r + "\n"
    
    msg += f"\n📅 周线MACD+KDJ金叉+放量: {weekly_count}只\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    for r in weekly_results[:20]:
        msg += r + "\n"
    
    print(msg)
    
    # 发送到飞书
    print("\n发送到飞书...")
    if send_to_feishu(msg):
        print("发送成功！")
    else:
        print("发送失败")

if __name__ == "__main__":
    main()
