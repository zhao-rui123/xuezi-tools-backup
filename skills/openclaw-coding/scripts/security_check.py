#!/usr/bin/env python3
"""
OpenClaw 安全检查脚本
功能: 检测代码中的安全漏洞和风险
用法: python security_check.py <file_or_directory> [--format json|html]
"""

import ast
import re
import sys
import os
import json
import argparse
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any
from enum import Enum
from datetime import datetime


class Severity(Enum):
    """漏洞严重程度"""
    CRITICAL = "critical"    # 必须立即修复
    HIGH = "high"           # 强烈建议修复
    MEDIUM = "medium"       # 建议修复
    LOW = "low"             # 可选修复


class VulnerabilityType(Enum):
    """漏洞类型"""
    INJECTION = "injection"              # 注入攻击
    XSS = "xss"                          # 跨站脚本
    CSRF = "csrf"                        # 跨站请求伪造
    AUTH = "authentication"              # 认证问题
    CRYPTO = "cryptography"              # 加密问题
    CONFIG = "configuration"             # 配置问题
    DATA_EXPOSURE = "data_exposure"      # 数据泄露
    ACCESS_CONTROL = "access_control"    # 访问控制


@dataclass
class Vulnerability:
    """安全漏洞"""
    file: str
    line: int
    column: int
    severity: Severity
    vuln_type: VulnerabilityType
    cwe_id: str
    message: str
    suggestion: str
    code_snippet: str
    references: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "severity": self.severity.value,
            "type": self.vuln_type.value,
            "cwe_id": self.cwe_id,
            "message": self.message,
            "suggestion": self.suggestion,
            "code_snippet": self.code_snippet,
            "references": self.references
        }


class SecurityChecker(ast.NodeVisitor):
    """安全检查器"""
    
    # 危险函数
    DANGEROUS_FUNCTIONS = {
        'eval': {'cwe': 'CWE-95', 'type': VulnerabilityType.INJECTION},
        'exec': {'cwe': 'CWE-95', 'type': VulnerabilityType.INJECTION},
        'compile': {'cwe': 'CWE-95', 'type': VulnerabilityType.INJECTION},
        '__import__': {'cwe': 'CWE-78', 'type': VulnerabilityType.INJECTION},
        'input': {'cwe': 'CWE-94', 'type': VulnerabilityType.INJECTION},
        'os.system': {'cwe': 'CWE-78', 'type': VulnerabilityType.INJECTION},
        'os.popen': {'cwe': 'CWE-78', 'type': VulnerabilityType.INJECTION},
        'subprocess.call': {'cwe': 'CWE-78', 'type': VulnerabilityType.INJECTION},
        'subprocess.Popen': {'cwe': 'CWE-78', 'type': VulnerabilityType.INJECTION},
        'pickle.loads': {'cwe': 'CWE-502', 'type': VulnerabilityType.INJECTION},
        'yaml.load': {'cwe': 'CWE-502', 'type': VulnerabilityType.INJECTION},
        'marshal.loads': {'cwe': 'CWE-502', 'type': VulnerabilityType.INJECTION},
    }
    
    # 硬编码敏感信息模式
    SENSITIVE_PATTERNS = [
        {
            'pattern': r'(?i)(password|passwd|pwd|secret_key)\s*=\s*["\'][^"\']+["\']',
            'name': '硬编码密码',
            'cwe': 'CWE-798',
            'type': VulnerabilityType.CONFIG,
            'severity': Severity.CRITICAL
        },
        {
            'pattern': r'(?i)(api[_-]?key|apikey)\s*=\s*["\'][^"\']{10,}["\']',
            'name': '硬编码API密钥',
            'cwe': 'CWE-798',
            'type': VulnerabilityType.CONFIG,
            'severity': Severity.CRITICAL
        },
        {
            'pattern': r'(?i)(token|access_token|auth_token)\s*=\s*["\'][^"\']{10,}["\']',
            'name': '硬编码令牌',
            'cwe': 'CWE-798',
            'type': VulnerabilityType.CONFIG,
            'severity': Severity.CRITICAL
        },
        {
            'pattern': r'(?i)private[_-]?key\s*=\s*["\'][^"\']{20,}["\']',
            'name': '硬编码私钥',
            'cwe': 'CWE-798',
            'type': VulnerabilityType.CRYPTO,
            'severity': Severity.CRITICAL
        },
        {
            'pattern': r'(?i)aws_access_key_id\s*=\s*["\'][^"\']+["\']',
            'name': '硬编码AWS密钥',
            'cwe': 'CWE-798',
            'type': VulnerabilityType.CONFIG,
            'severity': Severity.CRITICAL
        },
    ]
    
    # SQL注入风险模式
    SQL_KEYWORDS = [
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'TRUNCATE', 'EXEC', 'EXECUTE', 'UNION'
    ]
    
    def __init__(self, filename: str, source: str):
        self.filename = filename
        self.source = source
        self.lines = source.split('\n')
        self.vulnerabilities: List[Vulnerability] = []
        self.in_try_block = False
    
    def check(self) -> List[Vulnerability]:
        """执行安全检查"""
        try:
            tree = ast.parse(self.source)
            self.visit(tree)
            self._check_text_patterns()
            self._check_django_security()
            self._check_flask_security()
        except SyntaxError:
            pass
        
        return self.vulnerabilities
    
    def visit_Call(self, node: ast.Call):
        """检查函数调用"""
        self._check_dangerous_functions(node)
        self._check_sql_injection(node)
        self._check_xss_vulnerabilities(node)
        self._check_weak_crypto(node)
        self._check_insecure_deserialization(node)
        self.generic_visit(node)
    
    def visit_Try(self, node: ast.Try):
        """检查异常处理"""
        self.in_try_block = True
        self.generic_visit(node)
        self.in_try_block = False
    
    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        """检查异常处理"""
        self._check_information_disclosure(node)
        self.generic_visit(node)
    
    def _check_dangerous_functions(self, node: ast.Call):
        """检查危险函数调用"""
        func_name = self._get_func_name(node.func)
        
        if func_name in self.DANGEROUS_FUNCTIONS:
            info = self.DANGEROUS_FUNCTIONS[func_name]
            
            self._add_vulnerability(
                node=node,
                severity=Severity.CRITICAL,
                vuln_type=info['type'],
                cwe_id=info['cwe'],
                message=f"使用危险函数 '{func_name}'",
                suggestion=f"避免使用 {func_name}，使用更安全的替代方案",
                references=[
                    f"https://cwe.mitre.org/data/definitions/{info['cwe'].split('-')[1]}.html"
                ]
            )
    
    def _check_sql_injection(self, node: ast.Call):
        """检查SQL注入"""
        if not isinstance(node.func, ast.Attribute):
            return
        
        if node.func.attr not in ('execute', 'executemany', 'executescript', 
                                   'raw', 'extra'):
            return
        
        if not node.args:
            return
        
        first_arg = node.args[0]
        
        # 检查f-string
        if isinstance(first_arg, ast.JoinedStr):
            self._add_sql_injection_vuln(node, "f-string in SQL")
            return
        
        # 检查%格式化
        if isinstance(first_arg, ast.BinOp) and isinstance(first_arg.op, ast.Mod):
            self._add_sql_injection_vuln(node, "% formatting in SQL")
            return
        
        # 检查.format()
        if isinstance(first_arg, ast.Call):
            if isinstance(first_arg.func, ast.Attribute) and first_arg.func.attr == 'format':
                self._add_sql_injection_vuln(node, ".format() in SQL")
                return
        
        # 检查字符串拼接
        if isinstance(first_arg, ast.BinOp) and isinstance(first_arg.op, ast.Add):
            self._add_sql_injection_vuln(node, "string concatenation in SQL")
            return
    
    def _add_sql_injection_vuln(self, node: ast.Call, method: str):
        """添加SQL注入漏洞"""
        self._add_vulnerability(
            node=node,
            severity=Severity.CRITICAL,
            vuln_type=VulnerabilityType.INJECTION,
            cwe_id='CWE-89',
            message=f"检测到潜在的SQL注入风险 ({method})",
            suggestion="使用参数化查询替代字符串拼接，如: cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))",
            references=[
                "https://cwe.mitre.org/data/definitions/89.html",
                "https://owasp.org/www-community/attacks/SQL_Injection"
            ]
        )
    
    def _check_xss_vulnerabilities(self, node: ast.Call):
        """检查XSS漏洞"""
        if not isinstance(node.func, ast.Attribute):
            return
        
        # 检查模板渲染
        if node.func.attr in ('render_template_string', 'render_template_string'):
            if node.args:
                # 检查是否使用了用户输入
                self._check_user_input_in_template(node)
        
        # 检查mark_safe
        if node.func.attr == 'mark_safe':
            self._add_vulnerability(
                node=node,
                severity=Severity.HIGH,
                vuln_type=VulnerabilityType.XSS,
                cwe_id='CWE-79',
                message="使用mark_safe可能存在XSS风险",
                suggestion="确保mark_safe的内容已经过适当的转义",
                references=[
                    "https://cwe.mitre.org/data/definitions/79.html",
                    "https://owasp.org/www-community/attacks/xss/"
                ]
            )
    
    def _check_user_input_in_template(self, node: ast.Call):
        """检查模板中是否使用了用户输入"""
        # 简化检查
        pass
    
    def _check_weak_crypto(self, node: ast.Call):
        """检查弱加密"""
        func_name = self._get_func_name(node.func)
        
        weak_algorithms = {
            'hashlib.md5': ('MD5', 'CWE-328'),
            'hashlib.sha1': ('SHA1', 'CWE-328'),
            'cryptography.hazmat.primitives.hashes.MD5': ('MD5', 'CWE-328'),
            'cryptography.hazmat.primitives.hashes.SHA1': ('SHA1', 'CWE-328'),
        }
        
        if func_name in weak_algorithms:
            algo, cwe = weak_algorithms[func_name]
            self._add_vulnerability(
                node=node,
                severity=Severity.HIGH,
                vuln_type=VulnerabilityType.CRYPTO,
                cwe_id=cwe,
                message=f"使用弱哈希算法 {algo}",
                suggestion=f"使用更强的哈希算法，如SHA-256或SHA-3",
                references=[
                    f"https://cwe.mitre.org/data/definitions/{cwe.split('-')[1]}.html"
                ]
            )
    
    def _check_insecure_deserialization(self, node: ast.Call):
        """检查不安全的反序列化"""
        func_name = self._get_func_name(node.func)
        
        dangerous_deserializers = ['pickle.loads', 'yaml.load', 'marshal.loads']
        
        if func_name in dangerous_deserializers:
            self._add_vulnerability(
                node=node,
                severity=Severity.CRITICAL,
                vuln_type=VulnerabilityType.INJECTION,
                cwe_id='CWE-502',
                message=f"不安全的反序列化: {func_name}",
                suggestion="使用安全的反序列化方法，如yaml.safe_load()或json.loads()",
                references=[
                    "https://cwe.mitre.org/data/definitions/502.html",
                    "https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data"
                ]
            )
    
    def _check_information_disclosure(self, node: ast.ExceptHandler):
        """检查信息泄露"""
        # 检查是否将异常信息返回给用户
        for stmt in node.body:
            if isinstance(stmt, ast.Return):
                if isinstance(stmt.value, ast.Call):
                    func_name = self._get_func_name(stmt.value.func)
                    if 'str' in func_name or 'repr' in func_name:
                        if isinstance(stmt.value.args[0], ast.Name):
                            # 可能是返回异常信息
                            self._add_vulnerability(
                                node=stmt,
                                severity=Severity.MEDIUM,
                                vuln_type=VulnerabilityType.DATA_EXPOSURE,
                                cwe_id='CWE-209',
                                message="可能向用户暴露敏感的错误信息",
                                suggestion="返回通用的错误信息，将详细错误记录到日志",
                                references=[
                                    "https://cwe.mitre.org/data/definitions/209.html"
                                ]
                            )
    
    def _check_text_patterns(self):
        """检查文本模式"""
        for i, line in enumerate(self.lines, 1):
            # 检查硬编码敏感信息
            for pattern_info in self.SENSITIVE_PATTERNS:
                if re.search(pattern_info['pattern'], line):
                    # 检查是否使用了环境变量
                    if not re.search(r'(?i)(getenv|environ|config|settings)', line):
                        self._add_text_vulnerability(
                            line_no=i,
                            line=line,
                            severity=pattern_info['severity'],
                            vuln_type=pattern_info['type'],
                            cwe_id=pattern_info['cwe'],
                            message=f"检测到可能的{pattern_info['name']}",
                            suggestion="使用环境变量或密钥管理服务存储敏感信息"
                        )
            
            # 检查调试模式
            if re.search(r'(?i)debug\s*=\s*True', line):
                self._add_text_vulnerability(
                    line_no=i,
                    line=line,
                    severity=Severity.HIGH,
                    vuln_type=VulnerabilityType.CONFIG,
                    cwe_id='CWE-489',
                    message="生产环境中启用调试模式",
                    suggestion="在生产环境中禁用调试模式"
                )
            
            # 检查不安全的CORS
            if re.search(r'(?i)cors.*\*', line):
                self._add_text_vulnerability(
                    line_no=i,
                    line=line,
                    severity=Severity.MEDIUM,
                    vuln_type=VulnerabilityType.CONFIG,
                    cwe_id='CWE-346',
                    message="CORS配置允许所有来源",
                    suggestion="限制CORS只允许特定的可信域名"
                )
            
            # 检查不安全的SSL/TLS
            if re.search(r'(?i)verify\s*=\s*False', line):
                self._add_text_vulnerability(
                    line_no=i,
                    line=line,
                    severity=Severity.HIGH,
                    vuln_type=VulnerabilityType.CRYPTO,
                    cwe_id='CWE-295',
                    message="禁用SSL证书验证",
                    suggestion="不要禁用SSL验证，使用正确的证书"
                )
    
    def _check_django_security(self):
        """检查Django特定的安全问题"""
        if 'django' not in self.source.lower():
            return
        
        # 检查CSRF保护
        for i, line in enumerate(self.lines, 1):
            if '@csrf_exempt' in line:
                self._add_text_vulnerability(
                    line_no=i,
                    line=line,
                    severity=Severity.MEDIUM,
                    vuln_type=VulnerabilityType.CSRF,
                    cwe_id='CWE-352',
                    message="禁用CSRF保护",
                    suggestion="确保该端点确实不需要CSRF保护"
                )
    
    def _check_flask_security(self):
        """检查Flask特定的安全问题"""
        if 'flask' not in self.source.lower():
            return
        
        # 检查密钥配置
        has_secret_key = False
        for line in self.lines:
            if 'SECRET_KEY' in line:
                has_secret_key = True
                break
        
        if not has_secret_key:
            # 这是一个模块级别的检查，不太精确
            pass
    
    def _get_func_name(self, node: ast.AST) -> str:
        """获取函数完整名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_func_name(node.value)}.{node.attr}"
        return ""
    
    def _add_vulnerability(self, node: ast.AST, severity: Severity,
                          vuln_type: VulnerabilityType, cwe_id: str,
                          message: str, suggestion: str,
                          references: List[str] = None):
        """添加漏洞记录"""
        line = node.lineno if node else 0
        column = node.col_offset if node else 0
        
        self.vulnerabilities.append(Vulnerability(
            file=self.filename,
            line=line,
            column=column,
            severity=severity,
            vuln_type=vuln_type,
            cwe_id=cwe_id,
            message=message,
            suggestion=suggestion,
            code_snippet=self._get_snippet(line),
            references=references or []
        ))
    
    def _add_text_vulnerability(self, line_no: int, line: str,
                                severity: Severity, vuln_type: VulnerabilityType,
                                cwe_id: str, message: str, suggestion: str):
        """添加基于文本的漏洞记录"""
        self.vulnerabilities.append(Vulnerability(
            file=self.filename,
            line=line_no,
            column=0,
            severity=severity,
            vuln_type=vuln_type,
            cwe_id=cwe_id,
            message=message,
            suggestion=suggestion,
            code_snippet=line.strip(),
            references=[f"https://cwe.mitre.org/data/definitions/{cwe_id.split('-')[1]}.html"]
        ))
    
    def _get_snippet(self, line_no: int, context: int = 2) -> str:
        """获取代码片段"""
        start = max(0, line_no - context - 1)
        end = min(len(self.lines), line_no + context)
        return '\n'.join(self.lines[start:end])


def check_file(filepath: str) -> List[Vulnerability]:
    """检查单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        checker = SecurityChecker(filepath, source)
        return checker.check()
    except Exception as e:
        return []


def check_directory(directory: str) -> List[Vulnerability]:
    """检查整个目录"""
    all_vulns = []
    
    for root, dirs, files in os.walk(directory):
        # 跳过虚拟环境和依赖目录
        dirs[:] = [d for d in dirs if d not in 
                   {'.git', '__pycache__', 'venv', '.venv', 'node_modules',
                    '.tox', '.pytest_cache', '.mypy_cache', 'dist', 'build'}]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                vulns = check_file(filepath)
                all_vulns.extend(vulns)
    
    return all_vulns


def generate_html_report(vulns: List[Vulnerability]) -> str:
    """生成HTML报告"""
    severity_colors = {
        'critical': '#dc3545',
        'high': '#fd7e14',
        'medium': '#ffc107',
        'low': '#28a745'
    }
    
    severity_icons = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🟢'
    }
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>安全扫描报告</title>
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
            background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{ margin-bottom: 10px; }}
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
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            color: white;
        }}
        .vuln {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            padding: 20px;
        }}
        .vuln-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }}
        .vuln-title {{ font-size: 16px; font-weight: 600; }}
        .vuln-meta {{ color: #666; font-size: 14px; margin-bottom: 10px; }}
        .vuln-meta code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }}
        .vuln-suggestion {{
            background: #fff3cd;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 10px;
            border-left: 3px solid #ffc107;
        }}
        pre {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 13px;
        }}
        .cwe-link {{
            color: #667eea;
            text-decoration: none;
        }}
        .cwe-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 安全扫描报告</h1>
            <p>扫描时间: {datetime.now().isoformat()}</p>
            <p>共发现 {len(vulns)} 个安全问题</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>按严重程度</h3>
"""
    
    # 按严重程度统计
    severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    for v in vulns:
        severity_counts[v.severity.value] = severity_counts.get(v.severity.value, 0) + 1
    
    for severity in ['critical', 'high', 'medium', 'low']:
        count = severity_counts.get(severity, 0)
        color = severity_colors.get(severity, '#666')
        html += f'''
                <div class="severity-item">
                    <span>{severity_icons.get(severity, '⚪')} {severity.upper()}</span>
                    <span class="badge" style="background: {color}">{count}</span>
                </div>
'''
    
    html += """
            </div>
        </div>
"""
    
    # 按严重程度排序
    severity_order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]
    
    for severity in severity_order:
        severity_vulns = [v for v in vulns if v.severity == severity]
        for vuln in severity_vulns:
            color = severity_colors.get(vuln.severity.value, '#666')
            html += f'''
        <div class="vuln">
            <div class="vuln-header">
                <span class="badge" style="background: {color}">{vuln.severity.value.upper()}</span>
                <span class="vuln-title">{vuln.cwe_id}: {vuln.message}</span>
            </div>
            <div class="vuln-meta">
                <code>{vuln.file}:{vuln.line}</code> | 
                类型: {vuln.vuln_type.value} | 
                <a href="https://cwe.mitre.org/data/definitions/{vuln.cwe_id.split('-')[1]}.html" 
                   class="cwe-link" target="_blank">CWE详情</a>
            </div>
            <div class="vuln-suggestion">
                <strong>修复建议:</strong> {vuln.suggestion}
            </div>
            <pre><code>{vuln.code_snippet}</code></pre>
        </div>
'''
    
    html += """
    </div>
</body>
</html>
"""
    
    return html


def print_report(vulns: List[Vulnerability]):
    """打印报告"""
    if not vulns:
        print("\n✅ 未发现安全问题！\n")
        return
    
    print(f"\n{'='*80}")
    print(f"🔒 安全扫描报告 - 共发现 {len(vulns)} 个问题")
    print(f"{'='*80}")
    
    # 按严重程度统计
    severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    for v in vulns:
        severity_counts[v.severity.value] = severity_counts.get(v.severity.value, 0) + 1
    
    print("\n按严重程度:")
    severity_icons = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
    for severity in ['critical', 'high', 'medium', 'low']:
        count = severity_counts.get(severity, 0)
        icon = severity_icons.get(severity, '⚪')
        print(f"  {icon} {severity.upper()}: {count}")
    
    print(f"\n{'='*80}")
    print("详细问题")
    print(f"{'='*80}")
    
    # 按严重程度排序
    severity_order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]
    
    for severity in severity_order:
        severity_vulns = [v for v in vulns if v.severity == severity]
        if severity_vulns:
            print(f"\n[{severity.value.upper()}] 问题 ({len(severity_vulns)}个)")
            print('-' * 80)
            
            for vuln in severity_vulns:
                print(f"\n📍 {vuln.file}:{vuln.line}")
                print(f"   CWE: {vuln.cwe_id}")
                print(f"   类型: {vuln.vuln_type.value}")
                print(f"   问题: {vuln.message}")
                print(f"   建议: {vuln.suggestion}")
                if vuln.references:
                    print(f"   参考: {', '.join(vuln.references)}")
                if vuln.code_snippet:
                    print(f"   代码:\n{vuln.code_snippet}")


def main():
    parser = argparse.ArgumentParser(
        description='OpenClaw 安全检查工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python security_check.py myfile.py
  python security_check.py ./src --format json
  python security_check.py ./src --format html --output report.html
        """
    )
    parser.add_argument('target', help='目标文件或目录')
    parser.add_argument('--format', choices=['console', 'json', 'html'],
                       default='console', help='输出格式')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--min-severity', choices=['critical', 'high', 'medium', 'low'],
                       default='low', help='最小严重级别')
    
    args = parser.parse_args()
    
    # 收集漏洞
    if os.path.isfile(args.target):
        vulns = check_file(args.target)
    elif os.path.isdir(args.target):
        vulns = check_directory(args.target)
    else:
        print(f"错误: {args.target} 不是有效的文件或目录")
        sys.exit(1)
    
    # 过滤严重级别
    severity_levels = {
        'critical': [Severity.CRITICAL],
        'high': [Severity.CRITICAL, Severity.HIGH],
        'medium': [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM],
        'low': [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]
    }
    allowed_severities = severity_levels.get(args.min_severity, [])
    vulns = [v for v in vulns if v.severity in allowed_severities]
    
    # 输出报告
    if args.format == 'console':
        print_report(vulns)
    elif args.format == 'json':
        output = json.dumps(
            [v.to_dict() for v in vulns],
            indent=2,
            ensure_ascii=False
        )
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"JSON报告已保存到: {args.output}")
        else:
            print(output)
    elif args.format == 'html':
        output = generate_html_report(vulns)
        output_path = args.output or 'security_report.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"HTML报告已保存到: {output_path}")
    
    # 如果有严重漏洞，返回非零退出码
    critical_count = sum(1 for v in vulns if v.severity == Severity.CRITICAL)
    if critical_count > 0:
        print(f"\n⚠️  发现 {critical_count} 个严重安全漏洞，请立即修复！")
        sys.exit(1)


if __name__ == '__main__':
    main()
