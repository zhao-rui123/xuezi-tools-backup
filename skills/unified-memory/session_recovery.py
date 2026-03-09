#!/usr/bin/env python3
"""
会话恢复机制 - 解决跨会话失忆问题
Session Recovery System

核心功能：
1. 会话结束时自动保存状态
2. 新会话启动时主动恢复
3. 检测对话中断，提醒未完成的任务
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List

WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
SESSION_STATE_DIR = MEMORY_DIR / "session_states"
SESSION_STATE_DIR.mkdir(parents=True, exist_ok=True)

CURRENT_STATE_FILE = SESSION_STATE_DIR / "current_session.json"
PENDING_TASKS_FILE = SESSION_STATE_DIR / "pending_tasks.json"


class SessionRecovery:
    """会话恢复管理器"""
    
    def __init__(self):
        self.pending_context = []
        self.unfinished_tasks = []
    
    def save_session_state(self, context: Dict):
        """
        保存当前会话状态
        在以下情况调用：
        - 用户说"我去睡了"/"明天再说"
        - 会话自然结束
        - 系统即将重启/切换模型
        """
        state = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "context": context,
            "has_unfinished_work": context.get("has_unfinished_work", False),
            "last_query": context.get("last_query", ""),
            "pending_tasks": context.get("pending_tasks", []),
            "current_project": context.get("current_project", ""),
            "important_decisions": context.get("important_decisions", [])
        }
        
        with open(CURRENT_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        print(f"💾 会话状态已保存: {datetime.now().strftime('%H:%M:%S')}")
        return state
    
    def check_last_session(self) -> Optional[Dict]:
        """
        检查上一个会话状态
        在新会话启动时调用
        
        Returns:
            如果有未完成的上下文，返回状态字典
            如果会话已正常结束，返回 None
        """
        if not CURRENT_STATE_FILE.exists():
            return None
        
        try:
            with open(CURRENT_STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            last_time = datetime.fromisoformat(state["timestamp"])
            now = datetime.now()
            time_gap = now - last_time
            
            # 如果间隔小于1小时，可能是正常结束
            if time_gap < timedelta(hours=1):
                return None
            
            # 检查是否有未完成的工作
            if state.get("has_unfinished_work"):
                state["time_gap_hours"] = time_gap.total_seconds() / 3600
                return state
            
            # 如果有待办任务
            if state.get("pending_tasks"):
                state["time_gap_hours"] = time_gap.total_seconds() / 3600
                return state
            
            return None
            
        except Exception as e:
            print(f"⚠️ 读取会话状态失败: {e}")
            return None
    
    def generate_recovery_prompt(self, state: Dict) -> str:
        """
        生成恢复提示
        """
        gap_hours = state.get("time_gap_hours", 0)
        last_query = state.get("last_query", "")
        pending_tasks = state.get("pending_tasks", [])
        current_project = state.get("current_project", "")
        
        prompt_parts = []
        
        # 时间信息
        if gap_hours < 24:
            prompt_parts.append(f"距离上次对话已过去 {gap_hours:.1f} 小时")
        else:
            days = int(gap_hours / 24)
            prompt_parts.append(f"距离上次对话已过去 {days} 天")
        
        # 未完成的上下文
        if last_query:
            prompt_parts.append(f"\n上次我们聊到: {last_query[:100]}...")
        
        # 当前项目
        if current_project:
            prompt_parts.append(f"当时正在做的项目: {current_project}")
        
        # 待办任务
        if pending_tasks:
            prompt_parts.append(f"\n未完成的任务:")
            for task in pending_tasks[:3]:
                prompt_parts.append(f"  - {task}")
        
        # 询问
        prompt_parts.append(f"\n需要我:")
        prompt_parts.append(f"1. 继续之前的工作")
        prompt_parts.append(f"2. 总结一下当前状态")
        prompt_parts.append(f"3. 开始新的话题")
        
        return "\n".join(prompt_parts)
    
    def mark_session_closed(self, reason: str = "normal"):
        """
        标记会话已正常结束
        在用户明确说结束时调用
        """
        if CURRENT_STATE_FILE.exists():
            # 重命名为已关闭状态
            closed_file = SESSION_STATE_DIR / f"closed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            CURRENT_STATE_FILE.rename(closed_file)
            print(f"✅ 会话已标记为结束: {reason}")
    
    def detect_end_signal(self, user_message: str) -> bool:
        """
        检测用户是否要结束对话
        """
        end_signals = [
            "我去睡了", "睡觉了", "晚安", "明天再说",
            "先这样", "今天就到这里", "结束了", "bye",
            "我去吃饭了", "出门了", "忙去了"
        ]
        
        message_lower = user_message.lower()
        for signal in end_signals:
            if signal in message_lower:
                return True
        
        return False
    
    def record_pending_task(self, task: str):
        """
        记录待办任务
        """
        tasks = []
        if PENDING_TASKS_FILE.exists():
            try:
                with open(PENDING_TASKS_FILE, 'r', encoding='utf-8') as f:
                    tasks = json.load(f)
            except:
                pass
        
        tasks.append({
            "task": task,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        })
        
        with open(PENDING_TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        
        print(f"📝 已记录待办: {task}")


def on_session_start() -> Optional[str]:
    """
    新会话启动时调用
    
    Returns:
        如果有需要恢复的内容，返回提示字符串
        否则返回 None
    """
    recovery = SessionRecovery()
    state = recovery.check_last_session()
    
    if state:
        prompt = recovery.generate_recovery_prompt(state)
        return prompt
    
    return None


def on_session_end(context: Dict, user_message: str = ""):
    """
    会话结束时调用
    """
    recovery = SessionRecovery()
    
    # 检测是否是正常结束
    if recovery.detect_end_signal(user_message):
        context["has_unfinished_work"] = False
        recovery.save_session_state(context)
        recovery.mark_session_closed("user_end")
        print("✅ 会话正常结束，状态已保存")
    else:
        # 可能是意外中断
        context["has_unfinished_work"] = True
        recovery.save_session_state(context)
        print("⚠️ 检测到未完成工作，状态已保存")


def on_user_message(user_message: str, current_context: Dict) -> Dict:
    """
    每次用户消息时调用
    
    Returns:
        更新后的上下文
    """
    recovery = SessionRecovery()
    
    # 更新上下文
    current_context["last_query"] = user_message
    current_context["timestamp"] = datetime.now().isoformat()
    
    # 检测待办关键词
    todo_keywords = ["待办", "todo", "需要", "要做", "开发", "实现", "修复"]
    if any(kw in user_message for kw in todo_keywords):
        # 可能是新任务
        pass
    
    return current_context


# 命令行接口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="会话恢复系统")
    parser.add_argument("action", choices=["check", "save", "close"])
    parser.add_argument("--message", "-m", help="用户消息")
    parser.add_argument("--project", "-p", help="当前项目")
    
    args = parser.parse_args()
    
    recovery = SessionRecovery()
    
    if args.action == "check":
        result = on_session_start()
        if result:
            print(result)
        else:
            print("✅ 没有需要恢复的会话")
    
    elif args.action == "save":
        context = {
            "last_query": args.message or "",
            "current_project": args.project or "",
            "has_unfinished_work": True,
            "pending_tasks": []
        }
        recovery.save_session_state(context)
    
    elif args.action == "close":
        recovery.mark_session_closed("manual")
