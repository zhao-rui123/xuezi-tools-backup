"""
OpenClaw Guardian - 安全守护技能包
=====================================

一个全面的安全技能包，用于保护OpenClaw系统的安全与稳定。

主要功能:
- 技能安全扫描: 检测下载的skill是否包含恶意代码
- 程序稳定性监控: 监控系统运行状态，防止崩溃
- 自动Bug修复: 检测并修复常见程序问题
- 漏洞检测: 扫描skill中的安全漏洞

作者: OpenClaw Guardian Team
版本: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "OpenClaw Guardian Team"

from .core.guardian import OpenClawGuardian
from .core.security_manager import SecurityManager
from .core.stability_monitor import StabilityMonitor
from .core.bug_fixer import BugFixer
from .core.vulnerability_scanner import VulnerabilityScanner

__all__ = [
    'OpenClawGuardian',
    'SecurityManager', 
    'StabilityMonitor',
    'BugFixer',
    'VulnerabilityScanner',
]
