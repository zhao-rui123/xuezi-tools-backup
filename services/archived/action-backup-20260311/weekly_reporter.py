#!/usr/bin/env python3
"""
Action Service - 周报生成器
生成周报并发送飞书
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple

WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
KNOWLEDGE_BASE = WORKSPACE / "knowledge-base"


class WeeklyReporter:
    """周报生成器"""
    
    def __init__(self, workspace: Optional[Path] = None):
        self.workspace = workspace or WORKSPACE
        self.memory_dir = self.workspace / "memory"
        self.knowledge_base = self.workspace / "knowledge-base"
        
    def get_week_range(self) -> Tuple[datetime, datetime]:
        """获取本周时间范围"""
        today = datetime.now()
        # 本周一
        monday = today - timedelta(days=today.weekday())
        monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
        # 本周日
        sunday = monday + timedelta(days=6, hours=23, minutes=59)
        return monday, sunday
        
    def analyze_memory_files(self, start: datetime, end: datetime) -> Dict:
        """分析本周记忆文件"""
        stats = {
            "total_days": 0,
            "total_entries": 0,
            "topics": {},
            "decisions": [],
            "problems_solved": []
        }
        
        current = start
        while current <= end:
            memory_file = self.memory_dir / f"{current.strftime('%Y-%m-%d')}.md"
            
            if memory_file.exists():
                stats["total_days"] += 1
                content = memory_file.read_text(encoding='utf-8')
                
                # 统计条目数（## 标题）
                entries = re.findall(r'^## ', content, re.MULTILINE)
                stats["total_entries"] += len(entries)
                
                # 提取主题（简单关键词匹配）
                topics = self._extract_topics(content)
                for topic in topics:
                    stats["topics"][topic] = stats["topics"].get(topic, 0) + 1
                    
                # 提取决策
                decisions = re.findall(r'决策.*?:\s*(.+)', content, re.IGNORECASE)
                stats["decisions"].extend(decisions)
                
                # 提取解决的问题
                solved = re.findall(r'修复.*?:\s*(.+)|解决.*?:\s*(.+)', content)
                for s in solved:
                    stats["problems_solved"].append(s[0] or s[1])
                    
            current += timedelta(days=1)
            
        return stats
        
    def _extract_topics(self, content: str) -> List[str]:
        """提取主题关键词"""
        topics = []
        keywords = {
            "开发": ["开发", "代码", "脚本", "技能包"],
            "系统": ["系统", "OpenClaw", "备份", "配置"],
            "项目": ["项目", "储能", "股票", "小龙虾"],
            "问题": ["修复", "解决", "bug", "错误"],
            "学习": ["学习", "分析", "研究"]
        }
        
        for topic, words in keywords.items():
            for word in words:
                if word in content:
                    topics.append(topic)
                    break
                    
        return list(set(topics))
        
    def get_pending_tasks(self) -> List[Dict]:
        """获取待办任务"""
        tasks_file = self.memory_dir / "pending_tasks.json"
        
        if not tasks_file.exists():
            return []
            
        try:
            data = json.loads(tasks_file.read_text(encoding='utf-8'))
            return data.get("tasks", [])
        except:
            return []
            
    def analyze_knowledge_growth(self) -> Dict:
        """分析知识库增长"""
        week_ago = datetime.now() - timedelta(days=7)
        
        growth = {
            "decisions": 0,
            "problems": 0,
            "projects": 0,
            "learnings": 0
        }
        
        for category in ["decisions", "problems", "projects", "learnings"]:
            dir_path = self.knowledge_base / category
            if not dir_path.exists():
                continue
                
            for file in dir_path.glob("*.md"):
                if file.stat().st_mtime > week_ago.timestamp():
                    growth[category] += 1
                    
        return growth
        
    def generate_weekly_report(self) -> str:
        """生成周报"""
        monday, sunday = self.get_week_range()
        
        # 收集数据
        memory_stats = self.analyze_memory_files(monday, sunday)
        pending_tasks = self.get_pending_tasks()
        knowledge_growth = self.analyze_knowledge_growth()
        
        # 生成报告
        report = f"""# 📊 周报 ({monday.strftime('%m/%d')} - {sunday.strftime('%m/%d')})

## 📈 本周概览

| 指标 | 数值 |
|------|------|
| 活跃天数 | {memory_stats['total_days']} 天 |
| 记录条目 | {memory_stats['total_entries']} 条 |
| 重要决策 | {len(memory_stats['decisions'])} 个 |
| 问题解决 | {len(memory_stats['problems_solved'])} 个 |

## 📚 知识库增长

| 类别 | 新增 |
|------|------|
| 决策记录 | {knowledge_growth['decisions']} |
| 问题方案 | {knowledge_growth['problems']} |
| 项目文档 | {knowledge_growth['projects']} |
| 学习项 | {knowledge_growth['learnings']} |

## 🏷️ 本周主题

"""
        
        # 主题排序
        sorted_topics = sorted(memory_stats['topics'].items(), key=lambda x: x[1], reverse=True)
        for topic, count in sorted_topics[:5]:
            report += f"- **{topic}**: {count} 次\n"
            
        # 重要决策
        if memory_stats['decisions']:
            report += "\n## ✅ 重要决策\n\n"
            for decision in memory_stats['decisions'][:5]:
                report += f"- {decision}\n"
                
        # 解决的问题
        if memory_stats['problems_solved']:
            report += "\n## 🔧 解决的问题\n\n"
            for problem in memory_stats['problems_solved'][:5]:
                report += f"- {problem}\n"
                
        # 下周任务
        if pending_tasks:
            report += f"\n## 📋 下周任务 ({len(pending_tasks)}项)\n\n"
            
            # 按优先级分组
            high_priority = [t for t in pending_tasks if t.get("priority") == "high"][:3]
            medium_priority = [t for t in pending_tasks if t.get("priority") == "medium"][:3]
            
            if high_priority:
                report += "### 🔴 高优先级\n\n"
                for task in high_priority:
                    report += f"- **{task['title']}** ({task['type']})\n"
                    
            if medium_priority:
                report += "\n### 🟡 中优先级\n\n"
                for task in medium_priority:
                    report += f"- {task['title']} ({task['type']})\n"
                    
        report += f"\n---\n*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"
        
        return report
        
    def save_report(self, report: str) -> Path:
        """保存周报"""
        reports_dir = self.memory_dir / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        filename = f"weekly-report-{datetime.now().strftime('%Y%m%d')}.md"
        report_file = reports_dir / filename
        
        report_file.write_text(report, encoding='utf-8')
        
        return report_file
        
    def send_to_feishu(self, report: str) -> bool:
        """发送飞书通知"""
        try:
            # 简化版报告（飞书消息长度限制）
            lines = report.split('\n')
            summary = []
            
            for line in lines:
                if line.startswith('# ') or line.startswith('## ') or line.startswith('### '):
                    summary.append(line)
                elif '|' in line and '指标' not in line and '---' not in line:
                    summary.append(line)
                elif line.startswith('- **') or line.startswith('### '):
                    summary.append(line)
                    
                if len(summary) > 30:  # 限制长度
                    summary.append("\n... (完整报告见文件)")
                    break
                    
            message = '\n'.join(summary)
            
            # 调用 broadcaster.py 发送
            import subprocess
            result = subprocess.run(
                [
                    "python3",
                    str(self.workspace / "agents/kilo/broadcaster.py"),
                    "--task", "send",
                    "--message", message,
                    "--target", "group"
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ 发送飞书失败: {e}")
            return False


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='周报生成器')
    parser.add_argument('--workspace', '-w', help='工作空间路径')
    parser.add_argument('--save', '-s', action='store_true', help='保存到文件')
    parser.add_argument('--send', action='store_true', help='发送到飞书')
    parser.add_argument('--output', '-o', help='输出文件路径')
    
    args = parser.parse_args()
    
    workspace = Path(args.workspace) if args.workspace else None
    reporter = WeeklyReporter(workspace)
    
    # 生成报告
    report = reporter.generate_weekly_report()
    
    if args.output:
        Path(args.output).write_text(report, encoding='utf-8')
        print(f"✅ 报告已保存: {args.output}")
    elif args.save:
        report_file = reporter.save_report(report)
        print(f"✅ 报告已保存: {report_file}")
    else:
        print(report)
        
    if args.send:
        if reporter.send_to_feishu(report):
            print("✅ 已发送到飞书")
        else:
            print("❌ 发送飞书失败")


if __name__ == "__main__":
    main()
