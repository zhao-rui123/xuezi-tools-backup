#!/usr/bin/env python3
"""
知识库联动系统 (Knowledge Base Integration)
第三阶段 - 生态融合

功能：
1. 记忆自动同步到知识库
2. 知识库更新反馈到记忆
3. 双向链接维护
4. 知识一致性检查

作者: 雪子助手
版本: 1.0.0
日期: 2026-03-09
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# 配置
MEMORY_DIR = Path("/Users/zhaoruicn/.openclaw/workspace/memory")
KNOWLEDGE_DIR = Path("/Users/zhaoruicn/.openclaw/workspace/knowledge-base")
SYNC_LOG_FILE = MEMORY_DIR / "kb_sync_log.json"


@dataclass
class SyncRecord:
    """同步记录"""
    timestamp: str
    source: str
    target: str
    operation: str  # create, update, link
    status: str  # success, failed
    details: str


class KnowledgeBaseIntegration:
    """知识库联动系统"""
    
    def __init__(self):
        self.memory_dir = MEMORY_DIR
        self.knowledge_dir = KNOWLEDGE_DIR
        self.sync_records: List[SyncRecord] = []
        self._load_sync_log()
    
    def _load_sync_log(self):
        """加载同步日志"""
        if SYNC_LOG_FILE.exists():
            try:
                with open(SYNC_LOG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sync_records = [SyncRecord(**r) for r in data.get("records", [])]
            except:
                self.sync_records = []
    
    def _save_sync_log(self):
        """保存同步日志"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "records": [asdict(r) for r in self.sync_records[-100:]]  # 保留最近100条
        }
        with open(SYNC_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def sync_memory_to_kb(self):
        """将记忆同步到知识库"""
        print("🔄 同步记忆到知识库...")
        
        synced_count = 0
        
        # 扫描重要记忆
        for file_path in self.memory_dir.glob("2026-*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取关键信息
                key_info = self._extract_key_info(content)
                
                if key_info["importance"] >= 0.8:  # 只同步重要记忆
                    # 同步到对应的知识库位置
                    if self._sync_to_appropriate_location(file_path, key_info):
                        synced_count += 1
                        
            except Exception as e:
                print(f"  ⚠️ 同步 {file_path.name} 失败: {str(e)}")
        
        print(f"  ✅ 同步了 {synced_count} 条重要记忆")
        return synced_count
    
    def _extract_key_info(self, content: str) -> Dict:
        """提取关键信息"""
        info = {
            "title": "",
            "importance": 0.5,
            "category": "general",
            "projects": [],
            "decisions": [],
            "tags": []
        }
        
        # 提取标题
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            info["title"] = title_match.group(1)
        
        # 检测类别
        if "[PROJECT]" in content or "## 完成" in content:
            info["category"] = "project"
            info["importance"] += 0.3
        elif "[DECISION]" in content or "决定" in content:
            info["category"] = "decision"
            info["importance"] += 0.4
        
        # 提取项目
        projects = re.findall(r'###\s+(.+?)(?:开发|完成|项目)', content)
        info["projects"] = projects
        
        # 提取决策
        decisions = re.findall(r'\[DECISION\]\s*(.+?)(?=\n\[|\Z)', content, re.DOTALL)
        info["decisions"] = [d.strip()[:100] for d in decisions]
        
        # 提取标签
        tags = re.findall(r'#([\w\u4e00-\u9fa5-]+)', content)
        info["tags"] = tags
        
        return info
    
    def _sync_to_appropriate_location(self, source_file: Path, key_info: Dict) -> bool:
        """同步到适当位置"""
        category = key_info["category"]
        
        if category == "project":
            return self._sync_to_projects(source_file, key_info)
        elif category == "decision":
            return self._sync_to_decisions(source_file, key_info)
        else:
            return self._sync_to_references(source_file, key_info)
    
    def _sync_to_projects(self, source_file: Path, key_info: Dict) -> bool:
        """同步到项目目录"""
        projects_dir = self.knowledge_dir / "projects"
        projects_dir.mkdir(exist_ok=True)
        
        for project_name in key_info["projects"][:1]:  # 只取第一个项目
            # 清理项目名称
            clean_name = re.sub(r'[^\w\u4e00-\u9fa5-]', '-', project_name)[:30]
            project_dir = projects_dir / clean_name
            project_dir.mkdir(exist_ok=True)
            
            # 创建项目摘要
            summary_file = project_dir / "summary.md"
            summary_content = f"""# {project_name}

## 项目摘要
**来源**: {source_file.name}
**同步时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 关键信息
{key_info.get('title', '')}

## 标签
{', '.join(key_info.get('tags', []))}

## 原始文件
- [查看原始记忆](../memory/{source_file.name})
"""
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            
            # 记录同步
            self.sync_records.append(SyncRecord(
                timestamp=datetime.now().isoformat(),
                source=str(source_file),
                target=str(summary_file),
                operation="create",
                status="success",
                details=f"项目: {project_name}"
            ))
            
            return True
        
        return False
    
    def _sync_to_decisions(self, source_file: Path, key_info: Dict) -> bool:
        """同步到决策目录"""
        decisions_dir = self.knowledge_dir / "decisions"
        decisions_dir.mkdir(exist_ok=True)
        
        for decision in key_info["decisions"][:1]:
            # 生成文件名
            clean_name = re.sub(r'[^\w\u4e00-\u9fa5-]', '-', decision)[:30]
            decision_file = decisions_dir / f"{datetime.now().strftime('%Y-%m-%d')}-{clean_name}.md"
            
            content = f"""# 决策记录

**决策内容**: {decision}

**来源**: {source_file.name}
**记录时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 相关标签
{', '.join(key_info.get('tags', []))}

## 原始文件
- [查看完整上下文](../memory/{source_file.name})
"""
            
            with open(decision_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.sync_records.append(SyncRecord(
                timestamp=datetime.now().isoformat(),
                source=str(source_file),
                target=str(decision_file),
                operation="create",
                status="success",
                details=f"决策: {decision[:50]}"
            ))
            
            return True
        
        return False
    
    def _sync_to_references(self, source_file: Path, key_info: Dict) -> bool:
        """同步到参考资料"""
        refs_dir = self.knowledge_dir / "references"
        refs_dir.mkdir(exist_ok=True)
        
        # 创建月度参考资料
        month = datetime.now().strftime('%Y-%m')
        ref_file = refs_dir / f"memory-snapshot-{month}.md"
        
        entry = f"""
## {key_info.get('title', source_file.stem)}

- **文件**: {source_file.name}
- **时间**: {datetime.now().strftime('%Y-%m-%d')}
- **标签**: {', '.join(key_info.get('tags', []))}
"""
        
        # 追加到文件
        if ref_file.exists():
            with open(ref_file, 'a', encoding='utf-8') as f:
                f.write(entry)
        else:
            with open(ref_file, 'w', encoding='utf-8') as f:
                f.write(f"# 记忆快照 {month}\n{entry}")
        
        self.sync_records.append(SyncRecord(
            timestamp=datetime.now().isoformat(),
            source=str(source_file),
            target=str(ref_file),
            operation="update",
            status="success",
            details="追加到月度快照"
        ))
        
        return True
    
    def update_kb_links(self):
        """更新知识库链接"""
        print("🔗 更新知识库链接...")
        
        # 更新索引文件
        index_file = self.knowledge_dir / "INDEX.md"
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否需要更新
                current_date = datetime.now().strftime('%Y-%m-%d')
                if current_date not in content:
                    # 添加更新标记
                    content = content.replace(
                        "## 统计信息",
                        f"## 统计信息\n\n- **系统更新**: {current_date} - 统一记忆系统联动更新"
                    )
                    
                    with open(index_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print("  ✅ 知识库索引已更新")
                    
            except Exception as e:
                print(f"  ⚠️ 更新索引失败: {str(e)}")
    
    def check_consistency(self) -> Dict:
        """检查知识一致性"""
        print("🔍 检查知识一致性...")
        
        issues = []
        
        # 1. 检查知识库中是否有死链接
        for md_file in self.knowledge_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 查找链接到 memory 的文件
                memory_links = re.findall(r'\[.*?\]\(.*?memory/(.+?)\)', content)
                
                for link in memory_links:
                    memory_file = self.memory_dir / link
                    if not memory_file.exists():
                        issues.append({
                            "type": "dead_link",
                            "file": str(md_file),
                            "missing": link
                        })
                        
            except:
                continue
        
        # 2. 检查未同步的重要记忆
        unsynced = []
        for memory_file in self.memory_dir.glob("2026-*.md"):
            # 检查是否已同步
            is_synced = any(
                r.source == str(memory_file) and r.status == "success"
                for r in self.sync_records
            )
            
            if not is_synced:
                try:
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 检查重要性
                    if "[PROJECT]" in content or "[DECISION]" in content:
                        unsynced.append(memory_file.name)
                        
                except:
                    continue
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "dead_links": issues,
            "unsynced_important": unsynced[:10],
            "total_issues": len(issues) + len(unsynced)
        }
        
        print(f"  发现 {len(issues)} 个死链接, {len(unsynced)} 个未同步的重要记忆")
        return result
    
    def run(self):
        """运行知识库联动"""
        print("=" * 60)
        print("📚 知识库联动系统")
        print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 1. 同步记忆到知识库
        synced = self.sync_memory_to_kb()
        
        # 2. 更新链接
        self.update_kb_links()
        
        # 3. 检查一致性
        consistency = self.check_consistency()
        
        # 保存日志
        self._save_sync_log()
        
        # 打印报告
        print("\n" + "=" * 60)
        print("📊 同步报告")
        print("=" * 60)
        print(f"  同步记忆数: {synced}")
        print(f"  历史同步记录: {len(self.sync_records)} 条")
        print(f"  一致性问题: {consistency['total_issues']}")
        
        if consistency['dead_links']:
            print(f"\n  ⚠️ 死链接 ({len(consistency['dead_links'])}):")
            for issue in consistency['dead_links'][:3]:
                print(f"    - {issue['file']} -> {issue['missing']}")
        
        print("\n✅ 知识库联动完成")
        
        return {
            "synced": synced,
            "consistency": consistency
        }


def main():
    """主函数"""
    system = KnowledgeBaseIntegration()
    result = system.run()
    return result


if __name__ == "__main__":
    main()
