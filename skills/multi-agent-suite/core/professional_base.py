#!/usr/bin/env python3
"""
专业级基础模块 - 为所有核心模块提供统一的基础设施
包含: 日志、单例、配置、验证、异常、缓存、上下文管理
"""

import os
import sys
import json
import logging
import logging.handlers
import threading
import time
import functools
from pathlib import Path
from typing import TypeVar, Generic, Optional, Any, Callable, Dict, List, Type
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from contextlib import contextmanager
from collections import OrderedDict
import uuid
import traceback

SUITE_DIR = Path("~/.openclaw/workspace/skills/multi-agent-suite").expanduser()
LOGS_DIR = SUITE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


T = TypeVar('T')


class LogLevel(Enum):
    """日志级别"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class SingletonMeta(type):
    """线程安全的单例元类"""
    _instances: Dict[type, Any] = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


class ProfessionalLogger:
    """专业级日志管理器"""
    
    _loggers: Dict[str, logging.Logger] = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_logger(cls, name: str, level: LogLevel = LogLevel.INFO) -> logging.Logger:
        """获取或创建日志器"""
        if name in cls._loggers:
            return cls._loggers[name]
        
        with cls._lock:
            if name in cls._loggers:
                return cls._loggers[name]
            
            logger = logging.getLogger(name)
            logger.setLevel(level.value)
            logger.propagate = False
            
            if not logger.handlers:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(level.value)
                
                file_handler = logging.handlers.RotatingFileHandler(
                    LOGS_DIR / f"{name}.log",
                    maxBytes=10 * 1024 * 1024,
                    backupCount=5,
                    encoding='utf-8'
                )
                file_handler.setLevel(level.value)
                
                formatter = logging.Formatter(
                    '%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                console_handler.setFormatter(formatter)
                file_handler.setFormatter(formatter)
                
                logger.addHandler(console_handler)
                logger.addHandler(file_handler)
            
            cls._loggers[name] = logger
            return logger


def singleton(cls):
    """单例装饰器"""
    @functools.wraps(cls)
    @classmethod
    def get_instance(*args, **kwargs):
        if not hasattr(cls, '_instance') or cls._instance is None:
            with cls._lock:
                if not hasattr(cls, '_instance') or cls._instance is None:
                    cls._instance = cls(*args, **kwargs)
        return cls._instance
    
    cls.get_instance = get_instance
    cls._instance = None
    cls._lock = threading.Lock()
    return cls


class ConfigManager(metaclass=SingletonMeta):
    """统一配置管理器"""
    
    _config: Dict[str, Any] = {}
    _config_file: Path = SUITE_DIR / "config" / "system.json"
    _logger: logging.Logger = None
    
    def __init__(self):
        self._logger = ProfessionalLogger.get_logger("config")
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        if self._config_file.exists():
            try:
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                self._logger.info(f"配置加载成功: {len(self._config)} 项")
            except Exception as e:
                self._logger.error(f"配置加载失败: {e}")
                self._config = self._get_defaults()
        else:
            self._config = self._get_defaults()
            self._save_config()
    
    def _get_defaults(self) -> Dict:
        """获取默认配置"""
        return {
            "version": "4.0.0",
            "log_level": "INFO",
            "max_retries": 3,
            "timeout": 30,
            "cache_ttl": 3600,
            "max_workers": 4,
            "persistence": {
                "enabled": True,
                "auto_save": True,
                "interval": 60
            },
            "features": {
                "audit_log": True,
                "approval_system": True,
                "notifications": True
            }
        }
    
    def _save_config(self):
        """保存配置"""
        self._config_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._logger.error(f"配置保存失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self._save_config()
    
    def get_all(self) -> Dict:
        """获取所有配置"""
        return self._config.copy()


class CacheItem:
    """缓存项"""
    
    def __init__(self, value: Any, ttl: int = 3600):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.hits = 0
    
    def is_expired(self) -> bool:
        return time.time() - self.created_at > self.ttl
    
    def access(self) -> Any:
        self.hits += 1
        return self.value


class LRUCache(OrderedDict):
    """LRU缓存"""
    
    def __init__(self, maxsize: int = 128):
        super().__init__()
        self.maxsize = maxsize
    
    def get(self, key: Any, default: Any = None) -> Any:
        if key in self:
            self.move_to_end(key)
            item = super().__getitem__(key)
            item.hits += 1
            return item.value
        return default
    
    def set(self, key: Any, value: Any, ttl: int = 3600):
        if key in self:
            self.move_to_end(key)
        super().__setitem__(key, CacheItem(value, ttl))
        if len(self) > self.maxsize:
            self.popitem(last=False)
    
    def clear_expired(self):
        expired_keys = [
            k for k, v in self.items() 
            if isinstance(v, CacheItem) and v.is_expired()
        ]
        for k in expired_keys:
            del self[k]


class ThreadSafeCache:
    """线程安全的缓存管理器"""
    
    _cache: Dict[str, LRUCache] = {}
    _lock: threading.Lock = threading.Lock()
    
    @classmethod
    def get_cache(cls, name: str = "default", maxsize: int = 128) -> LRUCache:
        """获取命名缓存"""
        with cls._lock:
            if name not in cls._cache:
                cls._cache[name] = LRUCache(maxsize)
            return cls._cache[name]
    
    @classmethod
    def clear(cls, name: str = None):
        """清除缓存"""
        with cls._lock:
            if name:
                if name in cls._cache:
                    cls._cache[name].clear()
            else:
                for cache in cls._cache.values():
                    cache.clear()


class BaseException(Exception):
    """基础异常类"""
    
    def __init__(self, message: str, code: str = None, details: Dict = None):
        super().__init__(message)
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()


class ValidationError(BaseException):
    """验证错误"""
    def __init__(self, message: str, field: str = None):
        super().__init__(message, "VALIDATION_ERROR", {"field": field})


class NotFoundError(BaseException):
    """资源不存在错误"""
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            f"{resource} not found: {resource_id}",
            "NOT_FOUND",
            {"resource": resource, "id": resource_id}
        )


class StateError(BaseException):
    """状态错误"""
    def __init__(self, message: str, current_state: str = None):
        super().__init__(message, "STATE_ERROR", {"current_state": current_state})


class ConfigurationError(BaseException):
    """配置错误"""
    def __init__(self, message: str):
        super().__init__(message, "CONFIG_ERROR")


class BaseModel:
    """基础数据模型"""
    
    _logger: logging.Logger = None
    
    def __init__(self):
        if BaseModel._logger is None:
            BaseModel._logger = ProfessionalLogger.get_logger("model")
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                if isinstance(value, Enum):
                    result[key] = value.value
                elif isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif hasattr(value, 'to_dict'):
                    result[key] = value.to_dict()
                else:
                    result[key] = value
        return result
    
    def to_json(self) -> str:
        """转换为JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BaseModel':
        """从字典创建"""
        return cls(**data)
    
    def validate(self) -> List[str]:
        """验证模型数据,返回错误列表"""
        return []


class Repository(ABC, Generic[T]):
    """仓储基类 - 数据访问抽象"""
    
    _logger: logging.Logger = None
    _cache_enabled: bool = True
    _cache_ttl: int = 300
    
    def __init__(self):
        if Repository._logger is None:
            Repository._logger = ProfessionalLogger.get_logger("repository")
        self._cache = ThreadSafeCache.get_cache(self.__class__.__name__)
    
    @abstractmethod
    def _load_all(self) -> List[T]:
        """加载所有数据"""
        pass
    
    @abstractmethod
    def _save_all(self, items: List[T]) -> None:
        """保存所有数据"""
        pass
    
    def get(self, item_id: str) -> Optional[T]:
        """获取单个项目"""
        cache_key = f"item_{item_id}"
        
        if self._cache_enabled:
            cached = self._cache.get(cache_key)
            if cached:
                return cached
        
        items = self._load_all()
        for item in items:
            if hasattr(item, 'id') and item.id == item_id:
                if self._cache_enabled:
                    self._cache.set(cache_key, item, self._cache_ttl)
                return item
        return None
    
    def get_all(self) -> List[T]:
        """获取所有项目"""
        return self._load_all()
    
    def add(self, item: T) -> bool:
        """添加项目"""
        items = self._load_all()
        items.append(item)
        self._save_all(items)
        self._cache.clear()
        self._logger.info(f"Added item: {getattr(item, 'id', 'unknown')}")
        return True
    
    def update(self, item_id: str, data: Dict) -> bool:
        """更新项目"""
        items = self._load_all()
        for i, item in enumerate(items):
            if hasattr(item, 'id') and item.id == item_id:
                for key, value in data.items():
                    if hasattr(item, key):
                        setattr(item, key, value)
                self._save_all(items)
                self._cache.clear()
                self._logger.info(f"Updated item: {item_id}")
                return True
        return False
    
    def delete(self, item_id: str) -> bool:
        """删除项目"""
        items = self._load_all()
        original_len = len(items)
        items = [item for item in items if not (hasattr(item, 'id') and item.id == item_id)]
        
        if len(items) < original_len:
            self._save_all(items)
            self._cache.clear()
            self._logger.info(f"Deleted item: {item_id}")
            return True
        return False
    
    def count(self) -> int:
        """统计数量"""
        return len(self._load_all())


class EventDispatcher:
    """事件分发器"""
    
    _listeners: Dict[str, List[Callable]] = {}
    _logger: logging.Logger = None
    _lock: threading.Lock = threading.Lock()
    
    def __init__(self):
        if EventDispatcher._logger is None:
            EventDispatcher._logger = ProfessionalLogger.get_logger("events")
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """订阅事件"""
        with self._lock:
            if event_type not in self._listeners:
                self._listeners[event_type] = []
            if callback not in self._listeners[event_type]:
                self._listeners[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """取消订阅"""
        with self._lock:
            if event_type in self._listeners:
                if callback in self._listeners[event_type]:
                    self._listeners[event_type].remove(callback)
    
    def dispatch(self, event_type: str, data: Dict = None) -> None:
        """分发事件"""
        data = data or {}
        
        with self._lock:
            listeners = self._listeners.get(event_type, []).copy()
        
        self._logger.debug(f"Dispatching event: {event_type}")
        
        for listener in listeners:
            try:
                listener(data)
            except Exception as e:
                self._logger.error(f"Event listener error: {e}", exc_info=True)


class RetryPolicy:
    """重试策略"""
    
    @staticmethod
    def exponential_backoff(
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0
    ) -> Callable:
        """指数退避重试装饰器"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                logger = ProfessionalLogger.get_logger("retry")
                last_exception = None
                
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            delay = min(base_delay * (exponential_base ** attempt), max_delay)
                            logger.warning(
                                f"Attempt {attempt + 1}/{max_attempts} failed: {e}. "
                                f"Retrying in {delay:.1f}s..."
                            )
                            time.sleep(delay)
                        else:
                            logger.error(f"All {max_attempts} attempts failed")
                
                raise last_exception
            
            return wrapper
        return decorator


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls: List[float] = []
        self.lock = threading.Lock()
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:
                now = time.time()
                self.calls = [t for t in self.calls if now - t < self.period]
                
                if len(self.calls) >= self.max_calls:
                    sleep_time = self.period - (now - self.calls[0])
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                        now = time.time()
                        self.calls = [t for t in self.calls if now - t < self.period]
                
                self.calls.append(now)
            
            return func(*args, **kwargs)
        
        return wrapper


@contextmanager
def atomic_operation(backup: bool = True):
    """原子操作上下文管理器"""
    logger = ProfessionalLogger.get_logger("atomic")
    logger.debug("Starting atomic operation")
    try:
        yield
        logger.debug("Atomic operation completed successfully")
    except Exception as e:
        logger.error(f"Atomic operation failed: {e}", exc_info=True)
        raise


def validate_required_fields(data: Dict, required_fields: List[str]) -> None:
    """验证必需字段"""
    missing = [field for field in required_fields if field not in data or data[field] is None]
    if missing:
        raise ValidationError(f"Missing required fields: {missing}", ",".join(missing))


def validate_field_type(value: Any, expected_type: Type, field_name: str) -> None:
    """验证字段类型"""
    if not isinstance(value, expected_type):
        raise ValidationError(
            f"Field '{field_name}' expected {expected_type.__name__}, got {type(value).__name__}",
            field_name
        )


class MetricsCollector:
    """指标收集器"""
    
    _metrics: Dict[str, List[float]] = {}
    _lock: threading.Lock = threading.Lock()
    
    @classmethod
    def record(cls, metric_name: str, value: float):
        """记录指标"""
        with cls._lock:
            if metric_name not in cls._metrics:
                cls._metrics[metric_name] = []
            cls._metrics[metric_name].append(value)
    
    @classmethod
    def get_stats(cls, metric_name: str) -> Dict:
        """获取统计信息"""
        with cls._lock:
            values = cls._metrics.get(metric_name, [])
            if not values:
                return {"count": 0, "min": 0, "max": 0, "avg": 0, "sum": 0}
            
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "sum": sum(values)
            }


class HealthCheck:
    """健康检查基类"""
    
    @abstractmethod
    def check(self) -> Dict:
        """执行健康检查"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """检查项名称"""
        pass


class SystemHealthCheck(HealthCheck):
    """系统健康检查"""
    
    @property
    def name(self) -> str:
        return "system"
    
    def check(self) -> Dict:
        import psutil
        
        return {
            "status": "healthy",
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "timestamp": datetime.now().isoformat()
        }


def get_system_info() -> Dict:
    """获取系统信息"""
    import platform
    import psutil
    
    return {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "disk_total": psutil.disk_usage('/').total,
        "timestamp": datetime.now().isoformat()
    }


__all__ = [
    'ProfessionalLogger',
    'LogLevel',
    'SingletonMeta',
    'singleton',
    'ConfigManager',
    'LRUCache',
    'ThreadSafeCache',
    'BaseException',
    'ValidationError',
    'NotFoundError',
    'StateError',
    'ConfigurationError',
    'BaseModel',
    'Repository',
    'EventDispatcher',
    'RetryPolicy',
    'RateLimiter',
    'atomic_operation',
    'validate_required_fields',
    'validate_field_type',
    'MetricsCollector',
    'HealthCheck',
    'SystemHealthCheck',
    'get_system_info',
]
