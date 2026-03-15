#!/usr/bin/env python3
"""
Memory Suite v4.0 - 统一监控服务
整合原 services/monitor/ 功能，提供完整监控能力

功能:
- 定时任务监控
- 日志聚合分析
- 健康报告生成
- 飞书通知推送
"""

import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

WORKSPACE = Path.home() / ".openclaw" / "workspace"
LOG_DIR = Path("/tmp")
UNIFIED_LOG = LOG_DIR / "memory-suite.log"


class MonitorService:
    """统一监控服务 v4.0"""
    
    VERSION = "4.0.0"
    
    def __init__(self, workspace: Optional[Path] = None):
        self.workspace = workspace or WORKSPACE
        self.log_dir = LOG_DIR
        self.unified_log = UNIFIED_LOG
        
        # 日志文件映射 (统一命名规范)
        self.log_mapping = {
            "backup": "memory-suite.log",
            "memory": "memory-suite.log",
            "evolution": "memory-suite.log",
            "health": "memory-suite.log",
            "alert": "memory-suite.log",
            "stock": "memory-suite.log",
            "cron": "memory-suite.log",
        }
        
    def log(self, level: str, message: str):
        """写入统一日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"
        
        # 追加到统一日志
        with open(self.unified_log, 'a', encoding='utf-8') as f:
            f.write(log_line)
            
    def get_cron_tasks(self) -> List[Dict]:
        """获取所有定时任务"""
        try:
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True
            )
            
            tasks = []
            for line in result.stdout.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # 解析 crontab 行
                parts = line.split()
                if len(parts) >= 6:
                    schedule = ' '.join(parts[:5])
                    command = ' '.join(parts[5:])
                    
                    # 提取任务名
                    task_name = self._extract_task_name(command)
                    
                    tasks.append({
                        "schedule": schedule,
                        "command": command[:100] + "..." if len(command) > 100 else command,
                        "name": task_name
                    })
                    
            return tasks
            
        except Exception as e:
            return [{"error": str(e)}]
            
    def _extract_task_name(self, command: str) -> str:
        """从命令中提取任务名"""
        # 匹配 python 文件名
        match = re.search(r'(\w+)\.py', command)
        if match:
            return match.group(1)
        # 匹配 shell 脚本名
        match = re.search(r'(\w+)\.sh', command)
        if match:
            return match.group(1)
        # 匹配服务名
        if 'memory' in command:
            return "memory"
        elif 'backup' in command:
            return "backup"
        return "unknown"
        
    def check_log_status(self, log_file: Path) -> Dict:
        """检查日志文件状态"""
        if not log_file.exists():
            return {"exists": False, "status": "no_log"}
            
        stat = log_file.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime)
        
        # 检查最近是否有更新
        hours_ago = (datetime.now() - mtime).total_seconds() / 3600
        
        # 读取最后几行检查错误
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                last_lines = lines[-50:] if len(lines) > 50 else lines
                
                has_error = any('error' in line.lower() or '❌' in line or '[ERROR]' in line for line in last_lines)
                has_success = any('success' in line.lower() or '✅' in line or '[SUCCESS]' in line for line in last_lines)
                has_warning = any('warning' in line.lower() or '⚠️' in line or '[WARN]' in line for line in last_lines)
                
                return {
                    "exists": True,
                    "size": stat.st_size,
                    "last_update": mtime.isoformat(),
                    "hours_ago": round(hours_ago, 1),
                    "status": "error" if has_error else "warning" if has_warning else "success" if has_success else "unknown"
                }
        except:
            return {"exists": True, "status": "read_error"}
            
    def get_task_dashboard(self) -> str:
        """生成任务看板"""
        tasks = self.get_cron_tasks()
        
        dashboard = f"""# 📊 定时任务看板 v{self.VERSION}

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
任务总数: {len(tasks)}

| 任务名 | 调度 | 状态 |
|--------|------|------|
"""
        
        for task in tasks:
            if "error" in task:
                continue
                
            name = task.get("name", "unknown")
            schedule = task.get("schedule", "-")
            
            # 检查统一日志中的任务状态
            status_info = self._check_task_in_unified_log(name)
            
            if status_info.get("found"):
                if status_info.get("status") == "error":
                    status = f"🔴 错误 ({status_info.get('hours_ago', '?')}h前)"
                elif status_info.get("status") == "warning":
                    status = f"🟡 警告 ({status_info.get('hours_ago', '?')}h前)"
                elif status_info.get("status") == "success":
                    status = f"✅ 正常 ({status_info.get('hours_ago', '?')}h前)"
                else:
                    status = f"⚪ 未知"
            else:
                status = "⚪ 无记录"
                
            dashboard += f"| {name} | `{schedule}` | {status} |\n"
            
        return dashboard
        
    def _check_task_in_unified_log(self, task_name: str) -> Dict:
        """在统一日志中检查任务状态"""
        if not self.unified_log.exists():
            return {"found": False}
            
        try:
            with open(self.unified_log, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
                # 查找任务相关日志（倒序）
                for line in reversed(lines):
                    if task_name.lower() in line.lower():
                        # 解析时间戳
                        time_match = re.match(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
                        if time_match:
                            log_time = datetime.strptime(time_match.group(1), "%Y-%m-%d %H:%M:%S")
                            hours_ago = (datetime.now() - log_time).total_seconds() / 3600
                            
                            # 判断状态
                            if '[ERROR]' in line or '❌' in line:
                                return {"found": True, "status": "error", "hours_ago": round(hours_ago, 1)}
                            elif '[WARN]' in line or '⚠️' in line:
                                return {"found": True, "status": "warning", "hours_ago": round(hours_ago, 1)}
                            elif '[SUCCESS]' in line or '✅' in line:
                                return {"found": True, "status": "success", "hours_ago": round(hours_ago, 1)}
                            else:
                                return {"found": True, "status": "unknown", "hours_ago": round(hours_ago, 1)}
                                
                return {"found": False}
        except:
            return {"found": False, "error": "read_failed"}
            
    def aggregate_logs(self, days: int = 7) -> Dict:
        """聚合日志 (从统一日志中提取)"""
        if not self.unified_log.exists():
            return {"error": "统一日志不存在"}
            
        logs = {
            "summary": {},
            "errors": [],
            "warnings": [],
            "tasks": {}
        }
        
        cutoff = datetime.now() - timedelta(days=days)
        
        try:
            with open(self.unified_log, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    # 解析时间戳
                    time_match = re.match(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
                    if time_match:
                        log_time = datetime.strptime(time_match.group(1), "%Y-%m-%d %H:%M:%S")
                        if log_time < cutoff:
                            continue
                            
                        # 统计错误和警告
                        if '[ERROR]' in line or '❌' in line:
                            logs["errors"].append({
                                "time": time_match.group(1),
                                "message": line.strip()
                            })
                        elif '[WARN]' in line or '⚠️' in line:
                            logs["warnings"].append({
                                "time": time_match.group(1),
                                "message": line.strip()
                            })
                                
            logs["summary"] = {
                "total_errors": len(logs["errors"]),
                "total_warnings": len(logs["warnings"]),
                "period_days": days
            }
            
            return logs
            
        except Exception as e:
            return {"error": str(e)}
            
    def check_disk_space(self) -> Dict:
        """检查磁盘空间"""
        result = {}
        
        # 检查工作区磁盘
        try:
            df_result = subprocess.run(
                ["df", "-h", str(WORKSPACE)],
                capture_output=True,
                text=True
            )
            result["workspace"] = df_result.stdout
        except Exception as e:
            result["workspace_error"] = str(e)
            
        # 检查备份磁盘
        try:
            df_result = subprocess.run(
                ["df", "-h", "/Volumes/cu/ocu"],
                capture_output=True,
                text=True
            )
            result["backup"] = df_result.stdout
        except:
            result["backup"] = "未挂载"
            
        return result
        
    def generate_health_report(self) -> str:
        """生成健康报告"""
        report_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        report = f"""# 🏥 Memory Suite v4.0 系统健康报告

生成时间: {report_time}
版本: v{self.VERSION}

## 📋 定时任务状态

{self.get_task_dashboard()}

## 💾 磁盘空间

"""
        
        # 磁盘空间
        disk_info = self.check_disk_space()
        for key, value in disk_info.items():
            if "error" not in key:
                report += f"### {key}\n```\n{value}\n```\n\n"
            else:
                report += f"### {key}\n⚠️ {value}\n\n"
                
        # 日志统计
        report += "## 📝 日志统计 (最近7天)\n\n"
        logs = self.aggregate_logs(days=7)
        
        if "error" in logs:
            report += f"⚠️ {logs['error']}\n\n"
        else:
            summary = logs.get("summary", {})
            report += f"- 🔴 错误数: {summary.get('total_errors', 0)}\n"
            report += f"- 🟡 警告数: {summary.get('total_warnings', 0)}\n"
            report += f"- 📅 统计周期: {summary.get('period_days', 7)} 天\n\n"
            
            if logs.get("errors"):
                report += "### 最近错误\n\n"
                for error in logs["errors"][:5]:
                    report += f"- `{error['time']}` {error['message'][:100]}...\n"
                report += "\n"
                
        # 统一日志状态
        report += "## 📁 统一日志状态\n\n"
        log_status = self.check_log_status(self.unified_log)
        if log_status.get("exists"):
            report += f"- 📄 文件: {self.unified_log}\n"
            report += f"- 📦 大小: {log_status['size'] / 1024:.1f} KB\n"
            report += f"- 🕐 最后更新: {log_status['last_update']}\n"
            report += f"- ✅ 状态: {log_status['status']}\n"
        else:
            report += "⚠️ 统一日志不存在\n"
            
        return report
        
    def send_feishu_report(self, report: str) -> bool:
        """发送飞书报告"""
        try:
            # 尝试使用广播专员
            broadcaster_path = self.workspace / "agents" / "kilo" / "broadcaster.py"
            if broadcaster_path.exists():
                # 保存报告到临时文件
                report_file = Path("/tmp/health_report.md")
                report_file.write_text(report, encoding='utf-8')
                
                result = subprocess.run(
                    [
                        "python3", str(broadcaster_path),
                        "--task", "send",
                        "--message", "🏥 Memory Suite v4.0 系统健康报告已生成",
                        "--file", str(report_file),
                        "--target", "group"
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return result.returncode == 0
            else:
                self.log("WARN", "广播专员不存在，无法发送飞书通知")
                return False
        except Exception as e:
            self.log("ERROR", f"发送飞书报告失败: {e}")
            return False


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Suite v4.0 统一监控服务')
    parser.add_argument('--dashboard', '-d', action='store_true', help='显示任务看板')
    parser.add_argument('--logs', '-l', type=int, default=7, help='聚合最近N天的日志')
    parser.add_argument('--health', '-H', action='store_true', help='生成健康报告')
    parser.add_argument('--notify', '-n', action='store_true', help='发送飞书通知')
    parser.add_argument('--output', '-o', help='输出文件')
    parser.add_argument('--version', '-v', action='version', version='%(prog)s v4.0.0')
    
    args = parser.parse_args()
    
    service = MonitorService()
    
    if args.dashboard:
        output = service.get_task_dashboard()
    elif args.health:
        output = service.generate_health_report()
        if args.notify:
            service.send_feishu_report(output)
    elif args.logs:
        output = json.dumps(service.aggregate_logs(args.logs), ensure_ascii=False, indent=2)
    else:
        # 默认生成健康报告
        output = service.generate_health_report()
        
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"✅ 已保存: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
