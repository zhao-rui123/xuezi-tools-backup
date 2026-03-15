#!/usr/bin/env python3
"""
Action Service - 任务生成器
扫描知识库，生成可执行任务
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

WORKSPACE = Path.home() / ".openclaw" / "workspace"
KNOWLEDGE_BASE = WORKSPACE / "knowledge-base"


class TaskGenerator:
    """任务生成器"""
    
    def __init__(self, workspace: Optional[Path] = None):
        self.workspace = workspace or WORKSPACE
        self.knowledge_base = self.workspace / "knowledge-base"
        self.tasks = []
        
    def scan_decisions(self) -> List[Dict]:
        """扫描决策目录，找出未完成的决策"""
        decisions_dir = self.knowledge_base / "decisions"
        pending_decisions = []
        
        if not decisions_dir.exists():
            return pending_decisions
            
        for file in decisions_dir.glob("*.md"):
            if file.name == "README.md":
                continue
                
            content = file.read_text(encoding='utf-8')
            
            # 检查是否有待办事项
            if "- [ ]" in content or "TODO" in content.upper():
                # 提取标题
                title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else file.stem
                
                # 提取待办
                todos = re.findall(r'- \[ \] (.+)$', content, re.MULTILINE)
                
                pending_decisions.append({
                    "type": "decision",
                    "source": str(file),
                    "title": title,
                    "todos": todos,
                    "created": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                })
                
        return pending_decisions
        
    def scan_problems(self) -> List[Dict]:
        """扫描问题目录，找出待解决的问题"""
        problems_dir = self.knowledge_base / "problems"
        pending_problems = []
        
        if not problems_dir.exists():
            return pending_problems
            
        for file in problems_dir.glob("*.md"):
            if file.name == "README.md":
                continue
                
            content = file.read_text(encoding='utf-8')
            
            # 检查是否已解决
            if "✅ 已解决" not in content and "## 解决方案" not in content:
                title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else file.stem
                
                pending_problems.append({
                    "type": "problem",
                    "source": str(file),
                    "title": title,
                    "created": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                })
                
        return pending_problems
        
    def scan_projects(self) -> List[Dict]:
        """扫描项目目录，找出需要更新的项目"""
        projects_dir = self.knowledge_base / "projects"
        active_projects = []
        
        if not projects_dir.exists():
            return active_projects
            
        for project_dir in projects_dir.iterdir():
            if not project_dir.is_dir():
                continue
                
            readme = project_dir / "README.md"
            if not readme.exists():
                continue
                
            content = readme.read_text(encoding='utf-8')
            
            # 检查是否有待办或最近未更新
            has_todos = "- [ ]" in content
            
            # 检查最后更新时间
            last_update = datetime.fromtimestamp(readme.stat().st_mtime)
            days_since_update = (datetime.now() - last_update).days
            
            if has_todos or days_since_update > 7:
                title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else project_dir.name
                
                todos = re.findall(r'- \[ \] (.+)$', content, re.MULTILINE)
                
                active_projects.append({
                    "type": "project",
                    "source": str(readme),
                    "title": title,
                    "todos": todos,
                    "days_since_update": days_since_update,
                    "last_update": last_update.isoformat()
                })
                
        return active_projects
        
    def generate_tasks(self) -> List[Dict]:
        """生成任务列表"""
        self.tasks = []
        
        # 扫描各目录
        decisions = self.scan_decisions()
        problems = self.scan_problems()
        projects = self.scan_projects()
        
        # 合并任务
        for item in decisions:
            for todo in item.get("todos", []):
                self.tasks.append({
                    "id": f"dec-{len(self.tasks):03d}",
                    "type": "决策跟进",
                    "title": todo,
                    "source": item["source"],
                    "priority": "high",
                    "created": item["created"]
                })
                
        for item in problems:
            self.tasks.append({
                "id": f"prb-{len(self.tasks):03d}",
                "type": "问题解决",
                "title": item["title"],
                "source": item["source"],
                "priority": "high",
                "created": item["created"]
            })
            
        for item in projects:
            for todo in item.get("todos", []):
                self.tasks.append({
                    "id": f"prj-{len(self.tasks):03d}",
                    "type": "项目任务",
                    "title": todo,
                    "source": item["source"],
                    "priority": "medium" if item["days_since_update"] < 14 else "high",
                    "created": item["last_update"]
                })
                
        # 按优先级排序
        priority_order = {"high": 0, "medium": 1, "low": 2}
        self.tasks.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        return self.tasks
        
    def export_tasks(self, output_file: Optional[Path] = None) -> str:
        """导出任务列表"""
        tasks = self.generate_tasks()
        
        if not output_file:
            output_file = self.workspace / "memory" / "pending_tasks.json"
            
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "generated_at": datetime.now().isoformat(),
            "total_tasks": len(tasks),
            "tasks": tasks
        }
        
        output_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        
        return str(output_file)
        
    def generate_markdown_report(self) -> str:
        """生成Markdown格式的任务报告"""
        tasks = self.generate_tasks()
        
        report = f"""# 可执行任务列表

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
任务总数: {len(tasks)}

"""
        
        if not tasks:
            report += "✅ 当前没有待办任务\n"
            return report
            
        # 按类型分组
        by_type = {}
        for task in tasks:
            t = task["type"]
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(task)
            
        for type_name, type_tasks in by_type.items():
            report += f"\n## {type_name} ({len(type_tasks)}项)\n\n"
            for task in type_tasks:
                priority_emoji = "🔴" if task["priority"] == "high" else "🟡" if task["priority"] == "medium" else "🟢"
                report += f"{priority_emoji} **{task['title']}**\n"
                report += f"   - ID: {task['id']}\n"
                report += f"   - 来源: {task['source']}\n\n"
                
        return report


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='任务生成器')
    parser.add_argument('--workspace', '-w', help='工作空间路径')
    parser.add_argument('--export', '-e', help='导出JSON文件路径')
    parser.add_argument('--report', '-r', action='store_true', help='生成报告')
    
    args = parser.parse_args()
    
    workspace = Path(args.workspace) if args.workspace else None
    generator = TaskGenerator(workspace)
    
    if args.report:
        print(generator.generate_markdown_report())
    else:
        output = generator.export_tasks(Path(args.export) if args.export else None)
        print(f"✅ 任务已导出: {output}")
        print(f"📊 共生成 {len(generator.tasks)} 个任务")


if __name__ == "__main__":
    main()
