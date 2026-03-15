---
name: openclaw-coding
version: 1.0.0
description: 高水平编程技能包 - 包含代码编写、代码审查、代码优化、自动修复Bug等完整功能。专注于编写可靠、易维护、高质量的代码。
author: OpenClaw
tags: [coding, review, optimization, security, best-practices]
---

# OpenClaw 高水平编程技能包

> **目标**: 编写可靠性强、易于维护、水平卓越的代码。代码审查安全细致，能够自动修复Bug和优化代码。

---

## 目录

1. [核心原则](#核心原则)
2. [代码编写规范](#代码编写规范)
3. [代码审查流程](#代码审查流程)
4. [代码优化策略](#代码优化策略)
5. [安全编码规范](#安全编码规范)
6. [自动修复指南](#自动修复指南)
7. [语言特定规范](#语言特定规范)
8. [工具使用](#工具使用)

---

## 核心原则

### 1. 可靠性优先 (Reliability First)

```
✅ 所有代码必须经过边界条件测试
✅ 错误处理必须完整，不允许静默失败
✅ 关键路径必须有日志记录
✅ 并发代码必须有竞态条件防护
```

### 2. 可维护性 (Maintainability)

```
✅ 单一职责原则 (SRP) - 每个函数/类只做一件事
✅ 开闭原则 (OCP) - 对扩展开放，对修改关闭
✅ 代码自文档化 - 清晰的命名 > 注释
✅ 复杂度控制 - 圈复杂度 ≤ 10
```

### 3. 安全性 (Security)

```
✅ 零信任原则 - 不信任任何外部输入
✅ 最小权限原则 - 只授予必要的权限
✅ 纵深防御 - 多层安全机制
✅ 安全左移 - 在开发阶段就发现安全问题
```

---

## 代码编写规范

### 命名规范

```python
# ✅ 正确的命名
class UserAuthenticationService:  # 类名：名词，PascalCase
    MAX_RETRY_COUNT = 3           # 常量：全大写，下划线分隔
    
    def validate_user_credentials(self, username: str, password: str) -> bool:
        """验证用户凭据"""
        is_valid = self._check_password_hash(password)  # 变量：snake_case
        return is_valid

# ❌ 错误的命名
class userAuth:  # 类名不规范
    maxretry = 3   # 常量不规范
    
    def val(self, u, p):  # 函数名和参数名不清晰
        x = self.check(p)  # 变量名无意义
        return x
```

### 函数设计原则

```python
# ✅ 优秀的函数设计
def calculate_discounted_price(
    original_price: Decimal,
    discount_percentage: Decimal,
    minimum_purchase: Optional[Decimal] = None
) -> Result[Decimal, PricingError]:
    """
    计算折扣后的价格。
    
    Args:
        original_price: 原始价格，必须大于0
        discount_percentage: 折扣百分比，范围[0, 100]
        minimum_purchase: 最低购买金额要求
        
    Returns:
        Result包含折扣后的价格或错误信息
        
    Raises:
        不抛出异常，所有错误通过Result返回
    """
    # 参数验证
    if original_price <= 0:
        return Result.error(PricingError.INVALID_PRICE)
    
    if not (0 <= discount_percentage <= 100):
        return Result.error(PricingError.INVALID_DISCOUNT)
    
    # 检查最低购买要求
    if minimum_purchase and original_price < minimum_purchase:
        return Result.error(PricingError.BELOW_MINIMUM)
    
    # 计算折扣
    discount_amount = original_price * (discount_percentage / 100)
    final_price = original_price - discount_amount
    
    # 确保价格精度
    final_price = final_price.quantize(Decimal('0.01'))
    
    return Result.success(final_price)


# ❌ 糟糕的函数设计
def calc(p, d):  # 参数名不清晰，无类型提示
    if p > 0:    # 缺少边界检查
        return p * (1 - d/100)  # 魔法数字，无精度处理
    return 0     # 错误处理不当
```

### 错误处理规范

```python
# ✅ 完善的错误处理
from typing import Optional, TypeVar, Generic
from enum import Enum, auto
from dataclasses import dataclass
import logging

T = TypeVar('T')
E = TypeVar('E', bound=Exception)

class Result(Generic[T, E]):
    """函数式错误处理容器"""
    
    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        self._value = value
        self._error = error
    
    @staticmethod
    def success(value: T) -> 'Result[T, E]':
        return Result(value=value)
    
    @staticmethod
    def error(error: E) -> 'Result[T, E]':
        return Result(error=error)
    
    @property
    def is_success(self) -> bool:
        return self._error is None
    
    @property
    def is_error(self) -> bool:
        return self._error is not None
    
    def unwrap(self) -> T:
        if self.is_error:
            raise self._error
        return self._value
    
    def unwrap_or(self, default: T) -> T:
        return self._value if self.is_success else default


class DatabaseError(Enum):
    CONNECTION_FAILED = auto()
    QUERY_TIMEOUT = auto()
    RECORD_NOT_FOUND = auto()
    INTEGRITY_VIOLATION = auto()


@dataclass
class DatabaseException(Exception):
    error_type: DatabaseError
    message: str
    context: dict


def fetch_user_by_id(user_id: int) -> Result[User, DatabaseException]:
    """根据ID获取用户信息"""
    logger = logging.getLogger(__name__)
    
    try:
        # 参数验证
        if user_id <= 0:
            return Result.error(DatabaseException(
                error_type=DatabaseError.INTEGRITY_VIOLATION,
                message=f"Invalid user_id: {user_id}",
                context={"user_id": user_id}
            ))
        
        # 数据库操作
        connection = get_database_connection()
        cursor = connection.cursor()
        
        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))  # 参数化查询防SQL注入
        
        row = cursor.fetchone()
        
        if row is None:
            logger.warning(f"User not found: {user_id}")
            return Result.error(DatabaseException(
                error_type=DatabaseError.RECORD_NOT_FOUND,
                message=f"User with id {user_id} not found",
                context={"user_id": user_id}
            ))
        
        user = User.from_row(row)
        logger.info(f"Successfully fetched user: {user_id}")
        
        return Result.success(user)
        
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        return Result.error(DatabaseException(
            error_type=DatabaseError.CONNECTION_FAILED,
            message="Failed to connect to database",
            context={"original_error": str(e)}
        ))
        
    except psycopg2.extensions.QueryCanceledError as e:
        logger.error(f"Query timeout: {e}")
        return Result.error(DatabaseException(
            error_type=DatabaseError.QUERY_TIMEOUT,
            message="Database query timed out",
            context={"original_error": str(e)}
        ))
        
    except Exception as e:
        logger.exception(f"Unexpected error fetching user: {e}")
        return Result.error(DatabaseException(
            error_type=DatabaseError.INTEGRITY_VIOLATION,
            message="Unexpected error occurred",
            context={"original_error": str(e)}
        ))
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
```

### 并发安全规范

```python
# ✅ 线程安全的代码
import threading
from contextlib import contextmanager
from typing import Dict, Optional

class ThreadSafeCache:
    """线程安全的缓存实现"""
    
    def __init__(self, max_size: int = 1000):
        self._max_size = max_size
        self._cache: Dict[str, any] = {}
        self._lock = threading.RLock()  # 可重入锁
        self._access_count: Dict[str, int] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """线程安全的获取操作"""
        with self._lock:
            if key in self._cache:
                self._access_count[key] += 1
                return self._cache[key]
            return None
    
    def set(self, key: str, value: Any) -> None:
        """线程安全的设置操作"""
        with self._lock:
            # 检查容量
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._evict_lru()
            
            self._cache[key] = value
            self._access_count[key] = 0
    
    def _evict_lru(self) -> None:
        """淘汰最少使用的条目"""
        if not self._access_count:
            return
        
        lru_key = min(self._access_count, key=self._access_count.get)
        del self._cache[lru_key]
        del self._access_count[lru_key]


# ✅ 异步安全的代码
import asyncio
from asyncio import Lock

class AsyncRateLimiter:
    """异步速率限制器"""
    
    def __init__(self, max_requests: int, time_window: float):
        self._max_requests = max_requests
        self._time_window = time_window
        self._requests: List[float] = []
        self._lock = Lock()
    
    async def acquire(self) -> bool:
        """尝试获取请求许可"""
        async with self._lock:
            now = asyncio.get_event_loop().time()
            
            # 清理过期的请求记录
            cutoff = now - self._time_window
            self._requests = [t for t in self._requests if t > cutoff]
            
            # 检查是否超过限制
            if len(self._requests) >= self._max_requests:
                return False
            
            self._requests.append(now)
            return True
    
    @contextmanager
    async def limit(self):
        """上下文管理器形式的速率限制"""
        if not await self.acquire():
            raise RateLimitExceeded("Rate limit exceeded")
        try:
            yield
        finally:
            pass  # 请求计数会在时间窗口后自动清理
```

---

## 代码审查流程

### 审查检查清单

```markdown
## 代码审查检查清单

### 功能性检查
- [ ] 代码是否实现了需求规格说明中的所有功能
- [ ] 边界条件是否正确处理
- [ ] 错误路径是否被测试覆盖
- [ ] 并发场景是否有竞态条件

### 安全性检查
- [ ] 所有外部输入是否经过验证和清理
- [ ] 是否存在SQL注入、XSS等常见漏洞
- [ ] 敏感数据是否得到适当保护
- [ ] 权限检查是否完整

### 性能检查
- [ ] 是否存在明显的性能瓶颈
- [ ] 数据库查询是否优化（N+1问题）
- [ ] 内存使用是否合理
- [ ] 算法复杂度是否最优

### 可维护性检查
- [ ] 代码是否符合命名规范
- [ ] 函数是否遵循单一职责原则
- [ ] 圈复杂度是否在可接受范围内
- [ ] 是否有适当的文档和注释

### 测试检查
- [ ] 单元测试是否覆盖所有关键路径
- [ ] 集成测试是否验证组件交互
- [ ] 测试是否独立且可重复
- [ ] 测试命名是否清晰表达意图
```

### 自动化审查脚本

```python
#!/usr/bin/env python3
"""
代码审查自动化脚本
用法: python code_review.py <file_or_directory>
"""

import ast
import sys
import os
import re
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from enum import Enum
import json

class Severity(Enum):
    CRITICAL = "critical"    # 必须修复：安全漏洞、功能缺陷
    HIGH = "high"           # 强烈建议修复：性能问题、设计缺陷
    MEDIUM = "medium"       # 建议修复：代码风格、可维护性
    LOW = "low"             # 可选修复：格式问题

class Category(Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    CORRECTNESS = "correctness"
    STYLE = "style"

@dataclass
class Issue:
    file: str
    line: int
    column: int
    severity: Severity
    category: Category
    message: str
    suggestion: str
    code_snippet: str = ""

class CodeReviewer(ast.NodeVisitor):
    """Python代码审查器"""
    
    DANGEROUS_FUNCTIONS = {
        'eval', 'exec', 'compile', '__import__', 'input'
    }
    
    SQL_PATTERNS = [
        r'(?i)(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\s+',
        r'(?i)EXEC\s*\(',
        r'(?i)EXECUTE\s*\(',
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
                code_snippet=self.lines[e.lineno - 1] if e.lineno else ""
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
                self._get_snippet(node.lineno)
            )
        
        # 检查参数数量
        arg_count = len(node.args.args) + len(node.args.kwonlyargs)
        if arg_count > 5:
            self._add_issue(
                node, Severity.MEDIUM, Category.MAINTAINABILITY,
                f"函数 '{node.name}' 参数过多 ({arg_count} 个)",
                "考虑使用参数对象模式或拆分函数",
                self._get_snippet(node.lineno)
            )
        
        self.generic_visit(node)
        
        # 检查圈复杂度
        complexity = self.function_complexity.get(node.name, 1)
        if complexity > 10:
            self._add_issue(
                node, Severity.HIGH, Category.MAINTAINABILITY,
                f"函数 '{node.name}' 圈复杂度过高 ({complexity})",
                "简化条件逻辑，提取复杂条件为单独函数",
                self._get_snippet(node.lineno)
            )
        
        self.current_function = old_function
    
    def visit_If(self, node: ast.If):
        if self.current_function:
            self.function_complexity[self.current_function] += 1
        self.generic_visit(node)
    
    def visit_For(self, node: ast.For):
        if self.current_function:
            self.function_complexity[self.current_function] += 1
        self._check_for_loop_issues(node)
        self.generic_visit(node)
    
    def visit_While(self, node: ast.While):
        if self.current_function:
            self.function_complexity[self.current_function] += 1
        self._check_while_loop_issues(node)
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call):
        self._check_dangerous_calls(node)
        self._check_sql_injection(node)
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        self._check_exception_handling(node)
        self.generic_visit(node)
    
    def _check_dangerous_calls(self, node: ast.Call):
        """检查危险函数调用"""
        if isinstance(node.func, ast.Name):
            if node.func.id in self.DANGEROUS_FUNCTIONS:
                self._add_issue(
                    node, Severity.CRITICAL, Category.SECURITY,
                    f"使用危险函数 '{node.func.id}'",
                    f"避免使用 {node.func.id}，使用更安全的替代方案",
                    self._get_snippet(node.lineno)
                )
    
    def _check_sql_injection(self, node: ast.Call):
        """检查SQL注入风险"""
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ('execute', 'executemany'):
                # 检查第一个参数是否是格式化字符串
                if node.args and isinstance(node.args[0], ast.JoinedStr):
                    self._add_issue(
                        node, Severity.CRITICAL, Category.SECURITY,
                        "检测到潜在的SQL注入风险 (f-string in SQL)",
                        "使用参数化查询替代字符串拼接",
                        self._get_snippet(node.lineno)
                    )
    
    def _check_for_loop_issues(self, node: ast.For):
        """检查for循环问题"""
        # 检查是否在循环中修改迭代对象
        if isinstance(node.iter, ast.Name):
            loop_body = ast.dump(node.body)
            if f"Del({node.iter.id}" in loop_body or f"Store({node.iter.id}" in loop_body:
                self._add_issue(
                    node, Severity.HIGH, Category.CORRECTNESS,
                    "在迭代过程中修改迭代对象",
                    "创建列表副本后再修改: for item in list[:]:",
                    self._get_snippet(node.lineno)
                )
    
    def _check_while_loop_issues(self, node: ast.While):
        """检查while循环问题"""
        # 检查是否有退出的可能
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            # 检查是否有break
            body_dump = ast.dump(node.body)
            if 'Break' not in body_dump:
                self._add_issue(
                    node, Severity.CRITICAL, Category.CORRECTNESS,
                    "检测到无限循环 (while True without break)",
                    "添加退出条件或break语句",
                    self._get_snippet(node.lineno)
                )
    
    def _check_exception_handling(self, node: ast.ExceptHandler):
        """检查异常处理问题"""
        # 检查裸except
        if node.type is None:
            self._add_issue(
                node, Severity.HIGH, Category.CORRECTNESS,
                "使用裸except捕获所有异常",
                "捕获具体的异常类型，如 except ValueError:",
                self._get_snippet(node.lineno)
            )
        
        # 检查空的except块
        if not node.body or (len(node.body) == 1 and 
            isinstance(node.body[0], ast.Pass)):
            self._add_issue(
                node, Severity.HIGH, Category.CORRECTNESS,
                "空的异常处理块",
                "至少记录日志或重新抛出异常",
                self._get_snippet(node.lineno)
            )
        
        # 检查是否捕获了Exception但没有处理
        if isinstance(node.type, ast.Name) and node.type.id == 'Exception':
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
                    self._get_snippet(node.lineno)
                )
    
    def _check_additional_rules(self):
        """检查其他规则"""
        # 检查硬编码的敏感信息
        for i, line in enumerate(self.lines, 1):
            # 检查硬编码密码
            if re.search(r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']+["\']', line):
                if not re.search(r'(?i)(getenv|config|settings)', line):
                    self._add_issue(
                        None, Severity.CRITICAL, Category.SECURITY,
                        "检测到可能的硬编码密码",
                        "使用环境变量或密钥管理服务",
                        line.strip()
                    )
            
            # 检查硬编码API密钥
            if re.search(r'(?i)(api[_-]?key|apikey|secret[_-]?key)\s*=\s*["\'][^"\']{10,}["\']', line):
                self._add_issue(
                    None, Severity.CRITICAL, Category.SECURITY,
                    "检测到可能的硬编码API密钥",
                    "使用环境变量或密钥管理服务",
                    line.strip()
                )
            
            # 检查TODO/FIXME
            if re.search(r'#\s*(TODO|FIXME|XXX|HACK)', line, re.IGNORECASE):
                match = re.search(r'#\s*(TODO|FIXME|XXX|HACK)', line, re.IGNORECASE)
                self._add_issue(
                    None, Severity.LOW, Category.MAINTAINABILITY,
                    f"发现 {match.group(1)} 标记",
                    "尽快处理或创建正式的任务跟踪",
                    line.strip()
                )
    
    def _add_issue(self, node: Optional[ast.AST], severity: Severity, 
                   category: Category, message: str, suggestion: str, 
                   code_snippet: str = ""):
        """添加问题记录"""
        line = node.lineno if node else 0
        column = node.col_offset if node else 0
        
        self.issues.append(Issue(
            file=self.filename,
            line=line,
            column=column,
            severity=severity,
            category=category,
            message=message,
            suggestion=suggestion,
            code_snippet=code_snippet
        ))
    
    def _get_snippet(self, line_no: int, context: int = 2) -> str:
        """获取代码片段"""
        start = max(0, line_no - context - 1)
        end = min(len(self.lines), line_no + context)
        return '\n'.join(self.lines[start:end])


def review_file(filepath: str) -> List[Issue]:
    """审查单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    
    reviewer = CodeReviewer(filepath, source)
    return reviewer.review()


def review_directory(directory: str) -> List[Issue]:
    """审查整个目录"""
    all_issues = []
    
    for root, dirs, files in os.walk(directory):
        # 跳过虚拟环境和依赖目录
        dirs[:] = [d for d in dirs if d not in 
                   {'.git', '__pycache__', 'venv', '.venv', 'node_modules', '.tox'}]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                issues = review_file(filepath)
                all_issues.extend(issues)
    
    return all_issues


def print_report(issues: List[Issue]):
    """打印审查报告"""
    if not issues:
        print("✅ 未发现任何问题！代码质量很好。")
        return
    
    # 按严重程度和类别分组
    by_severity: Dict[Severity, List[Issue]] = {
        Severity.CRITICAL: [],
        Severity.HIGH: [],
        Severity.MEDIUM: [],
        Severity.LOW: []
    }
    
    for issue in issues:
        by_severity[issue.severity].append(issue)
    
    # 打印摘要
    total = len(issues)
    print(f"\n{'='*80}")
    print(f"代码审查报告 - 共发现 {total} 个问题")
    print(f"{'='*80}")
    print(f"严重: {len(by_severity[Severity.CRITICAL])} | "
          f"高: {len(by_severity[Severity.HIGH])} | "
          f"中: {len(by_severity[Severity.MEDIUM])} | "
          f"低: {len(by_severity[Severity.LOW])}")
    print(f"{'='*80}\n")
    
    # 打印详细问题
    for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
        if by_severity[severity]:
            print(f"\n[{severity.value.upper()}] 问题 ({len(by_severity[severity])}个)")
            print('-' * 80)
            
            for issue in by_severity[severity]:
                print(f"\n📍 {issue.file}:{issue.line}:{issue.column}")
                print(f"   类别: {issue.category.value}")
                print(f"   问题: {issue.message}")
                print(f"   建议: {issue.suggestion}")
                if issue.code_snippet:
                    print(f"   代码:\n{issue.code_snippet}")
    
    # 输出JSON格式（便于集成）
    print(f"\n{'='*80}")
    print("JSON格式输出:")
    print(f"{'='*80}")
    
    json_output = [
        {
            "file": i.file,
            "line": i.line,
            "column": i.column,
            "severity": i.severity.value,
            "category": i.category.value,
            "message": i.message,
            "suggestion": i.suggestion
        }
        for i in issues
    ]
    print(json.dumps(json_output, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python code_review.py <file_or_directory>")
        sys.exit(1)
    
    target = sys.argv[1]
    
    if os.path.isfile(target):
        issues = review_file(target)
    elif os.path.isdir(target):
        issues = review_directory(target)
    else:
        print(f"错误: {target} 不是有效的文件或目录")
        sys.exit(1)
    
    print_report(issues)
    
    # 如果有严重问题，返回非零退出码
    critical_count = sum(1 for i in issues if i.severity == Severity.CRITICAL)
    if critical_count > 0:
        sys.exit(1)
```

---

## 代码优化策略

### 性能优化模式

```python
# ✅ 使用生成器处理大数据
# 内存效率高，惰性求值
def process_large_file(filepath: str):
    """处理大文件，使用生成器避免内存溢出"""
    with open(filepath, 'r') as f:
        for line in f:
            yield process_line(line.strip())

# 使用
for result in process_large_file('huge_file.txt'):
    save_result(result)


# ✅ 使用lru_cache缓存计算结果
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    """带缓存的斐波那契计算"""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# ✅ 使用集合进行快速查找
# O(1) 查找 vs O(n) 列表查找
def find_duplicates(items: List[str]) -> Set[str]:
    """高效查找重复项"""
    seen = set()
    duplicates = set()
    
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    
    return duplicates


# ✅ 使用__slots__减少内存占用
class Point:
    """使用__slots__的轻量级类"""
    __slots__ = ['x', 'y']
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


# ✅ 使用预编译正则表达式
import re

# 模块级别编译，避免重复编译
EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

def validate_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(email))
```

### 重构模式

```python
# ❌ 重构前：长函数，多个职责
def process_order(order_data: dict) -> dict:
    # 验证订单
    if not order_data.get('items'):
        return {'error': 'No items'}
    if order_data.get('total', 0) <= 0:
        return {'error': 'Invalid total'}
    
    # 计算价格
    total = 0
    for item in order_data['items']:
        price = item['price'] * item['quantity']
        if item.get('discount'):
            price *= (1 - item['discount'])
        total += price
    
    # 应用优惠券
    if order_data.get('coupon'):
        coupon = get_coupon(order_data['coupon'])
        if coupon and coupon['valid']:
            total -= coupon['amount']
    
    # 计算税费
    tax = total * 0.08
    final_total = total + tax
    
    # 保存订单
    order_id = save_to_database({
        'items': order_data['items'],
        'subtotal': total,
        'tax': tax,
        'total': final_total
    })
    
    # 发送确认邮件
    send_email(
        order_data['customer_email'],
        'Order Confirmation',
        f'Your order {order_id} has been placed'
    )
    
    return {'order_id': order_id, 'total': final_total}


# ✅ 重构后：职责分离，单一职责
def validate_order(order_data: dict) -> Result[None, ValidationError]:
    """验证订单数据"""
    if not order_data.get('items'):
        return Result.error(ValidationError.NO_ITEMS)
    if order_data.get('total', 0) <= 0:
        return Result.error(ValidationError.INVALID_TOTAL)
    return Result.success(None)


def calculate_item_price(item: dict) -> Decimal:
    """计算单个商品价格"""
    price = Decimal(str(item['price'])) * item['quantity']
    if item.get('discount'):
        price *= (Decimal('1') - Decimal(str(item['discount'])))
    return price


def apply_coupon(subtotal: Decimal, coupon_code: str) -> Decimal:
    """应用优惠券"""
    coupon = get_coupon(coupon_code)
    if coupon and coupon['valid']:
        return max(Decimal('0'), subtotal - Decimal(str(coupon['amount'])))
    return subtotal


def calculate_tax(amount: Decimal, tax_rate: Decimal = Decimal('0.08')) -> Decimal:
    """计算税费"""
    return (amount * tax_rate).quantize(Decimal('0.01'))


class OrderService:
    """订单服务类"""
    
    def __init__(self, order_repo: OrderRepository, 
                 email_service: EmailService,
                 coupon_service: CouponService):
        self.order_repo = order_repo
        self.email_service = email_service
        self.coupon_service = coupon_service
    
    def process_order(self, order_data: dict) -> Result[Order, OrderError]:
        """处理订单的主流程"""
        # 验证
        validation = validate_order(order_data)
        if validation.is_error:
            return Result.error(OrderError.VALIDATION_FAILED)
        
        # 计算价格
        price_result = self._calculate_price(order_data)
        if price_result.is_error:
            return Result.error(price_result.error)
        
        price_breakdown = price_result.value
        
        # 保存订单
        order = self.order_repo.create(price_breakdown.to_dict())
        
        # 发送确认
        self.email_service.send_order_confirmation(
            order_data['customer_email'],
            order
        )
        
        return Result.success(order)
    
    def _calculate_price(self, order_data: dict) -> Result[PriceBreakdown, PricingError]:
        """计算订单价格"""
        subtotal = sum(
            calculate_item_price(item) 
            for item in order_data['items']
        )
        
        if order_data.get('coupon'):
            subtotal = apply_coupon(subtotal, order_data['coupon'])
        
        tax = calculate_tax(subtotal)
        total = subtotal + tax
        
        return Result.success(PriceBreakdown(
            subtotal=subtotal,
            tax=tax,
            total=total
        ))
```

---

## 安全编码规范

### 输入验证

```python
from pydantic import BaseModel, Field, validator
from typing import Optional
import re

class UserRegistration(BaseModel):
    """用户注册数据模型 - 自动验证"""
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=50,
        regex=r'^[a-zA-Z0-9_]+$'
    )
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=12)
    age: Optional[int] = Field(None, ge=13, le=120)
    
    @validator('password')
    def validate_password_strength(cls, v):
        """验证密码强度"""
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含大写字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含小写字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('密码必须包含特殊字符')
        return v
    
    @validator('username')
    def validate_username_not_reserved(cls, v):
        """验证用户名不是保留字"""
        reserved = {'admin', 'root', 'system', 'api', 'www'}
        if v.lower() in reserved:
            raise ValueError(f'用户名 "{v}" 是保留字')
        return v


# 使用
from fastapi import HTTPException

@app.post("/register")
async def register(data: UserRegistration):
    """注册端点 - 自动验证输入"""
    # 数据已经过验证
    user = await create_user(data)
    return {"message": "Registration successful"}
```

### 安全的数据库操作

```python
# ✅ 使用参数化查询防止SQL注入
async def get_user_by_email(email: str) -> Optional[User]:
    """安全的数据库查询"""
    query = """
        SELECT id, username, email, created_at 
        FROM users 
        WHERE email = $1 AND is_active = true
    """
    # 使用参数化查询，email被正确转义
    row = await db.fetchrow(query, email)
    return User.from_row(row) if row else None


# ❌ 危险的字符串拼接
def get_user_dangerous(email: str) -> Optional[User]:
    """不安全的查询 - 存在SQL注入风险"""
    query = f"SELECT * FROM users WHERE email = '{email}'"  # 危险！
    # 攻击者可以输入: ' OR '1'='1
    row = db.execute(query)
    return User.from_row(row)


# ✅ 使用ORM提供额外的安全层
from sqlalchemy import select
from sqlalchemy.orm import selectinload

async def get_user_with_orders(user_id: int) -> Optional[User]:
    """使用ORM安全查询"""
    query = (
        select(User)
        .where(User.id == user_id)
        .where(User.is_active == True)
        .options(selectinload(User.orders))
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()
```

### 安全的密码处理

```python
from bcrypt import hashpw, gensalt, checkpw
from cryptography.fernet import Fernet
import secrets
import hashlib
import hmac

class SecurityManager:
    """安全管理器"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """安全地哈希密码"""
        # 使用bcrypt自动处理salt
        salt = gensalt(rounds=12)  # 12轮迭代
        hashed = hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """验证密码"""
        return checkpw(
            password.encode('utf-8'),
            hashed.encode('utf-8')
        )
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """生成安全的随机令牌"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_csrf_token() -> str:
        """生成CSRF令牌"""
        return secrets.token_hex(32)
    
    @staticmethod
    def verify_csrf_token(token: str, expected_token: str) -> bool:
        """使用恒定时间比较验证CSRF令牌"""
        return hmac.compare_digest(token, expected_token)
    
    @staticmethod
    def hash_sensitive_data(data: str, secret_key: str) -> str:
        """哈希敏感数据用于日志记录"""
        return hmac.new(
            secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
```

---

## 自动修复指南

### 常见问题的自动修复

```python
#!/usr/bin/env python3
"""
代码自动修复脚本
用法: python auto_fix.py <file_or_directory> [--apply]
"""

import ast
import re
import sys
import os
import argparse
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Fix:
    """修复操作"""
    file: str
    line: int
    original: str
    replacement: str
    description: str
    applied: bool = False

class AutoFixer(ast.NodeVisitor):
    """自动代码修复器"""
    
    def __init__(self, filename: str, source: str):
        self.filename = filename
        self.source = source
        self.lines = source.split('\n')
        self.fixes: List[Fix] = []
    
    def analyze(self) -> List[Fix]:
        """分析代码并生成修复建议"""
        try:
            tree = ast.parse(self.source)
            self.visit(tree)
            self._analyze_patterns()
        except SyntaxError:
            pass  # 语法错误无法自动修复
        return self.fixes
    
    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        """修复裸except"""
        if node.type is None:
            line_idx = node.lineno - 1
            original = self.lines[line_idx]
            
            # 尝试推断可能的异常类型
            replacement = original.replace('except:', 'except Exception:')
            
            self.fixes.append(Fix(
                file=self.filename,
                line=node.lineno,
                original=original,
                replacement=replacement,
                description="将裸except改为except Exception"
            ))
        
        # 检查空的except块
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            line_idx = node.lineno - 1
            # 找到pass行
            for i in range(line_idx, min(line_idx + 10, len(self.lines))):
                if 'pass' in self.lines[i]:
                    original = self.lines[i]
                    replacement = original.replace('pass', 
                        'logging.exception("An error occurred")  # TODO: 添加适当的错误处理')
                    
                    self.fixes.append(Fix(
                        file=self.filename,
                        line=i + 1,
                        original=original,
                        replacement=replacement,
                        description="在空的except块中添加日志记录"
                    ))
                    break
        
        self.generic_visit(node)
    
    def visit_Compare(self, node: ast.Compare):
        """修复与None的比较"""
        if isinstance(node.ops[0], ast.Is):
            if isinstance(node.comparators[0], ast.Constant):
                if node.comparators[0].value is None:
                    # 检查是否是 x == None 而不是 x is None
                    line_idx = node.lineno - 1
                    original = self.lines[line_idx]
                    
                    # 简单的字符串替换（可能不完美，但能处理常见情况）
                    if ' == None' in original:
                        replacement = original.replace(' == None', ' is None')
                        self.fixes.append(Fix(
                            file=self.filename,
                            line=node.lineno,
                            original=original,
                            replacement=replacement,
                            description="使用'is None'替代'== None'"
                        ))
                    elif ' != None' in original:
                        replacement = original.replace(' != None', ' is not None')
                        self.fixes.append(Fix(
                            file=self.filename,
                            line=node.lineno,
                            original=original,
                            replacement=replacement,
                            description="使用'is not None'替代'!= None'"
                        ))
        
        self.generic_visit(node)
    
    def _analyze_patterns(self):
        """分析代码模式"""
        for i, line in enumerate(self.lines):
            line_no = i + 1
            
            # 修复print语句
            if re.search(r'(?<![\w.])print\s*\(', line):
                if 'import logging' not in self.source:
                    # 建议添加logging导入
                    pass
            
            # 修复可变默认参数
            if re.search(r'def\s+\w+\s*\([^)]*=\s*(\[|\{)', line):
                original = line
                # 这是一个复杂修复，需要重构函数定义
                # 简化处理：添加警告注释
                if '# FIXME' not in line:
                    replacement = line + '  # FIXME: 避免使用可变默认参数'
                    self.fixes.append(Fix(
                        file=self.filename,
                        line=line_no,
                        original=original,
                        replacement=replacement,
                        description="标记可变默认参数问题"
                    ))
            
            # 修复未使用的导入
            # 这需要更复杂的分析，简化处理
            
            # 修复字符串拼接
            if ' + ' in line and ('"' in line or "'" in line):
                # 可能是字符串拼接
                if line.count('"') >= 4 or line.count("'") >= 4:
                    if 'f"' not in line and "f'" not in line:
                        original = line
                        # 简单情况：尝试转换为f-string
                        # 这是一个简化版本，实际情况更复杂
                        pass


def apply_fixes(fixes: List[Fix], filepath: str) -> bool:
    """应用修复到文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 按行号降序排序，避免行号变化
        sorted_fixes = sorted(fixes, key=lambda f: f.line, reverse=True)
        
        for fix in sorted_fixes:
            line_idx = fix.line - 1
            if line_idx < len(lines):
                lines[line_idx] = lines[line_idx].replace(
                    fix.original, 
                    fix.replacement
                ) + '\n'
                fix.applied = True
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return True
    except Exception as e:
        print(f"应用修复失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='代码自动修复工具')
    parser.add_argument('target', help='目标文件或目录')
    parser.add_argument('--apply', action='store_true', help='应用修复')
    args = parser.parse_args()
    
    all_fixes = []
    
    if os.path.isfile(args.target):
        with open(args.target, 'r', encoding='utf-8') as f:
            source = f.read()
        fixer = AutoFixer(args.target, source)
        all_fixes = fixer.analyze()
    elif os.path.isdir(args.target):
        for root, dirs, files in os.walk(args.target):
            dirs[:] = [d for d in dirs if d not in 
                       {'.git', '__pycache__', 'venv', '.venv'}]
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        source = f.read()
                    fixer = AutoFixer(filepath, source)
                    all_fixes.extend(fixer.analyze())
    
    if not all_fixes:
        print("✅ 没有发现需要自动修复的问题")
        return
    
    print(f"\n发现 {len(all_fixes)} 个可自动修复的问题:\n")
    
    for i, fix in enumerate(all_fixes, 1):
        print(f"{i}. {fix.file}:{fix.line}")
        print(f"   描述: {fix.description}")
        print(f"   原始: {fix.original.strip()}")
        print(f"   修复: {fix.replacement.strip()}")
        print()
    
    if args.apply:
        print("应用修复...")
        # 按文件分组
        by_file = {}
        for fix in all_fixes:
            if fix.file not in by_file:
                by_file[fix.file] = []
            by_file[fix.file].append(fix)
        
        for filepath, fixes in by_file.items():
            if apply_fixes(fixes, filepath):
                applied_count = sum(1 for f in fixes if f.applied)
                print(f"  ✓ {filepath}: 应用了 {applied_count} 个修复")
        
        print("\n修复完成！建议运行测试验证更改。")
    else:
        print("使用 --apply 参数应用这些修复")


if __name__ == '__main__':
    main()
```

---

## 语言特定规范

### Python 规范

```python
"""
Python 编码规范速查
"""

# 类型提示
from typing import List, Dict, Optional, Union, Callable, TypeVar, Generic

T = TypeVar('T')

# 函数签名
async def process_items(
    items: List[Dict[str, Union[str, int]]],
    callback: Optional[Callable[[T], None]] = None,
    *,  # 强制关键字参数
    timeout: float = 30.0,
    retry_count: int = 3
) -> Dict[str, any]:
    """
    处理项目列表。
    
    Args:
        items: 待处理的项目列表
        callback: 处理完成后的回调函数
        timeout: 超时时间（秒）
        retry_count: 重试次数
        
    Returns:
        包含处理结果的字典
        
    Raises:
        TimeoutError: 处理超时
        ValueError: 输入数据无效
    """
    pass


# 类设计
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(frozen=True)  # 不可变数据类
class Point:
    x: float
    y: float
    
    def distance_to(self, other: 'Point') -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


class DataProcessor(ABC):
    """数据处理器抽象基类"""
    
    def __init__(self, config: dict):
        self._config = config
        self._logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def process(self, data: any) -> any:
        """处理数据 - 子类必须实现"""
        pass
    
    @property
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(self._config)


# 上下文管理器
from contextlib import asynccontextmanager

@asynccontextmanager
async def database_transaction():
    """数据库事务上下文"""
    conn = await get_connection()
    try:
        await conn.begin()
        yield conn
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise
    finally:
        await conn.close()


# 使用
async def update_user(user_id: int, data: dict):
    async with database_transaction() as conn:
        await conn.execute("UPDATE users SET ...", data)
```

### JavaScript/TypeScript 规范

```typescript
/**
 * TypeScript 编码规范速查
 */

// 接口定义
interface User {
  readonly id: string;        // 只读属性
  name: string;
  email: string;
  age?: number;               // 可选属性
  readonly createdAt: Date;
}

// 类型别名
type Result<T, E = Error> = 
  | { success: true; data: T }
  | { success: false; error: E };

// 泛型函数
async function fetchData<T>(
  url: string,
  options?: RequestInit
): Promise<Result<T>> {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      return {
        success: false,
        error: new Error(`HTTP ${response.status}: ${response.statusText}`)
      };
    }
    
    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return { 
      success: false, 
      error: error instanceof Error ? error : new Error(String(error))
    };
  }
}

// 类定义
class Cache<T> {
  private storage = new Map<string, T>();
  private readonly maxSize: number;
  
  constructor(maxSize: number = 100) {
    this.maxSize = maxSize;
  }
  
  get(key: string): T | undefined {
    return this.storage.get(key);
  }
  
  set(key: string, value: T): void {
    if (this.storage.size >= this.maxSize && !this.storage.has(key)) {
      const firstKey = this.storage.keys().next().value;
      this.storage.delete(firstKey);
    }
    this.storage.set(key, value);
  }
  
  clear(): void {
    this.storage.clear();
  }
}

// 工具类型
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object 
    ? DeepReadonly<T[P]> 
    : T[P];
};

// 常量枚举
const enum HttpStatus {
  OK = 200,
  Created = 201,
  BadRequest = 400,
  Unauthorized = 401,
  NotFound = 404,
  ServerError = 500
}
```

---

## 工具使用

### 推荐的开发工具

```yaml
# 代码质量工具
linters:
  python:
    - ruff        # 极速Python linter
    - black       # 代码格式化
    - mypy        # 静态类型检查
    - bandit      # 安全漏洞扫描
    
  javascript:
    - eslint      # JavaScript/TypeScript linter
    - prettier    # 代码格式化
    - tsc         # TypeScript编译器检查

testing:
  python:
    - pytest      # 测试框架
    - pytest-cov  # 覆盖率
    - hypothesis  # 属性测试
    
  javascript:
    - vitest      # 测试框架
    - playwright  # E2E测试

pre_commit:
  hooks:
    - id: trailing-whitespace
    - id: end-of-file-fixer
    - id: check-yaml
    - id: check-added-large-files
    - id: black
    - id: ruff
    - id: mypy
```

### 预提交钩子配置

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: local
    hooks:
      - id: code-review
        name: Code Review Check
        entry: python scripts/code_review.py
        language: system
        types: [python]
        pass_filenames: true
```

---

## 快速参考卡片

```
┌─────────────────────────────────────────────────────────────────┐
│                    OpenClaw 编码快速参考                         │
├─────────────────────────────────────────────────────────────────┤
│ 命名规范                                                         │
│  ├── 类: PascalCase (UserService)                               │
│  ├── 函数/变量: snake_case (get_user_by_id)                     │
│  ├── 常量: UPPER_SNAKE_CASE (MAX_RETRY_COUNT)                   │
│  └── 私有: _leading_underscore (_internal_method)               │
├─────────────────────────────────────────────────────────────────┤
│ 函数设计                                                         │
│  ├── 单一职责: 一个函数只做一件事                                │
│  ├── 参数数量: ≤ 5个，多用关键字参数                             │
│  ├── 函数长度: ≤ 50行，圈复杂度 ≤ 10                             │
│  └── 返回值: 使用Result模式处理错误                              │
├─────────────────────────────────────────────────────────────────┤
│ 安全检查                                                         │
│  ├── 输入验证: 不信任任何外部输入                                │
│  ├── SQL查询: 必须使用参数化查询                                 │
│  ├── 密码处理: 使用bcrypt，never明文存储                         │
│  └── 敏感数据: 环境变量，never硬编码                             │
├─────────────────────────────────────────────────────────────────┤
│ 性能优化                                                         │
│  ├── 大数据: 使用生成器，避免一次性加载                          │
│  ├── 缓存: @lru_cache 缓存重复计算                               │
│  ├── 查找: 使用set/dict，O(1) vs O(n)                            │
│  └── 正则: 预编译，避免重复编译                                  │
├─────────────────────────────────────────────────────────────────┤
│ 错误处理                                                         │
│  ├── 具体异常: 捕获具体类型，no裸except                          │
│  ├── 日志记录: 异常必须记录，使用logger.exception                │
│  ├── 资源释放: 使用try/finally或上下文管理器                     │
│  └── 错误传播: 使用Result模式，no静默失败                        │
└─────────────────────────────────────────────────────────────────┘
```

---

**文档版本**: 1.0.0  
**最后更新**: 2024年  
**维护者**: OpenClaw Team
