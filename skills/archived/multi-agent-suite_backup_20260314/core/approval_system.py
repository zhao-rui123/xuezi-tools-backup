"""
人工介入与审批系统
关键节点需要人工确认
"""

import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path

SUITE_DIR = Path("~/.openclaw/workspace/skills/multi-agent-suite").expanduser()

class ApprovalStatus(Enum):
    """审批状态"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class ApprovalType(Enum):
    """审批类型"""
    TASK_START = "task_start"
    TASK_COMPLETE = "task_complete"
    DEPLOYMENT = "deployment"
    CONFIG_CHANGE = "config_change"
    CODE_REVIEW = "code_review"
    CUSTOM = "custom"

@dataclass
class ApprovalRequest:
    """审批请求"""
    id: str
    type: ApprovalType
    title: str
    description: str
    requester: str
    approver: str = ""
    status: ApprovalStatus = ApprovalStatus.PENDING
    data: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    approved_at: Optional[str] = None
    comments: str = ""
    expires_at: Optional[str] = None

class ApprovalSystem:
    """人工介入审批系统"""

    def __init__(self, storage_dir: Path = None):
        self.storage_dir = storage_dir or (SUITE_DIR / "data" / "approvals")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.requests: Dict[str, ApprovalRequest] = {}
        self.handlers: Dict[ApprovalType, Callable] = {}
        self._load_requests()

    def _load_requests(self):
        """加载请求"""
        try:
            requests_file = self.storage_dir / "requests.json"
            if requests_file.exists():
                with open(requests_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for req_id, req_data in data.items():
                        req_data['type'] = ApprovalType(req_data['type'])
                        req_data['status'] = ApprovalStatus(req_data['status'])
                        self.requests[req_id] = ApprovalRequest(**req_data)
        except Exception as e:
            print(f"加载审批请求失败: {e}")

    def _save_requests(self):
        """保存请求"""
        try:
            requests_file = self.storage_dir / "requests.json"
            data = {}
            for req_id, req in self.requests.items():
                req_dict = {
                    'id': req.id,
                    'type': req.type.value,
                    'title': req.title,
                    'description': req.description,
                    'requester': req.requester,
                    'approver': req.approver,
                    'status': req.status.value,
                    'data': req.data,
                    'created_at': req.created_at,
                    'approved_at': req.approved_at,
                    'comments': req.comments,
                    'expires_at': req.expires_at
                }
                data[req_id] = req_dict
            with open(requests_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存审批请求失败: {e}")

    def create_request(self, approval_type: ApprovalType, title: str,
                      description: str, requester: str, data: Dict = None,
                      approver: str = "", expires_hours: int = 24) -> str:
        """创建审批请求"""
        request_id = f"apr-{uuid.uuid4().hex[:8]}"

        expires_at = None
        if expires_hours > 0:
            expires_at = (datetime.now().replace(
                hour=23, minute=59, second=59
            )).isoformat()

        request = ApprovalRequest(
            id=request_id,
            type=approval_type,
            title=title,
            description=description,
            requester=requester,
            approver=approver,
            data=data or {},
            expires_at=expires_at
        )

        self.requests[request_id] = request
        self._save_requests()

        return request_id

    def approve(self, request_id: str, approver: str, comments: str = "") -> bool:
        """批准请求"""
        request = self.requests.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return False

        request.status = ApprovalStatus.APPROVED
        request.approver = approver
        request.approved_at = datetime.now().isoformat()
        request.comments = comments

        self._save_requests()

        if request.type in self.handlers:
            try:
                self.handlers[request.type](request, True)
            except Exception as e:
                print(f"审批处理失败: {e}")

        return True

    def reject(self, request_id: str, approver: str, comments: str = "") -> bool:
        """拒绝请求"""
        request = self.requests.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return False

        request.status = ApprovalStatus.REJECTED
        request.approver = approver
        request.approved_at = datetime.now().isoformat()
        request.comments = comments

        self._save_requests()

        if request.type in self.handlers:
            try:
                self.handlers[request.type](request, False)
            except Exception as e:
                print(f"拒绝处理失败: {e}")

        return True

    def cancel(self, request_id: str) -> bool:
        """取消请求"""
        request = self.requests.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return False

        request.status = ApprovalStatus.CANCELLED
        self._save_requests()
        return True

    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """获取请求"""
        return self.requests.get(request_id)

    def list_pending(self, approver: str = None) -> List[ApprovalRequest]:
        """列出待审批请求"""
        pending = [r for r in self.requests.values()
                 if r.status == ApprovalStatus.PENDING]

        if approver:
            pending = [r for r in pending if r.approver == approver or not r.approver]

        return sorted(pending, key=lambda r: r.created_at)

    def register_handler(self, approval_type: ApprovalType, handler: Callable):
        """注册处理函数"""
        self.handlers[approval_type] = handler

    def get_status(self) -> Dict:
        """获取审批状态"""
        status_counts = {}
        for status in ApprovalStatus:
            status_counts[status.value] = sum(
                1 for r in self.requests.values() if r.status == status
            )

        return {
            'total': len(self.requests),
            'pending': status_counts['pending'],
            'approved': status_counts['approved'],
            'rejected': status_counts['rejected']
        }

    def visualize_pending(self) -> str:
        """可视化待审批列表"""
        pending = self.list_pending()

        if not pending:
            return "✅ 无待审批事项"

        lines = [
            f"📋 待审批事项 ({len(pending)} 项)",
            "=" * 50,
            ""
        ]

        for req in pending:
            type_emoji = {
                ApprovalType.TASK_START: "🚀",
                ApprovalType.TASK_COMPLETE: "✅",
                ApprovalType.DEPLOYMENT: "📦",
                ApprovalType.CONFIG_CHANGE: "⚙️",
                ApprovalType.CODE_REVIEW: "👀",
                ApprovalType.CUSTOM: "📝"
            }.get(req.type, "•")

            lines.append(f"{type_emoji} [{req.type.value}] {req.title}")
            lines.append(f"   申请人: {req.requester}")
            lines.append(f"   时间: {req.created_at[:16]}")
            if req.description:
                lines.append(f"   说明: {req.description[:50]}...")
            lines.append(f"   命令: python -m core.cli approval approve {req.id}")
            lines.append("")

        return "\n".join(lines)


approval_system = ApprovalSystem()
