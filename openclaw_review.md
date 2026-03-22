# OpenClaw 配置审查报告

**审查时间**: 2026-03-22 16:05 GMT+8  
**审查范围**: 
- Agent配置: `~/.openclaw/agents/main/agent/` 下的所有JSON文件
- 扩展插件: `/opt/homebrew/lib/node_modules/openclaw/extensions/` 下的config/schema文件

---

## 一、发现的问题列表

### 🔴 严重问题

#### 1. 硬编码API密钥泄露（安全风险）

**文件**: `~/.openclaw/openclaw.json`
- **行号**: 第7行
- **问题描述**: `KIMI_API_KEY` 以明文形式存储在配置文件中
- **风险**: 敏感信息泄露，可能被恶意程序读取

**文件**: `~/.openclaw/openclaw.json`
- **行号**: 第8行
- **问题描述**: `TAVILY_API_KEY` 以明文形式存储在配置文件中
- **风险**: 敏感信息泄露

**文件**: `~/.openclaw/openclaw.json`
- **行号**: 第22行
- **问题描述**: `bailian` provider 的 `apiKey` 硬编码为 `sk-sp-26a5e11d3a8d47589a2ce4a4d0e3222b`
- **风险**: API密钥泄露

**文件**: `~/.openclaw/openclaw.json`
- **行号**: 第45行
- **问题描述**: `kimi-coding` provider 的 `apiKey` 硬编码
- **风险**: API密钥泄露

**文件**: `~/.openclaw/openclaw.json`
- **行号**: 第66行
- **问题描述**: `minimax-cn` provider 的 `apiKey` 硬编码为完整密钥
- **风险**: API密钥泄露

**文件**: `~/.openclaw/openclaw.json`
- **行号**: 第96-97行
- **问题描述**: 飞书 `appId` 和 `appSecret` 以明文存储
- **风险**: 应用凭证泄露

**文件**: `~/.openclaw/openclaw.json`
- **行号**: 第103行
- **问题描述**: Gateway auth token 硬编码
- **风险**: 认证令牌泄露，可能导致未授权访问

**文件**: `~/.openclaw/agents/main/agent/models.json`
- **行号**: 第32行
- **问题描述**: `minimax-cn` provider 的 `apiKey` 硬编码
- **风险**: API密钥泄露

**文件**: `~/.openclaw/agents/main/agent/models.json`
- **行号**: 第55行
- **问题描述**: `bailian` provider 的 `apiKey` 硬编码
- **风险**: API密钥泄露

**文件**: `~/.openclaw/agents/main/agent/auth-profiles.json`
- **行号**: 第5行
- **问题描述**: `minimax-cn:default` profile 的 `key` 硬编码
- **风险**: API密钥泄露

---

### 🟡 中等问题

#### 2. 重复配置（配置冗余）

**文件**: `~/.openclaw/openclaw.json` 和 `~/.openclaw/agents/main/agent/models.json`
- **问题描述**: 模型配置在两个文件中重复定义，存在同步风险
- **详情**:
  - `bailian` provider 配置重复
  - `kimi-coding` provider 配置重复
  - `minimax-cn` provider 配置重复
- **风险**: 修改一处可能导致配置不一致

#### 3. 模型ID不一致（功能问题）

**文件**: `~/.openclaw/agents/main/agent/models.json`
- **行号**: 第14行
- **问题描述**: `kimi-coding` provider 中定义了 `k2p5` 模型ID，但主配置使用的是 `kimi-for-coding`
- **风险**: 可能导致模型切换失败或调用错误

#### 4. 备份文件权限问题（安全风险）

**文件**: `~/.openclaw/agents/main/agent/models.json.bak.*`
- **问题描述**: 备份文件权限为 `-rw-r--r--` (644)，其他用户可读
- **风险**: 备份文件包含敏感配置，应限制为仅所有者可读 (600)

---

### 🟢 轻微问题

#### 5. 缺失配置文件

**文件**: `~/.openclaw/agents/main/agent/config.json`
- **问题描述**: 该文件不存在（根据目录列表确认）
- **影响**: 如果OpenClaw期望此文件存在，可能导致功能异常

#### 6. 空配置文件

**文件**: `~/.openclaw/config.yaml.save`
- **问题描述**: 文件内容为空
- **建议**: 如不再需要，建议删除

#### 7. 扩展插件配置简化

**文件**: `/opt/homebrew/lib/node_modules/openclaw/extensions/*/openclaw.plugin.json`
- **问题描述**: 多个插件（feishu、telegram、discord、slack等）的 `configSchema.properties` 为空对象
- **影响**: 这可能导致配置验证过于宽松
- **涉及的插件**:
  - feishu
  - telegram
  - discord
  - slack
  - irc
  - line
  - matrix
  - mattermost
  - signal
  - whatsapp

---

## 二、修复建议

### 立即修复（高优先级）

1. **移除硬编码密钥**
   - 将所有API密钥、Token、密码改为从环境变量读取
   - 示例修改:
     ```json
     // 修改前
     "apiKey": "sk-xxx..."
     
     // 修改后
     "apiKey": "${MINIMAX_API_KEY}"
     ```

2. **设置正确的文件权限**
   ```bash
   chmod 600 ~/.openclaw/openclaw.json
   chmod 600 ~/.openclaw/agents/main/agent/*.json
   chmod 600 ~/.openclaw/credentials/*.json
   ```

3. **清理备份文件权限**
   ```bash
   chmod 600 ~/.openclaw/agents/main/agent/*.bak.*
   ```

### 建议修复（中优先级）

4. **统一模型配置**
   - 确定单一配置源（建议以 `~/.openclaw/openclaw.json` 为主）
   - 删除 `~/.openclaw/agents/main/agent/models.json` 中的重复配置
   - 或确保两处配置完全一致

5. **修复模型ID不一致**
   - 在 `models.json` 中统一使用 `kimi-for-coding` 或 `k2p5`
   - 确保与主配置 `openclaw.json` 保持一致

6. **删除空文件**
   ```bash
   rm ~/.openclaw/config.yaml.save
   ```

### 可选优化（低优先级）

7. **启用配置加密**
   - 考虑使用 OpenClaw 的加密存储功能（如果支持）
   - 或使用系统密钥链存储敏感信息

8. **定期轮换密钥**
   - 建议定期更换 API 密钥
   - 尤其是已暴露在配置文件中的密钥

---

## 三、安全风险评估

| 风险项 | 严重程度 | 状态 |
|--------|----------|------|
| 硬编码API密钥 | 🔴 高 | 需立即修复 |
| 文件权限过宽 | 🟡 中 | 建议修复 |
| 配置重复 | 🟡 中 | 建议修复 |
| 备份文件可读 | 🟡 中 | 建议修复 |
| 空配置文件 | 🟢 低 | 可选修复 |

---

## 四、审查结论

**总体状态**: ⚠️ 存在安全问题需要修复

**主要问题**:
1. 多个API密钥以明文形式硬编码在配置文件中，存在泄露风险
2. 配置文件权限设置不当，可能被其他用户读取
3. 模型配置在多处重复定义，存在同步风险

**建议操作**:
1. 立即将所有敏感信息迁移到环境变量
2. 设置正确的文件权限 (600)
3. 统一模型配置来源
4. 考虑轮换已暴露的API密钥

---

*报告生成时间: 2026-03-22 16:05 GMT+8*
