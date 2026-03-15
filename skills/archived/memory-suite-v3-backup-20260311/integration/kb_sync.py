#!/usr/bin/env python3
"""
知识库同步模块 (Knowledge Base Sync)
Memory Suite v3.0 - Phase 3

功能：
1. 同步记忆到 knowledge-base/pending/
2. 生成知识项并分类
3. 维护双向链接
4. 一致性检查

作者: 雪子助手
版本: 3.0.0
日期: 2026-03-11
"""

import os
import json
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

# 配置路径
WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
KNOWLEDGE_DIR = WORKSPACE / "knowledge-base"
PENDING_DIR = KNOWLEDGE_DIR / "pending"
SYNC_LOG_FILE = MEMORY_DIR / "kb_sync_log.json"

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('kb_sync')


class KnowledgeCategory(Enum):
    """知识分类"""
    PROJECT = "project"           # 项目相关
    DECISION = "decision"         # 决策记录
    REFERENCE = "reference"       # 参考资料
    SOLUTION = "solution"         # 解决方案
    INSIGHT = "insight"           # 洞察/经验
    GENERAL = "general"           # 一般知识


@dataclass
class KnowledgeItem:
    """知识项"""
    id: str
    title: str
    category: str
    source_file: str
    created_at: str
    importance: float
    tags: List[str]
    summary: str
    content: str
    links: List[str]
    status: str = "pending"  # pending, processed, archived


@dataclass
class SyncRecord:
    """同步记录"""
    timestamp: str
    source: str
    target: str
    operation: str
    status: str
    details: str


class KBSync:
    """知识库同步器"""
    
    def __init__(self, workspace: Optional[Path] = None):
        """
        初始化同步器
        
        Args:
            workspace: 工作空间路径，默认使用标准路径
        """
        self.workspace = workspace or WORKSPACE
        self.memory_dir = self.workspace / "memory"
        self.knowledge_dir = self.workspace / "knowledge-base"
        self.pending_dir = self.knowledge_dir / "pending"
        self.sync_log_file = self.memory_dir / "kb_sync_log.json"
        
        self.sync_records: List[SyncRecord] = []
        self.items_synced = 0
        self.items_failed = 0
        
        self._ensure_directories()
        self._load_sync_log()
    
    def _ensure_directories(self):
        """确保必要目录存在"""
        self.pending_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"确保目录存在: {self.pending_dir}")
    
    def _load_sync_log(self):
        """加载同步日志"""
        if self.sync_log_file.exists():
            try:
                with open(self.sync_log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sync_records = [SyncRecord(**r) for r in data.get("records", [])]
                logger.debug(f"加载了 {len(self.sync_records)} 条同步记录")
            except Exception as e:
                logger.warning(f"加载同步日志失败: {e}")
                self.sync_records = []
        else:
            self.sync_records = []
    
    def _save_sync_log(self):
        """保存同步日志"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "total_records": len(self.sync_records),
                "records": [asdict(r) for r in self.sync_records[-200:]]  # 保留最近200条
            }
            with open(self.sync_log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"保存了 {len(self.sync_records)} 条同步记录")
        except Exception as e:
            logger.error(f"保存同步日志失败: {e}")
    
    def sync(self, force: bool = False) -> Dict[str, Any]:
        """
        执行同步
        
        Args:
            force: 是否强制同步所有文件，忽略已同步记录
            
        Returns:
            同步结果统计
        """
        logger.info("=" * 60)
        logger.info("🔄 开始知识库同步")
        logger.info(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        self.items_synced = 0
        self.items_failed = 0
        
        try:
            # 1. 扫描记忆文件
            memory_files = self._scan_memory_files()
            logger.info(f"📁 发现 {len(memory_files)} 个记忆文件")
            
            # 2. 处理每个文件
            for file_path in memory_files:
                try:
                    if self._should_sync(file_path, force):
                        if self._process_memory_file(file_path):
                            self.items_synced += 1
                        else:
                            self.items_failed += 1
                    else:
                        logger.debug(f"跳过已同步文件: {file_path.name}")
                except Exception as e:
                    logger.error(f"处理文件失败 {file_path.name}: {e}")
                    self.items_failed += 1
            
            # 3. 更新知识库索引
            self._update_kb_index()
            
            # 4. 检查一致性
            consistency = self._check_consistency()
            
            # 5. 保存日志
            self._save_sync_log()
            
            result = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "files_scanned": len(memory_files),
                "items_synced": self.items_synced,
                "items_failed": self.items_failed,
                "consistency": consistency
            }
            
            self._print_summary(result)
            return result
            
        except Exception as e:
            logger.error(f"同步过程发生错误: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _scan_memory_files(self) -> List[Path]:
        """扫描记忆文件"""
        files = []
        
        # 扫描 memory/ 目录下的 .md 文件
        if self.memory_dir.exists():
            for pattern in ["*.md", "**/*.md"]:
                files.extend(self.memory_dir.glob(pattern))
        
        # 过滤掉归档和索引目录
        files = [
            f for f in files 
            if "archive" not in str(f) and "index" not in str(f) and "snapshots" not in str(f)
        ]
        
        # 按修改时间排序
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        return files
    
    def _should_sync(self, file_path: Path, force: bool = False) -> bool:
        """检查文件是否需要同步"""
        if force:
            return True
        
        # 检查是否已同步
        file_str = str(file_path)
        recent_syncs = [
            r for r in self.sync_records 
            if r.source == file_str and r.status == "success"
        ]
        
        if not recent_syncs:
            return True
        
        # 检查文件是否被修改过
        last_sync = max(recent_syncs, key=lambda x: x.timestamp)
        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        sync_time = datetime.fromisoformat(last_sync.timestamp)
        
        return file_mtime > sync_time
    
    def _process_memory_file(self, file_path: Path) -> bool:
        """处理单个记忆文件"""
        logger.info(f"📄 处理: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取知识项
            knowledge_items = self._extract_knowledge(content, file_path)
            
            if not knowledge_items:
                logger.debug(f"  未提取到知识项")
                return True
            
            # 保存知识项
            for item in knowledge_items:
                self._save_knowledge_item(item)
            
            # 记录同步
            self.sync_records.append(SyncRecord(
                timestamp=datetime.now().isoformat(),
                source=str(file_path),
                target=str(self.pending_dir),
                operation="sync",
                status="success",
                details=f"提取了 {len(knowledge_items)} 个知识项"
            ))
            
            logger.info(f"  ✅ 提取了 {len(knowledge_items)} 个知识项")
            return True
            
        except Exception as e:
            logger.error(f"  ❌ 处理失败: {e}")
            self.sync_records.append(SyncRecord(
                timestamp=datetime.now().isoformat(),
                source=str(file_path),
                target="",
                operation="sync",
                status="failed",
                details=str(e)
            ))
            return False
    
    def _extract_knowledge(self, content: str, source_file: Path) -> List[KnowledgeItem]:
        """从内容中提取知识项"""
        items = []
        
        # 提取标题
        title = self._extract_title(content) or source_file.stem
        
        # 提取重要性
        importance = self._calculate_importance(content)
        
        # 提取标签
        tags = self._extract_tags(content)
        
        # 提取分类
        category = self._determine_category(content)
        
        # 生成摘要
        summary = self._generate_summary(content)
        
        # 提取链接
        links = self._extract_links(content)
        
        # 创建知识项
        item_id = f"kb_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{source_file.stem[:20]}"
        
        item = KnowledgeItem(
            id=item_id,
            title=title,
            category=category.value,
            source_file=str(source_file.relative_to(self.workspace)),
            created_at=datetime.now().isoformat(),
            importance=importance,
            tags=tags,
            summary=summary,
            content=content[:5000],  # 限制内容长度
            links=links
        )
        
        items.append(item)
        
        # 如果内容很长，尝试提取更多知识项
        if len(content) > 2000:
            sub_items = self._extract_sub_knowledge(content, source_file)
            items.extend(sub_items)
        
        return items
    
    def _extract_title(self, content: str) -> Optional[str]:
        """提取标题"""
        # 匹配 # 标题
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # 匹配 ## 标题
        match = re.search(r'^##\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        return None
    
    def _calculate_importance(self, content: str) -> float:
        """计算重要性分数 (0-1)"""
        score = 0.5  # 基础分
        
        # 关键标记加分
        importance_markers = {
            r'\[IMPORTANT\]': 0.3,
            r'\[DECISION\]': 0.25,
            r'\[PROJECT\]': 0.2,
            r'\[KEY\]': 0.2,
            r'完成|搞定|解决': 0.15,
            r'重要|关键|核心': 0.1,
        }
        
        for pattern, weight in importance_markers.items():
            if re.search(pattern, content, re.IGNORECASE):
                score += weight
        
        # 内容长度调整
        if len(content) > 5000:
            score += 0.1
        
        return min(score, 1.0)
    
    def _extract_tags(self, content: str) -> List[str]:
        """提取标签"""
        tags = []
        
        # 匹配 #标签
        tags.extend(re.findall(r'#([\w\u4e00-\u9fa5-]+)', content))
        
        # 匹配 [TAG:xxx]
        tags.extend(re.findall(r'\[TAG:\s*([^\]]+)\]', content))
        
        # 去重并限制数量
        tags = list(set(tags))[:10]
        
        return tags
    
    def _determine_category(self, content: str) -> KnowledgeCategory:
        """确定知识分类"""
        content_lower = content.lower()
        
        # 项目相关
        if re.search(r'\[PROJECT\]|项目|开发|完成|部署', content_lower):
            return KnowledgeCategory.PROJECT
        
        # 决策记录
        if re.search(r'\[DECISION\]|决定|决策|选择|方案', content_lower):
            return KnowledgeCategory.DECISION
        
        # 解决方案
        if re.search(r'解决|方案|修复|bug|issue|问题', content_lower):
            return KnowledgeCategory.SOLUTION
        
        # 洞察/经验
        if re.search(r'经验|教训|洞察|总结|反思', content_lower):
            return KnowledgeCategory.INSIGHT
        
        # 参考资料
        if re.search(r'参考|链接|资料|文档|教程', content_lower):
            return KnowledgeCategory.REFERENCE
        
        return KnowledgeCategory.GENERAL
    
    def _generate_summary(self, content: str) -> str:
        """生成摘要"""
        # 移除Markdown标记
        text = re.sub(r'[#*\[\](){}|`]', '', content)
        
        # 取前200字符
        summary = text[:200].strip()
        
        # 如果太长，截断并添加省略号
        if len(text) > 200:
            summary += "..."
        
        return summary
    
    def _extract_links(self, content: str) -> List[str]:
        """提取链接"""
        links = []
        
        # Markdown 链接 [text](url)
        links.extend(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content))
        
        # 裸链接
        links.extend(re.findall(r'https?://[^\s\)\]]+', content))
        
        return links[:10]
    
    def _extract_sub_knowledge(self, content: str, source_file: Path) -> List[KnowledgeItem]:
        """提取子知识项"""
        items = []
        
        # 按 ## 分割
        sections = re.split(r'\n##\s+', content)
        
        for i, section in enumerate(sections[1:], 1):  # 跳过第一个（通常是标题）
            if len(section) < 200:
                continue
            
            section_title = section.split('\n')[0].strip()
            
            # 检查是否是重要部分
            if re.search(r'决策|决定|方案|解决|完成|重要', section):
                item_id = f"kb_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{source_file.stem[:15]}_{i}"
                
                item = KnowledgeItem(
                    id=item_id,
                    title=section_title[:50],
                    category=KnowledgeCategory.SOLUTION.value,
                    source_file=str(source_file.relative_to(self.workspace)),
                    created_at=datetime.now().isoformat(),
                    importance=0.7,
                    tags=[],
                    summary=self._generate_summary(section),
                    content=section[:3000],
                    links=[]
                )
                
                items.append(item)
        
        return items
    
    def _save_knowledge_item(self, item: KnowledgeItem):
        """保存知识项到 pending 目录"""
        # 按分类组织
        category_dir = self.pending_dir / item.category
        category_dir.mkdir(exist_ok=True)
        
        # 生成文件名
        safe_title = re.sub(r'[^\w\u4e00-\u9fa5-]', '_', item.title)[:30]
        filename = f"{item.id}_{safe_title}.json"
        filepath = category_dir / filename
        
        # 保存为 JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(item), f, ensure_ascii=False, indent=2)
        
        logger.debug(f"  保存知识项: {filepath.name}")
    
    def _update_kb_index(self):
        """更新知识库索引"""
        index_file = self.knowledge_dir / "pending_index.json"
        
        try:
            # 收集所有 pending 知识项
            items = []
            for json_file in self.pending_dir.rglob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        item = json.load(f)
                        items.append({
                            "id": item.get("id"),
                            "title": item.get("title"),
                            "category": item.get("category"),
                            "source_file": item.get("source_file"),
                            "created_at": item.get("created_at"),
                            "importance": item.get("importance"),
                            "tags": item.get("tags"),
                            "status": item.get("status")
                        })
                except Exception as e:
                    logger.warning(f"读取知识项失败 {json_file}: {e}")
            
            # 按时间排序
            items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            # 保存索引
            index_data = {
                "timestamp": datetime.now().isoformat(),
                "total_items": len(items),
                "items": items
            }
            
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📚 更新知识库索引: {len(items)} 个知识项")
            
        except Exception as e:
            logger.error(f"更新知识库索引失败: {e}")
    
    def _check_consistency(self) -> Dict[str, Any]:
        """检查一致性"""
        logger.info("🔍 检查知识一致性...")
        
        issues = []
        
        # 1. 检查死链接
        for json_file in self.pending_dir.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    item = json.load(f)
                
                source_file = self.workspace / item.get("source_file", "")
                if not source_file.exists():
                    issues.append({
                        "type": "missing_source",
                        "item": json_file.name,
                        "source": str(source_file)
                    })
            except Exception as e:
                issues.append({
                    "type": "read_error",
                    "item": str(json_file),
                    "error": str(e)
                })
        
        # 2. 检查重复
        seen_ids = set()
        for json_file in self.pending_dir.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    item = json.load(f)
                
                item_id = item.get("id")
                if item_id in seen_ids:
                    issues.append({
                        "type": "duplicate_id",
                        "item": json_file.name,
                        "id": item_id
                    })
                seen_ids.add(item_id)
            except:
                pass
        
        result = {
            "checked_at": datetime.now().isoformat(),
            "total_issues": len(issues),
            "issues": issues[:20]  # 限制报告数量
        }
        
        if issues:
            logger.warning(f"  发现 {len(issues)} 个一致性问题")
        else:
            logger.info("  ✅ 一致性检查通过")
        
        return result
    
    def _print_summary(self, result: Dict[str, Any]):
        """打印同步摘要"""
        logger.info("=" * 60)
        logger.info("📊 同步摘要")
        logger.info("=" * 60)
        logger.info(f"  扫描文件: {result.get('files_scanned', 0)}")
        logger.info(f"  同步成功: {result.get('items_synced', 0)}")
        logger.info(f"  同步失败: {result.get('items_failed', 0)}")
        logger.info(f"  一致性问题: {result.get('consistency', {}).get('total_issues', 0)}")
        logger.info("=" * 60)


def sync_memory_to_kb(force: bool = False) -> Dict[str, Any]:
    """
    便捷函数：同步记忆到知识库
    
    Args:
        force: 是否强制同步
        
    Returns:
        同步结果
    """
    sync = KBSync()
    return sync.sync(force=force)


def main():
    """主函数 - 用于命令行调用"""
    import argparse
    
    parser = argparse.ArgumentParser(description='知识库同步模块')
    parser.add_argument('--force', '-f', action='store_true', help='强制同步所有文件')
    parser.add_argument('--workspace', '-w', type=str, help='工作空间路径')
    
    args = parser.parse_args()
    
    workspace = Path(args.workspace) if args.workspace else None
    sync = KBSync(workspace=workspace)
    result = sync.sync(force=args.force)
    
    # 输出 JSON 结果
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    exit(main())
