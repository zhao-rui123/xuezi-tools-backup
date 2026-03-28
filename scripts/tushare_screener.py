#!/usr/bin/env python3
"""本地运行的Tushare选股推送"""
import sys
import time
sys.path.insert(0, '/opt/stock-screener-v2')

from tushare_api import get_pro, get_kline
import subprocess

GROUP_ID = "oc_b14195eb990ab57ea573e696758ae3d5"

def analyze_pattern(df):
    """K线形态分析"""
    if len(df) < 20:
        return "数据不足"
    
    closes = df['close'].tolist()
    volumes = df['vol'].tolist()
    
    ma5 = sum(closes[-5:]) / 5
    ma20 = sum(closes[-20:]) / 20
    
    if ma5 > ma20:
        trend = "上升趋势"
    elif ma5 < ma20:
        trend = "下降趋势"
    else:
        trend = "横盘整理"
    
    avg_vol = sum(volumes[-5:]) / 5
    if volumes[-1] > avg_vol * 1.5:
        volume = "放量"
    elif volumes[-1] < avg_vol * 0.7:
        volume = "缩量"
    else:
        volume = "正常"
    
    return f"{trend}，{volume}"

def main():
    print("开始Tushare选股筛选...")
    
    # 自选股列表
    self_stocks = ["002594.SZ", "002460.SZ", "002240.SZ", "600707.SZ", "000725.SZ", "000688.SZ", "08174.HK", "01772.HK"]
    
    results = []
    for code in self_stocks:
        try:
            time.sleep(0.5)  # 避免频率限制
            df = get_kline(code, 30)
            if len(df) < 20:
                continue
            pattern = analyze_pattern(df)
            results.append(f"{code[:6]} - {pattern}")
        except Exception as e:
            print(f"Error {code}: {e}")
    
    msg = "📊 Tushare自选股K线分析\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    for r in results:
        msg += r + "\n"
    
    print(msg)
    
    subprocess.run([
        "openclaw", "message", "send", "--channel", "feishu",
        "--target", GROUP_ID,
        "--message", msg
    ], capture_output=True, timeout=30)
    print("发送成功!")

if __name__ == "__main__":
    main()
