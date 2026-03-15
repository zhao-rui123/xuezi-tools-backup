#!/usr/bin/env python3
"""
统一配置管理模块
提供配置加载、保存、默认值管理
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger('memory-suite')

DEFAULT_WORKSPACE = Path.home() / ".openclaw" / "workspace"
DEFAULT_CONFIG_DIR = Path(__file__).parent


def get_workspace() -> Path:
    """获取工作空间路径，支持环境变量覆盖"""
    env_path = os.environ.get('MEMORY_SUITE_WORKSPACE')
    if env_path:
        return Path(env_path)
    return DEFAULT_WORKSPACE


def get_config_dir() -> Path:
    """获取配置目录路径"""
    return DEFAULT_CONFIG_DIR


class ConfigManager:
    """配置管理器"""

    _instance = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._workspace = get_workspace()
        self._config_dir = get_config_dir()
        self._load_config()

    @property
    def workspace(self) -> Path:
        return self._workspace

    @property
    def memory_dir(self) -> Path:
        return self._workspace / "memory"

    @property
    def knowledge_dir(self) -> Path:
        return self._workspace / "knowledge-base"

    @property
    def config_dir(self) -> Path:
        return self._config_dir

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "version": "4.0.0",
            "workspace": str(self._workspace),
            "memory_dir": str(self.memory_dir),
            "knowledge_dir": str(self.knowledge_dir),
            "modules": {
                "real_time": {"enabled": True, "interval_minutes": 10},
                "archiver": {"enabled": True, "archive_days": 7, "permanent_days": 30, "compress_days": 90, "cleanup_days": 365},
                "indexer": {"enabled": True, "interval_hours": 1, "max_files": 1000},
                "analyzer": {"enabled": True},
                "evolution": {
                    "enabled": True,
                    "daily_analysis": True,
                    "long_term_planning": True,
                    "monthly_report": True,
                    "skill_evaluation": True
                },
                "knowledge": {
                    "enabled": True,
                    "graph_building": True,
                    "auto_import": True,
                    "sync_enabled": True
                }
            },
            "paths": {
                "memory": "memory",
                "knowledge": "knowledge-base",
                "snapshots": "memory/snapshots",
                "archive": "memory/archive",
                "permanent": "memory/permanent",
                "index": "memory/index",
                "summary": "memory/summary",
                "evolution": "memory/evolution",
                "knowledge_graph": "knowledge-base/graph",
                "knowledge_sync": "knowledge-base/sync"
            }
        }

    def _load_config(self):
        """加载配置文件"""
        config_file = self._config_dir / "config.json"

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self._config = self._get_default_config()
                    self._config.update(loaded)
                    logger.info(f"配置已加载: {config_file}")
            except json.JSONDecodeError as e:
                logger.warning(f"配置文件解析失败，使用默认配置: {e}")
                self._config = self._get_default_config()
            except Exception as e:
                logger.warning(f"加载配置失败，使用默认配置: {e}")
                self._config = self._get_default_config()
        else:
            self._config = self._get_default_config()
            self.ensure_directories()
            logger.info("使用默认配置")

    def _resolve_path(self, path_str: str) -> Path:
        """解析路径，支持相对路径和绝对路径"""
        p = Path(path_str)
        if p.is_absolute():
            return p
        return self._workspace / p

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的键"""
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

    def get_path(self, path_key: str) -> Path:
        """获取路径配置"""
        path_str = self.get(f"paths.{path_key}", path_key)
        return self._resolve_path(path_str)

    def get_module_config(self, module: str) -> Dict[str, Any]:
        """获取模块配置"""
        return self.get(f"modules.{module}", {})

    def is_module_enabled(self, module: str) -> bool:
        """检查模块是否启用"""
        return self.get(f"modules.{module}.enabled", True)

    def save_config(self) -> bool:
        """保存配置到文件"""
        config_file = self._config_dir / "config.json"
        try:
            self._config_dir.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
            logger.info(f"配置已保存: {config_file}")
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False

    def set(self, key: str, value: Any) -> bool:
        """设置配置值"""
        keys = key.split('.')
        target = self._config
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
        return self.save_config()

    def ensure_directories(self):
        """确保所有必要目录存在"""
        dirs = [
            self.memory_dir,
            self.memory_dir / "snapshots",
            self.memory_dir / "archive",
            self.memory_dir / "permanent",
            self.memory_dir / "index",
            self.memory_dir / "summary",
            self.memory_dir / "evolution",
            self.knowledge_dir,
            self.knowledge_dir / "graph",
            self.knowledge_dir / "sync",
            self._config_dir
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    @property
    def config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self._config.copy()


_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """获取配置管理器单例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def reload_config() -> ConfigManager:
    """重新加载配置"""
    global _config_manager
    _config_manager = ConfigManager()
    return _config_manager
