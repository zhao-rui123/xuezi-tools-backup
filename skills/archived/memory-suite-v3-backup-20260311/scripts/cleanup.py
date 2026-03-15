#!/usr/bin/env python3
"""
Memory Suite v3.0 - 清理脚本
自动清理临时文件和过期数据
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# 配置
WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
SNAPSHOTS_DIR = MEMORY_DIR / "snapshots"
ARCHIVE_DIR = MEMORY_DIR / "archive"

# 清理配置
CLEANUP_CONFIG = {
    "temp_files": {
        "pattern": "*.tmp",
        "max_age_days": 1,
    },
    "old_snapshots": {
        "max_age_days": 30,
        "keep_min": 10,  # 至少保留10个
    },
    "session_backups": {
        "max_age_days": 7,
    },
}

def clean_temp_files():
    """清理临时文件"""
    print("🧹 清理临时文件...")
    cleaned = 0
    
    for temp_file in WORKSPACE.rglob("*.tmp"):
        try:
            temp_file.unlink()
            cleaned += 1
            print(f"  🗑️  {temp_file.name}")
        except Exception as e:
            print(f"  ⚠️  清理失败 {temp_file}: {e}")
    
    print(f"✅ 清理了 {cleaned} 个临时文件")
    return cleaned

def clean_old_snapshots():
    """清理旧快照文件"""
    print("🧹 清理旧快照...")
    
    cutoff_date = datetime.now() - timedelta(days=CLEANUP_CONFIG["old_snapshots"]["max_age_days"])
    min_keep = CLEANUP_CONFIG["old_snapshots"]["keep_min"]
    
    # 获取所有session快照（不包括current_session.json）
    snapshots = sorted(
        [f for f in SNAPSHOTS_DIR.glob("session_*.json")],
        key=lambda p: p.stat().st_mtime
    )
    
    if len(snapshots) <= min_keep:
        print(f"✅ 快照数量 ({len(snapshots)}) 未超过保留阈值 ({min_keep})，无需清理")
        return 0
    
    # 保留最新的min_keep个，清理其余的
    to_clean = snapshots[:-min_keep]
    cleaned = 0
    
    for snapshot in to_clean:
        try:
            mtime = datetime.fromtimestamp(snapshot.stat().st_mtime)
            if mtime < cutoff_date:
                snapshot.unlink()
                cleaned += 1
                print(f"  🗑️  {snapshot.name}")
        except Exception as e:
            print(f"  ⚠️  清理失败 {snapshot}: {e}")
    
    print(f"✅ 清理了 {cleaned} 个旧快照")
    return cleaned

def clean_session_backups():
    """清理session备份文件"""
    print("🧹 清理session备份...")
    
    cutoff_date = datetime.now() - timedelta(days=CLEANUP_CONFIG["session_backups"]["max_age_days"])
    cleaned = 0
    
    for backup_file in SNAPSHOTS_DIR.glob("snapshot_*.json"):
        try:
            mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if mtime < cutoff_date:
                backup_file.unlink()
                cleaned += 1
                print(f"  🗑️  {backup_file.name}")
        except Exception as e:
            print(f"  ⚠️  清理失败 {backup_file}: {e}")
    
    print(f"✅ 清理了 {cleaned} 个session备份")
    return cleaned

def get_directory_size(path):
    """获取目录大小"""
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += get_directory_size(entry.path)
    return total

def print_stats():
    """打印统计信息"""
    print("\n📊 清理后统计:")
    print(f"  记忆目录大小: {get_directory_size(MEMORY_DIR) / (1024*1024):.1f} MB")
    print(f"  快照文件数量: {len(list(SNAPSHOTS_DIR.glob('*.json')))}")

def main():
    """主函数"""
    print("=" * 60)
    print("Memory Suite v3.0 - 系统清理")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    total_cleaned = 0
    
    # 执行清理
    total_cleaned += clean_temp_files()
    print()
    
    total_cleaned += clean_old_snapshots()
    print()
    
    total_cleaned += clean_session_backups()
    print()
    
    # 打印统计
    print_stats()
    print()
    
    print("=" * 60)
    print(f"清理完成，共清理 {total_cleaned} 个文件")
    print("=" * 60)

if __name__ == "__main__":
    main()
