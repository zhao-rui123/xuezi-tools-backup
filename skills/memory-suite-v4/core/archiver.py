#!/usr/bin/env python3
"""
归档管理器 - 归档旧记忆文件
支持多层归档策略：7天归档、30天永久记录、90天压缩、365天清理
"""

import json
import gzip
import shutil
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from config import get_config

logger = logging.getLogger('memory-suite')


class Archiver:
    """归档管理器"""

    def __init__(self, config=None):
        self._config = config or get_config()
        self._archive_dir = self._config.get_path('archive')
        self._permanent_dir = self._config.get_path('permanent')
        self._memory_dir = self._config.get_path('memory')

        self._archive_days = self._config.get('modules.archiver.archive_days', 7)
        self._permanent_days = self._config.get('modules.archiver.permanent_days', 30)
        self._compress_days = self._config.get('modules.archiver.compress_days', 90)
        self._cleanup_days = self._config.get('modules.archiver.cleanup_days', 365)

        self._ensure_directories()

    def _ensure_directories(self):
        """确保目录存在"""
        self._archive_dir.mkdir(parents=True, exist_ok=True)
        self._permanent_dir.mkdir(parents=True, exist_ok=True)

    @property
    def archive_dir(self) -> Path:
        return self._archive_dir

    def get_stats(self) -> Dict[str, int]:
        """获取归档统计"""
        archived = len(list(self._archive_dir.glob("*.md")))
        archived_gz = len(list(self._archive_dir.glob("*.gz")))
        permanent = len(list(self._permanent_dir.glob("*.md")))
        total_memory = len(list(self._memory_dir.glob("*.md")))

        return {
            "archived": archived,
            "archived_compressed": archived_gz,
            "permanent": permanent,
            "total_memory": total_memory
        }

    def archive_files(self) -> Dict[str, Any]:
        """执行归档操作 - 将超过归档期限的文件移动到归档目录"""
        archived_count = 0
        permanent_count = 0
        compressed_count = 0
        now = datetime.now()
        errors = []

        try:
            memory_files = list(self._memory_dir.glob("*.md"))

            for memory_file in memory_files:
                try:
                    file_time = datetime.fromtimestamp(memory_file.stat().st_mtime)
                    age_days = (now - file_time).days

                    if age_days >= self._permanent_days:
                        target = self._permanent_dir / memory_file.name
                        shutil.copy2(memory_file, target)
                        permanent_count += 1
                        logger.debug(f"永久保存: {memory_file.name}")

                    elif age_days >= self._compress_days:
                        target = self._archive_dir / f"{memory_file.stem}.gz"
                        with open(memory_file, 'rb') as f_in:
                            with gzip.open(target, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        compressed_count += 1
                        logger.debug(f"压缩归档: {memory_file.name}")

                    elif age_days >= self._archive_days:
                        target = self._archive_dir / memory_file.name
                        shutil.move(str(memory_file), str(target))
                        archived_count += 1
                        logger.debug(f"移动归档: {memory_file.name}")

                except PermissionError as e:
                    errors.append(f"权限错误: {memory_file.name} - {e}")
                    logger.error(f"权限错误: {memory_file.name}")
                except Exception as e:
                    errors.append(f"归档失败: {memory_file.name} - {e}")
                    logger.error(f"归档失败: {memory_file.name} - {e}")

            result = {
                "archived": archived_count,
                "permanent": permanent_count,
                "compressed": compressed_count,
                "errors": errors,
                "timestamp": now.isoformat()
            }

            logger.info(f"归档完成: 移动 {archived_count}, 永久 {permanent_count}, 压缩 {compressed_count}")
            return result

        except Exception as e:
            logger.error(f"归档过程失败: {e}")
            return {
                "archived": 0,
                "permanent": 0,
                "compressed": 0,
                "errors": [str(e)],
                "timestamp": datetime.now().isoformat()
            }

    def restore_file(self, filename: str) -> Optional[str]:
        """恢复归档文件"""
        try:
            archive_file = self._archive_dir / filename
            if not archive_file.exists():
                archive_file_gz = self._archive_dir / f"{filename}.gz"
                if archive_file_gz.exists():
                    target = self._memory_dir / filename.replace('.gz', '')
                    with gzip.open(archive_file_gz, 'rb') as f_in:
                        with open(target, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    logger.info(f"已恢复(解压缩): {filename}")
                    return str(target)

            target = self._memory_dir / filename
            shutil.move(str(archive_file), str(target))
            logger.info(f"已恢复: {filename}")
            return str(target)

        except Exception as e:
            logger.error(f"恢复失败: {e}")
            return None

    def clean_old_archives(self) -> int:
        """清理超过清理期限的归档"""
        cleaned = 0
        threshold = datetime.now() - timedelta(days=self._cleanup_days)

        for archive_file in list(self._archive_dir.glob("*.md")) + list(self._archive_dir.glob("*.gz")):
            try:
                mtime = datetime.fromtimestamp(archive_file.stat().st_mtime)
                if mtime < threshold:
                    archive_file.unlink()
                    cleaned += 1
                    logger.debug(f"已清理: {archive_file.name}")
            except PermissionError as e:
                logger.warning(f"权限错误，无法清理 {archive_file.name}: {e}")
            except Exception as e:
                logger.warning(f"清理失败 {archive_file.name}: {e}")

        logger.info(f"清理完成: 删除 {cleaned} 个旧归档")
        return cleaned

    def list_archives(self, days: int = 30) -> List[Dict[str, Any]]:
        """列出归档文件"""
        archives = []
        threshold = datetime.now() - timedelta(days=days)

        for archive_file in list(self._archive_dir.glob("*.md")) + list(self._archive_dir.glob("*.gz")):
            try:
                stat = archive_file.stat()
                mtime = datetime.fromtimestamp(stat.st_mtime)
                archives.append({
                    "name": archive_file.name,
                    "size": stat.st_size,
                    "modified": mtime.isoformat(),
                    "type": "compressed" if archive_file.suffix == ".gz" else "standard"
                })
            except Exception as e:
                logger.warning(f"读取归档信息失败: {archive_file.name}")

        return sorted(archives, key=lambda x: x["modified"], reverse=True)


class ArchiveManager(Archiver):
    """归档管理器别名，保持向后兼容"""

    def run_archive_cycle(self) -> Dict[str, Any]:
        """运行完整的归档周期"""
        logger.info("开始归档周期...")
        return self.archive_files()
