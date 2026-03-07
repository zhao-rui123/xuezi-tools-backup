#!/usr/bin/env python3
"""
基础审计日志 - 记录关键操作便于追溯
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional

# 日志配置
LOG_DIR = os.path.expanduser("~/.openclaw/.logs")
AUDIT_LOG = os.path.join(LOG_DIR, "audit.log")
MAX_LOG_DAYS = 30  # 保留30天日志

class AuditLogger:
    """审计日志器"""
    
    def __init__(self):
        self.ensure_log_dir()
    
    def ensure_log_dir(self):
        """确保日志目录存在"""
        os.makedirs(LOG_DIR, exist_ok=True)
    
    def log(self, action: str, details: str = "", level: str = "INFO"):
        """
        记录操作日志
        
        Args:
            action: 操作类型（如 file_delete, message_send）
            details: 详细描述
            level: 日志级别（INFO/WARNING/ERROR）
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_entry = {
            'timestamp': timestamp,
            'action': action,
            'details': details,
            'level': level,
            'session': os.environ.get('OPENCLAW_SESSION', 'unknown')[:8]
        }
        
        # 写入日志文件
        with open(AUDIT_LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def log_file_operation(self, operation: str, filepath: str, result: str = "success"):
        """记录文件操作"""
        self.log(
            action=f'file_{operation}',
            details=f'path: {filepath}, result: {result}',
            level='WARNING' if operation in ['delete', 'modify'] else 'INFO'
        )
    
    def log_command(self, command: str, status: str = "executed"):
        """记录命令执行"""
        # 截断过长的命令
        cmd_short = command[:100] + '...' if len(command) > 100 else command
        self.log(
            action='command_execute',
            details=f'cmd: {cmd_short}, status: {status}',
            level='INFO'
        )
    
    def log_message_send(self, channel: str, target: str, has_attachment: bool = False):
        """记录消息发送"""
        self.log(
            action='message_send',
            details=f'channel: {channel}, target: {target}, attachment: {has_attachment}',
            level='INFO'
        )
    
    def log_skill_operation(self, operation: str, skill_name: str):
        """记录技能包操作"""
        self.log(
            action=f'skill_{operation}',
            details=f'skill: {skill_name}',
            level='WARNING' if operation in ['delete', 'modify'] else 'INFO'
        )
    
    def log_error(self, error_type: str, message: str):
        """记录错误"""
        self.log(
            action='error',
            details=f'type: {error_type}, msg: {message}',
            level='ERROR'
        )
    
    def query_recent(self, hours: int = 24, action_filter: str = None) -> list:
        """
        查询最近日志
        
        Args:
            hours: 查询最近几小时
            action_filter: 按操作类型过滤
        """
        if not os.path.exists(AUDIT_LOG):
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        results = []
        
        with open(AUDIT_LOG, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    entry_time = datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S')
                    
                    if entry_time < cutoff_time:
                        continue
                    
                    if action_filter and not entry['action'].startswith(action_filter):
                        continue
                    
                    results.append(entry)
                except:
                    continue
        
        return results
    
    def cleanup_old_logs(self):
        """清理旧日志"""
        if not os.path.exists(AUDIT_LOG):
            return
        
        cutoff_time = datetime.now() - timedelta(days=MAX_LOG_DAYS)
        temp_file = AUDIT_LOG + '.tmp'
        
        kept_count = 0
        removed_count = 0
        
        with open(AUDIT_LOG, 'r', encoding='utf-8') as f_in:
            with open(temp_file, 'w', encoding='utf-8') as f_out:
                for line in f_in:
                    try:
                        entry = json.loads(line.strip())
                        entry_time = datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S')
                        
                        if entry_time >= cutoff_time:
                            f_out.write(line)
                            kept_count += 1
                        else:
                            removed_count += 1
                    except:
                        f_out.write(line)  # 保留格式错误的行
        
        # 替换原文件
        os.replace(temp_file, AUDIT_LOG)
        
        return {'kept': kept_count, 'removed': removed_count}
    
    def generate_report(self, hours: int = 24) -> str:
        """生成审计报告"""
        logs = self.query_recent(hours)
        
        if not logs:
            return "📋 最近无操作记录"
        
        # 统计
        action_counts = {}
        error_count = 0
        
        for log in logs:
            action = log['action']
            action_counts[action] = action_counts.get(action, 0) + 1
            if log['level'] == 'ERROR':
                error_count += 1
        
        lines = [
            f"📊 审计报告（最近{hours}小时）",
            f"=" * 50,
            f"总操作数: {len(logs)}",
            f"错误数: {error_count}",
            f"",
            f"操作分布:",
        ]
        
        for action, count in sorted(action_counts.items(), key=lambda x: -x[1]):
            lines.append(f"  - {action}: {count}次")
        
        # 显示最近的错误
        if error_count > 0:
            lines.extend([f"", f"⚠️ 最近错误:"])
            for log in logs:
                if log['level'] == 'ERROR':
                    lines.append(f"  [{log['timestamp']}] {log['details'][:50]}")
        
        return "\n".join(lines)

# 全局日志实例
_audit_logger = None

def get_logger() -> AuditLogger:
    """获取日志器实例"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger

# 便捷函数
def log_action(action: str, details: str = "", level: str = "INFO"):
    """记录操作"""
    get_logger().log(action, details, level)

def log_file(operation: str, filepath: str, result: str = "success"):
    """记录文件操作"""
    get_logger().log_file_operation(operation, filepath, result)

def log_command(command: str, status: str = "executed"):
    """记录命令执行"""
    get_logger().log_command(command, status)

def show_recent_logs(hours: int = 24):
    """显示最近日志"""
    logger = get_logger()
    print(logger.generate_report(hours))

def cleanup_logs():
    """清理旧日志"""
    logger = get_logger()
    result = logger.cleanup_old_logs()
    print(f"🧹 日志清理完成: 保留 {result['kept']} 条, 删除 {result['removed']} 条")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'report':
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            show_recent_logs(hours)
        elif cmd == 'cleanup':
            cleanup_logs()
        elif cmd == 'test':
            # 测试日志
            log_action('test', '测试日志功能')
            log_file('read', '~/.openclaw/test.txt')
            log_command('ls -la')
            print("✅ 测试日志已写入")
            show_recent_logs(1)
    else:
        print("用法:")
        print("  python3 audit_logger.py report [hours]  # 生成报告")
        print("  python3 audit_logger.py cleanup          # 清理旧日志")
        print("  python3 audit_logger.py test             # 测试日志")
