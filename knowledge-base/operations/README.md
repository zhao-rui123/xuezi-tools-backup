# 运维知识库

> 系统运维、日常操作、环境配置等非项目类知识

## 目录

### OpenClaw 系统
- [模型切换速查](模型切换.md)
- [Gateway 管理](gateway管理.md)
- [故障排查](故障排查.md)

### 飞书集成
- [文件发送规范](飞书文件发送.md)
- [消息格式](飞书消息格式.md)

### 备份与恢复
- [每日备份流程](每日备份.md)
- [灾难恢复手册](灾难恢复.md)

### 开发环境
- [Mac 常用命令](mac命令.md)
- [SSH 连接配置](ssh配置.md)

## 快速参考

### 常用命令
```bash
# Gateway 管理
openclaw gateway status
openclaw gateway restart

# 模型切换
openclaw config set agents.defaults.model.primary "bailian/kimi-k2.5"

# 备份
bash ~/.openclaw/workspace/backup_memory.sh
```

### 重要路径
| 用途 | 路径 |
|------|------|
| 配置文件 | `~/.openclaw/openclaw.json` |
| 工作区 | `~/.openclaw/workspace/` |
| 媒体文件 | `~/.openclaw/media/inbound/` |
| 日志 | `~/.openclaw/logs/` |
