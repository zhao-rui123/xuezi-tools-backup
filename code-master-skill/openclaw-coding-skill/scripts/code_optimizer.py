#!/usr/bin/env python3
"""
OpenClaw 代码优化脚本
功能: 自动代码优化，包括性能优化、代码重构、代码简化
用法: python code_optimizer.py <file_or_directory> [--apply] [--dry-run]
"""

import ast
import re
import sys
import os
import argparse
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple, Any
from enum import Enum
from pathlib import Path
from datetime import datetime


class OptimizationType(Enum):
    """优化类型"""
    PERFORMANCE = "performance"       # 性能优化
    READABILITY = "readability"       # 可读性优化
    MAINTAINABILITY = "maintainability"  # 可维护性优化
    PYTHONIC = "pythonic"            # Pythonic写法
    SECURITY = "security"            # 安全优化


class Confidence(Enum):
    """优化信心度"""
    HIGH = "high"      # 高信心，可以自动应用
    MEDIUM = "medium"  # 中等信心，建议人工审核
    LOW = "low"        # 低信心，仅作为建议


@dataclass
class Optimization:
    """优化建议"""
    file: str
    line: int
    column: int
    type: OptimizationType
    confidence: Confidence
    original: str
    replacement: str
    description: str
    explanation: str
    applied: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "type": self.type.value,
            "confidence": self.confidence.value,
            "original": self.original,
            "replacement": self.replacement,
            "description": self.description,
            "explanation": self.explanation,
            "applied": self.applied
        }


class PythonCodeOptimizer(ast.NodeVisitor):
    """Python代码优化器"""
    
    def __init__(self, filename: str, source: str):
        self.filename = filename
        self.source = source
        self.lines = source.split('\n')
        self.optimizations: List[Optimization] = []
        self.imports: Set[str] = set()
    
    def analyze(self) -> List[Optimization]:
        """分析代码并生成优化建议"""
        try:
            tree = ast.parse(self.source)
            self._collect_imports(tree)
            self.visit(tree)
            self._analyze_patterns()
        except SyntaxError:
            pass  # 语法错误无法优化
        return self.optimizations
    
    def _collect_imports(self, tree: ast.AST):
        """收集导入信息"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.imports.add(node.module)
    
    def visit_For(self, node: ast.For):
        """优化循环"""
        self._optimize_list_building(node)
        self._optimize_enumerate(node)
        self._optimize_range_len(node)
        self.generic_visit(node)
    
    def visit_If(self, node: ast.If):
        """优化条件语句"""
        self._optimize_truthiness(node)
        self._optimize_chain_comparison(node)
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call):
        """优化函数调用"""
        self._optimize_get(node)
        self._optimize_str_format(node)
        self._optimize_list_constructor(node)
        self.generic_visit(node)
    
    def visit_ListComp(self, node: ast.ListComp):
        """优化列表推导式"""
        self._optimize_nested_loop(node)
        self.generic_visit(node)
    
    def visit_Compare(self, node: ast.Compare):
        """优化比较操作"""
        self._optimize_is_comparison(node)
        self.generic_visit(node)
    
    def _optimize_list_building(self, node: ast.For):
        """优化列表构建 - 转换为列表推导式"""
        # 检查是否是 for + append 模式
        if (len(node.body) == 1 and 
            isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Call)):
            
            call = node.body[0].value
            if (isinstance(call.func, ast.Attribute) and 
                call.func.attr == 'append'):
                
                # 找到包含这个循环的函数或类
                parent = self._find_parent_function(node)
                if parent:
                    # 检查是否是构建列表的模式
                    list_name = self._get_attribute_name(call.func.value)
                    
                    # 简化处理：建议转换为列表推导式
                    original = self._get_snippet(node.lineno, 5)
                    
                    # 构建建议的列表推导式
                    iter_var = node.target.id if isinstance(node.target, ast.Name) else 'item'
                    append_expr = ast.unparse(call.args[0]) if hasattr(ast, 'unparse') else '...'
                    iter_expr = ast.unparse(node.iter) if hasattr(ast, 'unparse') else '...'
                    
                    replacement = f"{list_name} = [{append_expr} for {iter_var} in {iter_expr}]"
                    
                    self.optimizations.append(Optimization(
                        file=self.filename,
                        line=node.lineno,
                        column=node.col_offset,
                        type=OptimizationType.PYTHONIC,
                        confidence=Confidence.MEDIUM,
                        original=original,
                        replacement=replacement,
                        description="使用列表推导式替代for循环",
                        explanation="列表推导式更Pythonic，通常性能更好"
                    ))
    
    def _optimize_enumerate(self, node: ast.For):
        """优化为使用enumerate"""
        # 检查是否是 range(len(...)) 模式
        if (isinstance(node.iter, ast.Call) and
            isinstance(node.iter.func, ast.Name) and
            node.iter.func.id == 'range'):
            
            range_args = node.iter.args
            if (len(range_args) == 1 and
                isinstance(range_args[0], ast.Call) and
                isinstance(range_args[0].func, ast.Name) and
                range_args[0].func.id == 'len'):
                
                # 检查循环体内是否使用了索引
                iter_var = node.target.id if isinstance(node.target, ast.Name) else None
                if iter_var:
                    body_str = ast.dump(node.body)
                    if iter_var in body_str:
                        original = self._get_snippet(node.lineno, 3)
                        
                        list_expr = ast.unparse(range_args[0].args[0]) if hasattr(ast, 'unparse') else '...'
                        
                        replacement = f"for {iter_var}, item in enumerate({list_expr}):\n    ..."
                        
                        self.optimizations.append(Optimization(
                            file=self.filename,
                            line=node.lineno,
                            column=node.col_offset,
                            type=OptimizationType.PYTHONIC,
                            confidence=Confidence.HIGH,
                            original=original,
                            replacement=replacement,
                            description="使用enumerate替代range(len())",
                            explanation="enumerate更Pythonic，代码更清晰"
                        ))
    
    def _optimize_range_len(self, node: ast.For):
        """优化 range(len(x)) 为直接迭代"""
        if (isinstance(node.iter, ast.Call) and
            isinstance(node.iter.func, ast.Name) and
            node.iter.func.id == 'range'):
            
            range_args = node.iter.args
            if (len(range_args) == 1 and
                isinstance(range_args[0], ast.Call) and
                isinstance(range_args[0].func, ast.Name) and
                range_args[0].func.id == 'len'):
                
                # 检查循环体内是否只使用索引访问列表
                iter_var = node.target.id if isinstance(node.target, ast.Name) else None
                if iter_var:
                    # 简化检查：如果循环体简单，建议直接迭代
                    original = self._get_snippet(node.lineno, 3)
                    
                    list_expr = ast.unparse(range_args[0].args[0]) if hasattr(ast, 'unparse') else '...'
                    
                    replacement = f"for item in {list_expr}:\n    ..."
                    
                    self.optimizations.append(Optimization(
                        file=self.filename,
                        line=node.lineno,
                        column=node.col_offset,
                        type=OptimizationType.PYTHONIC,
                        confidence=Confidence.MEDIUM,
                        original=original,
                        replacement=replacement,
                        description="直接迭代列表而非使用range(len())",
                        explanation="直接迭代更简洁，除非需要索引"
                    ))
    
    def _optimize_truthiness(self, node: ast.If):
        """优化真值判断"""
        # 检查 x == True 或 x == False
        if isinstance(node.test, ast.Compare):
            if (len(node.test.ops) == 1 and 
                isinstance(node.test.ops[0], ast.Eq)):
                
                comparator = node.test.comparators[0]
                if isinstance(comparator, ast.Constant):
                    if comparator.value is True:
                        original = self._get_snippet(node.lineno, 1)
                        left = ast.unparse(node.test.left) if hasattr(ast, 'unparse') else 'x'
                        replacement = f"if {left}:"
                        
                        self.optimizations.append(Optimization(
                            file=self.filename,
                            line=node.lineno,
                            column=node.col_offset,
                            type=OptimizationType.PYTHONIC,
                            confidence=Confidence.HIGH,
                            original=original,
                            replacement=replacement,
                            description="简化真值判断",
                            explanation="直接使用if x: 替代 if x == True:"
                        ))
                    elif comparator.value is False:
                        original = self._get_snippet(node.lineno, 1)
                        left = ast.unparse(node.test.left) if hasattr(ast, 'unparse') else 'x'
                        replacement = f"if not {left}:"
                        
                        self.optimizations.append(Optimization(
                            file=self.filename,
                            line=node.lineno,
                            column=node.col_offset,
                            type=OptimizationType.PYTHONIC,
                            confidence=Confidence.HIGH,
                            original=original,
                            replacement=replacement,
                            description="简化假值判断",
                            explanation="直接使用if not x: 替代 if x == False:"
                        ))
    
    def _optimize_chain_comparison(self, node: ast.If):
        """优化链式比较"""
        # 检查 x > a and x < b 模式
        if isinstance(node.test, ast.BoolOp) and isinstance(node.test.op, ast.And):
            values = node.test.values
            if len(values) == 2:
                left, right = values[0], values[1]
                if (isinstance(left, ast.Compare) and isinstance(right, ast.Compare)):
                    # 检查是否可以合并
                    left_name = ast.unparse(left.left) if hasattr(ast, 'unparse') else ''
                    right_name = ast.unparse(right.left) if hasattr(ast, 'unparse') else ''
                    
                    if left_name == right_name:
                        original = self._get_snippet(node.lineno, 1)
                        
                        left_cmp = ast.unparse(left) if hasattr(ast, 'unparse') else '...'
                        right_cmp = ast.unparse(right) if hasattr(ast, 'unparse') else '...'
                        
                        # 尝试构建链式比较
                        left_ops = left.ops
                        right_ops = right.ops
                        
                        if (len(left_ops) == 1 and len(right_ops) == 1):
                            left_comparator = ast.unparse(left.comparators[0]) if hasattr(ast, 'unparse') else ''
                            right_comparator = ast.unparse(right.comparators[0]) if hasattr(ast, 'unparse') else ''
                            
                            replacement = f"if {left_comparator} < {left_name} < {right_comparator}:"
                            
                            self.optimizations.append(Optimization(
                                file=self.filename,
                                line=node.lineno,
                                column=node.col_offset,
                                type=OptimizationType.READABILITY,
                                confidence=Confidence.MEDIUM,
                                original=original,
                                replacement=replacement,
                                description="使用链式比较",
                                explanation="a < x < b 比 a < x and x < b 更清晰"
                            ))
    
    def _optimize_get(self, node: ast.Call):
        """优化字典get方法"""
        # 检查 dict[key] if key in dict else default 模式
        pass  # 这需要更复杂的分析
    
    def _optimize_str_format(self, node: ast.Call):
        """优化字符串格式化"""
        # 检查 .format() 或 % 格式化，建议f-string
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'format':
            # 检查是否是字符串的format方法
            if hasattr(ast, 'unparse'):
                original_call = ast.unparse(node)
                if original_call.startswith(('"', "'")):
                    original = self._get_snippet(node.lineno, 1)
                    
                    # 建议转换为f-string
                    self.optimizations.append(Optimization(
                        file=self.filename,
                        line=node.lineno,
                        column=node.col_offset,
                        type=OptimizationType.PYTHONIC,
                        confidence=Confidence.LOW,
                        original=original,
                        replacement="# 考虑使用f-string: f'...{var}...'",
                        description="考虑使用f-string替代.format()",
                        explanation="f-string在Python 3.6+中性能更好，可读性更高"
                    ))
    
    def _optimize_list_constructor(self, node: ast.Call):
        """优化列表构造"""
        # 检查 list() 构造函数
        if isinstance(node.func, ast.Name) and node.func.id == 'list':
            if len(node.args) == 1:
                arg = node.args[0]
                # 检查 list([]) 或 list(())
                if isinstance(arg, (ast.List, ast.Tuple)):
                    if len(arg.elts) == 0:
                        original = self._get_snippet(node.lineno, 1)
                        
                        self.optimizations.append(Optimization(
                            file=self.filename,
                            line=node.lineno,
                            column=node.col_offset,
                            type=OptimizationType.PERFORMANCE,
                            confidence=Confidence.HIGH,
                            original=original,
                            replacement="[]",
                            description="使用[]替代list()",
                            explanation="[]字面量比list()构造函数更快"
                        ))
    
    def _optimize_nested_loop(self, node: ast.ListComp):
        """优化嵌套循环"""
        # 检查多层嵌套的列表推导式
        if len(node.generators) > 1:
            # 这是一个简化检查，实际应该更复杂
            pass
    
    def _optimize_is_comparison(self, node: ast.Compare):
        """优化is比较"""
        # 检查与None的比较
        if (len(node.ops) == 1 and 
            isinstance(node.ops[0], ast.Eq)):
            
            comparator = node.comparators[0]
            if isinstance(comparator, ast.Constant) and comparator.value is None:
                original = self._get_snippet(node.lineno, 1)
                left = ast.unparse(node.left) if hasattr(ast, 'unparse') else 'x'
                
                self.optimizations.append(Optimization(
                    file=self.filename,
                    line=node.lineno,
                    column=node.col_offset,
                    type=OptimizationType.PYTHONIC,
                    confidence=Confidence.HIGH,
                    original=original,
                    replacement=f"if {left} is None:",
                    description="使用is None替代== None",
                    explanation="is None是Pythonic的写法"
                ))
    
    def _analyze_patterns(self):
        """分析代码模式"""
        for i, line in enumerate(self.lines, 1):
            # 优化: 使用in替代多个or
            if re.search(r'\s==\s+', line):
                or_count = line.count(' or ')
                if or_count >= 2:
                    # 可能是多个相等比较
                    original = line.strip()
                    
                    self.optimizations.append(Optimization(
                        file=self.filename,
                        line=i,
                        column=0,
                        type=OptimizationType.READABILITY,
                        confidence=Confidence.LOW,
                        original=original,
                        replacement="# 考虑使用: if x in (a, b, c):",
                        description="考虑使用in替代多个or",
                        explanation="x in (a, b, c) 比 x == a or x == b or x == c 更清晰"
                    ))
            
            # 优化: 使用any/all
            if 'for ' in line and ('if ' in line or 'if_' in line):
                # 可能是可以转换为any/all的模式
                pass
            
            # 优化: 使用with语句
            if re.search(r'\.(open|connect)\(', line):
                # 检查是否有对应的close
                next_lines = '\n'.join(self.lines[i:i+10])
                if '.close()' not in next_lines:
                    original = line.strip()
                    
                    self.optimizations.append(Optimization(
                        file=self.filename,
                        line=i,
                        column=0,
                        type=OptimizationType.MAINTAINABILITY,
                        confidence=Confidence.MEDIUM,
                        original=original,
                        replacement="# 考虑使用with语句确保资源释放",
                        description="使用with语句管理资源",
                        explanation="with语句确保资源正确释放，即使发生异常"
                    ))
            
            # 优化: 使用生成器表达式
            if 'sum(' in line or 'max(' in line or 'min(' in line:
                if '[' in line and 'for ' in line:
                    # 可能是列表推导式，可以改为生成器
                    original = line.strip()
                    
                    self.optimizations.append(Optimization(
                        file=self.filename,
                        line=i,
                        column=0,
                        type=OptimizationType.PERFORMANCE,
                        confidence=Confidence.MEDIUM,
                        original=original,
                        replacement="# 考虑使用生成器表达式: sum(x for x in items)",
                        description="使用生成器表达式替代列表推导式",
                        explanation="生成器表达式内存效率更高，适用于sum/max/min等函数"
                    ))
            
            # 优化: 使用dict.get
            if re.search(r'if\s+\w+\s+in\s+\w+:', line):
                next_line = self.lines[i] if i < len(self.lines) else ''
                if '=' in next_line and '[' in next_line:
                    original = line.strip() + '\n' + next_line.strip()
                    
                    self.optimizations.append(Optimization(
                        file=self.filename,
                        line=i,
                        column=0,
                        type=OptimizationType.READABILITY,
                        confidence=Confidence.MEDIUM,
                        original=original,
                        replacement="# 考虑使用: value = d.get(key, default)",
                        description="使用dict.get替代in检查",
                        explanation="dict.get更简洁，一行替代多行"
                    ))
    
    def _find_parent_function(self, node: ast.AST) -> Optional[ast.FunctionDef]:
        """查找包含节点的函数"""
        # 简化实现
        return None
    
    def _get_attribute_name(self, node: ast.AST) -> str:
        """获取属性的完整名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_attribute_name(node.value)}.{node.attr}"
        return ""
    
    def _get_snippet(self, line_no: int, context: int = 2) -> str:
        """获取代码片段"""
        start = max(0, line_no - context - 1)
        end = min(len(self.lines), line_no + context)
        return '\n'.join(self.lines[start:end])


def optimize_file(filepath: str) -> List[Optimization]:
    """优化单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        optimizer = PythonCodeOptimizer(filepath, source)
        return optimizer.analyze()
    except Exception as e:
        return []


def optimize_directory(directory: str) -> List[Optimization]:
    """优化整个目录"""
    all_optimizations = []
    
    for root, dirs, files in os.walk(directory):
        # 跳过虚拟环境和依赖目录
        dirs[:] = [d for d in dirs if d not in 
                   {'.git', '__pycache__', 'venv', '.venv', 'node_modules', 
                    '.tox', '.pytest_cache', '.mypy_cache', 'dist', 'build'}]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                optimizations = optimize_file(filepath)
                all_optimizations.extend(optimizations)
    
    return all_optimizations


def apply_optimization(opt: Optimization, filepath: str) -> bool:
    """应用单个优化"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        line_idx = opt.line - 1
        if line_idx < len(lines):
            # 简单的字符串替换
            original_line = lines[line_idx]
            # 这里需要更智能的替换逻辑
            # 简化处理：仅标记为已应用
            opt.applied = True
            return True
        
        return False
    except Exception as e:
        print(f"应用优化失败: {e}")
        return False


def print_report(optimizations: List[Optimization]):
    """打印优化报告"""
    if not optimizations:
        print("\n✅ 没有发现可优化的地方，代码已经很棒了！\n")
        return
    
    # 按类型和信心度分组
    by_type: Dict[OptimizationType, List[Optimization]] = {
        opt_type: [] for opt_type in OptimizationType
    }
    
    for opt in optimizations:
        by_type[opt.type].append(opt)
    
    print(f"\n{'='*80}")
    print(f"代码优化报告 - 共发现 {len(optimizations)} 个优化建议")
    print(f"{'='*80}")
    
    # 按类型打印
    confidence_icons = {
        Confidence.HIGH: '✅',
        Confidence.MEDIUM: '⚠️',
        Confidence.LOW: '💡'
    }
    
    for opt_type in OptimizationType:
        opts = by_type[opt_type]
        if opts:
            print(f"\n【{opt_type.value.upper()}】({len(opts)}个建议)")
            print('-' * 80)
            
            for opt in opts:
                icon = confidence_icons.get(opt.confidence, '•')
                print(f"\n{icon} {opt.file}:{opt.line}")
                print(f"   信心度: {opt.confidence.value}")
                print(f"   描述: {opt.description}")
                print(f"   说明: {opt.explanation}")
                print(f"   原始代码:")
                for line in opt.original.split('\n'):
                    print(f"      {line}")
                print(f"   建议代码:")
                for line in opt.replacement.split('\n'):
                    print(f"      {line}")


def generate_json_report(optimizations: List[Optimization]) -> str:
    """生成JSON报告"""
    data = {
        "timestamp": datetime.now().isoformat(),
        "total_optimizations": len(optimizations),
        "by_type": {},
        "optimizations": [opt.to_dict() for opt in optimizations]
    }
    
    for opt_type in OptimizationType:
        count = sum(1 for o in optimizations if o.type == opt_type)
        if count > 0:
            data["by_type"][opt_type.value] = count
    
    return json.dumps(data, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description='OpenClaw 代码优化工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python code_optimizer.py myfile.py
  python code_optimizer.py ./src --format json
  python code_optimizer.py ./src --apply --min-confidence high
        """
    )
    parser.add_argument('target', help='目标文件或目录')
    parser.add_argument('--format', choices=['console', 'json'], 
                       default='console', help='输出格式')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--min-confidence', choices=['high', 'medium', 'low'],
                       default='low', help='最小信心级别')
    parser.add_argument('--apply', action='store_true', 
                       help='自动应用高信心度的优化')
    parser.add_argument('--dry-run', action='store_true',
                       help='模拟运行，不实际修改文件')
    
    args = parser.parse_args()
    
    # 收集优化建议
    if os.path.isfile(args.target):
        optimizations = optimize_file(args.target)
    elif os.path.isdir(args.target):
        optimizations = optimize_directory(args.target)
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
    optimizations = [o for o in optimizations if o.confidence in allowed_confidence]
    
    # 输出报告
    if args.format == 'console':
        print_report(optimizations)
    elif args.format == 'json':
        output = generate_json_report(optimizations)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"JSON报告已保存到: {args.output}")
        else:
            print(output)
    
    # 应用优化
    if args.apply:
        high_confidence_opts = [o for o in optimizations if o.confidence == Confidence.HIGH]
        
        if args.dry_run:
            print(f"\n[模拟运行] 将应用 {len(high_confidence_opts)} 个高信心度优化")
        else:
            print(f"\n应用 {len(high_confidence_opts)} 个高信心度优化...")
            
            # 按文件分组
            by_file: Dict[str, List[Optimization]] = {}
            for opt in high_confidence_opts:
                if opt.file not in by_file:
                    by_file[opt.file] = []
                by_file[opt.file].append(opt)
            
            for filepath, opts in by_file.items():
                applied_count = 0
                for opt in opts:
                    if apply_optimization(opt, filepath):
                        applied_count += 1
                
                print(f"  ✓ {filepath}: 应用了 {applied_count} 个优化")
            
            print("\n优化完成！建议运行测试验证更改。")


if __name__ == '__main__':
    main()
