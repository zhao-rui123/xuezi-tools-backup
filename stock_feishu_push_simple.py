#!/usr/bin/env python3
"""
飞书股票推送 - 定时任务专用版
简化版本，只使用新浪财经数据，避免 AkShare 超时问题
"""
import os
import sys
import subprocess
import urllib.request
import re
from datetime import datetime

# 自选股列表
WATCHLIST = [
    ("002738", "中矿资源", "锂矿/资源"),
    ("002460", "赣锋锂业", "锂电池/新能源"),
    ("000792", "盐湖股份", "盐湖提锂"),
    ("002240", "盛新锂能", "锂电池材料"),
    ("000725", "京东方A", "面板/显示"),
    ("600707", "彩虹股份", "面板/显示"),
]

# 大盘指数
MARKET_INDICES = {
    "上证指数": "sh000001",
    "深证成指": "sz399001",
    "创业板指": "sz399006",
}

def fetch_stock_data():
    """从新浪财经获取股票数据"""
    codes = [s[0] for s in WATCHLIST]
    code_str = ",".join([
        f"sz{c}" if c.startswith(("0", "3")) else f"sh{c}"
        for c in codes
    ])
    
    url = f"https://hq.sinajs.cn/list={code_str}"
    req = urllib.request.Request(url)
    req.add_header('Referer', 'https://finance.sina.com.cn')
    
    try:
        response = urllib.request.urlopen(req, timeout=10)
        data = response.read().decode('gb2312', errors='ignore')
        
        result = {}
        for line in data.strip().split('\n'):
            match = re.search(r'var hq_str_\w+="([^"]*)"', line)
            if match:
                fields = match.group(1).split(',')
                if len(fields) >= 33:
                    code = line.split('_')[-1].split('=')[0].replace('sz', '').replace('sh', '')
                    result[code] = {
                        'name': fields[0],
                        'price': float(fields[3]),
                        'yesterday': float(fields[2]),
                        'open': float(fields[1]),
                        'high': float(fields[4]),
                        'low': float(fields[5]),
                        'volume': int(fields[8]),
                        'amount': float(fields[9]),
                    }
        return result
    except Exception as e:
        print(f"获取股票数据失败: {e}", file=sys.stderr)
        return {}

def fetch_index_data():
    """获取大盘指数数据"""
    result = {}
    for name, code in MARKET_INDICES.items():
        try:
            url = f"https://hq.sinajs.cn/list={code}"
            req = urllib.request.Request(url)
            req.add_header('Referer', 'https://finance.sina.com.cn')
            response = urllib.request.urlopen(req, timeout=10)
            data = response.read().decode('gb2312', errors='ignore')
            
            match = re.search(r'var hq_str_\w+="([^"]*)"', data)
            if match:
                fields = match.group(1).split(',')
                if len(fields) >= 5:
                    current = float(fields[1])
                    yesterday = float(fields[2])
                    change = current - yesterday
                    change_pct = (change / yesterday * 100) if yesterday > 0 else 0
                    result[name] = {
                        'price': current,
                        'change': change,
                        'change_pct': change_pct,
                    }
        except Exception:
            pass
    return result

def generate_simple_report():
    """生成简化版报告"""
    lines = []
    now = datetime.now()
    
    # 标题
    lines.append("=" * 60)
    lines.append(f"📊 自选股日报 - {now.strftime('%Y年%m月%d日 %H:%M')}")
    lines.append("=" * 60)
    lines.append("")
    
    # 大盘指数
    lines.append("【大盘指数】")
    index_data = fetch_index_data()
    for name, data in index_data.items():
        emoji = "🔴" if data['change'] > 0 else "🟢"
        lines.append(f"  {emoji} {name}: {data['price']:.2f} ({data['change']:+.2f}, {data['change_pct']:+.2f}%)")
    lines.append("")
    
    # 自选股
    lines.append("【自选股表现】")
    stock_data = fetch_stock_data()
    
    if not stock_data:
        lines.append("  ❌ 数据获取失败")
    else:
        # 计算涨跌幅并排序
        stocks = []
        for code, name, industry in WATCHLIST:
            if code in stock_data:
                s = stock_data[code]
                change = s['price'] - s['yesterday']
                change_pct = (change / s['yesterday'] * 100) if s['yesterday'] > 0 else 0
                stocks.append({
                    'code': code,
                    'name': name,
                    'industry': industry,
                    'price': s['price'],
                    'change': change,
                    'change_pct': change_pct,
                    'amount': s['amount'] / 100000000,  # 转为亿元
                })
        
        # 按涨跌幅排序
        stocks.sort(key=lambda x: x['change_pct'], reverse=True)
        
        lines.append(f"{'名称':<8} {'代码':<8} {'现价':>8} {'涨跌':>8} {'涨幅':>8} {'成交额':>8}")
        lines.append("-" * 60)
        
        for s in stocks:
            emoji = "🔴" if s['change_pct'] > 0 else "🟢"
            lines.append(
                f"{emoji}{s['name']:<7} {s['code']:<8} "
                f"{s['price']:>8.2f} {s['change']:>+8.2f} {s['change_pct']:>+7.2f}% {s['amount']:>7.2f}亿"
            )
    
    lines.append("")
    lines.append("=" * 60)
    lines.append("💡 提示: 详细分析请使用 stock_analyzer_pro.py")
    lines.append("=" * 60)
    
    return '\n'.join(lines)

def send_to_feishu(message: str):
    """通过 feishu-notify.sh 脚本发送飞书消息"""
    try:
        notify_script = "/Users/zhaoruicn/.openclaw/workspace/scripts/feishu-notify.sh"
        
        # 设置环境变量
        env = os.environ.copy()
        env['PATH'] = '/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin'
        env['HOME'] = '/Users/zhaoruicn'
        
        # 分段发送（飞书消息长度限制）
        max_len = 3000
        if len(message) > max_len:
            message = message[:max_len] + "\n\n...(报告较长，已截断)"
        
        # 使用脚本发送消息
        result = subprocess.run(
            [notify_script, "send", message],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        
        if result.returncode != 0:
            print(f"脚本错误: {result.stderr}", file=sys.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"发送失败: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    try:
        print("生成股票报告...", file=sys.stderr)
        report = generate_simple_report()
        
        print("发送飞书消息...", file=sys.stderr)
        success = send_to_feishu(report)
        
        if success:
            print("✅ 飞书推送成功", file=sys.stderr)
        else:
            print("❌ 飞书推送失败", file=sys.stderr)
            # 保存到文件
            with open('/tmp/stock_report_simple.txt', 'w') as f:
                f.write(report)
            print("报告已保存到 /tmp/stock_report_simple.txt", file=sys.stderr)
    except Exception as e:
        print(f"执行失败: {e}", file=sys.stderr)
        sys.exit(1)
