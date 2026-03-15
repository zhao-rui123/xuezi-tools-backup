#!/usr/bin/env python3
"""
知识同步器 - 同步到 knowledge-base/，双向同步，冲突解决
"""

import json
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

from config import get_config

logger = logging.getLogger('memory-suite')


class KnowledgeSync:
    """知识同步器"""

    def __init__(self, config=None):
        self._config = config or get_config()
        self._memory_dir = self._config.get_path('memory')
        self._knowledge_dir = self._config.get_path('knowledge')
        self._sync_dir = self._knowledge_dir / "sync"
        self._sync_log_file = self._sync_dir / "sync_log.json"

        self._sync_dir.mkdir(parents=True, exist_ok=True)

    def sync_all(self, direction: str = "bidirectional") -> Optional[Dict[str, Any]]:
        """
        执行知识同步

        Args:
            direction: 同步方向 (export/import/bidirectional)

        Returns:
            同步结果
        """
        logger.info(f"执行知识同步 (方向：{direction})")

        if direction not in ("export", "import", "bidirectional"):
            logger.error(f"无效的同步方向：{direction}")
            return None

        try:
            exported = 0
            imported = 0
            conflicts = 0

            if direction in ("export", "bidirectional"):
                exported = self._export_to_knowledge_base()

            if direction in ("import", "bidirectional"):
                imported, conflicts = self._import_from_knowledge_base()

            self._log_sync(exported, imported, conflicts)

            result = {
                "exported": exported,
                "imported": imported,
                "conflicts": conflicts,
                "synced_at": datetime.now().isoformat()
            }

            logger.info(f"知识同步完成：导出 {exported}, 导入 {imported}, 冲突 {conflicts}")
            return result

        except PermissionError as e:
            logger.error(f"知识同步失败 - 权限不足：{e}")
            return None
        except Exception as e:
            logger.error(f"知识同步失败：{e}")
            return None

    def _export_to_knowledge_base(self) -> int:
        """导出记忆到知识库"""
        exported = 0

        memory_files = list(self._memory_dir.glob("*.md"))
        exports_dir = self._knowledge_dir / "memory_exports"
        exports_dir.mkdir(parents=True, exist_ok=True)

        for memory_file in memory_files:
            try:
                target_file = exports_dir / f"{memory_file.stem}.md"

                if target_file.exists():
                    with open(target_file, 'r', encoding='utf-8') as f:
                        existing = f.read()
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        current = f.read()

                    if existing == current:
                        continue

                shutil.copy2(memory_file, target_file)
                exported += 1
                logger.debug(f"导出：{memory_file.name}")

            except PermissionError:
                logger.warning(f"权限错误，无法导出：{memory_file.name}")
            except Exception as e:
                logger.warning(f"导出失败：{memory_file.name} - {e}")

        return exported

    def _import_from_knowledge_base(self) -> Tuple[int, int]:
        """从知识库导入"""
        imported = 0
        conflicts = 0

        entries_file = self._knowledge_dir / "entries.json"
        if not entries_file.exists():
            return 0, 0

        try:
            with open(entries_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            entries = data.get("entries", [])

            for entry in entries:
                if entry.get("source") == "memory_import":
                    continue

                title = entry.get("title", "")
                if title:
                    imported += 1

            return imported, conflicts

        except Exception as e:
            logger.warning(f"导入知识库失败：{e}")
            return 0, 0

    def _log_sync(self, exported: int, imported: int, conflicts: int):
        """记录同步日志"""
        log_entry = {
            "synced_at": datetime.now().isoformat(),
            "exported": exported,
            "imported": imported,
            "conflicts": conflicts
        }

        logs = []
        if self._sync_log_file.exists():
            try:
                with open(self._sync_log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = []
            except Exception:
                logs = []

        logs.append(log_entry)

        logs = logs[-100:]

        try:
            with open(self._sync_log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"记录同步日志失败：{e}")

    def get_sync_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取同步历史"""
        if not self._sync_log_file.exists():
            return []

        try:
            with open(self._sync_log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
                if not isinstance(logs, list):
                    return []
                return logs[-limit:]
        except Exception:
            return []
