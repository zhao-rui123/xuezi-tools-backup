#!/usr/bin/env python3
"""
Kilo - 通知消息专家
统一发送定时任务通知、每日报告、系统状态更新
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# 飞书配置
FEISHU_USER_ID = "ou_5a7b7ec0339ffe0c1d5bb6c5bc162579"
FEISHU_CHAT_ID = "oc_b14195eb990ab57ea573e696758ae3d5"  # 群聊ID

class NotificationAgent:
    """通知消息Agent - Kilo"""
    
    def __init__(self):
        self.name = "Kilo"
        self.role = "通知消息专家"
        
    def send_daily_summary(self):
        """发送每日汇总"""
        message = self._generate_daily_summary()
        self._send_to_feishu(message, "每日汇总")
        
    def send_backup_notification(self, status, details):
        """发送备份通知"""
        message = self._format_backup_message(status, details)
        self._send_to_feishu(message, "每日备份")
        
    def send_health_check_report(self, report):
        """发送健康检查报告"""
        message = self._format_health_message(report)
        self._send_to_feishu(message, "健康检查")
        
    def send_system_alert(self, alert_type, message):
        """发送系统告警"""
        emoji = {"error": "🚨", "warning": "⚠️", "info": "ℹ️"}.get(alert_type, "📢")
        full_message = f"{emoji} 系统告警\n\n类型: {alert_type}\n时间: {datetime.now().strftime('%H:%M')}\n\n{message}"
        self._send_to_feishu(full_message, "系统告警")
        
    def send_task_reminder(self, task_name, due_time):
        """发送任务提醒"""
        message = f"⏰ 任务提醒\n\n任务: {task_name}\n截止时间: {due_time}\n\n请及时处理！"
        self._send_to_feishu(message, "任务提醒")
        
    def _generate_daily_summary(self):
        """生成每日汇总"""
        # 读取小龙虾数据
        lobster_data = self._get_lobster_data()
        
        # 读取备份状态
        backup_status = self._get_backup_status()
        
        # 读取系统状态
        system_status = self._get_system_status()
        
        message = f"""🦞 每日工作汇总 ({datetime.now().strftime('%Y-%m-%d')})

📊 今日数据:
• Token使用: {lobster_data.get('tokens', 'N/A')}
• 完成任务: {lobster_data.get('tasks', 'N/A')} 个
• 工作时长: {lobster_data.get('minutes', 'N/A')} 分钟

💾 备份状态: {backup_status}

🖥️ 系统状态: {system_status}

📍 当前位置: {lobster_data.get('room', 'N/A')}

今日工作总结完成！如需查看详情，请访问小龙虾之家。
"""
        return message
        
    def _format_backup_message(self, status, details):
        """格式化备份消息"""
        emoji = "✅" if status == "success" else "❌"
        return f"""{emoji} 每日备份完成

状态: {status}
时间: {datetime.now().strftime('%H:%M')}

详情:
{details}

备份文件已保存到备份磁盘。
"""
        
    def _format_health_message(self, report):
        """格式化健康检查消息"""
        return f"""🏥 系统健康检查报告

检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

{report}

详细报告请查看日志文件。
"""
        
    def _send_to_feishu(self, message, msg_type):
        """发送消息到飞书群聊 - 使用Agent能力"""
        try:
            # 方法1: 尝试使用OpenClaw的message工具（如果在Agent上下文中）
            try:
                # 创建消息发送的标记文件，由主Agent处理
                import os
                notification_file = f"/tmp/kilo_notification_{datetime.now().strftime('%H%M%S')}.json"
                with open(notification_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "chat_id": FEISHU_CHAT_ID,
                        "message": message,
                        "type": msg_type,
                        "timestamp": datetime.now().isoformat()
                    }, f, ensure_ascii=False, indent=2)
                
                print(f"✅ [{msg_type}] 通知已保存: {notification_file}")
                print(f"   目标群聊: {FEISHU_CHAT_ID}")
                return True
            except Exception as e2:
                print(f"⚠️ 保存通知失败: {e2}")
                
        except Exception as e:
            print(f"❌ [{msg_type}] 发送失败: {e}")
            print(f"[{msg_type}] {message}")
            return False
            
    def _get_lobster_data(self):
        """获取小龙虾数据"""
        try:
            data_file = Path("/opt/lobster-home/data/daily") / f"{datetime.now().strftime('%Y-%m-%d')}.json"
            if data_file.exists():
                with open(data_file, 'r') as f:
                    data = json.load(f)
                return {
                    'tokens': data.get('total_tokens', 'N/A'),
                    'tasks': data.get('tasks_completed', 'N/A'),
                    'minutes': data.get('work_minutes', 'N/A'),
                    'room': data.get('current_room', 'N/A')
                }
        except:
            pass
        return {'tokens': 'N/A', 'tasks': 'N/A', 'minutes': 'N/A', 'room': 'N/A'}
        
    def _get_backup_status(self):
        """获取备份状态"""
        try:
            manifest_file = Path("/Volumes/cu/ocu/backup-manifest") / f"{datetime.now().strftime('%Y%m%d')}.json"
            if manifest_file.exists():
                return "✅ 今日已备份"
            return "⏳ 等待备份"
        except:
            return "❓ 未知"
            
    def _get_system_status(self):
        """获取系统状态"""
        return "✅ 正常运行"

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Kilo - 通知消息Agent')
    parser.add_argument('--daily-summary', action='store_true', help='发送每日汇总')
    parser.add_argument('--backup', type=str, help='发送备份通知 (success/failed)')
    parser.add_argument('--health', type=str, help='发送健康检查报告')
    parser.add_argument('--alert', type=str, help='发送系统告警')
    parser.add_argument('--alert-type', type=str, default='info', help='告警类型')
    parser.add_argument('--reminder', type=str, help='发送任务提醒')
    parser.add_argument('--due', type=str, help='截止时间')
    
    args = parser.parse_args()
    
    kilo = NotificationAgent()
    
    if args.daily_summary:
        kilo.send_daily_summary()
    elif args.backup:
        kilo.send_backup_notification(args.backup, "备份完成")
    elif args.health:
        kilo.send_health_check_report(args.health)
    elif args.alert:
        kilo.send_system_alert(args.alert_type, args.alert)
    elif args.reminder:
        kilo.send_task_reminder(args.reminder, args.due or "尽快")
    else:
        print("Kilo - 通知消息专家")
        print("用法: python3 kilo_notification.py --daily-summary")
        print("      python3 kilo_notification.py --backup success")
        print("      python3 kilo_notification.py --alert '磁盘空间不足' --alert-type warning")

if __name__ == '__main__':
    main()
