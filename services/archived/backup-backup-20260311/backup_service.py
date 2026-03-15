#!/usr/bin/env python3
"""
Backup Service - 智能备份服务
支持去重、增量备份、自动清理
"""

import hashlib
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Set

WORKSPACE = Path.home() / ".openclaw" / "workspace"
BACKUP_DIR = Path("/Volumes/cu/ocu")


class BackupService:
    """智能备份服务"""
    
    def __init__(self, backup_dir: Optional[Path] = None):
        self.backup_dir = backup_dir or BACKUP_DIR
        self.fingerprints_file = self.backup_dir / ".backup_fingerprints.json"
        
    def calculate_fingerprint(self, file_path: Path) -> str:
        """计算文件指纹"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
        
    def load_fingerprints(self) -> Dict:
        """加载指纹数据库"""
        if self.fingerprints_file.exists():
            return json.loads(self.fingerprints_file.read_text(encoding='utf-8'))
        return {}
        
    def save_fingerprints(self, fingerprints: Dict):
        """保存指纹数据库"""
        self.fingerprints_file.write_text(
            json.dumps(fingerprints, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        
    def smart_backup(self, source: Path, dest: Path) -> Dict:
        """智能备份（去重）"""
        fingerprints = self.load_fingerprints()
        stats = {"backed_up": 0, "deduplicated": 0, "errors": 0}
        
        for file in source.rglob("*"):
            if not file.is_file():
                continue
                
            try:
                # 计算指纹
                fp = self.calculate_fingerprint(file)
                
                # 检查是否已存在
                if fp in fingerprints:
                    stats["deduplicated"] += 1
                    continue
                    
                # 复制文件
                rel_path = file.relative_to(source)
                dest_file = dest / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, dest_file)
                
                # 记录指纹
                fingerprints[fp] = {
                    "path": str(rel_path),
                    "size": file.stat().st_size,
                    "mtime": file.stat().st_mtime
                }
                
                stats["backed_up"] += 1
                
            except Exception as e:
                print(f"❌ 备份失败 {file}: {e}")
                stats["errors"] += 1
                
        self.save_fingerprints(fingerprints)
        return stats
        
    def incremental_backup(self, source: Path, dest: Path, last_backup: Optional[datetime] = None) -> Dict:
        """增量备份"""
        if last_backup is None:
            last_backup = datetime.now() - timedelta(days=1)
            
        stats = {"backed_up": 0, "skipped": 0, "errors": 0}
        
        for file in source.rglob("*"):
            if not file.is_file():
                continue
                
            # 检查修改时间
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            if mtime <= last_backup:
                stats["skipped"] += 1
                continue
                
            try:
                rel_path = file.relative_to(source)
                dest_file = dest / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, dest_file)
                stats["backed_up"] += 1
            except Exception as e:
                print(f"❌ 备份失败 {file}: {e}")
                stats["errors"] += 1
                
        return stats
        
    def cleanup_old_backups(self, keep_daily: int = 7, keep_weekly: int = 4, keep_monthly: int = 12):
        """清理旧备份"""
        backup_files = sorted(
            self.backup_dir.glob("backup-*.tar.gz"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        to_keep = set()
        
        # 保留最近N天
        for f in backup_files[:keep_daily]:
            to_keep.add(f)
            
        # 保留每周一个
        weekly_count = 0
        last_week = None
        for f in backup_files:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            week = mtime.isocalendar()[1]
            if week != last_week and weekly_count < keep_weekly:
                to_keep.add(f)
                last_week = week
                weekly_count += 1
                
        # 保留每月一个
        monthly_count = 0
        last_month = None
        for f in backup_files:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            month = mtime.month
            if month != last_month and monthly_count < keep_monthly:
                to_keep.add(f)
                last_month = month
                monthly_count += 1
                
        # 删除其他
        deleted = 0
        for f in backup_files:
            if f not in to_keep:
                f.unlink()
                deleted += 1
                
        return {"kept": len(to_keep), "deleted": deleted}


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='智能备份服务')
    parser.add_argument('--smart', action='store_true', help='智能去重备份')
    parser.add_argument('--incremental', action='store_true', help='增量备份')
    parser.add_argument('--cleanup', action='store_true', help='清理旧备份')
    parser.add_argument('--source', '-s', help='源目录')
    parser.add_argument('--dest', '-d', help='目标目录')
    
    args = parser.parse_args()
    
    service = BackupService()
    
    if args.smart and args.source and args.dest:
        stats = service.smart_backup(Path(args.source), Path(args.dest))
        print(f"✅ 智能备份完成: {stats}")
    elif args.incremental and args.source and args.dest:
        stats = service.incremental_backup(Path(args.source), Path(args.dest))
        print(f"✅ 增量备份完成: {stats}")
    elif args.cleanup:
        stats = service.cleanup_old_backups()
        print(f"✅ 清理完成: 保留 {stats['kept']}, 删除 {stats['deleted']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
