#!/usr/bin/env python3
"""
Web管理界面 - 多Agent协作系统可视化看板
功能：任务看板、Agent状态监控、实时统计
"""

from flask import Flask, render_template, jsonify, request
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

SUITE_DIR = Path("~/.openclaw/workspace/skills/multi-agent-suite").expanduser()

def load_data():
    """加载系统数据"""
    data = {
        'agents': [],
        'tasks': [],
        'stats': {}
    }
    
    # 加载Agent状态
    state_file = SUITE_DIR / "state.json"
    if state_file.exists():
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
            data['agents'] = list(state.get('agents', {}).values())
    
    # 加载任务
    tasks_file = SUITE_DIR / "tasks" / "workflow_tasks.json"
    if tasks_file.exists():
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
            data['tasks'] = list(tasks_data.values())
    
    # 统计
    data['stats'] = {
        'total_agents': len(data['agents']),
        'idle_agents': sum(1 for a in data['agents'] if a.get('status') == 'idle'),
        'busy_agents': sum(1 for a in data['agents'] if a.get('status') == 'busy'),
        'total_tasks': len(data['tasks']),
        'completed_tasks': sum(1 for t in data['tasks'] if t.get('completed_at')),
        'in_progress_tasks': sum(1 for t in data['tasks'] if not t.get('completed_at'))
    }
    
    return data

@app.route('/')
def dashboard():
    """主看板"""
    data = load_data()
    return render_template('dashboard.html', **data)

@app.route('/api/agents')
def api_agents():
    """API: 获取Agent列表"""
    data = load_data()
    return jsonify(data['agents'])

@app.route('/api/tasks')
def api_tasks():
    """API: 获取任务列表"""
    data = load_data()
    return jsonify(data['tasks'])

@app.route('/api/stats')
def api_stats():
    """API: 获取统计数据"""
    data = load_data()
    return jsonify(data['stats'])

@app.route('/api/task/<task_id>')
def api_task_detail(task_id):
    """API: 获取任务详情"""
    tasks_file = SUITE_DIR / "tasks" / "workflow_tasks.json"
    if tasks_file.exists():
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
            task = tasks.get(task_id)
            if task:
                return jsonify(task)
    return jsonify({'error': 'Task not found'}), 404

def main():
    print("🌐 启动Web管理界面...")
    print("📍 访问: http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == '__main__':
    main()
