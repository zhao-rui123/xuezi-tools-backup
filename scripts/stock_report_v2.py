#!/usr/bin/env python3
"""
股票报告推送脚本 v2
- 16:30 自选股报告（完整技术指标）- 云服务器版本
- 20:00 MACD+KDJ金叉筛选

使用云服务器获取数据：
ssh -i ~/.ssh/id_ed25519 root@106.54.25.161 "python3 /tmp/stock_technical_analysis.py [代码]"
"""
import subprocess
import json
import sys
import os
from datetime import datetime

API_KEY = "mkt_zdTwvCWmIr9g4mHoM8sOsaK8M_ffrhinQPP-GAkhTNs"

# 云服务器连接信息
CLOUD_SERVER = "root@106.54.25.161"
SSH_KEY = "/Users/zhaoruicn/.ssh/id_ed25519"

def ssh_cmd(cmd):
    """通过SSH在云服务器上执行命令"""
    full_cmd = f'ssh -o ConnectTimeout=15 -o StrictHostKeyChecking=no -i {SSH_KEY} {CLOUD_SERVER} "{cmd}"'
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=60)
    return result.stdout

def get_cloud_tech_analysis(code):
    """获取云服务器的技术分析结果"""
    # 自动识别沪深
    if code.startswith('6'):
        prefix = 'sh'
    else:
        prefix = 'sz'
    
    full_code = f"{prefix}{code}"
    
    # 调用云服务器的脚本
    output = ssh_cmd(f"python3 /tmp/stock_technical_analysis.py {code}")
    
    # 解析输出
    result = {
        'code': code,
        'name': '',
        'price': '',
        'chg': '',
        'chg_pct': '',
        'macd_signal': '',
        'kdj_signal': '',
        'rsi_status': '',
        'bollinger_pos': '',
        'ma_status': '',
        'volume_ratio': '',
        'error': ''
    }
    
    if not output or 'error' in output.lower()[:100]:
        result['error'] = '获取失败'
        return result
    
    lines = output.split('\n')
    current_section = ''
    for line in lines:
        line = line.strip()
        # 股票名称和代码
        if '(' in line and ')' in line and '技术分析' in line:
            parts = line.split('(')
            result['name'] = parts[0].replace('=', '').strip()
        # 当前价和涨跌幅
        if '当前价:' in line:
            parts = line.split()
            for i, p in enumerate(parts):
                if '当前价:' in p:
                    try:
                        result['price'] = parts[i+1]
                    except:
                        pass
                if '涨跌:' in p:
                    try:
                        chg_str = parts[i+1]  # like "+1.80"
                        result['chg'] = chg_str
                    except:
                        pass
                if '(+' in p or '(-' in p:
                    try:
                        result['chg_pct'] = p.replace('(', '').replace(')', '')
                    except:
                        pass
        # 追踪当前在哪个指标区域
        if 'MACD' in line and '【' in line:
            current_section = 'MACD'
        elif 'KDJ' in line and '【' in line:
            current_section = 'KDJ'
        elif 'RSI' in line and '【' in line:
            current_section = 'RSI'
        elif '【' in line:
            current_section = ''
        
        # MACD信号 - 在信号行
        if current_section == 'MACD' and '信号:' in line:
            if '金叉' in line:
                result['macd_signal'] = '✅'
            elif '死叉' in line:
                result['macd_signal'] = '❌'
        # KDJ信号
        if current_section == 'KDJ' and '信号:' in line:
            if '金叉' in line:
                result['kdj_signal'] = '✅'
            elif '死叉' in line:
                result['kdj_signal'] = '❌'
        # RSI状态
        if current_section == 'RSI' and '状态' in line:
            if '超买' in line:
                result['rsi_status'] = '⚠️超买'
            elif '超卖' in line:
                result['rsi_status'] = '⚠️超卖'
            else:
                result['rsi_status'] = '正常'
        # 布林带位置
        if '价格位置:' in line:
            parts = line.split(':')
            if len(parts) > 1:
                result['bollinger_pos'] = parts[1].split('%')[0] + '%'
        # 均线状态
        if '均线状态:' in line:
            parts = line.split(':')
            if len(parts) > 1:
                result['ma_status'] = parts[1].strip()
        # 量比
        if '量比:' in line:
            parts = line.split(':')
            if len(parts) > 1:
                result['volume_ratio'] = parts[1].strip().split('(')[0]
    
    return result

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

def parse_selfselect(data):
    """解析自选股数据"""
    try:
        rows = data.get('data', {}).get('allResults', {}).get('result', {}).get('dataList', [])
    except:
        rows = []
    results = []
    today = datetime.now().strftime('%Y-%m-%d')
    today_key = f'{{{today}}}'
    for s in rows:
        results.append({
            'code': s.get('SECURITY_CODE', ''),
            'name': s.get('SECURITY_SHORT_NAME', ''),
            'price': s.get('NEWEST_PRICE', ''),
            'chg': s.get('CHG', ''),
        })
    return results

def screen_stocks(keyword: str):
    cmd = f"""curl -s -X POST 'https://mkapi2.dfcfs.com/finskillshub/api/claw/stock-screen' \
  -H 'Content-Type: application/json' \
  -H 'apikey: {API_KEY}' \
  --data '{{"keyword": "{keyword}", "pageNo": 1, "pageSize": 20}}'"""
    return curl_cmd(cmd)

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
    """发送消息到飞书"""
    try:
        openclaw_path = "/opt/homebrew/bin/openclaw"
        if os.path.exists(openclaw_path):
            subprocess.Popen(
                [openclaw_path, "message", "send", "--target", "oc_b14195eb990ab57ea573e696758ae3d5", "--message", message],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return True
        else:
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
    
    # 16:30 自选股报告 - 云服务器完整技术分析版
    if mode in ["selfselect", "all"]:
        print("获取自选股数据...")
        data = get_selfselect()
        stocks = parse_selfselect(data)
        
        if stocks:
            msg += "⭐ 我的自选股\n"
            msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            
            print(f"获取 {len(stocks)} 只股票的技术分析...")
            for i, s in enumerate(stocks):
                print(f"  [{i+1}/{len(stocks)}] {s['code']} {s['name']}...")
                analysis = get_cloud_tech_analysis(s['code'])
                
                # 涨跌emoji
                chg_val = float(analysis.get('chg_pct', '0').replace('%', '').replace('(', '').replace('+', '') or 0)
                emoji = "🔴" if chg_val > 0 else "🟢" if chg_val < 0 else "⚪"
                
                # 格式：名称 价格 (涨跌幅%) MACD信号 KDJ信号 RSI状态
                rsi = analysis.get('rsi_status', '')
                rsi_emoji = '🔥' if '超买' in rsi else '💧' if '超卖' in rsi else ''
                
                msg += f"{emoji} {s['name']}: {analysis.get('price', '-')} ({analysis.get('chg_pct', '-')}) "
                msg += f"MACD:{analysis.get('macd_signal', '-')} KDJ:{analysis.get('kdj_signal', '-')} "
                msg += f"{rsi_emoji}{rsi}\n"
            
            msg += "\n📊 布林带位置 | 均线状态 | 量比\n"
            msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for s in stocks:
                analysis = get_cloud_tech_analysis(s['code'])
                bollinger = analysis.get('bollinger_pos', '-')
                ma = analysis.get('ma_status', '-')
                vol = analysis.get('volume_ratio', '-')
                # 简化显示
                ma_short = ma[:4] if ma else '-'
                msg += f"{s['name']}: 布林{bollinger} | 均线{ma_short} | 量比{vol}\n"
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
        
        msg += f"\n🌙 月线MACD+KDJ金叉: {monthly_count}只\n"
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
