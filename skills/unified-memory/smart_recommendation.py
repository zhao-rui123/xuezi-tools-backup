#!/usr/bin/env python3
"""
智能推荐系统 (Smart Recommendation System)
第二阶段 - 智能进化

功能：
1. 基于上下文推荐相关知识
2. 主动提醒待办事项
3. 发现知识盲区
4. 个性化建议

作者: 雪子助手
版本: 1.0.0
日期: 2026-03-09
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# 配置
MEMORY_DIR = Path("/Users/zhaoruicn/.openclaw/workspace/memory")
KNOWLEDGE_DIR = MEMORY_DIR / "knowledge_graph"
PROFILE_FILE = MEMORY_DIR / "user_profile.json"


@dataclass
class Recommendation:
    """推荐项"""
    type: str  # knowledge, todo, skill, alert
    title: str
    description: str
    priority: str  # high, medium, low
    source: str
    confidence: float
    action: Optional[str] = None


class SmartRecommendationSystem:
    """智能推荐系统"""
    
    def __init__(self):
        self.memory_dir = MEMORY_DIR
        self.profile = self._load_profile()
        self.knowledge_graph = self._load_knowledge_graph()
        self.recommendations: List[Recommendation] = []
    
    def _load_profile(self) -> Optional[Dict]:
        """加载用户画像"""
        if PROFILE_FILE.exists():
            try:
                with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def _load_knowledge_graph(self) -> Optional[Dict]:
        """加载知识图谱"""
        graph_file = KNOWLEDGE_DIR / "graph.json"
        if graph_file.exists():
            try:
                with open(graph_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def recommend_knowledge(self, context: str = "") -> List[Recommendation]:
        """基于上下文推荐知识"""
        recs = []
        
        if not self.knowledge_graph:
            return recs
        
        # 1. 根据话题偏好推荐
        if self.profile and self.profile.get("topic_preferences"):
            top_topics = sorted(
                self.profile["topic_preferences"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            for topic, weight in top_topics:
                # 查找相关实体
                related = self._find_related_entities(topic)
                if related:
                    recs.append(Recommendation(
                        type="knowledge",
                        title=f"相关话题: {topic}",
                        description=f"您可能对{topic}相关的{len(related)}个知识点感兴趣",
                        priority="medium" if weight > 0.3 else "low",
                        source="topic_preference",
                        confidence=weight,
                        action=f"查看相关: {', '.join([r[:30] for r in related[:3]])}"
                    ))
        
        # 2. 基于当前上下文推荐
        if context:
            context_keywords = self._extract_keywords(context)
            for keyword in context_keywords:
                related = self._find_related_entities(keyword)
                if related:
                    recs.append(Recommendation(
                        type="knowledge",
                        title=f"相关: {keyword}",
                        description=f"与'{keyword}'相关的内容",
                        priority="high",
                        source="context",
                        confidence=0.8,
                        action=f"查看: {related[0][:50]}..." if related else None
                    ))
        
        return recs
    
    def recommend_todos(self) -> List[Recommendation]:
        """推荐待办事项"""
        recs = []
        
        # 1. 扫描未完成的TODO
        pending_todos = self._scan_pending_todos()
        
        for todo in pending_todos[:5]:  # 最多5个
            recs.append(Recommendation(
                type="todo",
                title=f"待办: {todo['title'][:40]}",
                description=f"来源: {todo['source']}",
                priority="high" if todo.get("important") else "medium",
                source="pending_task",
                confidence=0.9,
                action="查看详情"
            ))
        
        # 2. 基于活跃时段推荐
        if self.profile and self.profile.get("active_hours"):
            current_hour = datetime.now().hour
            if current_hour in self.profile["active_hours"]:
                recs.append(Recommendation(
                    type="alert",
                    title="⏰ 活跃时段提醒",
                    description="现在是您的工作高效时段，建议处理重要任务",
                    priority="medium",
                    source="active_hour",
                    confidence=0.7
                ))
        
        return recs
    
    def discover_knowledge_gaps(self) -> List[Recommendation]:
        """发现知识盲区"""
        recs = []
        
        # 1. 检查技能覆盖
        if self.profile and self.profile.get("skill_level"):
            skills = self.profile["skill_level"]
            
            # 找出低水平技能
            for skill, level in skills.items():
                if level in ["beginner", "learning"]:
                    recs.append(Recommendation(
                        type="skill",
                        title=f"📚 提升技能: {skill}",
                        description=f"您的{skill}技能还有提升空间",
                        priority="low",
                        source="skill_gap",
                        confidence=0.6,
                        action="建议学习相关资料"
                    ))
        
        # 2. 检查项目完整性
        incomplete_projects = self._find_incomplete_projects()
        for project in incomplete_projects:
            recs.append(Recommendation(
                type="alert",
                title=f"🚨 项目待完善: {project['name'][:40]}",
                description=f"项目可能缺少文档或测试",
                priority="medium",
                source="project_gap",
                confidence=0.7,
                action="完善项目文档"
            ))
        
        return recs
    
    def recommend_skills(self) -> List[Recommendation]:
        """推荐技能/工具"""
        recs = []
        
        # 基于项目需求推荐技能
        if self.knowledge_graph:
            entities = self.knowledge_graph.get("entities", {})
            
            # 统计高频技能
            skill_count = {}
            for entity_id, entity in entities.items():
                if entity.get("type") == "skill":
                    name = entity.get("name", "")
                    skill_count[name] = skill_count.get(name, 0) + 1
            
            # 推荐热门但用户未掌握的技能
            for skill, count in sorted(skill_count.items(), key=lambda x: x[1], reverse=True)[:3]:
                if not self._user_has_skill(skill):
                    recs.append(Recommendation(
                        type="skill",
                        title=f"🛠️ 推荐技能: {skill}",
                        description=f"该技能在您的项目中高频使用({count}次)",
                        priority="medium",
                        source="skill_recommendation",
                        confidence=0.75,
                        action="学习该技能"
                    ))
        
        return recs
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        keywords = []
        
        # 中文词汇
        chinese = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)
        keywords.extend(chinese)
        
        # 英文技术词汇
        english = re.findall(r'[A-Za-z][A-Za-z0-9_]{2,}', text)
        keywords.extend([w.lower() for w in english])
        
        return list(set(keywords))
    
    def _find_related_entities(self, keyword: str) -> List[str]:
        """查找相关实体"""
        if not self.knowledge_graph:
            return []
        
        related = []
        entities = self.knowledge_graph.get("entities", {})
        
        for entity_id, entity in entities.items():
            name = entity.get("name", "")
            if keyword in name or name in keyword:
                related.append(name)
        
        return related
    
    def _scan_pending_todos(self) -> List[Dict]:
        """扫描待办事项"""
        todos = []
        
        # 扫描记忆文件
        for file_path in self.memory_dir.glob("2026-*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 匹配 TODO
                todo_section = re.search(r'\[TODO\](.*?)(?=\n\[|\Z)', content, re.DOTALL)
                if todo_section:
                    todo_text = todo_section.group(1)
                    # 提取未完成的项
                    pending = re.findall(r'- \[ \] (.+)', todo_text)
                    for item in pending:
                        todos.append({
                            "title": item.strip(),
                            "source": file_path.name,
                            "important": "重要" in item or "紧急" in item
                        })
                
            except:
                continue
        
        return todos
    
    def _find_incomplete_projects(self) -> List[Dict]:
        """查找未完成的项目"""
        incomplete = []
        
        if not self.knowledge_graph:
            return incomplete
        
        entities = self.knowledge_graph.get("entities", {})
        
        for entity_id, entity in entities.items():
            if entity.get("type") == "project":
                name = entity.get("name", "")
                # 检查是否缺少文档
                if not self._has_documentation(name):
                    incomplete.append({
                        "name": name,
                        "issue": "缺少文档"
                    })
        
        return incomplete
    
    def _has_documentation(self, project_name: str) -> bool:
        """检查项目是否有文档"""
        # 简单检查：知识库中是否有该项目
        kb_dir = Path("/Users/zhaoruicn/.openclaw/workspace/knowledge-base")
        if kb_dir.exists():
            for file in kb_dir.rglob("*.md"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if project_name in content:
                        return True
                except:
                    continue
        return False
    
    def _user_has_skill(self, skill: str) -> bool:
        """检查用户是否已掌握某技能"""
        if self.profile and self.profile.get("skill_level"):
            return skill in self.profile["skill_level"]
        return False
    
    def generate_daily_digest(self) -> Dict:
        """生成每日推荐摘要"""
        print("📋 生成每日推荐...")
        
        self.recommendations = []
        
        # 收集各类推荐
        self.recommendations.extend(self.recommend_todos())
        self.recommendations.extend(self.recommend_knowledge())
        self.recommendations.extend(self.discover_knowledge_gaps())
        self.recommendations.extend(self.recommend_skills())
        
        # 按优先级排序
        priority_order = {"high": 0, "medium": 1, "low": 2}
        self.recommendations.sort(key=lambda x: priority_order.get(x.priority, 3))
        
        # 生成报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_recommendations": len(self.recommendations),
            "by_type": {},
            "by_priority": {},
            "high_priority": [],
            "all_recommendations": []
        }
        
        for rec in self.recommendations:
            # 按类型统计
            report["by_type"][rec.type] = report["by_type"].get(rec.type, 0) + 1
            
            # 按优先级统计
            report["by_priority"][rec.priority] = report["by_priority"].get(rec.priority, 0) + 1
            
            # 高优先级
            if rec.priority == "high":
                report["high_priority"].append({
                    "title": rec.title,
                    "description": rec.description,
                    "action": rec.action
                })
            
            # 所有推荐
            report["all_recommendations"].append({
                "type": rec.type,
                "title": rec.title,
                "priority": rec.priority,
                "confidence": rec.confidence
            })
        
        return report
    
    def run(self):
        """运行推荐系统"""
        print("=" * 60)
        print("💡 智能推荐系统")
        print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 生成每日摘要
        report = self.generate_daily_digest()
        
        # 打印报告
        print("\n" + "=" * 60)
        print("📊 推荐摘要")
        print("=" * 60)
        print(f"  总推荐数: {report['total_recommendations']}")
        
        print(f"\n  📦 按类型:")
        for rec_type, count in report["by_type"].items():
            print(f"    {rec_type}: {count}")
        
        print(f"\n  🔥 按优先级:")
        for priority, count in report["by_priority"].items():
            emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")
            print(f"    {emoji} {priority}: {count}")
        
        if report["high_priority"]:
            print(f"\n  ⚡ 高优先级推荐:")
            for i, item in enumerate(report["high_priority"][:5], 1):
                print(f"    {i}. {item['title']}")
                if item.get("action"):
                    print(f"       💡 {item['action']}")
        
        # 保存报告
        report_file = self.memory_dir / "daily_recommendations.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n  📝 报告已保存: {report_file}")
        
        print("\n✅ 推荐生成完成")
        
        return report


def main():
    """主函数"""
    system = SmartRecommendationSystem()
    report = system.run()
    return report


if __name__ == "__main__":
    main()
