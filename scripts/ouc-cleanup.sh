#!/bin/bash
#===============================================================================
# OUC 文件夹自动清理脚本
# 执行周期：每周日 03:00（通过 crontab 调度）
# 日志：~/.openclaw/ops/logs/tasks/ouc_cleanup.log（由 crontab 重定向）
#===============================================================================

DATE=$(date "+%Y-%m-%d %H:%M:%S")
echo "[$DATE] ========== OUC 清理开始 =========="

# ==================== 清理规则 ====================

# 1. 技能包备份 - 保留最近30天，删除旧备份
echo "[$DATE] 1. 清理技能包备份（保留30天）..."
find /Volumes/cu/ocu/skills-backup -name "skills-backup-*.tar.gz" -type f -mtime +30 -exec rm -f {} \; -print

# 2. archived/ 归档文件 - 保留最近90天
echo "[$DATE] 2. 清理归档文件（保留90天）..."
find /Volumes/cu/ocu/archived -type f -mtime +90 -exec rm -f {} \; -print

# 3. downloads/ 下载文件 - 保留最近30天
echo "[$DATE] 3. 清理下载文件（保留30天）..."
find /Volumes/cu/ocu/downloads -type f -mtime +30 -exec rm -f {} \; -print

# 4. extracted/ 解压文件 - 保留最近7天（临时文件）
echo "[$DATE] 4. 清理解压临时文件（保留7天）..."
find /Volumes/cu/ocu/extracted -type f -mtime +7 -exec rm -f {} \; -print
find /Volumes/cu/ocu/extracted -type d -empty -delete 2>/dev/null

# 5. memory/ 旧记忆文件 - 保留最近365天
echo "[$DATE] 5. 清理旧记忆文件（保留365天）..."
find /Volumes/cu/ocu/memory -name "*.md" -type f -mtime +365 -exec rm -f {} \; -print

# 6. backups/ 旧备份 - 保留最近60天
echo "[$DATE] 6. 清理旧备份（保留60天）..."
find /Volumes/cu/ocu/backups -type f -mtime +60 -exec rm -f {} \; -print

# 7. 清理 .DS_Store 文件
echo "[$DATE] 7. 清理 .DS_Store 缓存文件..."
find /Volumes/cu/ocu -name ".DS_Store" -type f -delete 2>/dev/null

# 8. 清理空目录
echo "[$DATE] 8. 清理空目录..."
find /Volumes/cu/ocu -type d -empty -delete 2>/dev/null

# ==================== 统计信息 ====================

echo "[$DATE] 清理完成！"
echo "[$DATE] 当前磁盘使用情况："
df -h /Volumes/cu/ocu

echo "[$DATE] 各目录大小："
du -sh /Volumes/cu/ocu/*/ 2>/dev/null | sort -h

echo "[$DATE] ========== OUC 清理结束 =========="
