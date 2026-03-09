#!/usr/bin/env python3
"""
文档自动化系统 (Doc Automation)
功能：自动从代码生成文档、统一文档格式、维护技能包索引
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

SKILLS_DIR = Path("~/.openclaw/workspace/skills").expanduser()
DOC_INDEX_FILE = SKILLS_DIR / "INDEX.md"

class DocAutomationSystem:
    """文档自动化系统"""
    
    def __init__(self):
        pass
    
    def extract_skill_info(self, skill_dir: Path) -> Optional[Dict]:
        """从技能包提取信息"""
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            return None
        
        try:
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()
            
            info = {
                'name': skill_dir.name,
                'title': skill_dir.name,
                'description': '',
                'version': '1.0.0',
                'category': 'other'
            }
            
            # 提取标题
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                info['title'] = title_match.group(1).strip()
            
            # 提取描述
            desc_match = re.search(r'^description:\s*(.+)$', content, re.MULTILINE | re.IGNORECASE)
            if desc_match:
                info['description'] = desc_match.group(1).strip()
            else:
                # 尝试从第一段提取
                lines = content.split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('#') and not line.startswith('---'):
                        info['description'] = line.strip()[:100]
                        break
            
            # 提取版本
            version_match = re.search(r'version:\s*(\S+)', content)
            if version_match:
                info['version'] = version_match.group(1)
            
            # 分类
            name_lower = skill_dir.name.lower()
            if 'stock' in name_lower or 'finance' in name_lower:
                info['category'] = '股票/金融'
            elif 'memory' in name_lower or 'knowledge' in name_lower:
                info['category'] = '记忆/知识'
            elif 'system' in name_lower or 'backup' in name_lower or 'guard' in name_lower:
                info['category'] = '系统运维'
            elif 'file' in name_lower or 'doc' in name_lower or 'pdf' in name_lower:
                info['category'] = '文件/文档'
            elif 'data' in name_lower or 'chart' in name_lower:
                info['category'] = '数据处理'
            elif 'cron' in name_lower or 'monitor' in name_lower or 'dashboard' in name_lower:
                info['category'] = '系统管理'
            
            return info
            
        except Exception as e:
            print(f"  ⚠️ 解析 {skill_dir.name} 失败: {e}")
            return None
    
    def generate_skill_index(self):
        """生成技能包索引"""
        print("🔍 扫描技能包...")
        
        skills = []
        categories = {}
        
        # 扫描核心技能包
        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir() and skill_dir.name not in ['.git', 'archived', 'suites']:
                info = self.extract_skill_info(skill_dir)
                if info:
                    skills.append(info)
                    cat = info['category']
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(info)
        
        # 扫描套件
        suites_dir = SKILLS_DIR / "suites"
        if suites_dir.exists():
            for suite_dir in suites_dir.iterdir():
                if suite_dir.is_dir() and suite_dir.name not in ['README.md']:
                    info = self.extract_skill_info(suite_dir)
                    if info:
                        info['category'] = '套件'
                        skills.append(info)
        
        # 生成索引文档
        self.write_index_md(skills, categories)
        
        print(f"✅ 索引生成完成: {len(skills)} 个技能包")
        return skills
    
    def write_index_md(self, skills: List[Dict], categories: Dict):
        """写入索引文档"""
        content = f"""# 技能包索引

> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}
> 
> 此索引由文档自动化系统自动维护

## 统计

- **核心技能包**: {len([s for s in skills if s['category'] != '套件'])} 个
- **技能包套件**: {len([s for s in skills if s['category'] == '套件'])} 个
- **分类数量**: {len(categories)} 个

## 按分类浏览

"""
        
        # 按分类输出
        category_order = ['股票/金融', '记忆/知识', '系统运维', '文件/文档', '数据处理', '系统管理', '套件', '其他']
        
        for cat in category_order:
            if cat in categories:
                content += f"### {cat}\n\n"
                for skill in sorted(categories[cat], key=lambda x: x['name']):
                    content += f"- **{skill['name']}** - {skill['description']}\n"
                content += "\n"
        
        # 完整列表
        content += "## 完整列表\n\n"
        content += "| 技能包 | 描述 | 版本 | 分类 |\n"
        content += "|--------|------|------|------|\n"
        
        for skill in sorted(skills, key=lambda x: x['name']):
            desc = skill['description'][:50] + '...' if len(skill['description']) > 50 else skill['description']
            content += f"| {skill['name']} | {desc} | {skill['version']} | {skill['category']} |\n"
        
        content += """
## 使用说明

### 快速查找
```bash
# 按分类查找技能包
grep "系统运维" ~/.openclaw/workspace/skills/INDEX.md
```

### 更新索引
```bash
cd ~/.openclaw/workspace/skills
doc_automation.py --update-index
```

---
*此文件由文档自动化系统自动生成，请勿手动修改*
"""
        
        with open(DOC_INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 索引已保存: {DOC_INDEX_FILE}")
    
    def check_doc_quality(self):
        """检查文档质量"""
        print("🔍 检查文档质量...")
        
        issues = []
        
        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir() and skill_dir.name not in ['.git', 'archived']:
                skill_md = skill_dir / "SKILL.md"
                
                if not skill_md.exists():
                    issues.append({
                        'skill': skill_dir.name,
                        'issue': '缺少 SKILL.md',
                        'severity': 'high'
                    })
                else:
                    with open(skill_md, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 检查必要内容
                    if not re.search(r'^#\s+', content, re.MULTILINE):
                        issues.append({
                            'skill': skill_dir.name,
                            'issue': '缺少标题',
                            'severity': 'medium'
                        })
                    
                    if len(content) < 100:
                        issues.append({
                            'skill': skill_dir.name,
                            'issue': '文档内容过少',
                            'severity': 'low'
                        })
        
        if issues:
            print(f"⚠️ 发现 {len(issues)} 个问题:")
            for issue in issues:
                emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(issue['severity'], '⚪')
                print(f"  {emoji} {issue['skill']}: {issue['issue']}")
        else:
            print("✅ 所有文档质量良好")
        
        return issues
    
    def run(self):
        """运行文档自动化"""
        print("=" * 60)
        print("📝 文档自动化系统")
        print("=" * 60)
        
        # 1. 生成索引
        self.generate_skill_index()
        
        # 2. 检查质量
        self.check_doc_quality()
        
        print("\n✅ 文档自动化完成")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='文档自动化系统')
    parser.add_argument('--update-index', action='store_true', help='更新技能包索引')
    parser.add_argument('--check-quality', action='store_true', help='检查文档质量')
    
    args = parser.parse_args()
    
    system = DocAutomationSystem()
    
    if args.update_index:
        system.generate_skill_index()
    elif args.check_quality:
        system.check_doc_quality()
    else:
        system.run()

if __name__ == '__main__':
    main()
