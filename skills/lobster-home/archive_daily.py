#!/usr/bin/env python3
"""
小龙虾之家 - 每日数据持久化脚本（修复版）
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

DATA_FILE = Path('/opt/lobster-home/data/stats.json')
HISTORY_DIR = Path('/opt/lobster-home/data/history')
HISTORY_DIR.mkdir(exist_ok=True)

def load_stats():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        'today': {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'tasks_completed': 0,
            'tokens_used': 0,
            'work_time_seconds': 0,
            'tasks': [],
            'room_time': {}
        },
        'current_room': 'livingroom',
        'current_status': 'resting',
        'last_activity': datetime.now().isoformat()
    }

def save_history(date_str, data):
    file_path = HISTORY_DIR / f'{date_str}.json'
    with open(file_path, 'w') as f:
        json.dump(data, f)
    return file_path

def archive_today():
    stats = load_stats()
    today_data = stats.get('today', {})
    
    # 获取今天的日期（从数据里读，而不是当前时间）
    today_str = today_data.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # 准备归档数据
    archive_data = {
        'date': today_str,
        'tasks_completed': today_data.get('tasks_completed', 0),
        'tokens_used': today_data.get('tokens_used', 0),
        'work_time_seconds': today_data.get('work_time_seconds', 0),
        'tasks': today_data.get('tasks', []),
        'room_time': today_data.get('room_time', {}),
        'archived_at': datetime.now().isoformat()
    }
    
    # 保存到历史文件
    file_path = save_history(today_str, archive_data)
    print(f'✅ 已归档 {today_str} 的数据到 {file_path}')
    
    # 修复：基于today_str计算明天，而不是用datetime.now()
    today = datetime.strptime(today_str, '%Y-%m-%d')
    tomorrow = today + timedelta(days=1)
    
    stats['today'] = {
        'date': tomorrow.strftime('%Y-%m-%d'),
        'tasks_completed': 0,
        'tokens_used': 0,
        'work_time_seconds': 0,
        'tasks': [],
        'room_time': {}
    }
    
    with open(DATA_FILE, 'w') as f:
        json.dump(stats, f)
    
    print(f'✅ 已重置 {tomorrow.strftime("%Y-%m-%d")} 的数据')
    return True

def cleanup_old_history(days=30):
    cutoff_date = datetime.now() - timedelta(days=days)
    deleted_count = 0
    
    for file_path in HISTORY_DIR.glob('*.json'):
        try:
            date_str = file_path.stem
            file_date = datetime.strptime(date_str, '%Y-%m-%d')
            
            if file_date < cutoff_date:
                file_path.unlink()
                deleted_count += 1
                print(f'🗑️  已删除旧数据: {date_str}')
        except:
            pass
    
    if deleted_count > 0:
        print(f'✅ 共清理 {deleted_count} 个旧文件')

def main():
    print('=' * 50)
    print('🦞 小龙虾之家 - 每日数据归档（修复版）')
    print('=' * 50)
    print(f'⏰ 执行时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    
    print('📦 步骤1: 归档今日数据...')
    archive_today()
    print()
    
    print('🧹 步骤2: 清理旧数据（保留30天）...')
    cleanup_old_history()
    print()
    
    print('=' * 50)
    print('✅ 数据持久化完成！')
    print('=' * 50)

if __name__ == '__main__':
    main()
