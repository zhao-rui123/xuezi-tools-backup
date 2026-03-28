"""
Bug修复器 - 自动检测和修复程序问题
====================================

提供自动bug检测和修复功能:
- 代码质量分析
- 常见错误检测
- 自动修复建议
- 代码重构建议
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging


@dataclass
class BugIssue:
    """Bug问题"""
    type: str
    severity: str  # critical, high, medium, low
    description: str
    file_path: str
    line_number: int
    code_snippet: str
    fix_suggestion: str
    auto_fixable: bool = False
    fixed_code: str = ""


@dataclass
class FixResult:
    """修复结果"""
    success: bool
    file_path: str
    issue_type: str
    original_code: str
    fixed_code: str
    message: str


class BugFixer:
    """Bug修复器类"""
    
    # 常见错误模式
    COMMON_BUG_PATTERNS = {
        # 语法错误
        'syntax_error': {
            'pattern': None,  # 通过AST检测
            'description': '语法错误',
            'severity': 'critical',
        },
        
        # 未定义变量
        'undefined_variable': {
            'pattern': None,  # 通过AST检测
            'description': '使用未定义的变量',
            'severity': 'critical',
        },
        
        # 导入错误
        'import_error': {
            'pattern': None,
            'description': '导入模块失败',
            'severity': 'high',
        },
        
        # 空指针/None检查
        'none_check': {
            'pattern': r'if\s+\w+\s*==\s*None',
            'description': '使用==比较None，应使用is',
            'severity': 'low',
            'fix': lambda m: m.group(0).replace('== None', 'is None'),
        },
        
        # 可变默认参数
        'mutable_default': {
            'pattern': r'def\s+\w+\s*\([^)]*=\s*(\[\s*\]|\{\s*\})',
            'description': '使用可变对象作为默认参数',
            'severity': 'medium',
        },
        
        # 未关闭的文件
        'unclosed_file': {
            'pattern': r'open\s*\([^)]+\)(?!\s*\.\s*close)',
            'description': '文件未正确关闭，建议使用with语句',
            'severity': 'medium',
        },
        
        # 裸except
        'bare_except': {
            'pattern': r'except\s*:',
            'description': '使用裸except，应指定异常类型',
            'severity': 'medium',
            'fix': lambda m: m.group(0).replace('except:', 'except Exception:'),
        },
        
        # 比较链错误
        'chained_comparison': {
            'pattern': r'\w+\s*==\s*\w+\s*==\s*\w+',
            'description': '可能的比较链错误',
            'severity': 'medium',
        },
        
        # 字符串格式化问题
        'string_format': {
            'pattern': r'"[^"]*%s[^"]*"\s*%',
            'description': '使用%格式化字符串，建议使用f-string或format',
            'severity': 'low',
        },
        
        # 未使用的导入
        'unused_import': {
            'pattern': None,  # 通过AST检测
            'description': '存在未使用的导入',
            'severity': 'low',
        },
        
        # 硬编码路径
        'hardcoded_path': {
            'pattern': r'["\']/[a-zA-Z]+/[^"\']+["\']',
            'description': '硬编码文件路径',
            'severity': 'low',
        },
        
        # 无限循环风险
        'infinite_loop': {
            'pattern': r'while\s+True\s*:',
            'description': '可能的无限循环，确保有break条件',
            'severity': 'medium',
        },
        
        # 资源泄漏
        'resource_leak': {
            'pattern': r'(socket|connection|cursor)\s*=\s*[^\n]+\n(?!.*\.close)',
            'description': '可能的资源泄漏',
            'severity': 'medium',
        },
    }
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化Bug修复器
        
        Args:
            config: 配置选项
        """
        self.config = config or {}
        self.logger = logging.getLogger("BugFixer")
        
        self.auto_fix = self.config.get('auto_fix', True)
        self.backup_before_fix = self.config.get('backup_before_fix', True)
        self.fix_severity_levels = self.config.get('fix_severity', ['low', 'medium'])
        
        # 修复统计
        self.fix_count = 0
        self.failed_fixes = 0
    
    def analyze_skill(self, skill_path: str) -> Dict[str, Any]:
        """
        分析技能包代码质量
        
        Args:
            skill_path: 技能包路径
            
        Returns:
            分析结果
        """
        skill_path = Path(skill_path)
        issues: List[BugIssue] = []
        warnings: List[str] = []
        
        if not skill_path.exists():
            return {
                'has_issues': True,
                'issues': [],
                'warnings': ['路径不存在'],
                'quality_score': 0,
            }
        
        # 扫描所有Python文件
        python_files = list(skill_path.rglob('*.py'))
        
        for py_file in python_files:
            file_issues = self._analyze_file(py_file)
            issues.extend(file_issues)
        
        # 计算质量评分
        quality_score = self._calculate_quality_score(issues, len(python_files))
        
        return {
            'has_issues': len(issues) > 0,
            'issues': [self._issue_to_dict(i) for i in issues],
            'warnings': warnings,
            'quality_score': quality_score,
            'files_analyzed': len(python_files),
        }
    
    def fix_issues(self, issues: List[Dict]) -> Dict[str, Any]:
        """
        修复检测到的问题
        
        Args:
            issues: 问题列表
            
        Returns:
            修复结果
        """
        result = {
            'fixed_count': 0,
            'failed_count': 0,
            'fixes': [],
            'skipped': [],
        }
        
        for issue_data in issues:
            issue = self._dict_to_issue(issue_data)
            
            # 检查是否可以自动修复
            if not issue.auto_fixable:
                result['skipped'].append({
                    'file_path': issue.file_path,
                    'reason': '不可自动修复',
                })
                continue
            
            # 检查严重级别
            if issue.severity not in self.fix_severity_levels:
                result['skipped'].append({
                    'file_path': issue.file_path,
                    'reason': f'严重级别{issue.severity}不在自动修复范围内',
                })
                continue
            
            # 执行修复
            fix_result = self._apply_fix(issue)
            
            if fix_result.success:
                result['fixed_count'] += 1
                self.fix_count += 1
            else:
                result['failed_count'] += 1
                self.failed_fixes += 1
            
            result['fixes'].append({
                'success': fix_result.success,
                'file_path': fix_result.file_path,
                'issue_type': fix_result.issue_type,
                'message': fix_result.message,
            })
        
        return result
    
    def fix_file(self, file_path: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        修复单个文件
        
        Args:
            file_path: 文件路径
            dry_run: 是否只预览不执行
            
        Returns:
            修复结果
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {'success': False, 'error': '文件不存在'}
        
        # 分析文件
        issues = self._analyze_file(file_path)
        
        # 筛选可自动修复的问题
        auto_fixable = [i for i in issues if i.auto_fixable]
        
        result = {
            'file_path': str(file_path),
            'total_issues': len(issues),
            'auto_fixable': len(auto_fixable),
            'fixes': [],
            'dry_run': dry_run,
        }
        
        if dry_run:
            result['fixes'] = [self._issue_to_dict(i) for i in auto_fixable]
            return result
        
        # 执行修复
        fix_results = self.fix_issues([self._issue_to_dict(i) for i in auto_fixable])
        result['fixes'] = fix_results['fixes']
        result['fixed_count'] = fix_results['fixed_count']
        result['failed_count'] = fix_results['failed_count']
        
        return result
    
    def _analyze_file(self, file_path: Path) -> List[BugIssue]:
        """分析单个文件"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            return [BugIssue(
                type='read_error',
                severity='high',
                description=f'无法读取文件: {e}',
                file_path=str(file_path),
                line_number=0,
                code_snippet='',
                fix_suggestion='检查文件权限和编码',
            )]
        
        # 1. 语法检查
        syntax_issues = self._check_syntax(file_path, content)
        issues.extend(syntax_issues)
        
        # 2. 模式匹配检查
        for bug_type, bug_info in self.COMMON_BUG_PATTERNS.items():
            if bug_info.get('pattern'):
                pattern = bug_info['pattern']
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line):
                        fix_suggestion = self._get_fix_suggestion(bug_type, line)
                        auto_fixable = bool(bug_info.get('fix'))
                        fixed_code = ''
                        
                        if auto_fixable and bug_info.get('fix'):
                            match = re.search(pattern, line)
                            if match:
                                fixed_code = bug_info['fix'](match)
                        
                        issue = BugIssue(
                            type=bug_type,
                            severity=bug_info.get('severity', 'medium'),
                            description=bug_info['description'],
                            file_path=str(file_path),
                            line_number=i,
                            code_snippet=line.strip()[:100],
                            fix_suggestion=fix_suggestion,
                            auto_fixable=auto_fixable,
                            fixed_code=fixed_code,
                        )
                        issues.append(issue)
        
        # 3. AST分析
        try:
            tree = ast.parse(content)
            ast_issues = self._analyze_ast(tree, file_path, lines)
            issues.extend(ast_issues)
        except SyntaxError:
            pass  # 语法错误已在上面处理
        
        return issues
    
    def _check_syntax(self, file_path: Path, content: str) -> List[BugIssue]:
        """检查语法错误"""
        issues = []
        
        try:
            ast.parse(content)
        except SyntaxError as e:
            issue = BugIssue(
                type='syntax_error',
                severity='critical',
                description=f'语法错误: {e.msg}',
                file_path=str(file_path),
                line_number=e.lineno or 1,
                code_snippet=e.text.strip() if e.text else '',
                fix_suggestion='修复语法错误',
                auto_fixable=False,
            )
            issues.append(issue)
        
        return issues
    
    def _analyze_ast(self, tree: ast.AST, file_path: Path, lines: List[str]) -> List[BugIssue]:
        """使用AST分析代码"""
        issues = []
        
        # 收集定义的变量和导入
        defined_names = set()
        imported_names = set()
        used_names = set()
        
        for node in ast.walk(tree):
            # 收集导入
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    imported_names.add(alias.asname or alias.name)
            
            # 收集变量定义
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    defined_names.add(node.id)
                elif isinstance(node.ctx, ast.Load):
                    used_names.add(node.id)
            
            # 检测可变默认参数
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict)):
                        if isinstance(default, ast.List) and default.elts == []:
                            issue = BugIssue(
                                type='mutable_default',
                                severity='medium',
                                description='使用空列表作为默认参数',
                                file_path=str(file_path),
                                line_number=node.lineno,
                                code_snippet=lines[node.lineno - 1].strip()[:100],
                                fix_suggestion='使用None作为默认值，在函数内部初始化',
                                auto_fixable=False,
                            )
                            issues.append(issue)
                        elif isinstance(default, ast.Dict) and default.keys == []:
                            issue = BugIssue(
                                type='mutable_default',
                                severity='medium',
                                description='使用空字典作为默认参数',
                                file_path=str(file_path),
                                line_number=node.lineno,
                                code_snippet=lines[node.lineno - 1].strip()[:100],
                                fix_suggestion='使用None作为默认值，在函数内部初始化',
                                auto_fixable=False,
                            )
                            issues.append(issue)
        
        # 检测未使用的导入
        for imported in imported_names:
            base_name = imported.split('.')[0]
            if base_name not in used_names and not base_name.startswith('_'):
                issue = BugIssue(
                    type='unused_import',
                    severity='low',
                    description=f'未使用的导入: {imported}',
                    file_path=str(file_path),
                    line_number=1,
                    code_snippet=f'import {imported}',
                    fix_suggestion=f'删除未使用的导入: {imported}',
                    auto_fixable=True,
                )
                issues.append(issue)
        
        return issues
    
    def _get_fix_suggestion(self, bug_type: str, code: str) -> str:
        """获取修复建议"""
        suggestions = {
            'none_check': '使用 "is None" 或 "is not None" 替代 "== None"',
            'bare_except': '指定具体的异常类型，如 except ValueError:',
            'string_format': '使用 f-string: f"value: {variable}"',
            'mutable_default': '使用 None 作为默认值，在函数内部初始化',
            'unclosed_file': '使用 with open(...) as f: 确保文件正确关闭',
            'infinite_loop': '确保循环内有适当的 break 条件',
        }
        return suggestions.get(bug_type, '参考Python最佳实践进行修复')
    
    def _apply_fix(self, issue: BugIssue) -> FixResult:
        """应用修复"""
        try:
            file_path = Path(issue.file_path)
            
            # 备份文件
            if self.backup_before_fix:
                backup_path = file_path.with_suffix(f'.py.backup.{int(datetime.now().timestamp())}')
                backup_path.write_bytes(file_path.read_bytes())
            
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 应用修复
            if issue.line_number > 0 and issue.line_number <= len(lines):
                original_line = lines[issue.line_number - 1]
                
                if issue.fixed_code:
                    # 使用提供的修复代码
                    lines[issue.line_number - 1] = original_line.replace(
                        issue.code_snippet, issue.fixed_code
                    )
                elif issue.type == 'unused_import':
                    # 删除未使用的导入行
                    for i, line in enumerate(lines):
                        if issue.code_snippet in line:
                            lines[i] = ''
                            break
                
                # 写回文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                return FixResult(
                    success=True,
                    file_path=str(file_path),
                    issue_type=issue.type,
                    original_code=issue.code_snippet,
                    fixed_code=issue.fixed_code or '已删除',
                    message=f'成功修复 {issue.type}',
                )
            
            return FixResult(
                success=False,
                file_path=str(file_path),
                issue_type=issue.type,
                original_code=issue.code_snippet,
                fixed_code='',
                message='无法定位到具体行',
            )
            
        except Exception as e:
            return FixResult(
                success=False,
                file_path=issue.file_path,
                issue_type=issue.type,
                original_code=issue.code_snippet,
                fixed_code='',
                message=f'修复失败: {str(e)}',
            )
    
    def _calculate_quality_score(self, issues: List[BugIssue], file_count: int) -> int:
        """计算代码质量评分"""
        if file_count == 0:
            return 100
        
        # 基础分数
        score = 100
        
        # 根据问题严重级别扣分
        severity_penalties = {
            'critical': 20,
            'high': 10,
            'medium': 5,
            'low': 2,
        }
        
        for issue in issues:
            score -= severity_penalties.get(issue.severity, 2)
        
        # 确保分数在0-100之间
        return max(0, min(100, score))
    
    def _issue_to_dict(self, issue: BugIssue) -> Dict[str, Any]:
        """转换BugIssue为字典"""
        return {
            'type': issue.type,
            'severity': issue.severity,
            'description': issue.description,
            'file_path': issue.file_path,
            'line_number': issue.line_number,
            'code_snippet': issue.code_snippet,
            'fix_suggestion': issue.fix_suggestion,
            'auto_fixable': issue.auto_fixable,
            'fixed_code': issue.fixed_code,
        }
    
    def _dict_to_issue(self, data: Dict) -> BugIssue:
        """转换字典为BugIssue"""
        return BugIssue(
            type=data['type'],
            severity=data['severity'],
            description=data['description'],
            file_path=data['file_path'],
            line_number=data['line_number'],
            code_snippet=data['code_snippet'],
            fix_suggestion=data['fix_suggestion'],
            auto_fixable=data.get('auto_fixable', False),
            fixed_code=data.get('fixed_code', ''),
        )
