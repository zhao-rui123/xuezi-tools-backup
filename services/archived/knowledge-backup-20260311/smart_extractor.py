#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Knowledge Service - 智能提取模块 v2.0

功能：
1. 读取昨日记忆文件
2. AI分析识别：决策/问题/项目/学习项
3. 生成知识库草稿到 knowledge-base/pending/
4. 生成学习项到 knowledge-base/learnings/
5. 发送飞书通知（Kilo广播专员）
6. 支持人工确认/拒绝

作者: Delta Agent (Builder) / Lima Agent (增强)
版本: 2.0.0
"""

import os
import re
import json
import hashlib
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class KnowledgeType(Enum):
    """知识类型枚举"""
    DECISION = "decision"      # 决策
    PROBLEM = "problem"        # 问题
    PROJECT = "project"        # 项目
    LEARNING = "learning"      # 学习项
    OPERATION = "operation"    # 运维操作
    REFERENCE = "reference"    # 参考资料
    UNKNOWN = "unknown"        # 未知类型


@dataclass
class ExtractedItem:
    """提取的知识项"""
    id: str
    type: KnowledgeType
    title: str
    content: str
    source: str
    created_at: str
    tags: List[str]
    confidence: float  # 置信度 0-1
    raw_text: str
    suggested_filename: str


@dataclass
class LearningItem:
    """学习项"""
    id: str
    topic: str
    content: str
    source: str
    created_at: str
    priority: str  # high/medium/low
    tags: List[str]
    related_items: List[str]


@dataclass
class PendingReview:
    """待审核项"""
    id: str
    filename: str
    filepath: str
    title: str
    item_type: KnowledgeType
    confidence: float
    status: str  # pending/confirmed/rejected
    created_at: str


class FeishuNotifier:
    """飞书通知器 - 使用Kilo广播专员"""
    
    def __init__(self, workspace_path: str = None):
        self.workspace = Path(workspace_path) if workspace_path else Path.home() / ".openclaw/workspace"
        self.pending_db_path = self.workspace / "knowledge-base" / ".pending_reviews.json"
        
    def _get_confirm_url(self, item_id: str) -> str:
        """生成确认链接（使用本地命令）"""
        return f"openclaw://knowledge/confirm/{item_id}"
    
    def _get_reject_url(self, item_id: str) -> str:
        """生成拒绝链接（使用本地命令）"""
        return f"openclaw://knowledge/reject/{item_id}"
    
    def send_notification(self, items: List[ExtractedItem], draft_files: List[str]) -> bool:
        """
        发送飞书通知
        
        Args:
            items: 提取的知识项列表
            draft_files: 生成的草稿文件列表
            
        Returns:
            是否发送成功
        """
        if not items:
            return False
        
        count = len(items)
        
        # 构建通知消息
        message_lines = [
            "📚 **知识提取完成 - 等待人工确认**",
            "",
            f"🤖 **Kilo广播专员** 为您播报：",
            "",
            f"✨ 发现 **{count}** 个新知识项，请确认：",
            "",
        ]
        
        # 添加每个项目的摘要
        for i, item in enumerate(items[:5], 1):  # 最多显示5个
            type_emoji = {
                KnowledgeType.DECISION: "🎯",
                KnowledgeType.PROBLEM: "🐛",
                KnowledgeType.PROJECT: "📁",
                KnowledgeType.LEARNING: "📖",
                KnowledgeType.OPERATION: "⚙️",
                KnowledgeType.REFERENCE: "📎",
                KnowledgeType.UNKNOWN: "❓"
            }.get(item.type, "📝")
            
            message_lines.append(f"{i}. {type_emoji} **{item.title}** (置信度: {item.confidence:.0%})")
        
        if len(items) > 5:
            message_lines.append(f"   ... 还有 {len(items) - 5} 个")
        
        message_lines.extend([
            "",
            "📂 **生成的草稿文件**：",
        ])
        
        for f in draft_files[:3]:  # 最多显示3个文件
            message_lines.append(f"   • `{Path(f).name}`")
        
        if len(draft_files) > 3:
            message_lines.append(f"   ... 还有 {len(draft_files) - 3} 个")
        
        message_lines.extend([
            "",
            "---",
            "",
            "🎮 **操作命令**：",
            "",
            "**一键确认全部**：",
            "```bash",
            f"python3 services/knowledge/smart_extractor.py --confirm-all",
            "```",
            "",
            "**查看待审核列表**：",
            "```bash",
            f"python3 services/knowledge/smart_extractor.py --list-pending",
            "```",
            "",
            "**逐个确认/拒绝**：",
            "```bash",
            "# 确认指定项目",
            f"python3 services/knowledge/smart_extractor.py --confirm <ID>",
            "",
            "# 拒绝指定项目",
            f"python3 services/knowledge/smart_extractor.py --reject <ID>",
            "```",
            "",
            "---",
            "",
            "⏰ 请在 **24小时内** 完成审核，逾期将自动归档。",
            "",
            "💡 **提示**：确认后的知识项将移动到正式目录，拒绝的项目将被删除。",
        ])
        
        message = "\n".join(message_lines)
        
        # 尝试通过多种方式发送通知
        return self._send_via_openclaw(message) or self._send_via_stdout(message)
    
    def _send_via_openclaw(self, message: str) -> bool:
        """尝试通过OpenClaw message工具发送"""
        try:
            # 保存消息到临时文件，供主Agent读取
            notification_file = self.workspace / "knowledge-base" / ".last_notification.txt"
            with open(notification_file, 'w', encoding='utf-8') as f:
                f.write(message)
            return True
        except Exception as e:
            print(f"[WARN] 保存通知文件失败: {e}")
            return False
    
    def _send_via_stdout(self, message: str) -> bool:
        """通过stdout输出（作为备选）"""
        print("\n" + "=" * 60)
        print("📨 FEISHU NOTIFICATION (Kilo广播专员)")
        print("=" * 60)
        print(message)
        print("=" * 60 + "\n")
        return True
    
    def save_pending_reviews(self, items: List[ExtractedItem], draft_files: List[str]) -> str:
        """
        保存待审核记录到数据库
        
        Returns:
            数据库文件路径
        """
        reviews = []
        timestamp = datetime.now().isoformat()
        
        for item, filepath in zip(items, draft_files):
            review = PendingReview(
                id=item.id,
                filename=Path(filepath).name,
                filepath=filepath,
                title=item.title,
                item_type=item.type,
                confidence=item.confidence,
                status="pending",
                created_at=timestamp
            )
            reviews.append(asdict(review))
        
        # 加载现有数据
        existing = []
        if self.pending_db_path.exists():
            try:
                with open(self.pending_db_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            except Exception:
                existing = []
        
        # 合并并保存
        existing.extend(reviews)
        with open(self.pending_db_path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        
        return str(self.pending_db_path)
    
    def load_pending_reviews(self) -> List[Dict]:
        """加载所有待审核记录"""
        if not self.pending_db_path.exists():
            return []
        
        try:
            with open(self.pending_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] 加载待审核记录失败: {e}")
            return []
    
    def update_review_status(self, item_id: str, status: str) -> Optional[Dict]:
        """
        更新审核状态
        
        Args:
            item_id: 项目ID
            status: 新状态 (confirmed/rejected)
            
        Returns:
            更新后的记录，如果不存在返回None
        """
        reviews = self.load_pending_reviews()
        
        for review in reviews:
            if review['id'] == item_id:
                review['status'] = status
                review['reviewed_at'] = datetime.now().isoformat()
                
                # 保存回文件
                with open(self.pending_db_path, 'w', encoding='utf-8') as f:
                    json.dump(reviews, f, ensure_ascii=False, indent=2)
                
                return review
        
        return None
    
    def confirm_item(self, item_id: str, extractor) -> Tuple[bool, str]:
        """
        确认知识项
        
        Args:
            item_id: 项目ID或"all"
            extractor: SmartExtractor实例
            
        Returns:
            (是否成功, 消息)
        """
        if item_id == "all":
            return self._confirm_all(extractor)
        
        review = self.update_review_status(item_id, "confirmed")
        if not review:
            return False, f"❌ 未找到ID为 {item_id} 的待审核项"
        
        # 移动文件到正式目录
        src_path = Path(review['filepath'])
        if not src_path.exists():
            return False, f"❌ 草稿文件不存在: {src_path}"
        
        # 确定目标目录
        type_dir = extractor.kb_dir / review['item_type']
        if not type_dir.exists():
            type_dir = extractor.kb_dir / "decisions"  # 默认目录
        
        # 移动文件
        dest_path = type_dir / review['filename']
        counter = 1
        original_dest = dest_path
        while dest_path.exists():
            stem = original_dest.stem
            dest_path = original_dest.with_name(f"{stem}_{counter}{original_dest.suffix}")
            counter += 1
        
        try:
            import shutil
            shutil.move(str(src_path), str(dest_path))
            
            # 更新文件中的状态
            with open(dest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace("🟡 待审核", "✅ 已确认")
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, f"✅ 已确认: {review['title']}\n   已移动到: {dest_path}"
        except Exception as e:
            return False, f"❌ 移动文件失败: {e}"
    
    def reject_item(self, item_id: str) -> Tuple[bool, str]:
        """
        拒绝知识项
        
        Args:
            item_id: 项目ID
            
        Returns:
            (是否成功, 消息)
        """
        review = self.update_review_status(item_id, "rejected")
        if not review:
            return False, f"❌ 未找到ID为 {item_id} 的待审核项"
        
        # 删除草稿文件
        src_path = Path(review['filepath'])
        if src_path.exists():
            try:
                src_path.unlink()
            except Exception as e:
                return False, f"❌ 删除草稿文件失败: {e}"
        
        return True, f"🗑️ 已拒绝并删除: {review['title']}"
    
    def _confirm_all(self, extractor) -> Tuple[bool, str]:
        """确认所有待审核项"""
        reviews = self.load_pending_reviews()
        pending = [r for r in reviews if r['status'] == 'pending']
        
        if not pending:
            return True, "📭 没有待审核的项目"
        
        success_count = 0
        fail_count = 0
        messages = []
        
        for review in pending:
            success, msg = self.confirm_item(review['id'], extractor)
            if success:
                success_count += 1
            else:
                fail_count += 1
            messages.append(msg)
        
        summary = f"📊 批量确认完成: {success_count} 成功, {fail_count} 失败"
        return success_count > 0, summary + "\n" + "\n".join(messages)
    
    def get_pending_summary(self) -> str:
        """获取待审核摘要"""
        reviews = self.load_pending_reviews()
        pending = [r for r in reviews if r['status'] == 'pending']
        
        if not pending:
            return "📭 当前没有待审核的知识项"
        
        lines = [
            "📋 **待审核知识项列表**",
            "",
            f"共 {len(pending)} 个项目等待确认：",
            "",
        ]
        
        for i, review in enumerate(pending, 1):
            type_emoji = {
                "decision": "🎯",
                "problem": "🐛",
                "project": "📁",
                "learning": "📖",
                "operation": "⚙️",
                "reference": "📎",
                "unknown": "❓"
            }.get(review['item_type'], "📝")
            
            lines.append(f"{i}. {type_emoji} **{review['title']}**")
            lines.append(f"   ID: `{review['id']}`")
            lines.append(f"   文件: `{review['filename']}`")
            lines.append(f"   置信度: {review['confidence']:.0%}")
            lines.append("")
        
        lines.extend([
            "**快速操作**：",
            "```bash",
            "# 确认全部",
            "python3 services/knowledge/smart_extractor.py --confirm-all",
            "",
            "# 确认单个",
            "python3 services/knowledge/smart_extractor.py --confirm <ID>",
            "",
            "# 拒绝单个",
            "python3 services/knowledge/smart_extractor.py --reject <ID>",
            "```"
        ])
        
        return "\n".join(lines)


class SmartExtractor:
    """智能知识提取器"""
    
    def __init__(self, workspace_path: str = None):
        """初始化提取器"""
        self.workspace = Path(workspace_path) if workspace_path else Path.home() / ".openclaw/workspace"
        self.memory_dir = self.workspace / "memory"
        self.kb_dir = self.workspace / "knowledge-base"
        self.pending_dir = self.kb_dir / "pending"
        self.learnings_dir = self.kb_dir / "learnings"
        
        # 确保目录存在
        self.pending_dir.mkdir(parents=True, exist_ok=True)
        self.learnings_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化通知器
        self.notifier = FeishuNotifier(workspace_path)
        
        # 类型识别关键词
        self.type_keywords = {
            KnowledgeType.DECISION: [
                "决定", "决策", "采用", "选择", "确定", "确定使用", "确定采用",
                "规范", "标准", "策略", "方案", "采纳", "废弃", "改用"
            ],
            KnowledgeType.PROBLEM: [
                "问题", "故障", "错误", "失败", "异常", "bug", "修复",
                "解决", "排查", "报错", "无法", "不能", "卡住"
            ],
            KnowledgeType.PROJECT: [
                "项目", "开发", "功能", "系统", "工具", "模块",
                "新增", "实现", "部署", "上线", "发布"
            ],
            KnowledgeType.LEARNING: [
                "学习", "了解", "掌握", "研究", "探索", "发现",
                "原理", "机制", "概念", "技术", "框架", "算法"
            ],
            KnowledgeType.OPERATION: [
                "操作", "运维", "备份", "恢复", "部署", "配置",
                "命令", "脚本", "步骤", "流程", "检查"
            ],
            KnowledgeType.REFERENCE: [
                "参考", "文档", "API", "配置", "参数", "说明",
                "指南", "手册", "教程", "链接", "资源"
            ]
        }
    
    def get_yesterday_memory_path(self) -> Optional[Path]:
        """获取昨日记忆文件路径"""
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y-%m-%d")
        memory_file = self.memory_dir / f"{date_str}.md"
        
        if memory_file.exists():
            return memory_file
        
        # 尝试查找最近的记忆文件
        memory_files = sorted(self.memory_dir.glob("*.md"), reverse=True)
        for f in memory_files:
            if f.name not in ["MEMORY.md", "README.md"]:
                return f
        
        return None
    
    def read_memory_file(self, file_path: Path) -> str:
        """读取记忆文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"[ERROR] 读取记忆文件失败: {e}")
            return ""
    
    def split_into_sections(self, content: str) -> List[Dict]:
        """将内容分割成段落/章节"""
        sections = []
        
        # 按标题分割 (## 或 ### 开头)
        pattern = r'(?:^|\n)(#{2,4}\s+.+?)(?:\n|$)'
        matches = list(re.finditer(pattern, content))
        
        if not matches:
            # 没有标题，按段落分割
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            for i, para in enumerate(paragraphs):
                sections.append({
                    'title': f'段落_{i+1}',
                    'content': para,
                    'level': 0
                })
        else:
            # 按标题分割
            for i, match in enumerate(matches):
                start = match.start()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
                section_content = content[start:end].strip()
                
                # 提取标题级别
                title_match = re.match(r'^(#{2,4})\s+(.+)$', match.group(1).strip())
                if title_match:
                    level = len(title_match.group(1))
                    title = title_match.group(2).strip()
                else:
                    level = 2
                    title = match.group(1).strip()
                
                sections.append({
                    'title': title,
                    'content': section_content,
                    'level': level
                })
        
        return sections
    
    def classify_content(self, text: str) -> Tuple[KnowledgeType, float, List[str]]:
        """
        基于规则的内容分类
        返回: (类型, 置信度, 标签列表)
        """
        text_lower = text.lower()
        scores = {}
        matched_keywords = []
        
        for ktype, keywords in self.type_keywords.items():
            score = 0
            type_keywords_found = []
            for keyword in keywords:
                count = text_lower.count(keyword.lower())
                if count > 0:
                    score += count
                    type_keywords_found.append(keyword)
            scores[ktype] = score
            if score > 0:
                matched_keywords.extend(type_keywords_found)
        
        # 找到得分最高的类型
        if scores:
            best_type = max(scores, key=scores.get)
            max_score = scores[best_type]
            total_score = sum(scores.values())
            
            # 计算置信度
            if total_score > 0:
                confidence = min(0.5 + (max_score / total_score) * 0.5, 0.95)
            else:
                confidence = 0.3
            
            # 生成标签
            tags = self._generate_tags(text, best_type, matched_keywords)
            
            return best_type, confidence, tags
        
        return KnowledgeType.UNKNOWN, 0.3, ["待分类"]
    
    def _generate_tags(self, text: str, ktype: KnowledgeType, keywords: List[str]) -> List[str]:
        """生成标签"""
        tags = []
        
        # 基础类型标签
        type_tag_map = {
            KnowledgeType.DECISION: "决策",
            KnowledgeType.PROBLEM: "问题",
            KnowledgeType.PROJECT: "项目",
            KnowledgeType.LEARNING: "学习",
            KnowledgeType.OPERATION: "运维",
            KnowledgeType.REFERENCE: "参考"
        }
        tags.append(type_tag_map.get(ktype, "其他"))
        
        # 领域标签识别
        domain_keywords = {
            "储能": ["储能", "电池", "电站", "电价", "充放电"],
            "股票": ["股票", "股市", "行情", "K线", "技术指标", "选股"],
            "OpenClaw": ["OpenClaw", "Agent", "模型", "技能包", "workspace"],
            "飞书": ["飞书", "推送", "消息", "通知"],
            "开发": ["开发", "代码", "Python", "JavaScript", "API"],
            "运维": ["服务器", "部署", "备份", "nginx", "SSH"],
            "AI": ["AI", "模型", "GPT", "Claude", "Kimi", "多Agent"]
        }
        
        for domain, words in domain_keywords.items():
            if any(word in text for word in words):
                tags.append(domain)
        
        # 去重并限制数量
        tags = list(dict.fromkeys(tags))[:5]
        
        return tags
    
    def generate_id(self, text: str) -> str:
        """生成唯一ID"""
        hash_obj = hashlib.md5(text.encode('utf-8'))
        return hash_obj.hexdigest()[:12]
    
    def generate_filename(self, item: ExtractedItem) -> str:
        """生成文件名"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        type_prefix = item.type.value
        
        # 清理标题，用于文件名
        clean_title = re.sub(r'[^\w\u4e00-\u9fff]+', '_', item.title)[:30]
        clean_title = clean_title.strip('_')
        
        return f"{date_str}_{type_prefix}_{clean_title}_{item.id[:6]}.md"
    
    def extract_title(self, section: Dict, ktype: KnowledgeType) -> str:
        """从章节提取标题"""
        base_title = section['title']
        content = section['content']
        
        # 如果是默认段落标题，尝试从内容中提取
        if base_title.startswith('段落_'):
            # 取第一行或前50个字符
            first_line = content.split('\n')[0].strip()
            if len(first_line) > 10:
                return first_line[:50]
            return "未命名内容"
        
        return base_title
    
    def extract_items(self, content: str, source_file: str) -> List[ExtractedItem]:
        """从内容中提取知识项"""
        items = []
        sections = self.split_into_sections(content)
        
        for section in sections:
            section_text = section['content']
            
            # 跳过太短的段落
            if len(section_text) < 50:
                continue
            
            # 分类
            ktype, confidence, tags = self.classify_content(section_text)
            
            # 提取标题
            title = self.extract_title(section, ktype)
            
            # 生成ID
            item_id = self.generate_id(section_text)
            
            # 创建知识项
            item = ExtractedItem(
                id=item_id,
                type=ktype,
                title=title,
                content=section_text,
                source=source_file,
                created_at=datetime.now().isoformat(),
                tags=tags,
                confidence=confidence,
                raw_text=section_text,
                suggested_filename=""
            )
            item.suggested_filename = self.generate_filename(item)
            
            items.append(item)
        
        return items
    
    def generate_knowledge_draft(self, item: ExtractedItem) -> str:
        """生成知识库草稿内容"""
        type_names = {
            KnowledgeType.DECISION: "决策记录",
            KnowledgeType.PROBLEM: "问题记录",
            KnowledgeType.PROJECT: "项目记录",
            KnowledgeType.LEARNING: "学习笔记",
            KnowledgeType.OPERATION: "运维记录",
            KnowledgeType.REFERENCE: "参考资料",
            KnowledgeType.UNKNOWN: "待分类内容"
        }
        
        type_name = type_names.get(item.type, "其他")
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        draft = f"""# {item.title}

**类型**: {type_name}
**来源**: {item.source}
**提取日期**: {date_str}
**置信度**: {item.confidence:.0%}
**标签**: {' '.join([f'#{tag}' for tag in item.tags])}
**状态**: 🟡 待审核
**ID**: `{item.id}`

---

## 内容摘要

{item.content[:500]}{'...' if len(item.content) > 500 else ''}

## 完整内容

{item.content}

---

## 审核操作

```bash
# 确认此知识项
python3 services/knowledge/smart_extractor.py --confirm {item.id}

# 拒绝此知识项
python3 services/knowledge/smart_extractor.py --reject {item.id}
```

## 元数据

- **ID**: {item.id}
- **原始文件**: {item.source}
- **提取时间**: {item.created_at}

## 后续行动

- [ ] 审核内容准确性
- [ ] 补充相关链接
- [ ] 移动到正式目录
- [ ] 更新知识库索引

---
*此文档由智能提取模块自动生成*
"""
        return draft
    
    def generate_learning_item(self, item: ExtractedItem) -> Optional[LearningItem]:
        """从知识项生成学习项（如果是学习类型）"""
        if item.type != KnowledgeType.LEARNING and item.confidence < 0.7:
            return None
        
        # 提取学习主题
        topic = item.title
        
        # 生成学习内容摘要
        content = item.content
        
        # 确定优先级
        priority = "medium"
        if any(word in content for word in ["重要", "核心", "关键", "必须"]):
            priority = "high"
        elif any(word in content for word in ["了解", "知道", "参考"]):
            priority = "low"
        
        learning = LearningItem(
            id=self.generate_id(f"learning_{item.id}"),
            topic=topic,
            content=content[:1000],
            source=item.source,
            created_at=datetime.now().isoformat(),
            priority=priority,
            tags=item.tags,
            related_items=[item.id]
        )
        
        return learning
    
    def save_learning_item(self, learning: LearningItem) -> Path:
        """保存学习项到文件"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}_learning_{learning.id[:6]}.md"
        filepath = self.learnings_dir / filename
        
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        emoji = priority_emoji.get(learning.priority, "🟡")
        
        content = f"""# {emoji} {learning.topic}

**优先级**: {learning.priority.upper()}
**来源**: {learning.source}
**创建日期**: {date_str}
**标签**: {' '.join([f'#{tag}' for tag in learning.tags])}
**状态**: 📝 待学习

---

## 学习内容

{learning.content}

---

## 学习检查清单

- [ ] 阅读并理解内容
- [ ] 记录关键要点
- [ ] 实践/验证（如适用）
- [ ] 更新到个人知识库
- [ ] 标记为已完成

## 相关资源

- 原始文档: {learning.source}
- 相关ID: {', '.join(learning.related_items)}

---
*此学习项由智能提取模块自动生成*
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def process_memory_file(self, memory_path: Optional[Path] = None, dry_run: bool = False) -> Dict:
        """
        处理记忆文件的主流程
        
        Args:
            memory_path: 记忆文件路径
            dry_run: 试运行模式（不保存文件）
            
        Returns:
            处理结果统计
        """
        result = {
            "success": False,
            "source_file": None,
            "items_extracted": 0,
            "drafts_created": 0,
            "learnings_created": 0,
            "draft_files": [],
            "learning_files": [],
            "errors": [],
            "notification_sent": False,
            "pending_db_path": None
        }
        
        # 获取记忆文件
        if memory_path is None:
            memory_path = self.get_yesterday_memory_path()
        
        if not memory_path:
            result["errors"].append("未找到记忆文件")
            return result
        
        result["source_file"] = str(memory_path)
        
        # 读取内容
        content = self.read_memory_file(memory_path)
        if not content:
            result["errors"].append("记忆文件为空或读取失败")
            return result
        
        # 提取知识项
        items = self.extract_items(content, str(memory_path.name))
        result["items_extracted"] = len(items)
        
        if dry_run:
            print("[DRY RUN] 试运行模式，不保存文件")
            result["success"] = True
            return result
        
        # 生成草稿和学习项
        for item in items:
            try:
                # 生成并保存知识库草稿
                draft_content = self.generate_knowledge_draft(item)
                draft_path = self.pending_dir / item.suggested_filename
                
                # 如果文件已存在，添加序号
                counter = 1
                original_path = draft_path
                while draft_path.exists():
                    stem = original_path.stem
                    draft_path = original_path.with_name(f"{stem}_{counter}{original_path.suffix}")
                    counter += 1
                
                with open(draft_path, 'w', encoding='utf-8') as f:
                    f.write(draft_content)
                
                result["drafts_created"] += 1
                result["draft_files"].append(str(draft_path))
                
                # 生成学习项（如果是学习类型或高置信度）
                learning = self.generate_learning_item(item)
                if learning:
                    learning_path = self.save_learning_item(learning)
                    result["learnings_created"] += 1
                    result["learning_files"].append(str(learning_path))
                
            except Exception as e:
                result["errors"].append(f"处理项目 {item.id} 时出错: {e}")
        
        # 保存待审核记录
        if items:
            result["pending_db_path"] = self.notifier.save_pending_reviews(items, result["draft_files"])
        
        # 发送飞书通知
        if items and result["draft_files"]:
            result["notification_sent"] = self.notifier.send_notification(items, result["draft_files"])
        
        result["success"] = len(result["errors"]) == 0
        return result
    
    def get_extraction_report(self, result: Dict) -> str:
        """生成提取报告"""
        lines = [
            "=" * 50,
            "📚 智能知识提取报告",
            "=" * 50,
            "",
            f"📄 源文件: {result.get('source_file', 'N/A')}",
            f"📊 提取项目数: {result.get('items_extracted', 0)}",
            f"📝 生成草稿数: {result.get('drafts_created', 0)}",
            f"🎓 生成学习项: {result.get('learnings_created', 0)}",
            f"📨 通知发送: {'✅' if result.get('notification_sent') else '❌'}",
            "",
            "📁 生成的文件:",
        ]
        
        if result.get('draft_files'):
            lines.append("\n  知识库草稿:")
            for f in result['draft_files']:
                lines.append(f"    - {Path(f).name}")
        
        if result.get('learning_files'):
            lines.append("\n  学习项:")
            for f in result['learning_files']:
                lines.append(f"    - {Path(f).name}")
        
        if result.get('errors'):
            lines.append("\n⚠️  错误:")
            for e in result['errors']:
                lines.append(f"    - {e}")
        
        lines.extend([
            "",
            "=" * 50,
            f"✅ 处理状态: {'成功' if result.get('success') else '部分失败'}",
            "=" * 50
        ])
        
        return '\n'.join(lines)


def main():
    """主函数 - 命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='智能知识提取模块 v2.0 - 支持飞书通知和人工确认',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 提取昨日记忆
  python3 services/knowledge/smart_extractor.py
  
  # 指定记忆文件
  python3 services/knowledge/smart_extractor.py -m memory/2024-01-15.md
  
  # 试运行（不保存文件）
  python3 services/knowledge/smart_extractor.py --dry-run
  
  # 查看待审核列表
  python3 services/knowledge/smart_extractor.py --list-pending
  
  # 确认知识项
  python3 services/knowledge/smart_extractor.py --confirm <ID>
  
  # 确认全部
  python3 services/knowledge/smart_extractor.py --confirm-all
  
  # 拒绝知识项
  python3 services/knowledge/smart_extractor.py --reject <ID>
        """
    )
    
    # 提取相关参数
    parser.add_argument('--workspace', '-w', help='工作空间路径')
    parser.add_argument('--memory', '-m', help='指定记忆文件路径')
    parser.add_argument('--dry-run', '-d', action='store_true', help='试运行模式（不保存文件）')
    parser.add_argument('--report', '-r', action='store_true', help='输出详细报告')
    
    # 确认/拒绝相关参数
    parser.add_argument('--list-pending', '-l', action='store_true', help='列出待审核的知识项')
    parser.add_argument('--confirm', '-c', metavar='ID', help='确认指定ID的知识项')
    parser.add_argument('--confirm-all', '-C', action='store_true', help='确认所有待审核项')
    parser.add_argument('--reject', '-R', metavar='ID', help='拒绝指定ID的知识项')
    
    args = parser.parse_args()
    
    # 创建提取器
    extractor = SmartExtractor(args.workspace)
    
    # 处理确认/拒绝/列表命令
    if args.list_pending:
        summary = extractor.notifier.get_pending_summary()
        print(summary)
        return 0
    
    if args.confirm:
        success, msg = extractor.notifier.confirm_item(args.confirm, extractor)
        print(msg)
        return 0 if success else 1
    
    if args.confirm_all:
        success, msg = extractor.notifier.confirm_item("all", extractor)
        print(msg)
        return 0 if success else 1
    
    if args.reject:
        success, msg = extractor.notifier.reject_item(args.reject)
        print(msg)
        return 0 if success else 1
    
    # 正常提取流程
    # 获取记忆文件
    memory_path = Path(args.memory) if args.memory else None
    
    print("🔍 开始智能知识提取...")
    print(f"📂 工作空间: {extractor.workspace}")
    
    if memory_path:
        print(f"📄 指定记忆文件: {memory_path}")
    else:
        print("📄 自动查找昨日记忆文件...")
    
    # 处理记忆文件
    result = extractor.process_memory_file(memory_path, dry_run=args.dry_run)
    
    # 输出报告
    if args.report or True:  # 默认输出报告
        print("\n" + extractor.get_extraction_report(result))
    
    # 返回退出码
    return 0 if result['success'] else 1


if __name__ == "__main__":
    exit(main())
