#!/usr/bin/env python3
"""
混合股票推送脚本 - 结合新浪财经行情 + MiniMax新闻搜索
不依赖东方财富API
"""
import subprocess
import json
import time
import sys
import os

# MiniMax API配置
MINIMAX_API_KEY = "sk-cp-TaEn7XZHReif66-VaxR-UZJuHCoYYYqho4xu6pV22L3MtAL9oImB0iubia4dRjZDN-0avV5_rSS2ggBC6w2gHYz1tYN0semS3mps1PrA9lS-16qJhoh8l3Q"
MINIMAX_API_HOST = "https://api.minimaxi.com"

# 自选股列表（手动维护）
WATCHLIST = [
    ("002594", "比亚迪", "sz"),
    ("002460", "赣锋锂业", "sz"),
    ("002240", "盛新锂能", "sz"),
    ("600707", "彩虹股份", "sh"),
    ("000725", "京东方A", "sz"),
    ("000688", "国城矿业", "sz"),
]

# 港股列表
HK_STOCKS = [
    ("08174", "比亚迪股份", "hk"),
    ("01772", "赣锋锂业", "hk"),
]

def is_hk_stock(code):
    return len(code) == 5 and code.startswith(('0', '1', '2', '3', '6', '8'))

def fetch_sina_data(codes):
    """获取新浪财经实时行情"""
    a_codes = [c[0] for c in codes if not is_hk_stock(c[0])]
    hk_codes = [c[0] for c in codes if is_hk_stock(c[0])]
    
    result = {}
    
    # A股
    if a_codes:
        code_str = ",".join([f"sh{c}" if c.startswith('6') else f"sz{c}" for c in a_codes])
        cmd = f'curl -s "http://hq.sinajs.cn/list={code_str}" -H "Referer: http://finance.sina.com.cn" | iconv -f GBK -t UTF-8'
        try:
            output = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10).stdout
            for line in output.strip().split('\n'):
                if '="' in line:
                    parts = line.split('="')
                    if len(parts) >= 2:
                        # 提取代码
                        raw_code = parts[0].split('_')[-1]
                        # 去掉sh/sz前缀
                        code = raw_code[2:] if raw_code.startswith(('sh', 'sz')) else raw_code
                        data = parts[1].split(',')
                        if len(data) >= 32:
                            try:
                                result[code] = {
                                    'name': data[0],
                                    'open': float(data[1]) if data[1] else 0,
                                    'close': float(data[2]) if data[2] else 0,  # 昨收
                                    'current': float(data[3]) if data[3] else 0,
                                    'high': float(data[4]) if data[4] else 0,
                                    'low': float(data[5]) if data[5] else 0,
                                    'volume': int(float(data[8])) if data[8] else 0,  # 成交量(手)
                                    'amount': float(data[9]) if data[9] else 0,  # 成交额(元)
                                    'bid1': float(data[21]) if data[21] else 0,
                                    'ask1': float(data[19]) if data[19] else 0,
                                }
                            except:
                                pass
        except:
            pass
    
    # 港股
    if hk_codes:
        code_str = ",".join([f"rt_hk{c}" for c in hk_codes])
        cmd = f'curl -s "http://hq.sinajs.cn/list={code_str}" -H "Referer: http://finance.sina.com.cn" | iconv -f GBK -t UTF-8'
        try:
            output = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10).stdout
            for line in output.strip().split('\n'):
                if '="' in line:
                    parts = line.split('="')
                    if len(parts) >= 2:
                        code = parts[0].split('_')[-1]
                        data = parts[1].split(',')
                        if len(data) >= 10:
                            try:
                                result[code] = {
                                    'name': data[1] if len(data) > 1 else '',
                                    'open': float(data[2]) if data[2] else 0,
                                    'close': float(data[3]) if data[3] else 0,
                                    'current': float(data[6]) if data[6] else 0,
                                    'high': float(data[4]) if data[4] else 0,
                                    'low': float(data[5]) if data[5] else 0,
                                    'volume': int(float(data[0])) if data[0] else 0,
                                    'amount': float(data[9]) if data[9] else 0,
                                }
                            except:
                                pass
        except:
            pass
    
    return result

def get_minimax_news(keyword, limit=3):
    """用MiniMax搜索获取股票相关新闻"""
    prompt = f"""搜索"{keyword}股票"的最新新闻资讯，返回最新的3条新闻标题和摘要。格式如下：
新闻1：[标题] - [简要描述]
新闻2：[标题] - [简要描述]
新闻3：[标题] - [简要描述]
只返回新闻，不要其他内容。"""
    
    cmd = [
        "curl", "-s", "-X", "POST",
        f"{MINIMAX_API_HOST}/v1/text/chatcompletion_pro",
        "-H", f"Authorization: Bearer {MINIMAX_API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "model": "MiniMax-Text-01",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.3
        })
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout)
        if 'choices' in data and len(data['choices']) > 0:
            return data['choices'][0]['text'].strip()
    except:
        pass
    return ""

def format_number(n, div=10000):
    """格式化数字"""
    if n >= div:
        return f"{n/div:.2f}万"
    return f"{n:.2f}"

def main():
    print("=" * 50)
    print("📊 混合股票推送 - 新浪财经 + MiniMax新闻")
    print("=" * 50)
    
    # 1. 获取实时行情
    print("\n1. 获取新浪财经实时行情...")
    all_stocks = WATCHLIST + HK_STOCKS
    data = fetch_sina_data(all_stocks)
    
    # 2. 生成行情消息
    msg = "📈 **自选股行情**\n"
    msg += "=" * 50 + "\n\n"
    
    # A股
    msg += "**【A股】**\n"
    for code, name, market in WATCHLIST:
        if code in data:
            d = data[code]
            current = d.get('current', 0)
            close = d.get('close', 0)
            if close > 0:
                change = (current - close) / close * 100
                arrow = "🔺" if change > 0 else "🔻" if change < 0 else "➡️"
                high = d.get('high', 0)
                low = d.get('low', 0)
                vol = format_number(d.get('volume', 0))
                amount = format_number(d.get('amount', 0), 100000000)
                msg += f"{arrow} **{name}**({code})\n"
                msg += f"   {current:.2f}元 {change:+.2f}%\n"
                msg += f"   最高{high:.2f} 最低{low:.2f}\n"
                msg += f"   成交量: {vol}手 成交额: {amount}元\n\n"
    
    # 港股
    msg += "**【港股】**\n"
    for code, name, market in HK_STOCKS:
        if code in data:
            d = data[code]
            current = d.get('current', 0)
            close = d.get('close', 0)
            if close > 0:
                change = (current - close) / close * 100
                arrow = "🔺" if change > 0 else "🔻" if change < 0 else "➡️"
                vol = format_number(d.get('volume', 0))
                msg += f"{arrow} **{name}**({code})\n"
                msg += f"   {current:.2f}港币 {change:+.2f}%\n"
                msg += f"   成交量: {vol}\n\n"
    
    print("\n2. 获取MiniMax新闻...")
    # 3. 获取重点股票新闻（选比亚迪和赣锋）
    news_section = "\n" + "=" * 50 + "\n"
    news_section += "📰 **最新资讯**\n"
    news_section += "=" * 50 + "\n\n"
    
    keywords = ["比亚迪 002594", "赣锋锂业", "面板 京东方"]
    for kw in keywords:
        print(f"   搜索: {kw}")
        news = get_minimax_news(kw, limit=2)
        if news:
            news_section += f"**【{kw.split()[0]}】**\n"
            news_section += news[:300] + "\n\n"
        time.sleep(0.5)
    
    msg += news_section
    
    # 4. 发送飞书消息
    print("\n3. 发送飞书消息...")
    GROUP_ID = "oc_b14195eb990ab57ea573e696758ae3d5"
    
    # 分割消息（飞书限制）
    parts = [msg[i:i+4000] for i in range(0, len(msg), 4000)]
    for i, part in enumerate(parts):
        cmd = [
            "openclaw", "message", "send",
            "--channel", "feishu",
            "--target", GROUP_ID,
            "--message", part
        ]
        subprocess.run(cmd, timeout=30)
        if i < len(parts) - 1:
            time.sleep(1)
    
    print("\n✅ 发送完成!")
    return msg

if __name__ == "__main__":
    main()
