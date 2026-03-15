#!/usr/bin/env python3
"""
Memory Service - 实时保存模块
Real-time Session Saver

功能：
1. 每10分钟自动保存完整会话状态
2. 保存最后50轮对话摘要
3. 生成语义摘要（使用简单关键词提取）
4. 保存到 memory/snapshots/current_session.json

作者: Alpha Agent (Builder)
版本: 1.0.0
"""

import json
import re
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# 工作空间路径
WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
SNAPSHOTS_DIR = MEMORY_DIR / "snapshots"
SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# OpenClaw 会话存储路径
OPENCLAW_SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"

# 默认保存路径
DEFAULT_SNAPSHOT_FILE = SNAPSHOTS_DIR / "current_session.json"

# 配置常量
MAX_CONVERSATION_ROUNDS = 50  # 保存最近50轮对话
AUTO_SAVE_INTERVAL = 600  # 10分钟 = 600秒


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
        """
        从文本中提取关键词
        
        Args:
            text: 输入文本
            top_n: 返回前N个关键词
            
        Returns:
            关键词列表
        """
        if not text:
            return []
        
        # 清理文本
        text = self._clean_text(text)
        
        # 分词（简单实现：按字符和空格分割）
        words = self._tokenize(text)
        
        # 统计词频
        word_freq = {}
        for word in words:
            word_lower = word.lower()
            if word_lower in self.STOP_WORDS:
                continue
            if len(word) < 2:
                continue
            
            # 基础权重
            weight = 1.0
            
            # 项目关键词加权
            for kw, kw_weight in self.PROJECT_KEYWORDS.items():
                if kw in word or word in kw:
                    weight *= kw_weight
                    break
            
            # 长度加权（中等长度词更重要）
            if 4 <= len(word) <= 8:
                weight *= 1.2
            
            word_freq[word] = word_freq.get(word, 0) + weight
        
        # 按频率排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, freq in sorted_words[:top_n]]
    
    def generate_summary(self, conversations: List[Dict], max_length: int = 200) -> str:
        """
        生成对话摘要
        
        Args:
            conversations: 对话列表
            max_length: 摘要最大长度
            
        Returns:
            摘要文本
        """
        # 合并所有对话内容
        all_text = " ".join([
            f"{c.get('role', '')}: {c.get('content', '')}"
            for c in conversations[-20:]  # 只取最近20轮
        ])
        
        # 提取关键词
        keywords = self.extract_keywords(all_text, top_n=15)
        
        # 生成摘要
        summary_parts = []
        
        # 1. 主题识别
        topic = self._identify_topic(keywords)
        if topic:
            summary_parts.append(f"主题: {topic}")
        
        # 2. 关键词
        if keywords:
            summary_parts.append(f"关键词: {', '.join(keywords[:8])}")
        
        # 3. 动作识别
        actions = self._extract_actions(conversations)
        if actions:
            summary_parts.append(f"主要动作: {'; '.join(actions[:3])}")
        
        summary = " | ".join(summary_parts)
        
        # 截断到最大长度
        if len(summary) > max_length:
            summary = summary[:max_length - 3] + "..."
        
        return summary
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除URL
        text = re.sub(r'http[s]?://\S+', ' ', text)
        # 移除特殊字符，保留中英文和数字
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', ' ', text)
        # 合并多余空格
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _tokenize(self, text: str) -> List[str]:
        """简单分词"""
        words = []
        
        # 按空格分割（英文）
        for part in text.split():
            # 英文单词
            if re.match(r'^[a-zA-Z]+$', part):
                words.append(part.lower())
            # 中文：逐字和按2-4字词组
            else:
                chars = list(part)
                words.extend(chars)
                # 提取2-4字词组
                for n in [4, 3, 2]:
                    for i in range(len(chars) - n + 1):
                        words.append(''.join(chars[i:i+n]))
        
        return words
    
    def _identify_topic(self, keywords: List[str]) -> Optional[str]:
        """识别主题"""
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
        """提取主要动作"""
        action_patterns = [
            r'(创建|开发|实现|编写|生成|计算|分析|筛选|导出|导入|修改|更新|删除|添加)',
            r'(create|develop|implement|write|generate|calculate|analyze|export|import|update|delete|add)'
        ]
        
        actions = []
        for conv in conversations[-10:]:  # 最近10轮
            content = conv.get('content', '')
            for pattern in action_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                actions.extend(matches)
        
        # 去重并保持顺序
        seen = set()
        unique_actions = []
        for action in actions:
            if action not in seen:
                seen.add(action)
                unique_actions.append(action)
        
        return unique_actions[:5]


class ConversationBuffer:
    """
    对话缓冲区 - 管理最近N轮对话
    """
    
    def __init__(self, max_rounds: int = MAX_CONVERSATION_ROUNDS):
        self.max_rounds = max_rounds
        self.buffer: deque = deque(maxlen=max_rounds * 2)  # *2 因为每轮包含用户和助手
        self.lock = threading.Lock()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        添加一条消息
        
        Args:
            role: 角色 (user/assistant/system)
            content: 消息内容
            metadata: 可选的元数据
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        with self.lock:
            self.buffer.append(message)
    
    def get_recent(self, n: int = 10) -> List[Dict]:
        """获取最近N条消息"""
        with self.lock:
            return list(self.buffer)[-n:]
    
    def get_all(self) -> List[Dict]:
        """获取所有消息"""
        with self.lock:
            return list(self.buffer)
    
    def clear(self):
        """清空缓冲区"""
        with self.lock:
            self.buffer.clear()
    
    def get_rounds_count(self) -> int:
        """获取对话轮数"""
        with self.lock:
            # 简单估算：每轮包含用户和助手两条消息
            return len(self.buffer) // 2


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
                 max_rounds: int = MAX_CONVERSATION_ROUNDS):
        """
        初始化实时保存器
        
        Args:
            snapshot_file: 快照文件路径，默认 memory/snapshots/current_session.json
            auto_save_interval: 自动保存间隔（秒），默认600秒（10分钟）
            max_rounds: 保存的最大对话轮数，默认50轮
        """
        self.snapshot_file = snapshot_file or DEFAULT_SNAPSHOT_FILE
        self.auto_save_interval = auto_save_interval
        self.max_rounds = max_rounds
        
        # 组件初始化
        self.buffer = ConversationBuffer(max_rounds)
        self.summarizer = SemanticSummarizer()
        
        # 会话状态
        self.session_state: Dict[str, Any] = {
            "started_at": datetime.now().isoformat(),
            "last_saved_at": None,
            "total_messages": 0,
            "total_rounds": 0,
            "current_task": "",
            "project": "",
            "tags": []
        }
        
        # 自动保存线程
        self._auto_save_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        
        # 确保目录存在
        self.snapshot_file.parent.mkdir(parents=True, exist_ok=True)
    
    def start(self):
        """启动自动保存服务"""
        if self._auto_save_thread is not None and self._auto_save_thread.is_alive():
            print("⚠️ 自动保存服务已在运行")
            return
        
        self._stop_event.clear()
        self._auto_save_thread = threading.Thread(
            target=self._auto_save_loop,
            daemon=True,
            name="RealTimeSaver"
        )
        self._auto_save_thread.start()
        print(f"✅ 实时保存服务已启动（每{self.auto_save_interval}秒自动保存）")
    
    def stop(self):
        """停止自动保存服务"""
        self._stop_event.set()
        if self._auto_save_thread and self._auto_save_thread.is_alive():
            self._auto_save_thread.join(timeout=5)
            print("✅ 实时保存服务已停止")
    
    def _auto_save_loop(self):
        """自动保存循环"""
        while not self._stop_event.is_set():
            # 等待指定间隔
            self._stop_event.wait(self.auto_save_interval)
            
            if not self._stop_event.is_set():
                try:
                    self.save(force=True)
                    print(f"💾 自动保存完成: {datetime.now().strftime('%H:%M:%S')}")
                except Exception as e:
                    print(f"❌ 自动保存失败: {e}")
    
    def record_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        记录一条消息
        
        Args:
            role: 角色 (user/assistant/system)
            content: 消息内容
            metadata: 可选的元数据
        """
        self.buffer.add_message(role, content, metadata)
        
        with self._lock:
            self.session_state["total_messages"] += 1
            self.session_state["total_rounds"] = self.buffer.get_rounds_count()
    
    def update_context(self, **kwargs):
        """更新会话上下文"""
        with self._lock:
            self.session_state.update(kwargs)
    
    def _load_openclaw_session(self) -> Dict:
        """从 OpenClaw 会话存储加载数据"""
        try:
            # 读取 sessions.json 找到当前会话
            sessions_file = OPENCLAW_SESSIONS_DIR / "sessions.json"
            if not sessions_file.exists():
                return {}
                
            sessions = json.loads(sessions_file.read_text(encoding='utf-8'))
            
            # 找到最新的主会话 (agent:main:main)
            latest_session = None
            latest_time = 0
            
            for key, session in sessions.items():
                # 优先找主会话，其次是任何活跃会话
                if key == 'agent:main:main':
                    latest_time = session.get('updatedAt', 0)
                    latest_session = session
                    break
                elif 'direct' in key and session.get('updatedAt', 0) > latest_time:
                    latest_time = session.get('updatedAt', 0)
                    latest_session = session
                    
            if not latest_session:
                return {}
                
            # 读取会话历史文件
            session_file = latest_session.get('sessionFile')
            if session_file and Path(session_file).exists():
                lines = Path(session_file).read_text(encoding='utf-8').strip().split('\n')
                
                # 解析最后20条消息
                conversations = []
                for line in lines[-40:]:  # 最近40行
                    try:
                        msg = json.loads(line)
                        # OpenClaw 格式: {"type":"message","message":{"role":"...","content":"..."}}
                        if msg.get('type') == 'message':
                            message_data = msg.get('message', {})
                            content_data = message_data.get('content', [])
                            
                            # 提取文本内容
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
                                    'content': text_content[:500],  # 限制长度
                                    'timestamp': msg.get('timestamp', datetime.now().isoformat())
                                })
                    except Exception as e:
                        continue
                        
                return {
                    'conversations': conversations,
                    'session_key': latest_session.get('sessionKey', ''),
                    'updated_at': latest_time
                }
                
        except Exception as e:
            print(f"⚠️ 读取 OpenClaw 会话失败: {e}")
            
        return {}
    
    def save(self, force: bool = False) -> Dict:
        """
        保存当前会话状态
        
        Args:
            force: 是否强制保存（忽略检查）
            
        Returns:
            保存的状态字典
        """
        with self._lock:
            # 从 OpenClaw 加载会话数据
            openclaw_data = self._load_openclaw_session()
            
            # 合并对话数据
            conversations = openclaw_data.get('conversations', [])
            if not conversations:
                conversations = self.buffer.get_all()
            
            # 生成语义摘要
            semantic_summary = self.summarizer.generate_summary(
                conversations, 
                max_length=300
            ) if conversations else "无对话记录"
            
            # 提取关键词
            all_text = " ".join([c.get("content", "") for c in conversations])
            keywords = self.summarizer.extract_keywords(all_text, top_n=20) if all_text else []
            
            # 推断当前任务（从对话内容）
            current_task = self._infer_task(conversations)
            
            # 构建快照数据
            snapshot = {
                "version": "1.1.0",
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
                "conversations": conversations[-self.max_rounds:]  # 限制数量
            }
            
            # 保存到文件
            with open(self.snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, ensure_ascii=False, indent=2)
            
            # 同时追加到每日记忆文件
            self._append_to_daily_memory(snapshot)
            
            return snapshot
    
    def _infer_task(self, conversations: List[Dict]) -> str:
        """从对话内容推断当前任务"""
        if not conversations:
            return ""
            
        # 取最近5条助手回复
        assistant_msgs = [c['content'] for c in conversations if c.get('role') == 'assistant'][-5:]
        
        # 提取任务关键词
        task_patterns = [
            r'(开发|创建|实现|编写|重构|改造|修复|优化).*?(系统|模块|功能|服务)',
            r'(完成|搞定|结束).*?(任务|工作|开发)',
        ]
        
        for msg in reversed(assistant_msgs):
            for pattern in task_patterns:
                match = re.search(pattern, msg)
                if match:
                    return match.group(0)
                    
        return ""
    
    def _append_to_daily_memory(self, snapshot: Dict):
        """追加到每日记忆文件"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            memory_file = MEMORY_DIR / f"{today}.md"
            
            # 读取现有内容
            if memory_file.exists():
                content = memory_file.read_text(encoding='utf-8')
            else:
                content = f"# {today} 记忆日志\n\n"
            
            # 检查是否已经记录了这次保存
            save_time = datetime.fromisoformat(snapshot['saved_at']).strftime('%H:%M')
            if f"**自动保存** ({save_time})" in content:
                return  # 已记录，跳过
            
            # 生成记忆条目
            summary = snapshot.get('semantic_summary', '')
            task = snapshot['context'].get('current_task', '')
            
            entry = f"\n## {save_time}\n\n"
            entry += f"**自动保存** - 会话快照\n\n"
            if task:
                entry += f"- 当前任务: {task}\n"
            if summary:
                entry += f"- 内容摘要: {summary[:200]}...\n"
            entry += f"- 对话轮数: {snapshot['session']['total_rounds']}\n"
            
            # 写入文件
            memory_file.write_text(content + entry, encoding='utf-8')
            
        except Exception as e:
            print(f"⚠️ 写入每日记忆失败: {e}")
            
            # 更新状态
            self.session_state["last_saved_at"] = datetime.now().isoformat()
            
            return snapshot
    
    def _calculate_duration(self) -> int:
        """计算会话持续时间（分钟）"""
        try:
            started = datetime.fromisoformat(self.session_state.get("started_at", ""))
            return int((datetime.now() - started).total_seconds() / 60)
        except:
            return 0
    
    def load(self) -> Optional[Dict]:
        """
        加载上次保存的快照
        
        Returns:
            快照数据字典，如果不存在则返回None
        """
        if not self.snapshot_file.exists():
            return None
        
        try:
            with open(self.snapshot_file, 'r', encoding='utf-8') as f:
                snapshot = json.load(f)
            
            # 恢复对话到缓冲区
            conversations = snapshot.get("conversations", [])
            for msg in conversations:
                self.buffer.add_message(
                    msg.get("role", ""),
                    msg.get("content", ""),
                    msg.get("metadata", {})
                )
            
            # 恢复会话状态
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
            
            print(f"✅ 已加载会话快照: {snapshot.get('saved_at', 'unknown')}")
            return snapshot
            
        except Exception as e:
            print(f"❌ 加载快照失败: {e}")
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
        """
        导出会话为Markdown格式
        
        Args:
            output_file: 输出文件路径，默认 memory/snapshots/session_YYYYMMDD_HHMMSS.md
            
        Returns:
            输出文件路径
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = SNAPSHOTS_DIR / f"session_{timestamp}.md"
        
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
        
        print(f"📝 已导出到: {output_file}")
        return output_file


# 全局实例（单例模式）
_saver_instance: Optional[RealTimeSaver] = None


def get_saver(snapshot_file: Optional[Path] = None) -> RealTimeSaver:
    """获取全局保存器实例"""
    global _saver_instance
    if _saver_instance is None:
        _saver_instance = RealTimeSaver(snapshot_file=snapshot_file)
    return _saver_instance


def init_service(snapshot_file: Optional[Path] = None, 
                 auto_start: bool = True) -> RealTimeSaver:
    """
    初始化实时保存服务
    
    Args:
        snapshot_file: 快照文件路径
        auto_start: 是否自动启动自动保存
        
    Returns:
        RealTimeSaver实例
    """
    saver = get_saver(snapshot_file)
    
    # 尝试加载之前的会话
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


# 命令行接口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Memory Service - 实时保存模块")
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
    
    args = parser.parse_args()
    
    snapshot_file = Path(args.file)
    
    if args.action == "start":
        saver = init_service(snapshot_file, auto_start=True)
        print(f"服务已启动，按 Ctrl+C 停止")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            saver.stop()
    
    elif args.action == "stop":
        saver = get_saver(snapshot_file)
        saver.stop()
    
    elif args.action == "save":
        saver = get_saver(snapshot_file)
        result = saver.save(force=True)
        print(f"✅ 已保存到: {snapshot_file}")
        print(f"📊 摘要: {result.get('semantic_summary', 'N/A')}")
    
    elif args.action == "load":
        saver = get_saver(snapshot_file)
        result = saver.load()
        if result:
            print(f"✅ 加载成功")
            print(f"📊 摘要: {result.get('semantic_summary', 'N/A')}")
        else:
            print("⚠️ 没有找到快照文件")
    
    elif args.action == "status":
        saver = get_saver(snapshot_file)
        status = saver.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    
    elif args.action == "export":
        saver = get_saver(snapshot_file)
        output = saver.export_to_markdown()
        print(f"✅ 已导出到: {output}")
