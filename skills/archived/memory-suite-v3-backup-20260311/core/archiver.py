#!/usr/bin/env python3
"""
Memory Suite v3 - Archiver Module
归档模块

功能：
1. 7 天后归档到 memory/archive/
2. 30 天后提取关键信息到 permanent/
3. 90 天后压缩存储
4. 365 天后删除

用法：
    from core.archiver import Archiver, get_archiver
    
    # 初始化
    archiver = get_archiver()
    
    # 运行归档
    archiver.run()
    
    # 或单独执行各阶段
    archiver.archive_daily_memories()
    archiver.create_permanent_records()
    archiver.compress_old_archives()
    archiver.cleanup_expired()

作者：Memory Suite Team
版本：3.0.0
"""

import json
import gzip
import shutil
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any


# ============================================================================
# 配置常量
# ============================================================================

DEFAULT_WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
DEFAULT_MEMORY_DIR = DEFAULT_WORKSPACE / "memory"
DEFAULT_ARCHIVE_DIR = DEFAULT_MEMORY_DIR / "archive"
DEFAULT_PERMANENT_DIR = DEFAULT_MEMORY_DIR / "permanent"
DEFAULT_SNAPSHOTS_DIR = DEFAULT_MEMORY_DIR / "snapshots"

# 时间阈值（天）
DAYS_TO_ARCHIVE = 7       # 7 天后归档
DAYS_TO_PERMANENT = 30    # 30 天后转永久
DAYS_TO_COMPRESS = 90     # 90 天后压缩
DAYS_TO_DELETE = 365      # 365 天后删除


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
# 归档器
# ============================================================================

class Archiver:
    """
    归档器 - 核心类
    
    功能：
    1. 7 天后归档每日记忆
    2. 30 天后提取关键信息到永久记忆
    3. 90 天后压缩归档文件
    4. 365 天后删除过期文件
    """
    
    def __init__(self, 
                 memory_dir: Optional[Path] = None,
                 archive_dir: Optional[Path] = None,
                 permanent_dir: Optional[Path] = None,
                 workspace: Optional[Path] = None):
        self.workspace = workspace or DEFAULT_WORKSPACE
        self.memory_dir = memory_dir or self.workspace / "memory"
        self.archive_dir = archive_dir or self.memory_dir / "archive"
        self.permanent_dir = permanent_dir or self.memory_dir / "permanent"
        self.snapshots_dir = self.memory_dir / "snapshots"
        
        self.logger = Logger("Archiver")
        self._ensure_directories()
        
        self.stats = {
            "archived": 0,
            "permanent": 0,
            "compressed": 0,
            "deleted": 0,
            "errors": []
        }
    
    def _ensure_directories(self):
        try:
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            self.permanent_dir.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"确保目录存在：{self.archive_dir}, {self.permanent_dir}")
        except Exception as e:
            self.logger.error(f"创建目录失败：{e}")
            raise
    
    def parse_date_from_filename(self, filename: str) -> Optional[datetime]:
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
        if match:
            year, month, day = map(int, match.groups())
            try:
                return datetime(year, month, day)
            except ValueError:
                return None
        return None
    
    def get_file_age_days(self, file_path: Path) -> int:
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            return (datetime.now() - mtime).days
        except Exception as e:
            self.logger.warn(f"获取文件年龄失败 {file_path.name}: {e}")
            return 0
    
    def extract_key_info(self, content: str) -> Dict[str, Any]:
        key_info = {
            "decisions": [],
            "projects": [],
            "tasks": [],
            "summary": "",
            "keywords": []
        }
        
        decision_pattern = r'\[DECISION\].*?(?=\n\[|\n## |\Z)'
        decisions = re.findall(decision_pattern, content, re.DOTALL)
        key_info["decisions"] = [d.strip() for d in decisions]
        
        project_pattern = r'\[PROJECT\].*?(?=\n\[|\n## |\Z)'
        projects = re.findall(project_pattern, content, re.DOTALL)
        key_info["projects"] = [p.strip() for p in projects]
        
        task_pattern = r'\[TODO\].*?(?=\n\[|\n## |\Z)'
        tasks = re.findall(task_pattern, content, re.DOTALL)
        key_info["tasks"] = [t.strip() for t in tasks]
        
        keyword_pattern = r'关键词 [：:]\s*(.+?)(?:\n|$)'
        keyword_matches = re.findall(keyword_pattern, content)
        if keyword_matches:
            keywords = [k.strip() for k in keyword_matches[0].split(',')]
            key_info["keywords"] = keywords[:20]
        
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
        try:
            file_date = self.parse_date_from_filename(file_path.name)
            if not file_date:
                self.logger.warn(f"无法解析日期：{file_path.name}")
                return False
            
            archive_subdir = self.archive_dir / f"{file_date.year}" / f"{file_date.month:02d}"
            archive_subdir.mkdir(parents=True, exist_ok=True)
            
            dest_path = archive_subdir / file_path.name
            shutil.move(str(file_path), str(dest_path))
            
            self.logger.info(f"已归档：{file_path.name} -> {dest_path.relative_to(self.memory_dir)}")
            self.stats["archived"] += 1
            return True
        
        except Exception as e:
            error_msg = f"归档 {file_path.name} 失败：{str(e)}"
            self.logger.error(error_msg)
            self.stats["errors"].append(error_msg)
            return False
    
    def create_permanent_record(self, file_path: Path) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            key_info = self.extract_key_info(content)
            
            file_date = self.parse_date_from_filename(file_path.name)
            if not file_date:
                return False
            
            record = {
                "date": file_date.strftime("%Y-%m-%d"),
                "source_file": str(file_path.name),
                "archived_at": datetime.fromtimestamp(
                    file_path.stat().st_mtime
                ).isoformat(),
                "summary": key_info["summary"],
                "decisions": key_info["decisions"],
                "projects": key_info["projects"],
                "tasks": key_info["tasks"],
                "keywords": key_info["keywords"],
                "created_at": datetime.now().isoformat()
            }
            
            permanent_file = self.permanent_dir / f"{file_date.strftime('%Y-%m-%d')}.json"
            with open(permanent_file, 'w', encoding='utf-8') as f:
                json.dump(record, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"已创建永久记录：{permanent_file.name}")
            self.stats["permanent"] += 1
            return True
        
        except Exception as e:
            error_msg = f"创建永久记录 {file_path.name} 失败：{str(e)}"
            self.logger.error(error_msg)
            self.stats["errors"].append(error_msg)
            return False
    
    def compress_archive_file(self, file_path: Path) -> bool:
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            compressed_path = file_path.with_suffix('.md.gz')
            with gzip.open(compressed_path, 'wb') as f:
                f.write(content)
            
            file_path.unlink()
            
            self.logger.info(f"已压缩：{file_path.name}")
            self.stats["compressed"] += 1
            return True
        
        except Exception as e:
            error_msg = f"压缩 {file_path.name} 失败：{str(e)}"
            self.logger.error(error_msg)
            self.stats["errors"].append(error_msg)
            return False
    
    def delete_expired_file(self, file_path: Path) -> bool:
        try:
            file_path.unlink()
            self.logger.info(f"已删除过期文件：{file_path.name}")
            self.stats["deleted"] += 1
            return True
        
        except Exception as e:
            error_msg = f"删除 {file_path.name} 失败：{str(e)}"
            self.logger.error(error_msg)
            self.stats["errors"].append(error_msg)
            return False
    
    def archive_daily_memories(self):
        self.logger.info("处理每日记忆文件归档...")
        
        daily_files = []
        for pattern in ["*.md", "202*-*.md"]:
            for file_path in self.memory_dir.glob(pattern):
                if file_path.name.startswith("20") and file_path.name.endswith(".md"):
                    if self.archive_dir in file_path.parents:
                        continue
                    daily_files.append(file_path)
        
        self.logger.info(f"找到 {len(daily_files)} 个记忆文件")
        
        for file_path in daily_files:
            age_days = self.get_file_age_days(file_path)
            
            if age_days >= DAYS_TO_ARCHIVE:
                self.logger.debug(f"处理：{file_path.name} ({age_days}天)")
                
                if age_days >= DAYS_TO_PERMANENT:
                    self.create_permanent_record(file_path)
                
                self.archive_daily_memory(file_path)
    
    def create_permanent_records(self):
        self.logger.info("处理永久记录创建...")
        
        archive_files = list(self.archive_dir.rglob("*.md"))
        self.logger.info(f"找到 {len(archive_files)} 个归档文件")
        
        for file_path in archive_files:
            age_days = self.get_file_age_days(file_path)
            
            if age_days >= DAYS_TO_PERMANENT:
                file_date = self.parse_date_from_filename(file_path.name)
                if file_date:
                    permanent_file = self.permanent_dir / f"{file_date.strftime('%Y-%m-%d')}.json"
                    if not permanent_file.exists():
                        self.logger.debug(f"创建永久记录：{file_path.name} ({age_days}天)")
                        self.create_permanent_record(file_path)
    
    def compress_old_archives(self):
        self.logger.info("处理归档压缩...")
        
        archive_files = list(self.archive_dir.rglob("*.md"))
        self.logger.info(f"找到 {len(archive_files)} 个归档文件")
        
        for file_path in archive_files:
            age_days = self.get_file_age_days(file_path)
            
            if age_days >= DAYS_TO_COMPRESS:
                self.logger.debug(f"压缩：{file_path.name} ({age_days}天)")
                self.compress_archive_file(file_path)
    
    def cleanup_expired(self):
        self.logger.info("清理过期文件...")
        
        archive_files = list(self.archive_dir.rglob("*.md"))
        archive_files += list(self.archive_dir.rglob("*.md.gz"))
        self.logger.info(f"找到 {len(archive_files)} 个归档文件")
        
        for file_path in archive_files:
            age_days = self.get_file_age_days(file_path)
            
            if age_days >= DAYS_TO_DELETE:
                self.logger.debug(f"删除过期文件：{file_path.name} ({age_days}天)")
                self.delete_expired_file(file_path)
        
        self.logger.info("清理旧快照...")
        if self.snapshots_dir.exists():
            snapshot_files = list(self.snapshots_dir.glob("*.json"))
            for file_path in snapshot_files:
                if file_path.name == "current_session.json":
                    continue
                
                age_days = self.get_file_age_days(file_path)
                if age_days >= 30:
                    self.logger.debug(f"删除旧快照：{file_path.name}")
                    self.delete_expired_file(file_path)
    
    def run(self, full: bool = False) -> Dict[str, Any]:
        self.logger.info("=" * 60)
        self.logger.info("🗄️  Memory Suite v3 - 归档系统")
        self.logger.info(f"⏰ 运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 60)
        
        self.stats = {
            "archived": 0,
            "permanent": 0,
            "compressed": 0,
            "deleted": 0,
            "errors": []
        }
        
        self.archive_daily_memories()
        self.create_permanent_records()
        
        if full:
            self.compress_old_archives()
            self.cleanup_expired()
        
        self.logger.info("=" * 60)
        self.logger.info("📊 归档统计")
        self.logger.info("=" * 60)
        self.logger.info(f"已归档：{self.stats['archived']} 个文件")
        self.logger.info(f"永久记录：{self.stats['permanent']} 个")
        self.logger.info(f"已压缩：{self.stats['compressed']} 个文件")
        self.logger.info(f"已删除：{self.stats['deleted']} 个文件")
        
        if self.stats["errors"]:
            self.logger.warn(f"错误 ({len(self.stats['errors'])}):")
            for error in self.stats["errors"]:
                self.logger.warn(f"  - {error}")
        
        self.logger.info("✅ 归档完成")
        
        return self.stats
    
    def get_stats(self) -> Dict[str, Any]:
        return self.stats
    
    def save_log(self, log_file: Optional[Path] = None):
        if log_file is None:
            log_file = self.archive_dir / "archive_log.json"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "stats": self.stats
        }
        
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except Exception:
                logs = []
        
        logs.append(log_entry)
        logs = logs[-100:]
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
        
        self.logger.debug(f"日志已保存：{log_file}")


# ============================================================================
# 全局实例（单例模式）
# ============================================================================

_archiver_instance: Optional[Archiver] = None


def get_archiver(memory_dir: Optional[Path] = None,
                 archive_dir: Optional[Path] = None,
                 permanent_dir: Optional[Path] = None,
                 workspace: Optional[Path] = None) -> Archiver:
    """获取全局归档器实例"""
    global _archiver_instance
    if _archiver_instance is None:
        _archiver_instance = Archiver(
            memory_dir=memory_dir,
            archive_dir=archive_dir,
            permanent_dir=permanent_dir,
            workspace=workspace
        )
    return _archiver_instance


def run_archive(full: bool = False) -> Dict[str, Any]:
    """运行归档任务"""
    archiver = get_archiver()
    return archiver.run(full=full)


def archive_daily() -> int:
    """归档每日记忆"""
    archiver = get_archiver()
    archiver.archive_daily_memories()
    return archiver.stats["archived"]


def create_permanent() -> int:
    """创建永久记录"""
    archiver = get_archiver()
    archiver.create_permanent_records()
    return archiver.stats["permanent"]


def compress_archives() -> int:
    """压缩旧归档"""
    archiver = get_archiver()
    archiver.compress_old_archives()
    return archiver.stats["compressed"]


def cleanup_expired() -> int:
    """清理过期文件"""
    archiver = get_archiver()
    archiver.cleanup_expired()
    return archiver.stats["deleted"]


# ============================================================================
# 命令行接口
# ============================================================================

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Memory Suite v3 - 归档模块")
    parser.add_argument("action",
                       choices=["run", "archive", "permanent", "compress", "cleanup", "status"],
                       help="执行的操作")
    parser.add_argument("--full", "-f",
                       action="store_true",
                       help="运行完整流程（包括压缩和删除）")
    parser.add_argument("--memory-dir", "-m",
                       help="记忆目录",
                       default=str(DEFAULT_MEMORY_DIR))
    parser.add_argument("--workspace", "-w",
                       help="工作空间路径",
                       default=str(DEFAULT_WORKSPACE))
    
    args = parser.parse_args()
    
    memory_dir = Path(args.memory_dir)
    workspace = Path(args.workspace)
    
    if args.action == "run":
        archiver = get_archiver(memory_dir, workspace=workspace)
        stats = archiver.run(full=args.full)
        archiver.save_log()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    elif args.action == "archive":
        archiver = get_archiver(memory_dir, workspace=workspace)
        archiver.archive_daily_memories()
        print(f"✅ 已归档 {archiver.stats['archived']} 个文件")
    
    elif args.action == "permanent":
        archiver = get_archiver(memory_dir, workspace=workspace)
        archiver.create_permanent_records()
        print(f"✅ 已创建 {archiver.stats['permanent']} 个永久记录")
    
    elif args.action == "compress":
        archiver = get_archiver(memory_dir, workspace=workspace)
        archiver.compress_old_archives()
        print(f"✅ 已压缩 {archiver.stats['compressed']} 个文件")
    
    elif args.action == "cleanup":
        archiver = get_archiver(memory_dir, workspace=workspace)
        archiver.cleanup_expired()
        print(f"✅ 已删除 {archiver.stats['deleted']} 个文件")
    
    elif args.action == "status":
        archiver = get_archiver(memory_dir, workspace=workspace)
        stats = archiver.get_stats()
        
        daily_count = len(list(memory_dir.glob("*.md")))
        archive_count = len(list(archiver.archive_dir.rglob("*.md")))
        archive_count += len(list(archiver.archive_dir.rglob("*.md.gz")))
        permanent_count = len(list(archiver.permanent_dir.glob("*.json")))
        
        status = {
            "daily_files": daily_count,
            "archived_files": archive_count,
            "permanent_records": permanent_count,
            "last_stats": stats
        }
        print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
