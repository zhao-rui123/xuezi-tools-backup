#!/usr/bin/env python3
"""
Memory Suite v3.0 - 集成层模块

提供与外部系统的集成能力：
- kb_sync: 知识库同步
- notifier: 通知系统
- backup_helper: 备份协助

作者: 雪子助手
版本: 3.0.0
日期: 2026-03-11
"""

__version__ = "3.0.0"
__author__ = "雪子助手"

from .kb_sync import KBSync, sync_memory_to_kb
from .notifier import Notifier
from .backup_helper import BackupHelper

__all__ = [
    "KBSync",
    "sync_memory_to_kb",
    "Notifier",
    "BackupHelper",
]


def get_integration_status():
    """获取集成层状态"""
    return {
        "version": __version__,
        "modules": {
            "kb_sync": "available",
            "notifier": "available",
            "backup_helper": "available",
        }
    }
