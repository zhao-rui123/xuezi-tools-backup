#!/usr/bin/env python3
"""
Web管理界面 - 多Agent协作系统可视化看板 v2.0
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime

from core.workflow import DevelopmentWorkflow
from core.orchestrator import AgentOrchestrator
from core.task_dag import TaskDAG

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

SUITE_DIR = Path("~/.openclaw/workspace/skills/multi-agent-suite").expanduser()

@app.route('/')
def index():
    """主页"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API状态"""
    return jsonify({
        'status': 'ok',
        'version': '2.0',
        'agents': 11,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/agents')
def api_agents():
    """获取Agent列表"""
    return jsonify({'agents': []})

@app.route('/api/tasks')
def api_tasks():
    """获取任务列表"""
    return jsonify({'tasks': []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
