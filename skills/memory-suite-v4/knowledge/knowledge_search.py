#!/usr/bin/env python3
"""
知识搜索 - 全文搜索、语义搜索、高级筛选、搜索结果排序
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

from config import get_config

logger = logging.getLogger('memory-suite')


class KnowledgeSearch:
    """知识搜索"""

    def __init__(self, config=None):
        self._config = config or get_config()
        self._knowledge_dir = self._config.get_path('knowledge')
        self._entries_file = self._knowledge_dir / "entries.json"

    def search(self, query: str, search_type: str = "fulltext",
               limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索知识

        Args:
            query: 搜索关键词
            search_type: 搜索类型 (fulltext/semantic)
            limit: 结果数量限制

        Returns:
            搜索结果列表
        """
        if not query or not query.strip():
            logger.warning("搜索词为空")
            return []

        logger.info(f"搜索知识：{query} (类型：{search_type})")

        if not self._entries_file.exists():
            logger.warning("知识条目文件不存在")
            return []

        try:
            with open(self._entries_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            entries = data.get("entries", [])
            results = []

            for entry in entries:
                try:
                    score = 0.0

                    if search_type == "fulltext":
                        score = self._fulltext_score(entry, query)
                    else:
                        score = self._semantic_score(entry, query)

                    if score > 0:
                        results.append({
                            "id": entry.get("id"),
                            "title": entry.get("title"),
                            "category": entry.get("category"),
                            "tags": entry.get("tags", []),
                            "snippet": self._extract_snippet(entry.get("content", ""), query),
                            "score": score,
                            "created_at": entry.get("created_at")
                        })
                except Exception as e:
                    logger.warning(f"搜索条目失败：{entry.get('id')} - {e}")

            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]

        except json.JSONDecodeError:
            logger.error("知识条目文件格式错误")
            return []
        except Exception as e:
            logger.error(f"知识搜索失败：{e}")
            return []

    def _fulltext_score(self, entry: Dict[str, Any], query: str) -> float:
        """全文搜索评分"""
        score = 0.0

        title = entry.get("title", "").lower()
        content = entry.get("content", "").lower()
        tags = " ".join(entry.get("tags", [])).lower()
        query_lower = query.lower()

        if query_lower in title:
            score += 10.0

        if query_lower in tags:
            score += 5.0

        if query_lower in content:
            score += 1.0
            score += min(content.count(query_lower) * 0.1, 5.0)

        return score

    def _semantic_score(self, entry: Dict[str, Any], query: str) -> float:
        """语义搜索评分"""
        query_terms = query.lower().split()
        score = 0.0

        title = entry.get("title", "").lower()
        content = entry.get("content", "").lower()
        tags = " ".join(entry.get("tags", [])).lower()

        for term in query_terms:
            if term in title:
                score += 5.0
            if term in content:
                score += 1.0
            if term in tags:
                score += 3.0

        return score

    def _extract_snippet(self, content: str, query: str, max_length: int = 150) -> str:
        """提取摘要片段"""
        if not content:
            return ""

        content = content.replace("\n", " ").strip()
        query_lower = query.lower()
        idx = content.lower().find(query_lower)

        if idx == -1:
            return content[:max_length] + "..." if len(content) > max_length else content

        start = max(0, idx - 50)
        end = min(len(content), idx + len(query) + 100)

        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet

    def advanced_search(self, category: Optional[str] = None,
                        tags: Optional[List[str]] = None,
                        date_from: Optional[str] = None,
                        date_to: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        高级搜索

        Args:
            category: 分类筛选
            tags: 标签筛选
            date_from: 起始日期
            date_to: 结束日期

        Returns:
            搜索结果列表
        """
        if not self._entries_file.exists():
            return []

        try:
            with open(self._entries_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            entries = data.get("entries", [])
            results = []

            for entry in entries:
                if category and entry.get("category") != category:
                    continue

                if tags:
                    entry_tags = entry.get("tags", [])
                    if not any(tag in entry_tags for tag in tags):
                        continue

                created_at = entry.get("created_at", "")
                if date_from and created_at < date_from:
                    continue
                if date_to and created_at > date_to:
                    continue

                results.append(entry)

            return results

        except Exception as e:
            logger.error(f"高级搜索失败：{e}")
            return []
