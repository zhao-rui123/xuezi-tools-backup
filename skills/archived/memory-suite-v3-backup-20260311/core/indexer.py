#!/usr/bin/env python3
"""
Memory Suite v3.0 - 语义索引模块
负责创建和维护记忆文件的搜索索引
"""

import os
import sys
import json
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('indexer')

# 路径配置
WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
INDEX_DIR = MEMORY_DIR / "index"

# 停用词
STOP_WORDS = {
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那',
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
    'http', 'https', 'com', '文件', '可以', '使用', '进行', '需要', '已经', '完成', '添加', '通过', '如果', '然后', '今天', '现在', '开始', '我们', '他们', '这个', '那个'
}


class IndexManager:
    """索引管理器"""
    
    def __init__(self):
        self.index_dir = INDEX_DIR
        self.keyword_index_file = self.index_dir / "keywords.json"
        self.file_index_file = self.index_dir / "file_index.json"
        self.ensure_directories()
        self.index_data = self._load_index()
    
    def ensure_directories(self):
        """确保目录存在"""
        self.index_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_index(self) -> Dict[str, Any]:
        """加载索引数据"""
        if self.keyword_index_file.exists():
            try:
                with open(self.keyword_index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载索引失败: {e}")
        return {"keywords": {}, "files": {}}
    
    def _save_index(self):
        """保存索引数据"""
        try:
            with open(self.keyword_index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存索引失败: {e}")
    
    def extract_keywords(self, text: str, top_n: int = 30) -> List[Tuple[str, int]]:
        """
        从文本中提取关键词
        
        Args:
            text: 输入文本
            top_n: 返回的关键词数量
        
        Returns:
            关键词列表 (词, 频次)
        """
        words = []
        
        # 提取中文词（2-6个字）
        chinese = re.findall(r'[\u4e00-\u9fa5]{2,6}', text)
        words.extend(chinese)
        
        # 提取英文词（3个字母以上）
        english = re.findall(r'[a-zA-Z_]{3,}', text)
        words.extend([w.lower() for w in english])
        
        # 过滤停用词
        filtered = [w for w in words if w not in STOP_WORDS and len(w) >= 2]
        
        # 统计频次
        counts = Counter(filtered)
        return counts.most_common(top_n)
    
    def update_index(self) -> Dict[str, Any]:
        """
        更新索引
        
        Returns:
            更新结果统计
        """
        logger.info("更新索引...")
        
        stats = {
            "indexed_files": 0,
            "total_keywords": 0,
            "updated_at": datetime.now().isoformat()
        }
        
        try:
            # 获取所有记忆文件
            memory_files = list(MEMORY_DIR.glob("*.md"))
            
            # 构建文件索引
            file_index = {}
            all_keywords = Counter()
            
            for f in memory_files:
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        content = fp.read()
                    
                    # 提取关键词
                    keywords = self.extract_keywords(content, top_n=50)
                    
                    # 添加到文件索引
                    file_index[f.name] = {
                        "path": str(f),
                        "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                        "size": f.stat().st_size,
                        "keywords": keywords[:20]
                    }
                    
                    # 累积关键词
                    for kw, count in keywords:
                        all_keywords[kw] += count
                    
                    stats["indexed_files"] += 1
                    
                except Exception as e:
                    logger.warning(f"索引文件失败: {f} - {e}")
            
            # 更新索引数据
            self.index_data = {
                "keywords": dict(all_keywords.most_common(500)),
                "files": file_index,
                "updated_at": stats["updated_at"]
            }
            
            stats["total_keywords"] = len(all_keywords)
            
            # 保存索引
            self._save_index()
            
            logger.info(f"索引更新完成: {stats['indexed_files']} 个文件, {stats['total_keywords']} 个关键词")
            
        except Exception as e:
            logger.error(f"更新索引失败: {e}")
        
        return stats
    
    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        搜索记忆
        
        Args:
            query: 搜索关键词
            top_k: 返回结果数量
        
        Returns:
            搜索结果列表
        """
        logger.info(f"搜索: {query}")
        
        results = []
        query_lower = query.lower()
        query_keywords = self.extract_keywords(query, top_n=10)
        
        try:
            # 确保索引已加载
            if not self.index_data.get("files"):
                self.index_data = self._load_index()
            
            file_index = self.index_data.get("files", {})
            
            for filename, file_info in file_index.items():
                score = 0.0
                matched_keywords = []
                
                # 检查文件名匹配
                if query_lower in filename.lower():
                    score += 2.0
                    matched_keywords.append(f"filename:{query}")
                
                # 检查关键词匹配
                for kw, _ in query_keywords:
                    file_keywords = [k for k, _ in file_info.get("keywords", [])]
                    if kw in file_keywords:
                        score += 1.5
                        matched_keywords.append(kw)
                
                # 读取文件内容进行全文搜索
                file_path = file_info.get("path")
                if file_path:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 简单文本匹配
                        if query_lower in content.lower():
                            score += 1.0
                            # 提取匹配的片段
                            snippet = self._extract_snippet(content, query)
                            file_info["snippet"] = snippet
                        
                    except Exception as e:
                        logger.warning(f"读取文件失败: {file_path} - {e}")
                
                # 如果有关联，添加到结果
                if score > 0:
                    results.append({
                        "title": filename.replace('.md', ''),
                        "file": filename,
                        "path": file_info.get("path"),
                        "score": score,
                        "matched_keywords": matched_keywords,
                        "snippet": file_info.get("snippet", ""),
                        "modified": file_info.get("modified")
                    })
            
            # 按得分排序
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def _extract_snippet(self, content: str, query: str, max_length: int = 150) -> str:
        """从内容中提取包含查询词的片段"""
        query_lower = query.lower()
        lines = content.split('\n')
        
        for line in lines:
            if query_lower in line.lower():
                # 清理 markdown 格式
                clean_line = re.sub(r'[#*`]', '', line).strip()
                if len(clean_line) > max_length:
                    clean_line = clean_line[:max_length] + "..."
                return clean_line
        
        # 如果没有找到匹配，返回开头
        return content[:max_length] + "..." if len(content) > max_length else content
    
    def get_keyword_cloud(self, top_n: int = 50) -> List[Tuple[str, int]]:
        """
        获取关键词云
        
        Args:
            top_n: 返回的关键词数量
        
        Returns:
            关键词列表
        """
        if not self.index_data.get("keywords"):
            self.update_index()
        
        keywords = self.index_data.get("keywords", {})
        sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
        return sorted_keywords[:top_n]
    
    def get_file_stats(self) -> Dict[str, Any]:
        """获取文件统计信息"""
        if not self.index_data.get("files"):
            self.update_index()
        
        files = self.index_data.get("files", {})
        
        total_size = sum(f.get("size", 0) for f in files.values())
        
        return {
            "total_files": len(files),
            "total_size": self._format_size(total_size),
            "total_keywords": len(self.index_data.get("keywords", {})),
            "updated_at": self.index_data.get("updated_at")
        }
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"


def main():
    """测试入口"""
    manager = IndexManager()
    
    print("📇 索引模块测试")
    print("=" * 50)
    
    # 测试更新索引
    print("\n1. 更新索引...")
    stats = manager.update_index()
    print(f"   索引文件: {stats['indexed_files']} 个")
    print(f"   关键词: {stats['total_keywords']} 个")
    
    # 测试搜索
    print("\n2. 测试搜索...")
    query = "储能"
    results = manager.search(query, top_k=5)
    if results:
        print(f"   搜索 '{query}' 找到 {len(results)} 条结果:")
        for i, r in enumerate(results, 1):
            print(f"   {i}. {r['title']} (得分: {r['score']:.2f})")
    else:
        print("   未找到结果")
    
    # 测试关键词云
    print("\n3. 关键词云 TOP10...")
    keywords = manager.get_keyword_cloud(10)
    for i, (kw, count) in enumerate(keywords, 1):
        bar = "█" * min(count, 20)
        print(f"   {i}. {kw}: {count} {bar}")
    
    # 测试统计
    print("\n4. 索引统计...")
    file_stats = manager.get_file_stats()
    print(f"   总文件: {file_stats['total_files']} 个")
    print(f"   总大小: {file_stats['total_size']}")
    print(f"   更新时间: {file_stats['updated_at']}")
    
    print("\n" + "=" * 50)


if __name__ == '__main__':
    main()
