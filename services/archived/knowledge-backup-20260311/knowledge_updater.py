#!/usr/bin/env python3
"""
Knowledge Updater - 知识更新检测
检测过时知识，提示更新
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

WORKSPACE = Path.home() / ".openclaw" / "workspace"
KNOWLEDGE_BASE = WORKSPACE / "knowledge-base"


class KnowledgeUpdater:
    """知识更新检测器"""
    
    def __init__(self):
        self.knowledge_base = KNOWLEDGE_BASE
        
    def check_outdated(self, days: int = 30) -> List[Dict]:
        """检查过时知识"""
        outdated = []
        
        for category in ['decisions', 'problems', 'projects']:
            category_dir = self.knowledge_base / category
            if not category_dir.exists():
                continue
                
            for file in category_dir.glob('*.md'):
                if file.name == 'README.md':
                    continue
                    
                stat = file.stat()
                mtime = datetime.fromtimestamp(stat.st_mtime)
                age = (datetime.now() - mtime).days
                
                if age > days:
                    content = file.read_text(encoding='utf-8')
                    
                    # 提取标题
                    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                    title = title_match.group(1) if title_match else file.stem
                    
                    # 检查是否有更新标记
                    has_update_note = '更新' in content or 'UPDATE' in content.upper()
                    
                    outdated.append({
                        'file': str(file),
                        'title': title,
                        'category': category,
                        'age_days': age,
                        'last_modified': mtime.isoformat(),
                        'needs_review': not has_update_note
                    })
                    
        return sorted(outdated, key=lambda x: x['age_days'], reverse=True)
        
    def generate_update_report(self) -> str:
        """生成更新报告"""
        outdated = self.check_outdated(days=30)
        
        if not outdated:
            return "✅ 所有知识都是最新的（30天内）"
            
        report = f"""# 📚 知识更新报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
需要审查: {len(outdated)} 条

## 过时知识清单

"""
        
        for item in outdated[:10]:  # 只显示前10条
            report += f"### {item['title']}\n\n"
            report += f"- 类别: {item['category']}\n"
            report += f"- 未更新: {item['age_days']} 天\n"
            report += f"- 文件: `{item['file']}`\n"
            if item['needs_review']:
                report += f"- ⚠️ 需要审查\n"
            report += "\n"
            
        return report
        
    def suggest_updates(self) -> List[Dict]:
        """建议更新"""
        suggestions = []
        
        # 检查决策是否有后续
        decisions_dir = self.knowledge_base / 'decisions'
        if decisions_dir.exists():
            for file in decisions_dir.glob('*.md'):
                content = file.read_text(encoding='utf-8')
                
                # 检查是否有TODO
                todos = re.findall(r'- \[ \] (.+)', content)
                if todos:
                    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                    title = title_match.group(1) if title_match else file.stem
                    
                    suggestions.append({
                        'type': 'decision',
                        'file': str(file),
                        'title': title,
                        'pending': todos,
                        'suggestion': f'决策"{title}"有{len(todos)}个待办事项未完成'
                    })
                    
        # 检查问题是否已解决
        problems_dir = self.knowledge_base / 'problems'
        if problems_dir.exists():
            for file in problems_dir.glob('*.md'):
                content = file.read_text(encoding='utf-8')
                
                # 如果没有解决方案标记
                if '✅ 已解决' not in content and '## 解决方案' not in content:
                    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                    title = title_match.group(1) if title_match else file.stem
                    
                    suggestions.append({
                        'type': 'problem',
                        'file': str(file),
                        'title': title,
                        'suggestion': f'问题"{title}"尚未标记为已解决'
                    })
                    
        return suggestions


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='知识更新检测')
    parser.add_argument('--check', '-c', action='store_true', help='检查过时知识')
    parser.add_argument('--suggest', '-s', action='store_true', help='生成更新建议')
    parser.add_argument('--days', '-d', type=int, default=30, help='天数阈值')
    
    args = parser.parse_args()
    
    updater = KnowledgeUpdater()
    
    if args.check:
        outdated = updater.check_outdated(args.days)
        print(f"发现 {len(outdated)} 条过时知识（>{args.days}天）")
        for item in outdated[:5]:
            print(f"  - {item['title']} ({item['age_days']}天)")
    elif args.suggest:
        suggestions = updater.suggest_updates()
        print(f"发现 {len(suggestions)} 条更新建议")
        for s in suggestions:
            print(f"  [{s['type']}] {s['suggestion']}")
    else:
        print(updater.generate_update_report())


if __name__ == "__main__":
    main()
