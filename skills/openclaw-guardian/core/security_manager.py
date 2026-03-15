"""
安全管理器 - 检测技能包中的安全威胁
======================================

提供全面的安全扫描功能:
- 恶意代码检测
- 危险操作识别
- 敏感文件访问检查
- 网络操作监控
"""

import os
import re
import ast
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Threat:
    """威胁信息"""
    type: str  # malware, suspicious, dangerous_operation
    severity: str  # critical, high, medium, low
    description: str
    file_path: str
    line_number: int = 0
    code_snippet: str = ""
    recommendation: str = ""


class SecurityManager:
    """安全管理器类"""
    
    # 危险函数和模块模式
    DANGEROUS_PATTERNS = {
        'critical': [
            # 系统命令执行
            (r'os\.system\s*\(', '系统命令执行', '避免使用os.system，使用subprocess并验证输入'),
            (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', 'shell=True危险调用', '避免使用shell=True'),
            (r'subprocess\.Popen\s*\([^)]*shell\s*=\s*True', 'shell=True危险调用', '避免使用shell=True'),
            (r'eval\s*\(', 'eval执行', '避免使用eval，使用ast.literal_eval或json.loads'),
            (r'exec\s*\(', 'exec执行', '避免使用exec'),
            (r'compile\s*\([^)]*exec', '动态代码编译', '避免动态编译代码'),
            
            # 文件系统危险操作
            (r'os\.rmdir\s*\([^)]*/', '目录删除', '验证路径防止误删'),
            (r'shutil\.rmtree\s*\(', '递归删除', '验证路径防止误删'),
            (r'os\.remove\s*\([^)]*/', '文件删除', '验证路径防止误删'),
        ],
        'high': [
            # 网络相关
            (r'urllib\.request\.urlopen\s*\(', '网络请求', '验证URL安全性'),
            (r'requests\.(get|post|put|delete)\s*\(', 'HTTP请求', '验证目标地址'),
            (r'socket\.', 'Socket操作', '注意网络安全'),
            
            # 文件操作
            (r'open\s*\([^)]*["\']w', '文件写入', '验证写入路径'),
            (r'open\s*\([^)]*["\']a', '文件追加', '验证写入路径'),
            
            # 动态导入
            (r'__import__\s*\(', '动态导入', '验证导入模块'),
            (r'importlib\.import_module\s*\(', '动态导入', '验证导入模块'),
        ],
        'medium': [
            # 反射和元编程
            (r'getattr\s*\(', '反射调用', '注意属性访问安全'),
            (r'setattr\s*\(', '反射设置', '注意属性设置安全'),
            (r'hasattr\s*\(', '反射检查', '注意属性检查'),
            
            # 序列化
            (r'pickle\.(loads|load)\s*\(', 'Pickle反序列化', '避免反序列化不可信数据'),
            (r'yaml\.(load|unsafe_load)', 'YAML不安全加载', '使用yaml.safe_load'),
        ],
    }
    
    # 敏感文件路径模式
    SENSITIVE_PATHS = [
        r'/etc/passwd',
        r'/etc/shadow',
        r'\.ssh/',
        r'\.bashrc',
        r'\.bash_profile',
        r'\.zshrc',
        r'\.profile',
        r'\.gitconfig',
        r'\.netrc',
        r'\.aws/',
        r'\.kube/',
        r'AppData/Roaming/',
        r'Library/Application Support/',
    ]
    
    # 恶意代码特征（哈希或模式）
    MALWARE_SIGNATURES = {
        # 可以添加已知的恶意代码特征
    }
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化安全管理器
        
        Args:
            config: 安全配置
        """
        self.config = config or {}
        self.whitelist = set(self.config.get('whitelist', []))
        self.blacklist = set(self.config.get('blacklist', []))
        self.allowed_modules = set(self.config.get('allowed_modules', []))
        self.blocked_modules = set(self.config.get('blocked_modules', [
            'ctypes', 'mmap', 'resource', 'pty', 'gc', 'sysconfig'
        ]))
        
        # 扫描统计
        self.scan_count = 0
        self.threats_found = 0
    
    def scan_skill(self, skill_path: str) -> Dict[str, Any]:
        """
        扫描技能包安全性
        
        Args:
            skill_path: 技能包路径
            
        Returns:
            扫描结果
        """
        self.scan_count += 1
        threats: List[Threat] = []
        
        skill_path = Path(skill_path)
        
        if not skill_path.exists():
            return {
                'has_threats': True,
                'threats': [Threat('error', 'critical', '路径不存在', str(skill_path))],
                'risk_score': 100,
            }
        
        # 扫描所有Python文件
        python_files = list(skill_path.rglob('*.py'))
        
        for py_file in python_files:
            file_threats = self._scan_python_file(py_file)
            threats.extend(file_threats)
        
        # 扫描配置文件
        config_files = list(skill_path.rglob('*.json')) + list(skill_path.rglob('*.yaml')) + list(skill_path.rglob('*.yml'))
        
        for config_file in config_files:
            file_threats = self._scan_config_file(config_file)
            threats.extend(file_threats)
        
        # 检查文件权限
        permission_threats = self._check_file_permissions(skill_path)
        threats.extend(permission_threats)
        
        # 计算风险评分
        risk_score = self._calculate_risk_score(threats)
        
        if threats:
            self.threats_found += len(threats)
        
        return {
            'has_threats': len(threats) > 0,
            'threats': [self._threat_to_dict(t) for t in threats],
            'risk_score': risk_score,
            'files_scanned': len(python_files) + len(config_files),
        }
    
    def _scan_python_file(self, file_path: Path) -> List[Threat]:
        """扫描Python文件"""
        threats = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            return [Threat('error', 'high', f'无法读取文件: {e}', str(file_path))]
        
        # 1. 模式匹配检测
        for severity, patterns in self.DANGEROUS_PATTERNS.items():
            for pattern, description, recommendation in patterns:
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line):
                        threat = Threat(
                            type='dangerous_operation',
                            severity=severity,
                            description=description,
                            file_path=str(file_path),
                            line_number=i,
                            code_snippet=line.strip()[:100],
                            recommendation=recommendation
                        )
                        threats.append(threat)
        
        # 2. AST分析检测
        try:
            tree = ast.parse(content)
            ast_threats = self._analyze_ast(tree, file_path, lines)
            threats.extend(ast_threats)
        except SyntaxError:
            pass  # 语法错误会在其他地方处理
        
        # 3. 敏感路径访问检测
        for i, line in enumerate(lines, 1):
            for sensitive_path in self.SENSITIVE_PATHS:
                if sensitive_path in line:
                    threat = Threat(
                        type='sensitive_access',
                        severity='high',
                        description=f'访问敏感路径: {sensitive_path}',
                        file_path=str(file_path),
                        line_number=i,
                        code_snippet=line.strip()[:100],
                        recommendation='避免访问系统敏感路径'
                    )
                    threats.append(threat)
        
        # 4. 检查黑名单模块导入
        for blocked in self.blocked_modules:
            pattern = rf'(^|\s)import\s+{blocked}([.\s]|$)|(^|\s)from\s+{blocked}'
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    threat = Threat(
                        type='blocked_module',
                        severity='high',
                        description=f'导入被禁止的模块: {blocked}',
                        file_path=str(file_path),
                        line_number=i,
                        code_snippet=line.strip()[:100],
                        recommendation=f'避免使用{blocked}模块'
                    )
                    threats.append(threat)
        
        return threats
    
    def _analyze_ast(self, tree: ast.AST, file_path: Path, lines: List[str]) -> List[Threat]:
        """使用AST分析代码"""
        threats = []
        
        for node in ast.walk(tree):
            # 检测硬编码的敏感信息
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                value = node.value
                
                # 检测硬编码的密钥
                if re.search(r'(?i)(api[_-]?key|secret[_-]?key|password|token)\s*=\s*["\'][^"\']+["\']', value):
                    threat = Threat(
                        type='hardcoded_secret',
                        severity='critical',
                        description='可能存在硬编码的敏感信息',
                        file_path=str(file_path),
                        line_number=getattr(node, 'lineno', 0),
                        code_snippet=value[:100],
                        recommendation='使用环境变量或配置文件存储敏感信息'
                    )
                    threats.append(threat)
                
                # 检测可疑URL
                if re.search(r'https?://[^\s"\']+', value):
                    url = re.search(r'https?://[^\s"\']+', value).group()
                    if any(domain in url for domain in ['pastebin', 'gist.github', 'transfer.sh']):
                        threat = Threat(
                            type='suspicious_url',
                            severity='high',
                            description=f'包含可疑URL: {url}',
                            file_path=str(file_path),
                            line_number=getattr(node, 'lineno', 0),
                            code_snippet=value[:100],
                            recommendation='验证外部URL的安全性'
                        )
                        threats.append(threat)
            
            # 检测不安全的反序列化
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['loads', 'load']:
                        if isinstance(node.func.value, ast.Name):
                            if node.func.value.id == 'pickle':
                                threat = Threat(
                                    type='unsafe_deserialization',
                                    severity='critical',
                                    description='使用pickle进行反序列化',
                                    file_path=str(file_path),
                                    line_number=getattr(node, 'lineno', 0),
                                    code_snippet=lines[getattr(node, 'lineno', 1) - 1].strip()[:100],
                                    recommendation='避免反序列化不可信数据，使用json替代'
                                )
                                threats.append(threat)
        
        return threats
    
    def _scan_config_file(self, file_path: Path) -> List[Threat]:
        """扫描配置文件"""
        threats = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return threats
        
        # 检测配置文件中的敏感信息
        sensitive_patterns = [
            (r'(?i)["\']?password["\']?\s*[:=]\s*["\'][^"\']+["\']', '密码'),
            (r'(?i)["\']?secret["\']?\s*[:=]\s*["\'][^"\']+["\']', '密钥'),
            (r'(?i)["\']?api[_-]?key["\']?\s*[:=]\s*["\'][^"\']+["\']', 'API密钥'),
            (r'(?i)["\']?token["\']?\s*[:=]\s*["\'][^"\']+["\']', '令牌'),
            (r'(?i)["\']?private[_-]?key["\']?\s*[:=]\s*["\'][^"\']+["\']', '私钥'),
        ]
        
        for pattern, desc in sensitive_patterns:
            if re.search(pattern, content):
                threat = Threat(
                    type='hardcoded_secret',
                    severity='critical',
                    description=f'配置文件中可能包含硬编码的{desc}',
                    file_path=str(file_path),
                    recommendation='使用环境变量存储敏感配置'
                )
                threats.append(threat)
        
        return threats
    
    def _check_file_permissions(self, skill_path: Path) -> List[Threat]:
        """检查文件权限"""
        threats = []
        
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                try:
                    stat = file_path.stat()
                    mode = stat.st_mode
                    
                    # 检查是否全局可写
                    if mode & 0o002:
                        threat = Threat(
                            type='insecure_permission',
                            severity='medium',
                            description=f'文件全局可写: {file_path.name}',
                            file_path=str(file_path),
                            recommendation='移除全局写权限'
                        )
                        threats.append(threat)
                    
                    # 检查SUID/SGID位
                    if mode & 0o4000 or mode & 0o2000:
                        threat = Threat(
                            type='suid_sgid',
                            severity='high',
                            description=f'文件设置了SUID/SGID位: {file_path.name}',
                            file_path=str(file_path),
                            recommendation='移除不必要的SUID/SGID权限'
                        )
                        threats.append(threat)
                        
                except Exception:
                    pass
        
        return threats
    
    def _calculate_risk_score(self, threats: List[Threat]) -> int:
        """计算风险评分"""
        score = 0
        
        severity_weights = {
            'critical': 40,
            'high': 20,
            'medium': 10,
            'low': 5,
        }
        
        for threat in threats:
            score += severity_weights.get(threat.severity, 5)
        
        # 上限100
        return min(100, score)
    
    def _threat_to_dict(self, threat: Threat) -> Dict[str, Any]:
        """转换Threat为字典"""
        return {
            'type': threat.type,
            'severity': threat.severity,
            'description': threat.description,
            'file_path': threat.file_path,
            'line_number': threat.line_number,
            'code_snippet': threat.code_snippet,
            'recommendation': threat.recommendation,
        }
    
    def add_to_whitelist(self, skill_hash: str) -> None:
        """添加技能哈希到白名单"""
        self.whitelist.add(skill_hash)
    
    def add_to_blacklist(self, skill_hash: str) -> None:
        """添加技能哈希到黑名单"""
        self.blacklist.add(skill_hash)
    
    def is_whitelisted(self, skill_path: str) -> bool:
        """检查技能是否在白名单中"""
        skill_hash = self._calculate_hash(skill_path)
        return skill_hash in self.whitelist
    
    def is_blacklisted(self, skill_path: str) -> bool:
        """检查技能是否在黑名单中"""
        skill_hash = self._calculate_hash(skill_path)
        return skill_hash in self.blacklist
    
    def _calculate_hash(self, skill_path: str) -> str:
        """计算技能包哈希"""
        hasher = hashlib.sha256()
        skill_path = Path(skill_path)
        
        for file_path in sorted(skill_path.rglob('*')):
            if file_path.is_file():
                try:
                    with open(file_path, 'rb') as f:
                        hasher.update(f.read())
                except Exception:
                    pass
        
        return hasher.hexdigest()
