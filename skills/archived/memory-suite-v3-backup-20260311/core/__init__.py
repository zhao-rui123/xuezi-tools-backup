#!/usr/bin/env python3
"""
Memory Suite v3.0 - 核心层模块初始化
版本信息、公共工具函数

注意：此模块仅导出通用工具函数，不自动导入所有管理器类。
各管理器类应单独从对应模块导入。
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# ============================================================================
# 版本信息
# ============================================================================

__version__ = "3.0.0"
__version_info__ = (3, 0, 0)
__author__ = "Memory Suite Team"
__license__ = "MIT"

VERSION_STRING = f"Memory Suite v{__version__}"


# ============================================================================
# 日志配置
# ============================================================================

def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO
) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件路径（可选）
        level: 日志级别
    
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了日志文件）
    if log_file:
        try:
            log_path = Path(log_file).expanduser()
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"无法创建日志文件 {log_file}: {e}")
    
    return logger


# ============================================================================
# 路径工具
# ============================================================================

def expand_path(path: str) -> Path:
    """
    展开路径（处理 ~ 和环境变量）
    
    Args:
        path: 路径字符串
    
    Returns:
        展开后的 Path 对象
    """
    return Path(os.path.expandvars(os.path.expanduser(path)))


def ensure_directory(path: Union[str, Path], create: bool = True) -> Path:
    """
    确保目录存在
    
    Args:
        path: 目录路径
        create: 是否自动创建
    
    Returns:
        Path 对象
    
    Raises:
        FileNotFoundError: 目录不存在且 create=False
        PermissionError: 无法创建目录
    """
    dir_path = expand_path(path) if isinstance(path, str) else path
    
    if not dir_path.exists():
        if create:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                raise PermissionError(f"无法创建目录 {dir_path}: {e}")
        else:
            raise FileNotFoundError(f"目录不存在：{dir_path}")
    
    return dir_path


def get_relative_path(path: Union[str, Path], base: Union[str, Path]) -> str:
    """
    获取相对路径
    
    Args:
        path: 目标路径
        base: 基础路径
    
    Returns:
        相对路径字符串
    """
    path_obj = expand_path(path) if isinstance(path, str) else path
    base_obj = expand_path(base) if isinstance(base, str) else base
    
    try:
        return str(path_obj.relative_to(base_obj))
    except ValueError:
        return str(path_obj)


# ============================================================================
# 时间工具
# ============================================================================

def get_timestamp() -> int:
    """获取当前时间戳（毫秒）"""
    return int(datetime.now().timestamp() * 1000)


def get_timestamp_seconds() -> int:
    """获取当前时间戳（秒）"""
    return int(datetime.now().timestamp())


def format_datetime(dt: Optional[datetime] = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间
    
    Args:
        dt: 日期时间对象（默认为当前时间）
        fmt: 格式字符串
    
    Returns:
        格式化后的字符串
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(fmt)


def parse_datetime(date_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    解析日期时间字符串
    
    Args:
        date_str: 日期时间字符串
        fmt: 格式字符串
    
    Returns:
        解析后的 datetime 对象，失败返回 None
    """
    try:
        return datetime.strptime(date_str, fmt)
    except ValueError:
        return None


def get_date_string(days_offset: int = 0) -> str:
    """
    获取日期字符串（用于文件命名）
    
    Args:
        days_offset: 天数偏移（0=今天，-1=昨天，1=明天）
    
    Returns:
        日期字符串（YYYY-MM-DD）
    """
    from datetime import timedelta
    target_date = datetime.now() + timedelta(days=days_offset)
    return target_date.strftime("%Y-%m-%d")


# ============================================================================
# JSON 工具
# ============================================================================

def load_json(file_path: Union[str, Path], encoding: str = 'utf-8') -> Optional[Dict]:
    """
    加载 JSON 文件
    
    Args:
        file_path: 文件路径
        encoding: 文件编码
    
    Returns:
        解析后的字典，失败返回 None
    """
    try:
        path = expand_path(file_path) if isinstance(file_path, str) else file_path
        with open(path, 'r', encoding=encoding) as f:
            return json.load(f)
    except FileNotFoundError:
        logging.getLogger(__name__).warning(f"JSON 文件不存在：{file_path}")
        return None
    except json.JSONDecodeError as e:
        logging.getLogger(__name__).error(f"JSON 格式错误 {file_path}: {e}")
        return None
    except Exception as e:
        logging.getLogger(__name__).error(f"加载 JSON 失败 {file_path}: {e}")
        return None


def save_json(
    data: Dict,
    file_path: Union[str, Path],
    encoding: str = 'utf-8',
    indent: int = 2,
    ensure_ascii: bool = False
) -> bool:
    """
    保存 JSON 文件
    
    Args:
        data: 要保存的数据
        file_path: 文件路径
        encoding: 文件编码
        indent: 缩进空格数
        ensure_ascii: 是否转义非 ASCII 字符
    
    Returns:
        是否保存成功
    """
    try:
        path = expand_path(file_path) if isinstance(file_path, str) else file_path
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding=encoding) as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
        return True
    except Exception as e:
        logging.getLogger(__name__).error(f"保存 JSON 失败 {file_path}: {e}")
        return False


def merge_dict(base: Dict, override: Dict, inplace: bool = False) -> Dict:
    """
    合并字典（递归合并嵌套字典）
    
    Args:
        base: 基础字典
        override: 覆盖字典
        inplace: 是否就地修改 base
    
    Returns:
        合并后的字典
    """
    result = base if inplace else base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dict(result[key], value, inplace=True)
        else:
            result[key] = value
    
    return result


# ============================================================================
# 配置管理
# ============================================================================

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: Optional[Union[str, Path]] = None):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录
        """
        if config_dir:
            self.config_dir = expand_path(config_dir) if isinstance(config_dir, str) else config_dir
        else:
            # 默认使用技能包目录下的 config
            self.config_dir = Path(__file__).parent.parent / "config"
        
        self.config_file = self.config_dir / "config.json"
        self.modules_file = self.config_dir / "modules.json"
        
        self._config: Optional[Dict] = None
        self._modules: Optional[Dict] = None
        self._logger = setup_logger(__name__)
    
    def load_config(self, force: bool = False) -> Optional[Dict]:
        """
        加载主配置
        
        Args:
            force: 是否强制重新加载
        
        Returns:
            配置字典
        """
        if self._config and not force:
            return self._config
        
        self._config = load_json(self.config_file)
        if self._config:
            self._logger.info(f"配置加载成功：{self.config_file}")
        else:
            self._logger.warning(f"配置加载失败：{self.config_file}")
        
        return self._config
    
    def load_modules(self, force: bool = False) -> Optional[Dict]:
        """
        加载模块配置
        
        Args:
            force: 是否强制重新加载
        
        Returns:
            模块配置字典
        """
        if self._modules and not force:
            return self._modules
        
        self._modules = load_json(self.modules_file)
        if self._modules:
            self._logger.info(f"模块配置加载成功：{self.modules_file}")
        else:
            self._logger.warning(f"模块配置加载失败：{self.modules_file}")
        
        return self._modules
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值（支持点分隔的嵌套键）
        
        Args:
            key: 配置键（如 "modules.real_time.enabled"）
            default: 默认值
        
        Returns:
            配置值
        """
        if not self._config:
            self.load_config()
        
        if not self._config:
            return default
        
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def is_module_enabled(self, module_name: str) -> bool:
        """
        检查模块是否启用
        
        Args:
            module_name: 模块名称
        
        Returns:
            是否启用
        """
        if not self._modules:
            self.load_modules()
        
        if not self._modules:
            return False
        
        # 在所有类别中查找模块
        for category, modules in self._modules.items():
            if module_name in modules:
                module_config = modules[module_name]
                if isinstance(module_config, dict):
                    return module_config.get('enabled', False)
        
        return False
    
    def get_module_config(self, module_name: str) -> Optional[Dict]:
        """
        获取模块配置
        
        Args:
            module_name: 模块名称
        
        Returns:
            模块配置字典
        """
        if not self._modules:
            self.load_modules()
        
        if not self._modules:
            return None
        
        # 在所有类别中查找模块
        for category, modules in self._modules.items():
            if module_name in modules:
                return modules[module_name]
        
        return None


# ============================================================================
# 错误处理
# ============================================================================

class MemorySuiteError(Exception):
    """Memory Suite 基础异常类"""
    pass


class ConfigError(MemorySuiteError):
    """配置错误"""
    pass


class DirectoryError(MemorySuiteError):
    """目录错误"""
    pass


class FileError(MemorySuiteError):
    """文件错误"""
    pass


def safe_execute(func, default: Any = None, logger: Optional[logging.Logger] = None):
    """
    安全执行函数（捕获所有异常）
    
    Args:
        func: 要执行的函数
        default: 失败时的默认返回值
        logger: 日志记录器
    
    Returns:
        函数返回值或默认值
    """
    try:
        return func()
    except Exception as e:
        if logger:
            logger.error(f"执行失败：{e}")
        return default


# ============================================================================
# 公共工具函数
# ============================================================================

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀
    
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    清理文件名（移除非法字符）
    
    Args:
        filename: 原始文件名
    
    Returns:
        清理后的文件名
    """
    # 移除非法字符
    illegal_chars = '<>:"/\\|？*'
    for char in illegal_chars:
        filename = filename.replace(char, '_')
    
    # 移除前后空格
    filename = filename.strip()
    
    # 限制长度
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename


def calculate_file_size(file_path: Union[str, Path]) -> int:
    """
    计算文件大小（字节）
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件大小（字节），失败返回 0
    """
    try:
        path = expand_path(file_path) if isinstance(file_path, str) else file_path
        return path.stat().st_size
    except Exception:
        return 0


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 字节数
    
    Returns:
        格式化后的大小字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def count_files(directory: Union[str, Path], pattern: str = "*") -> int:
    """
    统计目录中的文件数量
    
    Args:
        directory: 目录路径
        pattern: 文件匹配模式
    
    Returns:
        文件数量
    """
    try:
        dir_path = expand_path(directory) if isinstance(directory, str) else directory
        return len(list(dir_path.glob(pattern)))
    except Exception:
        return 0


# ============================================================================
# 模块导出
# ============================================================================

__all__ = [
    # 版本信息
    '__version__',
    '__version_info__',
    'VERSION_STRING',
    
    # 日志
    'setup_logger',
    
    # 路径工具
    'expand_path',
    'ensure_directory',
    'get_relative_path',
    
    # 时间工具
    'get_timestamp',
    'get_timestamp_seconds',
    'format_datetime',
    'parse_datetime',
    'get_date_string',
    
    # JSON 工具
    'load_json',
    'save_json',
    'merge_dict',
    
    # 配置管理
    'ConfigManager',
    
    # 错误处理
    'MemorySuiteError',
    'ConfigError',
    'DirectoryError',
    'FileError',
    'safe_execute',
    
    # 公共工具
    'truncate_text',
    'sanitize_filename',
    'calculate_file_size',
    'format_file_size',
    'count_files',
]


# ============================================================================
# 初始化日志
# ============================================================================

_logger = setup_logger(__name__)
_logger.debug(f"{VERSION_STRING} 核心层工具函数初始化完成")
