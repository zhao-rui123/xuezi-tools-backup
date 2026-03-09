#!/usr/bin/env python3
"""
自动归档系统 (Auto Archive System)
第一阶段 - 基础优化

功能：
1. 每日记忆 7天后自动归档到 archive/
2. 30天后提取关键信息到 permanent/
3. 90天后压缩存储
4. 清理过期临时文件

作者: 雪子助手
版本: 1.0.0
日期: 2026-03-09
"""

import os
import json
import shutil
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import re

# 配置
MEMORY_DIR = Path("/Users/zhaoruicn/.openclaw/workspace/memory")
ARCHIVE_DIR = MEMORY_DIR / "archive"
PERMANENT_DIR = MEMORY_DIR / "permanent"
SNAPSHOTS_DIR = MEMORY_DIR / "snapshots"

# 时间阈值
DAYS_TO_ARCHIVE = 7      # 7天后归档
DAYS_TO_PERMANENT = 30   # 30天后转永久
DAYS_TO_COMPRESS = 90    # 90天后压缩
DAYS_TO_DELETE = 365     # 365天后删除


class AutoArchiveSystem:
    """自动归档系统"""
    
    def __init__(self):
        self.memory_dir = MEMORY_DIR
        self.archive_dir = ARCHIVE_DIR
        self.permanent_dir = PERMANENT_DIR
        
        # 确保目录存在
        self.archive_dir.mkdir(exist_ok=True)
        self.permanent_dir.mkdir(exist_ok=True)
        
        self.stats = {
            "archived": 0,
            "permanent": 0,
            "compressed": 0,
            "deleted": 0,
            "errors": []
        }
    
    def parse_date_from_filename(self, filename: str) -> Optional[datetime]:
        """从文件名解析日期"""
        # 匹配 YYYY-MM-DD 格式
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
        if match:
            year, month, day = map(int, match.groups())
            return datetime(year, month, day)
        return None
    
    def get_file_age_days(self, file_path: Path) -> int:
        """获取文件年龄（天）"""
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        return (datetime.now() - mtime).days
    
    def extract_key_info(self, content: str) -> Dict:
        """从记忆内容中提取关键信息"""
        key_info = {
            "decisions": [],
            "projects": [],
            "tasks": [],
            "summary": ""
        }
        
        # 提取 [DECISION] 区块
        decision_pattern = r'\[DECISION\].*?(?=\n\[|\n## |\Z)'
        decisions = re.findall(decision_pattern, content, re.DOTALL)
        key_info["decisions"] = [d.strip() for d in decisions]
        
        # 提取项目信息
        project_pattern = r'\[PROJECT\].*?(?=\n\[|\n## |\Z)'
        projects = re.findall(project_pattern, content, re.DOTALL)
        key_info["projects"] = [p.strip() for p in projects]
        
        # 提取任务信息
        task_pattern = r'\[TODO\].*?(?=\n\[|\n## |\Z)'
        tasks = re.findall(task_pattern, content, re.DOTALL)
        key_info["tasks"] = [t.strip() for t in tasks]
        
        # 生成摘要（前500字符）
        lines = content.split('\n')
        summary_lines = []
        for line in lines:
            if line.strip() and not line.startswith('#'):
                summary_lines.append(line.strip())
            if len('\n'.join(summary_lines)) > 500:
                break
        key_info["summary"] = '\n'.join(summary_lines)[:500]
        
        return key_info
    
    def archive_daily_memory(self, file_path: Path) -> bool:
        """归档每日记忆文件"""
        try:
            # 解析日期
            file_date = self.parse_date_from_filename(file_path.name)
            if not file_date:
                return False
            
            # 按年月创建归档目录
            archive_subdir = self.archive_dir / f"{file_date.year}" / f"{file_date.month:02d}"
            archive_subdir.mkdir(parents=True, exist_ok=True)
            
            # 移动文件
            dest_path = archive_subdir / file_path.name
            shutil.move(str(file_path), str(dest_path))
            
            print(f"  📦 已归档: {file_path.name} -> {dest_path.relative_to(self.memory_dir)}")
            self.stats["archived"] += 1
            return True
            
        except Exception as e:
            self.stats["errors"].append(f"归档 {file_path.name} 失败: {str(e)}")
            return False
    
    def create_permanent_record(self, file_path: Path) -> bool:
        """创建永久记忆记录"""
        try:
            # 读取原文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取关键信息
            key_info = self.extract_key_info(content)
            
            # 解析日期
            file_date = self.parse_date_from_filename(file_path.name)
            if not file_date:
                return False
            
            # 创建永久记录
            record = {
                "date": file_date.strftime("%Y-%m-%d"),
                "source_file": str(file_path.name),
                "summary": key_info["summary"],
                "decisions": key_info["decisions"],
                "projects": key_info["projects"],
                "tasks": key_info["tasks"],
                "created_at": datetime.now().isoformat()
            }
            
            # 保存到永久记忆
            permanent_file = self.permanent_dir / f"{file_date.strftime('%Y-%m-%d')}.json"
            with open(permanent_file, 'w', encoding='utf-8') as f:
                json.dump(record, f, ensure_ascii=False, indent=2)
            
            print(f"  💎 已创建永久记录: {permanent_file.name}")
            self.stats["permanent"] += 1
            return True
            
        except Exception as e:
            self.stats["errors"].append(f"创建永久记录 {file_path.name} 失败: {str(e)}")
            return False
    
    def compress_old_archive(self, file_path: Path) -> bool:
        """压缩旧归档文件"""
        try:
            # 读取文件
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # 压缩
            compressed_path = file_path.with_suffix('.md.gz')
            with gzip.open(compressed_path, 'wb') as f:
                f.write(content)
            
            # 删除原文件
            file_path.unlink()
            
            print(f"  🗜️  已压缩: {file_path.name}")
            self.stats["compressed"] += 1
            return True
            
        except Exception as e:
            self.stats["errors"].append(f"压缩 {file_path.name} 失败: {str(e)}")
            return False
    
    def process_daily_memories(self):
        """处理每日记忆文件"""
        print("\n📋 处理每日记忆文件...")
        
        # 查找所有日常记忆文件
        daily_files = []
        for file_path in self.memory_dir.glob("2026-*.md"):
            if file_path.name.startswith("2026-"):
                daily_files.append(file_path)
        
        print(f"  找到 {len(daily_files)} 个记忆文件")
        
        for file_path in daily_files:
            age_days = self.get_file_age_days(file_path)
            
            # 7天后归档
            if age_days >= DAYS_TO_ARCHIVE:
                print(f"\n  处理: {file_path.name} ({age_days}天)")
                
                # 30天后先创建永久记录
                if age_days >= DAYS_TO_PERMANENT:
                    self.create_permanent_record(file_path)
                
                # 归档文件
                self.archive_daily_memory(file_path)
    
    def process_archive_compression(self):
        """处理归档压缩"""
        print("\n🗜️  处理归档压缩...")
        
        # 查找归档目录中的文件
        archive_files = list(self.archive_dir.rglob("*.md"))
        print(f"  找到 {len(archive_files)} 个归档文件")
        
        for file_path in archive_files:
            age_days = self.get_file_age_days(file_path)
            
            # 90天后压缩
            if age_days >= DAYS_TO_COMPRESS:
                print(f"  压缩: {file_path.name} ({age_days}天)")
                self.compress_old_archive(file_path)
    
    def cleanup_old_snapshots(self):
        """清理旧快照"""
        print("\n🧹 清理旧快照...")
        
        if not SNAPSHOTS_DIR.exists():
            print("  快照目录不存在")
            return
        
        snapshot_files = list(SNAPSHOTS_DIR.glob("*.json"))
        print(f"  找到 {len(snapshot_files)} 个快照文件")
        
        deleted = 0
        for file_path in snapshot_files:
            # 保留 current_session.json
            if file_path.name == "current_session.json":
                continue
            
            age_days = self.get_file_age_days(file_path)
            
            # 30天后删除旧快照
            if age_days >= 30:
                file_path.unlink()
                deleted += 1
                print(f"  删除旧快照: {file_path.name}")
        
        print(f"  已删除 {deleted} 个旧快照")
    
    def run(self):
        """运行自动归档"""
        print("=" * 60)
        print("🗄️  自动归档系统")
        print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 1. 处理每日记忆
        self.process_daily_memories()
        
        # 2. 处理归档压缩
        self.process_archive_compression()
        
        # 3. 清理旧快照
        self.cleanup_old_snapshots()
        
        # 打印统计
        print("\n" + "=" * 60)
        print("📊 归档统计")
        print("=" * 60)
        print(f"  📦 已归档: {self.stats['archived']} 个文件")
        print(f"  💎 永久记录: {self.stats['permanent']} 个")
        print(f"  🗜️  已压缩: {self.stats['compressed']} 个文件")
        print(f"  🗑️  已删除: {self.stats['deleted']} 个文件")
        
        if self.stats["errors"]:
            print(f"\n⚠️  错误 ({len(self.stats['errors'])}):")
            for error in self.stats["errors"]:
                print(f"    - {error}")
        
        print("\n✅ 自动归档完成")
        
        return self.stats


def main():
    """主函数"""
    system = AutoArchiveSystem()
    stats = system.run()
    
    # 保存统计到日志
    log_file = MEMORY_DIR / "archive" / "archive_log.json"
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "stats": stats
    }
    
    # 追加到日志
    logs = []
    if log_file.exists():
        with open(log_file, 'r', encoding='utf-8') as f:
            try:
                logs = json.load(f)
            except:
                logs = []
    
    logs.append(log_entry)
    
    # 只保留最近100条日志
    logs = logs[-100:]
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    
    print(f"\n📝 日志已保存: {log_file}")


if __name__ == "__main__":
    main()
