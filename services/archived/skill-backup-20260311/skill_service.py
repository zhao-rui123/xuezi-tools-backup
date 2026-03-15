#!/usr/bin/env python3
"""
Skill Service - 技能包管理服务
版本管理、依赖检查、自动审计
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

WORKSPACE = Path.home() / ".openclaw" / "workspace"
SKILLS_DIR = WORKSPACE / "skills"


class SkillService:
    """技能包管理服务"""
    
    def __init__(self, skills_dir: Optional[Path] = None):
        self.skills_dir = skills_dir or SKILLS_DIR
        
    def list_skills(self) -> List[Dict]:
        """列出所有技能包"""
        skills = []
        
        for item in self.skills_dir.iterdir():
            if not item.is_dir():
                continue
                
            skill_file = item / "SKILL.md"
            if not skill_file.exists():
                continue
                
            content = skill_file.read_text(encoding='utf-8')
            
            # 提取基本信息
            name = item.name
            version = self._extract_version(content)
            description = self._extract_description(content)
            
            # 检查文件数量
            file_count = len(list(item.rglob("*")))
            
            skills.append({
                "name": name,
                "version": version,
                "description": description[:100] + "..." if len(description) > 100 else description,
                "file_count": file_count,
                "has_skill_md": True,
                "path": str(item)
            })
            
        return sorted(skills, key=lambda x: x["name"])
        
    def _extract_version(self, content: str) -> str:
        """从SKILL.md提取版本"""
        match = re.search(r'[Vv]ersion[:\s]+([\d.]+)', content)
        return match.group(1) if match else "未指定"
        
    def _extract_description(self, content: str) -> str:
        """从SKILL.md提取描述"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 10:
                return line
        return "无描述"
        
    def check_dependencies(self, skill_name: str) -> Dict:
        """检查技能包依赖"""
        skill_dir = self.skills_dir / skill_name
        
        if not skill_dir.exists():
            return {"error": "技能包不存在"}
            
        deps = {
            "skill_name": skill_name,
            "dependencies": [],
            "referenced_by": []
        }
        
        # 检查SKILL.md中的依赖声明
        skill_file = skill_dir / "SKILL.md"
        if skill_file.exists():
            content = skill_file.read_text(encoding='utf-8')
            
            # 查找依赖声明
            dep_matches = re.findall(r'[Dd]epend.*?[:\s]+(.+)', content)
            for match in dep_matches:
                deps["dependencies"].extend([d.strip() for d in match.split(',')])
                
        # 检查哪些技能包引用了这个
        for other_skill in self.list_skills():
            if other_skill["name"] == skill_name:
                continue
                
            other_file = self.skills_dir / other_skill["name"] / "SKILL.md"
            if other_file.exists():
                content = other_file.read_text(encoding='utf-8')
                if skill_name in content:
                    deps["referenced_by"].append(other_skill["name"])
                    
        return deps
        
    def audit_skills(self) -> Dict:
        """审计所有技能包"""
        audit = {
            "total": 0,
            "healthy": 0,
            "issues": [],
            "categories": {}
        }
        
        for skill in self.list_skills():
            audit["total"] += 1
            
            issues = []
            
            # 检查SKILL.md
            skill_dir = self.skills_dir / skill["name"]
            skill_file = skill_dir / "SKILL.md"
            
            if not skill_file.exists():
                issues.append("缺少 SKILL.md")
            else:
                content = skill_file.read_text(encoding='utf-8')
                
                # 检查必要章节
                if "## " not in content:
                    issues.append("缺少章节结构")
                    
                # 检查版本
                if skill["version"] == "未指定":
                    issues.append("未指定版本")
                    
            # 检查脚本
            has_scripts = any((skill_dir / ext).exists() for ext in ["*.py", "*.sh"])
            if not has_scripts and skill["file_count"] < 3:
                issues.append("内容较少，可能不完整")
                
            # 分类
            category = self._categorize_skill(skill["name"], skill.get("description", ""))
            if category not in audit["categories"]:
                audit["categories"][category] = []
            audit["categories"][category].append(skill["name"])
            
            if issues:
                audit["issues"].append({
                    "skill": skill["name"],
                    "issues": issues
                })
            else:
                audit["healthy"] += 1
                
        return audit
        
    def _categorize_skill(self, name: str, description: str) -> str:
        """分类技能包"""
        text = (name + " " + description).lower()
        
        if any(k in text for k in ["memory", "knowledge", "learning"]):
            return "记忆知识"
        elif any(k in text for k in ["backup", "monitor", "maintenance", "guard"]):
            return "系统运维"
        elif any(k in text for k in ["stock", "finance", "calc"]):
            return "业务工具"
        elif any(k in text for k in ["feishu", "notify", "message"]):
            return "通知通讯"
        elif any(k in text for k in ["multi", "agent", "team"]):
            return "Agent协作"
        else:
            return "其他"
            
    def generate_changelog(self, skill_name: str) -> str:
        """生成变更日志"""
        skill_dir = self.skills_dir / skill_name
        
        if not skill_dir.exists():
            return "技能包不存在"
            
        # 使用git log生成changelog
        try:
            import subprocess
            result = subprocess.run(
                ["git", "log", "--oneline", "--", str(skill_dir)],
                cwd=WORKSPACE,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                commits = result.stdout.strip().split('\n')
                changelog = f"# {skill_name} 变更日志\n\n"
                
                for commit in commits[:20]:  # 最近20条
                    if commit:
                        changelog += f"- {commit}\n"
                        
                return changelog
            else:
                return "无法获取git历史"
        except:
            return "git命令失败"
            
    def export_audit_report(self) -> str:
        """导出审计报告"""
        audit = self.audit_skills()
        
        report = f"""# 📊 技能包审计报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 📈 统计概览

| 指标 | 数值 |
|------|------|
| 技能包总数 | {audit['total']} |
| 健康 | {audit['healthy']} |
| 有问题 | {len(audit['issues'])} |
| 健康率 | {audit['healthy']/audit['total']*100:.1f}% |

## 📂 分类统计

"""
        
        for category, skills in sorted(audit['categories'].items()):
            report += f"### {category} ({len(skills)}个)\n\n"
            for skill in skills:
                report += f"- {skill}\n"
            report += "\n"
            
        if audit['issues']:
            report += "## ⚠️ 问题列表\n\n"
            for item in audit['issues']:
                report += f"### {item['skill']}\n\n"
                for issue in item['issues']:
                    report += f"- {issue}\n"
                report += "\n"
                
        return report


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='技能包管理服务')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有技能包')
    parser.add_argument('--audit', '-a', action='store_true', help='审计技能包')
    parser.add_argument('--deps', '-d', help='检查指定技能包的依赖')
    parser.add_argument('--changelog', '-c', help='生成变更日志')
    parser.add_argument('--output', '-o', help='输出文件')
    
    args = parser.parse_args()
    
    service = SkillService()
    
    if args.list:
        skills = service.list_skills()
        output = f"# 技能包列表 ({len(skills)}个)\n\n"
        for skill in skills:
            output += f"## {skill['name']}\n"
            output += f"- 版本: {skill['version']}\n"
            output += f"- 描述: {skill['description']}\n"
            output += f"- 文件数: {skill['file_count']}\n\n"
    elif args.audit:
        output = service.export_audit_report()
    elif args.deps:
        output = json.dumps(service.check_dependencies(args.deps), ensure_ascii=False, indent=2)
    elif args.changelog:
        output = service.generate_changelog(args.changelog)
    else:
        parser.print_help()
        return
        
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"✅ 已保存: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
