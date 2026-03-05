#!/usr/bin/env python3
"""
会话状态快照 - 保存和恢复当前会话状态
"""

import json
from datetime import datetime
from pathlib import Path

class SessionSnapshot:
    def __init__(self, workspace_path="/Users/zhaoruicn/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.state_dir = self.workspace / "memory" / "session-state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / "current.json"
    
    def save_snapshot(self, session_info):
        """
        保存会话状态快照
        
        Args:
            session_info: {
                "session_key": "...",
                "current_topic": "...",
                "pending_tasks": [...],
                "user_mood": "...",
                "last_decision": "...",
                "key_files": [...],
                "recent_summary": "..."
            }
        """
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            **session_info
        }
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)
        
        return self.state_file
    
    def load_snapshot(self):
        """加载会话状态快照"""
        if not self.state_file.exists():
            return None
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载快照失败: {e}")
            return None
    
    def get_recovery_prompt(self):
        """
        生成恢复提示，帮助新模型快速了解上下文
        
        Returns:
            str: 3句话的恢复提示
        """
        snapshot = self.load_snapshot()
        if not snapshot:
            return None
        
        parts = []
        
        # 第一句：当前主题
        if snapshot.get("current_topic"):
            parts.append(f"当前正在讨论：{snapshot['current_topic']}")
        
        # 第二句：待办事项
        if snapshot.get("pending_tasks"):
            tasks = ", ".join(snapshot["pending_tasks"][:3])
            parts.append(f"待办事项：{tasks}")
        
        # 第三句：最近决策
        if snapshot.get("last_decision"):
            parts.append(f"最近决策：{snapshot['last_decision']}")
        
        if not parts:
            return "没有可用的会话状态快照"
        
        return "\n".join(parts)
    
    def clear_snapshot(self):
        """清除会话快照"""
        if self.state_file.exists():
            self.state_file.unlink()


if __name__ == "__main__":
    # 测试
    snapshot = SessionSnapshot()
    
    # 保存测试
    test_info = {
        "session_key": "test-session",
        "current_topic": "知识库管理升级",
        "pending_tasks": ["实现会话压缩", "实现自动提取"],
        "user_mood": "积极",
        "last_decision": "使用四层结构管理知识库",
        "key_files": ["knowledge-base/INDEX.md"],
        "recent_summary": "正在讨论记忆管理升级方案"
    }
    
    snapshot.save_snapshot(test_info)
    print("快照已保存")
    
    # 恢复测试
    prompt = snapshot.get_recovery_prompt()
    print("\n恢复提示：")
    print(prompt)
