#!/usr/bin/env python3
"""
小龙虾之家 - 每日数据持久化脚本
每天自动归档当天工作数据到历史文件
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

# 数据路径
DATA_FILE = Path('/opt/lobster-home/data/stats.json')
HISTORY_DIR = Path('/opt/lobster-home/data/history')
HISTORY_DIR.mkdir(exist_ok=True)

def load_stats():
    """加载当前统计数据"""
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
    """保存历史数据"""
    file_path = HISTORY_DIR / f'{date_str}.json'
    with open(file_path, 'w') as f:
        json.dump(data, f)
    return file_path

def archive_today():
    """归档今天的数据"""
    stats = load_stats()
    today_data = stats.get('today', {})
    
    # 获取今天的日期
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
    
    # 重置今天的数据（为新的一天做准备）
    tomorrow = datetime.now() + timedelta(days=1)
    stats['today'] = {
        'date': tomorrow.strftime('%Y-%m-%d'),
        'tasks_completed': 0,
        'tokens_used': 0,
        'work_time_seconds': 0,
        'tasks': [],
        'room_time': {}
    }
    
    # 保存重置后的数据
    with open(DATA_FILE, 'w') as f:
        json.dump(stats, f)
    
    print(f'✅ 已重置 {tomorrow.strftime("%Y-%m-%d")} 的数据')
    return True

def cleanup_old_history(days=30):
    """清理旧的历史数据（默认保留30天）"""
    cutoff_date = datetime.now() - timedelta(days=days)
    deleted_count = 0
    
    for file_path in HISTORY_DIR.glob('*.json'):
        try:
            # 从文件名提取日期
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
    else:
        print('ℹ️  没有需要清理的旧数据')

def main():
    """主函数"""
    print('=' * 50)
    print('🦞 小龙虾之家 - 每日数据归档')
    print('=' * 50)
    print(f'⏰ 执行时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    
    # 1. 归档今天数据
    print('📦 步骤1: 归档今日数据...')
    archive_today()
    print()
    
    # 2. 清理旧数据
    print('🧹 步骤2: 清理旧数据（保留30天）...')
    cleanup_old_history()
    print()
    
    print('=' * 50)
    print('✅ 数据持久化完成！')
    print('=' * 50)

if __name__ == '__main__':
    main()
