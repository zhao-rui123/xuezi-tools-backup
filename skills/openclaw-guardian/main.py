#!/usr/bin/env python3
"""
OpenClaw Guardian - 主入口脚本
==============================

提供命令行接口用于:
- 扫描技能包安全性
- 监控系统稳定性
- 修复程序问题
- 检测安全漏洞

用法:
    python main.py scan <skill_path>     # 扫描技能包
    python main.py monitor               # 启动监控
    python main.py fix <file_path>       # 修复文件
    python main.py health                # 检查系统健康
    python main.py install <skill_path>  # 安全安装技能包
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Optional

# 添加项目目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from core.guardian import OpenClawGuardian
from core.security_manager import SecurityManager
from core.stability_monitor import StabilityMonitor
from core.bug_fixer import BugFixer
from core.vulnerability_scanner import VulnerabilityScanner
from utils.config_loader import ConfigLoader
from utils.logger import setup_logger


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog='openclaw-guardian',
        description='OpenClaw Guardian - 安全守护技能包',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s scan ./my_skill                    # 扫描技能包
  %(prog)s scan ./my_skill --json             # 输出JSON格式
  %(prog)s monitor                            # 启动监控
  %(prog)s monitor --duration 3600            # 监控1小时
  %(prog)s fix ./my_skill/main.py             # 修复文件
  %(prog)s fix ./my_skill --dry-run           # 预览修复
  %(prog)s health                             # 检查系统健康
  %(prog)s install ./my_skill ./skills        # 安全安装技能包
  %(prog)s vuln-scan ./my_skill               # 漏洞扫描
        '''
    )
    
    parser.add_argument(
        '-c', '--config',
        help='配置文件路径',
        default=None
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='启用详细输出'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # scan 命令
    scan_parser = subparsers.add_parser('scan', help='扫描技能包安全性')
    scan_parser.add_argument('skill_path', help='技能包路径')
    scan_parser.add_argument('--json', action='store_true', help='输出JSON格式')
    scan_parser.add_argument('--save-report', help='保存报告到文件')
    
    # monitor 命令
    monitor_parser = subparsers.add_parser('monitor', help='启动系统监控')
    monitor_parser.add_argument('--duration', type=int, help='监控持续时间（秒）')
    monitor_parser.add_argument('--interval', type=int, help='检查间隔（秒）')
    
    # fix 命令
    fix_parser = subparsers.add_parser('fix', help='修复代码问题')
    fix_parser.add_argument('path', help='文件或目录路径')
    fix_parser.add_argument('--dry-run', action='store_true', help='预览修复不执行')
    fix_parser.add_argument('--severity', nargs='+', default=['low', 'medium'], help='修复的严重级别')
    
    # health 命令
    health_parser = subparsers.add_parser('health', help='检查系统健康')
    health_parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    # install 命令
    install_parser = subparsers.add_parser('install', help='安全安装技能包')
    install_parser.add_argument('skill_path', help='技能包路径')
    install_parser.add_argument('target_dir', help='安装目标目录')
    install_parser.add_argument('--force', action='store_true', help='强制安装（忽略警告）')
    
    # vuln-scan 命令
    vuln_parser = subparsers.add_parser('vuln-scan', help='漏洞扫描')
    vuln_parser.add_argument('skill_path', help='技能包路径')
    vuln_parser.add_argument('--json', action='store_true', help='输出JSON格式')
    vuln_parser.add_argument('--save-report', help='保存报告到文件')
    
    # stats 命令
    stats_parser = subparsers.add_parser('stats', help='显示统计信息')
    
    return parser


def cmd_scan(args, guardian: OpenClawGuardian) -> int:
    """执行扫描命令"""
    print(f"正在扫描技能包: {args.skill_path}")
    print("-" * 60)
    
    result = guardian.scan_skill(args.skill_path)
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 文本格式输出
        print(f"扫描时间: {result['timestamp']}")
        print(f"风险评分: {result['risk_score']}/100")
        print(f"安全状态: {'✓ 安全' if result['is_safe'] else '✗ 存在风险'}")
        print()
        
        if result['threats']:
            print(f"发现 {len(result['threats'])} 个安全威胁:")
            for threat in result['threats']:
                severity_icon = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢',
                }.get(threat['severity'], '⚪')
                print(f"  {severity_icon} [{threat['severity'].upper()}] {threat['description']}")
                print(f"     文件: {threat['file_path']}:{threat['line_number']}")
                if threat['code_snippet']:
                    print(f"     代码: {threat['code_snippet'][:80]}")
                print(f"     建议: {threat['recommendation']}")
                print()
        
        if result['vulnerabilities']:
            print(f"发现 {len(result['vulnerabilities'])} 个漏洞:")
            for vuln in result['vulnerabilities']:
                print(f"  [{vuln['severity'].upper()}] {vuln['name']} ({vuln['cwe_id']})")
                print(f"     文件: {vuln['file_path']}:{vuln['line_number']}")
                print()
        
        if result['warnings']:
            print(f"发现 {len(result['warnings'])} 个警告:")
            for warning in result['warnings']:
                print(f"  ⚠ {warning}")
    
    # 保存报告
    if args.save_report:
        with open(args.save_report, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n报告已保存到: {args.save_report}")
    
    return 0 if result['is_safe'] and result['risk_score'] < 50 else 1


def cmd_monitor(args, guardian: OpenClawGuardian) -> int:
    """执行监控命令"""
    import time
    
    print("启动系统监控...")
    print("按 Ctrl+C 停止监控")
    print("-" * 60)
    
    guardian.start()
    
    try:
        if args.duration:
            time.sleep(args.duration)
        else:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n停止监控...")
    finally:
        guardian.stop()
        
        # 显示统计
        stats = guardian.get_stats()
        print("\n监控统计:")
        print(f"  运行时间: {stats.get('uptime', 0):.1f} 秒")
        print(f"  扫描技能数: {stats['skills_scanned']}")
        print(f"  阻止威胁数: {stats['threats_blocked']}")
        print(f"  修复Bug数: {stats['bugs_fixed']}")
        print(f"  发现漏洞数: {stats['vulnerabilities_found']}")
    
    return 0


def cmd_fix(args, guardian: OpenClawGuardian) -> int:
    """执行修复命令"""
    path = Path(args.path)
    
    if not path.exists():
        print(f"错误: 路径不存在 - {path}")
        return 1
    
    print(f"分析路径: {path}")
    print("-" * 60)
    
    if path.is_file():
        result = guardian.bug_fixer.fix_file(str(path), dry_run=args.dry_run)
    else:
        analysis = guardian.bug_fixer.analyze_skill(str(path))
        
        auto_fixable = [i for i in analysis['issues'] if i.get('auto_fixable')]
        
        print(f"文件数: {analysis['files_analyzed']}")
        print(f"总问题数: {len(analysis['issues'])}")
        print(f"可自动修复: {len(auto_fixable)}")
        print(f"代码质量评分: {analysis['quality_score']}/100")
        print()
        
        if args.dry_run:
            print("预览修复内容:")
            for issue in auto_fixable[:10]:  # 只显示前10个
                print(f"  [{issue['severity'].upper()}] {issue['description']}")
                print(f"     位置: {issue['file_path']}:{issue['line_number']}")
                print(f"     建议: {issue['fix_suggestion']}")
                print()
            return 0
        
        # 执行修复
        result = guardian.bug_fixer.fix_issues(auto_fixable)
    
    print(f"修复完成:")
    print(f"  成功: {result.get('fixed_count', 0)}")
    print(f"  失败: {result.get('failed_count', 0)}")
    
    if result.get('fixes'):
        print("\n修复详情:")
        for fix in result['fixes'][:10]:
            status = "✓" if fix['success'] else "✗"
            print(f"  {status} {fix['issue_type']}: {fix['message']}")
    
    return 0


def cmd_health(args, guardian: OpenClawGuardian) -> int:
    """执行健康检查命令"""
    print("检查系统健康状态...")
    print("-" * 60)
    
    health = guardian.check_system_health()
    
    if args.json:
        print(json.dumps(health, ensure_ascii=False, indent=2))
    else:
        status_icon = {
            'healthy': '✓',
            'warning': '⚠',
            'critical': '✗',
        }.get(health['overall_status'], '?')
        
        print(f"整体状态: {status_icon} {health['overall_status'].upper()}")
        print()
        
        usage = health['components']['resources']['usage']
        print("资源使用:")
        print(f"  CPU: {usage['cpu_percent']:.1f}%")
        print(f"  内存: {usage['memory_percent']:.1f}% (可用: {usage['memory_available_mb']:.0f} MB)")
        print(f"  磁盘: {usage['disk_percent']:.1f}% (可用: {usage['disk_free_gb']:.1f} GB)")
        print()
        
        issues = health['components']['resources'].get('issues', [])
        if issues:
            print("检测到的问题:")
            for issue in issues:
                print(f"  ⚠ {issue}")
            print()
        
        recommendations = health.get('recommendations', [])
        if recommendations:
            print("建议:")
            for rec in recommendations:
                print(f"  • {rec}")
    
    return 0 if health['overall_status'] == 'healthy' else 1


def cmd_install(args, guardian: OpenClawGuardian) -> int:
    """执行安装命令"""
    print(f"准备安装技能包: {args.skill_path}")
    print(f"目标目录: {args.target_dir}")
    print("-" * 60)
    
    result = guardian.install_skill_safely(args.skill_path, args.target_dir)
    
    print(f"扫描结果:")
    scan = result['scan_result']
    print(f"  风险评分: {scan['risk_score']}/100")
    print(f"  安全状态: {'✓ 安全' if scan['is_safe'] else '✗ 存在风险'}")
    
    if scan['threats']:
        print(f"  威胁数: {len(scan['threats'])}")
    if scan['vulnerabilities']:
        print(f"  漏洞数: {len(scan['vulnerabilities'])}")
    
    print()
    
    if result['success']:
        print(f"✓ 安装成功: {result['installed_path']}")
        if 'backup_path' in result:
            print(f"  原文件已备份到: {result['backup_path']}")
    else:
        print(f"✗ 安装失败: {result['message']}")
        
        if args.force and scan['risk_score'] < 80:
            print("\n使用 --force 强制安装...")
            import shutil
            try:
                skill_name = os.path.basename(args.skill_path)
                install_path = os.path.join(args.target_dir, skill_name)
                shutil.copytree(args.skill_path, install_path)
                print(f"✓ 强制安装完成: {install_path}")
                print("⚠ 警告: 此技能包存在安全风险！")
            except Exception as e:
                print(f"✗ 强制安装失败: {e}")
                return 1
    
    return 0 if result['success'] else 1


def cmd_vuln_scan(args, guardian: OpenClawGuardian) -> int:
    """执行漏洞扫描命令"""
    print(f"正在扫描漏洞: {args.skill_path}")
    print("-" * 60)
    
    result = guardian.vuln_scanner.scan_skill(args.skill_path)
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"扫描文件数: {result['files_scanned']}")
        print(f"风险评分: {result['risk_score']}/100")
        print()
        
        vulns = result.get('vulnerabilities', [])
        if vulns:
            print(f"发现 {len(vulns)} 个漏洞:")
            print()
            
            # 按严重级别分组
            by_severity = {'critical': [], 'high': [], 'medium': [], 'low': []}
            for vuln in vulns:
                by_severity.get(vuln['severity'], []).append(vuln)
            
            for severity in ['critical', 'high', 'medium', 'low']:
                items = by_severity[severity]
                if items:
                    icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[severity]
                    print(f"{icon} {severity.upper()} ({len(items)}个):")
                    for vuln in items:
                        print(f"  [{vuln['cwe_id']}] {vuln['name']}")
                        print(f"    位置: {vuln['file_path']}:{vuln['line_number']}")
                        print(f"    描述: {vuln['description']}")
                        print(f"    修复: {vuln['remediation']}")
                        print()
        else:
            print("✓ 未发现漏洞")
    
    # 保存报告
    if args.save_report:
        guardian.vuln_scanner.generate_report(result, args.save_report)
        print(f"报告已保存到: {args.save_report}")
    
    return 0 if result['risk_score'] < 50 else 1


def cmd_stats(args, guardian: OpenClawGuardian) -> int:
    """显示统计信息"""
    stats = guardian.get_stats()
    
    print("OpenClaw Guardian 统计信息")
    print("-" * 60)
    
    if stats.get('start_time'):
        print(f"启动时间: {stats['start_time']}")
        print(f"运行时间: {stats.get('uptime', 0):.1f} 秒")
    else:
        print("状态: 未运行")
    
    print()
    print("操作统计:")
    print(f"  扫描技能数: {stats['skills_scanned']}")
    print(f"  阻止威胁数: {stats['threats_blocked']}")
    print(f"  修复Bug数: {stats['bugs_fixed']}")
    print(f"  发现漏洞数: {stats['vulnerabilities_found']}")
    
    return 0


def main(argv: Optional[list] = None) -> int:
    """主入口函数"""
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 设置日志级别
    log_level = 'DEBUG' if args.verbose else 'INFO'
    
    # 加载配置
    config = ConfigLoader.load(args.config)
    config['log_level'] = log_level
    
    # 创建Guardian实例
    guardian = OpenClawGuardian(config_path=args.config)
    
    # 执行命令
    commands = {
        'scan': cmd_scan,
        'monitor': cmd_monitor,
        'fix': cmd_fix,
        'health': cmd_health,
        'install': cmd_install,
        'vuln-scan': cmd_vuln_scan,
        'stats': cmd_stats,
    }
    
    if args.command in commands:
        return commands[args.command](args, guardian)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
