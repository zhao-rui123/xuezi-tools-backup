# DeepSeek 当前工作配置 (2026-04-25)

## openclaw.json 中的 deepseek provider

```json
{
  "baseUrl": "https://api.deepseek.com/v1",
  "apiKey": "sk-829a69f62a054d0f9a9ff3d79d7909b0",
  "api": "openai-completions",
  "models": [
    {
      "id": "deepseek-chat",
      "name": "DeepSeek-Chat (兼容模式)",
      "reasoning": false,
      "input": ["text", "image"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 640000,
      "maxTokens": 8192
    }
  ]
}
```

## defaults.models 别名

```json
{
  "deepseek/deepseek-chat": { "alias": "deepseek" }
}
```

## 关键修复记录

- **2026-04-25**: 删除了 `deepseek-v4-flash`，只保留 `deepseek-chat`
- **问题**: reasoning_content 导致流式输出出错
- **根因**: 上下文累积导致 DeepSeek 触发思考模式，新会话无此问题
- **结论**: `/new` 开新会话即可解决，配置本身无需特殊处理

## 验证状态
- ✅ 新会话无思考块返回
- ✅ `reasoning: false` 已设置（但实际不起作用，真正原因是新会话干净）
- ✅ deepseek-chat 模型正常工作
