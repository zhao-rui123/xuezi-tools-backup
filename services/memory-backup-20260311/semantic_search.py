#!/usr/bin/env python3
"""
Memory Service - Semantic Search Module
语义搜索模块：为记忆文件生成语义索引并提供搜索功能

功能：
1. 读取记忆文件（memory/*.md）
2. 生成语义索引（关键词+主题）
3. 搜索功能：根据查询返回相关记忆摘要
4. 保存索引到 memory/index/semantic_index.json
"""

import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """记忆条目数据结构"""
    file_path: str
    file_name: str
    date: str
    title: str
    summary: str
    keywords: List[str]
    themes: List[str]
    content_hash: str
    last_modified: float
    importance_score: float = 0.0


@dataclass
class SearchResult:
    """搜索结果数据结构"""
    entry: MemoryEntry
    relevance_score: float
    matched_keywords: List[str]
    matched_themes: List[str]
    excerpt: str


class SemanticSearchService:
    """语义搜索服务主类"""
    
    # 停用词列表
    STOP_WORDS = {
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '这些', '那些', '这个', '那个', '之', '与', '及', '等', '或', '但', '而', '如果', '因为', '所以', '虽然', '然而', '因此', '可以', '需要', '进行', '使用', '通过', '已经', '正在', '开始', '完成', '实现', '创建', '开发', '系统', '功能', '模块', '文件', '项目', '任务', '问题', '解决方案', 'the', 'is', 'and', 'to', 'of', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us'
    }
    
    # 主题关键词映射
    THEME_MAPPINGS = {
        '开发': ['开发', '代码', '程序', '编程', '实现', '构建', '编写', '函数', '类', '模块', '接口', 'API', 'git', 'github', 'commit', 'python', 'javascript', 'java', 'cpp', 'golang', 'rust'],
        '系统': ['系统', '架构', '设计', '配置', '部署', '运维', '监控', '日志', '备份', '恢复', '服务器', 'nginx', 'docker', 'kubernetes', '数据库', 'redis', 'mysql'],
        '项目': ['项目', '任务', '进度', '计划', '里程碑', '交付', '验收', '需求', '分析', '调研', '评估', '测算', '计算', '财务', '投资', '收益', 'IRR', 'NPV', 'ROI'],
        '股票': ['股票', '股市', '行情', '价格', '涨跌', '涨停', '跌停', '均线', 'K线', 'MACD', 'RSI', '成交量', '市值', '财报', '业绩', '盈利', '亏损', '分红', '股息', '中矿资源', '赣锋锂业', '盐湖股份', '盛新锂能', '京东方A', '彩虹股份', '中芯国际'],
        '储能': ['储能', '电池', '电站', '光伏', '风电', '新能源', '电力', '电价', '电费', '容量', '功率', 'kWh', 'MW', 'MWh', '充放电', '循环', '寿命', '锂电池', '钠电池', 'PCS', 'BMS', 'EMS'],
        '技能': ['技能', '技能包', 'skill', '工具', '工具包', '自动化', '脚本', 'CLI', '命令', '工作流', 'workflow', 'agent', '多agent', '智能体'],
        '问题': ['问题', 'bug', '错误', '异常', '故障', '排查', '修复', '解决', '调试', '测试', '验证', '失败', '报错', '警告'],
        '学习': ['学习', '研究', '阅读', '笔记', '总结', '文档', '资料', '书籍', '文章', '视频', '教程', '课程', '知识', '理解', '掌握'],
        '沟通': ['沟通', '会议', '讨论', '交流', '汇报', '反馈', '意见', '建议', '协商', '协调', '联系', '消息', '通知', '邮件', '电话'],
        '生活': ['生活', '健康', '运动', '饮食', '睡眠', '休息', '娱乐', '旅行', '购物', '家庭', '朋友', '社交', '心情', '感受']
    }
    
    def __init__(self, memory_dir: str = None, index_dir: str = None):
        """
        初始化语义搜索服务
        
        Args:
            memory_dir: 记忆文件目录，默认为 workspace/memory
            index_dir: 索引保存目录，默认为 memory/index
        """
        workspace_root = Path(__file__).parent.parent.parent
        self.memory_dir = Path(memory_dir) if memory_dir else workspace_root / 'memory'
        self.index_dir = Path(index_dir) if index_dir else self.memory_dir / 'index'
        self.index_file = self.index_dir / 'semantic_index.json'
        
        # 确保目录存在
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # 内存中的索引缓存
        self._index: Dict[str, MemoryEntry] = {}
        self._keyword_index: Dict[str, List[str]] = defaultdict(list)
        self._theme_index: Dict[str, List[str]] = defaultdict(list)
        
        logger.info(f"SemanticSearchService initialized: memory_dir={self.memory_dir}, index_dir={self.index_dir}")
    
    def _compute_hash(self, content: str) -> str:
        """计算内容哈希值"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _extract_date_from_filename(self, filename: str) -> str:
        """从文件名提取日期"""
        # 匹配 YYYY-MM-DD 格式
        match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
        if match:
            return match.group(1)
        return datetime.now().strftime('%Y-%m-%d')
    
    def _extract_title(self, content: str) -> str:
        """提取标题（第一个 # 标题）"""
        lines = content.split('\n')
        for line in lines[:10]:  # 只检查前10行
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
            if line.startswith('## ') and not line.startswith('## 20'):
                return line[3:].strip()
        return "无标题"
    
    def _extract_summary(self, content: str, max_length: int = 200) -> str:
        """提取内容摘要"""
        # 移除markdown标记
        text = re.sub(r'#+\s*', '', content)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # 移除链接
        text = re.sub(r'\*\*|__|\`|\*', '', text)  # 移除粗体、斜体、代码标记
        text = text.strip()
        
        # 取前N个字符作为摘要
        if len(text) > max_length:
            return text[:max_length] + '...'
        return text
    
    def _extract_keywords(self, content: str, top_n: int = 20) -> List[str]:
        """
        提取关键词
        使用简单TF-IDF-like算法：基于词频和词长
        """
        # 提取中文字符和英文单词
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,8}', content)
        english_words = re.findall(r'[a-zA-Z]{3,20}', content.lower())
        
        all_words = chinese_words + english_words
        
        # 统计词频
        word_freq = defaultdict(int)
        for word in all_words:
            if word.lower() not in self.STOP_WORDS and len(word) >= 2:
                word_freq[word] += 1
        
        # 计算权重：词频 * 词长权重
        word_scores = {}
        for word, freq in word_freq.items():
            length_weight = 1.0 + (len(word) - 2) * 0.1  # 词长权重
            word_scores[word] = freq * length_weight
        
        # 返回Top N关键词
        sorted_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:top_n]]
    
    def _extract_themes(self, content: str, keywords: List[str]) -> List[str]:
        """根据内容提取主题"""
        content_lower = content.lower()
        keyword_set = set(k.lower() for k in keywords)
        
        theme_scores = {}
        for theme, theme_keywords in self.THEME_MAPPINGS.items():
            score = 0
            for tk in theme_keywords:
                tk_lower = tk.lower()
                # 在内容中匹配
                if tk_lower in content_lower:
                    score += 2
                # 在关键词中匹配
                if tk_lower in keyword_set:
                    score += 3
            if score > 0:
                theme_scores[theme] = score
        
        # 按分数排序，返回前3个主题
        sorted_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)
        return [theme for theme, _ in sorted_themes[:3]]
    
    def _calculate_importance(self, content: str, keywords: List[str], themes: List[str]) -> float:
        """计算记忆重要性分数"""
        score = 0.0
        
        # 内容长度权重
        content_length = len(content)
        if content_length > 1000:
            score += 2.0
        elif content_length > 500:
            score += 1.0
        
        # 关键词数量权重
        score += len(keywords) * 0.1
        
        # 主题数量权重
        score += len(themes) * 0.5
        
        # 特殊标记权重
        if 'TODO' in content or '待办' in content:
            score += 1.0
        if '重要' in content or 'urgent' in content.lower():
            score += 1.5
        if '完成' in content or 'done' in content.lower():
            score += 0.5
        
        return min(score, 10.0)  # 最高10分
    
    def _parse_memory_file(self, file_path: Path) -> Optional[MemoryEntry]:
        """解析单个记忆文件"""
        try:
            content = file_path.read_text(encoding='utf-8')
            if not content.strip():
                return None
            
            file_stat = file_path.stat()
            file_name = file_path.name
            date = self._extract_date_from_filename(file_name)
            
            entry = MemoryEntry(
                file_path=str(file_path.relative_to(self.memory_dir)),
                file_name=file_name,
                date=date,
                title=self._extract_title(content),
                summary=self._extract_summary(content),
                keywords=self._extract_keywords(content),
                themes=self._extract_themes(content, []),
                content_hash=self._compute_hash(content),
                last_modified=file_stat.st_mtime,
                importance_score=0.0
            )
            
            # 重新计算主题（基于提取的关键词）
            entry.themes = self._extract_themes(content, entry.keywords)
            entry.importance_score = self._calculate_importance(content, entry.keywords, entry.themes)
            
            return entry
            
        except Exception as e:
            logger.error(f"Error parsing memory file {file_path}: {e}")
            return None
    
    def _build_inverted_index(self):
        """构建倒排索引"""
        self._keyword_index.clear()
        self._theme_index.clear()
        
        for entry_id, entry in self._index.items():
            # 关键词索引
            for keyword in entry.keywords:
                self._keyword_index[keyword.lower()].append(entry_id)
            
            # 主题索引
            for theme in entry.themes:
                self._theme_index[theme].append(entry_id)
    
    def build_index(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """
        构建语义索引
        
        Args:
            force_rebuild: 是否强制重建索引
            
        Returns:
            索引构建统计信息
        """
        logger.info("Building semantic index...")
        
        # 查找所有记忆文件
        memory_files = list(self.memory_dir.glob('*.md'))
        memory_files = [f for f in memory_files if f.name != 'MEMORY.md']  # 排除主记忆文件
        
        logger.info(f"Found {len(memory_files)} memory files")
        
        # 加载现有索引（用于增量更新）
        existing_index = {}
        if not force_rebuild and self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data.get('entries', []):
                        entry = MemoryEntry(**item)
                        existing_index[entry.file_path] = entry
                logger.info(f"Loaded {len(existing_index)} existing index entries")
            except Exception as e:
                logger.warning(f"Failed to load existing index: {e}")
        
        # 解析所有文件
        new_count = 0
        updated_count = 0
        unchanged_count = 0
        
        for file_path in memory_files:
            entry = self._parse_memory_file(file_path)
            if entry:
                entry_id = entry.file_path
                
                # 检查是否需要更新
                if entry_id in existing_index:
                    existing = existing_index[entry_id]
                    if existing.content_hash == entry.content_hash:
                        # 内容未变化，保留原有条目
                        self._index[entry_id] = existing
                        unchanged_count += 1
                    else:
                        # 内容已变化，更新条目
                        self._index[entry_id] = entry
                        updated_count += 1
                else:
                    # 新文件
                    self._index[entry_id] = entry
                    new_count += 1
        
        # 构建倒排索引
        self._build_inverted_index()
        
        # 保存索引
        self._save_index()
        
        stats = {
            'total_files': len(memory_files),
            'new_entries': new_count,
            'updated_entries': updated_count,
            'unchanged_entries': unchanged_count,
            'total_indexed': len(self._index),
            'keywords_indexed': len(self._keyword_index),
            'themes_indexed': len(self._theme_index)
        }
        
        logger.info(f"Index build complete: {stats}")
        return stats
    
    def _save_index(self):
        """保存索引到文件"""
        data = {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'total_entries': len(self._index),
            'entries': [asdict(entry) for entry in self._index.values()]
        }
        
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Index saved to {self.index_file}")
    
    def load_index(self) -> bool:
        """
        从文件加载索引
        
        Returns:
            是否成功加载
        """
        if not self.index_file.exists():
            logger.warning(f"Index file not found: {self.index_file}")
            return False
        
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._index.clear()
            for item in data.get('entries', []):
                entry = MemoryEntry(**item)
                self._index[entry.file_path] = entry
            
            self._build_inverted_index()
            
            logger.info(f"Loaded {len(self._index)} entries from index")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False
    
    def search(self, query: str, limit: int = 10, min_score: float = 0.1) -> List[SearchResult]:
        """
        搜索记忆
        
        Args:
            query: 搜索查询
            limit: 返回结果数量限制
            min_score: 最低相关性分数
            
        Returns:
            搜索结果列表
        """
        if not self._index:
            self.load_index()
        
        if not self._index:
            logger.warning("No index available for search")
            return []
        
        logger.info(f"Searching for: '{query}'")
        
        # 解析查询
        query_lower = query.lower()
        query_keywords = self._extract_keywords(query, top_n=10)
        
        # 计算每个条目的相关性分数
        scored_entries: List[Tuple[str, float, List[str], List[str]]] = []
        
        for entry_id, entry in self._index.items():
            score = 0.0
            matched_keywords = []
            matched_themes = []
            
            # 1. 关键词匹配
            entry_keywords_lower = [k.lower() for k in entry.keywords]
            for qk in query_keywords:
                if qk.lower() in entry_keywords_lower:
                    score += 2.0
                    matched_keywords.append(qk)
                # 模糊匹配（包含关系）
                for ek in entry_keywords_lower:
                    if qk.lower() in ek or ek in qk.lower():
                        score += 0.5
            
            # 2. 主题匹配
            for theme in entry.themes:
                if theme.lower() in query_lower or query_lower in theme.lower():
                    score += 3.0
                    matched_themes.append(theme)
            
            # 3. 标题匹配
            if query_lower in entry.title.lower():
                score += 5.0
            
            # 4. 内容摘要匹配
            if query_lower in entry.summary.lower():
                score += 1.0
            
            # 5. 日期匹配
            if query_lower in entry.date:
                score += 2.0
            
            # 6. 重要性加成
            score *= (1 + entry.importance_score * 0.1)
            
            if score >= min_score:
                scored_entries.append((entry_id, score, matched_keywords, matched_themes))
        
        # 按分数排序
        scored_entries.sort(key=lambda x: x[1], reverse=True)
        
        # 构建结果
        results = []
        for entry_id, score, matched_keywords, matched_themes in scored_entries[:limit]:
            entry = self._index[entry_id]
            
            # 生成摘要片段
            excerpt = self._generate_excerpt(entry.summary, query)
            
            result = SearchResult(
                entry=entry,
                relevance_score=round(score, 2),
                matched_keywords=matched_keywords,
                matched_themes=matched_themes,
                excerpt=excerpt
            )
            results.append(result)
        
        logger.info(f"Found {len(results)} results for query '{query}'")
        return results
    
    def _generate_excerpt(self, content: str, query: str, max_length: int = 150) -> str:
        """生成包含查询词的摘要片段"""
        query_lower = query.lower()
        content_lower = content.lower()
        
        # 查找查询词位置
        pos = content_lower.find(query_lower)
        if pos == -1:
            # 没有找到，返回开头
            return content[:max_length] + ('...' if len(content) > max_length else '')
        
        # 找到位置，提取上下文
        start = max(0, pos - 50)
        end = min(len(content), pos + len(query) + 50)
        
        excerpt = content[start:end]
        if start > 0:
            excerpt = '...' + excerpt
        if end < len(content):
            excerpt = excerpt + '...'
        
        return excerpt
    
    def search_by_theme(self, theme: str, limit: int = 10) -> List[MemoryEntry]:
        """
        按主题搜索记忆
        
        Args:
            theme: 主题名称
            limit: 返回结果数量限制
            
        Returns:
            记忆条目列表
        """
        if not self._index:
            self.load_index()
        
        results = []
        theme_lower = theme.lower()
        
        for entry in self._index.values():
            for t in entry.themes:
                if theme_lower in t.lower() or t.lower() in theme_lower:
                    results.append(entry)
                    break
        
        # 按重要性排序
        results.sort(key=lambda x: x.importance_score, reverse=True)
        return results[:limit]
    
    def search_by_date_range(self, start_date: str, end_date: str) -> List[MemoryEntry]:
        """
        按日期范围搜索记忆
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            记忆条目列表
        """
        if not self._index:
            self.load_index()
        
        results = []
        for entry in self._index.values():
            if start_date <= entry.date <= end_date:
                results.append(entry)
        
        # 按日期排序
        results.sort(key=lambda x: x.date)
        return results
    
    def get_recent_memories(self, days: int = 7, limit: int = 10) -> List[MemoryEntry]:
        """
        获取最近几天的记忆
        
        Args:
            days: 最近天数
            limit: 返回数量限制
            
        Returns:
            记忆条目列表
        """
        if not self._index:
            self.load_index()
        
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - __import__('datetime').timedelta(days=days)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        return self.search_by_date_range(start_str, end_str)[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        if not self._index:
            self.load_index()
        
        if not self._index:
            return {'status': 'empty'}
        
        # 计算主题分布
        theme_counts = defaultdict(int)
        for entry in self._index.values():
            for theme in entry.themes:
                theme_counts[theme] += 1
        
        # 计算日期范围
        dates = [entry.date for entry in self._index.values()]
        
        return {
            'status': 'ready',
            'total_entries': len(self._index),
            'total_keywords': len(self._keyword_index),
            'total_themes': len(self._theme_index),
            'date_range': {
                'earliest': min(dates) if dates else None,
                'latest': max(dates) if dates else None
            },
            'theme_distribution': dict(sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)),
            'avg_importance_score': sum(e.importance_score for e in self._index.values()) / len(self._index)
        }
    
    def format_search_results(self, results: List[SearchResult]) -> str:
        """格式化搜索结果为可读文本"""
        if not results:
            return "未找到相关记忆。"
        
        lines = [f"找到 {len(results)} 条相关记忆：\n"]
        
        for i, result in enumerate(results, 1):
            entry = result.entry
            lines.append(f"{i}. [{entry.date}] {entry.title}")
            lines.append(f"   文件: {entry.file_name}")
            lines.append(f"   相关度: {result.relevance_score}")
            if result.matched_keywords:
                lines.append(f"   匹配关键词: {', '.join(result.matched_keywords[:5])}")
            if result.matched_themes:
                lines.append(f"   主题: {', '.join(result.matched_themes)}")
            lines.append(f"   摘要: {result.excerpt}")
            lines.append("")
        
        return '\n'.join(lines)


# CLI接口
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Semantic Search Service')
    parser.add_argument('--build', action='store_true', help='Build index')
    parser.add_argument('--search', type=str, help='Search query')
    parser.add_argument('--theme', type=str, help='Search by theme')
    parser.add_argument('--recent', type=int, metavar='DAYS', help='Get recent memories')
    parser.add_argument('--stats', action='store_true', help='Show index statistics')
    parser.add_argument('--force', action='store_true', help='Force rebuild index')
    parser.add_argument('--limit', type=int, default=10, help='Result limit')
    
    args = parser.parse_args()
    
    service = SemanticSearchService()
    
    if args.build or args.force:
        stats = service.build_index(force_rebuild=args.force)
        print(f"索引构建完成:")
        print(f"  - 总文件数: {stats['total_files']}")
        print(f"  - 新增条目: {stats['new_entries']}")
        print(f"  - 更新条目: {stats['updated_entries']}")
        print(f"  - 未变更: {stats['unchanged_entries']}")
        print(f"  - 索引总数: {stats['total_indexed']}")
        print(f"  - 关键词数: {stats['keywords_indexed']}")
        print(f"  - 主题数: {stats['themes_indexed']}")
    
    elif args.search:
        results = service.search(args.search, limit=args.limit)
        print(service.format_search_results(results))
    
    elif args.theme:
        entries = service.search_by_theme(args.theme, limit=args.limit)
        print(f"主题 '{args.theme}' 的 {len(entries)} 条记忆：")
        for i, entry in enumerate(entries, 1):
            print(f"{i}. [{entry.date}] {entry.title} (重要性: {entry.importance_score:.1f})")
            print(f"   关键词: {', '.join(entry.keywords[:5])}")
    
    elif args.recent:
        entries = service.get_recent_memories(days=args.recent, limit=args.limit)
        print(f"最近 {args.recent} 天的 {len(entries)} 条记忆：")
        for i, entry in enumerate(entries, 1):
            print(f"{i}. [{entry.date}] {entry.title}")
            print(f"   摘要: {entry.summary[:100]}...")
    
    elif args.stats:
        stats = service.get_stats()
        print("索引统计信息:")
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    else:
        parser.print_help()
