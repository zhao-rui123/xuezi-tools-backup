---
name: server-monitor
description: Cloud server monitoring and health checks. Use when checking server status, disk usage, service health, or troubleshooting deployment issues. Covers Tencent Cloud server (106.54.25.161) monitoring.
---

# 服务器监控技能

## 服务器信息

| 项目 | 详情 |
|------|------|
| **IP** | 106.54.25.161 |
| **用户名** | root |
| **网站目录** | /usr/share/nginx/html/ |
| **网站地址** | http://106.54.25.161/ |

## 快速连接

```bash
# SSH连接
sshpass -p 'Zr123456' ssh root@106.54.25.161

# 执行远程命令
sshpass -p 'Zr123456' ssh root@106.54.25.161 "命令"
```

## 健康检查清单

### 1. 磁盘空间检查
```bash
sshpass -p 'Zr123456' ssh root@106.54.25.161 "df -h"
```

**正常标准**: 
- 使用率 < 80% ✅
- 使用率 80-90% ⚠️ 需关注
- 使用率 > 90% 🔴 需清理

### 2. 内存检查
```bash
sshpass -p 'Zr123456' ssh root@106.54.25.161 "free -h"
```

**当前配置**: 1.9G 内存 + 8G swap

### 3. Nginx 状态检查
```bash
sshpass -p 'Zr123456' ssh root@106.54.25.161 "systemctl status nginx --no-pager"
```

**重启命令**:
```bash
sshpass -p 'Zr123456' ssh root@106.54.25.161 "nginx -s reload"
```

### 4. 网站文件检查
```bash
# 查看目录结构
sshpass -p 'Zr123456' ssh root@106.54.25.161 "ls -la /usr/share/nginx/html/"

# 查看大文件
sshpass -p 'Zr123456' ssh root@106.54.25.161 "du -sh /usr/share/nginx/html/*/ | sort -hr | head -10"
```

## 大文件管理

### 当前大文件（定期清理候选）
| 文件 | 大小 | 说明 |
|------|------|------|
| website-backup.tar.gz | 170M | 网站完整备份 |
| downloads/xuezi-tools-完整版 | 86M | 工具包完整版 |
| openclaw-workspace-backup.tar.gz | 69M | OpenClaw备份 |

### 清理命令
```bash
# 删除旧备份（谨慎执行）
sshpass -p 'Zr123456' ssh root@106.54.25.161 "rm /usr/share/nginx/html/website-backup.tar.gz"

# 清理日志
sshpass -p 'Zr123456' ssh root@106.54.25.161 "find /var/log -name '*.log' -mtime +30 -delete"
```

## 部署操作

### 上传文件
```bash
# 单个文件
sshpass -p 'Zr123456' scp localfile.txt root@106.54.25.161:/usr/share/nginx/html/

# 整个目录
sshpass -p 'Zr123456' scp -r localdir/ root@106.54.25.161:/usr/share/nginx/html/
```

### 设置权限
```bash
sshpass -p 'Zr123456' ssh root@106.54.25.161 "chmod -R 755 /usr/share/nginx/html/*"
```

## 故障排查

### 网站无法访问
1. 检查 Nginx: `systemctl status nginx`
2. 检查端口: `netstat -tlnp | grep 80`
3. 检查防火墙: `firewall-cmd --list-all`

### 磁盘空间不足
1. 定位大文件: `du -sh /* | sort -hr`
2. 清理日志: 删除 `/var/log` 下旧日志
3. 清理备份: 删除旧版本备份文件

### 内存不足
1. 查看进程: `ps aux --sort=-%mem | head -10`
2. 重启服务: `systemctl restart nginx`
3. 增加 swap（如需要）

## 监控建议

**每日检查**（可自动化）:
- 磁盘使用率
- Nginx 运行状态
- 网站可访问性

**每周检查**:
- 大文件增长情况
- 日志文件大小
- 备份文件完整性

---
*创建于: 2026-03-04*  
*服务器: 腾讯云 106.54.25.161*
