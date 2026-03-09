#!/usr/bin/env python3
"""
系统监控告警系统 (Monitoring Alert System)
功能：监控定时任务、磁盘空间、备份状态，异常时推送告警
"""

import os
import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# 配置
ALERT_LOG = Path("~/.openclaw/workspace/logs/alert_system.log").expanduser()
ALERT_STATE_FILE = Path("~/.openclaw/workspace/logs/alert_state.json").expanduser()
FEISHU_USER = "ou_5a7b7ec0339ffe0c1d5bb6c5bc162579"  # 你的飞书用户ID

# 告警阈值
THRESHOLDS = {
    'disk_usage': 85,  # 磁盘使用率超过85%告警
    'backup_delay': 2,  # 备份延迟超过2天告警
}

class MonitoringAlertSystem:
    """监控告警系统"""
    
    def __init__(self):
        self.alerts = []
        self.state = self.load_state()
        ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    def load_state(self) -> Dict:
        """加载告警状态"""
        if ALERT_STATE_FILE.exists():
            with open(ALERT_STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'last_alerts': {}, 'silence_until': {}}
    
    def save_state(self):
        """保存告警状态"""
        with open(ALERT_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
    
    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        with open(ALERT_LOG, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        print(log_entry.strip())
    
    def check_disk_space(self):
        """检查磁盘空间"""
        self.log("🔍 检查磁盘空间...")
        
        # 检查主磁盘
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        
        for line in lines[1:]:  # 跳过标题行
            parts = line.split()
            if len(parts) >= 5:
                filesystem = parts[0]
                usage_str = parts[4]
                mount = parts[5] if len(parts) > 5 else '/'
                
                # 解析使用率
                usage_match = re.search(r'(\d+)%', usage_str)
                if usage_match:
                    usage = int(usage_match.group(1))
                    
                    if usage > THRESHOLDS['disk_usage']:
                        alert = {
                            'type': 'disk_space',
                            'severity': 'warning' if usage < 90 else 'critical',
                            'message': f'磁盘空间不足: {mount} 使用率 {usage}%',
                            'timestamp': datetime.now().isoformat()
                        }
                        self.alerts.append(alert)
                        self.log(f"⚠️ 磁盘告警: {mount} {usage}%")
    
    def check_cron_jobs(self):
        """检查定时任务状态"""
        self.log("🔍 检查定时任务状态...")
        
        # 检查关键日志文件
        log_files = [
            ('/tmp/unified-memory-cron.log', '统一记忆系统'),
            ('/tmp/daily-health.log', '每日健康检查'),
            ('/tmp/system-maintenance.log', '系统维护'),
        ]
        
        for log_file, job_name in log_files:
            if os.path.exists(log_file):
                # 检查最后更新时间
                mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                hours_since = (datetime.now() - mtime).total_seconds() / 3600
                
                # 超过25小时未更新（说明今天没运行）
                if hours_since > 25:
                    alert = {
                        'type': 'cron_job',
                        'severity': 'warning',
                        'message': f'{job_name} 可能未正常运行（{hours_since:.0f}小时未更新）',
                        'timestamp': datetime.now().isoformat()
                    }
                    self.alerts.append(alert)
                    self.log(f"⚠️ 定时任务告警: {job_name}")
    
    def check_backup_status(self):
        """检查备份状态"""
        self.log("🔍 检查备份状态...")
        
        # 检查记忆备份
        memory_backup_dir = Path("/Volumes/cu/ocu/memory")
        if memory_backup_dir.exists():
            latest_backup = None
            latest_time = None
            
            for file in memory_backup_dir.glob("*.md"):
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                if latest_time is None or mtime > latest_time:
                    latest_time = mtime
                    latest_backup = file
            
            if latest_time:
                days_since = (datetime.now() - latest_time).days
                if days_since > THRESHOLDS['backup_delay']:
                    alert = {
                        'type': 'backup',
                        'severity': 'warning',
                        'message': f'记忆备份延迟: {days_since}天未更新',
                        'timestamp': datetime.now().isoformat()
                    }
                    self.alerts.append(alert)
                    self.log(f"⚠️ 备份告警: {days_since}天未更新")
    
    def should_alert(self, alert_type: str, cooldown_hours: int = 24) -> bool:
        """检查是否应该发送告警（避免重复告警）"""
        last_alert = self.state['last_alerts'].get(alert_type)
        if last_alert:
            last_time = datetime.fromisoformat(last_alert)
            hours_since = (datetime.now() - last_time).total_seconds() / 3600
            if hours_since < cooldown_hours:
                return False
        return True
    
    def send_alert(self, alert: Dict):
        """发送告警通知"""
        severity_emoji = {
            'critical': '🔴',
            'warning': '🟡',
            'info': '🔵'
        }.get(alert['severity'], '⚪')
        
        message = f"""{severity_emoji} 系统告警

**类型**: {alert['type']}
**级别**: {alert['severity']}
**时间**: {alert['timestamp']}

**详情**:
{alert['message']}

---
*由监控告警系统发送*
"""
        
        # 这里调用飞书发送
        try:
            # 使用 OpenClaw 的消息工具发送
            import subprocess
            cmd = f'openclaw message send --channel feishu --target "user:{FEISHU_USER}" --message "{message[:500]}"'
            subprocess.run(cmd, shell=True, capture_output=True)
            self.log(f"📤 告警已发送: {alert['type']}")
        except Exception as e:
            self.log(f"❌ 发送告警失败: {e}")
    
    def run_checks(self):
        """运行所有检查"""
        self.log("=" * 60)
        self.log("🔍 开始系统监控检查")
        self.log("=" * 60)
        
        self.alerts = []
        
        # 执行检查
        self.check_disk_space()
        self.check_cron_jobs()
        self.check_backup_status()
        
        # 处理告警
        if self.alerts:
            self.log(f"\n⚠️ 发现 {len(self.alerts)} 个告警")
            
            for alert in self.alerts:
                if self.should_alert(alert['type']):
                    self.send_alert(alert)
                    self.state['last_alerts'][alert['type']] = datetime.now().isoformat()
                else:
                    self.log(f"   ⏸️  {alert['type']} 告警冷却中，跳过")
        else:
            self.log("\n✅ 系统状态正常")
        
        self.save_state()
        
        self.log("=" * 60)
        self.log("✅ 监控检查完成")
        self.log("=" * 60)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='系统监控告警系统')
    parser.add_argument('--run', action='store_true', help='立即运行检查')
    parser.add_argument('--status', action='store_true', help='查看状态')
    
    args = parser.parse_args()
    
    system = MonitoringAlertSystem()
    
    if args.run:
        system.run_checks()
    elif args.status:
        print("📊 监控告警系统状态")
        print(f"日志文件: {ALERT_LOG}")
        print(f"状态文件: {ALERT_STATE_FILE}")
        if ALERT_STATE_FILE.exists():
            with open(ALERT_STATE_FILE, 'r') as f:
                state = json.load(f)
                print(f"上次告警: {state.get('last_alerts', {})}")
    else:
        system.run_checks()

if __name__ == '__main__':
    main()
