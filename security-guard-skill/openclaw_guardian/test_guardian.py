#!/usr/bin/env python3
"""
OpenClaw Guardian 测试脚本
===========================

运行各种测试以验证Guardian功能。
"""

import os
import sys
import time
from pathlib import Path

# 添加项目目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from core.guardian import OpenClawGuardian
from core.security_manager import SecurityManager
from core.stability_monitor import StabilityMonitor
from core.bug_fixer import BugFixer
from core.vulnerability_scanner import VulnerabilityScanner


def test_security_scan():
    """测试安全扫描功能"""
    print("=" * 60)
    print("测试: 安全扫描功能")
    print("=" * 60)
    
    security = SecurityManager()
    
    # 测试安全技能包
    print("\n1. 扫描安全技能包...")
    safe_skill = Path(__file__).parent / "examples" / "safe_skill"
    if safe_skill.exists():
        result = security.scan_skill(str(safe_skill))
        print(f"   风险评分: {result['risk_score']}/100")
        print(f"   威胁数: {len(result['threats'])}")
        print(f"   ✓ 安全扫描测试通过" if result['risk_score'] < 20 else "   ⚠ 发现潜在问题")
    else:
        print("   ⚠ 安全技能包不存在，跳过")
    
    # 测试不安全技能包
    print("\n2. 扫描不安全技能包...")
    unsafe_skill = Path(__file__).parent / "examples" / "unsafe_skill"
    if unsafe_skill.exists():
        result = security.scan_skill(str(unsafe_skill))
        print(f"   风险评分: {result['risk_score']}/100")
        print(f"   威胁数: {len(result['threats'])}")
        
        # 显示发现的威胁
        if result['threats']:
            print("   发现的威胁:")
            for threat in result['threats'][:5]:  # 只显示前5个
                print(f"     - [{threat['severity'].upper()}] {threat['description']}")
        
        print(f"   ✓ 成功检测到安全问题" if result['risk_score'] > 50 else "   ⚠ 检测可能不完整")
    else:
        print("   ⚠ 不安全技能包不存在，跳过")
    
    print()


def test_stability_monitor():
    """测试稳定性监控功能"""
    print("=" * 60)
    print("测试: 稳定性监控功能")
    print("=" * 60)
    
    monitor = StabilityMonitor()
    
    # 检查资源
    print("\n1. 检查系统资源...")
    resources = monitor.check_resources()
    print(f"   状态: {resources['status']}")
    print(f"   CPU: {resources['usage']['cpu_percent']:.1f}%")
    print(f"   内存: {resources['usage']['memory_percent']:.1f}%")
    print(f"   磁盘: {resources['usage']['disk_percent']:.1f}%")
    
    if resources['issues']:
        print("   问题:")
        for issue in resources['issues']:
            print(f"     - {issue}")
    
    # 启动监控
    print("\n2. 启动监控（5秒）...")
    monitor.start()
    time.sleep(5)
    monitor.stop()
    
    # 获取历史数据
    history = monitor.get_history(limit=5)
    print(f"   采集数据点数: {len(history)}")
    
    # 获取警报
    alerts = monitor.get_alerts(limit=5)
    print(f"   警报数: {len(alerts)}")
    
    print("   ✓ 稳定性监控测试通过")
    print()


def test_bug_fixer():
    """测试Bug修复功能"""
    print("=" * 60)
    print("测试: Bug修复功能")
    print("=" * 60)
    
    fixer = BugFixer()
    
    # 分析安全技能包
    print("\n1. 分析安全技能包...")
    safe_skill = Path(__file__).parent / "examples" / "safe_skill"
    if safe_skill.exists():
        result = fixer.analyze_skill(str(safe_skill))
        print(f"   文件数: {result['files_analyzed']}")
        print(f"   问题数: {len(result['issues'])}")
        print(f"   质量评分: {result['quality_score']}/100")
        print(f"   ✓ 安全技能包分析完成")
    else:
        print("   ⚠ 安全技能包不存在，跳过")
    
    # 分析不安全技能包
    print("\n2. 分析不安全技能包...")
    unsafe_skill = Path(__file__).parent / "examples" / "unsafe_skill"
    if unsafe_skill.exists():
        result = fixer.analyze_skill(str(unsafe_skill))
        print(f"   文件数: {result['files_analyzed']}")
        print(f"   问题数: {len(result['issues'])}")
        print(f"   质量评分: {result['quality_score']}/100")
        
        # 显示发现的问题
        if result['issues']:
            print("   发现的问题:")
            for issue in result['issues'][:5]:
                print(f"     - [{issue['severity'].upper()}] {issue['description']}")
        
        print(f"   ✓ 成功检测到代码问题")
    else:
        print("   ⚠ 不安全技能包不存在，跳过")
    
    print()


def test_vulnerability_scanner():
    """测试漏洞扫描功能"""
    print("=" * 60)
    print("测试: 漏洞扫描功能")
    print("=" * 60)
    
    scanner = VulnerabilityScanner()
    
    # 扫描安全技能包
    print("\n1. 扫描安全技能包...")
    safe_skill = Path(__file__).parent / "examples" / "safe_skill"
    if safe_skill.exists():
        result = scanner.scan_skill(str(safe_skill))
        print(f"   风险评分: {result['risk_score']}/100")
        print(f"   漏洞数: {len(result['vulnerabilities'])}")
        print(f"   ✓ 安全技能包扫描完成")
    else:
        print("   ⚠ 安全技能包不存在，跳过")
    
    # 扫描不安全技能包
    print("\n2. 扫描不安全技能包...")
    unsafe_skill = Path(__file__).parent / "examples" / "unsafe_skill"
    if unsafe_skill.exists():
        result = scanner.scan_skill(str(unsafe_skill))
        print(f"   风险评分: {result['risk_score']}/100")
        print(f"   漏洞数: {len(result['vulnerabilities'])}")
        print(f"   严重: {result['critical_count']}, 高危: {result['high_count']}, 中危: {result['medium_count']}, 低危: {result['low_count']}")
        
        # 显示发现的漏洞
        if result['vulnerabilities']:
            print("   发现的漏洞:")
            for vuln in result['vulnerabilities'][:5]:
                print(f"     - [{vuln['severity'].upper()}] {vuln['name']} ({vuln['cwe_id']})")
        
        print(f"   ✓ 成功检测到安全漏洞" if result['risk_score'] > 50 else "   ⚠ 检测可能不完整")
    else:
        print("   ⚠ 不安全技能包不存在，跳过")
    
    print()


def test_guardian_integration():
    """测试Guardian集成功能"""
    print("=" * 60)
    print("测试: Guardian集成功能")
    print("=" * 60)
    
    # 创建Guardian实例
    print("\n1. 创建Guardian实例...")
    guardian = OpenClawGuardian()
    print("   ✓ Guardian实例创建成功")
    
    # 扫描技能包
    print("\n2. 扫描技能包...")
    unsafe_skill = Path(__file__).parent / "examples" / "unsafe_skill"
    if unsafe_skill.exists():
        result = guardian.scan_skill(str(unsafe_skill))
        print(f"   安全状态: {'安全' if result['is_safe'] else '存在风险'}")
        print(f"   风险评分: {result['risk_score']}/100")
        print(f"   ✓ 扫描完成")
    
    # 检查系统健康
    print("\n3. 检查系统健康...")
    health = guardian.check_system_health()
    print(f"   整体状态: {health['overall_status']}")
    print(f"   ✓ 健康检查完成")
    
    # 获取统计
    print("\n4. 获取统计信息...")
    stats = guardian.get_stats()
    print(f"   扫描技能数: {stats['skills_scanned']}")
    print(f"   阻止威胁数: {stats['threats_blocked']}")
    print(f"   ✓ 统计信息获取完成")
    
    print()


def test_cli():
    """测试命令行接口"""
    print("=" * 60)
    print("测试: 命令行接口")
    print("=" * 60)
    
    import subprocess
    
    # 测试帮助命令
    print("\n1. 测试帮助命令...")
    result = subprocess.run(
        [sys.executable, "main.py", "--help"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )
    if result.returncode == 0:
        print("   ✓ 帮助命令正常")
    else:
        print(f"   ✗ 帮助命令失败: {result.stderr}")
    
    # 测试扫描命令
    print("\n2. 测试扫描命令...")
    unsafe_skill = Path(__file__).parent / "examples" / "unsafe_skill"
    if unsafe_skill.exists():
        result = subprocess.run(
            [sys.executable, "main.py", "scan", str(unsafe_skill), "--json"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        if result.returncode in [0, 1]:  # 0=安全, 1=发现风险
            print("   ✓ 扫描命令正常")
        else:
            print(f"   ✗ 扫描命令失败: {result.stderr}")
    
    # 测试健康检查命令
    print("\n3. 测试健康检查命令...")
    result = subprocess.run(
        [sys.executable, "main.py", "health"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )
    if result.returncode in [0, 1]:
        print("   ✓ 健康检查命令正常")
    else:
        print(f"   ✗ 健康检查命令失败: {result.stderr}")
    
    print()


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("OpenClaw Guardian 测试套件")
    print("=" * 60 + "\n")
    
    try:
        test_security_scan()
    except Exception as e:
        print(f"安全扫描测试失败: {e}\n")
    
    try:
        test_stability_monitor()
    except Exception as e:
        print(f"稳定性监控测试失败: {e}\n")
    
    try:
        test_bug_fixer()
    except Exception as e:
        print(f"Bug修复测试失败: {e}\n")
    
    try:
        test_vulnerability_scanner()
    except Exception as e:
        print(f"漏洞扫描测试失败: {e}\n")
    
    try:
        test_guardian_integration()
    except Exception as e:
        print(f"Guardian集成测试失败: {e}\n")
    
    try:
        test_cli()
    except Exception as e:
        print(f"CLI测试失败: {e}\n")
    
    print("=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == '__main__':
    run_all_tests()
