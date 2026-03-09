#!/usr/bin/env python3
"""
历史数据管理
保存和查询历史统计
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path('/opt/lobster-home/data')
HISTORY_DIR = DATA_DIR / 'history'
HISTORY_DIR.mkdir(exist_ok=True)

def archive_daily_data(stats: dict):
    """归档今日数据到历史"""
    today = stats.get('today', {})
    date = today.get('date')
    
    if not date:
        return
    
    # 保存到历史文件
    history_file = HISTORY_DIR / f"{date}.json"
    with open(history_file, 'w') as f:
        json.dump(today, f)
    
    print(f"📦 已归档 {date} 的数据")

def get_history(days: int = 7) -> list:
    """获取最近N天的历史数据"""
    history = []
    today = datetime.now()
    
    for i in range(days, 0, -1):
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        file_path = HISTORY_DIR / f"{date}.json"
        
        if file_path.exists():
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    history.append({
                        'date': date,
                        'tasks': data.get('tasks_completed', 0),
                        'tokens': data.get('tokens_used', 0),
                        'work_time': data.get('work_time_seconds', 0),
                        'room_time': data.get('room_time', {})
                    })
            except:
                pass
        else:
            # 没有数据的天补零
            history.append({
                'date': date,
                'tasks': 0,
                'tokens': 0,
                'work_time': 0,
                'room_time': {}
            })
    
    return history

def get_room_stats(days: int = 7) -> dict:
    """获取房间停留统计"""
    history = get_history(days)
    room_totals = {}
    
    for day in history:
        for room, seconds in day.get('room_time', {}).items():
            room_totals[room] = room_totals.get(room, 0) + seconds
    
    # 转换为小时并排序
    result = []
    for room, seconds in sorted(room_totals.items(), key=lambda x: x[1], reverse=True):
        if seconds > 0:
            result.append({
                'room': room,
                'hours': round(seconds / 3600, 1),
                'minutes': seconds // 60
            })
    
    return result

if __name__ == '__main__':
    # 测试
    print("📊 历史数据管理")
    history = get_history(7)
    for day in history:
        print(f"{day['date']}: {day['tasks']}任务, {day['tokens']}tokens")
