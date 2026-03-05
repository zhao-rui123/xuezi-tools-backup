---
name: model-switching
description: Model switching guide and best practices. Use when switching between different AI models (kimi-for-coding, kimi-k2.5, qwen3.5-plus, MiniMax). Ensures smooth transitions and consistent behavior across models.
---

# 模型切换技能

## 可用模型速查

| 模型 | Provider | 特点 | 适用场景 |
|------|----------|------|---------|
| **kimi-for-coding** | kimi-coding | 代码优化，262k上下文 | 日常开发（默认） |
| **kimi-k2.5** | bailian | 支持识图，256k上下文 | 需要图像识别 |
| **qwen3.5-plus** | bailian | 备用，262k上下文 | 主模型故障时 |
| **MiniMax-M2.5** | minimax-cn | 推理强，200k上下文 | 复杂推理任务 |

## 切换命令

```bash
# 切换到指定模型
openclaw config set agents.defaults.model.primary "provider/model-id"
openclaw gateway restart

# 示例
openclaw config set agents.defaults.model.primary "kimi-coding/kimi-for-coding"
openclaw gateway restart
```

## 模型切换检查清单

### 切换前
- [ ] 保存当前工作进度
- [ ] 提交 Git 变更
- [ ] 记录当前模型（方便回退）

### 切换后
- [ ] 验证 Gateway 重启成功
- [ ] 测试基本功能（发送消息）
- [ ] 检查技能包加载正常

## 模型特性差异

### 图像识别
| 模型 | 支持 |
|------|------|
| kimi-for-coding | ❌ |
| kimi-k2.5 | ✅ |
| qwen3.5-plus | ✅ |
| MiniMax-M2.5 | ❌ |

### 推理能力
| 模型 | 特点 |
|------|------|
| kimi-for-coding | 代码优化 |
| kimi-k2.5 | 通用对话 |
| qwen3.5-plus | 长文本 |
| MiniMax-M2.5 | 深度推理 |

### 成本
| 模型 | 费用 |
|------|------|
| kimi-for-coding | 免费 |
| kimi-k2.5 | 免费 |
| qwen3.5-plus | 免费 |
| MiniMax-M2.5 | $0.3/M tokens |

## 常见问题

### 切换后模型不响应
```bash
# 检查 Gateway 状态
openclaw gateway status

# 重启 Gateway
openclaw gateway restart

# 检查配置
openclaw config get agents.defaults.model.primary
```

### 模型不允许错误
```bash
# 检查 models.json 是否包含该模型
cat ~/.openclaw/agents/main/agent/models.json | grep "model-id"

# 检查 openclaw.json 配置
cat ~/.openclaw/openclaw.json | grep -A5 "model-id"
```

### API Key 失效
- kimi-coding: 使用 `KIMI_API_KEY` 环境变量
- bailian: 使用 Coding Plan Key (`sk-sp-...`)
- minimax-cn: 使用标准 API Key

## 最佳实践

1. **默认模型**: 保持 `kimi-for-coding` 作为默认
2. **识图需求**: 临时切换到 `kimi-k2.5`
3. **故障切换**: 使用 `qwen3.5-plus` 作为备用
4. **深度推理**: 复杂任务使用 `MiniMax-M2.5`

## 快速切换别名

```bash
# 添加到 ~/.zshrc
alias model-kimi='openclaw config set agents.defaults.model.primary "kimi-coding/kimi-for-coding" && openclaw gateway restart'
alias model-vision='openclaw config set agents.defaults.model.primary "bailian/kimi-k2.5" && openclaw gateway restart'
alias model-backup='openclaw config set agents.defaults.model.primary "bailian/qwen3.5-plus" && openclaw gateway restart'
```

---
*创建于: 2026-03-04*
