#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notify Service - 统一通知模块

功能：
1. 统一通知格式
2. 分级发送（urgent/normal/low）
3. 批量合并短时间内的通知
4. 发送到飞书

Author: Juliet Agent (Builder)
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict, Callable, Any, Union
from collections import defaultdict
import aiohttp


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotifyLevel(Enum):
    """通知级别"""
    URGENT = "urgent"      # 紧急 - 立即发送
    NORMAL = "normal"      # 普通 - 正常发送
    LOW = "low"            # 低优先级 - 可批量合并


class NotifyStatus(Enum):
    """通知状态"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    MERGED = "merged"


@dataclass
class NotifyMessage:
    """通知消息数据类"""
    id: str
    title: str
    content: str
    level: NotifyLevel
    category: str = "default"
    target: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    status: NotifyStatus = NotifyStatus.PENDING
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "level": self.level.value,
            "category": self.category,
            "target": self.target,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "status": self.status.value,
            "retry_count": self.retry_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NotifyMessage":
        """从字典创建"""
        return cls(
            id=data["id"],
            title=data["title"],
            content=data["content"],
            level=NotifyLevel(data.get("level", "normal")),
            category=data.get("category", "default"),
            target=data.get("target", ""),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", time.time()),
            status=NotifyStatus(data.get("status", "pending")),
            retry_count=data.get("retry_count", 0)
        )


@dataclass
class NotifyConfig:
    """通知配置"""
    # 飞书配置
    feishu_webhook: Optional[str] = None
    feishu_app_id: Optional[str] = None
    feishu_app_secret: Optional[str] = None
    
    # 批量合并配置
    batch_interval: int = 30  # 批量合并时间窗口（秒）
    max_batch_size: int = 10  # 最大批量大小
    
    # 重试配置
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # 级别配置
    urgent_timeout: float = 0.0      # 紧急通知立即发送
    normal_timeout: float = 5.0      # 普通通知5秒内发送
    low_timeout: float = 30.0        # 低优先级通知30秒内发送


class NotifyService:
    """
    统一通知服务
    
    支持：
    - 统一通知格式管理
    - 分级发送（urgent/normal/low）
    - 批量合并短时间内的通知
    - 飞书消息推送
    """
    
    def __init__(self, config: Optional[NotifyConfig] = None):
        self.config = config or NotifyConfig()
        
        # 消息队列
        self._pending_messages: List[NotifyMessage] = []
        self._message_history: List[NotifyMessage] = []
        self._history_limit = 1000
        
        # 批量合并队列
        self._batch_queues: Dict[str, List[NotifyMessage]] = defaultdict(list)
        self._batch_timers: Dict[str, Optional[asyncio.Task]] = {}
        
        # 处理器注册
        self._handlers: Dict[str, Callable[[NotifyMessage], Any]] = {}
        
        # 统计
        self._stats = {
            "total_sent": 0,
            "total_failed": 0,
            "total_merged": 0,
            "by_level": defaultdict(int)
        }
        
        # 运行状态
        self._running = False
        self._main_loop_task: Optional[asyncio.Task] = None
        
        logger.info("NotifyService initialized")
    
    # ==================== 核心 API ====================
    
    async def start(self):
        """启动通知服务"""
        if self._running:
            return
        
        self._running = True
        self._main_loop_task = asyncio.create_task(self._main_loop())
        logger.info("NotifyService started")
    
    async def stop(self):
        """停止通知服务"""
        self._running = False
        
        # 取消所有批量定时器
        for timer in self._batch_timers.values():
            if timer and not timer.done():
                timer.cancel()
        
        # 取消主循环
        if self._main_loop_task:
            self._main_loop_task.cancel()
            try:
                await self._main_loop_task
            except asyncio.CancelledError:
                pass
        
        # 刷新剩余消息
        await self._flush_all_batches()
        
        logger.info("NotifyService stopped")
    
    async def send(self, 
                   title: str, 
                   content: str, 
                   level: Union[NotifyLevel, str] = NotifyLevel.NORMAL,
                   category: str = "default",
                   target: str = "",
                   metadata: Optional[Dict[str, Any]] = None) -> NotifyMessage:
        """
        发送通知
        
        Args:
            title: 通知标题
            content: 通知内容
            level: 通知级别 (urgent/normal/low)
            category: 通知分类
            target: 目标接收者
            metadata: 附加元数据
        
        Returns:
            NotifyMessage: 创建的消息对象
        """
        # 统一级别格式
        if isinstance(level, str):
            level = NotifyLevel(level)
        
        # 创建消息
        msg = NotifyMessage(
            id=self._generate_id(),
            title=title,
            content=content,
            level=level,
            category=category,
            target=target,
            metadata=metadata or {}
        )
        
        # 根据级别处理
        if level == NotifyLevel.URGENT:
            # 紧急通知立即发送
            await self._send_immediately(msg)
        elif level == NotifyLevel.NORMAL:
            # 普通通知加入队列，短时间内批量
            await self._add_to_batch(msg)
        else:
            # 低优先级加入批量队列
            await self._add_to_batch(msg)
        
        return msg
    
    async def send_urgent(self, title: str, content: str, **kwargs) -> NotifyMessage:
        """发送紧急通知"""
        return await self.send(title, content, level=NotifyLevel.URGENT, **kwargs)
    
    async def send_normal(self, title: str, content: str, **kwargs) -> NotifyMessage:
        """发送普通通知"""
        return await self.send(title, content, level=NotifyLevel.NORMAL, **kwargs)
    
    async def send_low(self, title: str, content: str, **kwargs) -> NotifyMessage:
        """发送低优先级通知"""
        return await self.send(title, content, level=NotifyLevel.LOW, **kwargs)
    
    # ==================== 批量合并逻辑 ====================
    
    async def _add_to_batch(self, msg: NotifyMessage):
        """添加到批量队列"""
        batch_key = f"{msg.category}:{msg.target}"
        self._batch_queues[batch_key].append(msg)
        
        # 启动或重置定时器
        if batch_key in self._batch_timers and self._batch_timers[batch_key]:
            self._batch_timers[batch_key].cancel()
        
        # 根据级别设置超时
        if msg.level == NotifyLevel.NORMAL:
            timeout = self.config.normal_timeout
        else:
            timeout = self.config.low_timeout
        
        self._batch_timers[batch_key] = asyncio.create_task(
            self._batch_timer(batch_key, timeout)
        )
        
        # 检查是否达到批量上限
        if len(self._batch_queues[batch_key]) >= self.config.max_batch_size:
            await self._flush_batch(batch_key)
    
    async def _batch_timer(self, batch_key: str, timeout: float):
        """批量定时器"""
        await asyncio.sleep(timeout)
        await self._flush_batch(batch_key)
    
    async def _flush_batch(self, batch_key: str):
        """刷新批量队列"""
        if batch_key not in self._batch_queues or not self._batch_queues[batch_key]:
            return
        
        messages = self._batch_queues[batch_key]
        self._batch_queues[batch_key] = []
        
        if len(messages) == 1:
            # 单条消息直接发送
            await self._send_immediately(messages[0])
        else:
            # 多条消息合并发送
            await self._send_batch(messages)
        
        # 清理定时器
        if batch_key in self._batch_timers:
            self._batch_timers[batch_key] = None
    
    async def _flush_all_batches(self):
        """刷新所有批量队列"""
        for batch_key in list(self._batch_queues.keys()):
            await self._flush_batch(batch_key)
    
    # ==================== 发送逻辑 ====================
    
    async def _send_immediately(self, msg: NotifyMessage):
        """立即发送单条消息"""
        try:
            # 发送到飞书
            if self.config.feishu_webhook:
                await self._send_to_feishu(msg)
            
            # 调用注册的处理器
            for handler in self._handlers.values():
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(msg)
                    else:
                        handler(msg)
                except Exception as e:
                    logger.error(f"Handler error: {e}")
            
            msg.status = NotifyStatus.SENT
            self._stats["total_sent"] += 1
            self._stats["by_level"][msg.level.value] += 1
            
        except Exception as e:
            logger.error(f"Send failed: {e}")
            msg.status = NotifyStatus.FAILED
            self._stats["total_failed"] += 1
            
            # 重试逻辑
            if msg.retry_count < self.config.max_retries:
                msg.retry_count += 1
                await asyncio.sleep(self.config.retry_delay * msg.retry_count)
                await self._send_immediately(msg)
        
        finally:
            self._add_to_history(msg)
    
    async def _send_batch(self, messages: List[NotifyMessage]):
        """发送批量消息"""
        if not messages:
            return
        
        # 合并内容
        merged_msg = self._merge_messages(messages)
        
        try:
            # 发送到飞书
            if self.config.feishu_webhook:
                await self._send_batch_to_feishu(messages, merged_msg)
            
            # 更新状态
            for msg in messages:
                msg.status = NotifyStatus.MERGED
                self._stats["total_merged"] += 1
                self._add_to_history(msg)
            
            self._stats["total_sent"] += 1
            
        except Exception as e:
            logger.error(f"Batch send failed: {e}")
            # 批量失败，尝试单独发送
            for msg in messages:
                await self._send_immediately(msg)
    
    def _merge_messages(self, messages: List[NotifyMessage]) -> NotifyMessage:
        """合并多条消息"""
        if len(messages) == 1:
            return messages[0]
        
        # 按级别排序
        levels = [msg.level for msg in messages]
        highest_level = min(levels, key=lambda x: list(NotifyLevel).index(x))
        
        # 合并标题和内容
        titles = [msg.title for msg in messages]
        contents = [f"**{msg.title}**\n{msg.content}" for msg in messages]
        
        merged = NotifyMessage(
            id=self._generate_id(),
            title=f"[{len(messages)}条通知] {titles[0]}{'...' if len(titles) > 1 else ''}",
            content="\n\n---\n\n".join(contents),
            level=highest_level,
            category=messages[0].category,
            target=messages[0].target,
            metadata={
                "merged_count": len(messages),
                "original_ids": [msg.id for msg in messages]
            }
        )
        
        return merged
    
    # ==================== 飞书发送 ====================
    
    async def _send_to_feishu(self, msg: NotifyMessage):
        """发送到飞书（单条）"""
        if not self.config.feishu_webhook:
            return
        
        # 根据级别设置颜色
        color_map = {
            NotifyLevel.URGENT: "red",
            NotifyLevel.NORMAL: "blue",
            NotifyLevel.LOW: "grey"
        }
        
        payload = {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"[{msg.level.value.upper()}] {msg.title}"
                    },
                    "template": color_map.get(msg.level, "blue")
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": msg.content
                        }
                    },
                    {
                        "tag": "note",
                        "elements": [
                            {
                                "tag": "plain_text",
                                "content": f"分类: {msg.category} | 时间: {self._format_time(msg.created_at)}"
                            }
                        ]
                    }
                ]
            }
        }
        
        await self._feishu_request(payload)
    
    async def _send_batch_to_feishu(self, messages: List[NotifyMessage], merged: NotifyMessage):
        """发送到飞书（批量）"""
        if not self.config.feishu_webhook:
            return
        
        # 统计各级别数量
        level_counts = defaultdict(int)
        for msg in messages:
            level_counts[msg.level.value] += 1
        
        level_summary = " | ".join([f"{k}: {v}" for k, v in level_counts.items()])
        
        payload = {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"[批量通知] {len(messages)}条消息"
                    },
                    "template": "orange"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**消息汇总**\n{level_summary}"
                        }
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": merged.content
                        }
                    }
                ]
            }
        }
        
        await self._feishu_request(payload)
    
    async def _feishu_request(self, payload: Dict[str, Any]):
        """飞书 HTTP 请求"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.config.feishu_webhook,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"Feishu API error: {resp.status} - {text}")
                
                result = await resp.json()
                if result.get("code") != 0:
                    raise Exception(f"Feishu API error: {result}")
    
    # ==================== 主循环 ====================
    
    async def _main_loop(self):
        """主循环 - 处理定时任务"""
        while self._running:
            try:
                # 定期刷新所有批量队列
                await self._flush_all_batches()
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                await asyncio.sleep(1)
    
    # ==================== 辅助方法 ====================
    
    def _generate_id(self) -> str:
        """生成唯一ID"""
        return f"{int(time.time() * 1000)}-{id(object())}"
    
    def _format_time(self, timestamp: float) -> str:
        """格式化时间"""
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    
    def _add_to_history(self, msg: NotifyMessage):
        """添加到历史记录"""
        self._message_history.append(msg)
        if len(self._message_history) > self._history_limit:
            self._message_history = self._message_history[-self._history_limit:]
    
    def register_handler(self, name: str, handler: Callable[[NotifyMessage], Any]):
        """注册自定义处理器"""
        self._handlers[name] = handler
        logger.info(f"Handler registered: {name}")
    
    def unregister_handler(self, name: str):
        """注销处理器"""
        if name in self._handlers:
            del self._handlers[name]
            logger.info(f"Handler unregistered: {name}")
    
    # ==================== 查询接口 ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self._stats,
            "pending_count": sum(len(q) for q in self._batch_queues.values()),
            "history_count": len(self._message_history)
        }
    
    def get_history(self, 
                    level: Optional[NotifyLevel] = None,
                    category: Optional[str] = None,
                    limit: int = 100) -> List[NotifyMessage]:
        """获取历史消息"""
        result = self._message_history
        
        if level:
            result = [m for m in result if m.level == level]
        
        if category:
            result = [m for m in result if m.category == category]
        
        return result[-limit:]
    
    def get_pending(self) -> List[NotifyMessage]:
        """获取待发送消息"""
        pending = []
        for queue in self._batch_queues.values():
            pending.extend(queue)
        return pending


# ==================== 便捷函数 ====================

# 全局服务实例
_default_service: Optional[NotifyService] = None


def init_service(config: Optional[NotifyConfig] = None) -> NotifyService:
    """初始化全局通知服务"""
    global _default_service
    _default_service = NotifyService(config)
    return _default_service


def get_service() -> NotifyService:
    """获取全局通知服务"""
    global _default_service
    if _default_service is None:
        _default_service = NotifyService()
    return _default_service


async def send(title: str, 
               content: str, 
               level: Union[NotifyLevel, str] = NotifyLevel.NORMAL,
               **kwargs) -> NotifyMessage:
    """便捷发送函数"""
    return await get_service().send(title, content, level, **kwargs)


async def send_urgent(title: str, content: str, **kwargs) -> NotifyMessage:
    """便捷发送紧急通知"""
    return await get_service().send_urgent(title, content, **kwargs)


async def send_normal(title: str, content: str, **kwargs) -> NotifyMessage:
    """便捷发送普通通知"""
    return await get_service().send_normal(title, content, **kwargs)


async def send_low(title: str, content: str, **kwargs) -> NotifyMessage:
    """便捷发送低优先级通知"""
    return await get_service().send_low(title, content, **kwargs)


# ==================== 示例用法 ====================

async def main():
    """示例用法"""
    # 配置
    config = NotifyConfig(
        feishu_webhook="https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_TOKEN",
        batch_interval=30,
        max_batch_size=10
    )
    
    # 初始化服务
    service = init_service(config)
    await service.start()
    
    # 发送紧急通知（立即发送）
    await service.send_urgent(
        title="系统告警",
        content="CPU使用率超过90%",
        category="monitoring"
    )
    
    # 发送普通通知（可能批量合并）
    await service.send_normal(
        title="任务完成",
        content="数据备份已完成",
        category="task"
    )
    
    # 发送多条低优先级通知（会批量合并）
    for i in range(5):
        await service.send_low(
            title=f"日志记录 #{i+1}",
            content=f"这是第{i+1}条日志消息",
            category="log"
        )
    
    # 等待批量发送
    await asyncio.sleep(5)
    
    # 查看统计
    print("Stats:", json.dumps(service.get_stats(), indent=2))
    
    # 停止服务
    await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
