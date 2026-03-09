#!/usr/bin/env python3
"""
定时任务监控通知脚本
每天早上8点统一汇总所有夜间和周期性任务
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# 配置
WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
NOTIFICATION_FILE = MEMORY_DIR / "task_notifications.json"

# 每日任务（22:00-08:00）→ 每天早上8点统一汇总
DAILY_TASKS = {
    "22:00-backup": {
        "name": "每日备份",
        "log_file": "/tmp/backup_cron.log",
        "schedule": "22:00",
        "group": "night"
    },
    "23:00-evolution": {
        "name": "每日自我进化",
        "log_file": "/tmp/evolution-daily.log",
        "schedule": "23:00",
        "group": "night"
    },
    "00:30-ums-daily": {
        "name": "每日记忆归档",
        "log_file": "/tmp/ums-daily.log",
        "schedule": "00:30",
        "group": "early"
    },
    "01:00-knowledge-graph": {
        "name": "知识图谱自动更新",
        "log_file": "/tmp/ums-graph.log",
        "schedule": "01:00",
        "group": "early"
    },
    "01:00-kb-sync": {
        "name": "每日知识同步",
        "log_file": "/tmp/kb-integration.log",
        "schedule": "01:00",
        "group": "early"
    },
    "01:00-ums-cron": {
        "name": "统一记忆系统归档",
        "log_file": "/Users/zhaoruicn/.openclaw/workspace/memory/cron.log",
        "schedule": "01:00",
        "group": "early"
    }
}

# 周日任务
SUNDAY_TASKS = {
    "02:00-system-maint": {
        "name": "系统维护",
        "log_file": "/tmp/system-maintenance.log",
        "schedule": "02:00 (周日)"
    },
    "03:00-ouc-cleanup": {
        "name": "OUC清理",
        "log_file": "/tmp/ouc-cleanup.log",
        "schedule": "03:00 (周日)"
    }
}

# 周一任务
MONDAY_TASKS = {
    "03:00-file-cleanup": {
        "name": "文件清理",
        "log_file": "/tmp/file-cleanup.log",
        "schedule": "03:00 (周一)"
    },
    "04:00-security-scan": {
        "name": "每周安全扫描",
        "log_file": "/tmp/system-guard-scan.log",
        "schedule": "04:00 (周一)"
    },
    "05:00-kb-maintenance": {
        "name": "每周知识库维护",
        "log_file": "/tmp/kb-maintenance.log",
        "schedule": "05:00 (周一)"
    }
}

# 每月1号任务
MONTHLY_TASKS = {
    "03:00-monthly-archive": {
        "name": "月度归档备份",
        "log_file": "/tmp/backup_archive.log",
        "schedule": "03:00 (每月1号)"
    },
    "02:00-monthly-analysis": {
        "name": "月度记忆深度分析",
        "log_file": "/tmp/ums-monthly.log",
        "schedule": "02:00 (每月1号)"
    },
    "08:00-monthly-evolution": {
        "name": "每月深度进化",
        "log_file": "/tmp/evolution-monthly.log",
        "schedule": "08:00 (每月1号)"
    },
    "09:00-evolution-report": {
        "name": "自我进化报告",
        "log_file": "/tmp/evolution-report.log",
        "schedule": "09:00 (每月2号)"
    }
}

# 其他时段任务 → 各自单独通知
OTHER_TASKS = {
    "08:30-english": {
        "name": "每日英语新闻",
        "log_file": "/tmp/english-news.log",
        "schedule": "08:30",
        "notify_time": "09:00"
    }
}

# 自选股推送监控
STOCK_NOTIFICATION_PATTERN = "/tmp/stock_notification_*.txt"

def load_notifications():
    """加载已通知记录"""
    if NOTIFICATION_FILE.exists():
        try:
            with open(NOTIFICATION_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_notifications(data):
    """保存通知记录"""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with open(NOTIFICATION_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def check_task_status(task_id, task_info, check_date):
    """检查任务在指定日期的状态"""
    log_file = Path(task_info["log_file"])
    
    if not log_file.exists():
        return {"status": "no_log", "time": "-"}
    
    # 获取文件修改时间
    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
    check_date_start = check_date.replace(hour=0, minute=0, second=0, microsecond=0)
    check_date_end = check_date_start + timedelta(days=1)
    
    # 检查是否是指定日期完成的
    if mtime < check_date_start or mtime >= check_date_end:
        return {"status": "not_run", "time": "-"}
    
    # 读取日志最后几行判断状态
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            last_lines = ''.join(lines[-20:]) if lines else ""
        
        if "完成" in last_lines or "success" in last_lines.lower():
            status = "success"
        elif "error" in last_lines.lower() or "失败" in last_lines:
            status = "failed"
        else:
            status = "unknown"
            
        return {
            "status": status,
            "time": mtime.strftime("%H:%M")
        }
        
    except Exception as e:
        return {"status": "error", "time": "-"}

def get_status_emoji(status):
    """获取状态表情"""
    return {
        "success": "✅",
        "failed": "❌",
        "unknown": "⚠️",
        "no_log": "❓",
        "not_run": "⏳",
        "error": "💥"
    }.get(status, "❓")

def check_tasks_group(tasks, check_date):
    """检查一组任务的状态"""
    results = []
    success_count = 0
    failed_count = 0
    
    for task_id, task_info in tasks.items():
        status_info = check_task_status(task_id, task_info, check_date)
        
        if status_info["status"] == "success":
            success_count += 1
        elif status_info["status"] in ["failed", "error"]:
            failed_count += 1
        
        results.append({
            "name": task_info["name"],
            "schedule": task_info["schedule"],
            "emoji": get_status_emoji(status_info["status"]),
            "time": status_info["time"],
            "status": status_info["status"]
        })
    
    return results, success_count, failed_count

def execute_auto_fix(action):
    """执行自动修复"""
    import subprocess
    result = {
        "success": False,
        "message": "",
        "output": ""
    }
    
    try:
        if action == "clean_logs":
            # 清理7天前的日志文件
            cmd = "find /tmp -name '*.log' -mtime +7 -delete"
            subprocess.run(cmd, shell=True, check=True)
            result["success"] = True
            result["message"] = "✅ 已清理7天前的日志文件"
            
        elif action.startswith("pip3 install"):
            # 安装Python模块
            module = action.replace("pip3 install ", "").strip()
            # 先检查是否已安装
            try:
                subprocess.run(["python3", "-c", f"import {module.split('[')[0]}"], 
                             capture_output=True, check=True)
                result["success"] = True
                result["message"] = f"✅ 模块已安装: {module}"
            except subprocess.CalledProcessError:
                # 未安装，尝试安装
                try:
                    subprocess.run(["pip3", "install", module], 
                                 capture_output=True, text=True, check=True)
                    result["success"] = True
                    result["message"] = f"✅ 已安装模块: {module}"
                except subprocess.CalledProcessError as e:
                    result["message"] = f"⚠️ 安装失败，请手动执行: pip3 install {module}"
            
        elif action == "restart_gateway":
            # 重启OpenClaw Gateway
            subprocess.run(["openclaw", "gateway", "restart"], 
                         capture_output=True, text=True)
            result["success"] = True
            result["message"] = "✅ 已重启 Gateway"
            
        elif action == "clear_cache":
            # 清理缓存
            cmd = "rm -rf ~/.openclaw/workspace/memory/cache/*"
            subprocess.run(cmd, shell=True, check=True)
            result["success"] = True
            result["message"] = "✅ 已清理缓存"
            
        else:
            result["message"] = f"⚠️ 未知的修复操作: {action}"
            
    except subprocess.CalledProcessError as e:
        result["message"] = f"❌ 修复失败: {e}"
        result["output"] = e.stderr if hasattr(e, 'stderr') else str(e)
    except Exception as e:
        result["message"] = f"❌ 修复异常: {e}"
    
    return result

def diagnose_task_failure(task_name, log_file):
    """诊断任务失败原因"""
    diagnosis = {
        "reason": "未知",
        "suggestion": "请检查日志文件",
        "auto_fixable": False,
        "action": None
    }
    
    # 检查日志文件
    if not Path(log_file).exists():
        diagnosis["reason"] = "日志文件不存在"
        diagnosis["suggestion"] = "任务可能未执行或日志路径错误"
        return diagnosis
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            log_content = f.read()
        
        # 常见错误模式匹配
        if "No space left" in log_content or "磁盘空间不足" in log_content:
            diagnosis["reason"] = "磁盘空间不足"
            diagnosis["suggestion"] = "清理旧日志文件或扩展磁盘空间"
            diagnosis["auto_fixable"] = True
            diagnosis["action"] = "clean_logs"
            
        elif "ModuleNotFoundError" in log_content or "No module named" in log_content:
            diagnosis["reason"] = "Python模块缺失"
            # 提取模块名
            import re
            match = re.search(r"No module named '([^']+)'", log_content)
            module = match.group(1) if match else "未知"
            diagnosis["suggestion"] = f"安装缺失模块: pip3 install {module}"
            diagnosis["auto_fixable"] = True
            diagnosis["action"] = f"pip3 install {module}"
            
        elif "Permission denied" in log_content:
            diagnosis["reason"] = "权限不足"
            diagnosis["suggestion"] = "检查文件权限或添加执行权限"
            diagnosis["auto_fixable"] = False
            
        elif "Connection" in log_content or "Timeout" in log_content or "timeout" in log_content:
            diagnosis["reason"] = "网络连接超时"
            diagnosis["suggestion"] = "检查网络连接，稍后重试"
            diagnosis["auto_fixable"] = False
            
        elif "Cookie" in log_content or "token" in log_content.lower():
            diagnosis["reason"] = "认证信息过期（Cookie/Token）"
            diagnosis["suggestion"] = "需要更新认证信息，请提供新的Token"
            diagnosis["auto_fixable"] = False
            
        elif "No such file" in log_content or "文件不存在" in log_content:
            diagnosis["reason"] = "依赖文件缺失"
            diagnosis["suggestion"] = "检查脚本依赖的文件路径"
            diagnosis["auto_fixable"] = False
            
        elif "MemoryError" in log_content or "内存" in log_content:
            diagnosis["reason"] = "内存不足"
            diagnosis["suggestion"] = "关闭不必要的程序释放内存"
            diagnosis["auto_fixable"] = False
            
        else:
            # 提取最后几行错误信息
            lines = log_content.split('\n')
            error_lines = [l for l in lines if 'error' in l.lower() or 'Error' in l or 'Exception' in l]
            if error_lines:
                diagnosis["reason"] = "执行异常"
                diagnosis["suggestion"] = f"错误信息: {error_lines[-1][:100]}"
            else:
                diagnosis["reason"] = "执行失败（未知原因）"
                diagnosis["suggestion"] = "请手动检查日志文件详情"
                
    except Exception as e:
        diagnosis["reason"] = f"诊断过程出错: {e}"
        diagnosis["suggestion"] = "请手动检查日志文件"
    
    return diagnosis

def generate_daily_report(check_date=None):
    """生成每日任务汇总报告"""
    if check_date is None:
        check_date = datetime.now() - timedelta(days=1)
    
    date_str = check_date.strftime("%Y-%m-%d")
    weekday = check_date.weekday()  # 0=周一, 6=周日
    is_monthly = check_date.day == 1
    
    all_tasks = []  # 收集所有任务用于失败汇总
    
    # 1. 每日任务（22:00-08:00）
    daily_results, s1, f1 = check_tasks_group(DAILY_TASKS, check_date)
    all_tasks.extend(daily_results)
    
    night_tasks = [t for t in daily_results if DAILY_TASKS.get(next(k for k, v in DAILY_TASKS.items() if v["name"] == t["name"]), {}).get("group") == "night"]
    early_tasks = [t for t in daily_results if DAILY_TASKS.get(next(k for k, v in DAILY_TASKS.items() if v["name"] == t["name"]), {}).get("group") == "early"]
    
    # 2. 周日任务
    sunday_results = []
    if weekday == 6:  # 周日
        sunday_results, s2, f2 = check_tasks_group(SUNDAY_TASKS, check_date)
        all_tasks.extend(sunday_results)
    
    # 3. 周一任务
    monday_results = []
    if weekday == 0:  # 周一
        monday_results, s3, f3 = check_tasks_group(MONDAY_TASKS, check_date)
        all_tasks.extend(monday_results)
    
    # 4. 每月1号任务
    monthly_results = []
    if is_monthly:
        monthly_results, s4, f4 = check_tasks_group(MONTHLY_TASKS, check_date)
        all_tasks.extend(monthly_results)
    
    # 计算统计
    total_success = sum(1 for t in all_tasks if t["status"] == "success")
    total_failed = sum(1 for t in all_tasks if t["status"] in ["failed", "error"])
    total_unknown = sum(1 for t in all_tasks if t["status"] in ["unknown", "no_log", "not_run"])
    total = len(all_tasks)
    
    # 收集失败任务
    failed_tasks = [t for t in all_tasks if t["status"] in ["failed", "error"]]
    
    # 生成报告
    lines = [f"🤖 定时任务日报 ({date_str})\n"]
    
    # 如果有失败任务，置顶显示并诊断
    if failed_tasks:
        lines.append("🚨 失败任务（需要关注）:")
        for task in failed_tasks:
            time_str = f" ({task['time']})" if task["time"] != "-" else ""
            lines.append(f"  ❌ {task['name']} ({task['schedule']}){time_str}")
        
        # 添加诊断信息和自动修复
        lines.append("")
        lines.append("📋 诊断详情:")
        
        auto_fix_results = []
        manual_fix_tasks = []
        
        for task in failed_tasks:
            # 查找任务的日志文件
            log_file = None
            task_info_found = None
            for task_id, task_info in {**DAILY_TASKS, **SUNDAY_TASKS, **MONDAY_TASKS, **MONTHLY_TASKS}.items():
                if task_info["name"] == task["name"]:
                    log_file = task_info.get("log_file")
                    task_info_found = task_info
                    break
            
            if log_file:
                diagnosis = diagnose_task_failure(task["name"], log_file)
                lines.append(f"\n🔍 {task['name']}:")
                lines.append(f"  原因: {diagnosis['reason']}")
                lines.append(f"  建议: {diagnosis['suggestion']}")
                
                if diagnosis['auto_fixable'] and diagnosis['action']:
                    lines.append(f"  🤖 正在自动修复...")
                    # 执行自动修复
                    fix_result = execute_auto_fix(diagnosis['action'])
                    lines.append(f"  {fix_result['message']}")
                    if fix_result['output']:
                        lines.append(f"  输出: {fix_result['output'][:200]}")
                    auto_fix_results.append({
                        "task": task["name"],
                        "result": fix_result
                    })
                else:
                    lines.append(f"  ⚠️ 需要人工处理")
                    manual_fix_tasks.append({
                        "task": task["name"],
                        "diagnosis": diagnosis
                    })
        
        # 修复结果汇总
        if auto_fix_results:
            lines.append("")
            lines.append("🔧 自动修复结果:")
            success_count = sum(1 for r in auto_fix_results if r["result"]["success"])
            lines.append(f"  ✅ 成功: {success_count}/{len(auto_fix_results)}")
            for r in auto_fix_results:
                status = "✅" if r["result"]["success"] else "❌"
                lines.append(f"  {status} {r['task']}: {r['result']['message']}")
        
        if manual_fix_tasks:
            lines.append("")
            lines.append("⚠️ 需要人工处理的任务:")
            for t in manual_fix_tasks:
                lines.append(f"  • {t['task']}: {t['diagnosis']['suggestion']}")
        
        lines.append("")
    
    if night_tasks:
        lines.append("🌙 夜间任务 (22:00-23:59):")
        for task in night_tasks:
            time_str = f" ({task['time']})" if task["time"] != "-" else ""
            lines.append(f"  • {task['name']} ({task['schedule']}): {task['emoji']}{time_str}")
        lines.append("")
    
    if early_tasks:
        lines.append("🌅 凌晨任务 (00:00-08:00):")
        for task in early_tasks:
            time_str = f" ({task['time']})" if task["time"] != "-" else ""
            lines.append(f"  • {task['name']} ({task['schedule']}): {task['emoji']}{time_str}")
        lines.append("")
    
    if sunday_results:
        lines.append("📅 周日任务:")
        for task in sunday_results:
            time_str = f" ({task['time']})" if task["time"] != "-" else ""
            lines.append(f"  • {task['name']}: {task['emoji']}{time_str}")
        lines.append("")
    
    if monday_results:
        lines.append("📅 周一任务:")
        for task in monday_results:
            time_str = f" ({task['time']})" if task["time"] != "-" else ""
            lines.append(f"  • {task['name']}: {task['emoji']}{time_str}")
        lines.append("")
    
    if monthly_results:
        lines.append("📆 月度任务:")
        for task in monthly_results:
            time_str = f" ({task['time']})" if task["time"] != "-" else ""
            lines.append(f"  • {task['name']}: {task['emoji']}{time_str}")
        lines.append("")
    
    # 统计行
    lines.append(f"📊 统计: {total_success}个成功, {total_failed}个失败, {total_unknown}个未运行/未知, 共{total}个任务")
    
    return "\n".join(lines), total_success, total_failed

def check_stock_notifications():
    """检查自选股推送通知文件"""
    import glob
    
    notifications = load_notifications()
    today = datetime.now().strftime("%Y-%m-%d")
    pending_notifications = []
    
    # 查找今日的股票通知文件
    stock_files = glob.glob(STOCK_NOTIFICATION_PATTERN)
    
    for file_path in stock_files:
        file_name = Path(file_path).name
        
        # 检查是否已经发送过
        if file_name in notifications.get("stock_sent", []):
            continue
        
        # 检查文件修改时间是否是今天
        mtime = datetime.fromtimestamp(Path(file_path).stat().st_mtime)
        if mtime.strftime("%Y-%m-%d") != today:
            continue
        
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content.strip():
                pending_notifications.append({
                    "task_id": "stock_push",
                    "task_name": "自选股收盘推送",
                    "message": content,
                    "notification_key": file_name
                })
                
                # 标记为已通知
                if "stock_sent" not in notifications:
                    notifications["stock_sent"] = []
                notifications["stock_sent"].append(file_name)
                
        except Exception as e:
            print(f"读取股票通知文件失败: {e}")
    
    save_notifications(notifications)
    return pending_notifications

def check_other_tasks():
    """检查其他时段任务，返回需要通知的列表"""
    notifications = load_notifications()
    today = datetime.now().strftime("%Y-%m-%d")
    current_hour = datetime.now().hour
    pending_notifications = []
    
    for task_id, task_info in OTHER_TASKS.items():
        notify_hour = int(task_info["notify_time"].split(":")[0])
        notification_key = f"{today}_{task_id}"
        
        # 检查是否到通知时间且未通知
        if current_hour >= notify_hour and notification_key not in notifications:
            # 检查任务状态
            check_date = datetime.now()
            status_info = check_task_status(task_id, task_info, check_date)
            
            if status_info["status"] != "not_run":  # 任务已执行
                emoji = get_status_emoji(status_info["status"])
                message = f"""🤖 {task_info['name']} 完成

📅 日期: {today}
⏰ 时间: {status_info['time']}

状态: {emoji} {"成功" if status_info['status'] == 'success' else status_info['status']}"""
                
                pending_notifications.append({
                    "task_id": task_id,
                    "task_name": task_info["name"],
                    "message": message,
                    "notification_key": notification_key
                })
                
                # 标记为已通知
                notifications[notification_key] = {
                    "time": datetime.now().isoformat(),
                    "status": status_info["status"]
                }
    
    save_notifications(notifications)
    return pending_notifications

def check_daily_report():
    """检查是否应该发送每日任务汇总"""
    notifications = load_notifications()
    today = datetime.now().strftime("%Y-%m-%d")
    current_hour = datetime.now().hour
    
    # 早上8点到9点之间
    if not (8 <= current_hour < 9):
        return None, "不是汇报时间（8:00-9:00）"
    
    daily_key = f"daily_report_{today}"
    if daily_key in notifications:
        return None, "今日任务日报已发送"
    
    # 生成任务汇总
    message, success, failed = generate_daily_report()
    
    # 标记为已通知
    notifications[daily_key] = {
        "time": datetime.now().isoformat(),
        "success_count": success,
        "failed_count": failed
    }
    save_notifications(notifications)
    
    return message, None

def check_all_tasks():
    """检查所有任务，返回需要发送的通知列表"""
    notifications_to_send = []
    
    # 1. 检查每日任务汇总（8:00-9:00）
    daily_message, error = check_daily_report()
    if daily_message:
        notifications_to_send.append({
            "type": "daily_summary",
            "title": "定时任务日报",
            "message": daily_message
        })
    
    # 2. 检查自选股推送（随时）
    stock_notifications = check_stock_notifications()
    for notif in stock_notifications:
        notifications_to_send.append({
            "type": "stock",
            "title": notif["task_name"],
            "message": notif["message"]
        })
    
    # 3. 检查其他时段任务
    other_notifications = check_other_tasks()
    for notif in other_notifications:
        notifications_to_send.append({
            "type": "single",
            "title": notif["task_name"],
            "message": notif["message"]
        })
    
    return notifications_to_send

if __name__ == "__main__":
    # 测试模式
    notifications = check_all_tasks()
    if notifications:
        print(f"发现 {len(notifications)} 条待发送通知:\n")
        for n in notifications:
            print(f"--- {n['title']} ---")
            print(n['message'])
            print()
    else:
        print("没有新的通知需要发送")
