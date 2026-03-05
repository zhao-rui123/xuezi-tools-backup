# 问题与解决方案 - OpenClaw

## 模型配置问题

### 问题：模型不允许错误
**现象**: 切换模型时提示 "model not allowed"

**原因**: 
- `openclaw.json` 和 `models.json` 配置不一致
- 或模型不在允许列表中

**解决方案**:
1. 检查 `~/.openclaw/openclaw.json` 的 `models.providers` 部分
2. 检查 `~/.openclaw/agents/main/agent/models.json` 的 `providers` 部分
3. 确保两个文件都包含目标模型

**预防措施**:
- 修改配置后运行 `openclaw gateway restart`

---

### 问题：API Key 认证失败
**现象**: 模型返回认证错误或无法连接

**原因**:
- API Key 格式不匹配（Coding Plan vs 标准接口）
- Key 已过期或被删除

**解决方案**:
| 模型 | Key 格式 | 获取方式 |
|------|---------|---------|
| MiniMax | `sk-cp-...` | MiniMax 官网 |
| 百炼 Coding | `sk-sp-...` | 阿里云百炼控制台 |
| Kimi API | `sk-kimi-...` | Moonshot 官网 |

**预防措施**:
- 定期检查 Key 有效性
- 在 MEMORY.md 记录当前使用的 Key 前缀

---

## 飞书集成问题

### 问题：图片/文件发送失败
**现象**: message 工具返回成功，但实际未发送

**原因**: 使用了 `/tmp/` 目录，飞书接收有 bug

**解决方案**:
```javascript
// ✅ 正确：使用 workspace 目录
{ "media": "/Users/zhaoruicn/.openclaw/workspace/image.png" }

// ✅ 正确：转发用户图片
{ "media": "/Users/zhaoruicn/.openclaw/media/inbound/xxx.png" }

// ❌ 错误：/tmp 目录会失败
{ "media": "/tmp/image.png" }
```

**预防措施**:
- 所有生成文件保存到 `~/.openclaw/workspace/`
- 参考技能包: `feishu-image-send`

---

### 问题：Gateway 连接失败
**现象**: 无法连接到 OpenClaw Gateway

**原因**:
- Gateway 未启动
- 端口被占用
- 配置错误

**解决方案**:
```bash
# 检查状态
openclaw gateway status

# 检查端口占用
lsof -i :18789

# 重启 Gateway
openclaw gateway restart

# 自动修复
openclaw doctor --fix
```

---

## 定时任务问题

### 问题：备份脚本不执行
**现象**: cron 任务未按预期运行

**原因**:
- 磁盘未挂载
- 脚本权限问题
- 路径解析错误

**解决方案**:
1. 检查磁盘挂载: `ls /Volumes/cu/ocu/`
2. 检查脚本权限: `chmod +x backup_memory.sh`
3. 使用绝对路径，避免 `$HOME`

**修复后的备份脚本要点**:
- 使用 `/Users/zhaoruicn/` 而非 `$HOME`
- 日志保存到 `/tmp/` 而非备份目录
- 删除 `--delete` 参数防止误删

---

## 关键配置文件路径

| 文件 | 路径 | 用途 |
|------|------|------|
| 主配置 | `~/.openclaw/openclaw.json` | 全局设置 |
| 模型配置 | `~/.openclaw/agents/main/agent/models.json` | 模型定义 |
| 认证配置 | `~/.openclaw/agents/main/agent/auth-profiles.json` | API Key |
| 飞书配置 | `openclaw.json` 的 `channels.feishu` | 飞书集成 |

---
*最后更新: 2026-03-04*
