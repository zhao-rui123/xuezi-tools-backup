#!/usr/bin/env python3
"""
统一索引模块 - 同时支持中文（jieba分词）和英文/数字（FTS风格关键词）搜索
"""

import jieba
import json
import re
import os
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict, Counter

logger = logging.getLogger('memory-suite')


class UnifiedIndexer:
    """统一索引管理器 - 混合中英文搜索"""

    def __init__(self, unified_dir: str = None, memory_dir: str = None):
        if unified_dir is None:
            unified_dir = str(Path(__file__).parent / "unified_index")
        if memory_dir is None:
            memory_dir = "/Users/zhaoruicn/.openclaw/workspace/memory"

        self.unified_dir = Path(unified_dir)
        self.memory_dir = Path(memory_dir)
        self.keywords_dir = self.unified_dir / "keywords"
        self.chinese_dir = self.unified_dir / "chinese"
        
        self.unified_dir.mkdir(parents=True, exist_ok=True)
        self.keywords_dir.mkdir(parents=True, exist_ok=True)
        self.chinese_dir.mkdir(parents=True, exist_ok=True)

        self.index_file = self.unified_dir / "index.json"  # file_path -> metadata
        self.stats_file = self.unified_dir / "stats.json"

        # 停用词
        self.stop_words = {
            '的', '了', '是', '在', '有', '和', '与', '或', '但', '就', '都', '也',
            '要', '会', '能', '可以', '这', '那', '他', '她', '它', '我', '你',
            '我们', '你们', '他们', '们', '自己', '什么', '哪个', '哪些',
            '这个', '那个', '一个', '一些', '还', '很', '最', '更', '已经', '正在',
            '着', '过', '地', '得', '而', '于', '上', '下', '中', '为', '而且',
            'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'must', 'shall', 'can', 'and', 'or', 'but', 'if', 'else',
            'when', 'at', 'from', 'this', 'that', 'these', 'those', 'am', 'not',
            'no', 'nor', 'a', 'an', 'to', 'of', 'in', 'for', 'on', 'with', 'as',
        }

        # 加载已有索引
        self.file_index: Dict[str, Dict] = {}
        self._load_index()

    def _load_index(self):
        """加载主索引"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.file_index = json.load(f)
            except Exception as e:
                logger.warning(f"加载主索引失败: {e}")
                self.file_index = {}

    def _save_index(self):
        """保存主索引"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.file_index, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存主索引失败: {e}")
            return False

    def _is_mostly_chinese(self, text: str) -> bool:
        """判断文本是否主要是中文"""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(re.sub(r'\s', '', text))
        if total_chars == 0:
            return False
        return chinese_chars / total_chars > 0.4

    def _is_english_word(self, word: str) -> bool:
        """判断是否是英文/数字词（FTS风格）"""
        return bool(re.match(r'^[a-zA-Z0-9_\-]+$', word)) and len(word) >= 1

    def _tokenize(self, text: str) -> Tuple[List[str], List[str]]:
        """分词：返回 (英文/数字词列表, 中文词列表)"""
        text = re.sub(r'[#*`\[\](){}|_]', ' ', text)
        text = re.sub(r'https?://\S+', ' ', text)  # 移除URL
        
        english_words = []
        chinese_words = []
        
        # 英文/数字词（直接提取）
        for word in re.findall(r'[a-zA-Z0-9_\-]+', text.lower()):
            if word not in self.stop_words and len(word) >= 1:
                english_words.append(word)
        
        # 中文词（jieba分词）—— 只要有中文就分词，不再检查整体占比
        if re.search(r'[\u4e00-\u9fff]', text):
            cn_tokens = [w for w in jieba.cut(text, cut_all=False) 
                        if w.strip() and w not in self.stop_words and len(w) >= 2
                        and not self._is_english_word(w)
                        and re.search(r'[\u4e00-\u9fff]', w)]  # 确保词中含中文
            chinese_words.extend(cn_tokens)
        
        return english_words, chinese_words

    def build_index(self, force: bool = False) -> Dict[str, Any]:
        """构建统一索引"""
        start = datetime.now()
        
        # 扫描记忆文件
        memory_files = list(self.memory_dir.glob("*.md"))
        memory_files.sort(key=lambda f: -f.stat().st_mtime)
        
        indexed_files = 0
        total_keywords = Counter()
        
        for mf in memory_files:
            try:
                with open(mf, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                english_words, chinese_words = self._tokenize(content)
                
                # 更新关键词索引
                en_count = Counter(english_words)
                cn_count = Counter(chinese_words)
                total_keywords.update(en_count)
                total_keywords.update(cn_count)
                
                # 保存文件元数据
                self.file_index[str(mf)] = {
                    "name": mf.name,
                    "size": len(content),
                    "en_keywords": list(set(english_words)),
                    "cn_keywords": list(set(chinese_words)),
                    "updated": datetime.now().isoformat(),
                    "mtime": int(mf.stat().st_mtime),
                }
                
                indexed_files += 1
                
            except Exception as e:
                logger.warning(f"索引文件失败 {mf.name}: {e}")
        
        # 保存关键词倒排索引
        self._save_index()
        self._build_inverted_index()
        
        # 更新统计
        stats = {
            "updated_at": datetime.now().isoformat(),
            "total_files": len(self.file_index),
            "total_keywords": len(total_keywords),
            "indexed_files": indexed_files,
            "memory_dir": str(self.memory_dir),
            "elapsed_seconds": (datetime.now() - start).total_seconds(),
        }
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"统一索引构建完成: {indexed_files} 文件, {len(total_keywords)} 关键词")
        return stats

    def _build_inverted_index(self):
        """构建倒排索引文件"""
        # 收集所有词 -> 文件映射
        en_map: Dict[str, Set[str]] = defaultdict(set)
        cn_map: Dict[str, Set[str]] = defaultdict(set)
        
        for file_path, meta in self.file_index.items():
            for kw in meta.get('en_keywords', []):
                en_map[kw].add(file_path)
            for kw in meta.get('cn_keywords', []):
                cn_map[kw].add(file_path)
        
        # 保存英文关键词索引
        for word, files in en_map.items():
            word_file = self.keywords_dir / f"{word}.json"
            try:
                existing = []
                if word_file.exists():
                    with open(word_file, 'r', encoding='utf-8') as f:
                        existing = json.load(f)
                existing_set = set(existing)
                existing_set.update(files)
                with open(word_file, 'w', encoding='utf-8') as f:
                    json.dump(sorted(existing_set), f, ensure_ascii=False)
            except Exception as e:
                logger.warning(f"保存关键词 {word} 失败: {e}")
        
        # 保存中文关键词索引
        for word, files in cn_map.items():
            word_file = self.chinese_dir / f"{word}.json"
            try:
                existing = []
                if word_file.exists():
                    with open(word_file, 'r', encoding='utf-8') as f:
                        existing = json.load(f)
                existing_set = set(existing)
                existing_set.update(files)
                with open(word_file, 'w', encoding='utf-8') as f:
                    json.dump(sorted(existing_set), f, ensure_ascii=False)
            except Exception as e:
                logger.warning(f"保存中文词 {word} 失败: {e}")

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """统一搜索：同时支持中英文"""
        english_words, chinese_words = self._tokenize(query)
        
        # 如果全是英文，直接用FTS风格搜索
        if english_words and not chinese_words:
            return self._search_keywords(english_words, limit)
        
        # 如果全是中文，用jieba搜索
        if chinese_words and not english_words:
            return self._search_chinese(chinese_words, limit)
        
        # 混合：合并两种搜索结果
        en_results = self._search_keywords(english_words, limit * 2)
        cn_results = self._search_chinese(chinese_words, limit * 2)
        
        # 合并结果，按分数排序
        combined = self._merge_results(en_results, cn_results, english_words, chinese_words)
        return combined[:limit]

    def _search_keywords(self, words: List[str], limit: int) -> List[Dict[str, Any]]:
        """FTS风格英文/数字搜索"""
        file_scores: Dict[str, float] = defaultdict(float)
        
        for word in words:
            word_file = self.keywords_dir / f"{word}.json"
            if word_file.exists():
                try:
                    with open(word_file, 'r', encoding='utf-8') as f:
                        files = json.load(f)
                    for f_path in files:
                        file_scores[f_path] += 1.0
                except Exception:
                    pass
        
        return self._score_to_results(file_scores)

    def _search_chinese(self, words: List[str], limit: int) -> List[Dict[str, Any]]:
        """中文jieba分词搜索"""
        file_scores: Dict[str, float] = defaultdict(float)
        
        for word in words:
            word_file = self.chinese_dir / f"{word}.json"
            if word_file.exists():
                try:
                    with open(word_file, 'r', encoding='utf-8') as f:
                        files = json.load(f)
                    for f_path in files:
                        file_scores[f_path] += 1.0
                except Exception:
                    pass
        
        return self._score_to_results(file_scores)

    def _score_to_results(self, file_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """将分数映射转换为结果列表"""
        if not file_scores:
            return []
        
        results = []
        for file_path, score in sorted(file_scores.items(), key=lambda x: -x[1]):
            if file_path in self.file_index:
                meta = self.file_index[file_path]
                results.append({
                    "path": file_path,
                    "name": meta.get("name", os.path.basename(file_path)),
                    "score": score,
                    "snippet": self._get_snippet(file_path),
                })
        
        return results

    def _merge_results(self, en_results: List, cn_results: List,
                       en_words: List, cn_words: List) -> List[Dict]:
        """合并中英文搜索结果"""
        score_map: Dict[str, Dict] = {}
        
        # 英文结果权重 x2（精确匹配英文关键词）
        for r in en_results:
            path = r['path']
            r['score'] = r['score'] * 2.0
            r['source'] = 'en'
            score_map[path] = r
        
        # 合并中文结果
        for r in cn_results:
            path = r['path']
            if path in score_map:
                score_map[path]['score'] += r['score']
                score_map[path]['source'] = 'mixed'
            else:
                r['source'] = 'cn'
                score_map[path] = r
        
        # 按分数排序
        sorted_results = sorted(score_map.values(), key=lambda x: -x['score'])
        
        # 重新生成snippet
        for r in sorted_results:
            r['snippet'] = self._get_snippet(r['path'])
        
        return sorted_results

    def _get_snippet(self, file_path: str, max_chars: int = 150) -> str:
        """获取文件片段"""
        try:
            if not os.path.exists(file_path):
                return ""
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content[:max_chars].replace('\n', ' ')
        except Exception:
            return ""

    # ============ FTS集成搜索 ============
    
    def search_fts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """通过OpenClaw FTS索引搜索"""
        fts_db = Path.home() / ".openclaw" / "memory" / "claude.sqlite"
        if not fts_db.exists():
            return []
        
        try:
            conn = sqlite3.connect(str(fts_db))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # FTS5搜索
            cursor.execute("""
                SELECT path, snippet(chunks_fts, 0, '【', '】', '...', 30) as snippet,
                       rank
                FROM chunks_fts
                WHERE chunks_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "path": row['path'],
                    "name": os.path.basename(row['path']),
                    "score": -row['rank'] if row['rank'] else 0,
                    "snippet": row['snippet'] or '',
                    "source": "fts",
                })
            
            conn.close()
            return results
        except Exception as e:
            logger.warning(f"FTS搜索失败: {e}")
            return []

    def search_all(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """综合搜索：统一索引 + FTS，取并集去重"""
        # 同时搜索
        unified = self.search(query, limit=limit * 2)
        fts = self.search_fts(query, limit=limit * 2)
        
        merged: Dict[str, Dict] = {}
        for r in unified:
            merged[r['path']] = r
        for r in fts:
            path = r['path']
            if path in merged:
                merged[path]['score'] = max(merged[path]['score'], r['score'])
                merged[path]['source'] = 'both'
            else:
                merged[path] = r
        
        results = sorted(merged.values(), key=lambda x: -x['score'])[:limit]
        return results
