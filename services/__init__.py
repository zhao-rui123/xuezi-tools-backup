#!/usr/bin/env python3
"""
OpenClaw Services - 统一服务层
整合 Memory / Knowledge / Action / Skill / Monitor / Backup / Git / Notify
"""

__version__ = "1.0.0"
__author__ = "雪子助手"

# 服务注册表
SERVICES = {
    "memory": {
        "name": "Memory Service",
        "description": "实时记忆、语义搜索、上下文恢复",
        "modules": ["real_time_saver", "context_recovery", "semantic_search"]
    },
    "knowledge": {
        "name": "Knowledge Service", 
        "description": "智能提取、知识库管理",
        "modules": ["smart_extractor"]
    },
    "action": {
        "name": "Action Service",
        "description": "任务生成、周报、进度跟踪",
        "modules": ["task_generator", "weekly_reporter"]
    },
    "skill": {
        "name": "Skill Service",
        "description": "技能包版本、依赖、审计",
        "modules": ["skill_service"]
    },
    "script": {
        "name": "Script Service",
        "description": "统一CLI入口",
        "modules": ["unified_cli"]
    },
    "monitor": {
        "name": "Monitor Service",
        "description": "任务看板、日志聚合、健康报告",
        "modules": ["monitor_service"]
    },
    "backup": {
        "name": "Backup Service",
        "description": "智能去重、增量备份、自动清理",
        "modules": ["backup_service"]
    },
    "git": {
        "name": "Git Service",
        "description": "语义提交、变更摘要",
        "modules": ["git_service"]
    },
    "notify": {
        "name": "Notify Service",
        "description": "统一通知、分级发送",
        "modules": ["notify_service"]
    }
}

def get_service_info(service_name: str) -> dict:
    """获取服务信息"""
    return SERVICES.get(service_name, {})

def list_services() -> list:
    """列出所有服务"""
    return list(SERVICES.keys())
