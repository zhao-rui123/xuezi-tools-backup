#!/usr/bin/env python3
"""
Memory Suite v3 - Real-time Saver Module
实时保存模块

功能：
1. 每 10 分钟自动保存会话快照
2. 保存最近 50 轮对话
3. 生成语义摘要和关键词
4. 保存到 memory/snapshots/current_session.json

用法：
    from core.real_time import RealTimeSaver, get_saver
    
    # 初始化并启动
    saver = get_saver()
    saver.start()
    
    # 手动保存
    saver.save()
    
    # 停止服务
    saver.stop()

作者：Memory Suite Team
版本：3.0.0
"""

import json
import re
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


# ============================================================================
# 配置常量
# ============================================================================

DEFAULT_WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
DEFAULT_MEMORY_DIR = DEFAULT_WORKSPACE / "memory"
DEFAULT_SNAPSHOTS_DIR = DEFAULT_MEMORY_DIR / "snapshots"
DEFAULT_SNAPSHOT_FILE = DEFAULT_SNAPSHOTS_DIR / "current_session.json"

MAX_CONVERSATION_ROUNDS = 50  # 保存最近 50 轮对话
AUTO_SAVE_INTERVAL = 600  # 10 分钟 = 600 秒

# OpenClaw 会话存储路径
OPENCLAW_SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"


# ============================================================================
# 日志工具
# ============================================================================

class Logger:
    """简单日志记录器"""
    
    LEVELS = {"DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3}
    
    def __init__(self, name: str, level: str = "INFO"):
        self.name = name
        self.level = self.LEVELS.get(level, 1)
    
    def _log(self, level: str, message: str):
        if self.LEVELS.get(level, 1) >= self.level:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [{level}] [{self.name}] {message}")
    
    def debug(self, message: str):
        self._log("DEBUG", message)
    
    def info(self, message: str):
        self._log("INFO", message)
    
    def warn(self, message: str):
        self._log("WARN", message)
    
    def error(self, message: str):
        self._log("ERROR", message)


# ============================================================================
# 语义摘要器
# ============================================================================

class SemanticSummarizer:
    """
    语义摘要生成器 - 使用简单关键词提取
    """
    
    # 中文停用词
    STOP_WORDS = {
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也',
        '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那',
        '我们', '为', '之', '与', '及', '等', '或', '但', '而', '如果', '因为', '所以', '可以',
        '需要', '进行', '使用', '通过', '根据', '关于', '对于', '以及', '或者', '但是', '然后',
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall',
        'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
        'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between',
        'and', 'but', 'or', 'yet', 'so', 'if', 'because', 'although', 'though', 'while', 'where',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
        'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours'
    }
    
    # 项目相关关键词权重
    PROJECT_KEYWORDS = {
        '储能': 3.0, '光伏': 3.0, '新能源': 2.5, '电站': 2.5, '项目': 2.0,
        '测算': 2.5, '财务': 2.0, '投资': 2.0, '收益': 2.0, '成本': 2.0,
        '股票': 2.5, '分析': 2.0, '筛选': 2.0, '预警': 2.0, '财报': 2.0,
        '开发': 2.0, '代码': 2.0, '功能': 2.0, '模块': 2.0, '系统': 2.0,
        'agent': 2.5, '技能': 2.0, '工具': 2.0, '自动化': 2.0
    }
    
    def __init__(self):
        self.keywords_cache: Dict[str, List[str]] = {}
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """从文本中提取关键词"""
        if not text:
            return []
        
        text = self._clean_text(text)
        words = self._tokenize(text)
        
        word_freq = {}
        for word in words:
            word_lower = word.lower()
            if word_lower in self.STOP_WORDS or len(word) < 2:
                continue
            
            weight = 1.0
            for kw, kw_weight in self.PROJECT_KEYWORDS.items():
                if kw in word or word in kw:
                    weight *= kw_weight
                    break
            
            if 4 <= len(word) <= 8:
                weight *= 1.2
            
            word_freq[word] = word_freq.get(word, 0) + weight
        
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_n]]
    
    def generate_summary(self, conversations: List[Dict], max_length: int = 200) -> str:
        """生成对话摘要"""
        all_text = " ".join([
            f"{c.get('role', '')}: {c.get('content', '')}"
            for c in conversations[-20:]
        ])
        
        keywords = self.extract_keywords(all_text, top_n=15)
        summary_parts = []
        
        topic = self._identify_topic(keywords)
        if topic:
            summary_parts.append(f"主题：{topic}")
        
        if keywords:
            summary_parts.append(f"关键词：{', '.join(keywords[:8])}")
        
        actions = self._extract_actions(conversations)
        if actions:
            summary_parts.append(f"主要动作：{'; '.join(actions[:3])}")
        
        summary = " | ".join(summary_parts)
        if len(summary) > max_length:
            summary = summary[:max_length - 3] + "..."
        
        return summary
    
    def _clean_text(self, text: str) -> str:
        text = re.sub(r'http[s]?://\S+', ' ', text)
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _tokenize(self, text: str) -> List[str]:
        words = []
        for part in text.split():
            if re.match(r'^[a-zA-Z]+$', part):
                words.append(part.lower())
            else:
                chars = list(part)
                words.extend(chars)
                for n in [4, 3, 2]:
                    for i in range(len(chars) - n + 1):
                        words.append(''.join(chars[i:i+n]))
        return words
    
    def _identify_topic(self, keywords: List[str]) -> Optional[str]:
        topic_keywords = {
            '储能项目': ['储能', '电站', '光伏', '测算', '投资'],
            '股票分析': ['股票', '分析', '筛选', '行情', '财报', '预警'],
            '代码开发': ['开发', '代码', '功能', '模块', '系统', 'agent', '技能'],
            '数据处理': ['数据', '处理', '导入', '导出', '分析', '计算'],
            '文档处理': ['文档', '报告', 'pdf', 'word', 'excel', '生成']
        }
        
        keyword_set = set(keywords)
        best_topic = None
        best_score = 0
        
        for topic, indicators in topic_keywords.items():
            score = len(keyword_set & set(indicators))
            if score > best_score:
                best_score = score
                best_topic = topic
        
        return best_topic if best_score >= 2 else None
    
    def _extract_actions(self, conversations: List[Dict]) -> List[str]:
        action_patterns = [
            r'(创建 | 开发 | 实现 | 编写 | 生成 | 计算 | 分析 | 筛选 | 导出 | 导入 | 修改 | 更新 | 删除 | 添加)',
            r'(create|develop|implement|write|generate|calculate|analyze|export|import|update|delete|add)'
        ]
        
        actions = []
        for conv in conversations[-10:]:
            content = conv.get('content', '')
            for pattern in action_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                actions.extend(matches)
        
        seen = set()
        unique_actions = []
        for action in actions:
            if action not in seen:
                seen.add(action)
                unique_actions.append(action)
        
        return unique_actions[:5]


# ============================================================================
# 对话缓冲区
# ============================================================================

class ConversationBuffer:
    """对话缓冲区 - 管理最近 N 轮对话"""
    
    def __init__(self, max_rounds: int = MAX_CONVERSATION_ROUNDS):
        self.max_rounds = max_rounds
        self.buffer: deque = deque(maxlen=max_rounds * 2)
        self.lock = threading.Lock()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        with self.lock:
            self.buffer.append(message)
    
    def get_recent(self, n: int = 10) -> List[Dict]:
        with self.lock:
            return list(self.buffer)[-n:]
    
    def get_all(self) -> List[Dict]:
        with self.lock:
            return list(self.buffer)
    
    def clear(self):
        with self.lock:
            self.buffer.clear()
    
    def get_rounds_count(self) -> int:
        with self.lock:
            return len(self.buffer) // 2


# ============================================================================
# 实时保存器
# ============================================================================

class RealTimeSaver:
    """
    实时保存器 - 核心类
    
    功能：
    1. 自动定时保存
    2. 手动触发保存
    3. 生成语义摘要
    4. 管理会话状态
    """
    
    def __init__(self, 
                 snapshot_file: Optional[Path] = None,
                 auto_save_interval: int = AUTO_SAVE_INTERVAL,
                 max_rounds: int = MAX_CONVERSATION_ROUNDS,
                 workspace: Optional[Path] = None):
        self.workspace = workspace or DEFAULT_WORKSPACE
        self.memory_dir = self.workspace / "memory"
        self.snapshots_dir = self.memory_dir / "snapshots"
        self.snapshot_file = snapshot_file or self.snapshots_dir / "current_session.json"
        self.auto_save_interval = auto_save_interval
        self.max_rounds = max_rounds
        
        self.buffer = ConversationBuffer(max_rounds)
        self.summarizer = SemanticSummarizer()
        self.logger = Logger("RealTimeSaver")
        
        self.session_state: Dict[str, Any] = {
            "started_at": datetime.now().isoformat(),
            "last_saved_at": None,
            "total_messages": 0,
            "total_rounds": 0,
            "current_task": "",
            "project": "",
            "tags": []
        }
        
        self._auto_save_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        
        self._ensure_directories()
    
    def _ensure_directories(self):
        try:
            self.snapshots_dir.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"确保目录存在：{self.snapshots_dir}")
        except Exception as e:
            self.logger.error(f"创建目录失败：{e}")
            raise
    
    def start(self):
        """启动自动保存服务"""
        if self._auto_save_thread is not None and self._auto_save_thread.is_alive():
            self.logger.warn("自动保存服务已在运行")
            return
        
        self._stop_event.clear()
        self._auto_save_thread = threading.Thread(
            target=self._auto_save_loop,
            daemon=True,
            name="RealTimeSaver"
        )
        self._auto_save_thread.start()
        self.logger.info(f"实时保存服务已启动（每{self.auto_save_interval}秒自动保存）")
    
    def stop(self):
        """停止自动保存服务"""
        self._stop_event.set()
        if self._auto_save_thread and self._auto_save_thread.is_alive():
            self._auto_save_thread.join(timeout=5)
            self.logger.info("实时保存服务已停止")
    
    def _auto_save_loop(self):
        """自动保存循环"""
        while not self._stop_event.is_set():
            self._stop_event.wait(self.auto_save_interval)
            
            if not self._stop_event.is_set():
                try:
                    self.save(force=True)
                    self.logger.info(f"自动保存完成：{datetime.now().strftime('%H:%M:%S')}")
                except Exception as e:
                    self.logger.error(f"自动保存失败：{e}")
    
    def record_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """记录一条消息"""
        self.buffer.add_message(role, content, metadata)
        with self._lock:
            self.session_state["total_messages"] += 1
            self.session_state["total_rounds"] = self.buffer.get_rounds_count()
    
    def update_context(self, **kwargs):
        """更新会话上下文"""
        with self._lock:
            self.session_state.update(kwargs)
            self.logger.debug(f"更新上下文：{kwargs}")
    
    def _load_openclaw_session(self) -> Dict:
        """从 OpenClaw 会话存储加载数据"""
        try:
            sessions_file = OPENCLAW_SESSIONS_DIR / "sessions.json"
            if not sessions_file.exists():
                return {}
            
            with open(sessions_file, 'r', encoding='utf-8') as f:
                sessions = json.load(f)
            
            latest_session = None
            latest_time = 0
            
            for key, session in sessions.items():
                if key == 'agent:main:main':
                    latest_time = session.get('updatedAt', 0)
                    latest_session = session
                    break
                elif 'direct' in key and session.get('updatedAt', 0) > latest_time:
                    latest_time = session.get('updatedAt', 0)
                    latest_session = session
            
            if not latest_session:
                return {}
            
            session_file = latest_session.get('sessionFile')
            if session_file and Path(session_file).exists():
                with open(session_file, 'r', encoding='utf-8') as f:
                    lines = f.read().strip().split('\n')
                
                conversations = []
                for line in lines[-100:]:
                    try:
                        msg = json.loads(line)
                        if msg.get('type') == 'message':
                            message_data = msg.get('message', {})
                            content_data = message_data.get('content', [])
                            
                            text_content = ""
                            if isinstance(content_data, list):
                                for item in content_data:
                                    if isinstance(item, dict) and item.get('type') == 'text':
                                        text_content += item.get('text', '')
                            elif isinstance(content_data, str):
                                text_content = content_data
                            
                            role = message_data.get('role', '')
                            if role in ['user', 'assistant'] and text_content:
                                conversations.append({
                                    'role': role,
                                    'content': text_content[:500],
                                    'timestamp': msg.get('timestamp', datetime.now().isoformat())
                                })
                    except Exception:
                        continue
                
                return {
                    'conversations': conversations,
                    'session_key': latest_session.get('sessionKey', ''),
                    'updated_at': latest_time
                }
        
        except Exception as e:
            self.logger.warn(f"读取 OpenClaw 会话失败：{e}")
        
        return {}
    
    def save(self, force: bool = False) -> Dict:
        """保存当前会话状态"""
        with self._lock:
            try:
                openclaw_data = self._load_openclaw_session()
                conversations = openclaw_data.get('conversations', [])
                if not conversations:
                    conversations = self.buffer.get_all()
                
                semantic_summary = self.summarizer.generate_summary(
                    conversations, max_length=300
                ) if conversations else "无对话记录"
                
                all_text = " ".join([c.get("content", "") for c in conversations])
                keywords = self.summarizer.extract_keywords(all_text, top_n=20) if all_text else []
                
                current_task = self._infer_task(conversations)
                
                snapshot = {
                    "version": "3.0.0",
                    "saved_at": datetime.now().isoformat(),
                    "session": {
                        "started_at": self.session_state.get("started_at"),
                        "last_saved_at": datetime.now().isoformat(),
                        "duration_minutes": self._calculate_duration(),
                        "total_messages": len(conversations),
                        "total_rounds": len(conversations) // 2,
                        "openclaw_session": openclaw_data.get('session_key', '')
                    },
                    "context": {
                        "current_task": current_task or self.session_state.get("current_task", ""),
                        "project": self.session_state.get("project", ""),
                        "tags": self.session_state.get("tags", []),
                        "has_unfinished_work": len(conversations) > 0
                    },
                    "semantic_summary": semantic_summary,
                    "keywords": keywords,
                    "conversations": conversations[-self.max_rounds:]
                }
                
                with open(self.snapshot_file, 'w', encoding='utf-8') as f:
                    json.dump(snapshot, f, ensure_ascii=False, indent=2)
                
                self._append_to_daily_memory(snapshot)
                self.session_state["last_saved_at"] = datetime.now().isoformat()
                
                self.logger.debug(f"保存完成：{self.snapshot_file}")
                return snapshot
            
            except Exception as e:
                self.logger.error(f"保存失败：{e}")
                raise
    
    def _infer_task(self, conversations: List[Dict]) -> str:
        if not conversations:
            return ""
        
        assistant_msgs = [c['content'] for c in conversations if c.get('role') == 'assistant'][-5:]
        
        task_patterns = [
            r'(开发 | 创建 | 实现 | 编写 | 重构 | 改造 | 修复 | 优化).*?(系统 | 模块 | 功能 | 服务)',
            r'(完成 | 搞定 | 结束).*?(任务 | 工作 | 开发)',
        ]
        
        for msg in reversed(assistant_msgs):
            for pattern in task_patterns:
                match = re.search(pattern, msg)
                if match:
                    return match.group(0)
        
        return ""
    
    def _append_to_daily_memory(self, snapshot: Dict):
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            memory_file = self.memory_dir / f"{today}.md"
            
            if memory_file.exists():
                with open(memory_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = f"# {today} 记忆日志\n\n"
            
            save_time = datetime.fromisoformat(snapshot['saved_at']).strftime('%H:%M')
            if f"**自动保存** ({save_time})" in content:
                return
            
            summary = snapshot.get('semantic_summary', '')
            task = snapshot['context'].get('current_task', '')
            
            entry = f"\n## {save_time}\n\n"
            entry += f"**自动保存** - 会话快照\n\n"
            if task:
                entry += f"- 当前任务：{task}\n"
            if summary:
                entry += f"- 内容摘要：{summary[:200]}...\n"
            entry += f"- 对话轮数：{snapshot['session']['total_rounds']}\n"
            
            with open(memory_file, 'a', encoding='utf-8') as f:
                f.write(entry)
            
            self.logger.debug(f"追加到每日记忆：{memory_file}")
        
        except Exception as e:
            self.logger.warn(f"写入每日记忆失败：{e}")
    
    def _calculate_duration(self) -> int:
        try:
            started = datetime.fromisoformat(self.session_state.get("started_at", ""))
            return int((datetime.now() - started).total_seconds() / 60)
        except Exception:
            return 0
    
    def load(self) -> Optional[Dict]:
        """加载上次保存的快照"""
        if not self.snapshot_file.exists():
            self.logger.debug("没有找到快照文件")
            return None
        
        try:
            with open(self.snapshot_file, 'r', encoding='utf-8') as f:
                snapshot = json.load(f)
            
            conversations = snapshot.get("conversations", [])
            for msg in conversations:
                self.buffer.add_message(
                    msg.get("role", ""),
                    msg.get("content", ""),
                    msg.get("metadata", {})
                )
            
            session = snapshot.get("session", {})
            context = snapshot.get("context", {})
            
            self.session_state.update({
                "started_at": session.get("started_at"),
                "total_messages": session.get("total_messages", 0),
                "total_rounds": session.get("total_rounds", 0),
                "current_task": context.get("current_task", ""),
                "project": context.get("project", ""),
                "tags": context.get("tags", []),
                "has_unfinished_work": context.get("has_unfinished_work", False)
            })
            
            self.logger.info(f"已加载会话快照：{snapshot.get('saved_at', 'unknown')}")
            return snapshot
        
        except Exception as e:
            self.logger.error(f"加载快照失败：{e}")
            return None
    
    def get_status(self) -> Dict:
        """获取当前状态"""
        return {
            "is_running": self._auto_save_thread is not None and self._auto_save_thread.is_alive(),
            "auto_save_interval": self.auto_save_interval,
            "snapshot_file": str(self.snapshot_file),
            "buffer_size": len(self.buffer.buffer),
            "session_state": self.session_state
        }
    
    def export_to_markdown(self, output_file: Optional[Path] = None) -> Path:
        """导出会话为 Markdown 格式"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.snapshots_dir / f"session_{timestamp}.md"
        
        conversations = self.buffer.get_all()
        
        lines = [
            "# 会话记录",
            "",
            f"**保存时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**对话轮数**: {self.buffer.get_rounds_count()}",
            f"**当前任务**: {self.session_state.get('current_task', '无')}",
            "",
            "---",
            ""
        ]
        
        for msg in conversations:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")
            
            if role == "user":
                lines.append(f"## 👤 用户 ({timestamp})")
            elif role == "assistant":
                lines.append(f"## 🤖 助手 ({timestamp})")
            else:
                lines.append(f"## {role} ({timestamp})")
            
            lines.append("")
            lines.append(content)
            lines.append("")
            lines.append("---")
            lines.append("")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        self.logger.info(f"已导出到：{output_file}")
        return output_file


# ============================================================================
# 全局实例（单例模式）
# ============================================================================

_saver_instance: Optional[RealTimeSaver] = None


def get_saver(snapshot_file: Optional[Path] = None,
              workspace: Optional[Path] = None) -> RealTimeSaver:
    """获取全局保存器实例"""
    global _saver_instance
    if _saver_instance is None:
        _saver_instance = RealTimeSaver(
            snapshot_file=snapshot_file,
            workspace=workspace
        )
    return _saver_instance


def init_service(snapshot_file: Optional[Path] = None,
                 workspace: Optional[Path] = None,
                 auto_start: bool = True) -> RealTimeSaver:
    """初始化实时保存服务"""
    saver = get_saver(snapshot_file, workspace)
    saver.load()
    if auto_start:
        saver.start()
    return saver


def record_user_message(content: str, metadata: Optional[Dict] = None):
    """记录用户消息"""
    saver = get_saver()
    saver.record_message("user", content, metadata)


def record_assistant_message(content: str, metadata: Optional[Dict] = None):
    """记录助手消息"""
    saver = get_saver()
    saver.record_message("assistant", content, metadata)


def update_task(task: str):
    """更新当前任务"""
    saver = get_saver()
    saver.update_context(current_task=task)


def update_project(project: str):
    """更新当前项目"""
    saver = get_saver()
    saver.update_context(project=project)


def manual_save() -> Dict:
    """手动触发保存"""
    saver = get_saver()
    return saver.save(force=True)


def get_session_summary() -> str:
    """获取当前会话摘要"""
    saver = get_saver()
    conversations = saver.buffer.get_all()
    return saver.summarizer.generate_summary(conversations)


# ============================================================================
# 命令行接口
# ============================================================================

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Memory Suite v3 - 实时保存模块")
    parser.add_argument("action", 
                       choices=["start", "stop", "save", "load", "status", "export"],
                       help="执行的操作")
    parser.add_argument("--file", "-f", 
                       help="快照文件路径",
                       default=str(DEFAULT_SNAPSHOT_FILE))
    parser.add_argument("--interval", "-i",
                       type=int,
                       default=AUTO_SAVE_INTERVAL,
                       help=f"自动保存间隔（秒），默认{AUTO_SAVE_INTERVAL}")
    parser.add_argument("--workspace", "-w",
                       help="工作空间路径",
                       default=str(DEFAULT_WORKSPACE))
    
    args = parser.parse_args()
    
    snapshot_file = Path(args.file)
    workspace = Path(args.workspace)
    
    if args.action == "start":
        saver = init_service(snapshot_file, workspace, auto_start=True)
        print(f"服务已启动，按 Ctrl+C 停止")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            saver.stop()
    
    elif args.action == "stop":
        saver = get_saver(snapshot_file, workspace)
        saver.stop()
    
    elif args.action == "save":
        saver = get_saver(snapshot_file, workspace)
        result = saver.save(force=True)
        print(f"✅ 已保存到：{snapshot_file}")
        print(f"📊 摘要：{result.get('semantic_summary', 'N/A')}")
    
    elif args.action == "load":
        saver = get_saver(snapshot_file, workspace)
        result = saver.load()
        if result:
            print(f"✅ 加载成功")
            print(f"📊 摘要：{result.get('semantic_summary', 'N/A')}")
        else:
            print("⚠️ 没有找到快照文件")
    
    elif args.action == "status":
        saver = get_saver(snapshot_file, workspace)
        status = saver.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    
    elif args.action == "export":
        saver = get_saver(snapshot_file, workspace)
        output = saver.export_to_markdown()
        print(f"✅ 已导出到：{output}")


if __name__ == "__main__":
    main()
