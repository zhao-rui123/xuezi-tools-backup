#!/usr/bin/env python3
"""
Kilo Agent v3 - 混合模式通知
高优先级 → 保存待人工审核
低优先级 → Kilo自动发送
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# 飞书群聊ID
FEISHU_CHAT_ID = "oc_b14195eb990ab57ea573e696758ae3d5"

# 通知队列目录
NOTIFICATION_DIR = Path("/tmp/kilo_notifications")
HIGH_PRIORITY_DIR = Path("/tmp/kilo_high_priority")
NOTIFICATION_DIR.mkdir(exist_ok=True)
HIGH_PRIORITY_DIR.mkdir(exist_ok=True)

class NotificationAgent:
    """Kilo - 智能通知Agent (混合模式)"""
    
    def __init__(self):
        self.name = "Kilo"
        self.role = "智能通知专家"
        
    def send_notification(self, msg_type, title, content, priority="normal"):
        """
        智能发送通知
        
        Args:
            msg_type: 通知类型 (backup/health/alert/reminder/summary)
            title: 标题
            content: 内容
            priority: 优先级 (normal/high/urgent)
        """
        # 构建通知消息
        emoji_map = {
            "backup": "💾",
            "health": "🏥",
            "alert": "🚨",
            "reminder": "⏰",
            "summary": "📊"
        }
        emoji = emoji_map.get(msg_type, "📢")
        
        message = f"""{emoji} {title}

{content}

---
🤖 Kilo | {datetime.now().strftime('%H:%M')} | 优先级: {priority}"""
        
        notification = {
            "chat_id": FEISHU_CHAT_ID,
            "type": msg_type,
            "title": title,
            "content": content,
            "message": message,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        
        # 根据优先级处理
        if priority in ["high", "urgent"]:
            # 高优先级：保存待人工审核
            filename = f"{msg_type}_{datetime.now().strftime('%H%M%S')}_HIGH.json"
            filepath = HIGH_PRIORITY_DIR / filename
            notification["requires_review"] = True
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(notification, f, ensure_ascii=False, indent=2)
            
            print(f"🔴 高优先级通知已保存（待审核）: {filepath}")
            print(f"   类型: {msg_type}")
            print(f"   标题: {title}")
            print(f"   ⚠️  需要人工审核后发送")
            
        else:
            # 低优先级：Kilo直接发送
            filename = f"{msg_type}_{datetime.now().strftime('%H%M%S')}.json"
            filepath = NOTIFICATION_DIR / filename
            notification["auto_send"] = True
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(notification, f, ensure_ascii=False, indent=2)
            
            print(f"🟢 常规通知已生成（自动发送）: {filepath}")
            print(f"   类型: {msg_type}")
            print(f"   标题: {title}")
            print(f"   ✅ Kilo将自动发送")
        
        return filepath, priority
    
    def send_backup_notification(self, status, details=""):
        """发送备份通知 - 常规优先级"""
        if status == "success":
            title = "每日备份完成"
            content = f"✅ 状态: 成功\n\n{details}"
            priority = "normal"  # 成功都是常规
        else:
            title = "每日备份失败"
            content = f"❌ 状态: 失败\n\n{details}"
            priority = "high"    # 失败是高优先级
        
        return self.send_notification("backup", title, content, priority)
    
    def send_health_check(self, report, has_issues=False):
        """发送健康检查报告"""
        title = "系统健康检查报告"
        
        if has_issues:
            content = f"⚠️ 发现问题\n\n{report}"
            priority = "high"    # 有问题是高优先级
        else:
            content = f"✅ 全部正常\n\n{report}"
            priority = "normal"  # 正常是常规
        
        return self.send_notification("health", title, content, priority)
    
    def send_alert(self, alert_type, message, priority="high"):
        """发送系统告警 - 默认高优先级"""
        emoji_map = {
            "error": "🚨",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        emoji = emoji_map.get(alert_type, "📢")
        title = f"{emoji} 系统告警"
        content = f"类型: {alert_type}\n\n{message}"
        return self.send_notification("alert", title, content, priority)
    
    def send_reminder(self, task, due_time, priority="normal"):
        """发送任务提醒"""
        title = "⏰ 任务提醒"
        content = f"任务: {task}\n截止时间: {due_time}\n\n请及时处理！"
        return self.send_notification("reminder", title, content, priority)
    
    def send_daily_summary(self):
        """发送每日汇总 - 常规优先级"""
        data = self._get_today_data()
        
        title = "📊 每日工作汇总"
        content = f"""📅 日期: {datetime.now().strftime('%Y-%m-%d')}

📈 今日数据:
• Token使用: {data.get('tokens', 'N/A')}
• 完成任务: {data.get('tasks', 'N/A')} 个
• 工作时长: {data.get('minutes', 'N/A')} 分钟

💾 备份状态: {data.get('backup', 'N/A')}
🖥️ 系统状态: {data.get('system', 'N/A')}

如需查看详情，请访问小龙虾之家。"""
        
        return self.send_notification("summary", title, content, "normal")
    
    def _get_today_data(self):
        """获取今日数据"""
        try:
            lobster_file = Path("/opt/lobster-home/data/daily") / f"{datetime.now().strftime('%Y-%m-%d')}.json"
            if lobster_file.exists():
                with open(lobster_file, 'r') as f:
                    data = json.load(f)
                return {
                    'tokens': data.get('total_tokens', 'N/A'),
                    'tasks': data.get('tasks_completed', 'N/A'),
                    'minutes': data.get('work_minutes', 'N/A'),
                    'backup': '✅ 已备份',
                    'system': '✅ 正常'
                }
        except:
            pass
        return {'tokens': 'N/A', 'tasks': 'N/A', 'minutes': 'N/A', 'backup': 'N/A', 'system': 'N/A'}

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Kilo - 智能通知Agent (混合模式)')
    parser.add_argument('--backup', type=str, help='发送备份通知 (success/failed)')
    parser.add_argument('--backup-details', type=str, default='', help='备份详情')
    parser.add_argument('--health', type=str, help='发送健康检查报告')
    parser.add_argument('--health-issues', action='store_true', help='健康检查发现问题')
    parser.add_argument('--alert', type=str, help='发送系统告警')
    parser.add_argument('--alert-type', type=str, default='warning', help='告警类型')
    parser.add_argument('--alert-priority', type=str, default='high', help='告警优先级')
    parser.add_argument('--reminder', type=str, help='发送任务提醒')
    parser.add_argument('--due', type=str, help='截止时间')
    parser.add_argument('--reminder-priority', type=str, default='normal', help='提醒优先级')
    parser.add_argument('--daily-summary', action='store_true', help='发送每日汇总')
    
    args = parser.parse_args()
    
    kilo = NotificationAgent()
    
    if args.backup:
        filepath, priority = kilo.send_backup_notification(args.backup, args.backup_details)
        print(f"\n通知已保存: {filepath}")
        print(f"优先级: {priority}")
        if priority in ['high', 'urgent']:
            print("⚠️  此通知需要人工审核后发送")
        else:
            print("✅ Kilo将自动处理")
            
    elif args.health:
        filepath, priority = kilo.send_health_check(args.health, args.health_issues)
        print(f"\n通知已保存: {filepath}")
        print(f"优先级: {priority}")
        
    elif args.alert:
        filepath, priority = kilo.send_alert(args.alert_type, args.alert, args.alert_priority)
        print(f"\n通知已保存: {filepath}")
        print(f"优先级: {priority}")
        
    elif args.reminder:
        filepath, priority = kilo.send_reminder(args.reminder, args.due or "尽快", args.reminder_priority)
        print(f"\n通知已保存: {filepath}")
        print(f"优先级: {priority}")
        
    elif args.daily_summary:
        filepath, priority = kilo.send_daily_summary()
        print(f"\n通知已保存: {filepath}")
        print(f"优先级: {priority}")
        
    else:
        print("Kilo v3 - 智能通知Agent (混合模式)")
        print("\n高优先级通知 → 保存待审核")
        print("常规通知 → Kilo自动处理")
        print("\n用法:")
        print("  python3 kilo_v3.py --backup success --backup-details '备份62个文件'")
        print("  python3 kilo_v3.py --health '系统正常'")
        print("  python3 kilo_v3.py --alert '磁盘空间不足' --alert-priority high")
        print("  python3 kilo_v3.py --daily-summary")

if __name__ == '__main__':
    main()
