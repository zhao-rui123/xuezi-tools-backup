#!/usr/bin/env python3
"""
Memory Suite v4.0 - 系统健康检查脚本
整合所有健康检查项，生成统一报告并发送到飞书
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

WORKSPACE = Path.home() / ".openclaw" / "workspace"
LOG_FILE = Path("/tmp/memory-suite.log")
REPORT_FILE = Path("/tmp/health_report.md")


class HealthChecker:
    """系统健康检查器"""
    
    def __init__(self):
        self.results = {}
        self.issues = []
        self.warnings = []
        
    def check_cron_tasks(self) -> Dict:
        """检查定时任务状态"""
        result = {
            "status": "ok",
            "tasks": [],
            "failed": 0
        }
        
        try:
            crontab_result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if crontab_result.returncode != 0:
                result["status"] = "error"
                result["error"] = "无法读取 crontab"
                return result
                
            tasks = []
            for line in crontab_result.stdout.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                parts = line.split()
                if len(parts) >= 6:
                    schedule = ' '.join(parts[:5])
                    command = ' '.join(parts[5:])
                    
                    # 提取任务名
                    task_name = "unknown"
                    for pattern in ['.py', '.sh']:
                        if pattern in command:
                            task_name = command.split('/')[-1].split(pattern)[0]
                            break
                    
                    tasks.append({
                        "name": task_name,
                        "schedule": schedule,
                        "command": command[:80] + "..." if len(command) > 80 else command
                    })
                    
            result["tasks"] = tasks
            result["total"] = len(tasks)
            
        except subprocess.TimeoutExpired:
            result["status"] = "timeout"
            result["error"] = "检查超时"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            
        return result
        
    def check_disk_space(self) -> Dict:
        """检查磁盘空间"""
        result = {
            "status": "ok",
            "partitions": []
        }
        
        paths_to_check = [
            ("/", "根分区"),
            (str(WORKSPACE), "工作区"),
            ("/Volumes/cu/ocu", "备份磁盘")
        ]
        
        for path, name in paths_to_check:
            try:
                df_result = subprocess.run(
                    ["df", "-h", path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if df_result.returncode == 0:
                    lines = df_result.stdout.strip().split('\n')
                    if len(lines) >= 2:
                        parts = lines[1].split()
                        if len(parts) >= 5:
                            usage_percent = int(parts[4].replace('%', ''))
                            
                            partition_info = {
                                "name": name,
                                "path": path,
                                "total": parts[1],
                                "used": parts[2],
                                "available": parts[3],
                                "usage_percent": usage_percent
                            }
                            
                            result["partitions"].append(partition_info)
                            
                            # 检查使用率
                            if usage_percent > 90:
                                self.issues.append(f"{name} 使用率超过 90% ({usage_percent}%)")
                                result["status"] = "warning"
                            elif usage_percent > 80:
                                self.warnings.append(f"{name} 使用率超过 80% ({usage_percent}%)")
                                
            except Exception as e:
                result["partitions"].append({
                    "name": name,
                    "path": path,
                    "error": str(e)
                })
                
        return result
        
    def check_log_status(self) -> Dict:
        """检查日志文件状态"""
        result = {
            "status": "ok",
            "log_file": str(LOG_FILE),
            "exists": False
        }
        
        if LOG_FILE.exists():
            result["exists"] = True
            stat = LOG_FILE.stat()
            
            result["size_mb"] = round(stat.st_size / (1024 * 1024), 2)
            result["last_modified"] = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            # 检查最后更新时间
            hours_ago = (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).total_seconds() / 3600
            
            if hours_ago > 48:
                self.warnings.append(f"日志文件超过 48 小时未更新 ({hours_ago:.1f}h)")
            elif hours_ago > 24:
                self.warnings.append(f"日志文件超过 24 小时未更新 ({hours_ago:.1f}h)")
                
            # 检查最后几行是否有错误
            try:
                with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    last_50 = lines[-50:] if len(lines) > 50 else lines
                    
                    error_count = sum(1 for line in last_50 if '[ERROR]' in line or '❌' in line)
                    warn_count = sum(1 for line in last_50 if '[WARN]' in line or '⚠️' in line)
                    
                    result["recent_errors"] = error_count
                    result["recent_warnings"] = warn_count
                    
                    if error_count > 5:
                        self.warnings.append(f"日志中最近有 {error_count} 条错误")
                        
            except Exception as e:
                result["read_error"] = str(e)
        else:
            self.warnings.append("统一日志文件不存在")
            
        return result
        
    def check_backup_status(self) -> Dict:
        """检查备份状态"""
        result = {
            "status": "ok",
            "backup_dir": Path("/Volumes/cu/ocu/openclaw-backups"),
            "exists": False
        }
        
        backup_dir = result["backup_dir"]
        
        if backup_dir.exists():
            result["exists"] = True
            
            # 查找最新备份
            try:
                backups = list(backup_dir.glob("*.tar.gz"))
                if backups:
                    latest = max(backups, key=lambda p: p.stat().st_mtime)
                    result["latest_backup"] = latest.name
                    result["latest_backup_time"] = datetime.fromtimestamp(
                        latest.stat().st_mtime
                    ).strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 检查备份是否超过 7 天
                    days_ago = (datetime.now() - datetime.fromtimestamp(
                        latest.stat().st_mtime
                    )).days
                    
                    if days_ago > 7:
                        self.warnings.append(f"备份超过 7 天未更新 ({days_ago}天前)")
                    result["days_since_backup"] = days_ago
                    
                result["total_backups"] = len(backups)
                
            except Exception as e:
                result["error"] = str(e)
        else:
            self.warnings.append("备份目录不存在")
            
        return result
        
    def check_memory_usage(self) -> Dict:
        """检查内存使用情况"""
        result = {
            "status": "ok"
        }
        
        try:
            vm_stat = subprocess.run(
                ["vm_stat"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if vm_stat.returncode == 0:
                # 解析 vm_stat 输出
                pages = {}
                for line in vm_stat.stdout.split('\n'):
                    if ':' in line:
                        key, value = line.split(':')
                        key = key.strip()
                        value = value.strip().rstrip('.')
                        try:
                            pages[key] = int(value)
                        except:
                            pass
                            
                # 计算内存使用 (macOS 页大小通常是 4KB)
                page_size = 4096
                total_pages = pages.get("Pages active", 0) + pages.get("Pages inactive", 0) + \
                             pages.get("Pages speculative", 0) + pages.get("Pages wired down", 0)
                
                if total_pages > 0:
                    used_percent = ((pages.get("Pages active", 0) + pages.get("Pages wired down", 0)) / total_pages) * 100
                    result["used_percent"] = round(used_percent, 1)
                    
                    if used_percent > 90:
                        self.warnings.append(f"内存使用率超过 90% ({used_percent:.1f}%)")
                        
        except Exception as e:
            result["error"] = str(e)
            
        return result
        
    def check_python_processes(self) -> Dict:
        """检查 Python 进程 (检测可能的卡死进程)"""
        result = {
            "status": "ok",
            "processes": []
        }
        
        try:
            ps_result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if ps_result.returncode == 0:
                python_processes = []
                for line in ps_result.stdout.split('\n'):
                    if 'python' in line.lower() and 'grep' not in line.lower():
                        parts = line.split()
                        if len(parts) >= 11:
                            pid = parts[1]
                            cpu = parts[2]
                            mem = parts[3]
                            command = ' '.join(parts[10:])
                            
                            python_processes.append({
                                "pid": pid,
                                "cpu": cpu,
                                "mem": mem,
                                "command": command[:60]
                            })
                            
                            # 检查高 CPU 使用
                            try:
                                if float(cpu) > 80:
                                    self.warnings.append(f"Python 进程 (PID {pid}) CPU 使用率高: {cpu}%")
                            except:
                                pass
                                
                result["processes"] = python_processes
                result["count"] = len(python_processes)
                
        except Exception as e:
            result["error"] = str(e)
            
        return result
        
    def run_all_checks(self) -> Dict:
        """运行所有检查"""
        print("🔍 开始系统健康检查...")
        
        self.results = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "hostname": subprocess.getoutput("hostname"),
            "checks": {}
        }
        
        # 执行各项检查
        checks = [
            ("cron_tasks", "定时任务", self.check_cron_tasks),
            ("disk_space", "磁盘空间", self.check_disk_space),
            ("log_status", "日志状态", self.check_log_status),
            ("backup_status", "备份状态", self.check_backup_status),
            ("memory_usage", "内存使用", self.check_memory_usage),
            ("python_processes", "Python 进程", self.check_python_processes),
        ]
        
        for key, name, check_func in checks:
            print(f"  检查 {name}...", end=" ")
            try:
                self.results["checks"][key] = check_func()
                print("✅")
            except Exception as e:
                print(f"❌ {e}")
                self.results["checks"][key] = {"status": "error", "error": str(e)}
                
        # 汇总状态
        if self.issues:
            self.results["overall_status"] = "critical"
        elif self.warnings:
            self.results["overall_status"] = "warning"
        else:
            self.results["overall_status"] = "ok"
            
        self.results["issues"] = self.issues
        self.results["warnings"] = self.warnings
        
        return self.results
        
    def generate_report(self) -> str:
        """生成健康报告"""
        if not self.results:
            return "❌ 未执行健康检查"
            
        r = self.results
        
        # 状态表情
        status_emoji = {
            "ok": "✅",
            "warning": "⚠️",
            "critical": "🚨",
            "error": "❌"
        }
        
        overall_emoji = status_emoji.get(r.get("overall_status", "error"), "❓")
        
        report = f"""# 🏥 Memory Suite v4.0 系统健康报告

**生成时间**: {r['timestamp']}
**主机**: {r['hostname']}
**整体状态**: {overall_emoji} {r['overall_status'].upper()}

"""
        
        # 问题和警告
        if r.get("issues"):
            report += "## 🚨 严重问题\n\n"
            for issue in r["issues"]:
                report += f"- ❌ {issue}\n"
            report += "\n"
            
        if r.get("warnings"):
            report += "## ⚠️ 警告\n\n"
            for warning in r["warnings"]:
                report += f"- ⚠️ {warning}\n"
            report += "\n"
            
        # 各项检查详情
        report += "## 📋 检查详情\n\n"
        
        checks = r.get("checks", {})
        
        # 定时任务
        if "cron_tasks" in checks:
            ct = checks["cron_tasks"]
            report += f"### ⏰ 定时任务\n\n"
            if ct.get("status") == "ok":
                report += f"- 任务总数：{ct.get('total', 0)}\n"
                for task in ct.get("tasks", [])[:5]:
                    report += f"  - `{task['schedule']}` **{task['name']}**\n"
            else:
                report += f"- 状态：{ct.get('status', 'unknown')}\n"
                if ct.get("error"):
                    report += f"- 错误：{ct['error']}\n"
            report += "\n"
            
        # 磁盘空间
        if "disk_space" in checks:
            ds = checks["disk_space"]
            report += f"### 💾 磁盘空间\n\n"
            for part in ds.get("partitions", []):
                if "error" not in part:
                    usage_bar = "█" * (part["usage_percent"] // 10) + "░" * (10 - part["usage_percent"] // 10)
                    report += f"- **{part['name']}**: `{usage_bar}` {part['usage_percent']}% ({part['used']}/{part['total']})\n"
                else:
                    report += f"- **{part['name']}**: ❌ {part['error']}\n"
            report += "\n"
            
        # 日志状态
        if "log_status" in checks:
            ls = checks["log_status"]
            report += f"### 📝 日志状态\n\n"
            if ls.get("exists"):
                report += f"- 文件：{ls['log_file']}\n"
                report += f"- 大小：{ls.get('size_mb', 0)} MB\n"
                report += f"- 最后更新：{ls.get('last_modified', 'unknown')}\n"
                if ls.get("recent_errors", 0) > 0:
                    report += f"- 最近错误：{ls['recent_errors']} 条\n"
                if ls.get("recent_warnings", 0) > 0:
                    report += f"- 最近警告：{ls['recent_warnings']} 条\n"
            else:
                report += "- ❌ 日志文件不存在\n"
            report += "\n"
            
        # 备份状态
        if "backup_status" in checks:
            bs = checks["backup_status"]
            report += f"### 📦 备份状态\n\n"
            if bs.get("exists"):
                report += f"- 最新备份：{bs.get('latest_backup', 'unknown')}\n"
                report += f"- 备份时间：{bs.get('latest_backup_time', 'unknown')}\n"
                report += f"- 距今天数：{bs.get('days_since_backup', '?')} 天\n"
                report += f"- 备份总数：{bs.get('total_backups', 0)}\n"
            else:
                report += "- ❌ 备份目录不存在\n"
            report += "\n"
            
        # 内存使用
        if "memory_usage" in checks:
            mu = checks["memory_usage"]
            report += f"### 🧠 内存使用\n\n"
            if "used_percent" in mu:
                report += f"- 使用率：{mu['used_percent']}%\n"
            elif mu.get("error"):
                report += f"- ❌ {mu['error']}\n"
            else:
                report += "- 无法获取\n"
            report += "\n"
            
        # Python 进程
        if "python_processes" in checks:
            pp = checks["python_processes"]
            report += f"### 🐍 Python 进程\n\n"
            report += f"- 运行中进程：{pp.get('count', 0)} 个\n"
            for proc in pp.get("processes", [])[:3]:
                report += f"  - PID {proc['pid']}: CPU {proc['cpu']}% MEM {proc['mem']}%\n"
            report += "\n"
            
        # 建议
        if r.get("warnings") or r.get("issues"):
            report += "## 💡 建议\n\n"
            if r.get("issues"):
                report += "1. 🔴 优先处理严重问题\n"
            if any("备份" in w for w in r.get("warnings", [])):
                report += "2. 📦 检查备份任务是否正常运行\n"
            if any("日志" in w for w in r.get("warnings", [])):
                report += "3. 📝 检查相关服务日志\n"
            if any("磁盘" in w or "使用率" in w for w in r.get("warnings", [])):
                report += "4. 💾 清理磁盘空间或扩容\n"
            report += "\n"
            
        report += "---\n"
        report += f"*Memory Suite v4.0 | 健康检查*\n"
        
        return report
        
    def send_feishu(self, report: str) -> bool:
        """发送飞书通知"""
        try:
            # 保存报告到文件
            REPORT_FILE.write_text(report, encoding='utf-8')
            
            # 使用广播专员发送
            broadcaster = WORKSPACE / "agents" / "kilo" / "broadcaster.py"
            if broadcaster.exists():
                result = subprocess.run(
                    [
                        "python3", str(broadcaster),
                        "--task", "send",
                        "--message", f"🏥 系统健康报告 ({self.results.get('overall_status', 'unknown').upper()})",
                        "--file", str(REPORT_FILE),
                        "--target", "group"
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return result.returncode == 0
            else:
                print("⚠️ 广播专员不存在")
                return False
                
        except Exception as e:
            print(f"❌ 发送失败：{e}")
            return False


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Suite v4.0 系统健康检查')
    parser.add_argument('--check', '-c', action='store_true', help='执行健康检查')
    parser.add_argument('--report', '-r', action='store_true', help='生成报告')
    parser.add_argument('--notify', '-n', action='store_true', help='发送飞书通知')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--all', '-a', action='store_true', help='执行全部操作')
    
    args = parser.parse_args()
    
    # 默认执行全部
    if not any([args.check, args.report, args.notify]):
        args.all = True
        
    checker = HealthChecker()
    
    if args.all or args.check:
        checker.run_all_checks()
        
    if args.all or args.report:
        if not checker.results:
            checker.run_all_checks()
        report = checker.generate_report()
        
        if args.output:
            Path(args.output).write_text(report, encoding='utf-8')
            print(f"✅ 报告已保存：{args.output}")
        else:
            print(report)
            
    if args.notify:
        if not checker.results:
            checker.run_all_checks()
        report = checker.generate_report()
        success = checker.send_feishu(report)
        if success:
            print("✅ 飞书通知已发送")
        else:
            print("❌ 飞书通知发送失败")


if __name__ == "__main__":
    main()
