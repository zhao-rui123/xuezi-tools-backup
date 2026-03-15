#!/usr/bin/env python3
"""
Memory Suite v3.0 - 通知系统模块
负责发送各类通知到飞书
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path


class Notifier:
    """通知系统"""
    
    def __init__(self, config_path=None):
        self.workspace = Path.home() / ".openclaw" / "workspace"
        self.config_path = config_path or self.workspace / "skills" / "memory-suite-v3" / "config" / "config.json"
        self.config = self._load_config()
        
    def _load_config(self):
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"notifications": {"enabled": True}}
    
    def notify(self, title, message, level="info"):
        """发送通知"""
        if not self.config.get("notifications", {}).get("enabled", True):
            print(f"[通知已禁用] {title}: {message}")
            return False
            
        timestamp = datetime.now().strftime("%H:%M")
        
        # 构建通知内容
        notification = f"""
🤖 Memory Suite 通知

⏰ {timestamp}
📌 {title}

{message}
"""
        
        # 尝试使用 feishu_notify.sh
        notify_script = self.workspace / "scripts" / "feishu_notify.sh"
        if notify_script.exists():
            try:
                subprocess.run([
                    str(notify_script),
                    title,
                    message,
                    level
                ], check=True, capture_output=True)
                print(f"✅ 通知已发送: {title}")
                return True
            except Exception as e:
                print(f"⚠️ 通知发送失败: {e}")
        
        # 备用：仅打印
        print(notification)
        return True
    
    def notify_archive(self, count):
        """归档完成通知"""
        if self.config.get("notifications", {}).get("on_archive", True):
            self.notify(
                "📦 记忆归档完成",
                f"已归档 {count} 个记忆文件",
                "normal"
            )
    
    def notify_error(self, error_msg):
        """错误通知"""
        if self.config.get("notifications", {}).get("on_error", True):
            self.notify(
                "❌ Memory Suite 错误",
                error_msg,
                "urgent"
            )
    
    def notify_backup(self, status):
        """备份通知"""
        if self.config.get("notifications", {}).get("on_backup", False):
            self.notify(
                "💾 备份状态",
                status,
                "normal"
            )


if __name__ == "__main__":
    # 测试
    n = Notifier()
    n.notify("测试通知", "这是一条测试消息")
