#!/usr/bin/env python3
"""
实时保存器 - 保存会话快照和记忆内容
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from config import get_config
from core.session_capture import SessionCapture, SnapshotCapture

logger = logging.getLogger('memory-suite')


class RealTimeSaver:
    """实时保存器"""

    def __init__(self, config=None):
        self._config = config or get_config()
        self._snapshot_dir = self._config.get_path('snapshots')
        self._snapshot_dir.mkdir(parents=True, exist_ok=True)
        self._memory_dir = self._config.get_path('memory')
        self._memory_dir.mkdir(parents=True, exist_ok=True)

        # 初始化捕获器
        self._session_capture = SessionCapture(self._memory_dir)
        self._snapshot_capture = SnapshotCapture(self._snapshot_dir)

    @property
    def snapshot_dir(self) -> Path:
        return self._snapshot_dir

    def save(self, metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """保存会话快照和记忆内容"""
        try:
            # 1. 保存增强版快照
            snapshot_path = self._snapshot_capture.save_snapshot(metadata or {})

            # 2. 如果有当前任务内容，记录到记忆
            # capture_session 会自动创建文件头
            if metadata and 'current_task' in metadata:
                self._session_capture.capture_session({
                    'title': metadata.get('current_task', '会话记录'),
                    'type': metadata.get('type', 'chat'),
                    'messages': metadata.get('messages', []),
                    'decisions': metadata.get('decisions', []),
                    'actions': metadata.get('actions', [])
                })

            logger.info(f"实时保存完成: 快照={snapshot_path}")
            return snapshot_path

        except PermissionError as e:
            logger.error(f"保存失败 - 权限不足: {e}")
            return None
        except IOError as e:
            logger.error(f"保存失败 - IO错误: {e}")
            return None
        except Exception as e:
            logger.error(f"保存失败: {e}")
            return None

    def load(self, snapshot_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """加载快照"""
        try:
            if snapshot_id:
                snapshot_file = self._snapshot_dir / f"snapshot_{snapshot_id}.json"
                if not snapshot_file.exists():
                    logger.warning(f"快照不存在: {snapshot_id}")
                    return None
            else:
                snapshots = list(self._snapshot_dir.glob("snapshot_*.json"))
                if not snapshots:
                    logger.warning("没有可用的快照")
                    return None
                snapshot_file = max(snapshots, key=lambda p: p.stat().st_mtime)

            logger.info(f"加载快照: {snapshot_file}")

            with open(snapshot_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data

        except json.JSONDecodeError as e:
            logger.error(f"快照文件格式错误: {e}")
            return None
        except PermissionError as e:
            logger.error(f"加载失败 - 权限不足: {e}")
            return None
        except Exception as e:
            logger.error(f"加载失败: {e}")
            return None

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
                            "size": s.stat().st_size,
                            "has_content": bool(data.get("session_history"))
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

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            session_stats = self._session_capture.get_session_stats(today)
            snapshots = self.list_snapshots()

            return {
                "today": today,
                "memory_file": session_stats,
                "total_snapshots": len(snapshots),
                "latest_snapshot": snapshots[0] if snapshots else None
            }
        except Exception as e:
            logger.error(f"获取统计失败: {e}")
            return {}
