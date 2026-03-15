#!/usr/bin/env python3
"""
知识导入器 - 从记忆文件导入知识，自动提取关键信息，去重合并
"""

import json
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Set

from config import get_config

logger = logging.getLogger('memory-suite')


class KnowledgeImporter:
    """知识导入器"""

    def __init__(self, config=None):
        self._config = config or get_config()
        self._memory_dir = self._config.get_path('memory')
        self._knowledge_dir = self._config.get_path('knowledge')
        self._entries_file = self._knowledge_dir / "entries.json"

        self._ensure_entries_file()

    def _ensure_entries_file(self):
        """确保条目文件存在"""
        self._knowledge_dir.mkdir(parents=True, exist_ok=True)
        if not self._entries_file.exists():
            with open(self._entries_file, 'w', encoding='utf-8') as f:
                json.dump({"entries": [], "next_id": 1}, f, ensure_ascii=False, indent=2)

    def _load_entries(self) -> Dict[str, Any]:
        """加载条目数据"""
        try:
            with open(self._entries_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"entries": [], "next_id": 1}
        except Exception as e:
            logger.error(f"加载条目失败：{e}")
            return {"entries": [], "next_id": 1}

    def _save_entries(self, data: Dict[str, Any]):
        """保存条目数据"""
        try:
            with open(self._entries_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存条目失败：{e}")

    def import_from_memory(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        """
        从记忆导入知识

        Args:
            date_from: 开始日期 (YYYY-MM-DD)
            date_to: 结束日期 (YYYY-MM-DD)

        Returns:
            导入结果
        """
        logger.info("开始从记忆导入知识...")

        imported = 0
        duplicates = 0
        skipped = 0

        try:
            memory_files = list(self._memory_dir.glob("*.md"))
            existing_titles = self._get_existing_titles()

            for memory_file in memory_files:
                try:
                    if date_from or date_to:
                        mtime = datetime.fromtimestamp(memory_file.stat().st_mtime)
                        if date_from and mtime < datetime.fromisoformat(date_from):
                            skipped += 1
                            continue
                        if date_to and mtime > datetime.fromisoformat(date_to):
                            skipped += 1
                            continue

                    with open(memory_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    title = memory_file.stem
                    if title in existing_titles:
                        duplicates += 1
                        logger.debug(f"跳过重复：{title}")
                        continue

                    extracted = self._extract_knowledge(title, content)
                    if extracted:
                        self._add_entry(title, extracted, content, "memory_import")
                        imported += 1
                        existing_titles.add(title)
                        logger.debug(f"导入：{title}")

                except PermissionError:
                    skipped += 1
                except Exception as e:
                    logger.warning(f"导入失败：{memory_file.name} - {e}")
                    skipped += 1

            result = {
                "imported": imported,
                "duplicates": duplicates,
                "skipped": skipped,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"知识导入完成：导入 {imported}, 重复 {duplicates}, 跳过 {skipped}")
            return result

        except Exception as e:
            logger.error(f"知识导入失败：{e}")
            return {
                "imported": 0,
                "duplicates": 0,
                "skipped": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _get_existing_titles(self) -> Set[str]:
        """获取已存在的标题"""
        try:
            data = self._load_entries()
            return {e.get("title", "") for e in data.get("entries", [])}
        except Exception:
            return set()

    def _extract_knowledge(self, title: str, content: str) -> Optional[Dict[str, Any]]:
        """从内容中提取知识"""
        lines = content.split('\n')

        category = "general"
        tags = []

        for line in lines[:5]:
            line = line.strip()
            if line.startswith('#'):
                category = line.lstrip('#').strip().lower()
                category = re.sub(r'[^a-z0-9\u4e00-\u9fff]', '', category)
                if not category:
                    category = "general"
                break

        tag_matches = re.findall(r'#(\w+)', content)
        tags = list(set(tag_matches))[:5]

        key_points = []
        for line in lines:
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                point = line[2:].strip()
                if len(point) > 10 and len(point) < 200:
                    key_points.append(point)
            if len(key_points) >= 5:
                break

        if len(content) < 50:
            return None

        return {
            "category": category,
            "tags": tags,
            "key_points": key_points,
            "source_file": f"{title}.md"
        }

    def _add_entry(self, title: str, extracted: Dict[str, Any], content: str, source: str):
        """添加知识条目"""
        data = self._load_entries()

        entry = {
            "id": f"kb_{data['next_id']:04d}",
            "title": title,
            "content": content[:5000],
            "category": extracted.get("category", "general"),
            "tags": extracted.get("tags", []),
            "source": source,
            "source_file": extracted.get("source_file"),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": 1
        }

        data["entries"].append(entry)
        data["next_id"] += 1
        self._save_entries(data)

    def import_file(self, file_path: str, category: str = "general", tags: Optional[List[str]] = None) -> bool:
        """导入单个文件"""
        try:
            source_file = Path(file_path)
            if not source_file.exists():
                logger.error(f"文件不存在：{file_path}")
                return False

            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()

            existing_titles = self._get_existing_titles()
            title = source_file.stem

            if title in existing_titles:
                logger.warning(f"标题已存在：{title}")
                return False

            extracted = self._extract_knowledge(title, content)
            if extracted:
                extracted["category"] = category
                if tags:
                    extracted["tags"] = tags
                self._add_entry(title, extracted, content, "file_import")
                logger.info(f"文件已导入：{title}")
                return True

            return False

        except Exception as e:
            logger.error(f"导入文件失败：{e}")
            return False
