#!/usr/bin/env python3
"""
云端股票筛选工具 - 优化版
支持后台执行和结果缓存
"""
import json
import os
import subprocess
import time
from datetime import datetime
from typing import Dict, Any, Optional

# 云服务器配置
CLOUD_SERVER = {
    "host": "106.54.25.161",
    "user": "root",
    "password": "Zr123456"
}

# 本地缓存目录
CACHE_DIR = os.path.expanduser("~/.openclaw/workspace/.stock_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def ssh_exec(command: str, timeout: int = 30) -> str:
    """通过SSH执行远程命令"""
    cmd = [
        "sshpass", "-p", CLOUD_SERVER["password"],
        "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=10",
        f"{CLOUD_SERVER['user']}@{CLOUD_SERVER['host']}",
        command
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:
        return f"ERROR: {str(e)}"

def get_cache_key(months: int, grade: str = None) -> str:
    """获取缓存文件名"""
    if grade:
        return f"screen_{months}m_grade_{grade}.json"
    return f"screen_{months}m_all.json"

def get_cached_result(months: int, grade: str = None) -> Optional[Dict]:
    """获取缓存结果"""
    cache_file = os.path.join(CACHE_DIR, get_cache_key(months, grade))
    if os.path.exists(cache_file):
        # 检查缓存是否过期（24小时）
        mtime = os.path.getmtime(cache_file)
        age_hours = (time.time() - mtime) / 3600
        if age_hours < 24:
            with open(cache_file, 'r') as f:
                return json.load(f)
    return None

def save_cache_result(months: int, grade: str, data: Dict):
    """保存结果到缓存"""
    cache_file = os.path.join(CACHE_DIR, get_cache_key(months, grade))
    with open(cache_file, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def start_background_screening(months: int) -> str:
    """后台启动股票筛选"""
    print(f"🚀 提交后台筛选任务 (近{months}个月)...")
    
    # 先创建一个脚本文件 (用双$$转义)
    script_content = f'''#!/bin/bash
cd /opt/stock-screener/backend
export PYTHONPATH=/opt/stock-screener/backend
python3 << 'PYEOF' > /tmp/screen_log_{months}m.txt 2>&1
import asyncio
import json
import sys
sys.path.insert(0, '.')
from services.stock_screener import StockScreener
from datetime import datetime

async def main():
    screener = StockScreener()
    results = await screener.screen_all_stocks(recent_months={months})
    
    grade_a = [r for r in results if r.get('grade') == 'A']
    grade_b = [r for r in results if r.get('grade') == 'B']
    grade_c = [r for r in results if r.get('grade') == 'C']
    
    output = {{
        'timestamp': datetime.now().isoformat(),
        'months': {months},
        'total': len(results),
        'grade_a_count': len(grade_a),
        'grade_b_count': len(grade_b),
        'grade_c_count': len(grade_c),
        'grade_a': grade_a,
        'grade_b': grade_b,
        'grade_c': grade_c
    }}
    
    with open('/tmp/screen_result_{months}m.json', 'w') as f:
        json.dump(output, f, ensure_ascii=False)
    
    print('DONE')

asyncio.run(main())
PYEOF
'''
    
    # 写入脚本文件
    script_cmd = f'echo "{script_content}" > /tmp/run_screen_{months}m.sh && chmod +x /tmp/run_screen_{months}m.sh'
    ssh_exec(script_cmd, timeout=10)
    
    # 后台执行脚本
    remote_cmd = f"nohup /tmp/run_screen_{months}m.sh > /dev/null 2>&1 & echo '任务已启动'"
    
    result = ssh_exec(remote_cmd, timeout=10)
    return result

def check_screening_status(months: int) -> Dict[str, Any]:
    """检查筛选状态"""
    # 检查结果文件
    check_cmd = f"cat /tmp/screen_result_{months}m.json 2>/dev/null | head -1"
    result = ssh_exec(check_cmd, timeout=10)
    
    if result.startswith("{"):
        try:
            data = json.loads(result)
            return {"status": "done", "data": data}
        except:
            pass
    
    # 检查日志
    log_cmd = f"tail -5 /tmp/screen_log_{months}m.txt 2>/dev/null"
    log = ssh_exec(log_cmd, timeout=10)
    
    return {"status": "running", "log": log}

def screen_stocks(months: int = 2, use_cache: bool = True) -> Dict[str, Any]:
    """执行股票筛选"""
    # 检查本地缓存
    if use_cache:
        cached = get_cached_result(months)
        if cached:
            print("📦 使用本地缓存结果")
            return {"status": "cached", "data": cached}
    
    # 检查云端缓存/状态
    status = check_screening_status(months)
    
    if status["status"] == "done":
        # 保存到本地缓存
        save_cache_result(months, None, status["data"])
        return {"status": "done", "data": status["data"]}
    
    if "log" in status and "DONE" in status["log"]:
        # 刚完成，再检查一次
        time.sleep(2)
        status = check_screening_status(months)
        if status["status"] == "done":
            save_cache_result(months, None, status["data"])
            return {"status": "done", "data": status["data"]}
    
    # 启动后台筛选
    start_background_screening(months)
    return {
        "status": "started",
        "message": f"已提交筛选任务（近{months}个月），约需10-15分钟完成",
        "check_command": f"选股状态 {months}个月"
    }

def filter_by_grade(months: int, grade: str) -> Dict[str, Any]:
    """筛选特定等级"""
    result = screen_stocks(months, use_cache=True)
    
    if result.get("status") in ["done", "cached"]:
        data = result.get("data", {})
        grade_key = f"grade_{grade.lower()}"
        stocks = data.get(grade_key, [])
        return {
            "status": "ok",
            "grade": grade.upper(),
            "count": data.get(f"{grade_key}_count", 0),
            "stocks": stocks
        }
    
    return result

def format_result(data: Dict[str, Any]) -> str:
    """格式化输出"""
    if "error" in data:
        return f"❌ 错误: {data['error']}"
    
    status = data.get("status", "")
    
    if status == "started":
        return f"⏳ {data.get('message', '任务已启动')}"
    
    if status == "running":
        return f"⏳ 筛选进行中...\n\n日志:\n{data.get('log', '')}"
    
    # 显示结果
    if "data" in data:
        result = data["data"]
    else:
        result = data
    
    lines = []
    lines.append("=" * 50)
    lines.append("📊 股票筛选结果")
    lines.append("=" * 50)
    
    if "timestamp" in result:
        lines.append(f"⏰ 筛选时间: {result['timestamp'][:19]}")
    
    lines.append(f"\n📈 总计: **{result.get('total', 0)}** 只")
    lines.append(f"  🌟 A级: **{result.get('grade_a_count', 0)}** 只")
    lines.append(f"  📗 B级: **{result.get('grade_b_count', 0)}** 只")
    lines.append(f"  📙 C级: **{result.get('grade_c_count', 0)}** 只")
    
    # A级详情
    grade_a = result.get("grade_a", [])
    if grade_a:
        lines.append("\n🌟 **A级股票 (MACD+KDJ双金叉)**")
        for stock in grade_a[:15]:
            lines.append(f"  • {stock.get('name')} ({stock.get('code')}) 💰{stock.get('current_price')}")
    
    # B级详情
    grade_b = result.get("grade_b", [])
    if grade_b:
        lines.append("\n📗 **B级股票 (仅MACD金叉)**")
        for stock in grade_b[:10]:
            lines.append(f"  • {stock.get('name')} ({stock.get('code')}) 💰{stock.get('current_price')}")
    
    # C级详情
    grade_c = result.get("grade_c", [])
    if grade_c:
        lines.append("\n📙 **C级股票 (仅KDJ金叉)**")
        for stock in grade_c[:10]:
            lines.append(f"  • {stock.get('name')} ({stock.get('code')}) 💰{stock.get('current_price')}")
    
    lines.append("\n" + "=" * 50)
    return "\n".join(lines)

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("📖 使用说明:")
        print("  选股 [月份]           - 筛选股票 (默认2个月)")
        print("  选股状态 [月份]       - 检查筛选状态")
        print("  筛选A级 [月份]        - 筛选A级股票")
        print("  筛选B级 [月份]        - 筛选B级股票")
        print("  筛选C级 [月份]        - 筛选C级股票")
        return
    
    cmd = sys.argv[1].lower()
    months = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    if cmd == "选股" or cmd == "screen":
        result = screen_stocks(months)
        print(format_result(result))
    elif cmd == "选股状态" or cmd == "status":
        status = check_screening_status(months)
        print(format_result(status))
    elif cmd == "筛选" or cmd == "filter":
        if len(sys.argv) > 3:
            grade = sys.argv[2].upper()
            result = filter_by_grade(months, grade)
            print(format_result(result))
        else:
            print("请指定等级: A, B, 或 C")
    else:
        print(f"未知命令: {cmd}")

if __name__ == "__main__":
    main()
