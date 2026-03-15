#!/usr/bin/env python3
"""
系统监控看板 - Flask后端API
零Token消耗，只读本地文件
"""

import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from system_monitor import (
    get_system_status,
    get_memory_stats,
    get_cron_tasks,
    MemoryStatsReader,
    CronTasksReader,
    SystemHealthReader
)

# 创建Flask应用
app = Flask(__name__)

# 启用CORS，允许前端访问
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:*", "http://127.0.0.1:*", "file://*"],
        "methods": ["GET", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})


# ============ API路由 ============

@app.route('/')
def index():
    """API根路径 - 返回可用接口列表"""
    return jsonify({
        "name": "系统监控看板API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "/api/system/status": "系统整体状态（磁盘、内存、CPU、进程）",
            "/api/system/disk": "磁盘使用情况",
            "/api/system/memory": "内存使用情况",
            "/api/system/cpu": "CPU使用情况",
            "/api/system/processes": "进程信息",
            "/api/system/workspace": "工作空间统计",
            "/api/memory/stats": "Memory Suite完整统计",
            "/api/memory/skills": "技能记忆统计",
            "/api/memory/scores": "记忆评分统计",
            "/api/memory/files": "记忆文件状态",
            "/api/cron/tasks": "定时任务完整列表",
            "/api/cron/crontab": "系统crontab任务",
            "/api/cron/managed": "Cron Manager管理的任务",
            "/api/cron/logs": "定时任务日志状态",
            "/api/health": "API健康检查"
        }
    })


@app.route('/api/health')
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "dashboard-backend"
    })


# ============ 系统状态API ============

@app.route('/api/system/status')
def api_system_status():
    """
    获取系统整体状态
    包含：磁盘、内存、CPU、进程、工作空间
    """
    try:
        data = get_system_status()
        return jsonify({
            "success": True,
            "data": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/system/disk')
def api_system_disk():
    """获取磁盘使用情况"""
    try:
        data = SystemHealthReader.get_disk_usage()
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/system/memory')
def api_system_memory():
    """获取内存使用情况"""
    try:
        data = SystemHealthReader.get_memory_usage()
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/system/cpu')
def api_system_cpu():
    """获取CPU使用情况"""
    try:
        data = SystemHealthReader.get_cpu_usage()
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/system/processes')
def api_system_processes():
    """获取进程信息"""
    try:
        data = SystemHealthReader.get_processes()
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/system/workspace')
def api_system_workspace():
    """获取工作空间统计"""
    try:
        data = SystemHealthReader.get_workspace_stats()
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============ Memory Suite API ============

@app.route('/api/memory/stats')
def api_memory_stats():
    """
    获取Memory Suite完整统计
    包含：技能记忆、评分统计、文件状态
    """
    try:
        data = get_memory_stats()
        return jsonify({
            "success": True,
            "data": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/memory/skills')
def api_memory_skills():
    """获取技能记忆统计"""
    try:
        data = MemoryStatsReader.get_skill_memory()
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/memory/scores')
def api_memory_scores():
    """获取记忆评分统计"""
    try:
        data = MemoryStatsReader.get_memory_scores()
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/memory/files')
def api_memory_files():
    """获取记忆文件状态"""
    try:
        data = MemoryStatsReader.get_memory_files_status()
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============ 定时任务API ============

@app.route('/api/cron/tasks')
def api_cron_tasks():
    """
    获取定时任务完整列表
    包含：crontab任务、Cron Manager任务、日志状态
    """
    try:
        data = get_cron_tasks()
        return jsonify({
            "success": True,
            "data": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/cron/crontab')
def api_cron_crontab():
    """获取系统crontab任务"""
    try:
        data = CronTasksReader.get_crontab_tasks()
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/cron/managed')
def api_cron_managed():
    """获取Cron Manager管理的任务"""
    try:
        data = CronTasksReader.get_cron_manager_tasks()
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/cron/logs')
def api_cron_logs():
    """获取定时任务日志状态"""
    try:
        data = CronTasksReader.get_cron_logs()
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============ 错误处理 ============

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "接口不存在",
        "available_endpoints": [
            "/api/system/status",
            "/api/memory/stats",
            "/api/cron/tasks",
            "/api/health"
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "服务器内部错误"
    }), 500


# ============ 启动服务 ============

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='系统监控看板后端API')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='监听端口 (默认: 5000)')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    print(f"🚀 系统监控看板API启动中...")
    print(f"📍 地址: http://{args.host}:{args.port}")
    print(f"📋 API文档: http://{args.host}:{args.port}/")
    print(f"❤️  健康检查: http://{args.host}:{args.port}/api/health")
    print("")
    print("可用接口:")
    print("  GET /api/system/status  - 系统整体状态")
    print("  GET /api/memory/stats   - Memory Suite统计")
    print("  GET /api/cron/tasks     - 定时任务列表")
    
    app.run(host=args.host, port=args.port, debug=args.debug)
