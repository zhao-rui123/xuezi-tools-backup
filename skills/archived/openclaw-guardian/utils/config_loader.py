"""
配置加载器 - 加载和管理配置
=============================
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigLoader:
    """配置加载器类"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        # 日志配置
        'log_level': 'INFO',
        'log_file': 'logs/guardian.log',
        
        # 监控配置
        'monitoring': {
            'interval': 60,  # 监控间隔（秒）
            'enabled': True,
        },
        
        # 安全配置
        'security': {
            'whitelist': [],
            'blacklist': [],
            'allowed_modules': [],
            'blocked_modules': [
                'ctypes', 'mmap', 'resource', 'pty', 'gc', 'sysconfig'
            ],
            'allow_medium_risk': False,
        },
        
        # 稳定性配置
        'stability': {
            'thresholds': {
                'cpu_warning': 70.0,
                'cpu_critical': 90.0,
                'memory_warning': 75.0,
                'memory_critical': 90.0,
                'disk_warning': 80.0,
                'disk_critical': 95.0,
            },
            'check_interval': 5,
            'auto_protect': True,
            'max_history': 1000,
            'max_alerts': 100,
        },
        
        # Bug修复配置
        'bug_fix': {
            'auto_fix': True,
            'backup_before_fix': True,
            'fix_severity': ['low', 'medium'],
        },
        
        # 漏洞扫描配置
        'vulnerability': {
            'severity_filter': ['critical', 'high', 'medium', 'low'],
            'include_patterns': ['*.py'],
            'exclude_patterns': ['test_*.py', '*_test.py'],
        },
        
        # 报告配置
        'reports_dir': 'reports',
        
        # 备份配置
        'backup_dir': 'backups',
    }
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        加载配置
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认配置
            
        Returns:
            配置字典
        """
        config = cls.DEFAULT_CONFIG.copy()
        
        if config_path:
            config_path = Path(config_path)
            
            if config_path.exists():
                loaded_config = cls._load_from_file(config_path)
                # 合并配置
                cls._merge_config(config, loaded_config)
            else:
                # 如果配置文件不存在，创建默认配置
                cls.save(config, config_path)
        
        # 从环境变量加载
        env_config = cls._load_from_env()
        cls._merge_config(config, env_config)
        
        return config
    
    @classmethod
    def save(cls, config: Dict[str, Any], config_path: str) -> None:
        """
        保存配置到文件
        
        Args:
            config: 配置字典
            config_path: 配置文件路径
        """
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 根据扩展名选择格式
        if config_path.suffix in ['.yaml', '.yml']:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        else:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def _load_from_file(cls, config_path: Path) -> Dict[str, Any]:
        """从文件加载配置"""
        suffix = config_path.suffix.lower()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if suffix in ['.yaml', '.yml']:
                    return yaml.safe_load(f) or {}
                elif suffix == '.json':
                    return json.load(f)
                else:
                    # 尝试JSON，失败则尝试YAML
                    try:
                        return json.load(f)
                    except json.JSONDecodeError:
                        f.seek(0)
                        return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}
    
    @classmethod
    def _load_from_env(cls) -> Dict[str, Any]:
        """从环境变量加载配置"""
        config = {}
        
        # 日志级别
        if 'GUARDIAN_LOG_LEVEL' in os.environ:
            config['log_level'] = os.environ['GUARDIAN_LOG_LEVEL']
        
        # 监控间隔
        if 'GUARDIAN_MONITOR_INTERVAL' in os.environ:
            try:
                config['monitoring'] = {'interval': int(os.environ['GUARDIAN_MONITOR_INTERVAL'])}
            except ValueError:
                pass
        
        # 自动修复
        if 'GUARDIAN_AUTO_FIX' in os.environ:
            config['bug_fix'] = {'auto_fix': os.environ['GUARDIAN_AUTO_FIX'].lower() == 'true'}
        
        # 自动保护
        if 'GUARDIAN_AUTO_PROTECT' in os.environ:
            config['stability'] = {'auto_protect': os.environ['GUARDIAN_AUTO_PROTECT'].lower() == 'true'}
        
        return config
    
    @classmethod
    def _merge_config(cls, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """递归合并配置"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                cls._merge_config(base[key], value)
            else:
                base[key] = value


def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    获取配置值（支持点号路径）
    
    Args:
        config: 配置字典
        key_path: 键路径，如 'security.blocked_modules'
        default: 默认值
        
    Returns:
        配置值
    """
    keys = key_path.split('.')
    value = config
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value


def set_config_value(config: Dict[str, Any], key_path: str, value: Any) -> None:
    """
    设置配置值（支持点号路径）
    
    Args:
        config: 配置字典
        key_path: 键路径
        value: 要设置的值
    """
    keys = key_path.split('.')
    target = config
    
    for key in keys[:-1]:
        if key not in target:
            target[key] = {}
        target = target[key]
    
    target[keys[-1]] = value
