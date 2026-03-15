#!/usr/bin/env python3
"""
OpenClaw 代码审查脚本
功能: 自动代码审查，检测安全漏洞、性能问题、可维护性问题
用法: python code_review.py <file_or_directory> [--format json|markdown|html]
"""

import ast
import sys
import os
import re
import json
import argparse
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Set, Optional, Any, Tuple
from enum import Enum, auto
from pathlib import Path
from datetime import datetime


class Severity(Enum):
    """问题严重程度"""
    CRITICAL = "critical"    # 必须修复：安全漏洞、功能缺陷
    HIGH = "high"           # 强烈建议修复：性能问题、设计缺陷
    MEDIUM = "medium"       # 建议修复：代码风格、可维护性
    LOW = "low"             # 可选修复：格式问题
    INFO = "info"           # 信息性提示


class Category(Enum):
    """问题类别"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    CORRECTNESS = "correctness"
    STYLE = "style"
    BEST_PRACTICE = "best_practice"


@dataclass
class Issue:
    """代码问题"""
    file: str
    line: int
    column: int
    severity: Severity
    category: Category
    message: str
    suggestion: str
    code_snippet: str = ""
    rule_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "severity": self.severity.value,
            "category": self.category.value,
            "message": self.message,
            "suggestion": self.suggestion,
            "code_snippet": self.code_snippet,
            "rule_id": self.rule_id
        }


@dataclass
class ReviewReport:
    """审查报告"""
    target: str
    timestamp: str
    total_files: int
    total_issues: int
    issues_by_severity: Dict[str, int] = field(default_factory=dict)
    issues_by_category: Dict[str, int] = field(default_factory=dict)
    issues: List[Issue] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "target": self.target,
            "timestamp": self.timestamp,
            "total_files": self.total_files,
            "total_issues": self.total_issues,
            "issues_by_severity": self.issues_by_severity,
            "issues_by_category": self.issues_by_category,
            "issues": [i.to_dict() for i in self.issues]
        }


class PythonCodeReviewer(ast.NodeVisitor):
    """Python代码审查器"""
    
    # 危险函数列表
    DANGEROUS_FUNCTIONS = {
        'eval', 'exec', 'compile', '__import__', 'input',
        'os.system', 'subprocess.call', 'subprocess.Popen'
    }
    
    # SQL注入风险模式
    SQL_PATTERNS = [
        r'(?i)(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)\s+',
        r'(?i)EXEC\s*\(',
        r'(?i)EXECUTE\s*\(',
    ]
    
    # 硬编码敏感信息模式
    SENSITIVE_PATTERNS = [
        (r'(?i)(password|passwd|pwd|secret)\s*=\s*["\'][^"\']+["\']', 
         '硬编码密码', Severity.CRITICAL),
        (r'(?i)(api[_-]?key|apikey|api_secret)\s*=\s*["\'][^"\']{10,}["\']',
         '硬编码API密钥', Severity.CRITICAL),
        (r'(?i)(token|access_token|auth_token)\s*=\s*["\'][^"\']{10,}["\']',
         '硬编码令牌', Severity.CRITICAL),
        (r'(?i)private[_-]?key\s*=\s*["\'][^"\']{20,}["\']',
         '硬编码私钥', Severity.CRITICAL),
    ]
    
    def __init__(self, filename: str, source: str):
        self.filename = filename
        self.source = source
        self.lines = source.split('\n')
        self.issues: List[Issue] = []
        self.current_function: Optional[str] = None
        self.function_complexity: Dict[str, int] = {}
        self.imported_names: Set[str] = set()
        self.defined_names: Set[str] = set()
        self.used_names: Set[str] = set()
        self.rule_counter = 0
    
    def _get_rule_id(self) -> str:
        """生成规则ID"""
        self.rule_counter += 1
        return f"RULE-{self.rule_counter:03d}"
    
    def review(self) -> List[Issue]:
        """执行代码审查"""
        try:
            tree = ast.parse(self.source)
            self.visit(tree)
            self._check_additional_rules()
        except SyntaxError as e:
            self.issues.append(Issue(
                file=self.filename,
                line=e.lineno or 1,
                column=e.offset or 0,
                severity=Severity.CRITICAL,
                category=Category.CORRECTNESS,
                message=f"语法错误: {e.msg}",
                suggestion="修复语法错误",
                code_snippet=self.lines[e.lineno - 1] if e.lineno else "",
                rule_id="SYNTAX-001"
            ))
        return self.issues
    
    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imported_names.add(alias.asname or alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        for alias in node.names:
            name = alias.asname or alias.name
            self.imported_names.add(name)
        self.generic_visit(node)
    
    def visit_Name(self, node: ast.Name):
        self.used_names.add(node.id)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        old_function = self.current_function
        self.current_function = node.name
        self.function_complexity[node.name] = 1
        
        # 检查函数长度
        func_lines = node.end_lineno - node.lineno if node.end_lineno else 0
        if func_lines > 50:
            self._add_issue(
                node, Severity.MEDIUM, Category.MAINTAINABILITY,
                f"函数 '{node.name}' 过长 ({func_lines} 行)",
                "考虑将函数拆分为多个小函数，每个函数只做一件事",
                self._get_snippet(node.lineno),
                "FUNC-001"
            )
        
        # 检查参数数量
        arg_count = len(node.args.args) + len(node.args.kwonlyargs)
        if arg_count > 5:
            self._add_issue(
                node, Severity.MEDIUM, Category.MAINTAINABILITY,
                f"函数 '{node.name}' 参数过多 ({arg_count} 个)",
                "考虑使用参数对象模式或拆分函数",
                self._get_snippet(node.lineno),
                "FUNC-002"
            )
        
        # 检查可变默认参数
        for default in node.args.defaults + node.args.kw_defaults:
            if default and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self._add_issue(
                    node, Severity.HIGH, Category.CORRECTNESS,
                    f"函数 '{node.name}' 使用可变默认参数",
                    "使用None作为默认值，在函数内部初始化可变对象",
                    self._get_snippet(node.lineno),
                    "FUNC-003"
                )
        
        self.generic_visit(node)
        
        # 检查圈复杂度
        complexity = self.function_complexity.get(node.name, 1)
        if complexity > 10:
            self._add_issue(
                node, Severity.HIGH, Category.MAINTAINABILITY,
                f"函数 '{node.name}' 圈复杂度过高 ({complexity})",
                "简化条件逻辑，提取复杂条件为单独函数",
                self._get_snippet(node.lineno),
                "FUNC-004"
            )
        
        self.current_function = old_function
    
    def visit_ClassDef(self, node: ast.ClassDef):
        # 检查类名规范
        if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
            self._add_issue(
                node, Severity.LOW, Category.STYLE,
                f"类名 '{node.name}' 不符合PascalCase规范",
                "类名应使用PascalCase，如: UserService",
                self._get_snippet(node.lineno),
                "CLASS-001"
            )
        
        # 检查类长度
        class_lines = node.end_lineno - node.lineno if node.end_lineno else 0
        if class_lines > 300:
            self._add_issue(
                node, Severity.MEDIUM, Category.MAINTAINABILITY,
                f"类 '{node.name}' 过长 ({class_lines} 行)",
                "考虑将类拆分为多个小类",
                self._get_snippet(node.lineno),
                "CLASS-002"
            )
        
        self.generic_visit(node)
    
    def visit_If(self, node: ast.If):
        if self.current_function:
            self.function_complexity[self.current_function] += 1
        
        # 检查过深的嵌套
        self._check_nesting_depth(node)
        
        self.generic_visit(node)
    
    def visit_For(self, node: ast.For):
        if self.current_function:
            self.function_complexity[self.current_function] += 1
        
        # 检查是否在循环中修改迭代对象
        if isinstance(node.iter, ast.Name):
            loop_body = ''.join(ast.dump(stmt) for stmt in node.body)
            if f"Del({node.iter.id}" in loop_body or f"Store({node.iter.id}" in loop_body:
                self._add_issue(
                    node, Severity.HIGH, Category.CORRECTNESS,
                    "在迭代过程中修改迭代对象",
                    "创建列表副本后再修改: for item in list[:]:",
                    self._get_snippet(node.lineno),
                    "LOOP-001"
                )
        
        self.generic_visit(node)
    
    def visit_While(self, node: ast.While):
        if self.current_function:
            self.function_complexity[self.current_function] += 1
        
        # 检查无限循环
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            body_dump = ''.join(ast.dump(stmt) for stmt in node.body)
            if 'Break' not in body_dump and 'Return' not in body_dump:
                self._add_issue(
                    node, Severity.CRITICAL, Category.CORRECTNESS,
                    "检测到无限循环 (while True without break/return)",
                    "添加退出条件或break/return语句",
                    self._get_snippet(node.lineno),
                    "LOOP-002"
                )
        
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call):
        self._check_dangerous_calls(node)
        self._check_sql_injection(node)
        self._check_logging_issues(node)
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        self._check_exception_handling(node)
        self.generic_visit(node)
    
    def visit_Try(self, node: ast.Try):
        # 检查空的try块
        if not node.body or (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)):
            self._add_issue(
                node, Severity.MEDIUM, Category.MAINTAINABILITY,
                "空的try块",
                "移除空的try块或添加需要保护的代码",
                self._get_snippet(node.lineno),
                "TRY-001"
            )
        
        self.generic_visit(node)
    
    def visit_Assign(self, node: ast.Assign):
        # 检查未使用的变量
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.defined_names.add(target.id)
        
        self.generic_visit(node)
    
    def _check_nesting_depth(self, node: ast.AST, depth: int = 0):
        """检查嵌套深度"""
        if depth > 4:
            self._add_issue(
                node, Severity.MEDIUM, Category.MAINTAINABILITY,
                f"代码嵌套过深 ({depth} 层)",
                "考虑提前返回或提取函数来减少嵌套",
                self._get_snippet(node.lineno),
                "NEST-001"
            )
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                self._check_nesting_depth(child, depth + 1)
    
    def _check_dangerous_calls(self, node: ast.Call):
        """检查危险函数调用"""
        if isinstance(node.func, ast.Name):
            if node.func.id in self.DANGEROUS_FUNCTIONS:
                self._add_issue(
                    node, Severity.CRITICAL, Category.SECURITY,
                    f"使用危险函数 '{node.func.id}'",
                    f"避免使用 {node.func.id}，使用更安全的替代方案",
                    self._get_snippet(node.lineno),
                    "SEC-001"
                )
        
        elif isinstance(node.func, ast.Attribute):
            full_name = self._get_attribute_name(node.func)
            if full_name in self.DANGEROUS_FUNCTIONS:
                self._add_issue(
                    node, Severity.CRITICAL, Category.SECURITY,
                    f"使用危险函数 '{full_name}'",
                    f"避免使用 {full_name}，使用更安全的替代方案",
                    self._get_snippet(node.lineno),
                    "SEC-002"
                )
    
    def _check_sql_injection(self, node: ast.Call):
        """检查SQL注入风险"""
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ('execute', 'executemany', 'executescript'):
                # 检查第一个参数是否是格式化字符串
                if node.args:
                    first_arg = node.args[0]
                    if isinstance(first_arg, ast.JoinedStr):
                        self._add_issue(
                            node, Severity.CRITICAL, Category.SECURITY,
                            "检测到潜在的SQL注入风险 (f-string in SQL)",
                            "使用参数化查询替代字符串拼接",
                            self._get_snippet(node.lineno),
                            "SEC-003"
                        )
                    elif isinstance(first_arg, ast.BinOp) and isinstance(first_arg.op, ast.Mod):
                        self._add_issue(
                            node, Severity.CRITICAL, Category.SECURITY,
                            "检测到潜在的SQL注入风险 (% formatting)",
                            "使用参数化查询替代字符串格式化",
                            self._get_snippet(node.lineno),
                            "SEC-004"
                        )
                    elif isinstance(first_arg, ast.Call):
                        if isinstance(first_arg.func, ast.Attribute) and first_arg.func.attr == 'format':
                            self._add_issue(
                                node, Severity.CRITICAL, Category.SECURITY,
                                "检测到潜在的SQL注入风险 (.format() in SQL)",
                                "使用参数化查询替代字符串格式化",
                                self._get_snippet(node.lineno),
                                "SEC-005"
                            )
    
    def _check_logging_issues(self, node: ast.Call):
        """检查日志问题"""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == 'logging':
                # 检查是否在异常处理块外使用logging.exception
                if node.func.attr == 'exception':
                    self._add_issue(
                        node, Severity.MEDIUM, Category.BEST_PRACTICE,
                        "在非异常处理块中使用 logging.exception",
                        "logging.exception 应该只在except块中使用",
                        self._get_snippet(node.lineno),
                        "LOG-001"
                    )
    
    def _check_exception_handling(self, node: ast.ExceptHandler):
        """检查异常处理问题"""
        # 检查裸except
        if node.type is None:
            self._add_issue(
                node, Severity.HIGH, Category.CORRECTNESS,
                "使用裸except捕获所有异常",
                "捕获具体的异常类型，如 except ValueError:",
                self._get_snippet(node.lineno),
                "EXCEPT-001"
            )
        
        # 检查捕获Exception但没有处理
        elif isinstance(node.type, ast.Name) and node.type.id == 'Exception':
            has_logging = any(
                isinstance(stmt, ast.Expr) and 
                isinstance(stmt.value, ast.Call) and
                isinstance(stmt.value.func, ast.Attribute) and
                stmt.value.func.attr in ('error', 'exception', 'warning')
                for stmt in node.body
            )
            if not has_logging:
                self._add_issue(
                    node, Severity.MEDIUM, Category.MAINTAINABILITY,
                    "捕获Exception但没有记录日志",
                    "建议记录异常信息以便调试",
                    self._get_snippet(node.lineno),
                    "EXCEPT-002"
                )
        
        # 检查空的except块
        if not node.body or (len(node.body) == 1 and 
            isinstance(node.body[0], ast.Pass)):
            self._add_issue(
                node, Severity.HIGH, Category.CORRECTNESS,
                "空的异常处理块",
                "至少记录日志或重新抛出异常",
                self._get_snippet(node.lineno),
                "EXCEPT-003"
            )
        
        # 检查bare raise
        for stmt in node.body:
            if isinstance(stmt, ast.Raise) and stmt.exc is None:
                # 这是合法的，但检查是否有其他问题
                pass
    
    def _check_additional_rules(self):
        """检查其他规则（基于文本分析）"""
        for i, line in enumerate(self.lines, 1):
            # 检查硬编码敏感信息
            for pattern, desc, severity in self.SENSITIVE_PATTERNS:
                if re.search(pattern, line):
                    if not re.search(r'(?i)(getenv|config|settings|os\.environ)', line):
                        self._add_issue(
                            None, severity, Category.SECURITY,
                            f"检测到可能的{desc}",
                            "使用环境变量或密钥管理服务",
                            line.strip(),
                            "SEC-010"
                        )
            
            # 检查TODO/FIXME
            if re.search(r'#\s*(TODO|FIXME|XXX|HACK)', line, re.IGNORECASE):
                match = re.search(r'#\s*(TODO|FIXME|XXX|HACK)', line, re.IGNORECASE)
                self._add_issue(
                    None, Severity.LOW, Category.MAINTAINABILITY,
                    f"发现 {match.group(1)} 标记",
                    "尽快处理或创建正式的任务跟踪",
                    line.strip(),
                    "TODO-001"
                )
            
            # 检查print语句
            if re.search(r'(?<![\w.])print\s*\(', line):
                if 'test' not in self.filename.lower():
                    self._add_issue(
                        None, Severity.LOW, Category.BEST_PRACTICE,
                        "使用print语句进行输出",
                        "使用logging模块替代print，便于生产环境管理",
                        line.strip(),
                        "PRINT-001"
                    )
            
            # 检查与None的比较
            if re.search(r'\s==\s*None', line):
                self._add_issue(
                    None, Severity.LOW, Category.STYLE,
                    "使用 '== None' 进行比较",
                    "使用 'is None' 替代 '== None'",
                    line.strip(),
                    "STYLE-001"
                )
            
            if re.search(r'\s!=\s*None', line):
                self._add_issue(
                    None, Severity.LOW, Category.STYLE,
                    "使用 '!= None' 进行比较",
                    "使用 'is not None' 替代 '!= None'",
                    line.strip(),
                    "STYLE-002"
                )
            
            # 检查过长的行
            if len(line) > 120:
                self._add_issue(
                    None, Severity.LOW, Category.STYLE,
                    f"行过长 ({len(line)} 字符)",
                    "遵循PEP 8，行长度应不超过120字符",
                    line[:80] + "...",
                    "STYLE-003"
                )
            
            # 检查尾随空格
            if line.rstrip() != line.rstrip('\n').rstrip():
                self._add_issue(
                    None, Severity.INFO, Category.STYLE,
                    "行尾有尾随空格",
                    "删除行尾空格",
                    repr(line),
                    "STYLE-004"
                )
        
        # 检查未使用的导入
        unused = self.imported_names - self.used_names - {'__future__'}
        for name in unused:
            # 找到导入行
            for i, line in enumerate(self.lines, 1):
                if re.search(rf'\bimport\s+{re.escape(name)}\b', line) or \
                   re.search(rf'\bfrom\s+\S+\s+import\s+.*\b{re.escape(name)}\b', line):
                    self._add_issue(
                        None, Severity.LOW, Category.MAINTAINABILITY,
                        f"未使用的导入: '{name}'",
                        "删除未使用的导入",
                        line.strip(),
                        "IMPORT-001"
                    )
    
    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """获取属性的完整名称"""
        parts = [node.attr]
        current = node.value
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return '.'.join(reversed(parts))
    
    def _add_issue(self, node: Optional[ast.AST], severity: Severity, 
                   category: Category, message: str, suggestion: str, 
                   code_snippet: str = "", rule_id: str = ""):
        """添加问题记录"""
        line = node.lineno if node else 0
        column = node.col_offset if node else 0
        
        if not rule_id:
            rule_id = self._get_rule_id()
        
        self.issues.append(Issue(
            file=self.filename,
            line=line,
            column=column,
            severity=severity,
            category=category,
            message=message,
            suggestion=suggestion,
            code_snippet=code_snippet,
            rule_id=rule_id
        ))
    
    def _get_snippet(self, line_no: int, context: int = 2) -> str:
        """获取代码片段"""
        start = max(0, line_no - context - 1)
        end = min(len(self.lines), line_no + context)
        return '\n'.join(self.lines[start:end])


def review_file(filepath: str) -> List[Issue]:
    """审查单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        reviewer = PythonCodeReviewer(filepath, source)
        return reviewer.review()
    except Exception as e:
        return [Issue(
            file=filepath,
            line=0,
            column=0,
            severity=Severity.CRITICAL,
            category=Category.CORRECTNESS,
            message=f"无法读取文件: {str(e)}",
            suggestion="检查文件权限和编码",
            code_snippet="",
            rule_id="FILE-001"
        )]


def review_directory(directory: str) -> List[Issue]:
    """审查整个目录"""
    all_issues = []
    
    for root, dirs, files in os.walk(directory):
        # 跳过虚拟环境和依赖目录
        dirs[:] = [d for d in dirs if d not in 
                   {'.git', '__pycache__', 'venv', '.venv', 'node_modules', 
                    '.tox', '.pytest_cache', '.mypy_cache', 'dist', 'build'}]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                issues = review_file(filepath)
                all_issues.extend(issues)
    
    return all_issues


def generate_markdown_report(report: ReviewReport) -> str:
    """生成Markdown格式报告"""
    lines = [
        "# 代码审查报告",
        "",
        f"**目标**: {report.target}",
        f"**时间**: {report.timestamp}",
        f"**文件数**: {report.total_files}",
        f"**问题总数**: {report.total_issues}",
        "",
        "## 摘要",
        "",
        "### 按严重程度",
        ""
    ]
    
    for severity in ['critical', 'high', 'medium', 'low', 'info']:
        count = report.issues_by_severity.get(severity, 0)
        icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢', 'info': '🔵'}.get(severity, '⚪')
        lines.append(f"- {icon} **{severity.upper()}**: {count}")
    
    lines.extend(["", "### 按类别", ""])
    
    for category, count in sorted(report.issues_by_category.items()):
        lines.append(f"- **{category}**: {count}")
    
    lines.extend(["", "## 详细问题", ""])
    
    # 按严重程度分组
    severity_order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
    
    for severity in severity_order:
        issues = [i for i in report.issues if i.severity == severity]
        if issues:
            lines.extend([
                f"### {severity.value.upper()} ({len(issues)}个问题)",
                ""
            ])
            
            for issue in issues:
                lines.extend([
                    f"#### {issue.rule_id}: {issue.message}",
                    "",
                    f"- **文件**: `{issue.file}:{issue.line}`",
                    f"- **类别**: {issue.category.value}",
                    f"- **建议**: {issue.suggestion}",
                    "",
                    "**代码片段**:",
                    "```python",
                    issue.code_snippet,
                    "```",
                    ""
                ])
    
    return '\n'.join(lines)


def generate_html_report(report: ReviewReport) -> str:
    """生成HTML格式报告"""
    severity_colors = {
        'critical': '#dc3545',
        'high': '#fd7e14',
        'medium': '#ffc107',
        'low': '#28a745',
        'info': '#17a2b8'
    }
    
    severity_icons = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🟢',
        'info': '🔵'
    }
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>代码审查报告 - {report.target}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{ margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; }}
        .summary {{ 
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-card h3 {{ margin-bottom: 15px; color: #555; }}
        .severity-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        .severity-item:last-child {{ border-bottom: none; }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            color: white;
        }}
        .issues {{ background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .issue {{
            padding: 20px;
            border-bottom: 1px solid #eee;
        }}
        .issue:last-child {{ border-bottom: none; }}
        .issue-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }}
        .issue-title {{ font-size: 16px; font-weight: 600; }}
        .issue-meta {{ color: #666; font-size: 14px; margin-bottom: 10px; }}
        .issue-meta code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }}
        .issue-suggestion {{
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 10px;
            border-left: 3px solid #667eea;
        }}
        pre {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 13px;
        }}
        .filter-bar {{
            background: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .filter-btn {{
            padding: 6px 16px;
            border: 1px solid #ddd;
            border-radius: 20px;
            background: white;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .filter-btn:hover, .filter-btn.active {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>代码审查报告</h1>
            <p>目标: {report.target} | 时间: {report.timestamp}</p>
            <p>共审查 {report.total_files} 个文件，发现 {report.total_issues} 个问题</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>按严重程度</h3>
"""
    
    for severity in ['critical', 'high', 'medium', 'low', 'info']:
        count = report.issues_by_severity.get(severity, 0)
        color = severity_colors.get(severity, '#666')
        html += f'''
                <div class="severity-item">
                    <span>{severity_icons.get(severity, '⚪')} {severity.upper()}</span>
                    <span class="badge" style="background: {color}">{count}</span>
                </div>
'''
    
    html += """
            </div>
            <div class="summary-card">
                <h3>按类别</h3>
"""
    
    for category, count in sorted(report.issues_by_category.items()):
        html += f'''
                <div class="severity-item">
                    <span>{category}</span>
                    <span class="badge" style="background: #6c757d">{count}</span>
                </div>
'''
    
    html += """
            </div>
        </div>
        
        <div class="filter-bar">
            <button class="filter-btn active" onclick="filterIssues('all')">全部</button>
            <button class="filter-btn" onclick="filterIssues('critical')">严重</button>
            <button class="filter-btn" onclick="filterIssues('high')">高</button>
            <button class="filter-btn" onclick="filterIssues('medium')">中</button>
            <button class="filter-btn" onclick="filterIssues('low')">低</button>
        </div>
        
        <div class="issues">
"""
    
    # 按严重程度排序
    severity_order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
    
    for severity in severity_order:
        issues = [i for i in report.issues if i.severity == severity]
        for issue in issues:
            color = severity_colors.get(issue.severity.value, '#666')
            html += f'''
            <div class="issue" data-severity="{issue.severity.value}">
                <div class="issue-header">
                    <span class="badge" style="background: {color}">{issue.severity.value.upper()}</span>
                    <span class="issue-title">{issue.rule_id}: {issue.message}</span>
                </div>
                <div class="issue-meta">
                    <code>{issue.file}:{issue.line}</code> | 类别: {issue.category.value}
                </div>
                <div class="issue-suggestion">
                    <strong>建议:</strong> {issue.suggestion}
                </div>
                <pre><code>{issue.code_snippet}</code></pre>
            </div>
'''
    
    html += """
        </div>
    </div>
    
    <script>
        function filterIssues(severity) {
            const issues = document.querySelectorAll('.issue');
            const buttons = document.querySelectorAll('.filter-btn');
            
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            issues.forEach(issue => {
                if (severity === 'all' || issue.dataset.severity === severity) {
                    issue.style.display = 'block';
                } else {
                    issue.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
"""
    
    return html


def print_console_report(report: ReviewReport):
    """打印控制台报告"""
    if report.total_issues == 0:
        print("\n✅ 未发现任何问题！代码质量很好。\n")
        return
    
    print(f"\n{'='*80}")
    print(f"代码审查报告")
    print(f"{'='*80}")
    print(f"目标: {report.target}")
    print(f"时间: {report.timestamp}")
    print(f"文件数: {report.total_files}")
    print(f"问题总数: {report.total_issues}")
    print(f"{'='*80}")
    
    print("\n按严重程度:")
    severity_icons = {
        'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢', 'info': '🔵'
    }
    for severity in ['critical', 'high', 'medium', 'low', 'info']:
        count = report.issues_by_severity.get(severity, 0)
        icon = severity_icons.get(severity, '⚪')
        print(f"  {icon} {severity.upper()}: {count}")
    
    print("\n按类别:")
    for category, count in sorted(report.issues_by_category.items()):
        print(f"  • {category}: {count}")
    
    print(f"\n{'='*80}")
    print("详细问题")
    print(f"{'='*80}")
    
    # 按严重程度分组
    severity_order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
    
    for severity in severity_order:
        issues = [i for i in report.issues if i.severity == severity]
        if issues:
            print(f"\n[{severity.value.upper()}] 问题 ({len(issues)}个)")
            print('-' * 80)
            
            for issue in issues:
                print(f"\n📍 {issue.file}:{issue.line}:{issue.column}")
                print(f"   规则: {issue.rule_id}")
                print(f"   类别: {issue.category.value}")
                print(f"   问题: {issue.message}")
                print(f"   建议: {issue.suggestion}")
                if issue.code_snippet:
                    print(f"   代码:\n{issue.code_snippet}")


def main():
    parser = argparse.ArgumentParser(
        description='OpenClaw 代码审查工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python code_review.py myfile.py
  python code_review.py ./src --format json
  python code_review.py ./src --format html --output report.html
        """
    )
    parser.add_argument('target', help='目标文件或目录')
    parser.add_argument('--format', choices=['console', 'json', 'markdown', 'html'], 
                       default='console', help='输出格式')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--min-severity', choices=['critical', 'high', 'medium', 'low', 'info'],
                       default='info', help='最小严重级别')
    
    args = parser.parse_args()
    
    # 收集问题
    if os.path.isfile(args.target):
        issues = review_file(args.target)
        total_files = 1
    elif os.path.isdir(args.target):
        issues = review_directory(args.target)
        # 统计文件数
        total_files = 0
        for root, dirs, files in os.walk(args.target):
            dirs[:] = [d for d in dirs if d not in 
                       {'.git', '__pycache__', 'venv', '.venv', 'node_modules'}]
            total_files += sum(1 for f in files if f.endswith('.py'))
    else:
        print(f"错误: {args.target} 不是有效的文件或目录")
        sys.exit(1)
    
    # 过滤严重级别
    severity_levels = {
        'critical': [Severity.CRITICAL],
        'high': [Severity.CRITICAL, Severity.HIGH],
        'medium': [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM],
        'low': [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW],
        'info': [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
    }
    allowed_severities = severity_levels.get(args.min_severity, [])
    issues = [i for i in issues if i.severity in allowed_severities]
    
    # 生成报告
    report = ReviewReport(
        target=args.target,
        timestamp=datetime.now().isoformat(),
        total_files=total_files,
        total_issues=len(issues),
        issues_by_severity={
            'critical': sum(1 for i in issues if i.severity == Severity.CRITICAL),
            'high': sum(1 for i in issues if i.severity == Severity.HIGH),
            'medium': sum(1 for i in issues if i.severity == Severity.MEDIUM),
            'low': sum(1 for i in issues if i.severity == Severity.LOW),
            'info': sum(1 for i in issues if i.severity == Severity.INFO)
        },
        issues_by_category={
            category.value: sum(1 for i in issues if i.category == category)
            for category in set(i.category for i in issues)
        },
        issues=issues
    )
    
    # 输出报告
    if args.format == 'console':
        print_console_report(report)
    elif args.format == 'json':
        output = json.dumps(report.to_dict(), indent=2, ensure_ascii=False)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"JSON报告已保存到: {args.output}")
        else:
            print(output)
    elif args.format == 'markdown':
        output = generate_markdown_report(report)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Markdown报告已保存到: {args.output}")
        else:
            print(output)
    elif args.format == 'html':
        output = generate_html_report(report)
        output_path = args.output or 'code_review_report.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"HTML报告已保存到: {output_path}")
    
    # 如果有严重问题，返回非零退出码
    critical_count = sum(1 for i in issues if i.severity == Severity.CRITICAL)
    if critical_count > 0:
        print(f"\n⚠️  发现 {critical_count} 个严重问题，请立即修复！")
        sys.exit(1)


if __name__ == '__main__':
    main()
