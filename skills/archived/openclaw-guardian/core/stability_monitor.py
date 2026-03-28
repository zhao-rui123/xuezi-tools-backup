"""
稳定性监控器 - 监控系统运行状态
==================================

提供系统稳定性监控功能:
- CPU使用率监控
- 内存使用监控
- 磁盘空间监控
- 进程状态监控
- 自动资源释放
"""

import os
import sys
import time
import psutil
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging


@dataclass
class ResourceUsage:
    """资源使用情况"""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_available_mb: float = 0.0
    disk_percent: float = 0.0
    disk_free_gb: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Alert:
    """警报信息"""
    level: str  # info, warning, critical
    component: str  # cpu, memory, disk
    message: str
    value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.now)


class StabilityMonitor:
    """稳定性监控器类"""
    
    # 默认阈值
    DEFAULT_THRESHOLDS = {
        'cpu_warning': 70.0,
        'cpu_critical': 90.0,
        'memory_warning': 75.0,
        'memory_critical': 90.0,
        'disk_warning': 80.0,
        'disk_critical': 95.0,
    }
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化稳定性监控器
        
        Args:
            config: 监控配置
        """
        self.config = config or {}
        self.thresholds = {**self.DEFAULT_THRESHOLDS, **self.config.get('thresholds', {})}
        
        self.logger = logging.getLogger("StabilityMonitor")
        
        # 监控状态
        self._running = False
        self._monitor_thread = None
        self._check_interval = self.config.get('check_interval', 5)
        
        # 历史数据
        self._history: List[ResourceUsage] = []
        self._max_history = self.config.get('max_history', 1000)
        
        # 警报
        self._alerts: List[Alert] = []
        self._max_alerts = self.config.get('max_alerts', 100)
        self._alert_handlers: List[Callable] = []
        
        # 进程监控
        self._monitored_processes: Dict[int, Dict] = {}
        
        # 自动保护
        self._auto_protect = self.config.get('auto_protect', True)
        self._protection_actions = []
    
    def start(self) -> None:
        """启动监控"""
        if self._running:
            return
        
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        
        self.logger.info("稳定性监控已启动")
    
    def stop(self) -> None:
        """停止监控"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        
        self.logger.info("稳定性监控已停止")
    
    def check_resources(self) -> Dict[str, Any]:
        """
        检查系统资源状态
        
        Returns:
            资源状态报告
        """
        usage = self._get_current_usage()
        
        status = 'healthy'
        issues = []
        
        # 检查CPU
        if usage.cpu_percent > self.thresholds['cpu_critical']:
            status = 'critical'
            issues.append(f"CPU使用率过高: {usage.cpu_percent:.1f}%")
        elif usage.cpu_percent > self.thresholds['cpu_warning']:
            if status == 'healthy':
                status = 'warning'
            issues.append(f"CPU使用率警告: {usage.cpu_percent:.1f}%")
        
        # 检查内存
        if usage.memory_percent > self.thresholds['memory_critical']:
            status = 'critical'
            issues.append(f"内存使用率过高: {usage.memory_percent:.1f}%")
        elif usage.memory_percent > self.thresholds['memory_warning']:
            if status == 'healthy':
                status = 'warning'
            issues.append(f"内存使用率警告: {usage.memory_percent:.1f}%")
        
        # 检查磁盘
        if usage.disk_percent > self.thresholds['disk_critical']:
            status = 'critical'
            issues.append(f"磁盘使用率过高: {usage.disk_percent:.1f}%")
        elif usage.disk_percent > self.thresholds['disk_warning']:
            if status == 'healthy':
                status = 'warning'
            issues.append(f"磁盘使用率警告: {usage.disk_percent:.1f}%")
        
        return {
            'status': status,
            'usage': {
                'cpu_percent': usage.cpu_percent,
                'memory_percent': usage.memory_percent,
                'memory_available_mb': usage.memory_available_mb,
                'disk_percent': usage.disk_percent,
                'disk_free_gb': usage.disk_free_gb,
            },
            'issues': issues,
        }
    
    def get_current_usage(self) -> ResourceUsage:
        """获取当前资源使用情况"""
        return self._get_current_usage()
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """
        获取历史使用数据
        
        Args:
            limit: 返回记录数
            
        Returns:
            历史数据列表
        """
        history = self._history[-limit:] if limit > 0 else self._history
        return [
            {
                'cpu_percent': h.cpu_percent,
                'memory_percent': h.memory_percent,
                'memory_available_mb': h.memory_available_mb,
                'disk_percent': h.disk_percent,
                'disk_free_gb': h.disk_free_gb,
                'timestamp': h.timestamp.isoformat(),
            }
            for h in history
        ]
    
    def get_alerts(self, level: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """
        获取警报列表
        
        Args:
            level: 过滤警报级别
            limit: 返回记录数
            
        Returns:
            警报列表
        """
        alerts = self._alerts
        if level:
            alerts = [a for a in alerts if a.level == level]
        alerts = alerts[-limit:] if limit > 0 else alerts
        
        return [
            {
                'level': a.level,
                'component': a.component,
                'message': a.message,
                'value': a.value,
                'threshold': a.threshold,
                'timestamp': a.timestamp.isoformat(),
            }
            for a in alerts
        ]
    
    def free_memory(self) -> Dict[str, Any]:
        """
        释放内存
        
        Returns:
            释放结果
        """
        result = {
            'freed_mb': 0,
            'actions': [],
        }
        
        try:
            # 1. 强制垃圾回收
            import gc
            gc.collect()
            result['actions'].append('执行垃圾回收')
            
            # 2. 清理缓存（如果可能）
            # 这里可以添加特定的缓存清理逻辑
            
            # 3. 获取释放后的内存状态
            memory = psutil.virtual_memory()
            result['memory_after'] = {
                'percent': memory.percent,
                'available_mb': memory.available / 1024 / 1024,
            }
            
            self.logger.info(f"内存释放完成，当前使用率: {memory.percent:.1f}%")
            
        except Exception as e:
            self.logger.error(f"内存释放失败: {e}")
            result['error'] = str(e)
        
        return result
    
    def monitor_process(self, pid: int, name: str = None) -> None:
        """
        监控指定进程
        
        Args:
            pid: 进程ID
            name: 进程名称
        """
        self._monitored_processes[pid] = {
            'name': name or f'process_{pid}',
            'start_time': datetime.now(),
            'history': [],
        }
        self.logger.info(f"开始监控进程: {name or pid} (PID: {pid})")
    
    def get_process_status(self, pid: int) -> Optional[Dict]:
        """获取进程状态"""
        if pid not in self._monitored_processes:
            return None
        
        try:
            proc = psutil.Process(pid)
            info = {
                'pid': pid,
                'name': proc.name(),
                'status': proc.status(),
                'cpu_percent': proc.cpu_percent(interval=0.1),
                'memory_percent': proc.memory_percent(),
                'memory_mb': proc.memory_info().rss / 1024 / 1024,
                'create_time': datetime.fromtimestamp(proc.create_time()).isoformat(),
            }
            return info
        except psutil.NoSuchProcess:
            return {'error': '进程不存在', 'pid': pid}
        except Exception as e:
            return {'error': str(e), 'pid': pid}
    
    def register_alert_handler(self, handler: Callable) -> None:
        """注册警报处理器"""
        self._alert_handlers.append(handler)
    
    def _monitor_loop(self) -> None:
        """监控循环"""
        while self._running:
            try:
                # 获取当前资源使用
                usage = self._get_current_usage()
                
                # 保存历史
                self._history.append(usage)
                if len(self._history) > self._max_history:
                    self._history = self._history[-self._max_history:]
                
                # 检查阈值并生成警报
                self._check_thresholds(usage)
                
                # 监控指定进程
                self._check_monitored_processes()
                
                # 自动保护
                if self._auto_protect:
                    self._auto_protection(usage)
                
                time.sleep(self._check_interval)
                
            except Exception as e:
                self.logger.error(f"监控循环出错: {e}")
                time.sleep(1)
    
    def _get_current_usage(self) -> ResourceUsage:
        """获取当前资源使用"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # 内存使用
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_mb = memory.available / 1024 / 1024
        
        # 磁盘使用
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        disk_free_gb = disk.free / 1024 / 1024 / 1024
        
        return ResourceUsage(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_available_mb=memory_available_mb,
            disk_percent=disk_percent,
            disk_free_gb=disk_free_gb,
        )
    
    def _check_thresholds(self, usage: ResourceUsage) -> None:
        """检查阈值并生成警报"""
        # CPU警报
        if usage.cpu_percent > self.thresholds['cpu_critical']:
            self._add_alert('critical', 'cpu', f"CPU使用率严重: {usage.cpu_percent:.1f}%", usage.cpu_percent, self.thresholds['cpu_critical'])
        elif usage.cpu_percent > self.thresholds['cpu_warning']:
            self._add_alert('warning', 'cpu', f"CPU使用率警告: {usage.cpu_percent:.1f}%", usage.cpu_percent, self.thresholds['cpu_warning'])
        
        # 内存警报
        if usage.memory_percent > self.thresholds['memory_critical']:
            self._add_alert('critical', 'memory', f"内存使用率严重: {usage.memory_percent:.1f}%", usage.memory_percent, self.thresholds['memory_critical'])
        elif usage.memory_percent > self.thresholds['memory_warning']:
            self._add_alert('warning', 'memory', f"内存使用率警告: {usage.memory_percent:.1f}%", usage.memory_percent, self.thresholds['memory_warning'])
        
        # 磁盘警报
        if usage.disk_percent > self.thresholds['disk_critical']:
            self._add_alert('critical', 'disk', f"磁盘使用率严重: {usage.disk_percent:.1f}%", usage.disk_percent, self.thresholds['disk_critical'])
        elif usage.disk_percent > self.thresholds['disk_warning']:
            self._add_alert('warning', 'disk', f"磁盘使用率警告: {usage.disk_percent:.1f}%", usage.disk_percent, self.thresholds['disk_warning'])
    
    def _add_alert(self, level: str, component: str, message: str, value: float, threshold: float) -> None:
        """添加警报"""
        alert = Alert(
            level=level,
            component=component,
            message=message,
            value=value,
            threshold=threshold,
        )
        
        self._alerts.append(alert)
        if len(self._alerts) > self._max_alerts:
            self._alerts = self._alerts[-self._max_alerts:]
        
        # 触发警报处理器
        for handler in self._alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"警报处理器出错: {e}")
        
        # 记录日志
        if level == 'critical':
            self.logger.error(message)
        elif level == 'warning':
            self.logger.warning(message)
    
    def _check_monitored_processes(self) -> None:
        """检查监控的进程"""
        for pid in list(self._monitored_processes.keys()):
            status = self.get_process_status(pid)
            if 'error' in status:
                self.logger.warning(f"监控的进程异常: PID {pid} - {status['error']}")
    
    def _auto_protection(self, usage: ResourceUsage) -> None:
        """自动保护措施"""
        # 如果内存严重不足，执行保护
        if usage.memory_percent > self.thresholds['memory_critical']:
            self.logger.warning("内存严重不足，执行自动保护...")
            self.free_memory()
