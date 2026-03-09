#!/usr/bin/env python3
"""
小龙虾之家 API 服务器
提供实时状态查询和数据更新接口
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
CORS(app)  # 允许跨域

# 数据文件路径
DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(exist_ok=True)
STATS_FILE = DATA_DIR / 'stats.json'

# 默认状态
DEFAULT_STATE = {
    'today': {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'tasks_completed': 0,
        'tokens_used': 0,
        'work_time_seconds': 0,
        'tasks': [],
        'room_time': {
            'tearoom': 0, 'kitchen': 0, 'gameroom': 0,
            'bathroom1': 0, 'livingroom': 300, 'workspace': 0,
            'dining': 0, 'bathroom2': 0, 'bedroom': 0,
            'playground': 0
        }
    },
    'current_room': 'livingroom',
    'current_status': 'resting',
    'current_task': None,
    'last_activity': datetime.now().isoformat(),
    'slacking_count': 0
}

def load_stats():
    """加载统计数据"""
    if STATS_FILE.exists():
        try:
            with open(STATS_FILE, 'r') as f:
                data = json.load(f)
                # 检查是否新的一天
                today = datetime.now().strftime('%Y-%m-%d')
                if data.get('today', {}).get('date') != today:
                    # 重置今日统计
                    data['today'] = DEFAULT_STATE['today'].copy()
                    data['today']['date'] = today
                return data
        except:
            pass
    return DEFAULT_STATE.copy()

def save_stats(data):
    """保存统计数据"""
    with open(STATS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# API 路由

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取当前状态"""
    return jsonify(load_stats())

@app.route('/api/status', methods=['POST'])
def update_status():
    """更新状态"""
    data = request.json
    stats = load_stats()
    
    # 更新房间
    if 'room' in data:
        old_room = stats['current_room']
        new_room = data['room']
        stats['current_room'] = new_room
        
        # 记录房间时间
        if old_room != new_room:
            now = datetime.now()
            last = datetime.fromisoformat(stats['last_activity'])
            time_spent = (now - last).total_seconds()
            stats['today']['room_time'][old_room] = \
                stats['today']['room_time'].get(old_room, 0) + int(time_spent)
    
    # 更新状态
    if 'status' in data:
        stats['current_status'] = data['status']
    
    # 更新任务
    if 'current_task' in data:
        stats['current_task'] = data['current_task']
    
    stats['last_activity'] = datetime.now().isoformat()
    save_stats(stats)
    
    return jsonify({'success': True, 'data': stats})

@app.route('/api/task/start', methods=['POST'])
def start_task():
    """开始任务"""
    data = request.json
    task_name = data.get('task_name', '未命名任务')
    
    stats = load_stats()
    stats['current_task'] = task_name
    stats['current_status'] = 'working'
    stats['current_room'] = 'workspace'
    stats['task_start_time'] = datetime.now().isoformat()
    stats['last_activity'] = datetime.now().isoformat()
    save_stats(stats)
    
    return jsonify({
        'success': True,
        'message': f'任务开始: {task_name}',
        'room': 'workspace'
    })

@app.route('/api/task/complete', methods=['POST'])
def complete_task():
    """完成任务"""
    data = request.json
    tokens = data.get('tokens_used', 0)
    
    stats = load_stats()
    
    # 计算任务时长
    task_duration = 0
    if 'task_start_time' in stats:
        start = datetime.fromisoformat(stats['task_start_time'])
        task_duration = (datetime.now() - start).total_seconds()
    
    # 记录任务
    task_record = {
        'name': stats.get('current_task', '未命名'),
        'duration': int(task_duration),
        'tokens': tokens,
        'completed_at': datetime.now().isoformat()
    }
    
    stats['today']['tasks'].append(task_record)
    stats['today']['tasks_completed'] += 1
    stats['today']['tokens_used'] += tokens
    stats['today']['work_time_seconds'] += int(task_duration)
    
    # 选择下一个房间
    import random
    hour = datetime.now().hour
    
    if task_duration > 1800:  # 高强度工作
        next_room = 'playground'
        next_status = 'exercising'
    elif 11 <= hour <= 13 or 17 <= hour <= 19:  # 饭点
        next_room = 'dining'
        next_status = 'eating'
    else:
        activities = [
            ('tearoom', 'drinking'),
            ('livingroom', 'resting'),
            ('gameroom', 'gaming')
        ]
        next_room, next_status = random.choice(activities)
    
    stats['current_room'] = next_room
    stats['current_status'] = next_status
    stats['current_task'] = None
    stats['last_activity'] = datetime.now().isoformat()
    
    save_stats(stats)
    
    return jsonify({
        'success': True,
        'message': '任务完成',
        'next_room': next_room,
        'task_summary': task_record
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计数据"""
    stats = load_stats()
    return jsonify(stats['today'])

@app.route('/api/summary', methods=['GET'])
def get_summary():
    """获取每日总结"""
    stats = load_stats()
    today = stats['today']
    
    # 找出最耗时的任务
    longest_task = None
    if today['tasks']:
        longest_task = max(today['tasks'], key=lambda x: x.get('duration', 0))
    
    # 房间停留时间排序
    room_times = sorted(
        today['room_time'].items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    summary = {
        'date': today['date'],
        'tasks_completed': today['tasks_completed'],
        'tokens_used': today['tokens_used'],
        'work_time_formatted': f"{today['work_time_seconds'] // 3600}h {(today['work_time_seconds'] % 3600) // 60}m",
        'longest_task': longest_task,
        'top_rooms': room_times[:3],
        'current_room': stats['current_room'],
        'slacking_count': stats.get('slacking_count', 0)
    }
    
    return jsonify(summary)

@app.route('/api/slacking', methods=['POST'])
def record_slacking():
    """记录摸鱼"""
    stats = load_stats()
    stats['slacking_count'] = stats.get('slacking_count', 0) + 1
    
    # 随机选择卫生间
    import random
    bath = random.choice(['bathroom1', 'bathroom2'])
    stats['current_room'] = bath
    stats['current_status'] = 'slacking'
    stats['last_activity'] = datetime.now().isoformat()
    
    save_stats(stats)
    
    return jsonify({
        'success': True,
        'message': '摸鱼记录成功',
        'room': bath
    })

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'time': datetime.now().isoformat()})

if __name__ == '__main__':
    print("🦞 小龙虾之家 API 服务器启动")
    print("监听端口: 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
