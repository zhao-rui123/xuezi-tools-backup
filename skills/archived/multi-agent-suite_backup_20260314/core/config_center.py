"""
配置中心
统一配置管理 + 热更新
"""

import os
import json
import threading
from pathlib import Path
from typing import Any, Dict, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field

# 尝试导入yaml，如果失败则只用json
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

SUITE_DIR = Path("~/.openclaw/workspace/skills/multi-agent-suite").expanduser()

@dataclass
class ConfigChange:
    """配置变更记录"""
    key: str
    old_value: Any
    new_value: Any
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class ConfigCenter:
    """配置中心"""

    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir) if config_dir else (SUITE_DIR / "config")
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self._config: Dict = {}
        self._watchers: Dict[str, list] = {}
        self._change_history: list = []
        self._lock = threading.RLock()

        self._load_all_configs()

    def _load_all_configs(self):
        """加载所有配置文件"""
        # 加载JSON配置
        json_config = self.config_dir / "config.json"
        if json_config.exists():
            try:
                with open(json_config, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            except Exception as e:
                print(f"⚠️ 加载配置失败: {e}")
                self._config = self._default_config()
        else:
            self._config = self._default_config()
            self._save_config()

    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            "system": {
                "name": "Multi-Agent Suite",
                "version": "2.0"
            },
            "agents": {},
            "workflow": {
                "max_retries": 3,
                "timeout": 300
            }
        }

    def _save_config(self):
        """保存配置"""
        config_file = self.config_dir / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default=None):
        """获取配置"""
        with self._lock:
            keys = key.split('.')
            value = self._config
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value

    def set(self, key: str, value: Any):
        """设置配置"""
        with self._lock:
            old_value = self.get(key)
            keys = key.split('.')
            config = self._config
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            config[keys[-1]] = value
            self._save_config()
            
            # 记录变更
            change = ConfigChange(key=key, old_value=old_value, new_value=value)
            self._change_history.append(change)
            
            # 通知监听器
            if key in self._watchers:
                for callback in self._watchers[key]:
                    try:
                        callback(old_value, value)
                    except Exception as e:
                        print(f"⚠️ 配置监听器错误: {e}")

# 全局配置中心实例
config_center = ConfigCenter()
