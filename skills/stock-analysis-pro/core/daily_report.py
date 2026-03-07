"""
日报生成模块
整合所有分析功能生成完整日报
"""

import sys
import subprocess
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace/skills/stock-analysis-pro')

from config.xueqiu_config import XUEQIU_HEADERS, XUEQIU_COOKIES, FEISHU_USER_ID, MARKET_INDICES
from config.watchlist import WATCHLIST
from core.data_fetcher import fetch_sina_data, fetch_xueqiu_data, fetch_tencent_kline, fetch_market_index
from core.pattern_recognition import analyze_patterns, format_pattern_report
from core.valuation import analyze_valuation, format_valuation_report

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

def generate_daily_report() -> str:
    """生成日报"""
    codes = [s[0] for s in WATCHLIST]
    
    # 获取数据
    sina_data = fetch_sina_data(codes)
    xueqiu_data = fetch_xueqiu_data(codes, XUEQIU_HEADERS, XUEQIU_COOKIES)
    
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
    
    # 自选股基本面
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
    
    # 技术形态识别
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
    
    # 估值策略筛选
    lines.append("")
    lines.append("【估值策略筛选】")
    codes_only = [s[0] for s in WATCHLIST]
    try:
        val_results = analyze_valuation(codes_only, XUEQIU_HEADERS, XUEQIU_COOKIES)
        
        if val_results.get('pb_roe'):
            lines.append("🏆 PB-ROE策略:")
            for i, r in enumerate(val_results['pb_roe'][:3]):
                lines.append(f"   {i+1}. {r.description}")
        
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

def send_to_feishu(message: str) -> bool:
    """发送消息到飞书"""
    env = {
        'PATH': '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin',
    }
    
    try:
        result = subprocess.run(
            ['openclaw', 'message', 'send', '--target', FEISHU_USER_ID, '--message', message],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        if result.returncode == 0:
            print("✅ 飞书消息发送成功")
            return True
        else:
            print(f"❌ 发送失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False

if __name__ == "__main__":
    print("生成自选股日报...")
    report = generate_daily_report()
    print(report)
    print("\n" + "="*50)
    print("发送到飞书...")
    send_to_feishu(report)
