#!/usr/bin/env python3
"""
自选股每日分析器 - 使用新浪财经免费API
作者: 雪子助手
"""

import urllib.request
import json
import re
from datetime import datetime
from typing import Dict, List, Tuple

# 自选股列表
WATCHLIST = [
    ("002738", "中矿资源", "锂矿/资源"),
    ("002460", "赣锋锂业", "锂电池/新能源"),
    ("000792", "盐湖股份", "盐湖提锂"),
    ("002240", "盛新锂能", "锂电池材料"),
    ("688411", "海博思创", "储能系统"),
    ("000725", "京东方A", "面板/显示"),
    ("600707", "彩虹股份", "面板/显示"),
]

def fetch_sina_data(codes: List[str]) -> Dict:
    """从新浪财经获取实时数据"""
    # 构建代码字符串
    code_str = ",".join([
        f"sz{c}" if c.startswith(("0", "3")) else f"sh{c}"
        for c in codes
    ])
    
    url = f"https://hq.sinajs.cn/list={code_str}"
    
    try:
        req = urllib.request.Request(url)
        req.add_header('Referer', 'https://finance.sina.com.cn')
        response = urllib.request.urlopen(req, timeout=10)
        data = response.read().decode('gb2312', errors='ignore')
        return parse_sina_data(data)
    except Exception as e:
        print(f"获取数据失败: {e}")
        return {}

def parse_sina_data(data: str) -> Dict:
    """解析新浪返回的数据"""
    result = {}
    
    for line in data.strip().split('\n'):
        match = re.search(r'var hq_str_(\w+)="([^"]*)"', line)
        if match:
            code_key = match.group(1)  # sz002738
            code = code_key[2:]  # 002738
            fields = match.group(2).split(',')
            
            if len(fields) >= 33:
                result[code] = {
                    'name': fields[0],
                    'open': float(fields[1]),
                    'yesterday_close': float(fields[2]),
                    'price': float(fields[3]),
                    'high': float(fields[4]),
                    'low': float(fields[5]),
                    'volume': int(float(fields[8])),  # 股数
                    'amount': float(fields[9]),  # 成交金额
                    'bid1_price': float(fields[11]),
                    'ask1_price': float(fields[21]),
                    'date': fields[30],
                    'time': fields[31],
                }
    
    return result

def calculate_metrics(stock: Dict) -> Dict:
    """计算衍生指标"""
    price = stock['price']
    yc = stock['yesterday_close']
    
    change = price - yc
    change_pct = (change / yc) * 100 if yc > 0 else 0
    amplitude = ((stock['high'] - stock['low']) / yc) * 100 if yc > 0 else 0
    volume_wan = stock['volume'] / 10000  # 万股
    amount_yi = stock['amount'] / 100000000  # 亿元
    
    return {
        'change': change,
        'change_pct': change_pct,
        'amplitude': amplitude,
        'volume_wan': volume_wan,
        'amount_yi': amount_yi,
    }

def get_industry_analysis(industry: str, change_pct: float) -> str:
    """根据行业和涨跌给出分析"""
    analyses = {
        '锂矿/资源': {
            'up': '碳酸锂价格企稳，资源端受益',
            'down': '锂价承压或需求预期下调',
        },
        '锂电池/新能源': {
            'up': '新能源车销量超预期或订单饱满',
            'down': '产业链价格战或需求疲软',
        },
        '盐湖提锂': {
            'up': '成本优势凸显，产能释放',
            'down': '锂价下跌影响盈利预期',
        },
        '锂电池材料': {
            'up': '原材料成本下降或产能利用率提升',
            'down': '加工费下滑或下游压价',
        },
        '储能系统': {
            'up': '储能装机量高增长，政策利好',
            'down': '行业竞争加剧或项目延期',
        },
        '面板/显示': {
            'up': '面板涨价或产能利用率提升',
            'down': '需求疲软或价格持续低迷',
        },
    }
    
    industry_key = industry.split('/')[0]
    for key in analyses:
        if key in industry or industry in key:
            direction = 'up' if change_pct > 0 else 'down'
            return analyses[key][direction]
    
    return '跟随板块波动'

def generate_report() -> str:
    """生成完整分析报告"""
    codes = [s[0] for s in WATCHLIST]
    data = fetch_sina_data(codes)
    
    if not data:
        return "❌ 数据获取失败"
    
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append(f"📊 自选股日报 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report_lines.append("=" * 70)
    report_lines.append("")
    
    # 汇总统计
    stocks_with_data = []
    total_change_pct = 0
    up_count = 0
    down_count = 0
    
    for code, name, industry in WATCHLIST:
        if code in data:
            stock = data[code]
            metrics = calculate_metrics(stock)
            total_change_pct += metrics['change_pct']
            if metrics['change_pct'] > 0:
                up_count += 1
            elif metrics['change_pct'] < 0:
                down_count += 1
            
            stocks_with_data.append({
                'code': code,
                'name': name,
                'industry': industry,
                'stock': stock,
                'metrics': metrics,
            })
    
    # 排序（按涨跌幅）
    stocks_with_data.sort(key=lambda x: x['metrics']['change_pct'], reverse=True)
    
    avg_change = total_change_pct / len(stocks_with_data) if stocks_with_data else 0
    
    report_lines.append(f"【市场概况】")
    report_lines.append(f"  上涨: {up_count}只  |  平盘: {len(stocks_with_data)-up_count-down_count}只  |  下跌: {down_count}只")
    report_lines.append(f"  平均涨跌幅: {avg_change:+.2f}%")
    report_lines.append("")
    
    # 个股详情
    report_lines.append("【个股表现】")
    report_lines.append("-" * 70)
    report_lines.append(f"{'排名':<4} {'名称':<8} {'代码':<8} {'现价':>8} {'涨跌':>8} {'涨幅':>8} {'振幅':>6}")
    report_lines.append("-" * 70)
    
    for i, item in enumerate(stocks_with_data, 1):
        s = item['stock']
        m = item['metrics']
        emoji = "🟢" if m['change_pct'] > 0 else "🔴" if m['change_pct'] < 0 else "⚪"
        
        report_lines.append(
            f"{emoji}{i:<3} {item['name']:<8} {item['code']:<8} "
            f"{s['price']:>8.2f} {m['change']:>+8.2f} {m['change_pct']:>+7.2f}% {m['amplitude']:>5.2f}%"
        )
    
    report_lines.append("-" * 70)
    report_lines.append("")
    
    # 板块分析
    report_lines.append("【板块分析】")
    industries = {}
    for item in stocks_with_data:
        ind = item['industry'].split('/')[0]
        if ind not in industries:
            industries[ind] = []
        industries[ind].append(item['metrics']['change_pct'])
    
    for ind, changes in industries.items():
        avg = sum(changes) / len(changes)
        report_lines.append(f"  {ind}: 平均 {avg:+.2f}% ({len(changes)}只)")
    
    report_lines.append("")
    
    # 异动分析
    report_lines.append("【异动解读】")
    for item in stocks_with_data:
        m = item['metrics']
        if abs(m['change_pct']) > 3:  # 涨跌幅超过3%
            analysis = get_industry_analysis(item['industry'], m['change_pct'])
            direction = "大涨" if m['change_pct'] > 0 else "大跌"
            report_lines.append(f"  {item['name']} {direction} {abs(m['change_pct']):.2f}%: {analysis}")
    
    report_lines.append("")
    report_lines.append("=" * 70)
    report_lines.append("数据来源: 新浪财经 | 更新时间: " + datetime.now().strftime('%H:%M:%S'))
    report_lines.append("=" * 70)
    
    return '\n'.join(report_lines)

if __name__ == "__main__":
    print(generate_report())
