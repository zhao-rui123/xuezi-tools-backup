#!/usr/bin/env python3
"""
Kilo - 通知消息专家 v2.0 (稳定版)
统一发送定时任务通知、每日报告、系统状态更新
支持飞书、Slack、Email等多种通知渠道

版本历史:
  - v1.0: 基础飞书通知
  - v2.0: 多渠道支持 (飞书/Slack/Email/控制台)
  - v3.0: 混合模式 (高优先级人工审核)

注意: 旧版本 (v1, v3) 请参考 kilo_v2.py 和 kilo_v3.py
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

SUITE_DIR = Path("~/.openclaw/workspace/skills/multi-agent-suite").expanduser()

class NotificationConfig:
    """通知配置"""
    
    def __init__(self):
        self.config_file = SUITE_DIR / "notification_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return self._default_config()
    
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            "feishu": {
                "enabled": True,
                "user_id": "ou_5a7b7ec0339ffe0c1d5bb6c5bc162579",
                "chat_id": "oc_b14195eb990ab57ea573e696758ae3d5"
            },
            "slack": {
                "enabled": False,
                "webhook_url": ""
            },
            "email": {
                "enabled": False,
                "smtp_server": "",
                "smtp_port": 587,
                "recipients": []
            },
            "console": {
                "enabled": True
            }
        }
    
    def save(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        self.config[key] = value
        self.save()


class NotificationAgent:
    """通知消息Agent - Kilo v2.0"""
    
    def __init__(self):
        self.name = "Kilo"
        self.role = "通知消息专家"
        self.config = NotificationConfig()
    
    def send_to_channels(self, message: str, msg_type: str) -> Dict[str, bool]:
        """发送消息到所有启用的渠道"""
        results = {}
        
        if self.config.get('console', {}).get('enabled', True):
            results['console'] = self._send_to_console(message, msg_type)
        
        if self.config.get('feishu', {}).get('enabled', True):
            results['feishu'] = self._send_to_feishu(message, msg_type)
        
        if self.config.get('slack', {}).get('enabled', False):
            results['slack'] = self._send_to_slack(message, msg_type)
        
        if self.config.get('email', {}).get('enabled', False):
            results['email'] = self._send_to_email(message, msg_type)
        
        return results
    
    def send_daily_summary(self) -> bool:
        """发送每日汇总"""
        message = self._generate_daily_summary()
        results = self.send_to_channels(message, "每日汇总")
        return any(results.values())
    
    def send_backup_notification(self, status: str, details: str) -> bool:
        """发送备份通知"""
        message = self._format_backup_message(status, details)
        results = self.send_to_channels(message, "备份通知")
        return any(results.values())
    
    def send_health_check_report(self, report: str) -> bool:
        """发送健康检查报告"""
        message = self._format_health_message(report)
        results = self.send_to_channels(message, "健康检查")
        return any(results.values())
    
    def send_system_alert(self, alert_type: str, message: str) -> bool:
        """发送系统告警"""
        emoji = {"error": "🚨", "warning": "⚠️", "info": "ℹ️", "success": "✅"}.get(alert_type, "📢")
        full_message = f"{emoji} 系统告警\n\n类型: {alert_type}\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{message}"
        results = self.send_to_channels(full_message, "系统告警")
        return any(results.values())
    
    def send_task_reminder(self, task_name: str, due_time: str, description: str = "") -> bool:
        """发送任务提醒"""
        message = f"⏰ 任务提醒\n\n任务: {task_name}\n截止时间: {due_time}\n" + (f"描述: {description}\n" if description else "") + "\n请及时处理！"
        results = self.send_to_channels(message, "任务提醒")
        return any(results.values())
    
    def send_custom_message(self, message: str, msg_type: str = "通知") -> bool:
        """发送自定义消息"""
        results = self.send_to_channels(message, msg_type)
        return any(results.values())
    
    def _send_to_console(self, message: str, msg_type: str) -> bool:
        """发送消息到控制台"""
        print(f"\n{'='*50}")
        print(f"📢 [{msg_type}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        print(message)
        print(f"{'='*50}\n")
        return True
    
    def _send_to_feishu(self, message: str, msg_type: str) -> bool:
        """发送消息到飞书"""
        try:
            feishu_config = self.config.get('feishu', {})
            chat_id = feishu_config.get('chat_id', '')
            
            notification_file = SUITE_DIR / f"tmp" / f"kilo_notification_{datetime.now().strftime('%H%M%S')}.json"
            notification_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(notification_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "chat_id": chat_id,
                    "message": message,
                    "type": msg_type,
                    "timestamp": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            print(f"✅ [{msg_type}] 飞书通知已保存: {notification_file}")
            return True
        except Exception as e:
            print(f"❌ 飞书通知失败: {e}")
            return False
    
    def _send_to_slack(self, message: str, msg_type: str) -> bool:
        """发送消息到Slack"""
        try:
            import requests
            webhook_url = self.config.get('slack', {}).get('webhook_url', '')
            if not webhook_url:
                return False
            
            payload = {"text": f"*{msg_type}*\n{message}"}
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Slack通知失败: {e}")
            return False
    
    def _send_to_email(self, message: str, msg_type: str) -> bool:
        """发送邮件"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            email_config = self.config.get('email', {})
            smtp_server = email_config.get('smtp_server', '')
            smtp_port = email_config.get('smtp_port', 587)
            recipients = email_config.get('recipients', [])
            
            if not smtp_server or not recipients:
                return False
            
            msg = MIMEText(message, 'plain', 'utf-8')
            msg['Subject'] = f"[Kilo] {msg_type}"
            msg['From'] = 'Kilo Notification <noreply@example.com>'
            msg['To'] = ', '.join(recipients)
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.send_message(msg)
            
            print(f"✅ 邮件已发送到: {recipients}")
            return True
        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")
            return False
    
    def _generate_daily_summary(self) -> str:
        """生成每日汇总"""
        lobster_data = self._get_lobster_data()
        backup_status = self._get_backup_status()
        system_status = self._get_system_status()
        
        return f"""🦞 每日工作汇总 ({datetime.now().strftime('%Y-%m-%d')})

📊 今日数据:
• Token使用: {lobster_data.get('tokens', 'N/A')}
• 完成任务: {lobster_data.get('tasks', 'N/A')} 个
• 工作时长: {lobster_data.get('minutes', 'N/A')} 分钟

💾 备份状态: {backup_status}

🖥️ 系统状态: {system_status}

📍 当前位置: {lobster_data.get('room', 'N/A')}

今日工作总结完成！
"""
    
    def _format_backup_message(self, status: str, details: str) -> str:
        """格式化备份消息"""
        emoji = "✅" if status == "success" else "❌"
        return f"""{emoji} 每日备份

状态: {status}
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

详情:
{details}
"""
    
    def _format_health_message(self, report: str) -> str:
        """格式化健康检查消息"""
        return f"""🏥 系统健康检查报告

检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{report}

详情请查看日志文件。
"""
    
    def _get_lobster_data(self) -> Dict:
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
    
    def _get_backup_status(self) -> str:
        """获取备份状态"""
        try:
            manifest_file = Path("/Volumes/cu/ocu/backup-manifest") / f"{datetime.now().strftime('%Y%m%d')}.json"
            if manifest_file.exists():
                return "✅ 今日已备份"
            return "⏳ 等待备份"
        except:
            return "❓ 未知"
    
    def _get_system_status(self) -> str:
        """获取系统状态"""
        return "✅ 正常运行"
    
    def configure(self, channel: str, **kwargs):
        """配置通知渠道"""
        if channel in self.config.config:
            self.config.config[channel].update(kwargs)
            self.config.save()
            print(f"✅ {channel} 配置已更新")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Kilo - 通知消息Agent v2.0')
    parser.add_argument('--daily-summary', action='store_true', help='发送每日汇总')
    parser.add_argument('--backup', type=str, help='发送备份通知 (success/failed)')
    parser.add_argument('--details', type=str, default='', help='备份详情')
    parser.add_argument('--health', type=str, help='发送健康检查报告')
    parser.add_argument('--alert', type=str, help='发送系统告警')
    parser.add_argument('--alert-type', type=str, default='info', choices=['info', 'warning', 'error', 'success'], help='告警类型')
    parser.add_argument('--reminder', type=str, help='发送任务提醒')
    parser.add_argument('--due', type=str, help='截止时间')
    parser.add_argument('--desc', type=str, default='', help='任务描述')
    parser.add_argument('--message', type=str, help='发送自定义消息')
    parser.add_argument('--type', type=str, default='通知', help='消息类型')
    parser.add_argument('--config', action='store_true', help='配置通知渠道')
    parser.add_argument('--channel', type=str, help='渠道名称')
    
    args = parser.parse_args()
    
    kilo = NotificationAgent()
    
    if args.daily_summary:
        kilo.send_daily_summary()
    elif args.backup:
        kilo.send_backup_notification(args.backup, args.details)
    elif args.health:
        kilo.send_health_check_report(args.health)
    elif args.alert:
        kilo.send_system_alert(args.alert_type, args.alert)
    elif args.reminder:
        kilo.send_task_reminder(args.reminder, args.due or "尽快", args.desc)
    elif args.message:
        kilo.send_custom_message(args.message, args.type)
    elif args.config:
        print("当前配置:")
        print(json.dumps(kilo.config.config, ensure_ascii=False, indent=2))
    else:
        print("""
Kilo - 通知消息专家 v2.0
=========================

用法:
  python3 kilo_notification.py --daily-summary          # 发送每日汇总
  python3 kilo_notification.py --backup success --details "备份62个文件"
  python3 kilo_notification.py --health "CPU: 45%, 内存: 60%"
  python3 kilo_notification.py --alert "磁盘空间不足" --alert-type warning
  python3 kilo_notification.py --reminder "检查代码" --due "22:00"
  python3 kilo_notification.py --message "自定义消息" --type "通知"
  python3 kilo_notification.py --config                # 查看配置
        """)

if __name__ == '__main__':
    main()
