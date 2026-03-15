#!/usr/bin/env python3
"""
Memory Suite v4.0 - 统一日志管理器
所有服务使用此模块记录日志，统一输出到 /tmp/memory-suite.log
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# 统一日志文件路径
UNIFIED_LOG_PATH = Path("/tmp/memory-suite.log")
MAX_LOG_SIZE_MB = 50  # 超过50MB触发轮转


class UnifiedLogger:
    """统一日志管理器"""
    
    LEVELS = {
        "DEBUG": ("🐛", "\033[36m"),      # 青色
        "INFO": ("ℹ️", "\033[34m"),       # 蓝色
        "SUCCESS": ("✅", "\033[32m"),    # 绿色
        "WARN": ("⚠️", "\033[33m"),       # 黄色
        "ERROR": ("❌", "\033[31m"),      # 红色
        "CRITICAL": ("🚨", "\033[35m"),   # 紫色
    }
    
    RESET = "\033[0m"
    
    def __init__(self, name: str = "memory-suite"):
        self.name = name
        self.log_file = UNIFIED_LOG_PATH
        
        # 确保日志目录存在
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
    def _check_rotation(self):
        """检查是否需要轮转"""
        if self.log_file.exists():
            size_mb = self.log_file.stat().st_size / (1024 * 1024)
            if size_mb > MAX_LOG_SIZE_MB:
                self._rotate_log()
                
    def _rotate_log(self):
        """执行日志轮转"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.log_file.parent / f"memory-suite-{timestamp}.log"
        
        try:
            # 重命名当前日志
            self.log_file.rename(backup_file)
            
            # 压缩备份
            import gzip
            with open(backup_file, 'rb') as f_in:
                with gzip.open(f"{backup_file}.gz", 'wb') as f_out:
                    import shutil
                    shutil.copyfileobj(f_in, f_out)
                    
            # 删除未压缩的备份
            backup_file.unlink()
            
            self._write_log("INFO", f"日志已轮转: {backup_file.name}.gz")
        except Exception as e:
            # 轮转失败，清空日志
            self.log_file.write_text("")
            self._write_log("WARN", f"日志轮转失败，已清空: {e}")
            
    def _write_log(self, level: str, message: str):
        """写入日志文件"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] [{self.name}] {message}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_line)
            
    def _console_output(self, level: str, message: str):
        """控制台输出 (带颜色)"""
        emoji, color = self.LEVELS.get(level, ("", ""))
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if sys.stdout.isatty():
            print(f"{color}[{timestamp}] {emoji} [{self.name}] {message}{self.RESET}")
        else:
            print(f"[{timestamp}] {emoji} [{self.name}] {message}")
            
    def log(self, level: str, message: str, console: bool = True):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG/INFO/SUCCESS/WARN/ERROR/CRITICAL)
            message: 日志消息
            console: 是否输出到控制台
        """
        level = level.upper()
        
        # 检查轮转
        self._check_rotation()
        
        # 写入文件
        self._write_log(level, message)
        
        # 控制台输出
        if console:
            self._console_output(level, message)
            
    def debug(self, message: str, console: bool = False):
        """调试日志"""
        self.log("DEBUG", message, console)
        
    def info(self, message: str, console: bool = True):
        """信息日志"""
        self.log("INFO", message, console)
        
    def success(self, message: str, console: bool = True):
        """成功日志"""
        self.log("SUCCESS", message, console)
        
    def warn(self, message: str, console: bool = True):
        """警告日志"""
        self.log("WARN", message, console)
        
    def error(self, message: str, console: bool = True):
        """错误日志"""
        self.log("ERROR", message, console)
        
    def critical(self, message: str, console: bool = True):
        """严重错误日志"""
        self.log("CRITICAL", message, console)


# 全局日志实例
_global_logger: Optional[UnifiedLogger] = None


def get_logger(name: str = "memory-suite") -> UnifiedLogger:
    """获取日志实例"""
    global _global_logger
    if _global_logger is None or _global_logger.name != name:
        _global_logger = UnifiedLogger(name)
    return _global_logger


def log(level: str, message: str, name: str = "memory-suite", console: bool = True):
    """快捷日志函数"""
    logger = get_logger(name)
    logger.log(level, message, console)


def debug(message: str, name: str = "memory-suite", console: bool = False):
    """快捷调试日志"""
    log("DEBUG", message, name, console)


def info(message: str, name: str = "memory-suite", console: bool = True):
    """快捷信息日志"""
    log("INFO", message, name, console)


def success(message: str, name: str = "memory-suite", console: bool = True):
    """快捷成功日志"""
    log("SUCCESS", message, name, console)


def warn(message: str, name: str = "memory-suite", console: bool = True):
    """快捷警告日志"""
    log("WARN", message, name, console)


def error(message: str, name: str = "memory-suite", console: bool = True):
    """快捷错误日志"""
    log("ERROR", message, name, console)


def critical(message: str, name: str = "memory-suite", console: bool = True):
    """快捷严重错误日志"""
    log("CRITICAL", message, name, console)


if __name__ == "__main__":
    # 测试日志功能
    logger = get_logger("test")
    
    logger.debug("这是一条调试日志", console=True)
    logger.info("这是一条信息日志")
    logger.success("这是一条成功日志")
    logger.warn("这是一条警告日志")
    logger.error("这是一条错误日志")
    logger.critical("这是一条严重错误日志")
    
    print(f"\n日志文件位置: {UNIFIED_LOG_PATH}")
    print(f"日志内容:\n{UNIFIED_LOG_PATH.read_text()}")
