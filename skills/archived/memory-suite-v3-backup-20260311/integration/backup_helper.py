#!/usr/bin/env python3
"""
备份协助模块 (Backup Helper)
Memory Suite v3.0 - Phase 3

功能：
1. 与备份系统协作
2. 预备份检查
3. 备份后清理
4. 备份状态管理

作者: 雪子助手
版本: 3.0.0
日期: 2026-03-11
"""

import os
import json
import shutil
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# 配置路径
WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
BACKUP_DIR = WORKSPACE / "backups" / "memory-suite"
BACKUP_LOG_FILE = MEMORY_DIR / "backup_log.json"

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('backup_helper')


class BackupStatus(Enum):
    """备份状态"""
    PENDING = "pending"           # 待备份
    IN_PROGRESS = "in_progress"   # 备份中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 失败
    CLEANED = "cleaned"           # 已清理


@dataclass
class BackupRecord:
    """备份记录"""
    id: str
    timestamp: str
    source_dir: str
    backup_path: str
    size_bytes: int
    file_count: int
    status: str
    duration_seconds: float
    error: Optional[str] = None
    cleanup_done: bool = False
    notes: str = ""


class BackupHelper:
    """备份协助器"""
    
    # 备份保留策略
    KEEP_DAILY = 7      # 保留 7 天的日备份
    KEEP_WEEKLY = 4     # 保留 4 周的周备份
    KEEP_MONTHLY = 12   # 保留 12 个月的月备份
    
    def __init__(self, workspace: Optional[Path] = None):
        """
        初始化备份协助器
        
        Args:
            workspace: 工作空间路径
        """
        self.workspace = workspace or WORKSPACE
        self.memory_dir = self.workspace / "memory"
        self.backup_dir = self.workspace / "backups" / "memory-suite"
        self.log_file = self.memory_dir / "backup_log.json"
        
        self.backup_records: List[BackupRecord] = []
        
        self._ensure_directories()
        self._load_backup_log()
    
    def _ensure_directories(self):
        """确保必要目录存在"""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"确保备份目录存在：{self.backup_dir}")
    
    def _load_backup_log(self):
        """加载备份日志"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.backup_records = [BackupRecord(**r) for r in data.get("records", [])]
                logger.debug(f"加载了 {len(self.backup_records)} 条备份记录")
            except Exception as e:
                logger.warning(f"加载备份日志失败：{e}")
                self.backup_records = []
        else:
            self.backup_records = []
    
    def _save_backup_log(self):
        """保存备份日志"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "total_backups": len(self.backup_records),
                "records": [asdict(r) for r in self.backup_records[-100:]]  # 保留最近 100 条
            }
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug("保存了备份日志")
        except Exception as e:
            logger.error(f"保存备份日志失败：{e}")
    
    def pre_backup_check(self) -> Dict[str, Any]:
        """
        预备份检查
        
        Returns:
            检查结果
        """
        logger.info("🔍 执行预备份检查...")
        
        checks = {
            "passed": True,
            "timestamp": datetime.now().isoformat(),
            "items": []
        }
        
        # 1. 检查源目录是否存在
        if self.memory_dir.exists():
            checks["items"].append({
                "name": "源目录存在",
                "status": "pass",
                "message": f"memory 目录存在：{self.memory_dir}"
            })
        else:
            checks["items"].append({
                "name": "源目录存在",
                "status": "fail",
                "message": f"memory 目录不存在：{self.memory_dir}"
            })
            checks["passed"] = False
        
        # 2. 检查备份目录是否可写
        try:
            test_file = self.backup_dir / ".write_test"
            test_file.touch()
            test_file.unlink()
            checks["items"].append({
                "name": "备份目录可写",
                "status": "pass",
                "message": f"备份目录可写：{self.backup_dir}"
            })
        except Exception as e:
            checks["items"].append({
                "name": "备份目录可写",
                "status": "fail",
                "message": f"备份目录不可写：{e}"
            })
            checks["passed"] = False
        
        # 3. 检查磁盘空间
        try:
            import os
            stat = os.statvfs(self.backup_dir)
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024 ** 3)
            
            if free_gb >= 1.0:
                checks["items"].append({
                    "name": "磁盘空间充足",
                    "status": "pass",
                    "message": f"可用空间：{free_gb:.2f} GB"
                })
            else:
                checks["items"].append({
                    "name": "磁盘空间充足",
                    "status": "warning",
                    "message": f"可用空间不足：{free_gb:.2f} GB"
                })
        except Exception as e:
            checks["items"].append({
                "name": "磁盘空间检查",
                "status": "warning",
                "message": f"无法检查磁盘空间：{e}"
            })
        
        # 4. 检查上次备份时间
        last_backup = self._get_last_backup_time()
        if last_backup:
            hours_since = (datetime.now() - last_backup).total_seconds() / 3600
            if hours_since < 1:
                checks["items"].append({
                    "name": "备份间隔",
                    "status": "warning",
                    "message": f"距离上次备份仅 {hours_since:.1f} 小时"
                })
            else:
                checks["items"].append({
                    "name": "备份间隔",
                    "status": "pass",
                    "message": f"距离上次备份 {hours_since:.1f} 小时"
                })
        else:
            checks["items"].append({
                "name": "备份间隔",
                "status": "pass",
                "message": "首次备份"
            })
        
        # 5. 统计待备份文件
        file_count = self._count_memory_files()
        checks["items"].append({
            "name": "待备份文件",
            "status": "info",
            "message": f"共 {file_count} 个文件"
        })
        
        # 总结
        passed = sum(1 for item in checks["items"] if item["status"] == "pass")
        failed = sum(1 for item in checks["items"] if item["status"] == "fail")
        warnings = sum(1 for item in checks["items"] if item["status"] == "warning")
        
        checks["summary"] = {
            "total": len(checks["items"]),
            "passed": passed,
            "failed": failed,
            "warnings": warnings
        }
        
        if checks["passed"]:
            logger.info(f"  ✅ 预备份检查通过 ({passed} 通过，{warnings} 警告)")
        else:
            logger.warning(f"  ⚠️ 预备份检查失败 ({failed} 失败)")
        
        return checks
    
    def create_backup(
        self,
        source_dir: Optional[Path] = None,
        backup_name: Optional[str] = None,
        compress: bool = True
    ) -> Dict[str, Any]:
        """
        创建备份
        
        Args:
            source_dir: 源目录，默认使用 memory_dir
            backup_name: 备份名称，默认使用时间戳
            compress: 是否压缩
            
        Returns:
            备份结果
        """
        source = source_dir or self.memory_dir
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = backup_name or f"memory_backup_{timestamp}"
        
        if compress:
            backup_path = self.backup_dir / f"{backup_name}.tar.gz"
        else:
            backup_path = self.backup_dir / backup_name
        
        logger.info(f"💾 开始备份：{source} -> {backup_path}")
        
        # 创建备份记录
        record = BackupRecord(
            id=f"backup_{timestamp}",
            timestamp=timestamp,
            source_dir=str(source),
            backup_path=str(backup_path),
            size_bytes=0,
            file_count=0,
            status=BackupStatus.IN_PROGRESS.value,
            duration_seconds=0.0
        )
        
        start_time = datetime.now()
        
        try:
            # 统计文件数量
            record.file_count = self._count_files_in_dir(source)
            
            # 执行备份
            if compress:
                self._create_tar_backup(source, backup_path)
            else:
                self._create_copy_backup(source, backup_path)
            
            # 计算备份大小
            record.size_bytes = backup_path.stat().st_size if backup_path.exists() else 0
            
            # 计算耗时
            end_time = datetime.now()
            record.duration_seconds = (end_time - start_time).total_seconds()
            
            # 更新状态
            record.status = BackupStatus.COMPLETED.value
            
            # 添加到记录
            self.backup_records.append(record)
            self._save_backup_log()
            
            # 打印摘要
            size_mb = record.size_bytes / (1024 * 1024)
            logger.info(f"  ✅ 备份完成：{record.file_count} 个文件，{size_mb:.2f} MB，耗时 {record.duration_seconds:.2f} 秒")
            
            return {
                "success": True,
                "backup_path": str(backup_path),
                "size_bytes": record.size_bytes,
                "file_count": record.file_count,
                "duration_seconds": record.duration_seconds
            }
            
        except Exception as e:
            record.status = BackupStatus.FAILED.value
            record.error = str(e)
            
            self.backup_records.append(record)
            self._save_backup_log()
            
            logger.error(f"  ❌ 备份失败：{e}")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_tar_backup(self, source: Path, backup_path: Path):
        """创建 tar 压缩备份"""
        import tarfile
        
        with tarfile.open(backup_path, "w:gz") as tar:
            tar.add(source, arcname=source.name)
    
    def _create_copy_backup(self, source: Path, backup_path: Path):
        """创建复制备份"""
        if backup_path.exists():
            shutil.rmtree(backup_path)
        shutil.copytree(source, backup_path)
    
    def _count_files_in_dir(self, directory: Path) -> int:
        """统计目录中的文件数量"""
        count = 0
        try:
            for item in directory.rglob("*"):
                if item.is_file():
                    count += 1
        except Exception as e:
            logger.warning(f"统计文件数量失败：{e}")
        return count
    
    def post_backup_cleanup(
        self,
        keep_days: int = 7,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        备份后清理
        
        Args:
            keep_days: 保留天数
            dry_run: 是否仅模拟（不实际删除）
            
        Returns:
            清理结果
        """
        logger.info(f"🧹 开始清理旧备份（保留 {keep_days} 天）...")
        
        cutoff = datetime.now() - timedelta(days=keep_days)
        
        cleaned = []
        kept = []
        total_size_freed = 0
        
        # 扫描备份文件
        for backup_file in self.backup_dir.glob("*"):
            if backup_file.is_file():
                # 获取文件修改时间
                mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                
                if mtime < cutoff:
                    # 需要清理
                    file_size = backup_file.stat().st_size
                    
                    if dry_run:
                        logger.info(f"  将删除：{backup_file.name} ({file_size / 1024 / 1024:.2f} MB)")
                    else:
                        try:
                            backup_file.unlink()
                            logger.info(f"  已删除：{backup_file.name}")
                        except Exception as e:
                            logger.warning(f"  删除失败 {backup_file.name}: {e}")
                            continue
                    
                    cleaned.append({
                        "file": str(backup_file),
                        "size_bytes": file_size,
                        "modified": mtime.isoformat()
                    })
                    total_size_freed += file_size
                else:
                    kept.append(str(backup_file.name))
        
        # 更新备份记录状态
        for record in self.backup_records:
            record_path = Path(record.backup_path)
            if record_path.name in [Path(c["file"]).name for c in cleaned]:
                record.cleanup_done = True
        
        if not dry_run:
            self._save_backup_log()
        
        # 打印摘要
        logger.info(f"  ✅ 清理完成：删除 {len(cleaned)} 个文件，释放 {total_size_freed / 1024 / 1024:.2f} MB")
        
        return {
            "cleaned_count": len(cleaned),
            "kept_count": len(kept),
            "size_freed_bytes": total_size_freed,
            "dry_run": dry_run,
            "cleaned_files": cleaned if not dry_run else []
        }
    
    def apply_retention_policy(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        应用备份保留策略
        
        保留策略：
        - 保留最近 7 天的日备份
        - 保留最近 4 周的周备份
        - 保留最近 12 个月的月备份
        
        Args:
            dry_run: 是否仅模拟
            
        Returns:
            清理结果
        """
        logger.info("📋 应用备份保留策略...")
        
        now = datetime.now()
        
        # 分类备份文件
        backups_by_date = []
        
        for backup_file in self.backup_dir.glob("*"):
            if backup_file.is_file() and backup_file.suffix in ['.gz', '.tar']:
                mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                backups_by_date.append({
                    "path": backup_file,
                    "mtime": mtime,
                    "size": backup_file.stat().st_size
                })
        
        # 按时间排序
        backups_by_date.sort(key=lambda x: x["mtime"], reverse=True)
        
        # 应用保留策略
        to_keep = set()
        
        # 日备份：最近 7 天
        daily_cutoff = now - timedelta(days=self.KEEP_DAILY)
        for backup in backups_by_date:
            if backup["mtime"] >= daily_cutoff:
                to_keep.add(str(backup["path"]))
        
        # 周备份：最近 4 周，每周保留一个
        weekly_cutoff = now - timedelta(weeks=self.KEEP_WEEKLY)
        seen_weeks = set()
        for backup in backups_by_date:
            if backup["mtime"] < daily_cutoff and backup["mtime"] >= weekly_cutoff:
                week_key = backup["mtime"].strftime('%Y-W%W')
                if week_key not in seen_weeks:
                    to_keep.add(str(backup["path"]))
                    seen_weeks.add(week_key)
        
        # 月备份：最近 12 个月，每月保留一个
        monthly_cutoff = now - timedelta(weeks=self.KEEP_MONTHLY * 4)
        seen_months = set()
        for backup in backups_by_date:
            if backup["mtime"] < weekly_cutoff and backup["mtime"] >= monthly_cutoff:
                month_key = backup["mtime"].strftime('%Y-%m')
                if month_key not in seen_months:
                    to_keep.add(str(backup["path"]))
                    seen_months.add(month_key)
        
        # 删除不需要的备份
        to_delete = []
        total_size_freed = 0
        
        for backup in backups_by_date:
            if str(backup["path"]) not in to_keep:
                if not dry_run:
                    try:
                        backup["path"].unlink()
                        logger.info(f"  已删除：{backup['path'].name}")
                    except Exception as e:
                        logger.warning(f"  删除失败 {backup['path'].name}: {e}")
                        continue
                
                to_delete.append({
                    "file": str(backup["path"]),
                    "size_bytes": backup["size"],
                    "modified": backup["mtime"].isoformat()
                })
                total_size_freed += backup["size"]
        
        logger.info(f"  ✅ 策略应用完成：删除 {len(to_delete)} 个文件，释放 {total_size_freed / 1024 / 1024:.2f} MB")
        
        return {
            "deleted_count": len(to_delete),
            "kept_count": len(to_keep),
            "size_freed_bytes": total_size_freed,
            "dry_run": dry_run,
            "deleted_files": to_delete if not dry_run else []
        }
    
    def _get_last_backup_time(self) -> Optional[datetime]:
        """获取上次备份时间"""
        if not self.backup_records:
            return None
        
        # 找到最近的成功备份
        for record in reversed(self.backup_records):
            if record.status == BackupStatus.COMPLETED.value:
                try:
                    return datetime.fromisoformat(record.timestamp)
                except:
                    pass
        
        return None
    
    def _count_memory_files(self) -> int:
        """统计记忆文件数量"""
        return self._count_files_in_dir(self.memory_dir)
    
    def get_backup_stats(self) -> Dict[str, Any]:
        """获取备份统计"""
        total_backups = len(self.backup_records)
        successful = sum(1 for r in self.backup_records if r.status == BackupStatus.COMPLETED.value)
        failed = sum(1 for r in self.backup_records if r.status == BackupStatus.FAILED.value)
        
        total_size = sum(r.size_bytes for r in self.backup_records if r.status == BackupStatus.COMPLETED.value)
        
        # 当前备份目录大小
        current_size = sum(
            f.stat().st_size for f in self.backup_dir.glob("*") if f.is_file()
        )
        
        return {
            "total_backups": total_backups,
            "successful": successful,
            "failed": failed,
            "total_size_bytes": total_size,
            "current_backup_size_bytes": current_size,
            "last_backup": self._get_last_backup_time().isoformat() if self._get_last_backup_time() else None,
            "backup_files_count": len(list(self.backup_dir.glob("*")))
        }
    
    def list_backups(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        列出备份记录
        
        Args:
            limit: 返回数量限制
            
        Returns:
            备份记录列表
        """
        records = sorted(
            self.backup_records,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]
        
        return [asdict(r) for r in records]
    
    def restore_backup(
        self,
        backup_path: str,
        target_dir: Optional[Path] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        恢复备份
        
        Args:
            backup_path: 备份文件路径
            target_dir: 恢复目标目录，默认恢复到 memory_dir
            dry_run: 是否仅模拟
            
        Returns:
            恢复结果
        """
        backup_file = Path(backup_path)
        target = target_dir or self.memory_dir
        
        logger.info(f"🔄 恢复备份：{backup_file} -> {target}")
        
        if not backup_file.exists():
            return {
                "success": False,
                "error": f"备份文件不存在：{backup_path}"
            }
        
        try:
            if dry_run:
                logger.info(f"  [模拟] 将恢复到：{target}")
                return {
                    "success": True,
                    "dry_run": True,
                    "target": str(target)
                }
            
            # 备份当前数据（以防万一）
            if target.exists():
                emergency_backup = target.parent / f"{target.name}_emergency_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                logger.info(f"  创建紧急备份：{emergency_backup}")
                shutil.move(target, emergency_backup)
            
            # 恢复备份
            if backup_file.suffix == '.gz':
                import tarfile
                with tarfile.open(backup_file, "r:gz") as tar:
                    tar.extractall(target.parent)
            else:
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(backup_file, target)
            
            logger.info(f"  ✅ 恢复完成")
            
            return {
                "success": True,
                "target": str(target),
                "backup": str(backup_file)
            }
            
        except Exception as e:
            logger.error(f"  ❌ 恢复失败：{e}")
            return {
                "success": False,
                "error": str(e)
            }


def main():
    """主函数 - 用于命令行调用"""
    import argparse
    
    parser = argparse.ArgumentParser(description='备份协助模块')
    parser.add_argument('--action', '-a', type=str, required=True,
                       choices=['check', 'backup', 'cleanup', 'policy', 'stats', 'list', 'restore'],
                       help='操作类型')
    parser.add_argument('--source', '-s', type=str, help='源目录路径')
    parser.add_argument('--target', '-t', type=str, help='目标目录路径')
    parser.add_argument('--backup', '-b', type=str, help='备份文件路径（用于恢复）')
    parser.add_argument('--keep-days', '-k', type=int, default=7, help='保留天数')
    parser.add_argument('--dry-run', '-n', action='store_true', help='模拟执行')
    parser.add_argument('--compress', '-c', action='store_true', help='压缩备份')
    
    args = parser.parse_args()
    
    helper = BackupHelper()
    
    if args.action == 'check':
        result = helper.pre_backup_check()
    elif args.action == 'backup':
        source = Path(args.source) if args.source else None
        result = helper.create_backup(source_dir=source, compress=args.compress)
    elif args.action == 'cleanup':
        result = helper.post_backup_cleanup(keep_days=args.keep_days, dry_run=args.dry_run)
    elif args.action == 'policy':
        result = helper.apply_retention_policy(dry_run=args.dry_run)
    elif args.action == 'stats':
        result = helper.get_backup_stats()
    elif args.action == 'list':
        result = {"backups": helper.list_backups()}
    elif args.action == 'restore':
        if not args.backup:
            print("错误：恢复操作需要指定 --backup 参数")
            return 1
        target = Path(args.target) if args.target else None
        result = helper.restore_backup(args.backup, target_dir=target, dry_run=args.dry_run)
    else:
        print(f"未知操作：{args.action}")
        return 1
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success", True) else 1


if __name__ == "__main__":
    exit(main())
