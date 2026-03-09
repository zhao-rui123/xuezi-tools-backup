import re

with open('/Users/zhaoruicn/.openclaw/workspace/skills/system-backup/scripts/daily-backup-v2.sh', 'r') as f:
    content = f.read()

# 删除有问题的部分（从 "使用 Kilo Agent 发送通知" 到多余的行）
old_text = '''    # 使用 Kilo Agent 发送通知
    log "使用 Kilo (通知Agent) 发送消息..."
    python3 ~/.openclaw/workspace/skills/multi-agent-suite/agents/kilo_notification.py \\
        --alert "每日备份完成\\n\\n📊 备份统计:\\n• Memory: $memory_count 个文件\\n• Skills: $skills_count 个文件\\n\\n📄 备份清单: backup-manifest-$DATE.json\\n\\n✅ 全部备份完成！" \\
        --alert-type info \\
        2>/dev/null || log "Kilo 通知发送失败，但备份已完成"
" 2>/dev/null || log "飞书通知发送失败"
}'''

new_text = '''    # 使用 Kilo Agent v2 发送通知到群聊
    log "使用 Kilo (通知Agent) 生成通知..."
    
    # 获取压缩包大小
    local backup_size="未知"
    if [ -f "$BACKUP_DIR/full-backups/latest" ]; then
        backup_size=$(du -h "$BACKUP_DIR/full-backups/latest" 2>/dev/null | cut -f1)
    fi
    
    python3 ~/.openclaw/workspace/skills/multi-agent-suite/agents/kilo_v2.py \\
        --backup success \\
        --backup-details "📊 备份统计:\\n• Memory: $memory_count 个文件\\n• Skills: $skills_count 个文件\\n• 压缩包大小: $backup_size\\n\\n📄 清单: backup-manifest-$DATE.json" \\
        2>/dev/null
    
    log "✅ Kilo 通知已生成"
}'''

if old_text in content:
    content = content.replace(old_text, new_text)
    with open('/Users/zhaoruicn/.openclaw/workspace/skills/system-backup/scripts/daily-backup-v2.sh', 'w') as f:
        f.write(content)
    print("✅ 备份脚本已修复")
else:
    print("⚠️ 未找到匹配文本，可能需要手动检查")
