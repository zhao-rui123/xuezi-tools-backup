#!/usr/bin/env python3
"""
世界时钟工具 - 显示多个时区的时间
"""

from datetime import datetime
from zoneinfo import ZoneInfo
import sys

# 常用时区配置
TIMEZONES = {
    '北京': 'Asia/Shanghai',
    '东京': 'Asia/Tokyo',
    '悉尼': 'Australia/Sydney',
    '伦敦': 'Europe/London',
    '纽约': 'America/New_York',
    '洛杉矶': 'America/Los_Angeles',
    'UTC': 'UTC',
}

def get_time_in_timezone(city, tz_name):
    """获取指定时区的当前时间"""
    try:
        tz = ZoneInfo(tz_name)
        now = datetime.now(tz)
        return {
            'city': city,
            'timezone': tz_name,
            'time': now.strftime('%H:%M:%S'),
            'date': now.strftime('%Y-%m-%d'),
            'weekday': now.strftime('%A'),
            'offset': now.strftime('%z'),
            'is_dst': now.dst().total_seconds() != 0
        }
    except Exception as e:
        return {'city': city, 'error': str(e)}

def format_time_info(info):
    """格式化时间信息"""
    if 'error' in info:
        return f"❌ {info['city']}: {info['error']}"
    
    dst_indicator = " (夏令时)" if info.get('is_dst') else ""
    return f"🌍 {info['city']:6s} {info['time']} {info['date']} {info['weekday'][:3]}{dst_indicator}"

def show_world_clock():
    """显示世界时钟"""
    print("=" * 70)
    print("🕐 世界时钟")
    print("=" * 70)
    
    for city, tz in TIMEZONES.items():
        info = get_time_in_timezone(city, tz)
        print(format_time_info(info))
    
    print("=" * 70)

def convert_time(from_city, time_str, to_city):
    """转换时间"""
    try:
        from_tz = ZoneInfo(TIMEZONES.get(from_city, from_city))
        to_tz = ZoneInfo(TIMEZONES.get(to_city, to_city))
        
        # 解析输入时间
        today = datetime.now().strftime('%Y-%m-%d')
        input_dt = datetime.strptime(f"{today} {time_str}", '%Y-%m-%d %H:%M')
        input_dt = input_dt.replace(tzinfo=from_tz)
        
        # 转换
        output_dt = input_dt.astimezone(to_tz)
        
        print(f"\n🔄 时间转换:")
        print(f"   {from_city}: {time_str} → {to_city}: {output_dt.strftime('%H:%M')}")
        print(f"   日期: {output_dt.strftime('%Y-%m-%d %A')}")
        
    except Exception as e:
        print(f"❌ 转换失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) == 1:
        show_world_clock()
    elif sys.argv[1] == 'convert' and len(sys.argv) == 5:
        # python3 world_clock.py convert 北京 14:30 纽约
        convert_time(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("用法:")
        print("  python3 world_clock.py                    # 显示世界时钟")
        print("  python3 world_clock.py convert 北京 14:30 纽约  # 时间转换")
        print("\n支持的城市:")
        for city in TIMEZONES.keys():
            print(f"  - {city}")

if __name__ == "__main__":
    main()
