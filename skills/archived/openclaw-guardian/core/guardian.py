"""
OpenClaw Guardian - 主控制类
=============================

协调所有安全模块，提供统一的安全管理接口。
"""

import os
import sys
import json
import time
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime

from core.security_manager import SecurityManager
from core.stability_monitor import StabilityMonitor
from core.bug_fixer import BugFixer
from core.vulnerability_scanner import VulnerabilityScanner
from utils.logger import setup_logger
from utils.config_loader import ConfigLoader


class OpenClawGuardian:
    """
    OpenClaw Guardian 主类
    
    提供全面的安全保护功能:
    1. 技能安全扫描
    2. 系统稳定性监控
    3. 自动Bug修复
    4. 漏洞检测
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化Guardian
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认配置
        """
        self.config = ConfigLoader.load(config_path)
        self.logger = setup_logger(
            name="OpenClawGuardian",
            level=self.config.get('log_level', 'INFO'),
            log_file=self.config.get('log_file', 'logs/guardian.log')
        )
        
        # 初始化各个模块
        self.logger.info("正在初始化OpenClaw Guardian...")
        
        self.security_manager = SecurityManager(self.config.get('security', {}))
        self.stability_monitor = StabilityMonitor(self.config.get('stability', {}))
        self.bug_fixer = BugFixer(self.config.get('bug_fix', {}))
        self.vuln_scanner = VulnerabilityScanner(self.config.get('vulnerability', {}))
        
        # 运行状态
        self._running = False
        self._monitor_thread = None
        self._callbacks: Dict[str, List[Callable]] = {
            'threat_detected': [],
            'system_unstable': [],
            'bug_fixed': [],
            'vulnerability_found': [],
        }
        
        # 统计信息
        self.stats = {
            'skills_scanned': 0,
            'threats_blocked': 0,
            'bugs_fixed': 0,
            'vulnerabilities_found': 0,
            'start_time': None,
        }
        
        self.logger.info("OpenClaw Guardian初始化完成")
    
    def start(self) -> None:
        """启动Guardian监控"""
        if self._running:
            self.logger.warning("Guardian已经在运行中")
            return
        
        self._running = True
        self.stats['start_time'] = datetime.now()
        
        # 启动稳定性监控
        self.stability_monitor.start()
        
        # 启动后台监控线程
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        
        self.logger.info("OpenClaw Guardian已启动")
        self._trigger_callback('guardian_started', {})
    
    def stop(self) -> None:
        """停止Guardian监控"""
        if not self._running:
            return
        
        self._running = False
        self.stability_monitor.stop()
        
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        
        self.logger.info("OpenClaw Guardian已停止")
        self._trigger_callback('guardian_stopped', {})
    
    def scan_skill(self, skill_path: str) -> Dict[str, Any]:
        """
        扫描技能包安全性
        
        Args:
            skill_path: 技能包路径
            
        Returns:
            扫描结果字典
        """
        self.logger.info(f"开始扫描技能包: {skill_path}")
        self.stats['skills_scanned'] += 1
        
        result = {
            'skill_path': skill_path,
            'timestamp': datetime.now().isoformat(),
            'is_safe': True,
            'threats': [],
            'vulnerabilities': [],
            'warnings': [],
            'risk_score': 0,  # 0-100, 越高越危险
        }
        
        # 1. 安全检查
        security_result = self.security_manager.scan_skill(skill_path)
        if security_result['has_threats']:
            result['is_safe'] = False
            result['threats'].extend(security_result['threats'])
            result['risk_score'] += security_result['risk_score']
            self.stats['threats_blocked'] += 1
            self._trigger_callback('threat_detected', {
                'skill_path': skill_path,
                'threats': security_result['threats']
            })
        
        # 2. 漏洞扫描
        vuln_result = self.vuln_scanner.scan_skill(skill_path)
        if vuln_result['vulnerabilities']:
            result['vulnerabilities'].extend(vuln_result['vulnerabilities'])
            result['risk_score'] += vuln_result['risk_score']
            self.stats['vulnerabilities_found'] += len(vuln_result['vulnerabilities'])
            self._trigger_callback('vulnerability_found', {
                'skill_path': skill_path,
                'vulnerabilities': vuln_result['vulnerabilities']
            })
        
        # 3. 代码质量检查
        quality_result = self.bug_fixer.analyze_skill(skill_path)
        result['warnings'].extend(quality_result.get('warnings', []))
        
        # 风险评分上限100
        result['risk_score'] = min(100, result['risk_score'])
        
        # 保存扫描报告
        self._save_scan_report(result)
        
        self.logger.info(f"技能包扫描完成: {skill_path}, 安全: {result['is_safe']}, 风险评分: {result['risk_score']}")
        return result
    
    def install_skill_safely(self, skill_path: str, target_dir: str) -> Dict[str, Any]:
        """
        安全地安装技能包
        
        Args:
            skill_path: 技能包路径
            target_dir: 安装目标目录
            
        Returns:
            安装结果
        """
        # 先进行扫描
        scan_result = self.scan_skill(skill_path)
        
        result = {
            'success': False,
            'scan_result': scan_result,
            'installed_path': None,
            'message': '',
        }
        
        # 如果存在高危风险，阻止安装
        if scan_result['risk_score'] >= 80:
            result['message'] = f"安装被阻止: 检测到高危风险 (评分: {scan_result['risk_score']})"
            self.logger.warning(f"阻止安装高风险技能包: {skill_path}")
            return result
        
        # 如果存在中等风险，警告但仍允许安装（如果配置允许）
        if scan_result['risk_score'] >= 50:
            if not self.config.get('security.allow_medium_risk', False):
                result['message'] = f"安装被阻止: 检测到中等风险 (评分: {scan_result['risk_score']})"
                return result
            result['message'] = f"警告: 技能包存在中等风险 (评分: {scan_result['risk_score']})"
        
        # 执行安装
        try:
            import shutil
            skill_name = os.path.basename(skill_path)
            install_path = os.path.join(target_dir, skill_name)
            
            # 如果已存在，先备份
            if os.path.exists(install_path):
                backup_path = f"{install_path}.backup.{int(time.time())}"
                shutil.move(install_path, backup_path)
                result['backup_path'] = backup_path
            
            shutil.copytree(skill_path, install_path)
            result['success'] = True
            result['installed_path'] = install_path
            result['message'] += f" 技能包已成功安装到: {install_path}"
            
            self.logger.info(f"技能包安装成功: {install_path}")
            
        except Exception as e:
            result['message'] = f"安装失败: {str(e)}"
            self.logger.error(f"技能包安装失败: {e}")
        
        return result
    
    def check_system_health(self) -> Dict[str, Any]:
        """
        检查系统健康状态
        
        Returns:
            健康状态报告
        """
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',  # healthy, warning, critical
            'components': {},
            'recommendations': [],
        }
        
        # 检查系统资源
        resource_status = self.stability_monitor.check_resources()
        health_report['components']['resources'] = resource_status
        
        if resource_status['status'] == 'critical':
            health_report['overall_status'] = 'critical'
            health_report['recommendations'].append("系统资源严重不足，建议立即释放资源")
        elif resource_status['status'] == 'warning':
            health_report['overall_status'] = 'warning'
            health_report['recommendations'].append("系统资源紧张，建议监控资源使用")
        
        # 检查OpenClaw核心状态
        core_status = self._check_openclaw_core()
        health_report['components']['openclaw_core'] = core_status
        
        if core_status['has_issues']:
            health_report['overall_status'] = 'warning'
            health_report['recommendations'].extend(core_status['recommendations'])
        
        # 自动修复尝试
        if self.config.get('bug_fix.auto_fix', True) and core_status['has_issues']:
            fix_result = self.bug_fixer.fix_issues(core_status['issues'])
            health_report['auto_fix_results'] = fix_result
            if fix_result['fixed_count'] > 0:
                self.stats['bugs_fixed'] += fix_result['fixed_count']
                self._trigger_callback('bug_fixed', fix_result)
        
        return health_report
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """
        注册事件回调
        
        Args:
            event: 事件名称
            callback: 回调函数
        """
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取Guardian运行统计"""
        stats = self.stats.copy()
        if stats['start_time']:
            stats['uptime'] = (datetime.now() - stats['start_time']).total_seconds()
        return stats
    
    def _monitor_loop(self) -> None:
        """后台监控循环"""
        check_interval = self.config.get('monitoring.interval', 60)
        
        while self._running:
            try:
                # 执行系统健康检查
                health = self.check_system_health()
                
                if health['overall_status'] == 'critical':
                    self.logger.error("检测到系统严重问题！")
                    self._trigger_callback('system_unstable', health)
                    
                    # 执行紧急保护措施
                    self._emergency_protection()
                
                time.sleep(check_interval)
                
            except Exception as e:
                self.logger.error(f"监控循环出错: {e}")
                time.sleep(5)
    
    def _check_openclaw_core(self) -> Dict[str, Any]:
        """检查OpenClaw核心状态"""
        result = {
            'has_issues': False,
            'issues': [],
            'recommendations': [],
        }
        
        # 检查关键进程
        # 这里可以根据实际的OpenClaw架构进行扩展
        
        return result
    
    def _emergency_protection(self) -> None:
        """执行紧急保护措施"""
        self.logger.warning("执行紧急保护措施...")
        
        # 1. 释放内存
        self.stability_monitor.free_memory()
        
        # 2. 暂停非关键任务
        # 3. 创建系统快照用于恢复
        
        self.logger.info("紧急保护措施执行完成")
    
    def _trigger_callback(self, event: str, data: Dict) -> None:
        """触发事件回调"""
        for callback in self._callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                self.logger.error(f"回调执行出错: {e}")
    
    def _save_scan_report(self, result: Dict[str, Any]) -> None:
        """保存扫描报告"""
        reports_dir = Path(self.config.get('reports_dir', 'reports'))
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        skill_name = os.path.basename(result['skill_path'])
        report_file = reports_dir / f"scan_{skill_name}_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
