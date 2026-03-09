#!/usr/bin/env python3
"""
数据可视化看板 (Data Dashboard)
功能：展示记忆系统、自我进化、技能包使用等统计数据
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

MEMORY_DIR = Path("~/.openclaw/workspace/memory").expanduser()
SKILLS_DIR = Path("~/.openclaw/workspace/skills").expanduser()
DASHBOARD_DIR = Path("~/.openclaw/workspace/dashboard").expanduser()

class DataDashboard:
    """数据可视化看板"""
    
    def __init__(self):
        DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    
    def generate_dashboard(self):
        """生成看板报告"""
        print("=" * 80)
        print("📊 智能助手数据看板")
        print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        report = []
        
        # 1. 记忆系统统计
        report.append(self.get_memory_stats())
        
        # 2. 自我进化统计
        report.append(self.get_evolution_stats())
        
        # 3. 技能包统计
        report.append(self.get_skills_stats())
        
        # 4. 系统健康度
        report.append(self.get_health_score())
        
        # 保存HTML报告
        self.save_html_report(report)
        
        return report
    
    def get_memory_stats(self) -> Dict:
        """记忆系统统计"""
        print("\n📚 记忆系统统计")
        print("-" * 80)
        
        stats = {
            'title': '记忆系统',
            'total_memories': 0,
            'memory_by_month': {},
            'avg_importance': 0,
            'knowledge_entities': 0,
            'knowledge_relations': 0
        }
        
        # 统计记忆文件
        if MEMORY_DIR.exists():
            memory_files = list(MEMORY_DIR.glob("2026-*.md"))
            stats['total_memories'] = len(memory_files)
            
            # 按月统计
            for f in memory_files:
                month = f.stem[:7]  # 2026-03
                stats['memory_by_month'][month] = stats['memory_by_month'].get(month, 0) + 1
            
            print(f"  总记忆数: {stats['total_memories']}")
            print(f"  月度分布: {stats['memory_by_month']}")
        
        # 统计知识图谱
        kg_file = MEMORY_DIR / "knowledge_graph" / "graph.json"
        if kg_file.exists():
            with open(kg_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stats['knowledge_entities'] = len(data.get('entities', {}))
                stats['knowledge_relations'] = len(data.get('relations', []))
            print(f"  知识实体: {stats['knowledge_entities']}")
            print(f"  知识关系: {stats['knowledge_relations']}")
        
        return stats
    
    def get_evolution_stats(self) -> Dict:
        """自我进化统计"""
        print("\n🧬 自我进化统计")
        print("-" * 80)
        
        stats = {
            'title': '自我进化',
            'total_lessons': 0,
            'applied_lessons': 0,
            'evolution_score': 0,
            'improvements': 0
        }
        
        evolution_file = MEMORY_DIR / "evolution" / "evolution_data.json"
        if evolution_file.exists():
            with open(evolution_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stats['total_lessons'] = len(data.get('lessons', []))
                stats['improvements'] = len(data.get('improvements', []))
                # 计算应用率
                lessons = data.get('lessons', [])
                if lessons:
                    stats['applied_lessons'] = sum(1 for l in lessons if l.get('applied'))
                    stats['evolution_score'] = round(stats['applied_lessons'] / len(lessons), 2)
        
        print(f"  学习点: {stats['total_lessons']}")
        print(f"  已应用: {stats['applied_lessons']}")
        print(f"  进化指数: {stats['evolution_score']:.2f}")
        print(f"  改进措施: {stats['improvements']}")
        
        return stats
    
    def get_skills_stats(self) -> Dict:
        """技能包统计"""
        print("\n🛠️  技能包统计")
        print("-" * 80)
        
        stats = {
            'title': '技能包',
            'total_skills': 0,
            'active_skills': 0,
            'archived_skills': 0,
            'suites': 0,
            'by_category': defaultdict(int)
        }
        
        if SKILLS_DIR.exists():
            # 核心技能包
            skills = [d for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith('.')]
            
            # 排除套件和归档
            active_skills = [s for s in skills if s.name not in ['suites', 'archived']]
            stats['total_skills'] = len(active_skills)
            
            # 统计分类
            for skill in active_skills:
                skill_file = skill / "SKILL.md"
                if skill_file.exists():
                    # 简单分类
                    if 'stock' in skill.name:
                        stats['by_category']['股票'] += 1
                    elif 'system' in skill.name:
                        stats['by_category']['系统'] += 1
                    elif 'memory' in skill.name or 'knowledge' in skill.name:
                        stats['by_category']['记忆'] += 1
                    else:
                        stats['by_category']['其他'] += 1
            
            # 套件
            suites_dir = SKILLS_DIR / "suites"
            if suites_dir.exists():
                stats['suites'] = len([d for d in suites_dir.iterdir() if d.is_dir()])
            
            # 归档
            archived_dir = SKILLS_DIR / "archived"
            if archived_dir.exists():
                stats['archived_skills'] = len([d for d in archived_dir.iterdir() if d.is_dir()])
            
            print(f"  核心技能包: {stats['total_skills']}")
            print(f"  技能包套件: {stats['suites']}")
            print(f"  已归档: {stats['archived_skills']}")
            print(f"  分类分布: {dict(stats['by_category'])}")
        
        return stats
    
    def get_health_score(self) -> Dict:
        """系统健康度评分"""
        print("\n🏥 系统健康度")
        print("-" * 80)
        
        scores = []
        
        # 1. 记忆系统健康度
        memory_score = 0
        if (MEMORY_DIR / "memory_scores.json").exists():
            memory_score = 90  # 有评分系统
        else:
            memory_score = 70
        scores.append(('记忆系统', memory_score))
        
        # 2. 备份健康度
        backup_score = 0
        backup_dir = Path("/Volumes/cu/ocu/memory")
        if backup_dir.exists():
            latest = max(backup_dir.glob("*"), key=lambda x: x.stat().st_mtime)
            days_since = (datetime.now() - datetime.fromtimestamp(latest.stat().st_mtime)).days
            backup_score = 100 if days_since < 1 else max(0, 100 - days_since * 10)
        else:
            backup_score = 50
        scores.append(('备份系统', backup_score))
        
        # 3. 定时任务健康度
        cron_score = 80  # 假设正常
        scores.append(('定时任务', cron_score))
        
        # 计算总分
        total_score = sum(s[1] for s in scores) / len(scores)
        
        print(f"  记忆系统: {scores[0][1]}分")
        print(f"  备份系统: {scores[1][1]}分")
        print(f"  定时任务: {scores[2][1]}分")
        print(f"  综合评分: {total_score:.1f}分")
        
        health_level = '优秀' if total_score >= 90 else '良好' if total_score >= 80 else '一般' if total_score >= 60 else '需改进'
        print(f"  健康等级: {health_level}")
        
        return {
            'title': '系统健康度',
            'total_score': round(total_score, 1),
            'health_level': health_level,
            'details': scores
        }
    
    def save_html_report(self, report: List[Dict]):
        """保存HTML报告"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>智能助手数据看板</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: #4CAF50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .card {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .card h2 {{ margin-top: 0; color: #333; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #4CAF50; }}
        .metric-label {{ color: #666; }}
        .health-excellent {{ color: #4CAF50; }}
        .health-good {{ color: #8BC34A; }}
        .health-fair {{ color: #FFC107; }}
        .health-poor {{ color: #F44336; }}
        .footer {{ text-align: center; color: #999; margin-top: 40px; padding: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 智能助手数据看板</h1>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
"""
        
        for section in report:
            html += f"""
        <div class="card">
            <h2>{section.get('title', '未知')}</h2>
"""
            for key, value in section.items():
                if key != 'title' and not isinstance(value, (dict, list)):
                    html += f"""
            <div class="metric">
                <div class="metric-value">{value}</div>
                <div class="metric-label">{key}</div>
            </div>
"""
            html += "</div>"
        
        html += f"""
        <div class="footer">
            <p>OpenClaw 智能助手系统 | 数据看板 v1.0</p>
        </div>
    </div>
</body>
</html>
"""
        
        report_file = DASHBOARD_DIR / f"dashboard_{datetime.now().strftime('%Y%m%d')}.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n📄 HTML报告已保存: {report_file}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='数据可视化看板')
    parser.add_argument('--generate', action='store_true', help='生成看板报告')
    parser.add_argument('--open', action='store_true', help='打开最新报告')
    
    args = parser.parse_args()
    
    dashboard = DataDashboard()
    
    if args.open:
        # 打开最新报告
        reports = sorted(DASHBOARD_DIR.glob("dashboard_*.html"))
        if reports:
            import subprocess
            subprocess.run(['open', str(reports[-1])])
        else:
            print("❌ 没有找到报告")
    else:
        dashboard.generate_dashboard()

if __name__ == '__main__':
    main()
