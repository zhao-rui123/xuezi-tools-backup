from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime, timedelta
from pathlib import Path

app = Flask(__name__)
CORS(app)

DATA_FILE = Path('/opt/lobster-home/data/stats.json')
HISTORY_DIR = Path('/opt/lobster-home/data/history')
HISTORY_DIR.mkdir(exist_ok=True)

def load_stats():
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
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

def save_stats(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def get_history(days=7):
    """获取历史数据"""
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
                        'work_time': data.get('work_time_seconds', 0)
                    })
            except:
                pass
        else:
            history.append({'date': date, 'tasks': 0, 'tokens': 0, 'work_time': 0})
    
    return history

@app.route('/api/status')
def get_status():
    return jsonify(load_stats())

@app.route('/api/task/start', methods=['POST'])
def start_task():
    data = request.json
    stats = load_stats()
    stats['current_room'] = 'workspace'
    stats['current_status'] = 'working'
    stats['current_task'] = data.get('task_name', '未命名')
    stats['task_start_time'] = datetime.now().isoformat()
    stats['last_activity'] = datetime.now().isoformat()
    save_stats(stats)
    return jsonify({'success': True, 'room': 'workspace'})

@app.route('/api/task/complete', methods=['POST'])
def complete_task():
    data = request.json
    tokens = data.get('tokens_used', 0)
    
    stats = load_stats()
    
    # 计算时长
    duration = 0
    if 'task_start_time' in stats:
        start = datetime.fromisoformat(stats['task_start_time'])
        duration = (datetime.now() - start).total_seconds()
    
    # 记录任务
    stats['today']['tasks'].append({
        'name': stats.get('current_task', '未命名'),
        'duration': int(duration),
        'tokens': tokens
    })
    
    stats['today']['tasks_completed'] += 1
    stats['today']['tokens_used'] += tokens
    stats['today']['work_time_seconds'] += int(duration)
    
    # 去客厅休息
    stats['current_room'] = 'livingroom'
    stats['current_status'] = 'resting'
    stats['last_activity'] = datetime.now().isoformat()
    
    save_stats(stats)
    return jsonify({'success': True, 'room': 'livingroom', 'tokens_recorded': tokens})

@app.route('/api/history')
def get_history_api():
    """获取历史趋势数据"""
    days = request.args.get('days', 7, type=int)
    history = get_history(days)
    return jsonify({'success': True, 'data': history})

@app.route('/api/archive', methods=['POST'])
def archive_today():
    """归档今日数据"""
    stats = load_stats()
    today = stats.get('today', {})
    date = today.get('date')
    
    if date:
        history_file = HISTORY_DIR / f"{date}.json"
        with open(history_file, 'w') as f:
            json.dump(today, f)
        return jsonify({'success': True, 'message': f'已归档 {date}'})
    
    return jsonify({'success': False, 'message': '无数据可归档'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
