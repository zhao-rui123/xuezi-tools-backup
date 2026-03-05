# 网站恢复技能

## 用途
从坚果云备份恢复雪子的智能工具包到腾讯云服务器

## 坚果云备份信息
- **WebDAV地址**: https://dav.jianguoyun.com/dav/OpenClaw/website-backup/
- **账号**: 1034440765@qq.com
- **应用密码**: azevrhj4j6igpt9q
- **备份文件格式**: `xuezi-tools-full-backup-YYYYMMDD_HHMMSS.tar.gz`

## 恢复步骤

### 1. 下载最新备份
```bash
# 列出备份文件
curl -u "1034440765@qq.com:azevrhj4j6igpt9q" \
  "https://dav.jianguoyun.com/dav/OpenClaw/website-backup/" | grep xuezi-tools-full-backup

# 下载最新备份（替换为最新的文件名）
curl -u "1034440765@qq.com:azevrhj4j6igpt9q" \
  -o /tmp/xuezi-tools-restore.tar.gz \
  "https://dav.jianguoyun.com/dav/OpenClaw/website-backup/xuezi-tools-full-backup-20260224_134314.tar.gz"
```

### 2. 备份当前网站（可选）
```bash
cd /usr/share/nginx/html
tar -czvf /tmp/xuezi-tools-backup-before-restore-$(date +%Y%m%d).tar.gz --exclude='*.tar.gz' .
```

### 3. 恢复网站
```bash
# 清空当前网站目录（保留备份文件）
cd /usr/share/nginx/html
find . -not -name '*.tar.gz' -not -name '.' -not -name '..' -delete

# 解压备份
tar -xzvf /tmp/xuezi-tools-restore.tar.gz -C /usr/share/nginx/html/

# 设置权限
chmod -R 755 /usr/share/nginx/html/*
chmod 644 /usr/share/nginx/html/*/index.html
```

### 4. 重启Nginx
```bash
nginx -t && nginx -s reload
```

## 一键恢复脚本
```bash
#!/bin/bash
# 从坚果云恢复网站

WEBDAV_URL="https://dav.jianguoyun.com/dav/OpenClaw/website-backup/"
USERNAME="1034440765@qq.com"
PASSWORD="azevrhj4j6igpt9q"
BACKUP_FILE="xuezi-tools-full-backup-20260224_134314.tar.gz"

echo "正在下载备份..."
curl -u "${USERNAME}:${PASSWORD}" \
  -o /tmp/${BACKUP_FILE} \
  "${WEBDAV_URL}${BACKUP_FILE}"

echo "正在备份当前网站..."
cd /usr/share/nginx/html
tar -czvf /tmp/xuezi-tools-backup-before-restore-$(date +%Y%m%d).tar.gz --exclude='*.tar.gz' .

echo "正在恢复网站..."
find . -not -name '*.tar.gz' -not -name '.' -not -name '..' -delete
tar -xzvf /tmp/${BACKUP_FILE} -C /usr/share/nginx/html/
chmod -R 755 /usr/share/nginx/html/*
chmod 644 /usr/share/nginx/html/*/index.html

echo "重启Nginx..."
nginx -t && nginx -s reload

echo "恢复完成！"
```

## 验证恢复
- 主站: http://106.54.25.161/
- 电价查询: http://106.54.25.161/electricity/
- 电气接线图: http://106.54.25.161/electrical/
- 股票筛选: http://106.54.25.161/stock8090/

## 注意事项
1. 恢复前建议备份当前网站
2. 确保Nginx配置正确
3. 恢复后检查各功能是否正常
4. 如果恢复失败，可以用备份文件回滚

## 相关文件
- 备份脚本: `/root/.openclaw/workspace/backup-website-to-jianguoyun.sh`
- 服务器信息: `/root/.openclaw/workspace/TOOLS.md`
