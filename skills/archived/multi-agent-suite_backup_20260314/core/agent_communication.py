# Agent间通信模块
# 实现Agent消息传递和协作

from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import os

SUITE_DIR = Path("~/.openclaw/workspace/skills/multi-agent-suite").expanduser()

class AgentCommunication:
    """Agent通信中心"""
    
    def __init__(self):
        self.messages = []
        self.subscriptions = {}
        self._load_messages()
    
    def _load_messages(self):
        """加载历史消息"""
        msg_file = SUITE_DIR / "messages.json"
        if msg_file.exists():
            try:
                with open(msg_file, 'r', encoding='utf-8') as f:
                    self.messages = json.load(f)
            except:
                self.messages = []
    
    def _save_messages(self):
        """保存消息到文件"""
        msg_file = SUITE_DIR / "messages.json"
        try:
            with open(msg_file, 'w', encoding='utf-8') as f:
                json.dump(self.messages[-100:], f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def send_message(self, from_agent: str, to_agent: str, message_type: str, content: Any) -> Dict:
        """发送消息"""
        msg = {
            'id': f"msg-{len(self.messages) + 1}",
            'from': from_agent,
            'to': to_agent,
            'type': message_type,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
        self.messages.append(msg)
        self._save_messages()
        return msg
    
    def get_messages(self, agent_id: str = None, unread_only: bool = False) -> List[Dict]:
        """获取消息"""
        if agent_id:
            filtered = [m for m in self.messages if m['to'] == agent_id or m['to'] == 'broadcast']
            if unread_only:
                filtered = [m for m in filtered if not m.get('read', False)]
            return filtered
        return self.messages
    
    def mark_read(self, message_id: str):
        """标记消息为已读"""
        for msg in self.messages:
            if msg['id'] == message_id:
                msg['read'] = True
                break
        self._save_messages()
    
    def subscribe(self, agent_id: str, event_type: str):
        """订阅事件"""
        key = f"{agent_id}"
        if key not in self.subscriptions:
            self.subscriptions[key] = []
        if event_type not in self.subscriptions[key]:
            self.subscriptions[key].append(event_type)
    
    def broadcast(self, from_agent: str, message_type: str, content: Any):
        """广播消息"""
        msg = self.send_message(from_agent, 'broadcast', message_type, content)
        for agent_id in self._get_all_agent_ids():
            if agent_id != from_agent:
                inbox_msg = msg.copy()
                inbox_msg['to'] = agent_id
                self.messages.append(inbox_msg)
        self._save_messages()
    
    def ask_for_help(self, agent_id: str, task: str, context: Dict) -> Dict:
        """请求协助"""
        return self.send_message(
            agent_id, 'orchestrator', 'help_request',
            {'task': task, 'context': context}
        )
    
    def notify_completion(self, agent_id: str, task_id: str, result: Any):
        """通知任务完成"""
        return self.send_message(
            agent_id, 'orchestrator', 'task_completed',
            {'task_id': task_id, 'result': result}
        )
    
    def notify_failure(self, agent_id: str, task_id: str, error: str):
        """通知任务失败"""
        return self.send_message(
            agent_id, 'orchestrator', 'task_failed',
            {'task_id': task_id, 'error': error}
        )
    
    def _get_all_agent_ids(self) -> List[str]:
        """获取所有Agent ID"""
        return ['alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot', 'golf', 'hotel', 'india', 'juliet', 'kilo']
