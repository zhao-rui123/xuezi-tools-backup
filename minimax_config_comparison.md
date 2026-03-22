# MiniMax 配置对比报告

## 当前配置（后台实际配置）

```json
"minimax-cn": {
  "baseUrl": "https://api.minimaxi.com/anthropic",
  "apiKey": "sk-cp-TaEn7XZHReif66-VaxR-UZJuHCoYYYqho4xu6pV22L3MtAL9oImB0iubia4dRjZDN-0avV5_rSS2ggBC6w2gHYz1tYN0semS3mps1PrA9lS-16qJhoh8l3Q",
  "api": "anthropic-messages",
  "authHeader": true,
  "models": [
    {
      "id": "MiniMax-M2.7",
      "name": "MiniMax M2.7",
      "api": "anthropic-messages",
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
}
```

## 官方文档推荐配置

根据你发的文档，官方配置应该是：

### Provider 名称
- 文档使用: `minimax-portal` (OAuth登录方式)
- 当前配置: `minimax-cn`

### API 端点
- 文档未明确写出，但 OAuth 方式应该是 `https://api.minimaxi.com/anthropic`
- 当前配置: `https://api.minimaxi.com/anthropic` ✅ 一致

### API Key 格式
- 文档 OAuth 方式：自动获取 token
- 当前配置: 手动填写的 API Key (`sk-cp-...`)

### 模型列表
- 文档默认: `minimax-portal/MiniMax-M2.5` + `minimax-portal/MiniMax-M2.7`
- 当前配置: 只有 `MiniMax-M2.7` (缺少 M2.5)

### 模型 ID 格式
- 文档格式: `MiniMax-M2.7` (不带 minimax-portal/ 前缀，因为 provider 已经指定)
- 当前配置: `MiniMax-M2.7` ✅ 一致

## 差异总结

| 项目 | 当前配置 | 官方推荐 | 差异 |
|------|---------|---------|------|
| Provider 名 | `minimax-cn` | `minimax-portal` | ⚠️ 不同 |
| 认证方式 | API Key 手动填写 | OAuth 自动获取 | ⚠️ 不同 |
| 模型数量 | 1个 (M2.7) | 2个 (M2.5 + M2.7) | ⚠️ 缺少 M2.5 |
| API 端点 | `api.minimaxi.com/anthropic` | 相同 | ✅ 一致 |
| 模型 ID | `MiniMax-M2.7` | `MiniMax-M2.7` | ✅ 一致 |

## 关键发现

1. **Provider 名称不同**: 你用的是 `minimax-cn`，官方 OAuth 方式是 `minimax-portal`
2. **缺少 M2.5 模型**: 当前只有 M2.7，官方默认有 M2.5 和 M2.7 两个
3. **认证方式不同**: 当前是手动 API Key，官方推荐 OAuth 自动获取

## 说明

文档里提到 OAuth 登录后会默认勾选两个模型：
- `minimax-portal/MiniMax-M2.5`
- `minimax-portal/MiniMax-M2.7`

你的配置可能是之前手动配置的，或者是旧版本 OpenClaw 的配置。
