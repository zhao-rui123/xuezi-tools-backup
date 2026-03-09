#!/usr/bin/env python3
"""
Memory QA System - 智能问答系统模块
基于 unified-memory 的记忆智能问答功能

功能：
1. 基于记忆的问答，不用翻找文件
2. 自然语言查询历史信息
3. 自动总结和推理

作者: 雪子助手
版本: 1.0.0
"""

import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import hashlib


@dataclass
class MemoryEntry:
    """记忆条目数据结构"""
    date: str
    content: str
    tags: List[str]
    importance: float  # 0-1
    category: str
    source_file: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QAContext:
    """问答上下文"""
    question: str
    relevant_entries: List[MemoryEntry]
    time_range: Optional[Tuple[str, str]]
    topic: Optional[str]
    confidence: float


class MemoryQA:
    """记忆问答系统主类"""
    
    def __init__(self, memory_dir: str = None):
        """
        初始化问答系统
        
        Args:
            memory_dir: 记忆文件目录，默认为 ~/.openclaw/workspace/memory/
        """
        if memory_dir is None:
            memory_dir = os.path.expanduser("~/.openclaw/workspace/memory/")
        self.memory_dir = Path(memory_dir)
        self.entries_cache: List[MemoryEntry] = []
        self.last_load_time: Optional[datetime] = None
        self.cache_ttl = 300  # 缓存5分钟
        
        # 关键词分类词典
        self.keyword_categories = {
            "project": ["项目", "开发", "完成", "部署", "系统", "功能", "模块"],
            "decision": ["决定", "决策", "选择", "确定", "方案", "策略"],
            "task": ["任务", "待办", "TODO", "计划", "安排", "工作"],
            "meeting": ["会议", "讨论", "沟通", "交流", "汇报"],
            "learning": ["学习", "研究", "分析", "了解", "掌握"],
            "issue": ["问题", "bug", "错误", "故障", "修复", "解决"],
            "stock": ["股票", "股市", "行情", "分析", "投资", "持仓"],
            "skill": ["技能包", "skill", "工具", "脚本", "功能包"],
            "backup": ["备份", "归档", "保存", "恢复"],
        }
        
        # 时间关键词映射
        self.time_keywords = {
            "今天": 0,
            "昨天": 1,
            "前天": 2,
            "最近": 7,
            "本周": 7,
            "上周": 14,
            "本月": 30,
            "上个月": 60,
            "今年": 365,
        }
    
    def _load_all_entries(self, force_reload: bool = False) -> List[MemoryEntry]:
        """加载所有记忆条目"""
        if not force_reload and self.entries_cache and self.last_load_time:
            if (datetime.now() - self.last_load_time).seconds < self.cache_ttl:
                return self.entries_cache
        
        entries = []
        if not self.memory_dir.exists():
            return entries
        
        for file_path in sorted(self.memory_dir.glob("*.md")):
            try:
                entries.extend(self._parse_memory_file(file_path))
            except Exception as e:
                print(f"解析文件失败 {file_path}: {e}")
        
        # 按日期排序（最新的在前）
        entries.sort(key=lambda x: x.date, reverse=True)
        
        self.entries_cache = entries
        self.last_load_time = datetime.now()
        return entries
    
    def _parse_memory_file(self, file_path: Path) -> List[MemoryEntry]:
        """解析单个记忆文件"""
        entries = []
        content = file_path.read_text(encoding='utf-8')
        
        # 提取日期（从文件名）
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_path.name)
        if not date_match:
            return entries
        
        date = date_match.group(1)
        
        # 解析内容块
        sections = re.split(r'\n##+\s+', content)
        
        for section in sections:
            if not section.strip():
                continue
            
            # 提取标题（第一行）
            lines = section.strip().split('\n')
            title = lines[0].strip() if lines else "未分类"
            section_content = '\n'.join(lines[1:]) if len(lines) > 1 else ""
            
            # 检测标签
            tags = self._extract_tags(section_content)
            
            # 检测分类
            category = self._detect_category(title + section_content)
            
            # 计算重要性
            importance = self._calculate_importance(section_content, tags)
            
            entry = MemoryEntry(
                date=date,
                content=f"{title}\n{section_content}",
                tags=tags,
                importance=importance,
                category=category,
                source_file=str(file_path)
            )
            entries.append(entry)
        
        return entries
    
    def _extract_tags(self, content: str) -> List[str]:
        """从内容中提取标签"""
        tags = []
        
        # 查找 [TAG] 格式
        tag_pattern = r'\[([^\]]+)\]|【([^】]+)】|#(\w+)'
        matches = re.findall(tag_pattern, content)
        for match in matches:
            tag = next((m for m in match if m), None)
            if tag:
                tags.append(tag.strip())
        
        # 查找关键词标记
        keyword_tags = {
            "[DECISION]": "决策",
            "[TODO]": "待办",
            "[IMPORTANT]": "重要",
            "[BUG]": "问题",
            "[FIXED]": "已修复",
            "✅": "已完成",
            "❌": "失败",
            "📝": "记录",
        }
        
        for marker, tag in keyword_tags.items():
            if marker in content:
                tags.append(tag)
        
        return list(set(tags))
    
    def _detect_category(self, content: str) -> str:
        """检测内容分类"""
        category_scores = defaultdict(int)
        
        for category, keywords in self.keyword_categories.items():
            for keyword in keywords:
                if keyword in content:
                    category_scores[category] += 1
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        return "general"
    
    def _calculate_importance(self, content: str, tags: List[str]) -> float:
        """计算内容重要性（0-1）"""
        score = 0.5  # 基础分
        
        # 标签权重
        important_tags = ["决策", "重要", "DECISION", "关键", "战略"]
        for tag in tags:
            if any(it in tag for it in important_tags):
                score += 0.2
        
        # 关键词权重
        important_keywords = [
            "完成", "部署", "上线", "发布", "里程碑",
            "决定", "选择", "方案", "架构", "设计",
            "重要", "关键", "核心", "主要"
        ]
        for keyword in important_keywords:
            if keyword in content:
                score += 0.05
        
        # 长度权重（适中为佳）
        content_length = len(content)
        if 200 < content_length < 2000:
            score += 0.1
        
        return min(1.0, score)
    
    def _extract_time_range(self, question: str) -> Optional[Tuple[str, str]]:
        """从问题中提取时间范围"""
        today = datetime.now()
        
        # 检查相对时间关键词
        for keyword, days in self.time_keywords.items():
            if keyword in question:
                end_date = today.strftime("%Y-%m-%d")
                start_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
                return (start_date, end_date)
        
        # 检查具体日期格式
        date_pattern = r'(\d{4}-\d{2}-\d{2})'
        dates = re.findall(date_pattern, question)
        if len(dates) >= 2:
            return (dates[0], dates[1])
        elif len(dates) == 1:
            return (dates[0], dates[0])
        
        return None
    
    def _extract_topic(self, question: str) -> Optional[str]:
        """从问题中提取主题"""
        # 去除疑问词和常见词汇
        stop_words = ["什么", "哪些", "怎么", "如何", "为什么", "吗", "呢", "了",
                     "我", "你", "他", "她", "它", "我们", "你们", "他们",
                     "的", "是", "在", "有", "和", "与", "或", "关于", "最近"]
        
        words = question
        for stop in stop_words:
            words = words.replace(stop, " ")
        
        # 提取关键词
        keywords = [w.strip() for w in words.split() if len(w.strip()) > 1]
        
        if keywords:
            return keywords[0]  # 返回第一个关键词作为主题
        return None
    
    def _calculate_relevance(self, entry: MemoryEntry, question: str, 
                            topic: Optional[str]) -> float:
        """计算条目与问题的相关度"""
        score = 0.0
        question_lower = question.lower()
        content_lower = entry.content.lower()
        
        # 直接匹配得分
        if topic and topic.lower() in content_lower:
            score += 0.4
        
        # 关键词匹配
        question_words = set(question_lower.split())
        content_words = set(content_lower.split())
        common_words = question_words & content_words
        
        if question_words:
            score += len(common_words) / len(question_words) * 0.3
        
        # 分类匹配
        for category, keywords in self.keyword_categories.items():
            if any(kw in question for kw in keywords):
                if entry.category == category:
                    score += 0.2
        
        # 标签匹配
        for tag in entry.tags:
            if tag.lower() in question_lower:
                score += 0.1
        
        # 时间衰减（越新越重要）
        try:
            entry_date = datetime.strptime(entry.date, "%Y-%m-%d")
            days_ago = (datetime.now() - entry_date).days
            time_decay = max(0, 1 - days_ago / 365)  # 一年内线性衰减
            score += time_decay * 0.1
        except:
            pass
        
        return min(1.0, score)
    
    def answer(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """
        回答用户问题
        
        Args:
            question: 用户问题
            top_k: 返回最多相关条目数
            
        Returns:
            包含答案和相关信息的字典
        """
        entries = self._load_all_entries()
        
        if not entries:
            return {
                "answer": "暂时没有找到相关记忆。",
                "confidence": 0.0,
                "sources": [],
                "suggestions": ["您可以先创建一些记忆文件。"]
            }
        
        # 提取时间和主题
        time_range = self._extract_time_range(question)
        topic = self._extract_topic(question)
        
        # 过滤时间范围
        filtered_entries = entries
        if time_range:
            start, end = time_range
            filtered_entries = [
                e for e in entries 
                if start <= e.date <= end
            ]
        
        # 计算相关度并排序
        scored_entries = []
        for entry in filtered_entries:
            relevance = self._calculate_relevance(entry, question, topic)
            # 最终得分 = 相关度 × 重要性
            final_score = relevance * (0.5 + 0.5 * entry.importance)
            scored_entries.append((entry, final_score))
        
        # 按得分排序
        scored_entries.sort(key=lambda x: x[1], reverse=True)
        
        # 获取最相关的条目
        relevant_entries = [
            entry for entry, score in scored_entries[:top_k] 
            if score > 0.1  # 阈值过滤
        ]
        
        if not relevant_entries:
            return {
                "answer": f"没有找到关于「{question}」的相关记忆。",
                "confidence": 0.0,
                "sources": [],
                "suggestions": [
                    f"尝试搜索其他关键词如：{', '.join(self.keyword_categories.keys())}",
                    "检查记忆文件是否存在",
                    "尝试使用更具体的时间范围"
                ]
            }
        
        # 生成答案
        context = QAContext(
            question=question,
            relevant_entries=relevant_entries,
            time_range=time_range,
            topic=topic,
            confidence=scored_entries[0][1] if scored_entries else 0
        )
        
        answer_text = self._generate_answer(context)
        
        return {
            "answer": answer_text,
            "confidence": context.confidence,
            "sources": [
                {
                    "date": e.date,
                    "category": e.category,
                    "tags": e.tags,
                    "importance": e.importance,
                    "preview": e.content[:200] + "..." if len(e.content) > 200 else e.content
                }
                for e in relevant_entries
            ],
            "time_range": time_range,
            "topic": topic
        }
    
    def _generate_answer(self, context: QAContext) -> str:
        """生成自然语言答案"""
        entries = context.relevant_entries
        
        if not entries:
            return "没有找到相关信息。"
        
        # 按日期分组
        by_date = defaultdict(list)
        for entry in entries:
            by_date[entry.date].append(entry)
        
        # 构建答案
        parts = []
        
        # 开头
        if context.topic:
            parts.append(f"关于「{context.topic}」，")
        
        # 时间范围说明
        if context.time_range:
            start, end = context.time_range
            if start == end:
                parts.append(f"在 {start} 的记录中：")
            else:
                parts.append(f"从 {start} 到 {end} 期间：")
        
        # 汇总信息
        total_entries = len(entries)
        categories = set(e.category for e in entries)
        
        parts.append(f"\n共找到 {total_entries} 条相关记忆")
        if len(categories) > 1:
            parts.append(f"，涉及 {', '.join(categories)} 等类别。")
        else:
            parts.append("。")
        
        # 详细内容（按时间倒序）
        parts.append("\n📋 **相关内容摘要：**\n")
        
        for date in sorted(by_date.keys(), reverse=True)[:3]:  # 最多显示3天
            day_entries = by_date[date]
            parts.append(f"\n**{date}** ({len(day_entries)}条)")
            
            for entry in day_entries[:3]:  # 每天最多3条
                # 提取标题（第一行）
                lines = entry.content.strip().split('\n')
                title = lines[0][:50]  # 限制长度
                
                # 提取要点
                key_points = self._extract_key_points(entry.content)
                
                parts.append(f"  • {title}")
                if key_points:
                    parts.append(f"    - {key_points[0]}")
        
        return '\n'.join(parts)
    
    def _extract_key_points(self, content: str) -> List[str]:
        """从内容中提取关键要点"""
        points = []
        
        # 查找列表项
        list_pattern = r'^[\s]*[-•\*][\s]+(.+)$'
        matches = re.findall(list_pattern, content, re.MULTILINE)
        points.extend(matches[:2])  # 最多2个
        
        # 查找完成标记
        done_pattern = r'[✅✔️√] *(.+?)(?:\n|$)'
        done_matches = re.findall(done_pattern, content)
        for match in done_matches[:2]:
            points.append(f"✓ {match.strip()}")
        
        # 查找重要句子
        important_pattern = r'(?:重要|关键|决定|完成).*?[。！]'
        important_matches = re.findall(important_pattern, content)
        if important_matches and not points:
            points.append(important_matches[0])
        
        return points
    
    def summarize_period(self, start: str, end: str, 
                         focus: str = None) -> Dict[str, Any]:
        """
        总结指定时间段的记忆
        
        Args:
            start: 开始日期 (YYYY-MM-DD)
            end: 结束日期 (YYYY-MM-DD)
            focus: 可选的关注主题
            
        Returns:
            总结结果字典
        """
        entries = self._load_all_entries()
        
        # 过滤时间范围
        period_entries = [
            e for e in entries
            if start <= e.date <= end
        ]
        
        if not period_entries:
            return {
                "summary": f"在 {start} 到 {end} 期间没有找到记忆。",
                "period": (start, end),
                "stats": {},
                "highlights": []
            }
        
        # 统计分析
        stats = {
            "total_entries": len(period_entries),
            "days_covered": len(set(e.date for e in period_entries)),
            "categories": {},
            "tags": defaultdict(int),
            "avg_importance": sum(e.importance for e in period_entries) / len(period_entries)
        }
        
        for entry in period_entries:
            # 分类统计
            stats["categories"][entry.category] = stats["categories"].get(entry.category, 0) + 1
            # 标签统计
            for tag in entry.tags:
                stats["tags"][tag] += 1
        
        # 提取亮点（高重要性条目）
        highlights = [
            e for e in period_entries 
            if e.importance > 0.7
        ]
        highlights.sort(key=lambda x: x.importance, reverse=True)
        
        # 主题聚焦
        if focus:
            focus_entries = [
                e for e in period_entries
                if focus.lower() in e.content.lower()
            ]
        else:
            focus_entries = period_entries
        
        # 生成总结文本
        summary_parts = [f"📅 **{start} 至 {end} 期间总结**\n"]
        summary_parts.append(f"共记录 {stats['total_entries']} 条记忆，跨越 {stats['days_covered']} 天。\n")
        
        # 主要类别
        if stats["categories"]:
            summary_parts.append("\n📊 **主要活动类别：**")
            for cat, count in sorted(stats["categories"].items(), key=lambda x: -x[1])[:5]:
                cat_emoji = {
                    "project": "🚀", "decision": "🎯", "task": "📋",
                    "meeting": "🗣️", "learning": "📚", "issue": "🐛",
                    "stock": "📈", "skill": "🛠️", "backup": "💾",
                    "general": "📝"
                }.get(cat, "📄")
                summary_parts.append(f"  {cat_emoji} {cat}: {count}条")
        
        # 重要亮点
        if highlights:
            summary_parts.append("\n⭐ **重要亮点：**")
            for h in highlights[:5]:
                title = h.content.strip().split('\n')[0][:40]
                summary_parts.append(f"  • [{h.date}] {title}")
        
        # 高频标签
        if stats["tags"]:
            top_tags = sorted(stats["tags"].items(), key=lambda x: -x[1])[:5]
            summary_parts.append(f"\n🏷️ **常见标签：**{', '.join([t[0] for t in top_tags])}")
        
        return {
            "summary": '\n'.join(summary_parts),
            "period": (start, end),
            "stats": dict(stats),
            "highlights": [h.to_dict() for h in highlights[:10]],
            "focus_entries": [e.to_dict() for e in focus_entries[:10]] if focus else []
        }
    
    def find_related(self, topic: str, limit: int = 10) -> Dict[str, Any]:
        """
        查找与主题相关的内容
        
        Args:
            topic: 搜索主题
            limit: 返回结果数量限制
            
        Returns:
            相关结果字典
        """
        entries = self._load_all_entries()
        
        # 计算每个条目的相关度
        scored = []
        for entry in entries:
            score = self._calculate_relevance(entry, topic, topic)
            if score > 0.1:  # 阈值
                scored.append((entry, score))
        
        # 排序并限制数量
        scored.sort(key=lambda x: x[1], reverse=True)
        related = scored[:limit]
        
        if not related:
            return {
                "topic": topic,
                "related_entries": [],
                "suggestions": ["尝试使用其他关键词", "检查拼写是否正确"],
                "timeline": []
            }
        
        # 构建时间线
        timeline = []
        for entry, score in related:
            title = entry.content.strip().split('\n')[0][:50]
            timeline.append({
                "date": entry.date,
                "title": title,
                "relevance": round(score, 2),
                "category": entry.category
            })
        
        # 按日期排序
        timeline.sort(key=lambda x: x["date"])
        
        # 相关主题建议
        all_categories = set(e.category for e, _ in related)
        related_topics = []
        for cat in all_categories:
            if cat != "general":
                related_topics.append(cat)
        
        return {
            "topic": topic,
            "related_entries": [
                {
                    "date": e.date,
                    "content": e.content[:300] + "..." if len(e.content) > 300 else e.content,
                    "relevance": round(s, 2),
                    "category": e.category,
                    "tags": e.tags
                }
                for e, s in related
            ],
            "timeline": timeline,
            "suggestions": [
                f"您可能还想了解：{', '.join(related_topics[:3])}"
            ] if related_topics else []
        }
    
    def generate_context_aware_response(self, 
                                       current_query: str,
                                       conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        生成上下文感知回复
        
        Args:
            current_query: 当前查询
            conversation_history: 对话历史（可选）
            
        Returns:
            上下文感知回复
        """
        if conversation_history is None:
            conversation_history = []
        
        # 分析当前查询
        current_answer = self.answer(current_query)
        
        # 提取当前主题
        current_topic = current_answer.get("topic")
        current_time_range = current_answer.get("time_range")
        
        # 检查历史对话中的上下文
        context_clues = []
        for msg in conversation_history[-3:]:  # 最近3条
            if msg.get("role") == "user":
                # 从历史问题中提取可能的主题
                prev_topic = self._extract_topic(msg.get("content", ""))
                if prev_topic and prev_topic != current_topic:
                    context_clues.append(prev_topic)
        
        # 如果有上下文线索，进行关联搜索
        related_context = []
        if context_clues:
            for clue in context_clues[:2]:
                related = self.find_related(clue, limit=3)
                if related["related_entries"]:
                    related_context.append({
                        "from_topic": clue,
                        "entries": related["related_entries"][:2]
                    })
        
        # 生成上下文增强的答案
        response_parts = [current_answer["answer"]]
        
        if related_context and current_answer["confidence"] < 0.5:
            response_parts.append("\n\n💡 **根据之前的对话，您可能还关心：**")
            for ctx in related_context:
                response_parts.append(f"\n与「{ctx['from_topic']}」相关的信息：")
                for entry in ctx["entries"][:2]:
                    title = entry["content"].split('\n')[0][:40]
                    response_parts.append(f"  • [{entry['date']}] {title}")
        
        # 智能建议
        suggestions = current_answer.get("suggestions", [])
        
        # 基于上下文的额外建议
        if current_topic:
            suggestions.append(f"搜索更多「{current_topic}」相关内容")
        if current_time_range:
            start, end = current_time_range
            suggestions.append(f"查看 {start} 至 {end} 的完整总结")
        
        return {
            "response": '\n'.join(response_parts),
            "current_answer": current_answer,
            "context_used": len(related_context) > 0,
            "related_topics": context_clues,
            "suggestions": list(set(suggestions))[:4],  # 去重并限制
            "confidence": current_answer["confidence"]
        }


# ============== 命令行接口 ==============

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Memory QA System - 智能问答系统")
    parser.add_argument("--memory-dir", help="记忆文件目录")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # answer 命令
    answer_parser = subparsers.add_parser("answer", help="回答用户问题")
    answer_parser.add_argument("question", help="问题内容")
    answer_parser.add_argument("-k", "--top-k", type=int, default=5, help="返回结果数量")
    answer_parser.add_argument("--json", action="store_true", help="输出JSON格式")
    
    # summarize 命令
    sum_parser = subparsers.add_parser("summarize", help="总结时间段")
    sum_parser.add_argument("start", help="开始日期 (YYYY-MM-DD)")
    sum_parser.add_argument("end", help="结束日期 (YYYY-MM-DD)")
    sum_parser.add_argument("--focus", help="关注主题")
    sum_parser.add_argument("--json", action="store_true", help="输出JSON格式")
    
    # find 命令
    find_parser = subparsers.add_parser("find", help="查找相关内容")
    find_parser.add_argument("topic", help="搜索主题")
    find_parser.add_argument("-l", "--limit", type=int, default=10, help="结果数量限制")
    find_parser.add_argument("--json", action="store_true", help="输出JSON格式")
    
    # context 命令
    ctx_parser = subparsers.add_parser("context", help="上下文感知回复")
    ctx_parser.add_argument("query", help="当前查询")
    ctx_parser.add_argument("--json", action="store_true", help="输出JSON格式")
    
    args = parser.parse_args()
    
    # 初始化系统
    qa = MemoryQA(memory_dir=args.memory_dir)
    
    if args.command == "answer":
        result = qa.answer(args.question, top_k=args.top_k)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result["answer"])
            print(f"\n置信度: {result['confidence']:.2f}")
            if result["sources"]:
                print(f"来源: {len(result['sources'])}条记忆")
    
    elif args.command == "summarize":
        result = qa.summarize_period(args.start, args.end, args.focus)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result["summary"])
    
    elif args.command == "find":
        result = qa.find_related(args.topic, limit=args.limit)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"📌 主题：{result['topic']}\n")
            print("📅 时间线：")
            for item in result["timeline"]:
                print(f"  [{item['date']}] {item['title']} (相关度: {item['relevance']})")
            if result["suggestions"]:
                print(f"\n💡 建议：{', '.join(result['suggestions'])}")
    
    elif args.command == "context":
        result = qa.generate_context_aware_response(args.query)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result["response"])
            if result["suggestions"]:
                print(f"\n💡 建议：")
                for s in result["suggestions"]:
                    print(f"  • {s}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
