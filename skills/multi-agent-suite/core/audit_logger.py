"""
审计日志系统
记录所有操作和系统事件
"""

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict
import uuid

SUITE_DIR = Path("~/.openclaw/workspace/skills/multi-agent-suite").expanduser()

class AuditLevel(Enum):
    """审计级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AuditCategory(Enum):
    """审计类别"""
    TASK = "task"
    AGENT = "agent"
    USER = "user"
    SYSTEM = "system"
    SECURITY = "security"
    NOTIFICATION = "notification"
    DEPLOYMENT = "deployment"

@dataclass
class AuditEntry:
    """审计条目"""
    id: str
    timestamp: str
    level: str
    category: str
    action: str
    user: str
    details: Dict
    ip_address: str = ""
    session_id: str = ""

class AuditLogger:
    """审计日志记录器"""

    def __init__(self, log_dir: Path = None):
        self.log_dir = log_dir or (SUITE_DIR / "logs" / "audit")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl"
        self.entries: List[AuditEntry] = []
        self.lock = threading.Lock()
        self._load_recent_entries()

    def _load_recent_entries(self):
        """加载最近条目"""
        try:
            if self.current_file.exists():
                with open(self.current_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                data = json.loads(line)
                                self.entries.append(AuditEntry(**data))
                            except:
                                pass
                self.entries = self.entries[-1000:]
        except Exception as e:
            print(f"加载审计日志失败: {e}")

    def log(self, level: AuditLevel, category: AuditCategory,
            action: str, user: str = "system", details: Dict = None,
            ip_address: str = "", session_id: str = ""):
        """记录审计日志"""
        entry = AuditEntry(
            id=f"audit-{uuid.uuid4().hex[:12]}",
            timestamp=datetime.now().isoformat(),
            level=level.value if hasattr(level, "value") else str(level),
            category=category.value if hasattr(category, "value") else str(category),
            action=action,
            user=user,
            details=details or {},
            ip_address=ip_address,
            session_id=session_id
        )

        with self.lock:
            self.entries.append(entry)
            self._write_entry(entry)

    def _write_entry(self, entry: AuditEntry):
        """写入条目"""
        try:
            with open(self.current_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(asdict(entry), ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"写入审计日志失败: {e}")

    def query(self, level: AuditLevel = None, category: AuditCategory = None,
              user: str = None, start_time: datetime = None,
              end_time: datetime = None, limit: int = 100) -> List[AuditEntry]:
        """查询审计日志"""
        results = self.entries

        if level:
            results = [e for e in results if e.level == level.value]
        if category:
            results = [e for e in results if e.category == category.value]
        if user:
            results = [e for e in results if e.user == user]
        if start_time:
            results = [e for e in results if datetime.fromisoformat(e.timestamp) >= start_time]
        if end_time:
            results = [e for e in results if datetime.fromisoformat(e.timestamp) <= end_time]

        return results[-limit:]

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        if not self.entries:
            return {}

        level_counts = defaultdict(int)
        category_counts = defaultdict(int)
        user_counts = defaultdict(int)

        for entry in self.entries:
            level_counts[entry.level] += 1
            category_counts[entry.category] += 1
            user_counts[entry.user] += 1

        return {
            'total': len(self.entries),
            'by_level': dict(level_counts),
            'by_category': dict(category_counts),
            'by_user': dict(user_counts),
            'first_entry': self.entries[0].timestamp if self.entries else None,
            'last_entry': self.entries[-1].timestamp if self.entries else None
        }

    def generate_report(self, days: int = 7) -> str:
        """生成审计报告"""
        start_time = datetime.now() - timedelta(days=days)
        entries = [e for e in self.entries
                   if datetime.fromisoformat(e.timestamp) >= start_time]

        lines = [
            f"📊 审计报告 (最近{days}天)",
            "=" * 50,
            f"总记录数: {len(entries)}",
            ""
        ]

        category_counts = defaultdict(int)
        for e in entries:
            category_counts[e.category] += 1

        lines.append("按类别统计:")
        for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            lines.append(f"  {cat}: {count}")

        lines.append("")
        lines.append("最近10条记录:")
        for e in entries[-10:]:
            emoji = {
                'INFO': 'ℹ️',
                'WARNING': '⚠️',
                'ERROR': '❌',
                'CRITICAL': '🔴'
            }.get(e.level, '•')
            lines.append(f"  {emoji} {e.timestamp[:19]} [{e.category}] {e.action}")

        return "\n".join(lines)


from datetime import timedelta

audit_logger = AuditLogger()
