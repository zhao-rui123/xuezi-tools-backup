#!/usr/bin/env python3
"""
知识图谱系统 (Knowledge Graph System)
第二阶段 - 智能进化

功能：
1. 自动提取实体和关系
2. 构建项目-技能-决策关联网络
3. 知识可视化
4. 关联推荐

作者: 雪子助手
版本: 1.0.0
日期: 2026-03-09
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass, asdict

# 配置
MEMORY_DIR = Path("/Users/zhaoruicn/.openclaw/workspace/memory")
KNOWLEDGE_DIR = MEMORY_DIR / "knowledge_graph"
GRAPH_FILE = KNOWLEDGE_DIR / "graph.json"

# 确保目录存在
KNOWLEDGE_DIR.mkdir(exist_ok=True)


@dataclass
class Entity:
    """知识实体"""
    id: str
    name: str
    type: str  # project, skill, decision, person, concept, tool
    properties: Dict
    sources: List[str]  # 来源文件
    created_at: str
    updated_at: str


@dataclass
class Relation:
    """实体关系"""
    source: str  # 实体ID
    target: str  # 实体ID
    type: str  # uses, depends_on, related_to, part_of, implements
    properties: Dict
    sources: List[str]


class KnowledgeGraphSystem:
    """知识图谱系统"""
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relations: List[Relation] = []
        self.graph_data = self._load_graph()
    
    def _load_graph(self) -> Dict:
        """加载图谱数据"""
        if GRAPH_FILE.exists():
            try:
                with open(GRAPH_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"entities": {}, "relations": []}
    
    def _save_graph(self):
        """保存图谱数据"""
        graph_data = {
            "timestamp": datetime.now().isoformat(),
            "entities": {k: asdict(v) for k, v in self.entities.items()},
            "relations": [asdict(r) for r in self.relations]
        }
        
        with open(GRAPH_FILE, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=2)
    
    def _extract_entities_from_content(self, content: str, source_file: str) -> List[Dict]:
        """从内容中提取实体"""
        entities = []
        
        # 1. 提取项目名称
        project_patterns = [
            r'###\s+(.+?)(?:开发|完成|项目|系统)',
            r'##\s+(.+?)(?:开发|完成|项目|系统)',
            r'\[PROJECT\]\s*(.+?)(?=\n|$)',
        ]
        
        for pattern in project_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                name = match.strip()
                if len(name) > 3 and len(name) < 50:
                    entities.append({
                        "name": name,
                        "type": "project",
                        "properties": {"category": "project"}
                    })
        
        # 2. 提取技能/工具
        skill_patterns = [
            r'`([^`]+?)\.py`',
            r'`([^`]+?)\.sh`',
            r'技能包[：:]\s*(.+?)(?=\n|$)',
            r'工具[：:]\s*(.+?)(?=\n|$)',
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                name = match.strip()
                if len(name) > 2:
                    entities.append({
                        "name": name,
                        "type": "skill",
                        "properties": {"category": "skill"}
                    })
        
        # 3. 提取技术概念
        tech_concepts = [
            "OpenClaw", "Python", "Flask", "JavaScript", "API", "GitHub",
            "储能", "光伏", "股票", "Kimi", "MiniMax", "飞书"
        ]
        
        for concept in tech_concepts:
            if concept in content:
                entities.append({
                    "name": concept,
                    "type": "concept",
                    "properties": {"category": "technology"}
                })
        
        # 4. 提取决策
        decision_pattern = r'\[DECISION\]\s*(.+?)(?=\n\[|\Z)'
        decisions = re.findall(decision_pattern, content, re.DOTALL)
        for decision in decisions:
            # 提取第一行作为决策名称
            first_line = decision.strip().split('\n')[0][:50]
            if first_line:
                entities.append({
                    "name": first_line,
                    "type": "decision",
                    "properties": {"category": "decision"}
                })
        
        return entities
    
    def _extract_relations_from_content(self, content: str, source_file: str, entities: List[Dict]) -> List[Dict]:
        """提取实体关系"""
        relations = []
        
        entity_names = [e["name"] for e in entities]
        
        # 1. 项目使用技能
        for project in [e for e in entities if e["type"] == "project"]:
            for skill in [e for e in entities if e["type"] == "skill"]:
                # 检查是否在同一段落
                if self._entities_in_same_paragraph(content, project["name"], skill["name"]):
                    relations.append({
                        "source": project["name"],
                        "target": skill["name"],
                        "type": "uses",
                        "properties": {}
                    })
        
        # 2. 技能依赖概念
        for skill in [e for e in entities if e["type"] == "skill"]:
            for concept in [e for e in entities if e["type"] == "concept"]:
                if concept["name"] in content and skill["name"] in content:
                    # 检查距离
                    pos_skill = content.find(skill["name"])
                    pos_concept = content.find(concept["name"])
                    if abs(pos_skill - pos_concept) < 500:
                        relations.append({
                            "source": skill["name"],
                            "target": concept["name"],
                            "type": "implements",
                            "properties": {}
                        })
        
        return relations
    
    def _entities_in_same_paragraph(self, content: str, entity1: str, entity2: str) -> bool:
        """检查两个实体是否在同一段落"""
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if entity1 in para and entity2 in para:
                return True
        return False
    
    def build_graph(self):
        """构建知识图谱"""
        print("🔨 构建知识图谱...")
        
        self.entities = {}
        self.relations = []
        
        # 扫描所有记忆文件
        memory_files = list(MEMORY_DIR.glob("2026-*.md"))
        archive_dir = MEMORY_DIR / "archive"
        if archive_dir.exists():
            memory_files.extend(archive_dir.rglob("*.md"))
        
        print(f"  扫描 {len(memory_files)} 个记忆文件")
        
        for file_path in memory_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                source = str(file_path.relative_to(MEMORY_DIR))
                
                # 提取实体
                entities = self._extract_entities_from_content(content, source)
                
                for entity_data in entities:
                    name = entity_data["name"]
                    entity_id = self._generate_id(name)
                    
                    if entity_id in self.entities:
                        # 更新已有实体
                        existing = self.entities[entity_id]
                        if source not in existing.sources:
                            existing.sources.append(source)
                        existing.updated_at = datetime.now().isoformat()
                    else:
                        # 创建新实体
                        now = datetime.now().isoformat()
                        self.entities[entity_id] = Entity(
                            id=entity_id,
                            name=name,
                            type=entity_data["type"],
                            properties=entity_data["properties"],
                            sources=[source],
                            created_at=now,
                            updated_at=now
                        )
                
                # 提取关系
                relations = self._extract_relations_from_content(content, source, entities)
                
                for rel_data in relations:
                    source_id = self._generate_id(rel_data["source"])
                    target_id = self._generate_id(rel_data["target"])
                    
                    # 检查是否已有相同关系
                    existing = [r for r in self.relations 
                              if r.source == source_id and r.target == target_id and r.type == rel_data["type"]]
                    
                    if not existing:
                        self.relations.append(Relation(
                            source=source_id,
                            target=target_id,
                            type=rel_data["type"],
                            properties=rel_data["properties"],
                            sources=[source]
                        ))
                
            except Exception as e:
                print(f"  ⚠️ 处理 {file_path.name} 失败: {str(e)}")
        
        # 保存
        self._save_graph()
        
        print(f"  ✅ 图谱构建完成: {len(self.entities)} 个实体, {len(self.relations)} 个关系")
    
    def _generate_id(self, name: str) -> str:
        """生成实体ID"""
        # 简单的哈希
        import hashlib
        return hashlib.md5(name.encode()).hexdigest()[:12]
    
    def find_related(self, entity_name: str, depth: int = 1) -> List[Dict]:
        """查找相关实体"""
        entity_id = self._generate_id(entity_name)
        
        if entity_id not in self.entities:
            return []
        
        related = []
        
        # 查找直接关系
        for rel in self.relations:
            if rel.source == entity_id:
                target = self.entities.get(rel.target)
                if target:
                    related.append({
                        "entity": asdict(target),
                        "relation": asdict(rel),
                        "direction": "outgoing"
                    })
            elif rel.target == entity_id:
                source = self.entities.get(rel.source)
                if source:
                    related.append({
                        "entity": asdict(source),
                        "relation": asdict(rel),
                        "direction": "incoming"
                    })
        
        return related
    
    def get_entity_stats(self) -> Dict:
        """获取实体统计"""
        type_counts = defaultdict(int)
        for entity in self.entities.values():
            type_counts[entity.type] += 1
        
        return {
            "total_entities": len(self.entities),
            "total_relations": len(self.relations),
            "type_distribution": dict(type_counts),
            "relation_types": list(set(r.type for r in self.relations))
        }
    
    def export_for_visualization(self) -> Dict:
        """导出可视化格式"""
        nodes = []
        links = []
        
        type_colors = {
            "project": "#4CAF50",
            "skill": "#2196F3",
            "decision": "#FF9800",
            "concept": "#9C27B0",
            "person": "#F44336",
            "tool": "#00BCD4"
        }
        
        for entity in self.entities.values():
            nodes.append({
                "id": entity.id,
                "name": entity.name,
                "type": entity.type,
                "color": type_colors.get(entity.type, "#999999"),
                "properties": entity.properties
            })
        
        for rel in self.relations:
            links.append({
                "source": rel.source,
                "target": rel.target,
                "type": rel.type
            })
        
        return {"nodes": nodes, "links": links}
    
    def run(self):
        """运行知识图谱构建"""
        print("=" * 60)
        print("🕸️ 知识图谱系统")
        print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 构建图谱
        self.build_graph()
        
        # 统计
        stats = self.get_entity_stats()
        
        print("\n" + "=" * 60)
        print("📊 图谱统计")
        print("=" * 60)
        print(f"  总实体数: {stats['total_entities']}")
        print(f"  总关系数: {stats['total_relations']}")
        
        print(f"\n  📦 实体类型分布:")
        for entity_type, count in sorted(stats['type_distribution'].items(), key=lambda x: x[1], reverse=True):
            print(f"    {entity_type}: {count}")
        
        print(f"\n  🔗 关系类型:")
        for rel_type in stats['relation_types']:
            print(f"    - {rel_type}")
        
        # 导出可视化数据
        viz_data = self.export_for_visualization()
        viz_file = KNOWLEDGE_DIR / "graph_visualization.json"
        with open(viz_file, 'w', encoding='utf-8') as f:
            json.dump(viz_data, f, ensure_ascii=False, indent=2)
        print(f"\n  📈 可视化数据: {viz_file}")
        
        print("\n✅ 知识图谱构建完成")
        
        return stats


def main():
    """主函数"""
    system = KnowledgeGraphSystem()
    stats = system.run()
    return stats


if __name__ == "__main__":
    main()
