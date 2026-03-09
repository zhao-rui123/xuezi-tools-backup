#!/usr/bin/env python3
"""
知识库智能管理系统 v2.0
配合统一记忆系统迭代升级

功能：
1. 从记忆自动生成知识库文档
2. 智能关联记忆和知识
3. 知识库内容质量评估
4. 自动归档过期内容
5. 知识一致性维护

作者: 雪子助手
版本: 2.0.0
日期: 2026-03-09
"""

import os
import json
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

# 配置
MEMORY_DIR = Path("/Users/zhaoruicn/.openclaw/workspace/memory")
KNOWLEDGE_DIR = Path("/Users/zhaoruicn/.openclaw/workspace/knowledge-base")
KB_MANAGE_FILE = KNOWLEDGE_DIR / ".kb_management.json"


@dataclass
class KnowledgeDoc:
    """知识文档"""
    path: str
    title: str
    category: str
    tags: List[str]
    importance: float
    last_updated: str
    related_memories: List[str]
    quality_score: float
    status: str  # active, stale, archived


class KnowledgeBaseManager:
    """知识库智能管理系统"""
    
    def __init__(self):
        self.memory_dir = MEMORY_DIR
        self.knowledge_dir = KNOWLEDGE_DIR
        self.docs: Dict[str, KnowledgeDoc] = {}
        self._load_management_data()
    
    def _load_management_data(self):
        """加载管理数据"""
        if KB_MANAGE_FILE.exists():
            try:
                with open(KB_MANAGE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.docs = {k: KnowledgeDoc(**v) for k, v in data.get("docs", {}).items()}
            except:
                self.docs = {}
    
    def _save_management_data(self):
        """保存管理数据"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "docs": {k: asdict(v) for k, v in self.docs.items()}
        }
        with open(KB_MANAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def scan_all_docs(self):
        """扫描所有知识文档"""
        print("🔍 扫描知识库文档...")
        
        md_files = list(self.knowledge_dir.rglob("*.md"))
        
        # 排除系统文件
        md_files = [f for f in md_files if ".kb_management" not in str(f)]
        
        print(f"  发现 {len(md_files)} 个文档")
        
        for file_path in md_files:
            relative_path = str(file_path.relative_to(self.knowledge_dir))
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取信息
                title = self._extract_title(content) or file_path.stem
                category = self._detect_category(file_path)
                tags = self._extract_tags(content)
                importance = self._calculate_importance(content)
                
                # 检查是否已存在
                if relative_path in self.docs:
                    doc = self.docs[relative_path]
                    doc.title = title
                    doc.category = category
                    doc.tags = tags
                    doc.importance = importance
                else:
                    self.docs[relative_path] = KnowledgeDoc(
                        path=relative_path,
                        title=title,
                        category=category,
                        tags=tags,
                        importance=importance,
                        last_updated=datetime.now().strftime('%Y-%m-%d'),
                        related_memories=[],
                        quality_score=0.0,
                        status="active"
                    )
                    
            except Exception as e:
                print(f"  ⚠️ 处理 {file_path.name} 失败: {str(e)}")
        
        self._save_management_data()
        print(f"  ✅ 扫描完成")
    
    def _extract_title(self, content: str) -> Optional[str]:
        """提取标题"""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None
    
    def _detect_category(self, file_path: Path) -> str:
        """检测类别"""
        path_str = str(file_path).lower()
        
        if "/projects/" in path_str:
            return "project"
        elif "/decisions/" in path_str:
            return "decision"
        elif "/problems/" in path_str:
            return "problem"
        elif "/references/" in path_str:
            return "reference"
        elif "/operations/" in path_str:
            return "operation"
        elif "/templates/" in path_str:
            return "template"
        else:
            return "other"
    
    def _extract_tags(self, content: str) -> List[str]:
        """提取标签"""
        tags = re.findall(r'#([\w\u4e00-\u9fa5-]+)', content)
        return list(set(tags))
    
    def _calculate_importance(self, content: str) -> float:
        """计算重要性"""
        score = 0.5  # 基础分
        
        # 关键词加分
        important_keywords = ['决策', '重要', '关键', '核心', '故障', '解决']
        for kw in important_keywords:
            if kw in content:
                score += 0.05
        
        # 长度适中加分
        if 500 < len(content) < 5000:
            score += 0.1
        
        # 有标签加分
        if '#' in content:
            score += 0.1
        
        # 有链接加分
        if '](http' in content or '](../' in content:
            score += 0.05
        
        return min(1.0, score)
    
    def link_with_memories(self):
        """关联记忆和知识"""
        print("🔗 关联记忆和知识...")
        
        linked_count = 0
        
        # 扫描记忆文件
        for memory_file in self.memory_dir.glob("2026-*.md"):
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    memory_content = f.read()
                
                # 提取关键词
                keywords = self._extract_keywords(memory_content)
                
                # 查找相关文档
                for doc_path, doc in self.docs.items():
                    if doc.status != "active":
                        continue
                    
                    # 检查标题和标签匹配
                    match_score = 0
                    
                    # 标题匹配
                    for kw in keywords:
                        if kw in doc.title or kw in ' '.join(doc.tags):
                            match_score += 1
                    
                    # 如果匹配度足够高，建立关联
                    if match_score >= 2:
                        memory_name = memory_file.name
                        if memory_name not in doc.related_memories:
                            doc.related_memories.append(memory_name)
                            linked_count += 1
                            
            except:
                continue
        
        if linked_count > 0:
            self._save_management_data()
        
        print(f"  建立了 {linked_count} 个新关联")
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词"""
        keywords = []
        
        # 中文词汇
        chinese = re.findall(r'[\u4e00-\u9fa5]{2,4}', content)
        keywords.extend(chinese)
        
        # 英文词汇
        english = re.findall(r'[A-Za-z][A-Za-z0-9_]{2,}', content)
        keywords.extend([w.lower() for w in english])
        
        return list(set(keywords))
    
    def evaluate_quality(self):
        """评估文档质量"""
        print("📊 评估文档质量...")
        
        for doc_path, doc in self.docs.items():
            if doc.status != "active":
                continue
            
            file_path = self.knowledge_dir / doc_path
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 质量评分
                score = 0.0
                
                # 有标题
                if re.search(r'^#\s+.+$', content, re.MULTILINE):
                    score += 0.2
                
                # 有标签
                if '#' in content:
                    score += 0.2
                
                # 内容长度
                if len(content) > 500:
                    score += 0.2
                
                # 有结构化内容
                if '##' in content:
                    score += 0.2
                
                # 有链接
                if '](' in content:
                    score += 0.1
                
                # 有关联记忆
                if doc.related_memories:
                    score += 0.1
                
                doc.quality_score = round(score, 2)
                
            except:
                continue
        
        self._save_management_data()
        print("  ✅ 质量评估完成")
    
    def identify_stale_content(self):
        """识别过期内容"""
        print("⏰ 识别过期内容...")
        
        stale_docs = []
        current_date = datetime.now()
        
        for doc_path, doc in self.docs.items():
            if doc.status != "active":
                continue
            
            # 检查最后更新时间
            try:
                last_updated = datetime.strptime(doc.last_updated, '%Y-%m-%d')
                days_since_update = (current_date - last_updated).days
                
                # 超过90天未更新
                if days_since_update > 90:
                    doc.status = "stale"
                    stale_docs.append(doc_path)
                    
            except:
                continue
        
        if stale_docs:
            self._save_management_data()
        
        print(f"  发现 {len(stale_docs)} 个过期文档")
        return stale_docs
    
    def generate_index_update(self):
        """生成索引更新建议"""
        print("📋 生成索引更新建议...")
        
        # 统计
        category_count = defaultdict(int)
        quality_distribution = {"high": 0, "medium": 0, "low": 0}
        
        for doc in self.docs.values():
            if doc.status == "active":
                category_count[doc.category] += 1
                
                if doc.quality_score >= 0.7:
                    quality_distribution["high"] += 1
                elif doc.quality_score >= 0.4:
                    quality_distribution["medium"] += 1
                else:
                    quality_distribution["low"] += 1
        
        # 高价值文档
        high_value = [
            (path, doc) for path, doc in self.docs.items()
            if doc.status == "active" and doc.importance >= 0.7
        ]
        high_value.sort(key=lambda x: x[1].importance, reverse=True)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_docs": len(self.docs),
                "active_docs": sum(1 for d in self.docs.values() if d.status == "active"),
                "stale_docs": sum(1 for d in self.docs.values() if d.status == "stale"),
                "archived_docs": sum(1 for d in self.docs.values() if d.status == "archived")
            },
            "category_distribution": dict(category_count),
            "quality_distribution": quality_distribution,
            "high_value_docs": [
                {"path": path, "title": doc.title, "importance": doc.importance}
                for path, doc in high_value[:10]
            ],
            "recommendations": []
        }
        
        # 生成建议
        if quality_distribution["low"] > 0:
            report["recommendations"].append({
                "type": "improve_quality",
                "message": f"有 {quality_distribution['low']} 个低质量文档需要完善",
                "priority": "medium"
            })
        
        if report["summary"]["stale_docs"] > 0:
            report["recommendations"].append({
                "type": "review_stale",
                "message": f"有 {report['summary']['stale_docs']} 个文档超过90天未更新",
                "priority": "low"
            })
        
        return report
    
    def auto_generate_from_memory(self):
        """从记忆自动生成知识文档"""
        print("📝 从记忆自动生成知识文档...")
        
        generated = 0
        
        # 扫描高重要性记忆
        for memory_file in self.memory_dir.glob("2026-*.md"):
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查重要性
                if "[PROJECT]" in content and "## 完成" in content:
                    # 提取项目名称
                    project_match = re.search(r'###\s+(.+?)(?:开发|完成|项目)', content)
                    if project_match:
                        project_name = project_match.group(1).strip()
                        
                        # 检查是否已存在
                        safe_name = re.sub(r'[^\w\u4e00-\u9fa5-]', '-', project_name)[:30]
                        doc_path = f"projects/{safe_name}/README.md"
                        
                        if doc_path not in self.docs:
                            # 生成项目文档
                            self._generate_project_doc(project_name, content, memory_file.name)
                            generated += 1
                            
            except:
                continue
        
        print(f"  生成了 {generated} 个新文档")
        return generated
    
    def _generate_project_doc(self, project_name: str, memory_content: str, memory_file: str):
        """生成项目文档"""
        safe_name = re.sub(r'[^\w\u4e00-\u9fa5-]', '-', project_name)[:30]
        project_dir = self.knowledge_dir / "projects" / safe_name
        project_dir.mkdir(parents=True, exist_ok=True)
        
        doc_path = project_dir / "README.md"
        
        # 提取关键信息
        features = re.findall(r'-\s+(.+?)(?=\n|$)', memory_content)
        features = [f for f in features if len(f) < 100][:10]
        
        content = f"""# {project_name}

**状态**: 🟢活跃
**来源**: [{memory_file}](../memory/{memory_file})
**创建时间**: {datetime.now().strftime('%Y-%m-%d')}
**自动生成的**: 从记忆文件自动提取

## 项目概述
从记忆自动生成的项目文档。

## 核心功能
{chr(10).join(['- ' + f for f in features])}

## 相关记忆
- [{memory_file}](../memory/{memory_file})

## 更新日志
- {datetime.now().strftime('%Y-%m-%d')}: 从记忆自动生成
"""
        
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 记录
        relative_path = str(doc_path.relative_to(self.knowledge_dir))
        self.docs[relative_path] = KnowledgeDoc(
            path=relative_path,
            title=project_name,
            category="project",
            tags=["auto-generated"],
            importance=0.6,
            last_updated=datetime.now().strftime('%Y-%m-%d'),
            related_memories=[memory_file],
            quality_score=0.5,
            status="active"
        )
        
        self._save_management_data()
    
    def run(self):
        """运行知识库管理"""
        print("=" * 60)
        print("📚 知识库智能管理系统 v2.0")
        print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 1. 扫描所有文档
        self.scan_all_docs()
        
        # 2. 关联记忆
        self.link_with_memories()
        
        # 3. 评估质量
        self.evaluate_quality()
        
        # 4. 识别过期内容
        stale = self.identify_stale_content()
        
        # 5. 自动生成文档
        generated = self.auto_generate_from_memory()
        
        # 6. 生成报告
        report = self.generate_index_update()
        
        # 打印报告
        print("\n" + "=" * 60)
        print("📊 知识库报告")
        print("=" * 60)
        print(f"  总文档数: {report['summary']['total_docs']}")
        print(f"  活跃文档: {report['summary']['active_docs']}")
        print(f"  过期文档: {report['summary']['stale_docs']}")
        
        print(f"\n  📦 类别分布:")
        for cat, count in sorted(report['category_distribution'].items(), key=lambda x: x[1], reverse=True):
            print(f"    {cat}: {count}")
        
        print(f"\n  📊 质量分布:")
        for quality, count in report['quality_distribution'].items():
            print(f"    {quality}: {count}")
        
        if generated > 0:
            print(f"\n  ✨ 自动生成: {generated} 个新文档")
        
        if stale:
            print(f"\n  ⚠️ 过期文档: {len(stale)} 个需要审查")
        
        if report['recommendations']:
            print(f"\n  💡 建议:")
            for rec in report['recommendations']:
                emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec['priority'], "⚪")
                print(f"    {emoji} {rec['message']}")
        
        # 保存报告
        report_file = self.knowledge_dir / ".kb_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print("\n✅ 知识库管理完成")
        
        return report


def main():
    """主函数"""
    manager = KnowledgeBaseManager()
    report = manager.run()
    return report


if __name__ == "__main__":
    main()
