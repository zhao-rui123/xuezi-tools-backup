#!/usr/bin/env python3
"""
股票报告推送脚本
- 16:30 自选股报告（完整技术指标）
- 20:00 MACD+KDJ金叉筛选
"""
import subprocess
import json
import sys
import os
from datetime import datetime

API_KEY = "mkt_zdTwvCWmIr9g4mHoM8sOsaK8M_ffrhinQPP-GAkhTNs"

def curl_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    try:
        return json.loads(result.stdout)
    except:
        return {}

def get_selfselect():
    cmd = f"""curl -s -X POST 'https://mkapi2.dfcfs.com/finskillshub/api/claw/self-select/get' \
  -H 'Content-Type: application/json' \
  -H 'apikey: {API_KEY}' \
  --data '{{"query": "查询我的自选股列表"}}'"""
    return curl_cmd(cmd)

def get_stock_pattern(code: str):
    """查询股票K线形态"""
    cmd = f"""curl -s -X POST 'https://mkapi2.dfcfs.com/finskillshub/api/claw/stock-screen' \
  -H 'Content-Type: application/json' \
  -H 'apikey: {API_KEY}' \
  --data '{{"keyword": "{code}K线形态", "pageNo": 1, "pageSize": 5}}'"""
    data = curl_cmd(cmd)
    if data.get('status') == 0:
        return data.get('data', {}).get('data', {}).get('responseConditionList', [])
    return []

def screen_stocks(keyword: str):
    cmd = f"""curl -s -X POST 'https://mkapi2.dfcfs.com/finskillshub/api/claw/stock-screen' \
  -H 'Content-Type: application/json' \
  -H 'apikey: {API_KEY}' \
  --data '{{"keyword": "{keyword}", "pageNo": 1, "pageSize": 20}}'"""
    return curl_cmd(cmd)

def parse_selfselect(data):
    """解析自选股数据 - 完整版（含K线形态）"""
    try:
        rows = data.get('data', {}).get('allResults', {}).get('result', {}).get('dataList', [])
    except:
        rows = []
    results = []
    for s in rows:
        results.append({
            'code': s.get('SECURITY_CODE', ''),
            'name': s.get('SECURITY_SHORT_NAME', ''),
            'price': s.get('NEWEST_PRICE', ''),
            'pchg': s.get('PCHG', ''),      # 涨跌额
            'chg': s.get('CHG', ''),         # 涨跌幅%
            'turnover': s.get('010000_TURNOVER_RATE<70>{2026-03-13}', ''),
            'volume': s.get('010000_VOLUME<70>{2026-03-13}', ''),
            'amount': s.get('010000_TRADING_VOLUMES<70>{2026-03-13}', ''),
            'pe': s.get('010000_PE_D{2026-03-13}', ''),
            'pb': s.get('010000_PB<70>{2026-03-13}', ''),
            'macd': s.get('010000_MACDJC<70>{2026-03-13}', ''),
            'kdj': s.get('010000_KDJJ<70>{2026-03-13}', ''),
            '形态': '待查询',  # K线形态需单独接口
        })
    return results

def parse_screen(data):
    if not data or data.get('status') != 0:
        return []
    try:
        text = data.get('data', {}).get('data', {}).get('partialResults', '')
    except:
        text = ''
    results = []
    for line in text.split('\n'):
        if '|' in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 3 and parts[0].isdigit():
                results.append(f"{parts[0]}. {parts[1]} {parts[2]}")
    return results

def send_to_feishu(message: str):
    """发送消息到飞书 - 使用直接HTTP API调用"""
    import urllib.request
    import urllib.parse
    
    # 使用飞书机器人API直接发送
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/"  # 需要替换为实际的webhook
    
    # 尝试使用openclaw命令，如果失败则使用替代方案
    try:
        # 先尝试使用完整路径的openclaw
        openclaw_path = "/opt/homebrew/bin/openclaw"
        if os.path.exists(openclaw_path):
            # 使用后台运行，避免超时
            subprocess.Popen(
                [openclaw_path, "message", "send", "--target", "oc_b14195eb990ab57ea573e696758ae3d5", "--message", message],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return True
        else:
            # 尝试PATH中的openclaw，后台运行
            subprocess.Popen(
                ["openclaw", "message", "send", "--target", "oc_b14195eb990ab57ea573e696758ae3d5", "--message", message],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True
            )
            return True
    except Exception as e:
        print(f"发送失败: {e}")
        return False

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 股票报告模式: {mode}")
    
    msg = f"📊 股票日报 ({datetime.now().strftime('%Y-%m-%d')})\n\n"
    
    # 16:30 自选股报告 - 完整技术指标版（含K线形态）
    if mode in ["selfselect", "all"]:
        print("获取自选股数据...")
        data = get_selfselect()
        stocks = parse_selfselect(data)
        
        # 查询K线形态（可选，比较耗时）
        if stocks and mode == "selfselect":
            print("查询K线形态...")
            for s in stocks[:6]:  # 限制数量
                patterns = get_stock_pattern(s['code'])
                if patterns:
                    s['形态'] = ", ".join([p.get('describe', '')[:10] for p in patterns[:2]])
        
        if stocks:
            msg += "⭐ 我的自选股 ({len(stocks)}只) - 技术指标+K线形态\n"
            msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            msg += "| 代码 | 名称 | 价格 | 涨跌% | 换手% | MACD | KDJ | 形态 |\n"
            msg += "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n"
            for s in stocks:
                # 涨跌幅
                try:
                    chg_val = float(s['chg']) if s['chg'] else 0
                except:
                    chg_val = 0
                emoji = "🔴" if chg_val > 0 else "🟢" if chg_val < 0 else "⚪"
                
                # 技术指标
                macd = "✅" if s.get('macd') == '符合' else "❌"
                kdj = "✅" if s.get('kdj') == '符合' else "❌"
                
                # K线形态 - 需要单独查询（暂显示待查询）
                形态 = s.get('形态', '-')
                
                msg += f"| {s['code']} | {s['name']} | {s['price']} | {emoji}{s['chg']}% | {s['turnover']}% | {macd} | {kdj} | {形态} |\n"
            
            msg += "\n📈 详细数据\n"
            msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for s in stocks:
                msg += f"**{s['code']} {s['name']}**\n"
                msg += f"  价格: {s['price']} | 涨跌: {s['chg']}% | 成交额: {s.get('amount', '-')}\n"
                msg += f"  换手: {s['turnover']}% | 量比: {s.get('volume', '-')} | 市盈率: {s.get('pe', '-')} | 市净率: {s.get('pb', '-')}\n"
                msg += f"  MACD: {macd} | KDJ: {kdj}\n\n"
        else:
            msg += "⭐ 自选股: 无\n\n"
    
    # 20:00 MACD+KDJ筛选
    if mode in ["screen", "all"]:
        print("筛选MACD+KDJ金叉...")
        weekly_data = screen_stocks("周线MACD金叉且KDJ金叉且放量且非近期强势股")
        monthly_data = screen_stocks("月线MACD金叉且KDJ金叉且放量")
        
        weekly_results = parse_screen(weekly_data)
        monthly_results = parse_screen(monthly_data)
        
        weekly_count = len(weekly_results)
        monthly_count = len(monthly_results)
        
        msg += f"🌙 月线MACD+KDJ金叉: {monthly_count}只\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for r in monthly_results[:10]:
            msg += r + "\n"
        msg += f"\n📅 周线MACD+KDJ金叉: {weekly_count}只\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for r in weekly_results[:15]:
            msg += r + "\n"
    
    print(msg)
    
    if send_to_feishu(msg):
        print("发送成功!")
    else:
        print("发送失败")

if __name__ == "__main__":
    main()
