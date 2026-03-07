#!/usr/bin/env python3
"""
网络对时工具 - 同步系统时间到网络时间服务器
"""

import subprocess
import sys
import time
from datetime import datetime
import urllib.request
import json

def get_network_time():
    """从网络获取准确时间（使用多个时间源）"""
    time_sources = [
        # 源1: worldtimeapi.org
        {
            'url': "https://worldtimeapi.org/api/ip",
            'parser': lambda d: {
                'datetime': d['datetime'],
                'timezone': d['timezone'],
                'utc_offset': d['utc_offset'],
                'unixtime': d['unixtime']
            }
        },
        # 源2: 淘宝时间API (国内可用)
        {
            'url': "https://worldtimeapi.org/api/timezone/Asia/Shanghai",
            'parser': lambda d: {
                'datetime': d['datetime'],
                'timezone': d['timezone'],
                'utc_offset': d['utc_offset'],
                'unixtime': d['unixtime']
            }
        },
    ]
    
    for source in time_sources:
        try:
            url = source['url']
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')
            response = urllib.request.urlopen(req, timeout=10)
            data = json.loads(response.read().decode('utf-8'))
            return source['parser'](data)
        except Exception as e:
            print(f"  尝试 {url.split('/')[2]}... 失败")
            continue
    
    print("❌ 所有时间源都不可用")
    return None

def get_system_time():
    """获取系统当前时间"""
    return {
        'datetime': datetime.now().isoformat(),
        'timezone': time.tzname[0] if time.tzname else 'Unknown',
        'utc_offset': time.strftime('%z'),
        'unixtime': int(time.time())
    }

def format_time_diff(seconds):
    """格式化时间差"""
    if abs(seconds) < 1:
        return "同步"
    elif seconds > 0:
        return f"慢 {seconds:.1f} 秒"
    else:
        return f"快 {abs(seconds):.1f} 秒"

def sync_time_darwin():
    """macOS系统时间同步"""
    try:
        # macOS 使用 sntp 或系统设置
        print("🔄 正在同步系统时间...")
        
        # 方法1: 使用 sntp
        result = subprocess.run(
            ['sntp', '-s', 'time.apple.com'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ 时间同步成功 (time.apple.com)")
            return True
        else:
            print(f"⚠️ sntp 同步失败: {result.stderr}")
            
        # 方法2: 提示用户手动设置
        print("\n💡 请手动执行以下命令同步时间:")
        print("   sudo sntp -s time.apple.com")
        print("   或")
        print("   系统设置 → 日期与时间 → 自动设置日期和时间")
        return False
        
    except Exception as e:
        print(f"❌ 同步失败: {e}")
        return False

def check_time():
    """检查系统时间与网络时间差异"""
    print("=" * 60)
    print("🕐 网络对时检查")
    print("=" * 60)
    
    # 获取网络时间
    print("\n📡 正在获取网络时间...")
    network_time = get_network_time()
    if not network_time:
        return
    
    # 获取系统时间
    system_time = get_system_time()
    
    # 计算差异
    time_diff = system_time['unixtime'] - network_time['unixtime']
    
    # 显示结果
    print("\n🌐 网络时间:")
    print(f"   时区: {network_time['timezone']}")
    print(f"   时间: {network_time['datetime'][:19]}")
    print(f"   UTC偏移: {network_time['utc_offset']}")
    
    print("\n💻 系统时间:")
    print(f"   时区: {system_time['timezone']}")
    print(f"   时间: {system_time['datetime'][:19]}")
    print(f"   UTC偏移: {system_time['utc_offset']}")
    
    print("\n📊 时间差异:")
    diff_status = format_time_diff(time_diff)
    if abs(time_diff) < 1:
        print(f"   ✅ {diff_status}")
    elif abs(time_diff) < 60:
        print(f"   ⚠️  {diff_status}")
    else:
        print(f"   ❌ 差异较大: {diff_status}")
    
    print("\n" + "=" * 60)
    
    return time_diff

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 time_sync.py [check|sync]")
        print("  check - 检查时间差异")
        print("  sync  - 尝试同步系统时间")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'check':
        check_time()
    elif command == 'sync':
        diff = check_time()
        if diff and abs(diff) > 1:
            print("\n🔄 开始同步...")
            if sys.platform == 'darwin':
                sync_time_darwin()
            else:
                print("❌ 暂不支持此操作系统")
        else:
            print("\n✅ 时间已经同步，无需调整")
    else:
        print(f"未知命令: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
