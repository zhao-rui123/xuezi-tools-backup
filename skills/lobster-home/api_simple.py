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
    return {'today': {'date': datetime.now().strftime('%Y-%m-%d'), 'tasks_completed': 0, 'tokens_used': 0, 'work_time_seconds': 0, 'tasks': [], 'room_time': {}}, 'current_room': 'livingroom', 'current_status': 'resting', 'last_activity': datetime.now().isoformat()}

def save_stats(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def get_history(days=7):
    history = []
    today = datetime.now()
    stats = load_stats()
    
    # 包含今天在内的近7天
    for i in range(days-1, -1, -1):
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # 如果是今天，使用当前stats数据
        if i == 0:
            today_data = stats.get('today', {})
            history.append({
                'date': date, 
                'tasks': today_data.get('tasks_completed', 0), 
                'tokens': today_data.get('tokens_used', 0), 
                'work_time': today_data.get('work_time_seconds', 0)
            })
        else:
            # 历史日期从文件读取
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
    return history

@app.route('/api/status')
def get_status():
    return jsonify(load_stats())

@app.route('/api/history')
def get_history_api():
    days = request.args.get('days', 7, type=int)
    history = get_history(days)
    return jsonify({'success': True, 'data': history})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
