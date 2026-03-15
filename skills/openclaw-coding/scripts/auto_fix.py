#!/usr/bin/env python3
"""
OpenClaw 自动修复脚本
功能: 自动修复代码中的常见问题
用法: python auto_fix.py <file_or_directory> [--apply] [--dry-run]
"""

import ast
import re
import sys
import os
import argparse
from dataclasses import dataclass
from typing import List, Dict, Set, Optional, Tuple
from enum import Enum
from pathlib import Path


class FixType(Enum):
    """修复类型"""
    SYNTAX = "syntax"
    STYLE = "style"
    SECURITY = "security"
    BUG = "bug"
    PERFORMANCE = "performance"


class Confidence(Enum):
    """修复信心度"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Fix:
    """修复操作"""
    file: str
    line: int
    original: str
    replacement: str
    description: str
    fix_type: FixType
    confidence: Confidence
    applied: bool = False


class AutoFixer:
    """自动修复器"""
    
    def __init__(self, filename: str, source: str):
        self.filename = filename
        self.source = source
        self.lines = source.split('\n')
        self.fixes: List[Fix] = []
    
    def analyze(self) -> List[Fix]:
        """分析代码并生成修复建议"""
        try:
            tree = ast.parse(self.source)
            self._analyze_ast(tree)
            self._analyze_text()
        except SyntaxError as e:
            # 语法错误无法自动修复
            pass
        
        return self.fixes
    
    def _analyze_ast(self, tree: ast.AST):
        """基于AST的分析"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                self._fix_bare_except(node)
                self._fix_empty_except(node)
            elif isinstance(node, ast.Compare):
                self._fix_none_comparison(node)
            elif isinstance(node, ast.FunctionDef):
                self._fix_mutable_default(node)
    
    def _analyze_text(self):
        """基于文本的分析"""
        for i, line in enumerate(self.lines, 1):
            # 修复尾随空格
            self._fix_trailing_whitespace(line, i)
            
            # 修复print语句
            self._fix_print_statement(line, i)
            
            # 修复比较操作
            self._fix_comparison_operators(line, i)
            
            # 修复导入格式
            self._fix_import_format(line, i)
            
            # 修复类继承
            self._fix_class_inheritance(line, i)
    
    def _fix_bare_except(self, node: ast.ExceptHandler):
        """修复裸except"""
        if node.type is None:
            line_idx = node.lineno - 1
            original = self.lines[line_idx]
            
            # 替换为Exception
            replacement = original.replace('except:', 'except Exception:')
            
            self.fixes.append(Fix(
                file=self.filename,
                line=node.lineno,
                original=original,
                replacement=replacement,
                description="将裸except改为except Exception",
                fix_type=FixType.BUG,
                confidence=Confidence.HIGH
            ))
    
    def _fix_empty_except(self, node: ast.ExceptHandler):
        """修复空的except块"""
        if (len(node.body) == 1 and 
            isinstance(node.body[0], ast.Pass)):
            
            # 找到pass行
            for i in range(node.lineno - 1, min(node.lineno + 10, len(self.lines))):
                if 'pass' in self.lines[i]:
                    original = self.lines[i]
                    indent = len(original) - len(original.lstrip())
                    replacement = ' ' * indent + 'logging.exception("An error occurred")  # TODO: Add proper error handling'
                    
                    self.fixes.append(Fix(
                        file=self.filename,
                        line=i + 1,
                        original=original,
                        replacement=replacement,
                        description="在空的except块中添加日志记录",
                        fix_type=FixType.BUG,
                        confidence=Confidence.MEDIUM
                    ))
                    break
    
    def _fix_none_comparison(self, node: ast.Compare):
        """修复None比较"""
        if (len(node.ops) == 1 and 
            isinstance(node.ops[0], ast.Eq)):
            
            comparator = node.comparators[0]
            if isinstance(comparator, ast.Constant) and comparator.value is None:
                line_idx = node.lineno - 1
                original = self.lines[line_idx]
                
                if ' == None' in original:
                    replacement = original.replace(' == None', ' is None')
                    
                    self.fixes.append(Fix(
                        file=self.filename,
                        line=node.lineno,
                        original=original,
                        replacement=replacement,
                        description="使用'is None'替代'== None'",
                        fix_type=FixType.STYLE,
                        confidence=Confidence.HIGH
                    ))
                elif ' != None' in original:
                    replacement = original.replace(' != None', ' is not None')
                    
                    self.fixes.append(Fix(
                        file=self.filename,
                        line=node.lineno,
                        original=original,
                        replacement=replacement,
                        description="使用'is not None'替代'!= None'",
                        fix_type=FixType.STYLE,
                        confidence=Confidence.HIGH
                    ))
    
    def _fix_mutable_default(self, node: ast.FunctionDef):
        """修复可变默认参数"""
        for default in node.args.defaults + node.args.kw_defaults:
            if default and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                line_idx = node.lineno - 1
                original = self.lines[line_idx]
                
                # 添加注释标记
                if '# FIXME' not in original:
                    replacement = original + '  # FIXME: Avoid mutable default arguments'
                    
                    self.fixes.append(Fix(
                        file=self.filename,
                        line=node.lineno,
                        original=original,
                        replacement=replacement,
                        description="标记可变默认参数问题",
                        fix_type=FixType.BUG,
                        confidence=Confidence.MEDIUM
                    ))
    
    def _fix_trailing_whitespace(self, line: str, line_no: int):
        """修复尾随空格"""
        stripped = line.rstrip()
        if stripped != line.rstrip('\n').rstrip():
            self.fixes.append(Fix(
                file=self.filename,
                line=line_no,
                original=line,
                replacement=stripped,
                description="删除行尾尾随空格",
                fix_type=FixType.STYLE,
                confidence=Confidence.HIGH
            ))
    
    def _fix_print_statement(self, line: str, line_no: int):
        """修复print语句"""
        # 检查是否是print语句（非测试文件）
        if 'test' in self.filename.lower():
            return
        
        if re.search(r'(?<![\w.])print\s*\(', line):
            # 检查是否已经有logging导入
            has_logging_import = 'import logging' in self.source
            
            if has_logging_import:
                # 替换print为logging
                original = line
                match = re.search(r'print\s*\((.*)\)', line)
                if match:
                    content = match.group(1)
                    indent = len(line) - len(line.lstrip())
                    replacement = ' ' * indent + f'logging.info({content})'
                    
                    self.fixes.append(Fix(
                        file=self.filename,
                        line=line_no,
                        original=original,
                        replacement=replacement,
                        description="将print替换为logging.info",
                        fix_type=FixType.STYLE,
                        confidence=Confidence.MEDIUM
                    ))
    
    def _fix_comparison_operators(self, line: str, line_no: int):
        """修复比较操作符"""
        # 修复 == True
        if re.search(r'\s==\s*True(?![\w])', line):
            original = line
            replacement = re.sub(r'\s==\s*True(?![\w])', '', line)
            
            self.fixes.append(Fix(
                file=self.filename,
                line=line_no,
                original=original,
                replacement=replacement,
                description="简化真值判断",
                fix_type=FixType.STYLE,
                confidence=Confidence.HIGH
            ))
        
        # 修复 == False
        if re.search(r'\s==\s*False(?![\w])', line):
            original = line
            # 需要更智能的处理
            match = re.search(r'(\w+)\s*==\s*False', line)
            if match:
                var = match.group(1)
                replacement = line.replace(f'{var} == False', f'not {var}')
                
                self.fixes.append(Fix(
                    file=self.filename,
                    line=line_no,
                    original=original,
                    replacement=replacement,
                    description="简化假值判断",
                    fix_type=FixType.STYLE,
                    confidence=Confidence.HIGH
                ))
    
    def _fix_import_format(self, line: str, line_no: int):
        """修复导入格式"""
        # 修复 from x import * 
        if re.search(r'from\s+\S+\s+import\s+\*', line):
            # 不建议自动修复，添加注释
            pass
    
    def _fix_class_inheritance(self, line: str, line_no: int):
        """修复类继承"""
        # 修复 class Foo: 为 class Foo(object):
        match = re.search(r'^class\s+(\w+)\s*:\s*$', line.strip())
        if match:
            class_name = match.group(1)
            original = line
            indent = len(line) - len(line.lstrip())
            replacement = ' ' * indent + f'class {class_name}(object):'
            
            self.fixes.append(Fix(
                file=self.filename,
                line=line_no,
                original=original,
                replacement=replacement,
                description="添加显式object继承（Python 2兼容）",
                fix_type=FixType.STYLE,
                confidence=Confidence.LOW
            ))


def fix_file(filepath: str) -> List[Fix]:
    """修复单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        fixer = AutoFixer(filepath, source)
        return fixer.analyze()
    except Exception as e:
        return []


def fix_directory(directory: str) -> List[Fix]:
    """修复整个目录"""
    all_fixes = []
    
    for root, dirs, files in os.walk(directory):
        # 跳过虚拟环境和依赖目录
        dirs[:] = [d for d in dirs if d not in 
                   {'.git', '__pycache__', 'venv', '.venv', 'node_modules'}]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                fixes = fix_file(filepath)
                all_fixes.extend(fixes)
    
    return all_fixes


def apply_fixes(fixes: List[Fix], dry_run: bool = False) -> Dict[str, int]:
    """应用修复"""
    results = {}
    
    # 按文件分组
    by_file: Dict[str, List[Fix]] = {}
    for fix in fixes:
        if fix.file not in by_file:
            by_file[fix.file] = []
        by_file[fix.file].append(fix)
    
    for filepath, file_fixes in by_file.items():
        if dry_run:
            results[filepath] = len(file_fixes)
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 按行号降序排序，避免行号变化
            sorted_fixes = sorted(file_fixes, key=lambda f: f.line, reverse=True)
            
            applied_count = 0
            for fix in sorted_fixes:
                line_idx = fix.line - 1
                if line_idx < len(lines):
                    # 确保行内容匹配
                    if fix.original.strip() == lines[line_idx].strip():
                        lines[line_idx] = fix.replacement + '\n'
                        fix.applied = True
                        applied_count += 1
            
            # 写回文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            results[filepath] = applied_count
            
        except Exception as e:
            print(f"应用修复失败 {filepath}: {e}")
            results[filepath] = 0
    
    return results


def print_report(fixes: List[Fix]):
    """打印修复报告"""
    if not fixes:
        print("\n✅ 没有发现需要自动修复的问题\n")
        return
    
    # 按类型分组
    by_type: Dict[FixType, List[Fix]] = {
        fix_type: [] for fix_type in FixType
    }
    
    for fix in fixes:
        by_type[fix.fix_type].append(fix)
    
    print(f"\n{'='*80}")
    print(f"自动修复报告 - 共发现 {len(fixes)} 个可修复问题")
    print(f"{'='*80}")
    
    confidence_icons = {
        Confidence.HIGH: '✅',
        Confidence.MEDIUM: '⚠️',
        Confidence.LOW: '💡'
    }
    
    for fix_type in FixType:
        type_fixes = by_type[fix_type]
        if type_fixes:
            print(f"\n【{fix_type.value.upper()}】({len(type_fixes)}个)")
            print('-' * 80)
            
            for fix in type_fixes:
                icon = confidence_icons.get(fix.confidence, '•')
                print(f"\n{icon} {fix.file}:{fix.line}")
                print(f"   信心度: {fix.confidence.value}")
                print(f"   描述: {fix.description}")
                print(f"   原始: {fix.original.strip()}")
                print(f"   修复: {fix.replacement.strip()}")


def main():
    parser = argparse.ArgumentParser(
        description='OpenClaw 自动修复工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python auto_fix.py myfile.py              # 查看可修复的问题
  python auto_fix.py myfile.py --apply      # 应用修复
  python auto_fix.py ./src --apply --dry-run # 模拟应用修复
        """
    )
    parser.add_argument('target', help='目标文件或目录')
    parser.add_argument('--apply', action='store_true', help='应用修复')
    parser.add_argument('--dry-run', action='store_true', help='模拟运行')
    parser.add_argument('--min-confidence', choices=['high', 'medium', 'low'],
                       default='medium', help='最小信心级别')
    
    args = parser.parse_args()
    
    # 收集修复建议
    if os.path.isfile(args.target):
        fixes = fix_file(args.target)
    elif os.path.isdir(args.target):
        fixes = fix_directory(args.target)
    else:
        print(f"错误: {args.target} 不是有效的文件或目录")
        sys.exit(1)
    
    # 过滤信心级别
    confidence_levels = {
        'high': [Confidence.HIGH],
        'medium': [Confidence.HIGH, Confidence.MEDIUM],
        'low': [Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW]
    }
    allowed_confidence = confidence_levels.get(args.min_confidence, [])
    fixes = [f for f in fixes if f.confidence in allowed_confidence]
    
    # 打印报告
    print_report(fixes)
    
    # 应用修复
    if args.apply:
        if args.dry_run:
            print(f"\n[模拟运行] 将应用 {len(fixes)} 个修复")
            results = apply_fixes(fixes, dry_run=True)
            for filepath, count in results.items():
                print(f"  将修复 {filepath}: {count} 处")
        else:
            print(f"\n应用 {len(fixes)} 个修复...")
            results = apply_fixes(fixes, dry_run=False)
            
            total_applied = sum(results.values())
            print(f"\n成功应用了 {total_applied} 个修复:")
            for filepath, count in results.items():
                if count > 0:
                    print(f"  ✓ {filepath}: {count} 处")
            
            print("\n修复完成！建议:")
            print("  1. 运行测试验证更改")
            print("  2. 审查修改的代码")
            print("  3. 提交更改到版本控制")


if __name__ == '__main__':
    main()
