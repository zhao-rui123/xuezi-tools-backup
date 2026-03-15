#!/usr/bin/env python3
"""
Memory Suite v4.0 - 统一日志轮转脚本
整合所有日志轮转功能，统一处理 /tmp/memory-suite.log
"""

import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# 配置
LOG_FILE = Path("/tmp/memory-suite.log")
ARCHIVE_DIR = Path("/tmp/memory-suite-archives")
MAX_LOG_SIZE_MB = 10          # 超过10MB触发轮转
MAX_LOG_DAYS = 30             # 日志保留30天
MAX_ARCHIVED_LOGS = 10        # 保留10个归档文件
COMPRESS_THRESHOLD_DAYS = 7   # 7天前的日志压缩


def ensure_archive_dir():
    """确保归档目录存在"""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)


def rotate_log():
    """
    轮转当前日志文件
    当日志超过大小时，创建时间戳命名的备份
    """
    if not LOG_FILE.exists():
        print("ℹ️ 日志文件不存在，无需轮转")
        return False
        
    # 检查文件大小
    size_mb = LOG_FILE.stat().st_size / (1024 * 1024)
    if size_mb < MAX_LOG_SIZE_MB:
        print(f"ℹ️ 日志文件大小 {size_mb:.1f}MB，未超过 {MAX_LOG_SIZE_MB}MB，无需轮转")
        return False
    
    ensure_archive_dir()
    
    # 生成归档文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archived_file = ARCHIVE_DIR / f"memory-suite-{timestamp}.log"
    
    try:
        # 移动并压缩
        shutil.move(str(LOG_FILE), str(archived_file))
        
        with open(archived_file, 'rb') as f_in:
            with gzip.open(f"{archived_file}.gz", 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
                
        # 删除未压缩版本
        archived_file.unlink()
        
        # 创建新的空日志文件
        LOG_FILE.write_text(f"# Memory Suite v4.0 日志\n# 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        print(f"✅ 日志已轮转: {archived_file.name}.gz")
        return True
        
    except Exception as e:
        print(f"❌ 轮转失败: {e}")
        return False


def clean_old_logs():
    """
    清理旧日志文件
    - 删除超过 MAX_LOG_DAYS 天的日志
    - 只保留最新的 MAX_ARCHIVED_LOGS 个归档文件
    """
    ensure_archive_dir()
    
    cleaned = 0
    cutoff_date = datetime.now() - timedelta(days=MAX_LOG_DAYS)
    
    # 清理旧归档文件
    for log_file in ARCHIVE_DIR.glob("memory-suite-*.log*"):
        try:
            # 从文件名提取日期
            file_date_str = log_file.name.split('-')[2]  # memory-suite-YYYYMMDD_HHMMSS.log.gz
            file_date = datetime.strptime(file_date_str[:8], "%Y%m%d")
            
            if file_date < cutoff_date:
                log_file.unlink()
                cleaned += 1
                print(f"🗑️  已清理旧日志: {log_file.name}")
        except Exception as e:
            print(f"⚠️  清理失败 {log_file}: {e}")
    
    # 如果归档文件过多，只保留最新的
    archived_logs = sorted(
        ARCHIVE_DIR.glob("memory-suite-*.log.gz"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if len(archived_logs) > MAX_ARCHIVED_LOGS:
        for old_log in archived_logs[MAX_ARCHIVED_LOGS:]:
            try:
                old_log.unlink()
                cleaned += 1
                print(f"🗑️  已清理多余日志: {old_log.name}")
            except Exception as e:
                print(f"⚠️  清理失败 {old_log}: {e}")
    
    if cleaned == 0:
        print("✅ 无需清理旧日志")
    else:
        print(f"✅ 共清理 {cleaned} 个旧日志文件")
        
    return cleaned


def compress_old_logs():
    """压缩未压缩的旧日志文件"""
    ensure_archive_dir()
    
    compressed = 0
    cutoff_date = datetime.now() - timedelta(days=COMPRESS_THRESHOLD_DAYS)
    
    for log_file in ARCHIVE_DIR.glob("memory-suite-*.log"):
        # 跳过已压缩的
        if log_file.suffix == '.gz':
            continue
            
        try:
            # 检查文件修改时间
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if mtime < cutoff_date:
                # 压缩文件
                with open(log_file, 'rb') as f_in:
                    with gzip.open(f"{log_file}.gz", 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                        
                log_file.unlink()
                compressed += 1
                print(f"🗜️  已压缩日志: {log_file.name}")
        except Exception as e:
            print(f"⚠️  压缩失败 {log_file}: {e}")
    
    if compressed > 0:
        print(f"✅ 共压缩 {compressed} 个日志文件")
        
    return compressed


def get_log_stats():
    """获取日志统计信息"""
    stats = {
        "current_log": None,
        "archived_logs": 0,
        "total_archive_size_mb": 0
    }
    
    # 当前日志
    if LOG_FILE.exists():
        stats["current_log"] = {
            "path": str(LOG_FILE),
            "size_mb": round(LOG_FILE.stat().st_size / (1024 * 1024), 2),
            "modified": datetime.fromtimestamp(LOG_FILE.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        }
    
    # 归档日志
    if ARCHIVE_DIR.exists():
        archived = list(ARCHIVE_DIR.glob("memory-suite-*.log*"))
        stats["archived_logs"] = len(archived)
        
        total_size = sum(f.stat().st_size for f in archived)
        stats["total_archive_size_mb"] = round(total_size / (1024 * 1024), 2)
    
    return stats


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Suite v4.0 日志轮转')
    parser.add_argument('--rotate', '-r', action='store_true', help='执行日志轮转')
    parser.add_argument('--clean', '-c', action='store_true', help='清理旧日志')
    parser.add_argument('--compress', '-z', action='store_true', help='压缩旧日志')
    parser.add_argument('--all', '-a', action='store_true', help='执行全部操作')
    parser.add_argument('--stats', '-s', action='store_true', help='显示统计信息')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Memory Suite v4.0 - 统一日志轮转")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"日志文件: {LOG_FILE}")
    print(f"归档目录: {ARCHIVE_DIR}")
    print()
    
    # 如果没有参数，默认执行全部
    if not any([args.rotate, args.clean, args.compress, args.stats]):
        args.all = True
    
    if args.all or args.rotate:
        print("📦 执行日志轮转...")
        rotate_log()
        print()
    
    if args.all or args.compress:
        print("🗜️  压缩旧日志...")
        compress_old_logs()
        print()
    
    if args.all or args.clean:
        print("🧹 清理旧日志...")
        clean_old_logs()
        print()
    
    if args.all or args.stats:
        print("📊 日志统计:")
        stats = get_log_stats()
        
        if stats["current_log"]:
            print(f"  当前日志: {stats['current_log']['path']}")
            print(f"  当前大小: {stats['current_log']['size_mb']} MB")
            print(f"  最后修改: {stats['current_log']['modified']}")
        else:
            print("  当前日志: 不存在")
            
        print(f"  归档数量: {stats['archived_logs']} 个")
        print(f"  归档总大小: {stats['total_archive_size_mb']} MB")
        print()
    
    print("=" * 60)
    print("日志轮转完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
