"""
增量代码审查模块
只审查Git变更部分，节省Token
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class CodeChange:
    """代码变更"""
    file_path: str
    status: str
    additions: int
    deletions: int
    diff_content: str
    old_content: str = ""
    new_content: str = ""

class IncrementalReviewer:
    """增量代码审查器"""

    def __init__(self, repo_path: str = None):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.review_prompt_template = """你是一个专业的代码审查专家。请审查以下代码变更。

文件: {file_path}
变更类型: {status}
新增行数: {additions}
删除行数: {deletions}

请检查以下方面:
1. 代码质量问题
2. 潜在bug
3. 安全漏洞
4. 性能问题
5. 代码风格

代码变更:
```{diff}
{diff_content}
```

请给出具体的改进建议。"""

    def get_changes(self, base: str = "HEAD~1", target: str = "HEAD") -> List[CodeChange]:
        """获取Git变更"""
        changes = []

        try:
            result = subprocess.run(
                ['git', 'diff', '--numstat', base, target],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )

            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                parts = line.split('\t')
                if len(parts) < 3:
                    continue

                additions = int(parts[0]) if parts[0] != '-' else 0
                deletions = int(parts[1]) if parts[1] != '-' else 0
                file_path = parts[2]

                status = self._get_file_status(file_path)

                diff_result = subprocess.run(
                    ['git', 'diff', base, '--', file_path],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )

                change = CodeChange(
                    file_path=file_path,
                    status=status,
                    additions=additions,
                    deletions=deletions,
                    diff_content=diff_result.stdout[:5000]
                )
                changes.append(change)

        except Exception as e:
            print(f"获取变更失败: {e}")

        return changes

    def _get_file_status(self, file_path: str) -> str:
        """获取文件状态"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain', '--', file_path],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            status_code = result.stdout[:2].strip()
            status_map = {
                'M': 'modified',
                'A': 'added',
                'D': 'deleted',
                'R': 'renamed',
                'C': 'copied'
            }
            return status_map.get(status_code, 'unknown')
        except:
            return 'unknown'

    def review_changes(self, changes: List[CodeChange]) -> Dict:
        """审查变更"""
        review_results = []

        for change in changes:
            if change.additions + change.deletions == 0:
                continue

            if change.additions + change.deletions > 500:
                issue = f"文件 {change.file_path} 变更过大({change.additions + change.deletions}行)，建议分批审查"
                review_results.append({
                    'file': change.file_path,
                    'status': 'warning',
                    'issue': issue
                })
                continue

            prompt = self.review_prompt_template.format(
                file_path=change.file_path,
                status=change.status,
                additions=change.additions,
                deletions=change.deletions,
                diff_content=change.diff_content[:3000]
            )

            review_results.append({
                'file': change.file_path,
                'status': change.status,
                'additions': change.additions,
                'deletions': change.deletions,
                'review_prompt': prompt
            })

        return {
            'total_files': len(changes),
            'total_additions': sum(c.additions for c in changes),
            'total_deletions': sum(c.deletions for c in changes),
            'reviews': review_results
        }

    def get_changed_files_only(self, base: str = "HEAD~1") -> List[str]:
        """只获取变更文件列表"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', base],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return [f for f in result.stdout.strip().split('\n') if f]
        except Exception as e:
            print(f"获取变更文件失败: {e}")
            return []

    def generate_summary(self, changes: List[CodeChange]) -> str:
        """生成变更摘要"""
        if not changes:
            return "无代码变更"

        lines = [
            "📝 代码变更摘要",
            "=" * 50,
            ""
        ]

        total_add = 0
        total_del = 0

        for change in changes:
            total_add += change.additions
            total_del += change.deletions

            emoji = {
                'modified': '📝',
                'added': '➕',
                'deleted': '🗑️',
                'renamed': '📦',
                'unknown': '❓'
            }.get(change.status, '❓')

            lines.append(f"{emoji} {change.file_path}")
            lines.append(f"   +{change.additions} -{change.deletions}")

        lines.append("")
        lines.append(f"总计: +{total_add} -{total_del} 行")

        return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='增量代码审查工具')
    parser.add_argument('--base', default='HEAD~1', help='基准版本')
    parser.add_argument('--target', default='HEAD', help='目标版本')
    parser.add_argument('--files-only', action='store_true', help='只显示变更文件')
    parser.add_argument('--summary', action='store_true', help='显示变更摘要')

    args = parser.parse_args()

    reviewer = IncrementalReviewer()

    if args.files_only:
        files = reviewer.get_changed_files_only(args.base)
        print("变更的文件:")
        for f in files:
            print(f"  - {f}")
    elif args.summary:
        changes = reviewer.get_changes(args.base, args.target)
        print(reviewer.generate_summary(changes))
    else:
        changes = reviewer.get_changes(args.base, args.target)
        result = reviewer.review_changes(changes)
        print(f"📊 变更统计:")
        print(f"   文件数: {result['total_files']}")
        print(f"   新增: {result['total_additions']} 行")
        print(f"   删除: {result['total_deletions']} 行")
        print()
        print("请使用 --review 参数进行详细审查")


if __name__ == '__main__':
    main()
