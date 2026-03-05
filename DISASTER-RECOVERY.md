# 灾难恢复手册

> 系统完全崩溃或迁移新机器时的恢复指南

## 快速检查清单

- [ ] Mac 可以正常开机
- [ ] 网络连接正常
- [ ] 备份磁盘 `/Volumes/cu/ocu/` 可访问
- [ ] GitHub 账号可用

---

## 场景1：OpenClaw 配置丢失

### 症状
- Gateway 无法启动
- 配置文件损坏
- 模型无法连接

### 恢复步骤

```bash
# 1. 从 GitHub 拉取最新配置
cd ~/.openclaw/workspace
git pull origin main

# 2. 恢复 OpenClaw 主配置
cp .openclaw/openclaw.json ~/.openclaw/

# 3. 重启 Gateway
openclaw gateway restart

# 4. 验证状态
openclaw status
```

---

## 场景2：工作区完全丢失

### 症状
- `~/.openclaw/workspace/` 被删除
- 所有技能包、记忆文件丢失

### 恢复步骤

```bash
# 1. 克隆仓库
git clone https://github.com/zhao-rui123/xuezi-tools-backup.git ~/.openclaw/workspace

# 2. 进入目录
cd ~/.openclaw/workspace

# 3. 恢复本地备份（如果有）
rsync -av /Volumes/cu/ocu/memory/ memory/

# 4. 验证文件完整性
ls -la skills/ | wc -l  # 应该显示技能包数量
ls memory/ | wc -l      # 应该显示记忆文件数量
```

---

## 场景3：Mac 完全重装

### 前置条件
- 新 Mac 已安装 Homebrew
- 有管理员权限

### 恢复步骤

#### Step 1: 安装基础依赖
```bash
# 安装 Node.js
brew install node

# 安装 OpenClaw
npm install -g openclaw

# 安装其他工具
brew install git rsync sshpass
```

#### Step 2: 恢复工作区
```bash
# 创建目录
mkdir -p ~/.openclaw/workspace

# 克隆仓库
git clone https://github.com/zhao-rui123/xuezi-tools-backup.git ~/.openclaw/workspace

# 恢复备份
rsync -av /Volumes/cu/ocu/memory/ ~/.openclaw/workspace/memory/
```

#### Step 3: 配置 OpenClaw
```bash
# 复制配置文件
cp ~/.openclaw/workspace/.openclaw/openclaw.json ~/.openclaw/

# 启动 Gateway
openclaw gateway start

# 验证
openclaw status
```

#### Step 4: 恢复定时任务
```bash
# 添加 cron 任务
crontab -e

# 粘贴以下内容：
0 22 * * * /Users/$USER/.openclaw/workspace/backup_memory.sh >> /tmp/backup_cron.log 2>&1
0 2 * * 0 /Users/$USER/.openclaw/workspace/scripts/system-maintenance.sh >> /tmp/system-maintenance.log 2>&1
0 9 * * * /Users/$USER/.openclaw/workspace/scripts/daily-health-check.sh >> /tmp/daily-health.log 2>&1
0 3 * * 1 /Users/$USER/.openclaw/workspace/scripts/file-cleanup.sh
```

---

## 场景4：云服务器故障

### 症状
- http://106.54.25.161/ 无法访问
- Nginx 服务停止

### 恢复步骤

```bash
# 1. SSH 登录服务器
sshpass -p 'Zr123456' ssh root@106.54.25.161

# 2. 检查 Nginx 状态
systemctl status nginx

# 3. 如果停止，启动它
systemctl start nginx
systemctl enable nginx

# 4. 如果文件丢失，从 GitHub 恢复
cd /usr/share/nginx/html
git pull origin main

# 5. 重启 Nginx
nginx -s reload
```

---

## 关键备份位置

| 数据 | 备份位置 | 恢复命令 |
|------|---------|---------|
| 工作区代码 | GitHub | `git clone` |
| 记忆文件 | `/Volumes/cu/ocu/memory/` | `rsync -av` |
| 技能包 | GitHub + 本地 | `git clone` |
| OpenClaw配置 | `.openclaw/openclaw.json` | `cp` |
| 云服务器网站 | GitHub + 腾讯云 | `git pull` |

---

## 预防措施

1. **定期提交 Git**: 每天结束时提交变更
2. **保持备份磁盘挂载**: 确保 `/Volumes/cu/ocu/` 可用
3. **测试恢复流程**: 每季度模拟一次恢复
4. **记录变更**: 重要修改记录在 MEMORY.md

---

## 紧急联系

- **GitHub**: https://github.com/zhao-rui123/xuezi-tools-backup
- **备用站点**: https://zhao-rui123.github.io/xuezi-tools-backup/
- **云服务器**: 106.54.25.161 (root/Zr123456)

---
*创建于: 2026-03-04*  
*最后更新: 2026-03-04*
