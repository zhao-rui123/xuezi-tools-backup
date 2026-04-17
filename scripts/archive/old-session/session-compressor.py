#!/usr/bin/env python3
"""
会话压缩器 - 自动压缩长对话，保留关键信息
"""

import json
import re
from datetime import datetime
from pathlib import Path

class SessionCompressor:
    def __init__(self, workspace_path="/Users/zhaoruicn/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.memory_dir = self.workspace / "memory"
        self.summary_dir = self.memory_dir / "session-summaries"
        self.summary_dir.mkdir(parents=True, exist_ok=True)
    
    def compress_session(self, messages, session_key=None):
        """
        压缩会话，提取关键信息
        
        Args:
            messages: 对话消息列表 [{"role": "user/assistant", "content": "..."}]
            session_key: 会话标识
        
        Returns:
            dict: 压缩后的会话摘要
        """
        if len(messages) < 10:
            return None  # 对话太短，不需要压缩
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "session_key": session_key,
            "total_messages": len(messages),
            "summary": self._generate_summary(messages),
            "decisions": self._extract_decisions(messages),
            "todos": self._extract_todos(messages),
            "key_data": self._extract_key_data(messages),
            "topics": self._extract_topics(messages)
        }
        
        return summary
    
    def _generate_summary(self, messages):
        """生成3-5句话的会话摘要"""
        # 提取用户的主要请求
        user_messages = [m["content"] for m in messages if m["role"] == "user"]
        
        if not user_messages:
            return "无用户输入"
        
        # 取最后几条用户消息作为当前主题
        recent_topics = user_messages[-3:]
        
        summary_parts = []
        
        # 第一条：会话主题
        first_msg = user_messages[0][:100]
        summary_parts.append(f"会话主题：{first_msg}...")
        
        # 第二条：主要活动
        assistant_msgs = [m["content"] for m in messages if m["role"] == "assistant"]
        if assistant_msgs:
            # 检测活动类型
            activities = []
            content = " ".join(assistant_msgs).lower()
            
            if any(word in content for word in ["创建", "生成", "写", "做"]):
                activities.append("创建内容")
            if any(word in content for word in ["修复", "解决", "调试"]):
                activities.append("修复问题")
            if any(word in content for word in ["查询", "查看", "检查"]):
                activities.append("查询信息")
            if any(word in content for word in ["配置", "设置", "修改"]):
                activities.append("配置系统")
            
            if activities:
                summary_parts.append(f"主要活动：{', '.join(activities)}")
        
        # 第三条：当前状态
        if recent_topics:
            last_topic = recent_topics[-1][:80]
            summary_parts.append(f"当前讨论：{last_topic}...")
        
        return "\n".join(summary_parts)
    
    def _extract_decisions(self, messages):
        """提取决策点"""
        decisions = []
        
        # 决策关键词模式
        decision_patterns = [
            r"确定[了用]?(.{3,30})",
            r"决定[了用]?(.{3,30})",
            r"采用(.{3,30})",
            r"选择[了]?(.{3,30})",
            r"使用(.{3,30})",
            r"方案[是：]?(.{3,30})",
        ]
        
        for msg in messages:
            if msg["role"] != "user":
                continue
            
            content = msg["content"]
            for pattern in decision_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    decisions.append(match.strip())
        
        return list(set(decisions))[:5]  # 去重，最多5个
    
    def _extract_todos(self, messages):
        """提取待办事项"""
        todos = []
        
        # 待办关键词模式
        todo_patterns = [
            r"待办[：:]?(.+)",
            r"TODO[：:]?(.+)",
            r"\[ \](.+)",
            r"需要(.{3,30})",
            r"还要(.{3,30})",
            r"下次(.{3,30})",
        ]
        
        for msg in messages:
            content = msg["content"]
            for pattern in todo_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    todos.append(match.strip())
        
        return list(set(todos))[:10]  # 去重，最多10个
    
    def _extract_key_data(self, messages):
        """提取关键数据"""
        data = {}
        
        # 提取配置信息
        config_patterns = [
            (r"主模型[：:]\s*(.+)", "主模型"),
            (r"API Key[：:]\s*(sk-[a-zA-Z0-9-]+)", "API Key"),
            (r"路径[：:]\s*(/[^\s]+)", "路径"),
            (r"IP[：:]\s*(\d+\.\d+\.\d+\.\d+)", "IP地址"),
            (r"端口[：:]\s*(\d+)", "端口"),
        ]
        
        for msg in messages:
            content = msg["content"]
            for pattern, label in config_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    if label not in data:
                        data[label] = []
                    data[label].extend(matches)
        
        # 去重
        for key in data:
            data[key] = list(set(data[key]))
        
        return data
    
    def _extract_topics(self, messages):
        """提取讨论主题"""
        topics = []
        
        # 主题关键词
        topic_keywords = [
            "知识库", "模型", "配置", "备份", "恢复",
            "飞书", "Gateway", "技能包", "项目", "代码"
        ]
        
        all_content = " ".join([m["content"] for m in messages])
        
        for keyword in topic_keywords:
            if keyword in all_content:
                topics.append(keyword)
        
        return topics
    
    def save_summary(self, summary):
        """保存会话摘要"""
        if not summary:
            return None
        
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
        filename = f"session-summary-{timestamp}.json"
        filepath = self.summary_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def get_latest_summary(self):
        """获取最新的会话摘要"""
        summaries = sorted(self.summary_dir.glob("session-summary-*.json"))
        if not summaries:
            return None
        
        with open(summaries[-1], 'r', encoding='utf-8') as f:
            return json.load(f)


if __name__ == "__main__":
    # 测试
    compressor = SessionCompressor()
    
    test_messages = [
        {"role": "user", "content": "帮我整理一下知识库"},
        {"role": "assistant", "content": "好的，我来整理知识库结构"},
        {"role": "user", "content": "确定使用四层结构：projects/decisions/problems/references"},
        {"role": "assistant", "content": "已创建目录结构"},
        {"role": "user", "content": "待办：添加文档模板"},
    ]
    
    summary = compressor.compress_session(test_messages, "test-session")
    if summary:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        compressor.save_summary(summary)
