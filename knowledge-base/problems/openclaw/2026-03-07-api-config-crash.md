# OpenClaw API 配置问题

## 问题描述

添加 Kimi Coding API 配置时，AI 助手卡死无响应。

## 发生时间

2026-03-07

## 问题表现

- 用户要求新增 API 配置
- AI 助手尝试主动搜索/查找信息
- 导致系统卡死，需要 `/new` 重启

## 根本原因

AI 助手主动搜索外部信息导致超时/卡死。

## 解决方案

### 用户端修复

手动编辑配置文件，添加 Kimi Coding provider：

**~/.openclaw/openclaw.json:**
```json
{
  "providers": {
    "kimi-coding": {
      "baseUrl": "https://api.kimi.com/coding",
      "api": "anthropic-messages",
      "apiKey": "YOUR_API_KEY",
      "authHeader": true,
      "models": [...]
    }
  }
}
```

**~/.openclaw/agents/main/agent/models.json:**
添加相同的 provider 配置

重启 Gateway：
```bash
openclaw gateway restart
```

### 预防机制

已记录学习项：`error-001` 主动行为边界

**准则：**
- 不主动搜索/查找外部信息
- 只处理用户明确提供的内容
- 需要信息时，让用户提供截图或文本

## 相关学习

- [自我改进学习库](../../MEMORY.md#自我改进学习库)
- `memory/self-improvement.json`

## 状态

✅ 已解决
