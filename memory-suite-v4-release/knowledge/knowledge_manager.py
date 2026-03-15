#!/usr/bin/env python3
"""
知识管理器 - 知识条目 CRUD、分类管理、标签系统、版本控制
"""

import json
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

from config import get_config

logger = logging.getLogger('memory-suite')


class KnowledgeManager:
    """知识管理器"""

    def __init__(self, config=None):
        self._config = config or get_config()
        self._knowledge_dir = self._config.get_path('knowledge')
        self._entries_file = self._knowledge_dir / "entries.json"
        self._knowledge_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_entries_file()

    def _ensure_entries_file(self):
        """确保条目文件存在"""
        if not self._entries_file.exists():
            with open(self._entries_file, 'w', encoding='utf-8') as f:
                json.dump({"entries": [], "next_id": 1}, f, ensure_ascii=False, indent=2)

    def _load_entries(self) -> Dict[str, Any]:
        """加载条目数据"""
        try:
            with open(self._entries_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning("条目文件损坏，重新创建")
            return {"entries": [], "next_id": 1}
        except Exception as e:
            logger.error(f"加载条目失败：{e}")
            return {"entries": [], "next_id": 1}

    def _save_entries(self, data: Dict[str, Any]):
        """保存条目数据"""
        try:
            temp_file = self._entries_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            shutil.move(str(temp_file), str(self._entries_file))
        except Exception as e:
            logger.error(f"保存条目失败：{e}")

    def list_entries(self, category: Optional[str] = None, tag: Optional[str] = None,
                     limit: int = 20) -> List[Dict[str, Any]]:
        """
        列出知识条目

        Args:
            category: 按分类筛选
            tag: 按标签筛选
            limit: 数量限制

        Returns:
            条目列表
        """
        data = self._load_entries()
        entries = data.get("entries", [])

        if category:
            entries = [e for e in entries if e.get("category") == category]
        if tag:
            entries = [e for e in entries if tag in e.get("tags", [])]

        entries.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return entries[:limit]

    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """
        获取知识条目

        Args:
            entry_id: 条目 ID

        Returns:
            条目详情
        """
        data = self._load_entries()
        entries = data.get("entries", [])

        for entry in entries:
            if entry.get("id") == entry_id:
                return entry

        return None

    def add_entry(self, title: str, content: str, category: str = "general",
                  tags: Optional[List[str]] = None, source: str = "manual") -> Optional[Dict[str, Any]]:
        """
        添加知识条目

        Args:
            title: 标题
            content: 内容
            category: 分类
            tags: 标签列表
            source: 来源

        Returns:
            新条目
        """
        if not title or not title.strip():
            logger.error("标题不能为空")
            return None

        data = self._load_entries()

        entry = {
            "id": f"kb_{data['next_id']:04d}",
            "title": title.strip(),
            "content": content,
            "category": category,
            "tags": tags or [],
            "source": source,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": 1
        }

        data["entries"].append(entry)
        data["next_id"] += 1
        self._save_entries(data)

        logger.info(f"添加知识条目：{entry['id']} - {title}")
        return entry

    def update_entry(self, entry_id: str, **updates) -> Optional[Dict[str, Any]]:
        """更新知识条目"""
        data = self._load_entries()

        for entry in data.get("entries", []):
            if entry.get("id") == entry_id:
                for key, value in updates.items():
                    if key not in ("id", "created_at"):
                        entry[key] = value
                entry["updated_at"] = datetime.now().isoformat()
                entry["version"] = entry.get("version", 1) + 1
                self._save_entries(data)
                logger.info(f"更新知识条目：{entry_id}")
                return entry

        logger.warning(f"条目不存在：{entry_id}")
        return None

    def delete_entry(self, entry_id: str) -> bool:
        """删除知识条目"""
        data = self._load_entries()
        entries = data.get("entries", [])

        original_len = len(entries)
        data["entries"] = [e for e in entries if e.get("id") != entry_id]

        if len(data["entries"]) < original_len:
            self._save_entries(data)
            logger.info(f"删除知识条目：{entry_id}")
            return True

        logger.warning(f"条目不存在：{entry_id}")
        return False

    def get_categories(self) -> List[str]:
        """获取所有分类"""
        data = self._load_entries()
        categories = {e.get("category", "general") for e in data.get("entries", [])}
        return sorted(list(categories))

    def get_tags(self) -> List[str]:
        """获取所有标签"""
        data = self._load_entries()
        tags = set()
        for e in data.get("entries", []):
            tags.update(e.get("tags", []))
        return sorted(list(tags))

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        data = self._load_entries()
        entries = data.get("entries", [])

        categories = {}
        tags = {}

        for e in entries:
            cat = e.get("category", "general")
            categories[cat] = categories.get(cat, 0) + 1

            for tag in e.get("tags", []):
                tags[tag] = tags.get(tag, 0) + 1

        return {
            "total_entries": len(entries),
            "categories": categories,
            "top_tags": sorted(tags.items(), key=lambda x: x[1], reverse=True)[:10],
            "next_id": data.get("next_id", 1)
        }
