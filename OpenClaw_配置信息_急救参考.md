# OpenClaw 配置信息 - 急救医生参考

## 当前主配置文件 ~/.openclaw/openclaw.json

```json
{
  "meta": {
    "lastTouchedVersion": "2026.2.26",
    "lastTouchedAt": "2026-03-08T02:40:25.024Z"
  },
  "env": {
    "KIMI_API_KEY": "[你的Kimi API Key]",
    "TAVILY_API_KEY": "[你的Tavily API Key]"
  },
  "models": {
    "mode": "merge",
    "providers": {
      "minimax-cn": {
        "baseUrl": "https://api.minimaxi.com/anthropic",
        "api": "anthropic-messages",
        "authHeader": true,
        "models": [
          {
            "id": "MiniMax-M2.5",
            "name": "MiniMax M2.5",
            "reasoning": true,
            "input": ["text"],
            "cost": {
              "input": 0.3,
              "output": 1.2,
              "cacheRead": 0.03,
              "cacheWrite": 0.12
            },
            "contextWindow": 200000,
            "maxTokens": 8192
          }
        ]
      },
      "bailian": {
        "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",
        "apiKey": "[你的百炼API Key]",
        "api": "openai-completions",
        "models": [
          {
            "id": "kimi-k2.5",
            "name": "Kimi K2.5",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
            "contextWindow": 256000,
            "maxTokens": 8192
          },
          {
            "id": "qwen3.5-plus",
            "name": "通义千问3.5 Plus",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
            "contextWindow": 262144,
            "maxTokens": 65536
          }
        ]
      },
      "kimi-coding": {
        "baseUrl": "https://api.kimi.com/coding",
        "apiKey": "[你的Kimi Coding API Key]",
        "api": "anthropic-messages",
        "authHeader": true,
        "models": [
          {
            "id": "kimi-for-coding",
            "name": "Kimi Code",
            "reasoning": false,
            "input": ["text"],
            "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
            "contextWindow": 262144,
            "maxTokens": 32768
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "kimi-coding/k2p5",
        "fallbacks": [
          "bailian/qwen3.5-plus",
          "minimax-cn/MiniMax-M2.5"
        ]
      },
      "models": {
        "minimax-cn/MiniMax-M2.5": {"alias": "Minimax"},
        "bailian/kimi-k2.5": {},
        "kimi-coding/k2p5": {"alias": "KimiCode"},
        "kimi-coding/kimi-for-coding": {"alias": "KimiCode"}
      },
      "compaction": {"mode": "safeguard"},
      "maxConcurrent": 4,
      "subagents": {"maxConcurrent": 8}
    }
  },
  "channels": {
    "feishu": {
      "appId": "[飞书App ID]",
      "appSecret": "[飞书App Secret]",
      "enabled": true
    }
  },
  "gateway": {
    "mode": "local",
    "auth": {
      "mode": "token",
      "token": "[Gateway Token]"
    }
  },
  "plugins": {
    "entries": {
      "feishu": {"enabled": true}
    }
  }
}
```

---

## 关键配置项说明

### 1. 模型配置 (models.providers)
| Provider | 用途 | 必需 |
|----------|------|------|
| `kimi-coding` | 当前主模型 | ✅ 必需 |
| `bailian` | 备用模型 | ✅ 建议 |
| `minimax-cn` | 备用模型 | ⚠️ 可选 |

### 2. API Key 配置
| Key | 位置 | 用途 |
|-----|------|------|
| `KIMI_API_KEY` | `env.KIMI_API_KEY` | Kimi API |
| `bailian.apiKey` | `models.providers.bailian.apiKey` | 百炼 API |
| `kimi-coding.apiKey` | `models.providers.kimi-coding.apiKey` | Kimi Coding API |

### 3. 飞书配置 (channels.feishu)
```json
{
  "appId": "cli_a928644411785bdf",
  "appSecret": "[需要填入]",
  "enabled": true
}
```

### 4. 当前主模型
- **Primary**: `kimi-coding/k2p5`
- **Fallback 1**: `bailian/qwen3.5-plus`
- **Fallback 2**: `minimax-cn/MiniMax-M2.5`

---

## 急救场景快速修复命令

### 场景1：模型不允许错误
```bash
# 检查配置
openclaw config get agents.defaults.model.primary

# 切换到备用模型
openclaw config set agents.defaults.model.primary "bailian/qwen3.5-plus"
openclaw gateway restart
```

### 场景2：API Key 错误
```bash
# 编辑配置文件，检查 apiKey 是否正确
open ~/.openclaw/openclaw.json

# 重启生效
openclaw gateway restart
```

### 场景3：飞书连接失败
```bash
# 检查飞书配置
openclaw config get channels.feishu

# 检查 Gateway 状态
openclaw gateway status

# 重启
openclaw gateway restart
```

### 场景4：完全重置
```bash
# 备份
openclaw doctor --backup

# 自动修复
openclaw doctor --fix

# 重启
openclaw gateway restart
```

---

## 重要文件路径

| 文件 | 路径 | 用途 |
|------|------|------|
| 主配置 | `~/.openclaw/openclaw.json` | 全局设置 |
| 模型配置 | `~/.openclaw/agents/main/agent/models.json` | 模型定义 |
| 认证配置 | `~/.openclaw/agents/main/agent/auth-profiles.json` | API Key |
| 日志 | `~/.openclaw/logs/gateway.err.log` | 错误日志 |
| 技能包 | `~/.openclaw/workspace/skills/` | 自定义技能 |
| 记忆 | `~/.openclaw/workspace/memory/` | 每日记忆 |

---

## 生成时间
2026-03-07 23:03

**注意**：此配置包含敏感信息（API Key、App Secret），请妥善保管！
