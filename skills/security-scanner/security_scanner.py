#!/usr/bin/env python3
"""
技能包安全检查工具 - 安装前扫描潜在风险
"""

import os
import sys
import re
import subprocess
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class SecurityIssue:
    """安全问题"""
    level: str  # critical/warning/info
    category: str
    description: str
    file: str
    line: int = 0

class SkillSecurityScanner:
    """技能包安全扫描器"""
    
    # 危险模式
    DANGEROUS_PATTERNS = {
        'network_exfil': [
            (r'curl\s+.*https?://[^\s\'"]+', "HTTP请求可能泄露数据"),
            (r'wget\s+.*https?://', "下载外部文件"),
            (r'fetch\(["\']https?://', "JavaScript网络请求"),
        ],
        'code_execution': [
            (r'eval\s*\(', "使用eval执行代码"),
            (r'exec\s*\(', "使用exec执行代码"),
            (r'os\.system\s*\(', "执行系统命令"),
            (r'subprocess\.(call|run|Popen)\s*\(', "调用子进程"),
            # 命令替换，但排除Markdown代码块中的示例
            # (r'\`[^`]+\`', "命令替换可能危险"),
        ],
        'file_operations': [
            (r'rm\s+-rf\s+', "强制递归删除"),
            (r'>\s*/\w+', "写入系统文件"),
            (r'chmod\s+777', "设置全权限"),
        ],
        'credential_access': [
            (r'password\s*=\s*["\'][^"\']+["\']', "硬编码密码"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "硬编码API Key"),
            (r'token\s*=\s*["\'][^"\']+["\']', "硬编码Token"),
            (r'~/.ssh/', "访问SSH密钥"),
            (r'~/.aws/', "访问AWS凭证"),
        ],
        'data_collection': [
            (r'whoami', "获取用户信息"),
            (r'id\s*$', "获取用户ID"),
            (r'uname\s+-a', "获取系统信息"),
            (r'hostname', "获取主机名"),
            (r'ifconfig|ip\s+addr', "获取网络信息"),
        ],
    }
    
    # 文件权限风险
    RISKY_EXTENSIONS = {'.exe', '.dll', '.so', '.dylib', '.bin'}
    
    def __init__(self, skill_path: str):
        self.skill_path = skill_path
        self.issues: List[SecurityIssue] = []
        self.files_checked = 0
    
    def scan(self) -> List[SecurityIssue]:
        """执行完整扫描"""
        self.issues = []
        
        if not os.path.exists(self.skill_path):
            self.issues.append(SecurityIssue(
                level='critical',
                category='path',
                description=f'技能包路径不存在: {self.skill_path}',
                file=''
            ))
            return self.issues
        
        # 扫描文件内容
        for root, dirs, files in os.walk(self.skill_path):
            # 跳过隐藏目录和缓存
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.startswith('.'):
                    continue
                
                file_path = os.path.join(root, file)
                self._scan_file(file_path)
                self.files_checked += 1
        
        # 检查SKILL.md
        self._check_skill_md()
        
        # 检查脚本权限
        self._check_script_permissions()
        
        return self.issues
    
    def _scan_file(self, file_path: str):
        """扫描单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except:
            return
        
        rel_path = os.path.relpath(file_path, self.skill_path)
        
        # 检查危险模式
        for category, patterns in self.DANGEROUS_PATTERNS.items():
            for pattern, description in patterns:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        # 排除注释行
                        if line.strip().startswith('#') or line.strip().startswith('//'):
                            continue
                        
                        level = 'critical' if category in ['code_execution', 'credential_access'] else 'warning'
                        
                        self.issues.append(SecurityIssue(
                            level=level,
                            category=category,
                            description=description,
                            file=rel_path,
                            line=line_num
                        ))
    
    def _check_skill_md(self):
        """检查SKILL.md"""
        skill_md = os.path.join(self.skill_path, 'SKILL.md')
        
        if not os.path.exists(skill_md):
            self.issues.append(SecurityIssue(
                level='warning',
                category='documentation',
                description='缺少SKILL.md文档',
                file='SKILL.md'
            ))
            return
        
        try:
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查必要信息
            if 'description:' not in content:
                self.issues.append(SecurityIssue(
                    level='info',
                    category='documentation',
                    description='SKILL.md缺少description字段',
                    file='SKILL.md'
                ))
            
            # 检查可疑描述
            suspicious = ['password', 'credential', 'token', 'key']
            for word in suspicious:
                if word in content.lower():
                    self.issues.append(SecurityIssue(
                        level='info',
                        category='documentation',
                        description=f'SKILL.md包含敏感词: {word}',
                        file='SKILL.md'
                    ))
                    
        except Exception as e:
            self.issues.append(SecurityIssue(
                level='warning',
                category='documentation',
                description=f'无法读取SKILL.md: {e}',
                file='SKILL.md'
            ))
    
    def _check_script_permissions(self):
        """检查脚本权限"""
        scripts_dir = os.path.join(self.skill_path, 'scripts')
        if not os.path.exists(scripts_dir):
            return
        
        for file in os.listdir(scripts_dir):
            file_path = os.path.join(scripts_dir, file)
            if os.path.isfile(file_path):
                # 检查是否有执行权限
                if os.access(file_path, os.X_OK):
                    self.issues.append(SecurityIssue(
                        level='info',
                        category='permissions',
                        description=f'脚本有执行权限: {file}',
                        file=os.path.join('scripts', file)
                    ))
    
    def generate_report(self) -> str:
        """生成扫描报告"""
        if not self.issues:
            return f"""
{'='*70}
✅ 安全检查通过
{'='*70}

扫描文件: {self.files_checked} 个
发现问题: 0 个

该技能包看起来是安全的，可以安装。
{'='*70}
"""
        
        critical = [i for i in self.issues if i.level == 'critical']
        warnings = [i for i in self.issues if i.level == 'warning']
        infos = [i for i in self.issues if i.level == 'info']
        
        lines = [
            f"{'='*70}",
            f"🔒 技能包安全检查报告",
            f"{'='*70}",
            f"",
            f"扫描路径: {self.skill_path}",
            f"扫描文件: {self.files_checked} 个",
            f"",
            f"问题统计:",
            f"  🔴 严重: {len(critical)} 个",
            f"  🟡 警告: {len(warnings)} 个",
            f"  🔵 信息: {len(infos)} 个",
            f"",
        ]
        
        if critical:
            lines.append("🔴 严重问题（建议不要安装）:")
            for issue in critical[:10]:  # 最多显示10个
                lines.append(f"  [{issue.category}] {issue.description}")
                lines.append(f"    位置: {issue.file}:{issue.line}")
            lines.append("")
        
        if warnings:
            lines.append("🟡 警告（建议审查）:")
            for issue in warnings[:10]:
                lines.append(f"  [{issue.category}] {issue.description}")
                lines.append(f"    位置: {issue.file}")
            lines.append("")
        
        if infos:
            lines.append("🔵 信息（供参考）:")
            for issue in infos[:5]:
                lines.append(f"  [{issue.category}] {issue.description}")
            lines.append("")
        
        # 建议
        if critical:
            lines.append("⚠️ 建议: 发现严重安全问题，不建议安装此技能包！")
        elif warnings:
            lines.append("💡 建议: 有警告项，请审查后决定是否安装。")
        else:
            lines.append("✅ 建议: 只有信息项，可以安装。")
        
        lines.append(f"{'='*70}")
        
        return "\n".join(lines)

def scan_skill(skill_path: str) -> str:
    """快捷扫描函数"""
    scanner = SkillSecurityScanner(skill_path)
    scanner.scan()
    return scanner.generate_report()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 security_scanner.py /path/to/skill")
        print("  python3 security_scanner.py ~/.openclaw/workspace/skills/stock-analysis-pro")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    print(scan_skill(skill_path))
