#!/usr/bin/env python3
"""
自我进化系统 v2.0 - 与统一记忆系统联动
================================================

功能：
1. 从记忆自动提取学习点
2. 跟踪改进措施执行
3. 评估改进效果
4. 生成进化报告
5. 与记忆系统深度整合

作者: 雪子助手
版本: 2.0.0
日期: 2026-03-09
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

# 配置
MEMORY_DIR = Path("/Users/zhaoruicn/.openclaw/workspace/memory")
SKILLS_DIR = Path("/Users/zhaoruicn/.openclaw/workspace/skills")
EVOLUTION_FILE = MEMORY_DIR / "evolution" / "evolution_data.json"
LESSONS_FILE = MEMORY_DIR / "evolution" / "lessons_learned.json"
IMPROVEMENTS_FILE = MEMORY_DIR / "evolution" / "improvements_tracking.json"

# 确保目录存在
EVOLUTION_FILE.parent.mkdir(exist_ok=True)


@dataclass
class Lesson:
    """学习点"""
    id: str
    date: str
    category: str  # error, success, insight, pattern
    trigger: str
    lesson: str
    solution: str
    applied: bool
    evidence: str  # 来自哪个记忆文件
    effectiveness: float  # 0-1


@dataclass
class Improvement:
    """改进措施"""
    id: str
    lesson_id: str
    action: str
    target: str
    start_date: str
    expected_completion: str
    status: str  # planned, in_progress, completed, abandoned
    progress: float  # 0-1
    verification_method: str
    actual_result: str


class SelfEvolutionSystem:
    """自我进化系统 v2.0"""
    
    def __init__(self):
        self.memory_dir = MEMORY_DIR
        self.skills_dir = SKILLS_DIR
        self.lessons: List[Lesson] = []
        self.improvements: List[Improvement] = []
        self._load_data()
    
    def _load_data(self):
        """加载进化数据"""
        # 加载学习点
        if LESSONS_FILE.exists():
            try:
                with open(LESSONS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.lessons = [Lesson(**l) for l in data.get("lessons", [])]
            except:
                self.lessons = []
        
        # 加载改进措施
        if IMPROVEMENTS_FILE.exists():
            try:
                with open(IMPROVEMENTS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.improvements = [Improvement(**i) for i in data.get("improvements", [])]
            except:
                self.improvements = []
    
    def _save_data(self):
        """保存进化数据"""
        # 保存学习点
        lessons_data = {
            "timestamp": datetime.now().isoformat(),
            "lessons": [asdict(l) for l in self.lessons]
        }
        with open(LESSONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(lessons_data, f, ensure_ascii=False, indent=2)
        
        # 保存改进措施
        improvements_data = {
            "timestamp": datetime.now().isoformat(),
            "improvements": [asdict(i) for i in self.improvements]
        }
        with open(IMPROVEMENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(improvements_data, f, ensure_ascii=False, indent=2)
    
    def extract_lessons_from_memory(self):
        """从记忆自动提取学习点"""
        print("🔍 从记忆提取学习点...")
        
        new_lessons = 0
        
        # 扫描记忆文件
        for file_path in self.memory_dir.glob("2026-*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取日期
                date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', file_path.name)
                date = date_match.group(0) if date_match else datetime.now().strftime('%Y-%m-%d')
                
                # 1. 提取错误/教训
                error_patterns = [
                    r'(?:错误|问题|故障|失败|bug).*?[:：]\s*(.+?)(?=\n|$)',
                    r'(?:教训|反思|总结).*?[:：]\s*(.+?)(?=\n|$)',
                ]
                
                for pattern in error_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                    for match in matches:
                        lesson_text = match.strip()[:200]
                        if len(lesson_text) < 10:
                            continue
                        
                        # 生成ID
                        lesson_id = f"lesson-{date}-{hash(lesson_text) % 10000:04d}"
                        
                        # 检查是否已存在
                        if any(l.id == lesson_id for l in self.lessons):
                            continue
                        
                        # 提取解决方案
                        solution = ""
                        solution_match = re.search(r'(?:解决|方案|改进|修复).*?[:：]\s*(.+?)(?=\n|$)', content)
                        if solution_match:
                            solution = solution_match.group(1).strip()[:200]
                        
                        lesson = Lesson(
                            id=lesson_id,
                            date=date,
                            category="error",
                            trigger=lesson_text[:100],
                            lesson=lesson_text,
                            solution=solution,
                            applied=False,
                            evidence=file_path.name,
                            effectiveness=0.0
                        )
                        
                        self.lessons.append(lesson)
                        new_lessons += 1
                
                # 2. 提取成功模式
                success_patterns = [
                    r'(?:成功|完成|达成).*?[:：]\s*(.+?)(?=\n|$)',
                ]
                
                for pattern in success_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                    for match in matches[:2]:  # 限制数量
                        success_text = match.strip()[:200]
                        if len(success_text) < 10:
                            continue
                        
                        lesson_id = f"success-{date}-{hash(success_text) % 10000:04d}"
                        
                        if any(l.id == lesson_id for l in self.lessons):
                            continue
                        
                        lesson = Lesson(
                            id=lesson_id,
                            date=date,
                            category="success",
                            trigger=success_text[:100],
                            lesson=success_text,
                            solution="",
                            applied=True,
                            evidence=file_path.name,
                            effectiveness=1.0
                        )
                        
                        self.lessons.append(lesson)
                        new_lessons += 1
                        
            except Exception as e:
                print(f"  ⚠️ 处理 {file_path.name} 失败: {str(e)}")
        
        if new_lessons > 0:
            self._save_data()
        
        print(f"  提取了 {new_lessons} 个新学习点")
        return new_lessons
    
    def create_improvement_plan(self, lesson_id: str) -> Optional[Improvement]:
        """为学习点创建改进计划"""
        lesson = next((l for l in self.lessons if l.id == lesson_id), None)
        if not lesson:
            return None
        
        # 已应用的学习点不需要改进计划
        if lesson.applied:
            return None
        
        # 生成改进措施
        improvement_id = f"imp-{lesson_id}"
        
        action = f"改进: {lesson.lesson[:50]}..."
        if lesson.solution:
            action = lesson.solution[:100]
        
        improvement = Improvement(
            id=improvement_id,
            lesson_id=lesson_id,
            action=action,
            target="系统行为",
            start_date=datetime.now().strftime('%Y-%m-%d'),
            expected_completion=(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            status="planned",
            progress=0.0,
            verification_method="观察后续类似场景的处理",
            actual_result=""
        )
        
        self.improvements.append(improvement)
        self._save_data()
        
        return improvement
    
    def track_improvement_progress(self):
        """跟踪改进进度"""
        print("📊 跟踪改进进度...")
        
        updated = 0
        
        for imp in self.improvements:
            if imp.status == "completed":
                continue
            
            # 检查是否过期
            expected = datetime.strptime(imp.expected_completion, '%Y-%m-%d')
            if datetime.now() > expected and imp.status == "in_progress":
                imp.status = "abandoned"
                updated += 1
                continue
            
            # 根据相关学习点的新记录评估效果
            lesson = next((l for l in self.lessons if l.id == imp.lesson_id), None)
            if lesson and lesson.category == "error":
                # 检查是否有同类错误再次发生
                similar_errors = [
                    l for l in self.lessons
                    if l.category == "error" 
                    and l.date > imp.start_date
                    and l.trigger == lesson.trigger
                ]
                
                if not similar_errors:
                    # 没有再次发生，改进有效
                    imp.status = "completed"
                    imp.progress = 1.0
                    lesson.effectiveness = 1.0
                    lesson.applied = True
                    updated += 1
                else:
                    # 再次发生，改进无效
                    imp.progress = 0.3
                    lesson.effectiveness = 0.2
        
        if updated > 0:
            self._save_data()
        
        print(f"  更新了 {updated} 个改进措施状态")
    
    def generate_evolution_report(self) -> Dict:
        """生成进化报告"""
        # 统计
        total_lessons = len(self.lessons)
        applied_lessons = sum(1 for l in self.lessons if l.applied)
        
        total_improvements = len(self.improvements)
        completed = sum(1 for i in self.improvements if i.status == "completed")
        in_progress = sum(1 for i in self.improvements if i.status == "in_progress")
        abandoned = sum(1 for i in self.improvements if i.status == "abandoned")
        
        # 分类统计
        category_count = defaultdict(int)
        for l in self.lessons:
            category_count[l.category] += 1
        
        # 计算进化指数
        if total_lessons > 0:
            evolution_score = (applied_lessons / total_lessons * 0.5 + 
                             completed / max(total_improvements, 1) * 0.5)
        else:
            evolution_score = 0.0
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "evolution_score": round(evolution_score, 2),
            "summary": {
                "total_lessons": total_lessons,
                "applied_lessons": applied_lessons,
                "application_rate": round(applied_lessons / total_lessons * 100, 1) if total_lessons > 0 else 0,
                "total_improvements": total_improvements,
                "completed": completed,
                "in_progress": in_progress,
                "abandoned": abandoned
            },
            "category_distribution": dict(category_count),
            "recent_lessons": [
                {
                    "date": l.date,
                    "category": l.category,
                    "trigger": l.trigger[:50],
                    "applied": l.applied
                }
                for l in sorted(self.lessons, key=lambda x: x.date, reverse=True)[:5]
            ],
            "active_improvements": [
                {
                    "id": i.id,
                    "action": i.action[:50],
                    "progress": i.progress,
                    "status": i.status
                }
                for i in self.improvements if i.status in ["planned", "in_progress"]
            ][:5]
        }
        
        return report
    
    def generate_recommendations(self) -> List[Dict]:
        """生成进化建议"""
        recommendations = []
        
        # 1. 为未应用的学习点创建改进计划
        unapplied = [l for l in self.lessons if not l.applied and not any(i.lesson_id == l.id for i in self.improvements)]
        
        for lesson in unapplied[:3]:
            recommendations.append({
                "type": "create_improvement",
                "title": f"为学习点创建改进计划",
                "description": lesson.lesson[:80],
                "priority": "high" if lesson.category == "error" else "medium",
                "action": f"create_improvement_plan('{lesson.id}')"
            })
        
        # 2. 检查长期未完成的改进
        stale = [
            i for i in self.improvements
            if i.status == "in_progress"
            and (datetime.now() - datetime.strptime(i.start_date, '%Y-%m-%d')).days > 14
        ]
        
        if stale:
            recommendations.append({
                "type": "review_stale",
                "title": f"Review {len(stale)} 个停滞的改进措施",
                "description": "这些改进措施已进行超过14天",
                "priority": "medium",
                "action": "review_improvements()"
            })
        
        # 3. 高频率错误模式
        error_triggers = defaultdict(int)
        for l in self.lessons:
            if l.category == "error":
                error_triggers[l.trigger] += 1
        
        for trigger, count in error_triggers.items():
            if count >= 2:
                recommendations.append({
                    "type": "address_pattern",
                    "title": f"⚠️ 高频错误模式",
                    "description": f"'{trigger[:40]}' 已发生 {count} 次",
                    "priority": "high",
                    "action": "制定系统性改进方案"
                })
        
        return recommendations
    
    def run(self):
        """运行自我进化系统"""
        print("=" * 60)
        print("🧬 自我进化系统 v2.0")
        print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 1. 从记忆提取学习点
        new_lessons = self.extract_lessons_from_memory()
        
        # 2. 跟踪改进进度
        self.track_improvement_progress()
        
        # 3. 生成报告
        report = self.generate_evolution_report()
        
        # 4. 生成建议
        recommendations = self.generate_recommendations()
        
        # 打印报告
        print("\n" + "=" * 60)
        print("📊 进化报告")
        print("=" * 60)
        print(f"  🧬 进化指数: {report['evolution_score']:.2f}/1.0")
        print(f"\n  📚 学习点:")
        print(f"    总数: {report['summary']['total_lessons']}")
        print(f"    已应用: {report['summary']['applied_lessons']}")
        print(f"    应用率: {report['summary']['application_rate']}%")
        
        print(f"\n  🔧 改进措施:")
        print(f"    总数: {report['summary']['total_improvements']}")
        print(f"    已完成: {report['summary']['completed']}")
        print(f"    进行中: {report['summary']['in_progress']}")
        
        if report['recent_lessons']:
            print(f"\n  📖 最近学习点:")
            for i, l in enumerate(report['recent_lessons'][:3], 1):
                status = "✅" if l['applied'] else "⏳"
                print(f"    {i}. {status} [{l['category']}] {l['trigger'][:40]}...")
        
        if recommendations:
            print(f"\n  💡 进化建议:")
            for i, rec in enumerate(recommendations[:3], 1):
                emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec['priority'], "⚪")
                print(f"    {i}. {emoji} {rec['title']}")
        
        # 保存报告
        report_file = self.memory_dir / "evolution" / "evolution_report.json"
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n  📝 报告已保存: {report_file}")
        
        print("\n✅ 自我进化完成")
        
        return report


def main():
    """主函数"""
    system = SelfEvolutionSystem()
    report = system.run()
    return report


if __name__ == "__main__":
    main()
