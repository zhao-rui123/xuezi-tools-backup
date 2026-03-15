#!/usr/bin/env python3
"""
Web管理界面 - 多Agent协作系统可视化看板 v2.0
功能：任务看板、Agent状态监控、实时统计
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, jsonify, request
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

SUITE_DIR = Path("~/.openclaw/workspace/skills/multi-agent-suite").expanduser()

def load_state():
    """加载系统状态"""
    state_file = SUITE_DIR / "state.json"
    if state_file.exists():
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {'agents': {}, 'tasks': {}, 'subtasks': {}}

def load_tasks():
    """加载工作流任务"""
    tasks_file = SUITE_DIR / "tasks" / "workflow_tasks.json"
    if tasks_file.exists():
        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}

def load_data():
    """加载系统数据"""
    data = {
        'agents': [],
        'tasks': [],
        'workflow_tasks': [],
        'stats': {}
    }

    state = load_state()
    data['agents'] = list(state.get('agents', {}).values())

    tasks_file = SUITE_DIR / "tasks" / "workflow_tasks.json"
    if tasks_file.exists():
        with open(tasks_file, 'r', encoding='utf-8') as f:
            data['workflow_tasks'] = list(json.load(f).values())

    idle = sum(1 for a in data['agents'] if a.get('status') == 'idle')
    busy = sum(1 for a in data['agents'] if a.get('status') == 'busy')

    data['stats'] = {
        'total_agents': len(data['agents']),
        'idle_agents': idle,
        'busy_agents': busy,
        'total_tasks': len(data['workflow_tasks']),
        'completed_tasks': sum(1 for t in data['workflow_tasks'] if t.get('completed_at')),
        'in_progress_tasks': sum(1 for t in data['workflow_tasks'] if not t.get('completed_at'))
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
    state = load_state()
    agents = list(state.get('agents', {}).values())
    return jsonify(agents)

@app.route('/api/tasks')
def api_tasks():
    """API: 获取工作流任务列表"""
    tasks = load_tasks()
    return jsonify(list(tasks.values()))

@app.route('/api/stats')
def api_stats():
    """API: 获取统计数据"""
    data = load_data()
    return jsonify(data['stats'])

@app.route('/api/task/<task_id>')
def api_task_detail(task_id):
    """API: 获取任务详情"""
    tasks = load_tasks()
    task = tasks.get(task_id)
    if task:
        return jsonify(task)
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/health')
def api_health():
    """API: 健康检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0'
    })

@app.route('/api/create-task', methods=['POST'])
def api_create_task():
    """API: 创建任务"""
    data = request.get_json()
    title = data.get('title', '新任务')
    description = data.get('description', '')

    from core.workflow import DevelopmentWorkflow
    workflow = DevelopmentWorkflow()
    task_id = workflow.create_task(title, description, [])

    return jsonify({'success': True, 'task_id': task_id})

def main():
    print("🌐 启动Web管理界面 v2.0...")
    print("📍 访问: http://localhost:8080")
    print("🔄 支持实时数据刷新")
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == '__main__':
    main()
