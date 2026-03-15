#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识关联模块 - Knowledge Graph

功能：
1. 读取知识库所有条目
2. 分析关联关系（相同关键词、相关主题）
3. 生成知识图谱（简单的JSON格式）
4. 支持查询相关条目

作者: November Agent (Builder)
日期: 2026-03-10
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict


@dataclass
class KnowledgeEntry:
    """知识库条目"""
    id: str
    title: str
    path: str
    content: str
    entry_type: str  # 'project', 'decision', 'problem', 'reference', 'operation'
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    related_entries: List[str] = field(default_factory=list)
    created_date: Optional[str] = None
    updated_date: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Relationship:
    """条目间关系"""
    source_id: str
    target_id: str
    relation_type: str  # 'tag_shared', 'keyword_shared', 'content_similar', 'reference'
    strength: float  # 0.0 - 1.0
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class KnowledgeGraph:
    """知识图谱核心类"""
    
    def __init__(self, knowledge_base_path: str = "knowledge-base"):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.entries: Dict[str, KnowledgeEntry] = {}
        self.relationships: List[Relationship] = []
        self.tag_index: Dict[str, Set[str]] = defaultdict(set)
        self.keyword_index: Dict[str, Set[str]] = defaultdict(set)
        
    def scan_entries(self) -> List[KnowledgeEntry]:
        """扫描知识库所有条目"""
        entries = []
        
        if not self.knowledge_base_path.exists():
            return entries
        
        # 定义扫描路径和类型映射
        scan_paths = {
            "projects": "project",
            "decisions": "decision",
            "problems": "problem",
            "references": "reference",
            "operations": "operation",
            "plans": "plan"
        }
        
        entry_id = 0
        for folder, entry_type in scan_paths.items():
            folder_path = self.knowledge_base_path / folder
            if not folder_path.exists():
                continue
            
            for md_file in folder_path.rglob("*.md"):
                entry = self._parse_entry(md_file, entry_type, entry_id)
                if entry:
                    entries.append(entry)
                    entry_id += 1
        
        # 同时扫描根目录的索引文件
        for md_file in self.knowledge_base_path.glob("*.md"):
            entry = self._parse_entry(md_file, "index", entry_id)
            if entry:
                entries.append(entry)
                entry_id += 1
        
        return entries
    
    def _parse_entry(self, file_path: Path, entry_type: str, entry_id: int) -> Optional[KnowledgeEntry]:
        """解析单个条目文件"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # 提取标题（第一个 # 开头的行）
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else file_path.stem
            
            # 提取标签
            tags = re.findall(r'#(\w+)', content)
            
            # 提取关键词（从内容中提取重要词汇）
            keywords = self._extract_keywords(content)
            
            # 提取日期
            date_patterns = [
                r'\*\*日期\*\*:\s*(\d{4}-\d{2}-\d{2})',
                r'\*\*创建时间\*\*:\s*(\d{4}-\d{2}-\d{2})',
                r'\*\*更新时间\*\*:\s*(\d{4}-\d{2}-\d{2})',
            ]
            created_date = None
            updated_date = None
            for pattern in date_patterns:
                match = re.search(pattern, content)
                if match:
                    if created_date is None:
                        created_date = match.group(1)
                    updated_date = match.group(1)
            
            # 生成唯一ID
            entry_uid = f"{entry_type}_{entry_id}_{file_path.stem}"
            
            return KnowledgeEntry(
                id=entry_uid,
                title=title,
                path=str(file_path.relative_to(self.knowledge_base_path)),
                content=content[:5000],  # 限制内容长度
                entry_type=entry_type,
                tags=list(set(tags)),
                keywords=keywords,
                created_date=created_date,
                updated_date=updated_date
            )
        except Exception as e:
            print(f"解析文件失败 {file_path}: {e}")
            return None
    
    def _extract_keywords(self, content: str) -> List[str]:
        """从内容中提取关键词"""
        # 定义停用词
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', 
                      '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
                      '你', '会', '着', '没有', '看', '好', '自己', '这', '那',
                      'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                      'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                      'could', 'should', 'may', 'might', 'must', 'can', 'need'}
        
        # 提取中文词汇（2-6个字符）
        chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,6}', content)
        
        # 提取英文单词
        english_words = re.findall(r'[a-zA-Z]{3,}', content.lower())
        
        # 统计词频
        word_freq = defaultdict(int)
        for word in chinese_words + english_words:
            if word.lower() not in stop_words and len(word) >= 2:
                word_freq[word] += 1
        
        # 返回高频词（前15个）
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:15]]
    
    def build_graph(self) -> None:
        """构建知识图谱"""
        print("开始扫描知识库条目...")
        entries = self.scan_entries()
        
        # 存储条目
        for entry in entries:
            self.entries[entry.id] = entry
            
            # 建立标签索引
            for tag in entry.tags:
                self.tag_index[tag].add(entry.id)
            
            # 建立关键词索引
            for keyword in entry.keywords:
                self.keyword_index[keyword].add(entry.id)
        
        print(f"已加载 {len(self.entries)} 个条目")
        
        # 分析关联关系
        print("分析条目关联关系...")
        self._analyze_relationships()
        print(f"发现 {len(self.relationships)} 个关系")
    
    def _analyze_relationships(self) -> None:
        """分析条目间的关联关系"""
        entry_ids = list(self.entries.keys())
        
        for i, source_id in enumerate(entry_ids):
            source = self.entries[source_id]
            
            for target_id in entry_ids[i+1:]:
                target = self.entries[target_id]
                
                # 1. 标签共享关系
                shared_tags = set(source.tags) & set(target.tags)
                if shared_tags:
                    strength = len(shared_tags) / max(len(source.tags), len(target.tags), 1)
                    self.relationships.append(Relationship(
                        source_id=source_id,
                        target_id=target_id,
                        relation_type="tag_shared",
                        strength=round(strength, 2),
                        details={"shared_tags": list(shared_tags)}
                    ))
                
                # 2. 关键词共享关系
                shared_keywords = set(source.keywords) & set(target.keywords)
                if shared_keywords:
                    strength = len(shared_keywords) / max(len(source.keywords), len(target.keywords), 1)
                    self.relationships.append(Relationship(
                        source_id=source_id,
                        target_id=target_id,
                        relation_type="keyword_shared",
                        strength=round(strength, 2),
                        details={"shared_keywords": list(shared_keywords)}
                    ))
                
                # 3. 内容相似度（简单实现：共同词汇比例）
                content_sim = self._calculate_content_similarity(source.content, target.content)
                if content_sim > 0.1:  # 阈值
                    self.relationships.append(Relationship(
                        source_id=source_id,
                        target_id=target_id,
                        relation_type="content_similar",
                        strength=round(content_sim, 2),
                        details={}
                    ))
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """计算内容相似度（Jaccard相似度）"""
        # 提取词汇
        words1 = set(re.findall(r'[\u4e00-\u9fa5]{2,}|[a-zA-Z]{3,}', content1.lower()))
        words2 = set(re.findall(r'[\u4e00-\u9fa5]{2,}|[a-zA-Z]{3,}', content2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def export_to_json(self, output_path: Optional[str] = None) -> str:
        """导出知识图谱为JSON格式"""
        graph_data = {
            "metadata": {
                "version": "1.0",
                "total_entries": len(self.entries),
                "total_relationships": len(self.relationships),
                "generated_at": self._get_current_timestamp()
            },
            "entries": {entry_id: entry.to_dict() for entry_id, entry in self.entries.items()},
            "relationships": [rel.to_dict() for rel in self.relationships],
            "indices": {
                "tags": {tag: list(entry_ids) for tag, entry_ids in self.tag_index.items()},
                "keywords": {kw: list(entry_ids) for kw, entry_ids in self.keyword_index.items()}
            }
        }
        
        json_str = json.dumps(graph_data, ensure_ascii=False, indent=2)
        
        if output_path:
            Path(output_path).write_text(json_str, encoding='utf-8')
            print(f"知识图谱已导出到: {output_path}")
        
        return json_str
    
    def find_related_entries(self, entry_id: str, min_strength: float = 0.1) -> List[Dict[str, Any]]:
        """查询与指定条目相关的其他条目"""
        if entry_id not in self.entries:
            return []
        
        related = []
        for rel in self.relationships:
            if rel.source_id == entry_id:
                target_id = rel.target_id
            elif rel.target_id == entry_id:
                target_id = rel.source_id
            else:
                continue
            
            if rel.strength >= min_strength:
                related.append({
                    "entry": self.entries[target_id].to_dict(),
                    "relationship": rel.to_dict()
                })
        
        # 按关联强度排序
        related.sort(key=lambda x: x["relationship"]["strength"], reverse=True)
        return related
    
    def search_by_tag(self, tag: str) -> List[KnowledgeEntry]:
        """按标签搜索条目"""
        entry_ids = self.tag_index.get(tag, set())
        return [self.entries[eid] for eid in entry_ids if eid in self.entries]
    
    def search_by_keyword(self, keyword: str) -> List[KnowledgeEntry]:
        """按关键词搜索条目"""
        entry_ids = self.keyword_index.get(keyword, set())
        return [self.entries[eid] for eid in entry_ids if eid in self.entries]
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """综合搜索（支持标签、关键词、标题匹配）"""
        results = []
        query_lower = query.lower()
        
        for entry in self.entries.values():
            score = 0
            match_reasons = []
            
            # 标签匹配
            if query in entry.tags:
                score += 10
                match_reasons.append(f"标签匹配: #{query}")
            
            # 关键词匹配
            if query in entry.keywords:
                score += 8
                match_reasons.append(f"关键词匹配: {query}")
            
            # 标题匹配
            if query_lower in entry.title.lower():
                score += 5
                match_reasons.append(f"标题包含: {query}")
            
            # 内容匹配
            if query_lower in entry.content.lower():
                score += 2
                match_reasons.append(f"内容包含: {query}")
            
            if score > 0:
                results.append({
                    "entry": entry.to_dict(),
                    "score": score,
                    "reasons": match_reasons
                })
        
        # 按分数排序
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def get_entry_summary(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """获取条目摘要信息"""
        if entry_id not in self.entries:
            return None
        
        entry = self.entries[entry_id]
        related = self.find_related_entries(entry_id)
        
        return {
            "entry": entry.to_dict(),
            "related_count": len(related),
            "top_related": related[:5],
            "tags": entry.tags,
            "keywords": entry.keywords
        }
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """获取知识图谱统计信息"""
        entry_types = defaultdict(int)
        for entry in self.entries.values():
            entry_types[entry.entry_type] += 1
        
        rel_types = defaultdict(int)
        for rel in self.relationships:
            rel_types[rel.relation_type] += 1
        
        return {
            "total_entries": len(self.entries),
            "total_relationships": len(self.relationships),
            "entry_types": dict(entry_types),
            "relationship_types": dict(rel_types),
            "unique_tags": len(self.tag_index),
            "unique_keywords": len(self.keyword_index),
            "avg_relationships_per_entry": len(self.relationships) / len(self.entries) if self.entries else 0
        }
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ==================== CLI 接口 ====================

def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="知识图谱工具")
    parser.add_argument("--path", default="knowledge-base", help="知识库路径")
    parser.add_argument("--build", action="store_true", help="构建知识图谱")
    parser.add_argument("--export", help="导出JSON文件路径")
    parser.add_argument("--search", help="搜索关键词")
    parser.add_argument("--tag", help="按标签搜索")
    parser.add_argument("--keyword", help="按关键词搜索")
    parser.add_argument("--related", help="查找相关条目")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    parser.add_argument("--min-strength", type=float, default=0.1, help="最小关联强度")
    
    args = parser.parse_args()
    
    # 创建知识图谱实例
    kg = KnowledgeGraph(args.path)
    
    if args.build or args.export or args.stats:
        kg.build_graph()
    
    if args.stats:
        stats = kg.get_graph_stats()
        print("\n=== 知识图谱统计 ===")
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    if args.export:
        kg.export_to_json(args.export)
    
    if args.search:
        results = kg.search(args.search)
        print(f"\n=== 搜索结果: '{args.search}' ===")
        print(f"找到 {len(results)} 个结果")
        for r in results[:10]:
            print(f"\n[{r['score']}分] {r['entry']['title']}")
            print(f"  路径: {r['entry']['path']}")
            print(f"  原因: {', '.join(r['reasons'])}")
    
    if args.tag:
        entries = kg.search_by_tag(args.tag)
        print(f"\n=== 标签搜索: #{args.tag} ===")
        print(f"找到 {len(entries)} 个条目")
        for e in entries:
            print(f"- {e.title} ({e.path})")
    
    if args.keyword:
        entries = kg.search_by_keyword(args.keyword)
        print(f"\n=== 关键词搜索: {args.keyword} ===")
        print(f"找到 {len(entries)} 个条目")
        for e in entries:
            print(f"- {e.title} ({e.path})")
    
    if args.related:
        related = kg.find_related_entries(args.related, args.min_strength)
        print(f"\n=== 相关条目: {args.related} ===")
        print(f"找到 {len(related)} 个相关条目")
        for r in related[:10]:
            print(f"\n[强度: {r['relationship']['strength']}] {r['entry']['title']}")
            print(f"  类型: {r['relationship']['relation_type']}")
            print(f"  路径: {r['entry']['path']}")


if __name__ == "__main__":
    main()
