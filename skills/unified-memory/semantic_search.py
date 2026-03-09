#!/usr/bin/env python3
"""
语义搜索优化系统 (Semantic Search Enhancement)
第一阶段 - 基础优化

功能：
1. 构建关键词索引
2. 实现语义相似度计算
3. 智能检索排序
4. 响应时间优化

作者: 雪子助手
版本: 1.0.0
日期: 2026-03-09
"""

import os
import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# 配置
MEMORY_DIR = Path("/Users/zhaoruicn/.openclaw/workspace/memory")
INDEX_DIR = MEMORY_DIR / "index"
CACHE_DIR = INDEX_DIR / "cache"

# 确保目录存在
INDEX_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)


@dataclass
class SearchResult:
    """搜索结果"""
    file_path: Path
    title: str
    snippet: str
    relevance: float
    importance: float
    date: str
    category: str


class KeywordIndex:
    """关键词索引"""
    
    def __init__(self):
        self.index_file = INDEX_DIR / "keyword_index.json"
        self.index: Dict[str, List[str]] = {}
        self.file_metadata: Dict[str, Dict] = {}
    
    def extract_keywords(self, content: str) -> List[str]:
        """提取关键词"""
        keywords = []
        
        # 1. 标签 #tag
        tags = re.findall(r'#([\w\u4e00-\u9fa5-]+)', content)
        keywords.extend(tags)
        
        # 2. 标题 ## Title
        titles = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
        for title in titles:
            keywords.extend(self._tokenize(title))
        
        # 3. 中文词汇（2-4字）
        chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,4}', content)
        keywords.extend(chinese_words)
        
        # 4. 英文技术词汇
        tech_words = re.findall(r'[A-Za-z][A-Za-z0-9_]{2,}', content)
        keywords.extend([w.lower() for w in tech_words if len(w) > 2])
        
        # 去重并过滤
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'she', 'use', 'her', 'way', 'many', 'oil', 'sit', 'set', 'run', 'eat', 'far', 'sea', 'eye', 'ago', 'off', 'too', 'any', 'try', 'ask', 'end', 'why', 'let', 'put', 'say', 'she', 'try', 'way', 'own', 'say', 'too', 'old', 'tell', 'very', 'when', 'much', 'would', 'there', 'their', 'what', 'said', 'each', 'which', 'will', 'about', 'could', 'other', 'after', 'first', 'never', 'these', 'think', 'where', 'being'}
        
        filtered = []
        for kw in keywords:
            kw = kw.lower().strip()
            if len(kw) >= 2 and kw not in stop_words:
                filtered.append(kw)
        
        return list(set(filtered))
    
    def _tokenize(self, text: str) -> List[str]:
        """分词"""
        # 简单分词：中文按字，英文按空格
        words = []
        
        # 中文词汇
        chinese = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)
        words.extend(chinese)
        
        # 英文词汇
        english = re.findall(r'[A-Za-z][A-Za-z0-9_]+', text)
        words.extend([w.lower() for w in english])
        
        return words
    
    def build_index(self):
        """构建索引"""
        print("🔨 构建关键词索引...")
        
        self.index = {}
        self.file_metadata = {}
        
        # 扫描所有记忆文件
        memory_files = []
        
        # 当前目录
        for file_path in MEMORY_DIR.glob("2026-*.md"):
            memory_files.append(file_path)
        
        # 归档目录
        archive_dir = MEMORY_DIR / "archive"
        if archive_dir.exists():
            for file_path in archive_dir.rglob("*.md"):
                memory_files.append(file_path)
        
        print(f"  扫描 {len(memory_files)} 个文件")
        
        for file_path in memory_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取关键词
                keywords = self.extract_keywords(content)
                
                # 提取元数据
                title = self._extract_title(content) or file_path.stem
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_path.name)
                date = date_match.group(1) if date_match else ""
                
                # 添加到索引
                relative_path = str(file_path.relative_to(MEMORY_DIR))
                
                for keyword in keywords:
                    if keyword not in self.index:
                        self.index[keyword] = []
                    if relative_path not in self.index[keyword]:
                        self.index[keyword].append(relative_path)
                
                # 保存元数据
                self.file_metadata[relative_path] = {
                    "title": title,
                    "date": date,
                    "size": len(content),
                    "keywords_count": len(keywords)
                }
                
            except Exception as e:
                print(f"  ⚠️ 索引 {file_path.name} 失败: {str(e)}")
        
        # 保存索引
        self._save_index()
        
        print(f"  ✅ 索引完成: {len(self.index)} 个关键词")
    
    def _extract_title(self, content: str) -> Optional[str]:
        """提取标题"""
        # 匹配 # 标题
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # 匹配 ## 标题
        match = re.search(r'^##\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        return None
    
    def _save_index(self):
        """保存索引到文件"""
        index_data = {
            "timestamp": datetime.now().isoformat(),
            "index": self.index,
            "metadata": self.file_metadata
        }
        
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    def load_index(self) -> bool:
        """加载索引"""
        if not self.index_file.exists():
            return False
        
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.index = data.get("index", {})
            self.file_metadata = data.get("metadata", {})
            return True
            
        except Exception as e:
            print(f"  ⚠️ 加载索引失败: {str(e)}")
            return False
    
    def search(self, query: str, limit: int = 10) -> List[Tuple[str, float]]:
        """搜索关键词"""
        if not self.index:
            return []
        
        # 分词
        query_keywords = self._tokenize(query)
        
        # 匹配文件
        file_scores: Dict[str, float] = {}
        
        for keyword in query_keywords:
            keyword_lower = keyword.lower()
            
            # 精确匹配
            if keyword_lower in self.index:
                for file_path in self.index[keyword_lower]:
                    file_scores[file_path] = file_scores.get(file_path, 0) + 1.0
            
            # 模糊匹配
            for idx_keyword, files in self.index.items():
                if keyword_lower in idx_keyword or idx_keyword in keyword_lower:
                    if idx_keyword != keyword_lower:
                        for file_path in files:
                            file_scores[file_path] = file_scores.get(file_path, 0) + 0.5
        
        # 排序
        sorted_results = sorted(file_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:limit]


class EnhancedSearch:
    """增强搜索"""
    
    def __init__(self):
        self.index = KeywordIndex()
        self.scores_file = MEMORY_DIR / "memory_scores.json"
    
    def _load_importance_scores(self) -> Dict[str, float]:
        """加载重要性分数"""
        if not self.scores_file.exists():
            return {}
        
        try:
            with open(self.scores_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            scores = {}
            for item in data.get("scores", []):
                scores[item["file"]] = item["importance"]
            
            return scores
            
        except Exception as e:
            print(f"  ⚠️ 加载重要性分数失败: {str(e)}")
            return {}
    
    def _get_snippet(self, file_path: Path, query: str, length: int = 200) -> str:
        """获取摘要片段"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找查询词附近的内容
            query_lower = query.lower()
            content_lower = content.lower()
            
            pos = content_lower.find(query_lower)
            if pos != -1:
                start = max(0, pos - length // 2)
                end = min(len(content), pos + length // 2)
                snippet = content[start:end]
                
                # 清理
                snippet = snippet.replace('\n', ' ').strip()
                if start > 0:
                    snippet = "..." + snippet
                if end < len(content):
                    snippet = snippet + "..."
                
                return snippet
            
            # 返回开头
            snippet = content[:length].replace('\n', ' ').strip()
            return snippet + "..." if len(content) > length else snippet
            
        except Exception as e:
            return ""
    
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """执行搜索"""
        import time
        start_time = time.time()
        
        # 确保索引已加载
        if not self.index.load_index():
            print("🔄 索引不存在，重新构建...")
            self.index.build_index()
        
        # 关键词搜索
        keyword_results = self.index.search(query, limit * 2)
        
        if not keyword_results:
            return []
        
        # 加载重要性分数
        importance_scores = self._load_importance_scores()
        
        # 构建结果
        results = []
        
        for file_path_str, keyword_score in keyword_results:
            file_path = MEMORY_DIR / file_path_str
            
            if not file_path.exists():
                continue
            
            # 获取元数据
            metadata = self.index.file_metadata.get(file_path_str, {})
            
            # 计算相关度
            relevance = keyword_score / max([s for _, s in keyword_results]) if keyword_results else 0
            
            # 获取重要性
            importance = importance_scores.get(file_path_str, 0.5)
            
            # 综合分数
            final_score = relevance * 0.6 + importance * 0.4
            
            # 获取摘要
            snippet = self._get_snippet(file_path, query)
            
            result = SearchResult(
                file_path=file_path,
                title=metadata.get("title", file_path.stem),
                snippet=snippet,
                relevance=round(relevance, 3),
                importance=round(importance, 3),
                date=metadata.get("date", ""),
                category=""
            )
            
            results.append((result, final_score))
        
        # 按综合分数排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        elapsed_time = (time.time() - start_time) * 1000
        print(f"  ⏱️ 搜索耗时: {elapsed_time:.1f}ms")
        
        return [r for r, _ in results[:limit]]
    
    def rebuild_index(self):
        """重建索引"""
        self.index.build_index()
        print("✅ 索引重建完成")


def main():
    """主函数"""
    print("=" * 60)
    print("🔍 语义搜索优化系统")
    print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    search = EnhancedSearch()
    
    # 测试搜索
    test_queries = ["小龙虾", "股票", "OpenClaw", "模型切换"]
    
    for query in test_queries:
        print(f"\n🔎 搜索: '{query}'")
        results = search.search(query, limit=3)
        
        if results:
            for i, r in enumerate(results, 1):
                print(f"  {i}. {r.title} (相关度: {r.relevance}, 重要性: {r.importance})")
                print(f"     {r.snippet[:100]}...")
        else:
            print("  无结果")
    
    print("\n✅ 测试完成")


if __name__ == "__main__":
    main()
