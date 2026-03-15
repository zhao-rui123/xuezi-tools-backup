#!/usr/bin/env python3
"""
Memory Suite v3.0 - 推荐系统模块 (Recommender)

功能：
1. 基于用户画像推荐相关记忆
2. 推荐待办事项
3. 推荐相关技能包
4. 生成个性化推荐报告

作者: Memory Suite Team
版本: 3.0.0
日期: 2026-03-11
"""

import json
import logging
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set

# 导入核心层工具
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from core import (
    setup_logger, expand_path, load_json, save_json,
    format_datetime, get_date_string, ConfigManager,
    MemorySuiteError, safe_execute, truncate_text
)


# ============================================================================
# 数据类定义
# ============================================================================

@dataclass
class Recommendation:
    """推荐项数据类"""
    type: str           # 推荐类型: memory, todo, skill, topic, action
    title: str          # 推荐标题
    description: str    # 推荐描述
    priority: str       # 优先级: high, medium, low
    source: str         # 来源
    confidence: float   # 置信度 (0-1)
    action: Optional[str] = None    # 建议操作
    metadata: Optional[Dict] = None # 附加元数据
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Recommendation':
        """从字典创建"""
        return cls(**data)


# ============================================================================
# 推荐系统主类
# ============================================================================

class Recommender:
    """
    智能推荐系统
    
    基于用户画像、历史记忆、当前上下文生成个性化推荐。
    """
    
    # 推荐类型
    TYPE_MEMORY = "memory"
    TYPE_TODO = "todo"
    TYPE_SKILL = "skill"
    TYPE_TOPIC = "topic"
    TYPE_ACTION = "action"
    TYPE_ALERT = "alert"
    
    # 优先级
    PRIORITY_HIGH = "high"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_LOW = "low"
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化推荐系统
        
        Args:
            config: 配置字典，None 则自动加载
        """
        self.logger = setup_logger("memory_suite.recommender")
        self.logger.info("初始化推荐系统...")
        
        # 加载配置
        if config is None:
            config_manager = ConfigManager()
            config = config_manager.load_config() or {}
        self.config = config
        
        # 路径设置
        self.workspace = expand_path(config.get('workspace', '~/.openclaw/workspace'))
        self.memory_dir = expand_path(config.get('memory_dir', '~/.openclaw/workspace/memory'))
        self.index_dir = self.memory_dir / 'index'
        
        # 用户画像路径
        self.profile_file = self.memory_dir / 'user_profile.json'
        
        # 内部状态
        self._profile: Optional[Dict] = None
        self._index: Optional[Dict] = None
        self._recommendations: List[Recommendation] = []
        
        self.logger.info("推荐系统初始化完成")
    
    # ========================================================================
    # 数据加载
    # ========================================================================
    
    def _load_profile(self) -> Optional[Dict]:
        """加载用户画像"""
        if self._profile is not None:
            return self._profile
        
        self._profile = load_json(self.profile_file)
        if self._profile:
            self.logger.debug(f"用户画像加载成功: {self.profile_file}")
        else:
            self.logger.warning("用户画像不存在或加载失败")
        
        return self._profile
    
    def _load_index(self) -> Optional[Dict]:
        """加载语义索引"""
        if self._index is not None:
            return self._index
        
        index_file = self.index_dir / 'semantic_index.json'
        self._index = load_json(index_file)
        
        if self._index:
            self.logger.debug(f"语义索引加载成功: {index_file}")
        else:
            self.logger.warning("语义索引不存在，将使用基础推荐")
        
        return self._index
    
    def _load_recent_memories(self, days: int = 7) -> List[Dict]:
        """
        加载近期记忆
        
        Args:
            days: 加载最近几天的记忆
            
        Returns:
            记忆列表
        """
        memories = []
        today = datetime.now()
        
        for i in range(days):
            date_str = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            memory_file = self.memory_dir / f'{date_str}.md'
            
            if memory_file.exists():
                try:
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    memories.append({
                        'date': date_str,
                        'file': str(memory_file),
                        'content': content,
                        'size': len(content)
                    })
                except Exception as e:
                    self.logger.warning(f"读取记忆文件失败 {memory_file}: {e}")
        
        self.logger.debug(f"加载了 {len(memories)} 天的记忆")
        return memories
    
    # ========================================================================
    # 记忆推荐
    # ========================================================================
    
    def recommend_memories(self, context: str = "", limit: int = 5) -> List[Recommendation]:
        """
        基于上下文推荐相关记忆
        
        Args:
            context: 当前上下文/查询
            limit: 返回数量限制
            
        Returns:
            记忆推荐列表
        """
        self.logger.info(f"生成记忆推荐 (context={bool(context)}, limit={limit})")
        recommendations = []
        
        # 加载必要数据
        profile = self._load_profile()
        index = self._load_index()
        memories = self._load_recent_memories(days=30)
        
        # 1. 基于话题偏好推荐
        if profile and profile.get('topic_preferences'):
            topic_recs = self._recommend_by_topics(profile['topic_preferences'], memories)
            recommendations.extend(topic_recs)
        
        # 2. 基于当前上下文推荐
        if context:
            context_recs = self._recommend_by_context(context, memories, index)
            recommendations.extend(context_recs)
        
        # 3. 基于时间相关性推荐（今天/昨天的重要记忆）
        time_recs = self._recommend_by_time(memories)
        recommendations.extend(time_recs)
        
        # 去重并排序
        recommendations = self._deduplicate_recommendations(recommendations)
        recommendations = self._sort_by_priority(recommendations)
        
        self.logger.info(f"生成 {len(recommendations[:limit])} 条记忆推荐")
        return recommendations[:limit]
    
    def _recommend_by_topics(self, topic_preferences: Dict[str, float], 
                             memories: List[Dict]) -> List[Recommendation]:
        """基于话题偏好推荐"""
        recommendations = []
        
        # 获取 Top 5 话题
        top_topics = sorted(topic_preferences.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for topic, weight in top_topics:
            # 在记忆中查找相关话题
            related_memories = []
            for mem in memories:
                if topic in mem['content']:
                    related_memories.append(mem)
            
            if related_memories:
                # 提取相关片段
                snippets = self._extract_snippets(related_memories[0]['content'], topic)
                
                rec = Recommendation(
                    type=self.TYPE_MEMORY,
                    title=f"相关话题: {topic}",
                    description=f"找到 {len(related_memories)} 条相关记忆" + 
                               (f" | {snippets[0][:80]}..." if snippets else ""),
                    priority=self.PRIORITY_MEDIUM if weight > 0.3 else self.PRIORITY_LOW,
                    source="topic_preference",
                    confidence=round(weight, 2),
                    action=f"查看 {related_memories[0]['date']} 的记忆",
                    metadata={
                        'topic': topic,
                        'memory_count': len(related_memories),
                        'dates': [m['date'] for m in related_memories[:3]]
                    }
                )
                recommendations.append(rec)
        
        return recommendations
    
    def _recommend_by_context(self, context: str, memories: List[Dict],
                              index: Optional[Dict]) -> List[Recommendation]:
        """基于上下文推荐"""
        recommendations = []
        
        # 提取上下文关键词
        keywords = self._extract_keywords(context)
        
        for keyword in keywords[:5]:  # 限制关键词数量
            matching_memories = []
            
            for mem in memories:
                if keyword.lower() in mem['content'].lower():
                    matching_memories.append(mem)
            
            if matching_memories:
                snippets = self._extract_snippets(matching_memories[0]['content'], keyword)
                
                rec = Recommendation(
                    type=self.TYPE_MEMORY,
                    title=f"相关内容: {keyword}",
                    description=f"在 {matching_memories[0]['date']} 的记忆中找到相关内容" +
                               (f" | {snippets[0][:80]}..." if snippets else ""),
                    priority=self.PRIORITY_HIGH,
                    source="context_match",
                    confidence=0.8,
                    action=f"查看相关记忆: {matching_memories[0]['date']}",
                    metadata={
                        'keyword': keyword,
                        'memory_count': len(matching_memories),
                        'dates': [m['date'] for m in matching_memories[:3]]
                    }
                )
                recommendations.append(rec)
        
        return recommendations
    
    def _recommend_by_time(self, memories: List[Dict]) -> List[Recommendation]:
        """基于时间相关性推荐"""
        recommendations = []
        
        if not memories:
            return recommendations
        
        # 推荐昨天的记忆（如果有）
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        yesterday_memories = [m for m in memories if m['date'] == yesterday]
        
        if yesterday_memories:
            # 提取重要内容（标题、项目等）
            important_sections = self._extract_important_sections(yesterday_memories[0]['content'])
            
            if important_sections:
                rec = Recommendation(
                    type=self.TYPE_MEMORY,
                    title=f"昨日回顾: {yesterday}",
                    description=f"昨天记录了 {len(important_sections)} 项重要内容" +
                               f" | {important_sections[0][:80]}...",
                    priority=self.PRIORITY_MEDIUM,
                    source="time_based",
                    confidence=0.7,
                    action=f"查看昨日完整记忆",
                    metadata={
                        'date': yesterday,
                        'sections': important_sections[:3]
                    }
                )
                recommendations.append(rec)
        
        return recommendations
    
    # ========================================================================
    # 待办推荐
    # ========================================================================
    
    def recommend_todos(self, limit: int = 5) -> List[Recommendation]:
        """
        推荐待办事项
        
        Args:
            limit: 返回数量限制
            
        Returns:
            待办推荐列表
        """
        self.logger.info(f"扫描待办事项 (limit={limit})")
        recommendations = []
        
        # 扫描最近记忆文件中的 TODO
        memories = self._load_recent_memories(days=14)
        pending_todos = []
        
        for mem in memories:
            todos = self._extract_todos(mem['content'])
            for todo in todos:
                pending_todos.append({
                    'task': todo['task'],
                    'date': mem['date'],
                    'important': todo.get('important', False),
                    'urgent': todo.get('urgent', False)
                })
        
        # 按重要性和紧急性排序
        pending_todos.sort(key=lambda x: (not x['important'], not x['urgent'], x['date']))
        
        # 生成推荐
        for todo in pending_todos[:limit]:
            priority = self.PRIORITY_HIGH if todo['important'] or todo['urgent'] else self.PRIORITY_MEDIUM
            
            rec = Recommendation(
                type=self.TYPE_TODO,
                title=f"待办: {truncate_text(todo['task'], 50)}",
                description=f"记录于 {todo['date']}" +
                           (" | 🔴 重要" if todo['important'] else "") +
                           (" | ⚡ 紧急" if todo['urgent'] else ""),
                priority=priority,
                source="pending_task",
                confidence=0.9,
                action="标记完成" if not todo['important'] else "优先处理",
                metadata={
                    'task': todo['task'],
                    'date': todo['date'],
                    'important': todo['important'],
                    'urgent': todo['urgent']
                }
            )
            recommendations.append(rec)
        
        self.logger.info(f"找到 {len(recommendations)} 条待办推荐")
        return recommendations
    
    def _extract_todos(self, content: str) -> List[Dict]:
        """从内容中提取待办事项"""
        todos = []
        
        # 匹配 TODO 部分
        todo_section = re.search(r'\[TODO\](.*?)(?=\n\[|\Z)', content, re.DOTALL | re.IGNORECASE)
        if todo_section:
            todo_text = todo_section.group(1)
            
            # 匹配未完成的待办项
            pending_pattern = r'- \[ \] (.+)'
            for match in re.finditer(pending_pattern, todo_text):
                task = match.group(1).strip()
                todos.append({
                    'task': task,
                    'important': any(kw in task for kw in ['重要', '紧急', '优先', '必须', '关键']),
                    'urgent': any(kw in task for kw in ['紧急', '立即', '今天', '马上'])
                })
        
        # 也检查内联 TODO
        inline_todos = re.findall(r'TODO[:：]\s*(.+?)(?=\n|$)', content, re.IGNORECASE)
        for task in inline_todos:
            todos.append({
                'task': task.strip(),
                'important': False,
                'urgent': False
            })
        
        return todos
    
    # ========================================================================
    # 技能推荐
    # ========================================================================
    
    def recommend_skills(self, context: str = "", limit: int = 5) -> List[Recommendation]:
        """
        推荐相关技能包
        
        Args:
            context: 当前上下文
            limit: 返回数量限制
            
        Returns:
            技能推荐列表
        """
        self.logger.info(f"生成技能推荐 (context={bool(context)}, limit={limit})")
        recommendations = []
        
        # 加载用户画像
        profile = self._load_profile()
        
        # 1. 基于话题偏好推荐技能
        if profile and profile.get('topic_preferences'):
            topic_recs = self._recommend_skills_by_topics(profile['topic_preferences'])
            recommendations.extend(topic_recs)
        
        # 2. 基于上下文推荐技能
        if context:
            context_recs = self._recommend_skills_by_context(context)
            recommendations.extend(context_recs)
        
        # 3. 基于项目需求推荐技能
        project_recs = self._recommend_skills_by_projects()
        recommendations.extend(project_recs)
        
        # 去重并排序
        recommendations = self._deduplicate_recommendations(recommendations, key='title')
        recommendations = self._sort_by_priority(recommendations)
        
        self.logger.info(f"生成 {len(recommendations[:limit])} 条技能推荐")
        return recommendations[:limit]
    
    def _recommend_skills_by_topics(self, topic_preferences: Dict[str, float]) -> List[Recommendation]:
        """基于话题偏好推荐技能"""
        recommendations = []
        
        # 话题到技能的映射
        topic_skill_map = {
            '储能': ['storage-calc', 'electricity-price-crawler', 'project-finance-model'],
            '股票': ['stock-screener', 'stock-analysis-suite', 'tushare-stock-datasource'],
            '开发': ['multi-agent-cn', 'agent-team-orchestration', 'skill-creator'],
            'AI/模型': ['model-switching', 'context-management'],
            '运维': ['system-backup', 'system-maintenance', 'monitoring-alert'],
            '数据分析': ['data-processor', 'chart-generator', 'office-pro'],
        }
        
        for topic, weight in topic_preferences.items():
            if topic in topic_skill_map and weight > 0.2:
                for skill in topic_skill_map[topic]:
                    rec = Recommendation(
                        type=self.TYPE_SKILL,
                        title=f"推荐技能: {skill}",
                        description=f"基于您对'{topic}'的兴趣推荐此技能包",
                        priority=self.PRIORITY_MEDIUM if weight > 0.3 else self.PRIORITY_LOW,
                        source="topic_preference",
                        confidence=round(weight, 2),
                        action=f"安装/使用技能: {skill}",
                        metadata={
                            'skill_name': skill,
                            'topic': topic,
                            'reason': 'topic_match'
                        }
                    )
                    recommendations.append(rec)
        
        return recommendations
    
    def _recommend_skills_by_context(self, context: str) -> List[Recommendation]:
        """基于上下文推荐技能"""
        recommendations = []
        
        # 上下文关键词到技能的映射
        context_skill_map = {
            r'(股票|行情|K线|涨停)': ['stock-screener', 'stock-analysis-suite'],
            r'(储能|电价|光伏|新能源)': ['storage-calc', 'electricity-price-crawler'],
            r'(备份|恢复|维护)': ['system-backup', 'system-maintenance'],
            r'(Agent|多Agent|开发)': ['multi-agent-cn', 'agent-team-orchestration'],
            r'(图表|数据|分析)': ['chart-generator', 'data-processor'],
            r'(文档|报告|Excel)': ['office-pro', 'report-generator'],
        }
        
        for pattern, skills in context_skill_map.items():
            if re.search(pattern, context, re.IGNORECASE):
                for skill in skills:
                    rec = Recommendation(
                        type=self.TYPE_SKILL,
                        title=f"相关技能: {skill}",
                        description=f"此技能可能有助于当前任务",
                        priority=self.PRIORITY_HIGH,
                        source="context_match",
                        confidence=0.85,
                        action=f"尝试使用: {skill}",
                        metadata={
                            'skill_name': skill,
                            'context_match': pattern,
                            'reason': 'context_match'
                        }
                    )
                    recommendations.append(rec)
        
        return recommendations
    
    def _recommend_skills_by_projects(self) -> List[Recommendation]:
        """基于项目需求推荐技能"""
        recommendations = []
        
        # 检查当前项目
        profile = self._load_profile()
        if not profile or not profile.get('interested_projects'):
            return recommendations
        
        # 项目到推荐技能的映射
        project_skill_hints = {
            '储能': 'storage-calc',
            '股票': 'stock-screener',
            '网站': 'system-backup',
            '技能包': 'skill-creator',
        }
        
        for project in profile.get('interested_projects', [])[:5]:
            for keyword, skill in project_skill_hints.items():
                if keyword in project:
                    rec = Recommendation(
                        type=self.TYPE_SKILL,
                        title=f"项目技能: {skill}",
                        description=f"基于项目'{project}'推荐",
                        priority=self.PRIORITY_MEDIUM,
                        source="project_based",
                        confidence=0.7,
                        action=f"查看技能: {skill}",
                        metadata={
                            'skill_name': skill,
                            'project': project,
                            'reason': 'project_based'
                        }
                    )
                    recommendations.append(rec)
        
        return recommendations
    
    # ========================================================================
    # 辅助方法
    # ========================================================================
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        keywords = []
        
        # 中文词汇 (2-6字)
        chinese = re.findall(r'[\u4e00-\u9fa5]{2,6}', text)
        keywords.extend(chinese)
        
        # 英文技术词汇
        english = re.findall(r'[A-Za-z][A-Za-z0-9_-]{2,}', text)
        keywords.extend([w.lower() for w in english])
        
        # 统计频率并去重
        counter = Counter(keywords)
        # 返回频率较高的词
        return [word for word, count in counter.most_common(10) if count >= 1]
    
    def _extract_snippets(self, content: str, keyword: str, context_chars: int = 50) -> List[str]:
        """提取关键词周围的文本片段"""
        snippets = []
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        
        for match in pattern.finditer(content):
            start = max(0, match.start() - context_chars)
            end = min(len(content), match.end() + context_chars)
            snippet = content[start:end].replace('\n', ' ').strip()
            snippets.append(snippet)
            
            if len(snippets) >= 3:  # 最多3个片段
                break
        
        return snippets
    
    def _extract_important_sections(self, content: str) -> List[str]:
        """提取重要内容段落"""
        sections = []
        
        # 匹配标题
        headers = re.findall(r'^##?\s+(.+)$', content, re.MULTILINE)
        sections.extend(headers[:5])
        
        # 匹配项目标记
        projects = re.findall(r'\[PROJECT\]\s*(.+?)(?=\n|\[)', content, re.DOTALL)
        sections.extend([p.strip()[:50] for p in projects])
        
        # 匹配决策记录
        decisions = re.findall(r'\[DECISION\]\s*(.+?)(?=\n|\[)', content, re.DOTALL)
        sections.extend([d.strip()[:50] for d in decisions])
        
        return sections
    
    def _deduplicate_recommendations(self, recommendations: List[Recommendation],
                                     key: str = 'title') -> List[Recommendation]:
        """去重推荐"""
        seen = set()
        unique = []
        
        for rec in recommendations:
            value = getattr(rec, key, rec.title)
            if value not in seen:
                seen.add(value)
                unique.append(rec)
        
        return unique
    
    def _sort_by_priority(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """按优先级排序"""
        priority_order = {
            self.PRIORITY_HIGH: 0,
            self.PRIORITY_MEDIUM: 1,
            self.PRIORITY_LOW: 2
        }
        
        return sorted(recommendations, key=lambda x: (
            priority_order.get(x.priority, 3),
            -x.confidence
        ))
    
    # ========================================================================
    # 报告生成
    # ========================================================================
    
    def generate_report(self, context: str = "") -> Dict[str, Any]:
        """
        生成完整推荐报告
        
        Args:
            context: 可选的上下文
            
        Returns:
            推荐报告字典
        """
        self.logger.info("生成完整推荐报告...")
        
        # 收集所有推荐
        all_recommendations = []
        all_recommendations.extend(self.recommend_memories(context, limit=5))
        all_recommendations.extend(self.recommend_todos(limit=5))
        all_recommendations.extend(self.recommend_skills(context, limit=5))
        
        # 去重并排序
        all_recommendations = self._deduplicate_recommendations(all_recommendations)
        all_recommendations = self._sort_by_priority(all_recommendations)
        
        # 按类型分组
        by_type = defaultdict(list)
        by_priority = defaultdict(list)
        
        for rec in all_recommendations:
            by_type[rec.type].append(rec.to_dict())
            by_priority[rec.priority].append(rec.to_dict())
        
        # 高优先级推荐
        high_priority = [r.to_dict() for r in all_recommendations if r.priority == self.PRIORITY_HIGH][:5]
        
        report = {
            'timestamp': format_datetime(),
            'total_recommendations': len(all_recommendations),
            'by_type': dict(by_type),
            'by_priority': dict(by_priority),
            'high_priority': high_priority,
            'all_recommendations': [r.to_dict() for r in all_recommendations]
        }
        
        self.logger.info(f"报告生成完成: {len(all_recommendations)} 条推荐")
        return report
    
    def save_report(self, report: Optional[Dict] = None, 
                    filename: Optional[str] = None) -> Path:
        """
        保存推荐报告
        
        Args:
            report: 报告字典，None 则自动生成
            filename: 文件名，None 则使用默认名称
            
        Returns:
            保存的文件路径
        """
        if report is None:
            report = self.generate_report()
        
        if filename is None:
            filename = f"recommendations_{get_date_string()}.json"
        
        report_path = self.memory_dir / 'recommendations' / filename
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        if save_json(report, report_path):
            self.logger.info(f"推荐报告已保存: {report_path}")
        else:
            self.logger.error(f"保存推荐报告失败: {report_path}")
        
        return report_path
    
    # ========================================================================
    # CLI 接口
    # ========================================================================
    
    def run(self, context: str = "", save: bool = True) -> Dict[str, Any]:
        """
        运行推荐系统（完整流程）
        
        Args:
            context: 可选的上下文
            save: 是否保存报告
            
        Returns:
            推荐报告
        """
        self.logger.info("=" * 60)
        self.logger.info("开始运行推荐系统")
        self.logger.info("=" * 60)
        
        # 生成报告
        report = self.generate_report(context)
        
        # 打印摘要
        self._print_summary(report)
        
        # 保存报告
        if save:
            self.save_report(report)
        
        self.logger.info("推荐系统运行完成")
        return report
    
    def _print_summary(self, report: Dict):
        """打印推荐摘要"""
        print("\n" + "=" * 60)
        print("💡 智能推荐报告")
        print("=" * 60)
        print(f"  生成时间: {report['timestamp']}")
        print(f"  总推荐数: {report['total_recommendations']}")
        
        # 按类型统计
        if report.get('by_type'):
            print(f"\n  📦 按类型:")
            for rec_type, items in report['by_type'].items():
                type_emoji = {
                    'memory': '📝',
                    'todo': '✅',
                    'skill': '🛠️',
                    'topic': '🏷️',
                    'action': '⚡',
                    'alert': '🔔'
                }.get(rec_type, '📌')
                print(f"    {type_emoji} {rec_type}: {len(items)}")
        
        # 按优先级统计
        if report.get('by_priority'):
            print(f"\n  🔥 按优先级:")
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
            for priority, items in report['by_priority'].items():
                emoji = priority_emoji.get(priority, '⚪')
                print(f"    {emoji} {priority}: {len(items)}")
        
        # 高优先级推荐
        if report.get('high_priority'):
            print(f"\n  ⚡ 高优先级推荐:")
            for i, item in enumerate(report['high_priority'][:5], 1):
                print(f"    {i}. [{item['type']}] {item['title']}")
                if item.get('action'):
                    print(f"       💡 {item['action']}")
        
        print("\n" + "=" * 60)


# ============================================================================
# 命令行接口
# ============================================================================

def main():
    """主函数 - CLI 入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Memory Suite 推荐系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python recommender.py                    # 生成完整推荐报告
  python recommender.py --context "股票"    # 基于上下文推荐
  python recommender.py --type memory      # 仅推荐记忆
  python recommender.py --save false       # 不保存报告
        """
    )
    
    parser.add_argument('--context', '-c', type=str, default='',
                       help='当前上下文/查询')
    parser.add_argument('--type', '-t', type=str, 
                       choices=['all', 'memory', 'todo', 'skill'],
                       default='all',
                       help='推荐类型')
    parser.add_argument('--limit', '-l', type=int, default=5,
                       help='每种类型返回数量限制')
    parser.add_argument('--save', '-s', type=lambda x: x.lower() == 'true',
                       default=True,
                       help='是否保存报告 (true/false)')
    parser.add_argument('--config', type=str,
                       help='配置文件路径')
    
    args = parser.parse_args()
    
    # 加载配置
    config = None
    if args.config:
        config = load_json(args.config)
    
    # 初始化推荐系统
    recommender = Recommender(config)
    
    # 根据类型执行推荐
    if args.type == 'all':
        report = recommender.run(context=args.context, save=args.save)
    elif args.type == 'memory':
        recs = recommender.recommend_memories(args.context, args.limit)
        for rec in recs:
            print(f"[{rec.priority}] {rec.title}")
            print(f"  {rec.description}")
            print()
    elif args.type == 'todo':
        recs = recommender.recommend_todos(args.limit)
        for rec in recs:
            print(f"[{rec.priority}] {rec.title}")
            print(f"  {rec.description}")
            print()
    elif args.type == 'skill':
        recs = recommender.recommend_skills(args.context, args.limit)
        for rec in recs:
            print(f"[{rec.priority}] {rec.title}")
            print(f"  {rec.description}")
            print()


if __name__ == "__main__":
    main()
