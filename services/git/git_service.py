"""
Git Service - 语义提交模块

功能：
1. 分析变更内容，生成语义化提交信息（feat/fix/docs/style/refactor）
2. 生成变更摘要
3. 支持自动提交

Author: India Agent (Builder)
"""

import subprocess
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple
from pathlib import Path


class CommitType(Enum):
    """语义化提交类型"""
    FEAT = "feat"           # 新功能
    FIX = "fix"             # 修复
    DOCS = "docs"           # 文档
    STYLE = "style"         # 代码格式
    REFACTOR = "refactor"   # 重构
    PERF = "perf"           # 性能优化
    TEST = "test"           # 测试
    CHORE = "chore"         # 构建/工具
    BUILD = "build"         # 构建系统
    CI = "ci"               # CI配置
    REVERT = "revert"       # 回滚


@dataclass
class FileChange:
    """文件变更信息"""
    path: str
    change_type: str  # added, modified, deleted, renamed
    additions: int = 0
    deletions: int = 0


@dataclass
class ChangeSummary:
    """变更摘要"""
    total_files: int
    additions: int
    deletions: int
    file_changes: List[FileChange]
    scope: Optional[str] = None


@dataclass
class SemanticCommit:
    """语义化提交信息"""
    commit_type: CommitType
    scope: Optional[str]
    description: str
    body: Optional[str]
    breaking_change: bool
    full_message: str


class GitService:
    """Git 语义提交服务"""
    
    # 文件类型到提交类型的映射
    FILE_TYPE_PATTERNS = {
        CommitType.DOCS: [
            r'\.(md|rst|txt)$',
            r'^(README|CHANGELOG|LICENSE|CONTRIBUTING)',
            r'^docs?/',
        ],
        CommitType.TEST: [
            r'[._-]?test[._-]?',
            r'[._-]?spec[._-]?',
            r'^tests?/',
        ],
        CommitType.STYLE: [
            r'\.(css|scss|sass|less|styl)$',
        ],
        CommitType.BUILD: [
            r'^(package\.json|setup\.py|pyproject\.toml|Makefile|Dockerfile)',
            r'\.(lock|toml|cfg|ini)$',
        ],
        CommitType.CI: [
            r'^\.github/',
            r'^\.gitlab-ci',
            r'\.yml$',
            r'\.yaml$',
        ],
    }
    
    # 代码变更关键词映射
    CODE_KEYWORDS = {
        CommitType.FEAT: ['add', 'create', 'implement', 'introduce', 'new', 'feature'],
        CommitType.FIX: ['fix', 'bugfix', 'repair', 'correct', 'resolve', 'patch'],
        CommitType.REFACTOR: ['refactor', 'restructure', 'rewrite', 'cleanup', 'clean up'],
        CommitType.PERF: ['optimize', 'performance', 'speed', 'improve', 'faster'],
        CommitType.REVERT: ['revert', 'rollback', 'undo'],
    }
    
    def __init__(self, repo_path: str = "."):
        """
        初始化 Git 服务
        
        Args:
            repo_path: Git 仓库路径
        """
        self.repo_path = Path(repo_path).resolve()
        self._validate_git_repo()
    
    def _validate_git_repo(self) -> None:
        """验证是否为有效的 Git 仓库"""
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            raise ValueError(f"{self.repo_path} 不是有效的 Git 仓库")
    
    def _run_git_command(self, args: List[str]) -> Tuple[int, str, str]:
        """
        执行 Git 命令
        
        Args:
            args: Git 命令参数
            
        Returns:
            (returncode, stdout, stderr)
        """
        cmd = ["git"] + args
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)
    
    def get_staged_files(self) -> List[FileChange]:
        """
        获取已暂存的文件变更列表
        
        Returns:
            文件变更列表
        """
        returncode, stdout, stderr = self._run_git_command(
            ["diff", "--cached", "--name-status", "--diff-filter=ACDMRT"]
        )
        
        if returncode != 0:
            raise RuntimeError(f"获取暂存文件失败: {stderr}")
        
        changes = []
        for line in stdout.strip().split("\n"):
            if not line:
                continue
            
            parts = line.split("\t")
            if len(parts) >= 2:
                status = parts[0][0]  # A, M, D, R, T
                path = parts[-1]
                
                change_type_map = {
                    "A": "added",
                    "M": "modified",
                    "D": "deleted",
                    "R": "renamed",
                    "T": "type_changed",
                }
                
                changes.append(FileChange(
                    path=path,
                    change_type=change_type_map.get(status, "unknown")
                ))
        
        return changes
    
    def get_diff_stats(self) -> Tuple[int, int]:
        """
        获取暂存区的代码统计
        
        Returns:
            (additions, deletions)
        """
        returncode, stdout, stderr = self._run_git_command(
            ["diff", "--cached", "--shortstat"]
        )
        
        if returncode != 0 or not stdout:
            return 0, 0
        
        # 解析类似: "5 files changed, 100 insertions(+), 50 deletions(-)"
        additions = 0
        deletions = 0
        
        add_match = re.search(r'(\d+) insertion', stdout)
        del_match = re.search(r'(\d+) deletion', stdout)
        
        if add_match:
            additions = int(add_match.group(1))
        if del_match:
            deletions = int(del_match.group(1))
        
        return additions, deletions
    
    def get_diff_content(self, max_lines: int = 100) -> str:
        """
        获取暂存区的 diff 内容
        
        Args:
            max_lines: 最大行数限制
            
        Returns:
            diff 内容
        """
        returncode, stdout, stderr = self._run_git_command(
            ["diff", "--cached", "--no-ext-diff"]
        )
        
        if returncode != 0:
            return ""
        
        lines = stdout.split("\n")
        if len(lines) > max_lines:
            return "\n".join(lines[:max_lines]) + "\n... (truncated)"
        
        return stdout
    
    def detect_scope(self, file_changes: List[FileChange]) -> Optional[str]:
        """
        从文件变更中检测作用域
        
        Args:
            file_changes: 文件变更列表
            
        Returns:
            检测到的作用域，如果没有则返回 None
        """
        if not file_changes:
            return None
        
        # 提取所有目录
        scopes = []
        for change in file_changes:
            path = Path(change.path)
            parts = path.parts
            
            if len(parts) > 1:
                # 使用第一级目录作为作用域
                scope = parts[0]
                if scope not in ['.', '']:
                    scopes.append(scope)
        
        if not scopes:
            return None
        
        # 找出最常见的目录
        from collections import Counter
        most_common = Counter(scopes).most_common(1)
        
        if most_common:
            return most_common[0][0]
        
        return None
    
    def detect_commit_type(self, file_changes: List[FileChange], diff_content: str = "") -> CommitType:
        """
        检测提交类型
        
        Args:
            file_changes: 文件变更列表
            diff_content: diff 内容
            
        Returns:
            检测到的提交类型
        """
        # 1. 基于文件类型检测
        type_scores = {t: 0 for t in CommitType}
        
        for change in file_changes:
            path = change.path.lower()
            
            for commit_type, patterns in self.FILE_TYPE_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, path, re.IGNORECASE):
                        type_scores[commit_type] += 1
        
        # 2. 基于 diff 内容关键词检测
        diff_lower = diff_content.lower()
        
        for commit_type, keywords in self.CODE_KEYWORDS.items():
            for keyword in keywords:
                count = diff_lower.count(keyword.lower())
                type_scores[commit_type] += count * 2  # 关键词权重更高
        
        # 3. 基于变更类型检测
        has_deletions = any(c.change_type == "deleted" for c in file_changes)
        has_additions = any(c.change_type in ["added", "modified"] for c in file_changes)
        
        # 如果主要是删除，可能是 refactor 或 fix
        if has_deletions and not has_additions:
            type_scores[CommitType.REFACTOR] += 1
        
        # 4. 选择得分最高的类型
        best_type = max(type_scores, key=type_scores.get)
        
        # 如果没有明显特征，默认使用 feat（新增）或 fix（修改）
        if type_scores[best_type] == 0:
            if any(c.change_type == "added" for c in file_changes):
                return CommitType.FEAT
            else:
                return CommitType.FIX
        
        return best_type
    
    def generate_description(self, commit_type: CommitType, file_changes: List[FileChange], 
                            diff_content: str = "") -> str:
        """
        生成提交描述
        
        Args:
            commit_type: 提交类型
            file_changes: 文件变更列表
            diff_content: diff 内容
            
        Returns:
            提交描述
        """
        descriptions = {
            CommitType.FEAT: ["add", "implement", "create", "introduce"],
            CommitType.FIX: ["fix", "resolve", "correct", "repair"],
            CommitType.DOCS: ["update documentation", "add documentation", "document"],
            CommitType.STYLE: ["format", "style", "clean up formatting"],
            CommitType.REFACTOR: ["refactor", "restructure", "optimize structure"],
            CommitType.PERF: ["optimize", "improve performance", "speed up"],
            CommitType.TEST: ["add tests", "update tests", "fix tests"],
            CommitType.CHORE: ["update", "maintain", "cleanup"],
            CommitType.BUILD: ["update build", "fix build", "configure"],
            CommitType.CI: ["update CI", "fix CI", "configure CI"],
            CommitType.REVERT: ["revert", "rollback", "undo"],
        }
        
        # 获取文件类型信息
        file_types = set()
        for change in file_changes:
            ext = Path(change.path).suffix.lower()
            if ext:
                file_types.add(ext)
        
        # 构建描述
        verbs = descriptions.get(commit_type, ["update"])
        verb = verbs[0]
        
        # 根据变更内容生成更具体的描述
        if len(file_changes) == 1:
            # 单文件变更
            path = file_changes[0].path
            filename = Path(path).name
            
            if commit_type == CommitType.FEAT:
                return f"{verb} {filename}"
            elif commit_type == CommitType.FIX:
                return f"{verb} issue in {filename}"
            elif commit_type == CommitType.DOCS:
                return f"{verb} for {filename}"
            else:
                return f"{verb} {filename}"
        else:
            # 多文件变更
            scope = self.detect_scope(file_changes)
            
            if scope:
                if commit_type == CommitType.FEAT:
                    return f"{verb} features in {scope}"
                elif commit_type == CommitType.FIX:
                    return f"{verb} issues in {scope}"
                elif commit_type == CommitType.REFACTOR:
                    return f"{verb} {scope} module"
                else:
                    return f"{verb} {scope}"
            else:
                file_count = len(file_changes)
                if commit_type == CommitType.FEAT:
                    return f"{verb} features ({file_count} files)"
                elif commit_type == CommitType.FIX:
                    return f"{verb} various issues"
                else:
                    return f"{verb} multiple files"
    
    def generate_body(self, file_changes: List[FileChange], additions: int, 
                     deletions: int) -> Optional[str]:
        """
        生成提交正文
        
        Args:
            file_changes: 文件变更列表
            additions: 新增行数
            deletions: 删除行数
            
        Returns:
            提交正文，如果没有则返回 None
        """
        lines = []
        
        # 变更统计
        if additions > 0 or deletions > 0:
            lines.append(f"Changes: +{additions}/-{deletions}")
            lines.append("")
        
        # 文件列表（限制数量）
        if len(file_changes) <= 10:
            lines.append("Files modified:")
            for change in file_changes:
                status_icon = {
                    "added": "+",
                    "modified": "~",
                    "deleted": "-",
                    "renamed": "→",
                    "type_changed": "T",
                }.get(change.change_type, "?")
                lines.append(f"  {status_icon} {change.path}")
        else:
            lines.append(f"Files modified: {len(file_changes)} files")
            # 按类型分组
            by_type = {}
            for change in file_changes:
                by_type.setdefault(change.change_type, []).append(change)
            
            for change_type, changes in by_type.items():
                lines.append(f"  {change_type}: {len(changes)} files")
        
        return "\n".join(lines) if lines else None
    
    def analyze_changes(self) -> ChangeSummary:
        """
        分析暂存区的变更
        
        Returns:
            变更摘要
        """
        file_changes = self.get_staged_files()
        additions, deletions = self.get_diff_stats()
        scope = self.detect_scope(file_changes)
        
        return ChangeSummary(
            total_files=len(file_changes),
            additions=additions,
            deletions=deletions,
            file_changes=file_changes,
            scope=scope
        )
    
    def generate_semantic_commit(self, custom_description: Optional[str] = None,
                                  include_body: bool = True) -> SemanticCommit:
        """
        生成语义化提交信息
        
        Args:
            custom_description: 自定义描述，如果提供则使用此描述
            include_body: 是否包含提交正文
            
        Returns:
            语义化提交信息
        """
        # 获取变更信息
        file_changes = self.get_staged_files()
        
        if not file_changes:
            raise ValueError("没有暂存的变更，请先执行 git add")
        
        additions, deletions = self.get_diff_stats()
        diff_content = self.get_diff_content()
        scope = self.detect_scope(file_changes)
        
        # 检测提交类型
        commit_type = self.detect_commit_type(file_changes, diff_content)
        
        # 生成描述
        if custom_description:
            description = custom_description
        else:
            description = self.generate_description(commit_type, file_changes, diff_content)
        
        # 生成正文
        body = None
        if include_body:
            body = self.generate_body(file_changes, additions, deletions)
        
        # 检测是否为破坏性变更（删除大量代码或包含 BREAKING CHANGE 标记）
        breaking_change = False
        if deletions > additions * 2 and deletions > 50:
            breaking_change = True
        if "BREAKING CHANGE" in diff_content.upper():
            breaking_change = True
        
        # 构建完整提交信息
        scope_str = f"({scope})" if scope else ""
        breaking_marker = "!" if breaking_change else ""
        
        full_message = f"{commit_type.value}{scope_str}{breaking_marker}: {description}"
        
        if body:
            full_message += f"\n\n{body}"
        
        if breaking_change:
            full_message += "\n\nBREAKING CHANGE: This commit contains breaking changes"
        
        return SemanticCommit(
            commit_type=commit_type,
            scope=scope,
            description=description,
            body=body,
            breaking_change=breaking_change,
            full_message=full_message
        )
    
    def commit(self, message: Optional[str] = None, auto_generate: bool = True,
               custom_description: Optional[str] = None, include_body: bool = True) -> Tuple[bool, str]:
        """
        执行提交
        
        Args:
            message: 自定义提交信息，如果提供则直接使用
            auto_generate: 是否自动生成语义化提交信息
            custom_description: 自定义描述（仅在 auto_generate=True 时有效）
            include_body: 是否包含提交正文
            
        Returns:
            (success, message_or_error)
        """
        # 检查是否有暂存的变更
        file_changes = self.get_staged_files()
        if not file_changes:
            return False, "没有暂存的变更，请先执行 git add"
        
        # 确定提交信息
        if message:
            commit_message = message
        elif auto_generate:
            try:
                semantic_commit = self.generate_semantic_commit(
                    custom_description=custom_description,
                    include_body=include_body
                )
                commit_message = semantic_commit.full_message
            except ValueError as e:
                return False, str(e)
        else:
            return False, "必须提供提交信息或启用自动生成"
        
        # 执行提交
        returncode, stdout, stderr = self._run_git_command(
            ["commit", "-m", commit_message]
        )
        
        if returncode != 0:
            return False, f"提交失败: {stderr}"
        
        return True, f"提交成功: {stdout}"
    
    def preview_commit(self, custom_description: Optional[str] = None,
                      include_body: bool = True) -> str:
        """
        预览将要生成的提交信息
        
        Args:
            custom_description: 自定义描述
            include_body: 是否包含提交正文
            
        Returns:
            提交信息预览
        """
        try:
            semantic_commit = self.generate_semantic_commit(
                custom_description=custom_description,
                include_body=include_body
            )
            
            preview = [
                "=" * 50,
                "📝 语义化提交信息预览",
                "=" * 50,
                "",
                f"类型: {semantic_commit.commit_type.value}",
                f"作用域: {semantic_commit.scope or '无'}",
                f"描述: {semantic_commit.description}",
                f"破坏性变更: {'是' if semantic_commit.breaking_change else '否'}",
                "",
                "-" * 50,
                "完整提交信息:",
                "-" * 50,
                semantic_commit.full_message,
                "-" * 50,
            ]
            
            return "\n".join(preview)
        
        except ValueError as e:
            return f"❌ 错误: {e}"
    
    def get_commit_history(self, limit: int = 10) -> List[dict]:
        """
        获取提交历史
        
        Args:
            limit: 返回的提交数量
            
        Returns:
            提交历史列表
        """
        format_str = '%H|%s|%an|%ae|%ad'
        returncode, stdout, stderr = self._run_git_command([
            "log", f"--pretty=format:{format_str}",
            "--date=short", f"-{limit}"
        ])
        
        if returncode != 0:
            return []
        
        commits = []
        for line in stdout.strip().split("\n"):
            if "|" in line:
                parts = line.split("|", 4)
                if len(parts) == 5:
                    commits.append({
                        "hash": parts[0][:7],
                        "full_hash": parts[0],
                        "message": parts[1],
                        "author_name": parts[2],
                        "author_email": parts[3],
                        "date": parts[4],
                    })
        
        return commits


# 便捷函数

def quick_commit(repo_path: str = ".", custom_description: Optional[str] = None) -> Tuple[bool, str]:
    """
    快速提交暂存区的变更
    
    Args:
        repo_path: 仓库路径
        custom_description: 自定义描述
        
    Returns:
        (success, message_or_error)
    """
    service = GitService(repo_path)
    return service.commit(auto_generate=True, custom_description=custom_description)


def preview(repo_path: str = ".", custom_description: Optional[str] = None) -> str:
    """
    预览将要生成的提交信息
    
    Args:
        repo_path: 仓库路径
        custom_description: 自定义描述
        
    Returns:
        提交信息预览
    """
    service = GitService(repo_path)
    return service.preview_commit(custom_description=custom_description)


def analyze(repo_path: str = ".") -> ChangeSummary:
    """
    分析暂存区的变更
    
    Args:
        repo_path: 仓库路径
        
    Returns:
        变更摘要
    """
    service = GitService(repo_path)
    return service.analyze_changes()


# 命令行接口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Git 语义提交工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python git_service.py preview              # 预览生成的提交信息
  python git_service.py commit               # 自动提交
  python git_service.py commit -m "fix bug"  # 使用自定义描述
  python git_service.py analyze              # 分析变更
  python git_service.py log                  # 查看提交历史
        """
    )
    
    parser.add_argument(
        "action",
        choices=["preview", "commit", "analyze", "log"],
        help="执行的操作"
    )
    
    parser.add_argument(
        "-m", "--message",
        help="自定义提交描述"
    )
    
    parser.add_argument(
        "--no-body",
        action="store_true",
        help="不包含提交正文"
    )
    
    parser.add_argument(
        "-C", "--repo",
        default=".",
        help="仓库路径 (默认: 当前目录)"
    )
    
    parser.add_argument(
        "-n", "--limit",
        type=int,
        default=10,
        help="提交历史数量 (默认: 10)"
    )
    
    args = parser.parse_args()
    
    try:
        service = GitService(args.repo)
        
        if args.action == "preview":
            print(service.preview_commit(
                custom_description=args.message,
                include_body=not args.no_body
            ))
        
        elif args.action == "commit":
            success, result = service.commit(
                custom_description=args.message,
                include_body=not args.no_body
            )
            print(result)
            exit(0 if success else 1)
        
        elif args.action == "analyze":
            summary = service.analyze_changes()
            print(f"📊 变更分析")
            print(f"=" * 40)
            print(f"文件数: {summary.total_files}")
            print(f"新增: +{summary.additions}")
            print(f"删除: -{summary.deletions}")
            print(f"作用域: {summary.scope or '未检测'}")
            print(f"\n文件列表:")
            for change in summary.file_changes:
                icon = {"added": "+", "modified": "~", "deleted": "-", "renamed": "→"}.get(
                    change.change_type, "?"
                )
                print(f"  {icon} {change.path}")
        
        elif args.action == "log":
            commits = service.get_commit_history(args.limit)
            print(f"📜 最近 {len(commits)} 条提交")
            print("=" * 60)
            for commit in commits:
                print(f"\n[{commit['hash']}] {commit['message']}")
                print(f"  Author: {commit['author_name']} <{commit['author_email']}>")
                print(f"  Date: {commit['date']}")
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        exit(1)
