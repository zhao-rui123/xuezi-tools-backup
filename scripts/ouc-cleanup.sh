#!/bin/bash
# OUC 文件夹自动清理脚本
# 执行周期：建议每周运行一次（可通过cron设置）

LOG_FILE="/tmp/ouc-cleanup.log"
DATE=$(date "+%Y-%m-%d %H:%M:%S")

echo "[$DATE] 开始执行 OUC 文件夹清理..." | tee -a $LOG_FILE

# ==================== 清理规则 ====================

# 1. 技能包备份 - 保留最近30天，删除旧备份
echo "[$DATE] 1. 清理技能包备份（保留30天）..." | tee -a $LOG_FILE
find /Volumes/cu/ocu/skills-backup -name "skills-backup-*.tar.gz" -type f -mtime +30 -exec rm -f {} \; -print | tee -a $LOG_FILE

# 2. archived/ 归档文件 - 保留最近90天
echo "[$DATE] 2. 清理归档文件（保留90天）..." | tee -a $LOG_FILE
find /Volumes/cu/ocu/archived -type f -mtime +90 -exec rm -f {} \; -print | tee -a $LOG_FILE

# 3. downloads/ 下载文件 - 保留最近30天
echo "[$DATE] 3. 清理下载文件（保留30天）..." | tee -a $LOG_FILE
find /Volumes/cu/ocu/downloads -type f -mtime +30 -exec rm -f {} \; -print | tee -a $LOG_FILE

# 4. extracted/ 解压文件 - 保留最近7天（临时文件）
echo "[$DATE] 4. 清理解压临时文件（保留7天）..." | tee -a $LOG_FILE
find /Volumes/cu/ocu/extracted -type f -mtime +7 -exec rm -f {} \; -print | tee -a $LOG_FILE
find /Volumes/cu/ocu/extracted -type d -empty -delete 2>/dev/null

# 5. memory/ 旧记忆文件 - 保留最近365天
echo "[$DATE] 5. 清理旧记忆文件（保留365天）..." | tee -a $LOG_FILE
find /Volumes/cu/ocu/memory -name "*.md" -type f -mtime +365 -exec rm -f {} \; -print | tee -a $LOG_FILE

# 6. backups/ 旧备份 - 保留最近60天
echo "[$DATE] 6. 清理旧备份（保留60天）..." | tee -a $LOG_FILE
find /Volumes/cu/ocu/backups -type f -mtime +60 -exec rm -f {} \; -print | tee -a $LOG_FILE

# 7. 清理 .DS_Store 文件
echo "[$DATE] 7. 清理 .DS_Store 缓存文件..." | tee -a $LOG_FILE
find /Volumes/cu/ocu -name ".DS_Store" -type f -delete 2>/dev/null

# 8. 清理空目录
echo "[$DATE] 8. 清理空目录..." | tee -a $LOG_FILE
find /Volumes/cu/ocu -type d -empty -delete 2>/dev/null

# ==================== 统计信息 ====================

echo "[$DATE] 清理完成！" | tee -a $LOG_FILE
echo "[$DATE] 当前磁盘使用情况：" | tee -a $LOG_FILE
df -h /Volumes/cu/ocu | tee -a $LOG_FILE

echo "[$DATE] 各目录大小：" | tee -a $LOG_FILE
du -sh /Volumes/cu/ocu/*/ 2>/dev/null | sort -h | tee -a $LOG_FILE
