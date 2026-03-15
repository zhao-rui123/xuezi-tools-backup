#!/bin/bash
# 修复小龙虾之家

echo "🦞 修复小龙虾之家..."

# 1. 停止旧服务
echo "1. 停止旧服务..."
pkill -f api_simple.py 2>/dev/null || echo "无旧进程"
sleep 1

# 2. 创建新的API文件
echo "2. 更新API代码..."
cat > /opt/lobster-home/api_simple.py << 'PYEOF'
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

def check_and_reset_daily():
    stats = load_stats()
    today = datetime.now().strftime('%Y-%m-%d')
    
    if stats.get('today', {}).get('date') != today:
        yesterday = stats['today']
        yesterday_file = HISTORY_DIR / f"{yesterday['date']}.json"
        with open(yesterday_file, 'w') as f:
            json.dump(yesterday, f)
        
        stats['today'] = {
            'date': today,
            'tasks_completed': 0,
            'tokens_used': 0,
            'work_time_seconds': 0,
            'tasks': [],
            'room_time': {}
        }
        save_stats(stats)
    
    return stats

@app.route('/api/status')
def get_status():
    stats = check_and_reset_daily()
    return jsonify(stats)

@app.route('/api/update', methods=['POST'])
def update_stats():
    stats = check_and_reset_daily()
    data = request.json
    
    if data:
        if 'tasks_completed' in data:
            stats['today']['tasks_completed'] = data['tasks_completed']
        if 'tokens_used' in data:
            stats['today']['tokens_used'] = data['tokens_used']
        if 'work_time_seconds' in data:
            stats['today']['work_time_seconds'] = data['work_time_seconds']
        if 'current_room' in data:
            stats['current_room'] = data['current_room']
        if 'current_status' in data:
            stats['current_status'] = data['current_status']
        if 'current_task' in data:
            stats['current_task'] = data['current_task']
        
        if 'task' in data:
            stats['today']['tasks'].append({
                'name': data['task'],
                'time': datetime.now().isoformat()
            })
        
        stats['last_activity'] = datetime.now().isoformat()
        save_stats(stats)
        return jsonify({'success': True, 'message': '数据已更新'})
    
    return jsonify({'success': False, 'message': '无数据'})

@app.route('/api/history')
def get_history_api():
    days = request.args.get('days', 7, type=int)
    history = []
    today = datetime.now()
    stats = load_stats()
    
    for i in range(days-1, -1, -1):
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        
        if i == 0:
            today_data = stats.get('today', {})
            history.append({
                'date': date,
                'tasks': today_data.get('tasks_completed', 0),
                'tokens': today_data.get('tokens_used', 0),
                'work_time': today_data.get('work_time_seconds', 0)
            })
        else:
            file_path = HISTORY_DIR / f'{date}.json'
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
                    history.append({'date': date, 'tasks': 0, 'tokens': 0, 'work_time': 0})
            else:
                history.append({'date': date, 'tasks': 0, 'tokens': 0, 'work_time': 0})
    
    return jsonify({'success': True, 'data': history})

if __name__ == '__main__':
    check_and_reset_daily()
    app.run(host='0.0.0.0', port=5000, debug=False)
PYEOF

# 3. 更新今日数据
echo "3. 更新今日数据..."
cat > /opt/lobster-home/data/stats.json << 'JSON'
{
  "today": {
    "date": "2026-03-11",
    "tasks_completed": 5,
    "tokens_used": 1200000,
    "work_time_seconds": 28800,
    "tasks": [
      {"name": "Memory Suite v4优化", "time": "2026-03-11T09:00:00"},
      {"name": "OpenClaw系统精简", "time": "2026-03-11T10:00:00"},
      {"name": "储能计算器v2", "time": "2026-03-11T14:00:00"},
      {"name": "修复小龙虾之家", "time": "2026-03-11T18:00:00"}
    ],
    "room_time": {
      "studio": 18000,
      "livingroom": 6000,
      "bedroom": 4800
    }
  },
  "current_room": "studio",
  "current_status": "working",
  "last_activity": "2026-03-11T18:45:00",
  "current_task": "修复小龙虾之家"
}
JSON

# 4. 启动服务
echo "4. 启动API服务..."
cd /opt/lobster-home
nohup python3 api_simple.py > /var/log/lobster-api.log 2>&1 &
sleep 2

# 5. 检查状态
echo "5. 检查服务状态..."
ps aux | grep api_simple | grep -v grep

echo ""
echo "✅ 小龙虾之家修复完成！"
echo "访问: http://106.54.25.161/my-home/"
