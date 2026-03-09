---
name: system-maintenance
description: |
  全面系统维护技能包 - 整合 OpenClaw 维护、每日健康检查、服务器监控。
  v2.0 整合: daily-health-check + server-monitor
---

# 系统维护技能包 v2.0

全面系统维护解决方案，整合 OpenClaw 环境维护、每日健康检查、云服务器监控。

## 功能特性

### 1. OpenClaw 环境维护
- 日志轮转和清理
- 孤儿会话文件清理
- 磁盘空间检查
- Gateway 状态监控

### 2. 每日健康检查 ⭐NEW v2.0
- OpenClaw 状态检查
- 云服务器健康检查
- 备份状态验证
- 今日工作统计

### 3. 服务器监控 ⭐NEW v2.0
- 腾讯云服务器 (106.54.25.161) 监控
- 磁盘/内存/服务状态
- 网站可访问性检查
- 大文件管理

## 维护脚本

### 主维护脚本
```bash
# 完整系统维护（每周执行）
bash ~/.openclaw/workspace/skills/system-maintenance/system-maintenance.sh
```

### 每日健康检查
```bash
# 每日健康检查（每日执行）
bash ~/.openclaw/workspace/skills/system-maintenance/daily-health-check.sh
```

### 快速服务器检查
```bash
# 服务器快速检查
bash ~/.openclaw/workspace/skills/system-maintenance/server-check.sh
```

## 定时任务配置

### 推荐配置
```bash
# 每日早上9点 - 健康检查
0 9 * * * /Users/zhaoruicn/.openclaw/workspace/skills/system-maintenance/daily-health-check.sh >> /tmp/daily-health.log 2>&1

# 每周日凌晨2点 - 系统维护
0 2 * * 0 /Users/zhaoruicn/.openclaw/workspace/skills/system-maintenance/system-maintenance.sh >> /tmp/system-maintenance.log 2>&1

# 每小时 - 服务器检查
0 * * * * /Users/zhaoruicn/.openclaw/workspace/skills/system-maintenance/server-check.sh >> /tmp/server-check.log 2>&1
```

## 服务器信息

| 项目 | 详情 |
|------|------|
| **IP** | 106.54.25.161 |
| **用户名** | root |
| **网站目录** | /usr/share/nginx/html/ |
| **网站地址** | http://106.54.25.161/ |

## 快速操作

### SSH连接服务器
```bash
sshpass -p 'Zr123456' ssh root@106.54.25.161
```

### 检查服务器状态
```bash
sshpass -p 'Zr123456' ssh root@106.54.25.161 "df -h && free -h && systemctl status nginx --no-pager"
```

### 上传文件到服务器
```bash
sshpass -p 'Zr123456' scp localfile.txt root@106.54.25.161:/usr/share/nginx/html/
```

### 重启 Nginx
```bash
sshpass -p 'Zr123456' ssh root@106.54.25.161 "nginx -s reload"
```

## 告警阈值

| 指标 | 正常 | 警告 | 危险 |
|------|------|------|------|
| 磁盘空间 | < 70% | 70-85% | > 85% |
| 内存使用 | < 70% | 70-85% | > 85% |
| 备份延迟 | < 1天 | 1-2天 | > 2天 |

## 故障处理

### Gateway 未启动
```bash
openclaw gateway restart
```

### 磁盘空间不足
```bash
# 清理日志
rm ~/.openclaw/logs/gateway.log.*.bak

# 清理旧备份
find /Volumes/cu/ocu -name "*.bak" -mtime +30 -delete

# 服务器磁盘清理
sshpass -p 'Zr123456' ssh root@106.54.25.161 "find /var/log -name '*.log' -mtime +30 -delete"
```

### 网站无法访问
1. 检查 Nginx: `systemctl status nginx`
2. 检查端口: `netstat -tlnp | grep 80`
3. 检查防火墙: `firewall-cmd --list-all`

## 文件说明

| 文件 | 功能 |
|------|------|
| system-maintenance.sh | 主维护脚本（日志轮转、会话清理） |
| daily-health-check.sh | 每日健康检查脚本 ⭐NEW |
| server-check.sh | 服务器快速检查 ⭐NEW |
| SKILL.md | 本文档 |

## 更新日志

### v2.0 (2026-03-09)
- ✅ 整合 daily-health-check 每日健康检查
- ✅ 整合 server-monitor 服务器监控
- ✅ 创建全面的系统维护技能包
- ✅ 统一定时任务配置

### v1.0
- 初始版本，基础 OpenClaw 维护功能

---
*创建于: 2026-03-04*  
*整合时间: 2026-03-09*
