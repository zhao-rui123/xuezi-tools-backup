#!/usr/bin/env python3
"""
系统监控模块 - 读取本地系统状态
零Token消耗，只读本地文件
"""

import os
import json
import subprocess
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 路径配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
SKILLS_DIR = WORKSPACE / "skills"
CRON_CONFIG_FILE = WORKSPACE / "cron_manager_config.json"


class MemoryStatsReader:
    """Memory Suite 状态读取器"""
    
    @staticmethod
    def get_skill_memory() -> Dict[str, Any]:
        """读取技能记忆统计"""
        skill_memory_file = MEMORY_DIR / "skill_memory.json"
        
        if not skill_memory_file.exists():
            return {"error": "技能记忆文件不存在", "skills_count": 0}
        
        try:
            with open(skill_memory_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            skills = data.get('skills', {})
            total_skills = len(skills)
            
            # 计算分类统计
            categories = {}
            for name, skill in skills.items():
                cat = skill.get('category', 'unknown')
                categories[cat] = categories.get(cat, 0) + 1
            
            # 计算标签统计
            all_tags = []
            for name, skill in skills.items():
                all_tags.extend(skill.get('tags', []))
            
            tag_counts = {}
            for tag in all_tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            return {
                "total_skills": total_skills,
                "categories": categories,
                "top_tags": sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10],
                "timestamp": data.get('timestamp'),
                "skills": [
                    {
                        "name": name,
                        "category": s.get('category'),
                        "usage_count": s.get('usage_count', 0),
                        "tags": s.get('tags', [])
                    }
                    for name, s in list(skills.items())[:20]  # 只返回前20个
                ]
            }
        except Exception as e:
            return {"error": str(e), "skills_count": 0}
    
    @staticmethod
    def get_memory_scores() -> Dict[str, Any]:
        """读取记忆评分统计"""
        scores_file = MEMORY_DIR / "memory_scores.json"
        
        if not scores_file.exists():
            return {"error": "记忆评分文件不存在", "files_count": 0}
        
        try:
            with open(scores_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            scores = data.get('scores', [])
            
            # 按类别统计
            categories = {}
            for item in scores:
                cat = item.get('category', 'unknown')
                categories[cat] = categories.get(cat, 0) + 1
            
            # 按重要性统计
            high_importance = sum(1 for s in scores if s.get('importance', 0) >= 0.9)
            medium_importance = sum(1 for s in scores if 0.7 <= s.get('importance', 0) < 0.9)
            low_importance = sum(1 for s in scores if s.get('importance', 0) < 0.7)
            
            return {
                "total_files": len(scores),
                "categories": categories,
                "importance_distribution": {
                    "high": high_importance,
                    "medium": medium_importance,
                    "low": low_importance
                },
                "timestamp": data.get('timestamp'),
                "recent_files": scores[:10]
            }
        except Exception as e:
            return {"error": str(e), "files_count": 0}
    
    @staticmethod
    def get_memory_files_status() -> Dict[str, Any]:
        """获取记忆文件状态"""
        try:
            memory_files = list(MEMORY_DIR.glob("*.md"))
            archive_files = list((MEMORY_DIR / "archive").rglob("*.md")) if (MEMORY_DIR / "archive").exists() else []
            
            # 获取今日文件
            today = datetime.now().strftime("%Y-%m-%d")
            today_file = MEMORY_DIR / f"{today}.md"
            today_exists = today_file.exists()
            today_size = today_file.stat().st_size if today_exists else 0
            
            return {
                "daily_files": len(memory_files),
                "archive_files": len(archive_files),
                "today_file_exists": today_exists,
                "today_file_size": today_size,
                "memory_dir_size": MemoryStatsReader._get_dir_size(MEMORY_DIR)
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def _get_dir_size(path: Path) -> int:
        """计算目录大小"""
        total = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += MemoryStatsReader._get_dir_size(Path(entry.path))
        except:
            pass
        return total


class CronTasksReader:
    """定时任务状态读取器"""
    
    @staticmethod
    def get_crontab_tasks() -> List[Dict[str, Any]]:
        """从系统crontab读取任务"""
        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if result.returncode != 0:
                return []
            
            tasks = []
            lines = result.stdout.split('\n')
            current_group = "其他"
            
            for line in lines:
                line = line.strip()
                
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    # 检查是否是分组标记
                    if '---' in line and '任务' in line:
                        current_group = line.split('---')[-1].strip().replace('任务', '').strip()
                    continue
                
                # 解析cron行
                parts = line.split()
                if len(parts) >= 6:
                    schedule = ' '.join(parts[:5])
                    command = ' '.join(parts[5:])
                    
                    tasks.append({
                        "schedule": schedule,
                        "command": command[:100] + '...' if len(command) > 100 else command,
                        "group": current_group,
                        "enabled": True
                    })
            
            return tasks
        except Exception as e:
            return [{"error": str(e)}]
    
    @staticmethod
    def get_cron_manager_tasks() -> Dict[str, Any]:
        """从cron_manager配置读取任务"""
        if not CRON_CONFIG_FILE.exists():
            return {"error": "Cron Manager配置不存在", "tasks": []}
        
        try:
            with open(CRON_CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            jobs = data.get('jobs', {})
            tasks = []
            
            for name, job in jobs.items():
                tasks.append({
                    "name": name,
                    "schedule": job.get('schedule'),
                    "command": job.get('command'),
                    "enabled": job.get('enabled', True),
                    "last_run": job.get('last_run'),
                    "last_status": job.get('last_status'),
                    "description": job.get('description', '')
                })
            
            return {
                "total_tasks": len(tasks),
                "enabled_count": sum(1 for t in tasks if t['enabled']),
                "disabled_count": sum(1 for t in tasks if not t['enabled']),
                "tasks": tasks
            }
        except Exception as e:
            return {"error": str(e), "tasks": []}
    
    @staticmethod
    def get_cron_logs() -> Dict[str, Any]:
        """获取定时任务日志状态"""
        log_files = [
            "/tmp/memory-suite.log",
            "/tmp/backup_cron.log",
            "/tmp/service-monitor.log",
            "/tmp/stock_push.log"
        ]
        
        logs_status = {}
        for log_file in log_files:
            path = Path(log_file)
            if path.exists():
                stat = path.stat()
                logs_status[log_file] = {
                    "exists": True,
                    "size": stat.st_size,
                    "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
            else:
                logs_status[log_file] = {"exists": False}
        
        return logs_status


class SystemHealthReader:
    """系统健康状态读取器"""
    
    @staticmethod
    def get_disk_usage() -> Dict[str, Any]:
        """获取磁盘使用情况"""
        try:
            disk = psutil.disk_usage('/')
            return {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent,
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2)
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_memory_usage() -> Dict[str, Any]:
        """获取内存使用情况"""
        try:
            mem = psutil.virtual_memory()
            return {
                "total": mem.total,
                "available": mem.available,
                "used": mem.used,
                "percent": mem.percent,
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "used_gb": round(mem.used / (1024**3), 2)
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_cpu_usage() -> Dict[str, Any]:
        """获取CPU使用情况"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            return {
                "percent": cpu_percent,
                "count": cpu_count,
                "freq_current": cpu_freq.current if cpu_freq else None,
                "freq_max": cpu_freq.max if cpu_freq else None
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_processes() -> Dict[str, Any]:
        """获取进程信息"""
        try:
            # OpenClaw相关进程
            openclaw_procs = []
            python_procs = []
            node_procs = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_percent', 'cpu_percent']):
                try:
                    name = proc.info['name'] or ''
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    
                    if 'openclaw' in cmdline.lower() or 'openclaw' in name.lower():
                        openclaw_procs.append({
                            "pid": proc.info['pid'],
                            "name": name,
                            "cmdline": cmdline[:100] + '...' if len(cmdline) > 100 else cmdline,
                            "memory_percent": round(proc.info['memory_percent'] or 0, 2),
                            "cpu_percent": round(proc.info['cpu_percent'] or 0, 2)
                        })
                    elif name.startswith('python') or 'python' in name:
                        python_procs.append({
                            "pid": proc.info['pid'],
                            "name": name,
                            "cmdline": cmdline[:100] + '...' if len(cmdline) > 100 else cmdline
                        })
                    elif name.startswith('node') or 'node' in name:
                        node_procs.append({
                            "pid": proc.info['pid'],
                            "name": name,
                            "cmdline": cmdline[:100] + '...' if len(cmdline) > 100 else cmdline
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                "openclaw_processes": openclaw_procs[:10],
                "openclaw_count": len(openclaw_procs),
                "python_count": len(python_procs),
                "node_count": len(node_procs),
                "total_processes": len(list(psutil.process_iter()))
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_workspace_stats() -> Dict[str, Any]:
        """获取工作空间统计"""
        try:
            # 统计技能包数量
            skills_count = len([d for d in SKILLS_DIR.iterdir() if d.is_dir()]) if SKILLS_DIR.exists() else 0
            
            # 统计项目数量
            projects_dir = WORKSPACE / "projects"
            projects_count = len([d for d in projects_dir.iterdir() if d.is_dir()]) if projects_dir.exists() else 0
            
            # 统计脚本数量
            scripts_dir = WORKSPACE / "scripts"
            scripts_count = len(list(scripts_dir.glob("*.py"))) if scripts_dir.exists() else 0
            
            return {
                "skills_count": skills_count,
                "projects_count": projects_count,
                "scripts_count": scripts_count,
                "workspace_path": str(WORKSPACE)
            }
        except Exception as e:
            return {"error": str(e)}


# 统一接口
def get_system_status() -> Dict[str, Any]:
    """获取完整系统状态"""
    return {
        "timestamp": datetime.now().isoformat(),
        "disk": SystemHealthReader.get_disk_usage(),
        "memory": SystemHealthReader.get_memory_usage(),
        "cpu": SystemHealthReader.get_cpu_usage(),
        "processes": SystemHealthReader.get_processes(),
        "workspace": SystemHealthReader.get_workspace_stats()
    }


def get_memory_stats() -> Dict[str, Any]:
    """获取Memory Suite统计"""
    return {
        "timestamp": datetime.now().isoformat(),
        "skills": MemoryStatsReader.get_skill_memory(),
        "scores": MemoryStatsReader.get_memory_scores(),
        "files": MemoryStatsReader.get_memory_files_status()
    }


def get_cron_tasks() -> Dict[str, Any]:
    """获取定时任务列表"""
    return {
        "timestamp": datetime.now().isoformat(),
        "crontab_tasks": CronTasksReader.get_crontab_tasks(),
        "managed_tasks": CronTasksReader.get_cron_manager_tasks(),
        "logs": CronTasksReader.get_cron_logs()
    }


if __name__ == "__main__":
    # 测试输出
    print("=== 系统状态 ===")
    print(json.dumps(get_system_status(), indent=2, ensure_ascii=False))
    
    print("\n=== Memory统计 ===")
    print(json.dumps(get_memory_stats(), indent=2, ensure_ascii=False))
    
    print("\n=== 定时任务 ===")
    print(json.dumps(get_cron_tasks(), indent=2, ensure_ascii=False))
