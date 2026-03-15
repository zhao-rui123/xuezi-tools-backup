#!/usr/bin/env python3
"""
实时保存器 - 保存会话快照
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from config import get_config

logger = logging.getLogger('memory-suite')


class RealTimeSaver:
    """实时保存器"""

    def __init__(self, config=None):
        self._config = config or get_config()
        self._snapshot_dir = self._config.get_path('snapshots')
        self._snapshot_dir.mkdir(parents=True, exist_ok=True)

    @property
    def snapshot_dir(self) -> Path:
        return self._snapshot_dir

    def save(self, metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """保存会话快照"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_file = self._snapshot_dir / f"snapshot_{timestamp}.json"

            snapshot_data = {
                "timestamp": timestamp,
                "created_at": datetime.now().isoformat(),
                "type": "manual",
                "status": "ok",
                "metadata": metadata or {}
            }

            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot_data, f, ensure_ascii=False, indent=2)

            logger.info(f"快照已保存: {snapshot_file}")
            return str(snapshot_file)

        except PermissionError as e:
            logger.error(f"保存失败 - 权限不足: {e}")
            return None
        except IOError as e:
            logger.error(f"保存失败 - IO错误: {e}")
            return None
        except Exception as e:
            logger.error(f"保存失败: {e}")
            return None

    def load(self, snapshot_id: Optional[str] = None) -> bool:
        """加载快照"""
        try:
            if snapshot_id:
                snapshot_file = self._snapshot_dir / f"snapshot_{snapshot_id}.json"
                if not snapshot_file.exists():
                    logger.warning(f"快照不存在: {snapshot_id}")
                    return False
            else:
                snapshots = list(self._snapshot_dir.glob("snapshot_*.json"))
                if not snapshots:
                    logger.warning("没有可用的快照")
                    return False
                snapshot_file = max(snapshots, key=lambda p: p.stat().st_mtime)

            logger.info(f"加载快照: {snapshot_file}")

            with open(snapshot_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"快照内容: {data.get('timestamp')}")

            return True

        except json.JSONDecodeError as e:
            logger.error(f"快照文件格式错误: {e}")
            return False
        except PermissionError as e:
            logger.error(f"加载失败 - 权限不足: {e}")
            return False
        except Exception as e:
            logger.error(f"加载失败: {e}")
            return False

    def list_snapshots(self) -> list:
        """列出所有快照"""
        try:
            snapshots = sorted(
                self._snapshot_dir.glob("snapshot_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            result = []
            for s in snapshots:
                try:
                    with open(s, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        result.append({
                            "id": s.stem.replace("snapshot_", ""),
                            "timestamp": data.get("timestamp"),
                            "created_at": data.get("created_at"),
                            "type": data.get("type"),
                            "size": s.stat().st_size
                        })
                except Exception:
                    continue
            return result
        except Exception as e:
            logger.error(f"列出快照失败: {e}")
            return []

    def delete_snapshot(self, snapshot_id: str) -> bool:
        """删除指定快照"""
        try:
            snapshot_file = self._snapshot_dir / f"snapshot_{snapshot_id}.json"
            if not snapshot_file.exists():
                logger.warning(f"快照不存在: {snapshot_id}")
                return False

            snapshot_file.unlink()
            logger.info(f"快照已删除: {snapshot_id}")
            return True

        except PermissionError as e:
            logger.error(f"删除失败 - 权限不足: {e}")
            return False
        except Exception as e:
            logger.error(f"删除失败: {e}")
            return False
