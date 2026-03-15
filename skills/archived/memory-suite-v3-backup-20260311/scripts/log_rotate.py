#!/usr/bin/env python3
"""
Memory Suite v3.0 - 日志轮转脚本
自动轮转和清理日志文件
"""

import os
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# 配置
LOG_DIR = Path("/tmp")
LOG_FILE = LOG_DIR / "memory-suite.log"
MAX_LOG_SIZE_MB = 10  # 超过10MB轮转
MAX_LOG_DAYS = 30     # 保留30天
MAX_ARCHIVED_LOGS = 10  # 保留10个归档文件

def rotate_log():
    """轮转日志文件"""
    if not LOG_FILE.exists():
        print("日志文件不存在，无需轮转")
        return
    
    # 检查文件大小
    size_mb = LOG_FILE.stat().st_size / (1024 * 1024)
    if size_mb < MAX_LOG_SIZE_MB:
        print(f"日志文件大小 {size_mb:.1f}MB，未超过 {MAX_LOG_SIZE_MB}MB，无需轮转")
        return
    
    # 生成归档文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archived_file = LOG_DIR / f"memory-suite-{timestamp}.log.gz"
    
    # 压缩并归档
    try:
        with open(LOG_FILE, 'rb') as f_in:
            with gzip.open(archived_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # 清空原日志文件
        LOG_FILE.write_text("")
        print(f"✅ 日志已轮转: {archived_file}")
        
    except Exception as e:
        print(f"❌ 轮转失败: {e}")

def clean_old_logs():
    """清理旧日志文件"""
    cutoff_date = datetime.now() - timedelta(days=MAX_LOG_DAYS)
    
    # 清理旧日志文件
    cleaned = 0
    for log_file in LOG_DIR.glob("memory-suite-*.log.gz"):
        try:
            # 从文件名提取日期
            file_date_str = log_file.name.split('-')[2]  # memory-suite-YYYYMMDD_HHMMSS.log.gz
            file_date = datetime.strptime(file_date_str, "%Y%m%d")
            
            if file_date < cutoff_date:
                log_file.unlink()
                cleaned += 1
                print(f"🗑️  已清理旧日志: {log_file.name}")
        except Exception as e:
            print(f"⚠️  清理失败 {log_file}: {e}")
    
    # 如果归档文件过多，只保留最新的
    archived_logs = sorted(LOG_DIR.glob("memory-suite-*.log.gz"), 
                          key=lambda p: p.stat().st_mtime, 
                          reverse=True)
    
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

def main():
    """主函数"""
    print("=" * 60)
    print("Memory Suite v3.0 - 日志轮转")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 执行轮转
    rotate_log()
    print()
    
    # 执行清理
    clean_old_logs()
    print()
    
    print("=" * 60)
    print("日志轮转完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
