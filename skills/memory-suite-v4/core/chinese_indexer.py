#!/usr/bin/env python3
"""
中文分词索引模块 - 基于 jieba 的倒排索引
"""

import jieba
import json
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Set, Tuple
from collections import defaultdict

logger = logging.getLogger('memory-suite')


class ChineseIndexer:
    """中文分词索引管理器"""

    def __init__(self, memory_dir: str = None, index_dir: str = None):
        if memory_dir is None:
            memory_dir = "/Users/zhaoruicn/.openclaw/workspace/memory"
        if index_dir is None:
            index_dir = str(Path(__file__).parent / "chinese_index")

        self.memory_dir = Path(memory_dir)
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.inverted_index_file = self.index_dir / "inverted_index.json"
        self.file_meta_file = self.index_dir / "file_meta.json"
        self.stats_file = self.index_dir / "stats.json"

        # 停用词
        self.stop_words = {
            '的', '了', '是', '在', '有', '和', '与', '或', '但', '就', '都', '也',
            '要', '会', '能', '可以', '这', '那', '他', '她', '它', '我', '你',
            '我们', '你们', '他们', '她们', '它们', '自己', '什么', '哪个', '哪些',
            '这个', '那个', '一个', '一些', '还', '很', '最', '更', '已经', '正在',
            '着', '过', '地', '得', '而', '于', '上', '下', '中', '为', '而且',
            'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'must', 'shall', 'can', 'and', 'or', 'but', 'if', 'else',
            'when', 'at', 'from', 'this', 'that', 'these', 'those', 'am', 'not',
            'no', 'nor', 'not', 'a', 'an', 'to', 'of', 'in', 'for', 'on', 'with',
        }

        # 加载已有索引（如果存在）
        self.inverted_index: Dict[str, List[Dict]] = {}
        self.file_meta: Dict[str, Dict] = {}
        self._load_index()

    def _load_index(self):
        """加载已有索引"""
        if self.inverted_index_file.exists():
            try:
                with open(self.inverted_index_file, 'r', encoding='utf-8') as f:
                    self.inverted_index = json.load(f)
            except Exception as e:
                logger.warning(f"加载倒排索引失败: {e}")
                self.inverted_index = {}

        if self.file_meta_file.exists():
            try:
                with open(self.file_meta_file, 'r', encoding='utf-8') as f:
                    self.file_meta = json.load(f)
            except Exception as e:
                logger.warning(f"加载文件元数据失败: {e}")
                self.file_meta = {}

    def _save_index(self):
        """保存索引到文件"""
        try:
            with open(self.inverted_index_file, 'w', encoding='utf-8') as f:
                json.dump(self.inverted_index, f, ensure_ascii=False, indent=2)

            with open(self.file_meta_file, 'w', encoding='utf-8') as f:
                json.dump(self.file_meta, f, ensure_ascii=False, indent=2)

            stats = {
                "updated_at": datetime.now().isoformat(),
                "total_words": len(self.inverted_index),
                "total_files": len(self.file_meta),
                "memory_dir": str(self.memory_dir),
            }
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            logger.error(f"保存索引失败: {e}")
            return False

    def _tokenize(self, text: str) -> List[str]:
        """对文本进行分词"""
        # 清理特殊字符
        text = re.sub(r'[#*`\[\](){}|_]', ' ', text)
        # jieba 分词
        words = jieba.cut(text, cut_all=False)
        # 过滤停用词和短词
        return [w.strip() for w in words if w.strip() and len(w.strip()) >= 2 and w.strip() not in self.stop_words]

    def _read_file(self, file_path: Path) -> str:
        """安全读取文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            logger.warning(f"跳过二进制文件: {file_path.name}")
            return ""
        except PermissionError:
            logger.warning(f"权限不足: {file_path.name}")
            return ""
        except Exception as e:
            logger.warning(f"读取文件失败: {file_path.name} - {e}")
            return ""

    def build_index(self, force: bool = False) -> Dict[str, Any]:
        """构建/重建索引"""
        logger.info(f"开始构建中文索引，memory_dir: {self.memory_dir}")

        if not force:
            self.inverted_index = {}
            self.file_meta = {}

        md_files = list(self.memory_dir.glob("*.md"))
        if not md_files:
            logger.warning(f"没有找到 .md 文件 in {self.memory_dir}")
            return {"indexed_files": 0, "total_words": 0}

        indexed_count = 0
        total_words = 0

        for md_file in md_files:
            try:
                content = self._read_file(md_file)
                if not content:
                    continue

                mtime = md_file.stat().st_mtime
                file_key = md_file.name

                # 检查是否需要重新索引（文件未变化则跳过）
                if not force and file_key in self.file_meta:
                    if self.file_meta[file_key].get("mtime") == mtime:
                        # 文件未变化，使用已有索引数据
                        indexed_count += 1
                        total_words += len(self.file_meta[file_key].get("words", []))
                        continue

                # 分词
                words = self._tokenize(content)

                # 记录文件元数据
                self.file_meta[file_key] = {
                    "path": str(md_file),
                    "mtime": mtime,
                    "size": len(content),
                    "word_count": len(words),
                    "words": list(set(words)),  # 去重后的词列表
                    "indexed_at": datetime.now().isoformat(),
                }

                # 构建倒排索引
                word_positions: Dict[str, List[int]] = defaultdict(list)
                for pos, word in enumerate(words):
                    word_positions[word].append(pos)

                for word, positions in word_positions.items():
                    if word not in self.inverted_index:
                        self.inverted_index[word] = []
                    self.inverted_index[word].append({
                        "file": file_key,
                        "count": len(positions),
                        "positions": positions[:20],  # 只保留前20个位置
                    })

                total_words += len(words)
                indexed_count += 1

            except Exception as e:
                logger.warning(f"索引文件失败: {md_file.name} - {e}")

        # 保存索引
        self._save_index()

        logger.info(f"索引构建完成: {indexed_count} 个文件, {len(self.inverted_index)} 个词条")
        return {
            "indexed_files": indexed_count,
            "total_words": total_words,
            "unique_words": len(self.inverted_index),
        }

    def update_index(self) -> Dict[str, Any]:
        """增量更新索引"""
        return self.build_index(force=False)

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """中文搜索"""
        if not query.strip():
            return []

        # 对查询词分词
        query_words = self._tokenize(query)
        if not query_words:
            # 如果分词结果为空（全是停用词），直接用原查询做简单匹配
            query_words = [query.strip()]

        logger.info(f"搜索查询: '{query}' -> 分词: {query_words}")

        # 收集每个文件的相关度得分
        file_scores: Dict[str, Dict] = defaultdict(lambda: {"score": 0, "matched_words": set(), "match_details": []})

        for qword in query_words:
            if qword in self.inverted_index:
                for entry in self.inverted_index[qword]:
                    file_key = entry["file"]
                    count = entry["count"]
                    # 相关度评分：词频 * 匹配词数量权重
                    file_scores[file_key]["score"] += count * len(query_words)
                    file_scores[file_key]["matched_words"].add(qword)
                    file_scores[file_key]["match_details"].append({
                        "word": qword,
                        "count": count,
                    })
            else:
                # 模糊匹配：查询词是某个索引词的子串
                for indexed_word in self.inverted_index:
                    if qword in indexed_word or indexed_word in qword:
                        for entry in self.inverted_index[indexed_word]:
                            file_key = entry["file"]
                            count = entry["count"]
                            file_scores[file_key]["score"] += count * 0.3  # 模糊匹配低权重
                            file_scores[file_key]["matched_words"].add(indexed_word)
                            file_scores[file_key]["match_details"].append({
                                "word": indexed_word,
                                "count": count,
                                "fuzzy": True,
                            })

        # 排序
        results = []
        for file_key, data in file_scores.items():
            if data["score"] > 0:
                meta = self.file_meta.get(file_key, {})
                content = self._read_file(Path(meta.get("path", self.memory_dir / file_key)))
                snippet = self._extract_snippet(content, query, query_words)

                results.append({
                    "title": file_key.replace('.md', ''),
                    "file": file_key,
                    "score": data["score"],
                    "matched_words": list(data["matched_words"]),
                    "match_count": len(data["match_details"]),
                    "snippet": snippet,
                    "size": meta.get("size", 0),
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def _extract_snippet(self, content: str, query: str, query_words: List[str]) -> str:
        """提取内容片段"""
        content = content.replace("\n", " ").strip()
        max_length = 200

        # 优先找第一个匹配词的位置
        query_lower = query.lower()
        content_lower = content.lower()

        best_idx = -1
        for qw in query_words:
            idx = content_lower.find(qw)
            if idx != -1:
                if best_idx == -1 or idx < best_idx:
                    best_idx = idx

        if best_idx == -1:
            idx = content_lower.find(query_lower)
            if idx != -1:
                best_idx = idx

        if best_idx == -1:
            return content[:max_length] + "..." if len(content) > max_length else content

        start = max(0, best_idx - 50)
        end = min(len(content), best_idx + len(query) + 150)

        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet

    def get_stats(self) -> Dict[str, Any]:
        """获取索引统计"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "total_words": len(self.inverted_index),
            "total_files": len(self.file_meta),
            "memory_dir": str(self.memory_dir),
        }
