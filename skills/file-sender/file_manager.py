#!/usr/bin/env python3
"""
文件管理工具 - 整合自 file-management
功能：工作区文件组织和清理
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE_DIR = Path("/Users/zhaoruicn/.openclaw/workspace")
TMP_DIR = WORKSPACE_DIR / "tmp"


def cleanup_temp_files():
    """清理临时文件"""
    print("🧹 清理临时文件...")
    
    cleaned = 0
    
    # 清理7天前的截图
    screenshots_dir = TMP_DIR / "screenshots"
    if screenshots_dir.exists():
        for file in screenshots_dir.glob("*"):
            if file.is_file():
                file_age = (datetime.now() - datetime.fromtimestamp(file.stat().st_mtime)).days
                if file_age > 7:
                    file.unlink()
                    cleaned += 1
    
    # 清理7天前的下载文件
    downloads_dir = TMP_DIR / "downloads"
    if downloads_dir.exists():
        for file in downloads_dir.glob("*"):
            if file.is_file():
                file_age = (datetime.now() - datetime.fromtimestamp(file.stat().st_mtime)).days
                if file_age > 7:
                    file.unlink()
                    cleaned += 1
    
    print(f"  清理了 {cleaned} 个临时文件")
    return cleaned


def ensure_directory_structure():
    """确保目录结构完整"""
    dirs = [
        TMP_DIR / "screenshots",
        TMP_DIR / "downloads",
        TMP_DIR / "cache",
        WORKSPACE_DIR / "reports" / "daily",
        WORKSPACE_DIR / "reports" / "weekly",
        WORKSPACE_DIR / "assets" / "images",
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    
    print("✅ 目录结构检查完成")


def get_file_size(path: Path) -> str:
    """获取文件大小"""
    size = path.stat().st_size
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def find_large_files(max_size_mb: int = 10):
    """查找大文件"""
    print(f"🔍 查找大于 {max_size_mb}MB 的文件...")
    
    large_files = []
    max_size_bytes = max_size_mb * 1024 * 1024
    
    for file_path in WORKSPACE_DIR.rglob("*"):
        if file_path.is_file():
            try:
                if file_path.stat().st_size > max_size_bytes:
                    large_files.append({
                        "path": file_path,
                        "size": get_file_size(file_path)
                    })
            except:
                continue
    
    large_files.sort(key=lambda x: x["path"].stat().st_size, reverse=True)
    
    if large_files:
        print(f"  发现 {len(large_files)} 个大文件:")
        for f in large_files[:10]:
            print(f"    - {f['path'].relative_to(WORKSPACE_DIR)}: {f['size']}")
    else:
        print("  未发现大文件")
    
    return large_files


def manage_files():
    """运行文件管理"""
    print("=" * 60)
    print("📁 文件管理工具")
    print("=" * 60)
    
    # 确保目录结构
    ensure_directory_structure()
    
    # 清理临时文件
    cleanup_temp_files()
    
    # 查找大文件
    find_large_files()
    
    print("\n✅ 文件管理完成")


if __name__ == "__main__":
    manage_files()
