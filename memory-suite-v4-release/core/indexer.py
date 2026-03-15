#!/usr/bin/env python3
"""
索引管理器 - 语义索引
"""

import json
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from collections import Counter

from config import get_config

logger = logging.getLogger('memory-suite')


class IndexManager:
    """索引管理器"""

    def __init__(self, config=None):
        self._config = config or get_config()
        self._index_dir = self._config.get_path('index')
        self._memory_dir = self._config.get_path('memory')
        self._index_file = self._index_dir / "index.json"
        self._keywords_file = self._index_dir / "keywords.json"
        self._max_files = self._config.get('modules.indexer.max_files', 1000)

        self._index_dir.mkdir(parents=True, exist_ok=True)

    @property
    def index_dir(self) -> Path:
        return self._index_dir

    def update_index(self) -> Dict[str, Any]:
        """更新索引"""
        try:
            memory_files = list(self._memory_dir.glob("*.md"))[:self._max_files]

            keywords = Counter()
            file_index = {}
            total_size = 0

            for memory_file in memory_files:
                try:
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    total_size += len(content)

                    file_keywords = self._extract_keywords(content)
                    keywords.update(file_keywords)

                    file_index[memory_file.name] = {
                        "size": len(content),
                        "keywords": list(set(file_keywords))[:20],
                        "updated": datetime.now().isoformat()
                    }

                except UnicodeDecodeError as e:
                    logger.warning(f"跳过二进制文件: {memory_file.name}")
                except PermissionError as e:
                    logger.warning(f"权限不足: {memory_file.name}")
                except Exception as e:
                    logger.warning(f"索引文件失败: {memory_file.name} - {e}")

            index_data = {
                "updated_at": datetime.now().isoformat(),
                "total_files": len(memory_files),
                "total_size": total_size,
                "unique_keywords": len(keywords),
                "files": list(file_index.keys())
            }

            with open(self._index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)

            keywords_data = {
                "updated_at": datetime.now().isoformat(),
                "keywords": dict(keywords.most_common(500))
            }

            with open(self._keywords_file, 'w', encoding='utf-8') as f:
                json.dump(keywords_data, f, ensure_ascii=False, indent=2)

            logger.info(f"索引已更新: {len(memory_files)} 个文件, {len(keywords)} 个关键词")
            return {"indexed_files": len(memory_files), "unique_keywords": len(keywords)}

        except PermissionError as e:
            logger.error(f"索引更新失败 - 权限不足: {e}")
            return {"indexed_files": 0, "error": "permission denied"}
        except IOError as e:
            logger.error(f"索引更新失败 - IO错误: {e}")
            return {"indexed_files": 0, "error": str(e)}
        except Exception as e:
            logger.error(f"索引更新失败: {e}")
            return {"indexed_files": 0, "error": str(e)}

    def _extract_keywords(self, content: str) -> List[str]:
        """从内容中提取关键词"""
        content = content.lower()
        content = re.sub(r'[#*`\[\](){}]', ' ', content)
        words = re.findall(r'\b[a-zA-Z\u4e00-\u9fff]{2,}\b', content)
        stop_words = {'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                      'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                      'could', 'should', 'may', 'might', 'must', 'shall', 'can',
                      'and', 'or', 'but', 'if', 'else', 'when', 'at', 'from',
                      'this', 'that', 'these', 'those', 'am', 'not', 'no', 'nor',
                      '也', '的', '了', '是', '在', '有', '和', '与', '或', '但', '就'}
        return [w for w in words if w not in stop_words and len(w) > 1]

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """搜索"""
        results = []

        try:
            query_lower = query.lower().strip()
            if not query_lower:
                return results

            for memory_file in self._memory_dir.glob("*.md"):
                try:
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    content_lower = content.lower()
                    if query_lower in content_lower:
                        score = content_lower.count(query_lower)
                        snippet = self._extract_snippet(content, query_lower)
                        results.append({
                            "title": memory_file.stem,
                            "score": score,
                            "snippet": snippet,
                            "file": memory_file.name
                        })
                except UnicodeDecodeError:
                    continue
                except PermissionError:
                    continue
                except Exception:
                    continue

            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:top_k]

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []

    def _extract_snippet(self, content: str, query: str, max_length: int = 200) -> str:
        """提取内容片段"""
        content = content.replace("\n", " ").strip()
        idx = content.lower().find(query)

        if idx == -1:
            return content[:max_length] + "..." if len(content) > max_length else content

        start = max(0, idx - 50)
        end = min(len(content), idx + len(query) + 150)

        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet

    def get_index_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        try:
            if not self._index_file.exists():
                return {"status": "no_index", "message": "索引文件不存在"}

            with open(self._index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return {
                "total_files": data.get("total_files", 0),
                "total_size": data.get("total_size", 0),
                "unique_keywords": data.get("unique_keywords", 0),
                "updated_at": data.get("updated_at"),
                "status": "ok"
            }
        except json.JSONDecodeError as e:
            return {"status": "error", "message": f"索引文件损坏: {e}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
