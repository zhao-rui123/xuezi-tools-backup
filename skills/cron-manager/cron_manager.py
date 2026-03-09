#!/usr/bin/env python3
"""
定时任务统一管理系统 (Cron Manager)
功能：统一管理所有技能包定时任务
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

CRON_CONFIG_FILE = Path("~/.openclaw/workspace/cron_manager_config.json").expanduser()
LOG_FILE = Path("~/.openclaw/workspace/logs/cron_manager.log").expanduser()

@dataclass
class CronJob:
    name: str
    schedule: str  # cron表达式
    command: str
    log_file: str
    enabled: bool = True
    last_run: Optional[str] = None
    last_status: Optional[str] = None  # success, failed, running
    description: str = ""

class CronManager:
    """定时任务管理器"""
    
    def __init__(self):
        self.jobs: Dict[str, CronJob] = {}
        self.load_config()
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    def load_config(self):
        """加载配置"""
        if CRON_CONFIG_FILE.exists():
            with open(CRON_CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for name, job_data in data.get('jobs', {}).items():
                    self.jobs[name] = CronJob(**job_data)
    
    def save_config(self):
        """保存配置"""
        data = {
            'updated_at': datetime.now().isoformat(),
            'jobs': {name: asdict(job) for name, job in self.jobs.items()}
        }
        with open(CRON_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def register_job(self, name: str, schedule: str, command: str, 
                     log_file: str, description: str = ""):
        """注册定时任务"""
        self.jobs[name] = CronJob(
            name=name,
            schedule=schedule,
            command=command,
            log_file=log_file,
            description=description
        )
        self.save_config()
        print(f"✅ 已注册任务: {name}")
    
    def enable_job(self, name: str):
        """启用任务"""
        if name in self.jobs:
            self.jobs[name].enabled = True
            self.save_config()
            print(f"✅ 已启用: {name}")
    
    def disable_job(self, name: str):
        """禁用任务"""
        if name in self.jobs:
            self.jobs[name].enabled = False
            self.save_config()
            print(f"✅ 已禁用: {name}")
    
    def get_cron_line(self, job: CronJob) -> str:
        """生成crontab行"""
        return f"{job.schedule} {job.command} >> {job.log_file} 2>&1"
    
    def apply_to_crontab(self):
        """应用到系统crontab"""
        # 获取当前crontab
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_crontab = result.stdout if result.returncode == 0 else ""
        
        # 过滤掉我们的任务（标记为# Managed by CronManager）
        lines = current_crontab.split('\n')
        new_lines = []
        skip = False
        for line in lines:
            if '# CronManager START' in line:
                skip = True
                continue
            if '# CronManager END' in line:
                skip = False
                continue
            if not skip:
                new_lines.append(line)
        
        # 添加我们的任务
        new_lines.append('')
        new_lines.append('# CronManager START - 由定时任务管理器自动管理')
        new_lines.append(f'# 更新时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
        
        for name, job in self.jobs.items():
            if job.enabled:
                new_lines.append(f'')
                new_lines.append(f'# {name}: {job.description}')
                new_lines.append(self.get_cron_line(job))
        
        new_lines.append('')
        new_lines.append('# CronManager END')
        
        # 写入crontab
        new_crontab = '\n'.join(new_lines)
        subprocess.run(['crontab', '-'], input=new_crontab, text=True)
        print("✅ 已更新系统crontab")
    
    def list_jobs(self):
        """列出所有任务"""
        print("=" * 80)
        print("📋 定时任务列表")
        print("=" * 80)
        print(f"{'名称':<30} {'状态':<8} {'调度':<20} {'描述'}")
        print("-" * 80)
        for name, job in self.jobs.items():
            status = "🟢 启用" if job.enabled else "🔴 禁用"
            print(f"{name:<30} {status:<10} {job.schedule:<20} {job.description[:30]}")
        print("=" * 80)
    
    def run_job(self, name: str):
        """手动运行任务"""
        if name not in self.jobs:
            print(f"❌ 任务不存在: {name}")
            return
        
        job = self.jobs[name]
        print(f"🚀 运行任务: {name}")
        print(f"   命令: {job.command}")
        
        job.last_run = datetime.now().isoformat()
        job.last_status = "running"
        
        result = subprocess.run(job.command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            job.last_status = "success"
            print(f"✅ 任务成功完成")
        else:
            job.last_status = "failed"
            print(f"❌ 任务失败")
            print(f"   错误: {result.stderr[:200]}")
        
        self.save_config()
    
    def init_default_jobs(self):
        """初始化默认任务"""
        default_jobs = [
            ('unified-memory', '0 1 * * *', 
             '~/.openclaw/workspace/skills/unified-memory/cron_tasks.sh',
             '/tmp/unified-memory-cron.log',
             '统一记忆系统定时任务'),
            ('daily-health-check', '0 9 * * *',
             '~/.openclaw/workspace/skills/system-maintenance/daily-health-check.sh',
             '/tmp/daily-health.log',
             '每日健康检查'),
            ('system-maintenance', '0 2 * * 0',
             '~/.openclaw/workspace/skills/system-maintenance/system-maintenance.sh',
             '/tmp/system-maintenance.log',
             '系统维护（每周日）'),
            ('backup-check', '5 22 * * *',
             '~/.openclaw/workspace/scripts/backup-check.sh',
             '/tmp/backup-check.log',
             '备份检查'),
        ]
        
        for name, schedule, command, log_file, desc in default_jobs:
            if name not in self.jobs:
                self.register_job(name, schedule, command, log_file, desc)
        
        print("✅ 默认任务已初始化")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='定时任务管理器')
    parser.add_argument('--init', action='store_true', help='初始化默认任务')
    parser.add_argument('--list', action='store_true', help='列出所有任务')
    parser.add_argument('--apply', action='store_true', help='应用到crontab')
    parser.add_argument('--run', type=str, help='手动运行指定任务')
    parser.add_argument('--enable', type=str, help='启用任务')
    parser.add_argument('--disable', type=str, help='禁用任务')
    
    args = parser.parse_args()
    
    manager = CronManager()
    
    if args.init:
        manager.init_default_jobs()
    elif args.list:
        manager.list_jobs()
    elif args.apply:
        manager.apply_to_crontab()
    elif args.run:
        manager.run_job(args.run)
    elif args.enable:
        manager.enable_job(args.enable)
    elif args.disable:
        manager.disable_job(args.disable)
    else:
        manager.list_jobs()

if __name__ == '__main__':
    main()
