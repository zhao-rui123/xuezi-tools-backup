#!/usr/bin/env python3
"""
Monitor Service - 监控服务
任务看板、日志聚合、健康报告
"""

import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

WORKSPACE = Path.home() / ".openclaw" / "workspace"
LOG_DIR = Path("/tmp")


class MonitorService:
    """监控服务"""
    
    def __init__(self, workspace: Optional[Path] = None):
        self.workspace = workspace or WORKSPACE
        self.log_dir = LOG_DIR
        
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
                last_lines = lines[-20:] if len(lines) > 20 else lines
                
                has_error = any('error' in line.lower() or '❌' in line for line in last_lines)
                has_success = any('success' in line.lower() or '✅' in line for line in last_lines)
                
                return {
                    "exists": True,
                    "size": stat.st_size,
                    "last_update": mtime.isoformat(),
                    "hours_ago": round(hours_ago, 1),
                    "status": "error" if has_error else "success" if has_success else "unknown"
                }
        except:
            return {"exists": True, "status": "read_error"}
            
    def get_task_dashboard(self) -> str:
        """生成任务看板"""
        tasks = self.get_cron_tasks()
        
        dashboard = f"""# 📊 定时任务看板

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
任务总数: {len(tasks)}

| 任务名 | 调度 | 状态 |
|--------|------|------|
"""
        
        # 常见日志文件映射
        log_mapping = {
            "backup": "backup_cron.log",
            "memory": "ums-daily.log",
            "evolution": "evolution-daily.log",
            "health": "daily-health.log"
        }
        
        for task in tasks:
            if "error" in task:
                continue
                
            name = task.get("name", "unknown")
            schedule = task.get("schedule", "-")
            
            # 检查对应日志
            log_file = self.log_dir / log_mapping.get(name, f"{name}.log")
            status_info = self.check_log_status(log_file)
            
            if status_info.get("exists"):
                if status_info.get("status") == "error":
                    status = "🔴 错误"
                elif status_info.get("status") == "success":
                    hours = status_info.get("hours_ago", 999)
                    if hours < 24:
                        status = f"✅ 正常 ({hours}h前)"
                    else:
                        status = f"⚠️ 滞后 ({hours}h前)"
                else:
                    status = "🟡 未知"
            else:
                status = "⚪ 无日志"
                
            dashboard += f"| {name} | `{schedule}` | {status} |\n"
            
        return dashboard
        
    def aggregate_logs(self, service: Optional[str] = None) -> Dict:
        """聚合日志"""
        logs = {}
        
        # 按服务分类的日志模式
        patterns = {
            "memory": ["ums-*.log", "memory*.log"],
            "backup": ["backup*.log"],
            "evolution": ["evolution*.log"],
            "system": ["daily-health.log", "system-*.log"]
        }
        
        if service and service in patterns:
            patterns = {service: patterns[service]}
            
        for svc, patterns_list in patterns.items():
            logs[svc] = []
            
            for pattern in patterns_list:
                for log_file in self.log_dir.glob(pattern):
                    info = self.check_log_status(log_file)
                    if info.get("exists"):
                        logs[svc].append({
                            "file": log_file.name,
                            **info
                        })
                        
        return logs
        
    def generate_health_report(self) -> str:
        """生成健康报告"""
        report = f"""# 🏥 系统健康报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 📋 定时任务状态

{self.get_task_dashboard()}

## 💾 磁盘空间

"""
        
        # 检查磁盘空间
        try:
            result = subprocess.run(
                ["df", "-h", str(WORKSPACE)],
                capture_output=True,
                text=True
            )
            report += "```\n" + result.stdout + "\n```\n"
        except:
            report += "⚠️ 无法获取磁盘信息\n"
            
        # 检查备份磁盘
        report += "\n## 📦 备份磁盘\n\n"
        try:
            result = subprocess.run(
                ["df", "-h", "/Volumes/cu/ocu"],
                capture_output=True,
                text=True
            )
            report += "```\n" + result.stdout + "\n```\n"
        except:
            report += "⚠️ 备份磁盘未挂载\n"
            
        # 日志统计
        report += "\n## 📝 日志统计\n\n"
        logs = self.aggregate_logs()
        
        for svc, log_list in logs.items():
            report += f"### {svc}\n\n"
            for log in log_list:
                status_emoji = "✅" if log.get("status") == "success" else "🔴" if log.get("status") == "error" else "🟡"
                report += f"- {status_emoji} {log['file']} ({log.get('hours_ago', '?')}h前)\n"
            report += "\n"
            
        return report


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='监控服务')
    parser.add_argument('--dashboard', '-d', action='store_true', help='显示任务看板')
    parser.add_argument('--logs', '-l', help='聚合指定服务的日志')
    parser.add_argument('--health', '-H', action='store_true', help='生成健康报告')
    parser.add_argument('--output', '-o', help='输出文件')
    
    args = parser.parse_args()
    
    service = MonitorService()
    
    if args.dashboard:
        output = service.get_task_dashboard()
    elif args.logs:
        output = json.dumps(service.aggregate_logs(args.logs), ensure_ascii=False, indent=2)
    elif args.health:
        output = service.generate_health_report()
    else:
        parser.print_help()
        return
        
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"✅ 已保存: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
