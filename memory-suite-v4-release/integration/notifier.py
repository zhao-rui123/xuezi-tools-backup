#!/usr/bin/env python3
"""
通知系统 - 飞书通知支持
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger('memory-suite')

# 路径配置
WORKSPACE = Path("/home/user/workspace")
MEMORY_DIR = WORKSPACE / "memory"


class Notifier:
    """通知系统"""
    
    def __init__(self):
        self.notification_log = MEMORY_DIR / "notification_log.json"
    
    def send(self, title: str, message: str, level: str = "info") -> bool:
        """
        发送通知
        
        Args:
            title: 标题
            message: 消息内容
            level: 级别 (info/warning/error)
            
        Returns:
            是否成功
        """
        logger.info(f"发送通知：{title} - {message}")
        
        # 记录通知日志
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "title": title,
                "message": message
            }
            
            logs = []
            if self.notification_log.exists():
                import json
                with open(self.notification_log, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            
            logs.append(log_entry)
            
            with open(self.notification_log, 'w', encoding='utf-8') as f:
                import json
                json.dump(logs, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"发送通知失败：{e}")
            return False
    
    def send_error(self, task_name: str, error: str) -> bool:
        """发送错误通知"""
        return self.send(
            title=f"任务错误：{task_name}",
            message=str(error),
            level="error"
        )
