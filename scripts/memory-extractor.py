#!/usr/bin/env python3
"""
自动记忆提取器 - 从对话中自动提取关键信息
"""

import json
import re
from datetime import datetime
from pathlib import Path

class MemoryExtractor:
    def __init__(self, workspace_path="/Users/zhaoruicn/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.kb_dir = self.workspace / "knowledge-base"
        self.memory_dir = self.workspace / "memory"
    
    def extract_from_message(self, user_msg, assistant_msg):
        """
        从单条对话中提取记忆
        
        Returns:
            list: 提取到的记忆项 [{"type": "decision/problem/todo/data", "content": "..."}]
        """
        memories = []
        
        # 提取决策
        decisions = self._extract_decisions(user_msg)
        for d in decisions:
            memories.append({"type": "decision", "content": d})
        
        # 提取问题
        problems = self._extract_problems(user_msg, assistant_msg)
        for p in problems:
            memories.append({"type": "problem", "content": p})
        
        # 提取待办
        todos = self._extract_todos(user_msg)
        for t in todos:
            memories.append({"type": "todo", "content": t})
        
        # 提取数据
        data = self._extract_data(user_msg, assistant_msg)
        for d in data:
            memories.append({"type": "data", "content": d})
        
        return memories
    
    def _extract_decisions(self, message):
        """提取决策"""
        decisions = []
        
        # 决策模式
        patterns = [
            r"确定[了用]?(.{3,50}?)[。，\n]",
            r"决定[了用]?(.{3,50}?)[。，\n]",
            r"采用(.{3,50}?)[。，\n]",
            r"选择[了]?(.{3,50}?)[。，\n]",
            r"使用(.{3,50}?)[。，\n]",
            r"方案[是：](.{3,50}?)[。，\n]",
            r"(.{3,30}?)[，。]就按这个",
            r"同意(.{3,30}?)[。，\n]",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, message)
            for match in matches:
                decisions.append(match.strip())
        
        return decisions
    
    def _extract_problems(self, user_msg, assistant_msg):
        """提取问题和解决方案"""
        problems = []
        
        # 问题模式
        problem_patterns = [
            r"(.{3,30}?)有[个种]?问题",
            r"(.{3,30}?)出错了",
            r"(.{3,30}?)失败了",
            r"(.{3,30}?)不[能工作正常]",
            r"解决[了]?(.{3,30}?)[。，\n]",
        ]
        
        for pattern in problem_patterns:
            matches = re.findall(pattern, user_msg + " " + assistant_msg)
            for match in matches:
                problems.append(match.strip())
        
        return problems
    
    def _extract_todos(self, message):
        """提取待办事项"""
        todos = []
        
        # 待办模式
        patterns = [
            r"待办[：:]?(.+?)[。\n]",
            r"TODO[：:]?(.+?)[。\n]",
            r"\[ \](.+?)[。\n]",
            r"需要(.{3,30}?)[。，\n]",
            r"还要(.{3,30}?)[。，\n]",
            r"下次(.{3,30}?)[。，\n]",
            r"之后(.{3,30}?)[。，\n]",
            r"记得(.{3,30}?)[。，\n]",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            for match in matches:
                todos.append(match.strip())
        
        return todos
    
    def _extract_data(self, user_msg, assistant_msg):
        """提取关键数据"""
        data = []
        content = user_msg + " " + assistant_msg
        
        # 配置数据
        config_patterns = [
            (r"主模型[：:]\s*(.+?)[。，\n]", "模型配置"),
            (r"API Key[：:]\s*(sk-[a-zA-Z0-9-]+)", "API Key"),
            (r"路径[：:]\s*(/[^\s]+)", "路径"),
            (r"IP[：:]\s*(\d+\.\d+\.\d+\.\d+)", "IP地址"),
            (r"端口[：:]\s*(\d+)", "端口"),
            (r"成本[：:]\s*(\d+[\.\d]*)", "成本"),
            (r"投资[：:]\s*(\d+[\.\d]*万?)", "投资金额"),
            (r"收益[：:]\s*(\d+[\.\d]*万?)", "收益金额"),
        ]
        
        for pattern, label in config_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                data.append(f"{label}: {match}")
        
        return data
    
    def save_memory(self, memory):
        """保存提取的记忆"""
        if not memory:
            return None
        
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        if memory["type"] == "decision":
            # 保存到 decisions
            filename = f"auto-{timestamp}-{memory['content'][:20]}.md"
            filepath = self.kb_dir / "decisions" / filename
            
            content = f"""# {memory['content']}

**状态**: ✅已采纳
**标签**: #自动提取
**日期**: {timestamp}

## 背景
从对话中自动提取的决策

## 决策内容
{memory['content']}

## 相关链接
- [对话记录](../memory/{timestamp}.md)
"""
            
        elif memory["type"] == "problem":
            # 保存到 problems
            filename = f"auto-{timestamp}-{memory['content'][:20]}.md"
            filepath = self.kb_dir / "problems" / "auto" / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            content = f"""# {memory['content']}

**状态**: ⚠️待验证
**标签**: #自动提取
**日期**: {timestamp}

## 问题描述
{memory['content']}

## 备注
从对话中自动提取，需要人工验证和补充解决方案
"""
            
        elif memory["type"] == "todo":
            # 添加到今日记忆的 TODO 区块
            today_file = self.memory_dir / f"{timestamp}.md"
            if today_file.exists():
                with open(today_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n- [ ] {memory['content']} (自动提取)\n")
            return today_file
            
        elif memory["type"] == "data":
            # 添加到 MEMORY.md 的 DATA 区块
            memory_file = self.workspace / "MEMORY.md"
            if memory_file.exists():
                with open(memory_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n- {memory['content']} ({timestamp})\n")
            return memory_file
        
        else:
            return None
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath


if __name__ == "__main__":
    # 测试
    extractor = MemoryExtractor()
    
    user_msg = "确定使用四层结构管理知识库，待办：添加文档模板"
    assistant_msg = "好的，已创建目录结构"
    
    memories = extractor.extract_from_message(user_msg, assistant_msg)
    print(json.dumps(memories, ensure_ascii=False, indent=2))
