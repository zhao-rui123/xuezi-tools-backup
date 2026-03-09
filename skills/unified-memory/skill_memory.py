#!/usr/bin/env python3
"""
技能包记忆系统 (Skill Package Memory System)
第三阶段 - 生态融合

功能：
1. 记录每个技能包的使用频率
2. 自动优化技能包推荐
3. 技能包使用模式学习
4. 技能包效果评估

作者: 雪子助手
版本: 1.0.0
日期: 2026-03-09
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict

# 配置
SKILLS_DIR = Path("/Users/zhaoruicn/.openclaw/workspace/skills")
MEMORY_DIR = Path("/Users/zhaoruicn/.openclaw/workspace/memory")
SKILL_MEMORY_FILE = MEMORY_DIR / "skill_memory.json"


@dataclass
class SkillUsage:
    """技能包使用记录"""
    name: str
    path: str
    category: str
    usage_count: int = 0
    last_used: Optional[str] = None
    first_used: Optional[str] = None
    success_count: int = 0
    fail_count: int = 0
    avg_execution_time: float = 0.0
    user_rating: float = 0.0  # 1-5分
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class SkillPackageMemorySystem:
    """技能包记忆系统"""
    
    def __init__(self):
        self.skills_dir = SKILLS_DIR
        self.memory_dir = MEMORY_DIR
        self.skill_memory: Dict[str, SkillUsage] = {}
        self._load_memory()
    
    def _load_memory(self):
        """加载技能包记忆"""
        if SKILL_MEMORY_FILE.exists():
            try:
                with open(SKILL_MEMORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for name, skill_data in data.get("skills", {}).items():
                    self.skill_memory[name] = SkillUsage(**skill_data)
                    
            except Exception as e:
                print(f"  ⚠️ 加载技能包记忆失败: {str(e)}")
    
    def _save_memory(self):
        """保存技能包记忆"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "skills": {name: asdict(skill) for name, skill in self.skill_memory.items()}
        }
        
        with open(SKILL_MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def scan_skills(self):
        """扫描所有技能包"""
        print("🔍 扫描技能包...")
        
        skill_dirs = [d for d in self.skills_dir.iterdir() if d.is_dir()]
        
        for skill_dir in skill_dirs:
            skill_name = skill_dir.name
            
            # 检测技能包类别
            category = self._detect_category(skill_dir)
            
            # 检测标签
            tags = self._detect_tags(skill_dir)
            
            if skill_name not in self.skill_memory:
                # 新技能包
                self.skill_memory[skill_name] = SkillUsage(
                    name=skill_name,
                    path=str(skill_dir.relative_to(Path("/Users/zhaoruicn/.openclaw/workspace"))),
                    category=category,
                    tags=tags,
                    first_used=datetime.now().isoformat()
                )
            else:
                # 更新现有技能包信息
                skill = self.skill_memory[skill_name]
                skill.category = category
                skill.tags = tags
        
        print(f"  发现 {len(skill_dirs)} 个技能包")
        self._save_memory()
    
    def _detect_category(self, skill_dir: Path) -> str:
        """检测技能包类别"""
        skill_name = skill_dir.name.lower()
        
        # 根据名称判断
        if any(kw in skill_name for kw in ['stock', 'finance', 'calc', 'tax']):
            return "finance"
        elif any(kw in skill_name for kw in ['memory', 'knowledge', 'data']):
            return "data"
        elif any(kw in skill_name for kw in ['backup', 'guard', 'security', 'monitor']):
            return "ops"
        elif any(kw in skill_name for kw in ['feishu', 'telegram', 'discord', 'message']):
            return "communication"
        elif any(kw in skill_name for kw in ['chart', 'pdf', 'office', 'doc']):
            return "document"
        elif any(kw in skill_name for kw in ['agent', 'multi', 'team', 'orchestration']):
            return "agent"
        elif any(kw in skill_name for kw in ['web', 'crawler', 'scrap', 'fetch']):
            return "web"
        else:
            return "general"
    
    def _detect_tags(self, skill_dir: Path) -> List[str]:
        """检测技能包标签"""
        tags = []
        skill_name = skill_dir.name.lower()
        
        # 读取 SKILL.md
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            try:
                with open(skill_md, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取标签
                if 'finance' in content.lower() or '股票' in content:
                    tags.append("金融")
                if 'backup' in content.lower() or '备份' in content:
                    tags.append("备份")
                if 'memory' in content.lower() or '记忆' in content:
                    tags.append("记忆")
                if 'agent' in content.lower() or '智能体' in content:
                    tags.append("Agent")
                    
            except:
                pass
        
        return tags
    
    def record_usage(self, skill_name: str, success: bool = True, execution_time: float = 0.0):
        """记录技能包使用"""
        if skill_name not in self.skill_memory:
            # 自动注册新技能包
            skill_dir = self.skills_dir / skill_name
            if skill_dir.exists():
                self.scan_skills()
            else:
                return
        
        skill = self.skill_memory[skill_name]
        skill.usage_count += 1
        skill.last_used = datetime.now().isoformat()
        
        if success:
            skill.success_count += 1
        else:
            skill.fail_count += 1
        
        # 更新平均执行时间
        if execution_time > 0:
            total_time = skill.avg_execution_time * (skill.usage_count - 1) + execution_time
            skill.avg_execution_time = total_time / skill.usage_count
        
        self._save_memory()
    
    def rate_skill(self, skill_name: str, rating: float):
        """评价技能包"""
        if skill_name in self.skill_memory:
            # 简单平均
            skill = self.skill_memory[skill_name]
            if skill.user_rating == 0:
                skill.user_rating = rating
            else:
                skill.user_rating = (skill.user_rating + rating) / 2
            self._save_memory()
    
    def get_recommendations(self, context: str = "") -> List[Dict]:
        """推荐技能包"""
        recommendations = []
        
        # 1. 基于使用频率推荐
        popular_skills = sorted(
            self.skill_memory.items(),
            key=lambda x: x[1].usage_count,
            reverse=True
        )[:5]
        
        for name, skill in popular_skills:
            if skill.usage_count > 0:
                recommendations.append({
                    "name": name,
                    "reason": f"已使用 {skill.usage_count} 次",
                    "category": skill.category,
                    "priority": "high" if skill.usage_count > 5 else "medium",
                    "confidence": min(skill.usage_count / 10, 1.0)
                })
        
        # 2. 基于类别推荐
        if context:
            context_lower = context.lower()
            for name, skill in self.skill_memory.items():
                if skill.category in context_lower or any(tag in context_lower for tag in skill.tags):
                    if skill.usage_count == 0:  # 未使用过的
                        recommendations.append({
                            "name": name,
                            "reason": f"与'{context}'相关，未使用过",
                            "category": skill.category,
                            "priority": "medium",
                            "confidence": 0.7
                        })
        
        # 3. 推荐未使用的实用技能
        unused_useful = [
            (name, skill) for name, skill in self.skill_memory.items()
            if skill.usage_count == 0 and skill.category in ["ops", "backup", "security"]
        ]
        
        for name, skill in unused_useful[:3]:
            recommendations.append({
                "name": name,
                "reason": "运维类技能，建议了解",
                "category": skill.category,
                "priority": "low",
                "confidence": 0.5
            })
        
        # 去重并排序
        seen = set()
        unique_recs = []
        for rec in recommendations:
            if rec["name"] not in seen:
                seen.add(rec["name"])
                unique_recs.append(rec)
        
        return unique_recs[:10]
    
    def analyze_usage_patterns(self) -> Dict:
        """分析使用模式"""
        patterns = {
            "total_skills": len(self.skill_memory),
            "used_skills": sum(1 for s in self.skill_memory.values() if s.usage_count > 0),
            "unused_skills": sum(1 for s in self.skill_memory.values() if s.usage_count == 0),
            "category_usage": defaultdict(lambda: {"count": 0, "usage": 0}),
            "top_skills": [],
            "neglected_skills": []
        }
        
        for name, skill in self.skill_memory.items():
            # 类别统计
            patterns["category_usage"][skill.category]["count"] += 1
            patterns["category_usage"][skill.category]["usage"] += skill.usage_count
            
            # Top技能
            if skill.usage_count > 0:
                patterns["top_skills"].append({
                    "name": name,
                    "usage": skill.usage_count,
                    "success_rate": skill.success_count / skill.usage_count if skill.usage_count > 0 else 0
                })
            else:
                patterns["neglected_skills"].append(name)
        
        # 排序
        patterns["top_skills"].sort(key=lambda x: x["usage"], reverse=True)
        patterns["top_skills"] = patterns["top_skills"][:10]
        
        return patterns
    
    def generate_report(self) -> Dict:
        """生成技能包报告"""
        patterns = self.analyze_usage_patterns()
        recommendations = self.get_recommendations()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_skills": patterns["total_skills"],
                "used_skills": patterns["used_skills"],
                "usage_rate": round(patterns["used_skills"] / patterns["total_skills"] * 100, 1) if patterns["total_skills"] > 0 else 0
            },
            "category_breakdown": dict(patterns["category_usage"]),
            "top_skills": patterns["top_skills"],
            "neglected_skills": patterns["neglected_skills"][:10],
            "recommendations": recommendations[:5]
        }
        
        return report
    
    def run(self):
        """运行技能包记忆系统"""
        print("=" * 60)
        print("🛠️ 技能包记忆系统")
        print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 扫描技能包
        self.scan_skills()
        
        # 生成报告
        report = self.generate_report()
        
        # 打印报告
        print("\n" + "=" * 60)
        print("📊 技能包报告")
        print("=" * 60)
        print(f"  总技能包: {report['summary']['total_skills']}")
        print(f"  已使用: {report['summary']['used_skills']}")
        print(f"  使用率: {report['summary']['usage_rate']}%")
        
        print(f"\n  📦 类别分布:")
        for cat, data in sorted(report['category_breakdown'].items(), key=lambda x: x[1]['usage'], reverse=True):
            print(f"    {cat}: {data['count']}个 (使用{data['usage']}次)")
        
        if report['top_skills']:
            print(f"\n  🔥 热门技能:")
            for i, skill in enumerate(report['top_skills'][:5], 1):
                success_rate = skill['success_rate'] * 100
                print(f"    {i}. {skill['name']}: {skill['usage']}次 (成功率{success_rate:.0f}%)")
        
        if report['recommendations']:
            print(f"\n  💡 技能推荐:")
            for i, rec in enumerate(report['recommendations'][:3], 1):
                print(f"    {i}. {rec['name']} - {rec['reason']}")
        
        # 保存报告
        report_file = self.memory_dir / "skill_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n  📝 报告已保存: {report_file}")
        
        print("\n✅ 技能包记忆更新完成")
        
        return report


def main():
    """主函数"""
    system = SkillPackageMemorySystem()
    report = system.run()
    return report


if __name__ == "__main__":
    main()
