#!/usr/bin/env python3
"""
会话内容捕获器 - 捕获OpenClaw会话内容
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import os

logger = logging.getLogger('memory-suite')


class SessionCapture:
    """会话内容捕获器"""

    def __init__(self, memory_dir: Path):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def capture_session(self, session_data: Dict[str, Any]) -> Optional[str]:
        """捕获会话内容并保存"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            memory_file = self.memory_dir / f"{today}.md"

            # 确保记忆文件存在（如果不存在则创建）
            if not memory_file.exists():
                self._create_memory_file_header(memory_file, today)

            # 构建记忆内容
            content = self._format_session_content(session_data)

            # 追加到今日记忆文件
            with open(memory_file, 'a', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"会话内容已保存: {memory_file}")
            return str(memory_file)

        except Exception as e:
            logger.error(f"捕获会话失败: {e}")
            return None

    def _create_memory_file_header(self, memory_file: Path, date_str: str) -> None:
        """创建记忆文件头部"""
        with open(memory_file, 'w', encoding='utf-8') as f:
            f.write(f"# {date_str} 记忆记录\n\n")
            f.write(f"*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            f.write("## 今日概览\n\n")
            f.write("- 新的一天开始\n\n")
            f.write("## 会话记录\n\n")

    def _format_session_content(self, data: Dict[str, Any]) -> str:
        """格式化会话内容为Markdown"""
        timestamp = datetime.now().strftime("%H:%M")

        content_parts = [
            f"\n## [{timestamp}] {data.get('title', '会话记录')}\n",
            f"\n**类型**: {data.get('type', 'chat')}\n",
        ]

        # 添加对话内容
        if 'messages' in data:
            content_parts.append("\n### 对话内容\n")
            for msg in data['messages']:
                role = msg.get('role', 'unknown')
                text = msg.get('content', '')
                content_parts.append(f"\n**{role}**: {text}\n")

        # 添加关键决策
        if 'decisions' in data:
            content_parts.append("\n### 关键决策\n")
            for decision in data['decisions']:
                content_parts.append(f"- {decision}\n")

        # 添加执行的操作
        if 'actions' in data:
            content_parts.append("\n### 执行操作\n")
            for action in data['actions']:
                content_parts.append(f"- {action}\n")

        # 添加元数据
        content_parts.append(f"\n---\n*记录时间: {datetime.now().isoformat()}*\n")

        return "".join(content_parts)

    def create_daily_summary(self) -> Optional[str]:
        """创建每日记忆文件（如果不存在）"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            memory_file = self.memory_dir / f"{today}.md"

            if not memory_file.exists():
                # 创建空的每日记忆文件
                with open(memory_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {today} 记忆记录\n\n")
                    f.write(f"*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
                    f.write("## 今日概览\n\n")
                    f.write("- 等待记录...\n\n")

                logger.info(f"创建每日记忆文件: {memory_file}")
                return str(memory_file)

            return None

        except Exception as e:
            logger.error(f"创建每日记忆文件失败: {e}")
            return None

    def ensure_daily_file_exists(self) -> Path:
        """确保今日记忆文件存在（用于定时任务）"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            memory_file = self.memory_dir / f"{today}.md"

            if not memory_file.exists():
                # 创建新的每日记忆文件
                with open(memory_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {today} 记忆记录\n\n")
                    f.write(f"*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
                    f.write("## 今日概览\n\n")
                    f.write("- 新的一天开始\n\n")
                    f.write("## 会话记录\n\n")

                logger.info(f"创建新的每日记忆文件: {memory_file}")

            return memory_file

        except Exception as e:
            logger.error(f"确保每日记忆文件失败: {e}")
            return self.memory_dir / f"{datetime.now().strftime('%Y-%m-%d')}.md"

    def get_session_stats(self, date: Optional[str] = None) -> Dict[str, Any]:
        """获取会话统计信息"""
        try:
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")

            memory_file = self.memory_dir / f"{date}.md"

            if not memory_file.exists():
                return {
                    "date": date,
                    "exists": False,
                    "sessions": 0,
                    "word_count": 0
                }

            content = memory_file.read_text(encoding='utf-8')
            sessions = content.count("## [")
            word_count = len(content.split())

            return {
                "date": date,
                "exists": True,
                "sessions": sessions,
                "word_count": word_count,
                "file_size": memory_file.stat().st_size
            }

        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {"date": date, "error": str(e)}


class SnapshotCapture:
    """增强版快照捕获器"""

    def __init__(self, snapshot_dir: Path):
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def save_snapshot(self, session_content: Dict[str, Any]) -> Optional[str]:
        """保存包含内容的快照"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_file = self.snapshot_dir / f"snapshot_{timestamp}.json"

            # 读取当前会话历史（如果可用）
            session_history = self._get_session_history()

            snapshot_data = {
                "timestamp": timestamp,
                "created_at": datetime.now().isoformat(),
                "type": "auto",
                "status": "ok",
                "session_history": session_history,
                "current_task": session_content.get('current_task', ''),
                "context": session_content.get('context', {}),
                "metadata": session_content.get('metadata', {})
            }

            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot_data, f, ensure_ascii=False, indent=2)

            logger.info(f"增强快照已保存: {snapshot_file}")
            return str(snapshot_file)

        except Exception as e:
            logger.error(f"保存快照失败: {e}")
            return None

    def _get_session_history(self) -> List[Dict[str, Any]]:
        """获取当前会话历史"""
        # 尝试从环境变量或临时文件读取
        history = []

        # 检查是否有会话历史文件
        session_file = Path("/tmp/openclaw_session.json")
        if session_file.exists():
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                pass

        return history
