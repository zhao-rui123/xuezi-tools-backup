#!/usr/bin/env python3
"""
自选股飞书推送 - 新浪财经 + 雪球融合版
定时任务调用，生成并推送详细股票报告
"""

import os
import sys
import json
import subprocess
import urllib.request
import re
from datetime import datetime

# 尝试导入requests，如果失败则使用urllib替代
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("⚠️ requests模块未安装，使用urllib替代")

# 导入新模块
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace')
from stock_pattern_recognition import analyze_patterns, format_pattern_report
from stock_valuation_screener import analyze_valuation, format_valuation_report
from stock_deep_analysis import deep_analyze_stock, format_deep_analysis

# 添加workspace到路径
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace')

# ============ 飞书配置 ============
FEISHU_USER_ID = "ou_5a7b7ec0339ffe0c1d5bb6c5bc162579"

# ============ 雪球API配置 ============
XUEQIU_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'origin': 'https://xueqiu.com',
    'priority': 'u=1, i',
    'referer': 'https://xueqiu.com/',
    'sec-ch-ua': '"Not:A-Brand";v="99", "Microsoft Edge";v="145", "Chromium";v="145"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0',
}

XUEQIU_COOKIES = {
    'cookiesu': '841772842781365',
    'device_id': 'd30532eeec1ab76c3eb0cbcd787c258d',
    'xq_a_token': '8661982e927e023bf957bbc24b6fe85211ed4348',
    'xqat': '8661982e927e023bf957bbc24b6fe85211ed4348',
    'xq_r_token': 'a48ce0f397b2c32744404a9e435a0ab6f0b9ba59',
    'xq_id_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjM0NDE2NzY4MjYsImlzcyI6InVjIiwiZXhwIjoxNzc1NDM0ODI0LCJjdG0iOjE3NzI4NDI4MjQ3MTQsImNpZCI6ImQ5ZDBuNEFadXAifQ.R8VRuz4gcsPrDv5jFU1c9WJYmulgC33sxR5Pkig9CRB-JZU4R--VkM9_mZjuKmx7g8SsJURq4UH5za6Qe9ey4RRtlKst1iL-2bKfX1_c5hxG9x6bHugx62zSlIJKYvqnPLwQ_rzgVH7daq11lfOoCya6LlOLZKffCgUiNzOlYSJTd9-m5Vf8ESs6kw1Nmh6lSEvbYym0VuvoN0YPiap9FlgLKUkuWLf9PJvo0Lfa6FoTAO6uMLTWYzUTSsTccTzF3xWUHb-ZBQY8kU72ZeDtXt_JzTYOov6ylbCOUSXPi4pY0_qZud_B71yFapuKheKbgMMZk2qPXZkbFgLHJJntXQ',
    'xq_is_login': '1',
    'u': '3441676826',
}

# ============ 股票配置 ============
WATCHLIST = [
    ("002594", "比亚迪", "新能源汽车"),
    ("002460", "赣锋锂业", "锂电池/新能源"),
    ("002240", "盛新锂能", "锂电池材料"),
    ("600707", "彩虹股份", "面板/显示"),
    ("000725", "京东方A", "面板/显示"),
    ("000688", "国城矿业", "有色金属"),
    ("08174", "比亚迪", "港股/新能源汽车"),
    ("01772", "赣锋锂业", "港股/锂电池"),
]

MARKET_INDICES = {
    "上证指数": "sh000001",
    "深证成指": "sz399001",
    "创业板指": "sz399006",
}

def is_hk_stock(code):
    """判断是否为港股代码"""
    # 港股代码是5位数且以0开头
    return len(code) == 5 and code.startswith(('0', '1', '2', '3', '6', '8'))

def fetch_sina_data(codes):
    """获取新浪财经数据"""
    # 分离A股和港股
    a_codes = [c for c in codes if not is_hk_stock(c)]
    hk_codes = [c for c in codes if is_hk_stock(c)]
    
    result = {}
    
    # 获取A股数据
    if a_codes:
        code_str = ",".join([f"sz{c}" if c.startswith(("0", "3")) else f"sh{c}" for c in a_codes])
        url = f"https://hq.sinajs.cn/list={code_str}"
        
        try:
            req = urllib.request.Request(url)
            req.add_header('Referer', 'https://finance.sina.com.cn')
            response = urllib.request.urlopen(req, timeout=10)
            data = response.read().decode('gb2312', errors='ignore')
            
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
                        }
        except Exception as e:
            print(f"新浪A股API错误: {e}")
    
    # 获取港股数据
    if hk_codes:
        hk_code_str = ",".join([f"rt_hk{c}" for c in hk_codes])
        url = f"https://hq.sinajs.cn/list={hk_code_str}"
        
        try:
            req = urllib.request.Request(url)
            req.add_header('Referer', 'https://finance.sina.com.cn')
            response = urllib.request.urlopen(req, timeout=10)
            data = response.read().decode('gb2312', errors='ignore')
            
            for line in data.strip().split('\n'):
                match = re.search(r'var hq_str_rt_hk(\w+)="([^"]*)"', line)
                if match:
                    code = match.group(1)
                    fields = match.group(2).split(',')
                    if len(fields) >= 7:
                        # 港股格式: 英文名称,中文名称,开盘价,昨收,最高价,最低价,最新价...
                        result[code] = {
                            'name': fields[1] if fields[1] else fields[0],
                            'price': float(fields[6]) if fields[6] else 0,
                            'yesterday': float(fields[3]) if fields[3] else 0,
                        }
        except Exception as e:
            print(f"新浪港股API错误: {e}")
    
    return result

def fetch_xueqiu_data(codes):
    """获取雪球数据"""
    symbols = []
    for c in codes:
        if is_hk_stock(c):
            # 港股直接传入代码
            symbols.append(c)
        elif c.startswith('6'):
            symbols.append(f'SH{c}')
        else:
            symbols.append(f'SZ{c}')
    
    symbol_str = ','.join(symbols)
    url = f"https://stock.xueqiu.com/v5/stock/batch/quote.json?symbol={symbol_str}&extend=detail&is_delay_hk=false"
    
    try:
        if HAS_REQUESTS:
            response = requests.get(url, headers=XUEQIU_HEADERS, cookies=XUEQIU_COOKIES, timeout=15)
            if response.status_code == 200:
                data = response.json()
            else:
                print(f"雪球API返回错误状态码: {response.status_code}")
                return {}
        else:
            # 使用urllib替代
            req = urllib.request.Request(url, headers=XUEQIU_HEADERS)
            # 添加cookies
            cookie_str = '; '.join([f"{k}={v}" for k, v in XUEQIU_COOKIES.items()])
            req.add_header('Cookie', cookie_str)
            response = urllib.request.urlopen(req, timeout=15)
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
            else:
                print(f"雪球API返回错误状态码: {response.status}")
                return {}
        
        # 解析数据
        result = {}
        for item in data.get('data', {}).get('items', []):
            quote = item.get('quote', {})
            code = quote.get('code', '')
            # 港股code就是纯数字，A股有SH/SZ前缀
            if code.startswith(('SZ', 'SH')):
                code = code[2:]
            if code:
                result[code] = {
                    'name': quote.get('name'),
                    'current': quote.get('current'),
                    'percent': quote.get('percent', 0),
                    'pe_ttm': quote.get('pe_ttm'),
                    'pb': quote.get('pb'),
                    'turnover_rate': quote.get('turnover_rate'),
                    'volume_ratio': quote.get('volume_ratio'),
                    'high52w': quote.get('high52w'),
                    'low52w': quote.get('low52w'),
                }
        return result
    except Exception as e:
        print(f"雪球API错误: {e}")
    return {}

def fetch_market_index(index_code):
    """获取大盘指数"""
    try:
        url = f"https://hq.sinajs.cn/list={index_code}"
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
                change_pct = ((current - yesterday) / yesterday * 100) if yesterday > 0 else 0
                return {'price': current, 'change_pct': change_pct}
    except Exception:
        pass
    return None

def fetch_tencent_kline(stock_code):
    """从腾讯财经获取K线数据并计算技术指标"""
    try:
        # 转换代码格式
        if is_hk_stock(stock_code):
            # 港股格式: hk00981
            tencent_code = f"hk{stock_code}"
        elif stock_code.startswith('6') or stock_code.startswith('688'):
            tencent_code = f"sh{stock_code}"
        elif stock_code.startswith(('0', '3')):
            tencent_code = f"sz{stock_code}"
        else:
            return None
        
        # 获取最近60天日线数据
        url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={tencent_code},day,,,60,qfq"
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        # 解析数据 - A股用qfqday，港股用day
        kline_key = f"{tencent_code}"
        if kline_key not in data.get('data', {}):
            return None
        
        stock_data = data['data'][kline_key]
        # A股前复权数据
        kline_data = stock_data.get('qfqday', [])
        # 如果没有qfqday，尝试day（港股）
        if not kline_data:
            kline_data = stock_data.get('day', [])
        
        if len(kline_data) < 20:
            return None
        
        # 提取收盘价 - 格式不同：
        # A股 qfqday: [日期, 开盘, 收盘, 最低, 最高, 成交量]
        # 港股 day: [日期, 开盘, 收盘, 最高, 最低, 成交量]
        # 都是索引2为收盘价
        closes = [float(day[2]) for day in kline_data]
        
        # 计算均线
        ma5 = sum(closes[-5:]) / 5
        ma10 = sum(closes[-10:]) / 10
        ma20 = sum(closes[-20:]) / 20
        current_price = closes[-1]
        
        # 判断趋势
        if current_price > ma5 > ma10 > ma20:
            trend = "多头"
            trend_emoji = "📈"
        elif current_price < ma5 < ma10 < ma20:
            trend = "空头"
            trend_emoji = "📉"
        else:
            trend = "震荡"
            trend_emoji = "↔️"
        
        # 计算RSI (14日)
        rsi = 50
        if len(closes) >= 15:
            deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
            gains = [d if d > 0 else 0 for d in deltas[-14:]]
            losses = [-d if d < 0 else 0 for d in deltas[-14:]]
            avg_gain = sum(gains) / 14
            avg_loss = sum(losses) / 14
            if avg_loss > 0:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
        
        # RSI状态
        if rsi > 70:
            rsi_status = "超买"
        elif rsi < 30:
            rsi_status = "超卖"
        else:
            rsi_status = "正常"
        
        # 计算偏离度（当前价与MA20的偏离）
        deviation = ((current_price - ma20) / ma20 * 100) if ma20 > 0 else 0
        
        return {
            'ma5': ma5,
            'ma10': ma10,
            'ma20': ma20,
            'trend': trend,
            'trend_emoji': trend_emoji,
            'rsi': rsi,
            'rsi_status': rsi_status,
            'deviation': deviation,
        }
    except Exception as e:
        print(f"腾讯K线获取失败 {stock_code}: {e}")
    return None

def get_valuation_label(pe):
    """获取估值标签"""
    if pe is None:
        return "N/A"
    if pe < 0:
        return "亏损"
    elif pe < 15:
        return "低估"
    elif pe < 30:
        return "合理"
    elif pe < 50:
        return "偏高"
    else:
        return "高估"

def generate_report():
    """生成报告"""
    codes = [s[0] for s in WATCHLIST]
    
    # 获取数据
    sina_data = fetch_sina_data(codes)
    xueqiu_data = fetch_xueqiu_data(codes)
    
    # 构建报告
    lines = []
    lines.append("📊 自选股日报 - " + datetime.now().strftime('%Y-%m-%d %H:%M'))
    lines.append("")
    
    # 大盘指数
    lines.append("【大盘指数】")
    for name, code in MARKET_INDICES.items():
        index = fetch_market_index(code)
        if index:
            emoji = "🔴" if index['change_pct'] > 0 else "🟢"
            lines.append(f"{emoji} {name}: {index['price']:.2f} ({index['change_pct']:+.2f}%)")
    lines.append("")
    
    # 自选股 - 基本面数据
    lines.append("【自选股 - 基本面】")
    total_change = 0
    stock_data = []
    
    for code, name, sector in WATCHLIST:
        xq = xueqiu_data.get(code, {})
        percent = xq.get('percent', 0)
        total_change += percent
        
        pe = xq.get('pe_ttm')
        pb = xq.get('pb')
        turnover = xq.get('turnover_rate')
        
        # 计算52周位置
        position = None
        if xq.get('high52w') and xq.get('low52w') and xq.get('current'):
            position = (xq['current'] - xq['low52w']) / (xq['high52w'] - xq['low52w']) * 100
        
        stock_data.append({
            'name': name,
            'code': code,
            'percent': percent,
            'pe': pe,
            'pb': pb,
            'turnover': turnover,
            'position': position,
        })
        
        emoji = "🔴" if percent > 0 else "🟢" if percent < 0 else "⚪"
        pe_str = f"{pe:.1f}" if pe else "N/A"
        pb_str = f"{pb:.2f}" if pb else "N/A"
        turnover_str = f"{turnover:.1f}%" if turnover else "N/A"
        pos_str = f"{position:.0f}%" if position else "N/A"
        valuation = get_valuation_label(pe)
        
        lines.append(f"{emoji} {name} ({code}) {percent:+.2f}%")
        lines.append(f"   PE:{pe_str}({valuation}) PB:{pb_str} 换手:{turnover_str} 52周:{pos_str}")
    
    # 技术指标板块
    lines.append("")
    lines.append("【技术分析 - 日线指标】")
    
    for code, name, sector in WATCHLIST:
        tech = fetch_tencent_kline(code)
        if tech:
            emoji = tech['trend_emoji']
            rsi_emoji = "🔥" if tech['rsi'] > 70 else "❄️" if tech['rsi'] < 30 else "➖"
            dev_emoji = "📈" if tech['deviation'] > 5 else "📉" if tech['deviation'] < -5 else "➖"
            
            lines.append(f"{emoji} {name}: {tech['trend']}趋势")
            lines.append(f"   MA5:{tech['ma5']:.2f} MA10:{tech['ma10']:.2f} MA20:{tech['ma20']:.2f}")
            lines.append(f"   {rsi_emoji} RSI:{tech['rsi']:.1f}({tech['rsi_status']}) {dev_emoji} 偏离MA20:{tech['deviation']:+.1f}%")
        else:
            lines.append(f"⚪ {name}: 技术指标暂不可用")
    
    # 技术形态识别（新增）
    lines.append("")
    lines.append("【技术形态识别】")
    pattern_found = False
    for code, name, sector in WATCHLIST:
        pattern = analyze_patterns(code, name)
        if pattern and pattern.confidence >= 60:
            pattern_found = True
            emoji = "📐" if pattern.direction == "bullish" else "📉"
            lines.append(f"{emoji} {name}: {pattern.pattern_name} ({pattern.confidence}%)")
            lines.append(f"   {pattern.suggestion}")
    if not pattern_found:
        lines.append("   暂无明确技术形态信号")
    
    # 估值策略筛选（新增）
    lines.append("")
    lines.append("【估值策略筛选】")
    codes_only = [s[0] for s in WATCHLIST]
    names_dict = {s[0]: s[1] for s in WATCHLIST}
    try:
        val_results = analyze_valuation(codes_only)
        
        # PB-ROE前3
        if val_results.get('pb_roe'):
            lines.append("🏆 PB-ROE策略:")
            for i, r in enumerate(val_results['pb_roe'][:3]):
                lines.append(f"   {i+1}. {r.description}")
        
        # 综合评分前3
        if val_results.get('comprehensive'):
            lines.append("📊 综合估值:")
            for i, r in enumerate(val_results['comprehensive'][:3]):
                lines.append(f"   {i+1}. 得分{r.score} - {r.description}")
    except Exception as e:
        lines.append(f"   估值分析暂不可用")
    
    # 统计
    avg_change = total_change / len(WATCHLIST)
    lines.append("")
    lines.append("【统计】")
    lines.append(f"组合平均: {avg_change:+.2f}%")
    
    sorted_stocks = sorted(stock_data, key=lambda x: x['percent'], reverse=True)
    lines.append(f"🏆 最强: {sorted_stocks[0]['name']} ({sorted_stocks[0]['percent']:+.2f}%)")
    lines.append(f"📉 最弱: {sorted_stocks[-1]['name']} ({sorted_stocks[-1]['percent']:+.2f}%)")
    
    return "\n".join(lines)

def send_to_feishu(message):
    """发送消息到飞书 - 使用openclaw CLI"""
    import subprocess
    import os
    
    # 保存报告到临时文件
    report_file = f"/tmp/stock_report_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(message)
    
    try:
        # 使用openclaw CLI直接发送
        env = os.environ.copy()
        env['PATH'] = '/opt/homebrew/bin:' + env.get('PATH', '')
        
        result = subprocess.run(
            ['openclaw', 'message', 'send', '--channel', 'feishu',
             '--target', 'ou_5a7b7ec0339ffe0c1d5bb6c5bc162579',
             '--message', message],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        if result.returncode == 0:
            print("✅ 股票报告已发送")
            return True
        else:
            print(f"❌ 发送失败: {result.stderr}")
            # 尝试使用message工具
            return send_via_message_tool(message)
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return send_via_message_tool(message)

def send_via_message_tool(message):
    """备用发送方式"""
    try:
        # 将消息写入文件，通过文件发送
        report_file = f"/tmp/stock_report_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(message)
        print(f"✅ 报告已保存到: {report_file}")
        print("请手动查看或使用openclaw message send --media发送")
        return True
    except Exception as e:
        print(f"❌ 备用发送也失败: {e}")
        return False

if __name__ == "__main__":
    print("生成自选股日报...")
    report = generate_report()
    print(report)
    print("\n" + "="*50)
    print("发送到飞书...")
    send_to_feishu(report)
