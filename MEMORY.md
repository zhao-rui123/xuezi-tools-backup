# MEMORY.md - 雪子的智能工具包

## 项目概览
- **项目名称**: 雪子的智能工具包
- **主站地址**: http://106.54.25.161/
- **GitHub备份**: https://github.com/zhao-rui123/xuezi-tools-backup
- **GitHub Pages备用站**: https://zhao-rui123.github.io/xuezi-tools-backup/
- **离线压缩包下载**: http://106.54.25.161/xuezi-tools-backup.tar.gz

## 包含工具
1. **全国电价查询** - 31省份分时电价数据，支持循环次数计算
2. **电气接线图绘制** - 一二次接线图设计工具
3. **储能智能排布** - 储能电站设备布局设计
4. **工程师计算手册** - 电气/暖通/储能/光伏/流体力学计算
5. **项目测算工具包** - 零碳园区/独立储能/光储充/工商业储能测算
6. **国网数据分析** - 用电数据导入分析与储能优化
7. **电费清单处理器** - 自动处理国网电费清单和负荷曲线，计算储能最优容量
8. **小龙虾之家** 🦞 - AI助手工作状态可视化看板

### 当前方案
- **Obsidian** 作为笔记工具（Windows已安装）
- **坚果云** 作为同步服务（WebDAV已配置）
- **我（雪子助手）** 通过WebDAV增强搜索和整理

### 坚果云WebDAV配置（连接Obsidian）
| 项目 | 值 |
|------|------|
| **账号** | 1034440765@qq.com |
| **服务器** | https://dav.jianguoyun.com/dav/ |
| **Vault路径** | /BOSI/zhaorui/ |
| **密码** | ai7eaer5mv2gixex |

### 坚果云命令
```bash
# 列出文件
~/.openclaw/workspace/obsidian-webdav/webdav.sh list

# 读取笔记
~/.openclaw/workspace/obsidian-webdav/webdav.sh read <文件名>

# 搜索
~/.openclaw/workspace/obsidian-webdav/webdav.sh search <关键词>
```

### 备份信息（仅保留参考）
- **备份文件**: `xuezi-tools-backup.tar.gz` (2.0MB)
- **备份位置**: 
  - 腾讯云服务器: `/usr/share/nginx/html/xuezi-tools-backup.tar.gz`
  - GitHub仓库: https://github.com/zhao-rui123/xuezi-tools-backup

### 恢复方法（参考）
```bash
tar -xzvf xuezi-tools-backup.tar.gz -C /usr/share/nginx/html/
chmod -R 755 /usr/share/nginx/html/*
chmod 644 /usr/share/nginx/html/*/index.html
```

## 电价数据更新流程
- **更新频率**: 每月（用户主动通知）
- **更新方式**: 用户告知需要更新的省份 → 我修改数据 → 重新部署 → 更新GitHub备份
- **数据来源**: 各省发改委/电网公司官方文件

# 执行开发 → MiniMax
cp ~/.claude/settings-minimax.json ~/.claude/settings.json

# 架构/审核 → 官方（需手动编辑）
```

### 完整工作流程
1. 📋 向雪子确认需求
2. 官方Sonnet → 架构设计 + Superpowers规划
3. MiniMax Claude Code → sessions_spawn 分模块执行开发
4. 官方Sonnet → 验收审查
5. 我（决策）→ 部署 or 返工
6. OpenClaw子Agent → 部署上线
7. ✅ 向雪子汇报完成

### 汇报节点
- **📋 任务启动**：开始时汇报
- **⚠️ 关键里程碑**：遇到问题/重大进展时汇报
- **✅ 任务完成**：部署成功后汇报

### 适用场景
- 大型Web应用开发
- 多模块系统设计
- 需要架构审查的复杂项目

### 不适用场景
- 简单问答、已有明确步骤的任务、紧急小修小改

## 注意事项
- 电价查询工具在GitHub Pages备用站使用iframe嵌入主站
- 如主站无法访问，备用站的电价查询会显示错误提示，需下载离线包使用
- 其他五个工具在备用站可独立正常使用

**参考技能包**: `skills/feishu-image-send/SKILL.md`（支持图片、文档、文本等）

## 🤖 Claude Code / Codex screen 调用规范（2026-04-24 新增）

**铁律：所有 Claude Code 和 Codex 调用必须用 screen，不允许 sessions_spawn/acpx 直接调**

| 工具 | 命令 |
|------|------|
| **本地 Claude Code** | `screen -dmS claude-task bash -c "claude --print '任务' 2>&1 | tee /tmp/claude-task.log"` |
| **本地 Codex** | `screen -dmS codex-task bash -c "export https_proxy=http://127.0.0.1:1087 http_proxy=http://127.0.0.1:1087 && codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox '任务' 2>&1 | tee /tmp/codex-task.log"` |
| **韩国 Codex** | `ssh ... "screen -dmS kr-task bash -c 'codex exec ...'"` |

**查看/管理**：`screen -ls` / `screen -r 任务名` / `Ctrl+A D` 分离 / `tail -f /tmp/xxx.log`

---

## 📄 文件分享规范（2026-04-24 新增）

给朋友分享任何内容前，必须脱敏：
- ❌ API Key / Token → 改为 `[YOUR_KEY]` 或空
- ❌ Cookie / user_id → 全部删除
- ❌ 个人路径 → 改为通用路径（如 `~/.claude/`）
- ❌ 密码/授权码 → 全部删除
- ❌ 内部群ID/服务器IP → 删除或占位符

**触发词**："发给你"、"发给朋友"、"分享"、"发个文档"

---

**核心规则**:
- ✅ 截图/生成文件保存到: `~/.openclaw/workspace/` 目录
- ✅ 转发用户文件: 使用 `~/.openclaw/media/inbound/` 路径
- ❌ 绝对不要用: `/tmp/` 目录（飞书接收会失败）

**截图命令**:
```bash
/usr/sbin/screencapture -x ~/.openclaw/workspace/screenshot.png
```

**发送文档**:
```javascript
{
  "action": "send",
  "caption": "文档名称",
  "media": "/Users/zhaoruicn/.openclaw/workspace/filename.ext"
}
```

---

## 📧 Himalaya 邮件配置 (2026-04-02 新增)

**用途**：通过 himalaya CLI 发送 QQ 邮箱邮件

**配置**：
- 配置文件：`~/.config/himalaya/config.toml`
- 密码文件：`~/.config/himalaya/password`（600权限）
- 邮箱地址：1034440765@qq.com
- 授权码：已安全存储

**使用方式**：
```bash
# 发邮件
cat << 'EOF' | himalaya template send
From: 1034440765@qq.com
To: 收件人@邮箱.com
Subject: 主题
Content-Type: text/plain; charset=utf-8

正文...
EOF
```

### 🔐 技能包分享安全规范

**重要原则：分享技能包给朋友时，必须移除所有个人信息**

#### 必须移除的内容：
- API Key / Token（如雪球 xq_a_token、xq_id_token）
- Cookie 信息
- 用户ID（如飞书 user_id）
- 设备标识符
- 个人配置路径

#### 处理流程：
1. 创建配置模板文件（.template）
2. 将实际配置文件中的敏感信息替换为占位符
3. 打包时排除 .backup 等临时文件
4. 在文档中明确说明需要朋友自行配置

#### 示例（雪球配置）：
```python
# 分享前 - 需要改成：
XUEQIU_COOKIES = {
    'xq_a_token': '请填入你的token',
    'xq_id_token': '请填入你的id_token',
}
```

#### 已执行：
- ✅ 2026-03-07 stock-analysis-pro v2.1.0 清洁版已创建
- ✅ 朋友版本移除了所有Cookie和个人ID
- ✅ 添加了模板配置说明

**违反后果**：泄露Cookie可能导致账号被盗用、API额度被消耗等风险。

---

## 技能包自动备份系统 [2026-03-07 更新]

### 备份配置（已合并）
- **备份时间**: 每天 22:00
- **备份脚本**: `~/.openclaw/workspace/skills/system-backup/scripts/daily-backup.sh`
- **备份内容**:
  1. Memory → `/Volumes/cu/ocu/memory/`
  2. Skills → `/Volumes/cu/ocu/skills/`
  3. **Workspace Skills → `/Volumes/cu/ocu/workspace-skills/` (文件夹同步)**
  4. **Workspace Skills → `/Volumes/cu/ocu/skills-backup/*.tar.gz` (压缩包)**
  5. OpenClaw配置 → `/Volumes/cu/ocu/openclaw-config/`

### 两种备份格式
| 格式 | 位置 | 用途 |
|------|------|------|
| **文件夹同步** | `workspace-skills/` | 快速恢复、查看文件 |
| **tar.gz压缩包** | `skills-backup/` | 分享、迁移到其他电脑 |

### 保留策略
- 文件夹同步：始终保留最新版本
- tar.gz压缩包：保留最近30个历史版本

### 使用方法
```bash
# 查看备份
ls /Volumes/cu/ocu/workspace-skills/      # 文件夹版本
ls /Volumes/cu/ocu/skills-backup/         # 压缩包版本

# 恢复到新电脑
cd ~/.openclaw/workspace
tar -xzvf /Volumes/cu/ocu/skills-backup/latest

# 手动执行备份
~/.openclaw/workspace/skills/system-backup/scripts/daily-backup.sh
```

---

## 用户偏好设置 [2026-03-07]

### 股票报告偏好
- **涨跌颜色**: 涨用红色🔴，跌用绿色🟢（A股习惯）
- **自选股列表**: 每年初或调整时更新，移除海博思创(2026-03-09)

### 时区偏好
- **用户所在时区**: 北京时间 (CST, UTC+8)
- **系统当前时区**: 洛杉矶时间 (PST, UTC-8)
- **时间差**: 北京时间 = 系统时间 + 16小时

**要求**: 以后所有时间表述使用北京时间，避免混淆。

---

## 🧠 记忆系统维护规范 (2026-04-12)

### 记忆系统架构
```
1. memory/*.md → 每日自动记录 (source of truth)
2. archive_summary.md → 历史精华提炼 (每月25号整理)
3. claude.sqlite FTS → 新系统搜索 (~6ms, 0 token)
```

### 每月整理记忆流程
- **触发**: 每月25号（或积累满30天）
- **操作步骤**:
  1. 读取过去30天的每日md文件
  2. 提取精华内容 → 更新到 archive_summary.md
  3. 格式: 项目~时间~具体内容
  4. 删除已被合并的旧md文件
  5. 执行 `openclaw memory index --force` 重新索引

### Archive_summary.md 更新规则
- **结构**: 按项目分类，每个章节带日期
- **格式**: `### 项目名称 (2026-04-25)`
- **内容**: 保留具体详情（地址、功能、状态等）
- **保留**: 技能包清单、定时任务、重要教训

### 下次整理时间
- **预计**: 2026-04-25（飞书定时消息提醒）

---



|------|------|------|
| `/model MiniMax-M2.7` | minimax-cn/MiniMax-M2.7 | 主用模型 |
| `/model k2.5` | bailian/kimi-k2.5 | 百炼Kimi |

| `/model right` | rightcodes/right | Right.codes GPT-5.4 |
| `/model k2p5` | kimi-coding/k2p5 | Kimi Coding |

### 修复记录

**问题**：模型名称不匹配，显示 M2/M2.1 而不是 M2.7
**原因**：配置里模型 id 缺少 `minimax-cn/` 前缀，导致匹配到 OpenClaw 内置别名
**修复**：
- `openclaw.json`: 模型 id 从 `MiniMax-M2.7` 改为 `minimax-cn/MiniMax-M2.7`
- `models.json`: 同上
- `kimi-coding`: API Key 为 `sk-kimi-2sxCTUilQ9nPKSPAFHcO2gIm7EguvTWvmZwaVclW15ZKwWq4uWZxKAhIWbULJEmD`（2026-04-16 实测有效）

---

## AI模型矩阵（2026-04-24 更新）

**工具分工（2026-05 起）：**
| 工具 | 模型 | 用途 |
|------|------|------|
| **OpenClaw（我）** | MiniMax M2.7 | 日常对话（飞书） |
| **Claude Code CLI（Mac）** | DeepSeek V4 Flash | 本地开发 |
| **Codex（Mac）** | GPT-5.5 | 复杂任务（5月升级） |

**停用：** Opus、Kimi（2026-05 起不再续费）

- **API地址**: `https://api.minimaxi.com/v1/image_generation`
- **模型**: `image-01`
- **Key**: Token Plan的Key (sk-cp-xxx) 可用
- **认证**: Bearer Token

#### 图生图参数（subject_reference）
```python
{
    "model": "image-01",
    "prompt": "场景描述",
    "subject_reference": [{
        "type": "character",
        "image_file": "data:image/jpeg;base64,<照片base64>"
    }]
}
```

#### 限制
- 只支持单张照片参考
- 不能同时用多张（需要分步生成）
- 真实人物泳装照拒绝
- 政治人物体育恶搞场景可以

#### 成功案例
- 特朗普湖人23号隔扣 ✅
- 永野一夏和服照 ✅
- 永野一夏隔扣特朗普 ✅

---

- **已整理PPT技能包清单**：19个，推荐powerpoint-pptx
- **已使用image-process**：放大、去背景、换背景

---

## 📊 PPT智能生成系统 (2026-03-22)

### 工作流程
1. 用户 → Kimi深度思考 → 生成PPT内容大纲
2. 用户发送内容给我
3. 我套用模板 + MiniMax生成配图 → 生成完整PPTX
4. 发送PPTX给用户

### 模板
- 精美模板V2: `~/.openclaw/workspace/zero_carbon_template_v2.pptx`
- 配色: 深蓝(#0A2864) + 翠绿(#00B488)
- 比例: 16:9宽屏

### 记住要点
1. 用户先去Kimi深度思考生成内容
2. 用户发送内容给我
3. 我使用python-pptx套模板生成PPTX
4. 用MiniMax image-01生成配图并插入
5. 发送完整PPT给用户

---

## 🔧 MiniMax Skills (2026-03-23)

### 位置
- `~/.openclaw/workspace/skills/minimax-skills/`

### 核心Skill（当前在用）
| Skill | 功能 |
|-------|------|
| minimax-pdf | PDF生成/填写/重排版 |
| minimax-xlsx | Excel处理（XML模板） |
| pptx-generator | PPT生成/编辑 |

### 使用方式
- Claude Code读取SKILL.md作为指导
- 不直接触发，通过代码调用

---

## [PROJECT] Claude Code 使用
- 雪子在笔记本上通过 Trae 安装了 Claude Code
- 雪子自己先用懂，再教我怎么更好地调用
- 结论：OpenClaw(图形中枢) + Claude Code(命令行代码) 组合够用，不需要 Trae

- [ ] 处理GitHub 2FA #GitHub #待办
```


### Opus配置（雪子提供）
| 项目 | 值 |
|------|------|
| Provider | opus-proxy |
| Base URL | https://timesniper.club |
| API Key | sk-OLqePftCUT0kOGggfgGtgeMOE3km0hPXwxUf6FTpFFL7mdsJ |
| 模型 | claude-opus-4-6 |
| 调用方式 | sessions_spawn(model="opus-proxy/claude-opus-4-6") |

### MiniMax配置（已有）
| 项目 | 值 |
|------|------|
| Provider | minimax-cn |
| Base URL | https://api.minimaxi.com/anthropic |
| API Key | sk-cp-TaEn7XZH... |
| 模型 | MiniMax-M2.7 |

### Claude Code环境变量（给雪子CC用）
```bash
ANTHROPIC_AUTH_TOKEN=sk-OLqePftCUT0kOGggfgGtgeMOE3km0hPXwxUf6FTpFFL7mdsJ
ANTHROPIC_BASE_URL=https://timesniper.club
ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-4-6
ANTHROPIC_MODEL=claude-opus-4-6
```

### 使用场景
- 架构设计/算法审核 → Opus (opus-proxy/claude-opus-4-6)
- 执行开发/日常任务 → MiniMax (minimax-cn/MiniMax-M2.7)

---

## Claude Code ACP 集成 [2026-04-09 新增]

### 核心配置
| 组件 | 状态 | 路径 |
|------|------|------|
| acpx CLI | ✅ 已安装 | `/opt/homebrew/bin/acpx` v0.5.3 |
| 模型切换脚本 | ✅ | `~/.openclaw/workspace/scripts/cc-model-switch.sh` |
| 完整使用指南 | ✅ | `Claude Code ACP调用完整指南.md` (Obsidian) |

### 三层模型工作流
| 阶段 | 模型 | Session |
|------|------|---------|
| 架构设计 | Opus | arch |
| 执行开发 | MiniMax | dev |
| 验收审查 | Opus | review |

### 快速命令
```bash
# 模型切换
cc-model-switch.sh opus    # 架构/验收
cc-model-switch.sh minimax # 执行开发

# ACP 调用（必须先关闭 Claude GUI）
acpx claude -s <session> "任务" --approve-all

# 后台自动驾驶（重要！）
acpx claude sessions new --name bg-task
acpx claude -s bg-task --no-wait "用 autopilot 开发 xxx"
# 我可以做其他事，acpx 后台自动跑完
```

### 关键要点
- **必须关闭 Claude GUI** 才能用 acpx
- **当前模型**: MiniMax-M2.7（执行开发）
- **Opus**: 架构设计、验收审查
- **--no-wait**: 后台自动驾驶，做完一件我可以继续做其他的

## MiniMax MMX-CLI 命令行工具 (2026-04-11 新增)

### 安装
```bash
npm install -g mmx-cli
```

### API Key 配置（已配置）
```bash
export MINIMAX_API_KEY="sk-cp-TaEn7XZHReif66-VaxR-UZJuHCoYYYqho4xu6pV22L3MtAL9oImB0iubia4dRjZDN-0avV5_rSS2ggBC6w2gHYz1tYN0semS3mps1PrA9lS-16qJhoh8l3Q"
# 或
mmx auth login
```

### Token Plan 可用功能 ✅
| 功能 | 命令 | 状态 |
|------|------|------|
| 网络搜索 | `mmx search query "关键词"` | ✅ |
| 语音合成 | `mmx speech synthesize "文本" --voice xxx` | ✅ |
| 图片生成 | `mmx image generate "描述"` | ✅ |
| 文本对话 | `mmx text chat "消息"` | ✅ |
| 图片理解 | `mmx vision describe <图片>` | ✅ |
| 查看额度 | `mmx quota show` | ✅ |

### 需要 Max Plan 功能 ❌
| 功能 | 命令 | 状态 |
|------|------|------|
| 视频生成 | `mmx video generate` | ❌ 需要Max Plan |
| 音乐生成 | `mmx music generate` | ❌ 需要高级套餐 |

### 常用命令
```bash
# 搜索
mmx search query "比亚迪最新消息"

# 语音合成
mmx speech synthesize "你好" --voice female-tianmei --output test.mp3

# 查看可用声音
mmx speech voices

# 图片理解
mmx vision describe image.jpg

# 查看额度
mmx quota show

# 帮助
mmx --help
mmx <resource> --help
```

### 语音合成音色
- 中文：male-qn-*, female-*
- 英文：male-*, female-*, clever_boy, cute_girl 等
- 推荐：female-tianmei（甜妹）、male-qn-badao（霸道）

---

## 韩国V2Ray代理服务器 (2026-04-12 新增)

### 服务器信息
| 项目 | 值 |
|------|-----|
| IP | 43.108.18.71 |
| 端口 | 10086 |
| 协议 | VMess |
| UUID | 8285c54c-994e-4bc0-b923-2ba88cc7a7af |
| AlterId | 0 |
| 节点 | 阿里云韩国 |
| 配置 | 2核2G / 200M带宽 / 不限流量 |
| 费用 | 68元/年 |
| 系统 | Ubuntu 22.04 LTS |

### VMess链接
```
vmess://eyJ2IjoiMiIsInBzIjoiS29yZWEtVjJSYXkiLCJhZGQiOiI0My4xMDguMTguNzEiLCJwb3J0IjoiMTAwODYiLCJpZCI6IjgyODVjNTRjLTk5NGUtNGJjMC1iOTIzLTJiYTg4Y2M3YTdhZiIsImFpZCI6IjAiLCJuZXQiOiJ0Y3AiLCJzY3kiOiJhdXRvIiwidGxzIjoiIn0=
```

### 配置文件
- Clash配置: `~/.openclaw/workspace/korea-proxy.yaml`
- 快捷信息: `~/.openclaw/workspace/korea-v2ray-info.txt`

### 用途
- 访问 Google / GitHub / YouTube / OpenAI / Gemini 等海外站点
- Android: Clash for Android / V2RayNG
- Mac: ClashX / V2RayU
- 分流: 国内直连，海外代理

### 管理命令
```bash
# 服务器SSH
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71

# V2Ray状态
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "systemctl status v2ray"

# 重启V2Ray
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "systemctl restart v2ray"
```

---

## 韩国阿里云服务器 (2026-04-12 新增)

### 服务器信息
| 项目 | 值 |
|------|-----|
| IP | 43.108.18.71 |
| 价格 | 79元/年（含海外附加费11元）|
| 配置 | 2核2G / 200M带宽 / 不限流量 |
| 节点 | 阿里云韩国 |
| 系统 | Ubuntu 22.04 LTS |

### SSH访问
```bash
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71
```

### 已安装服务
1. **V2Ray** - 手机梯子（端口10086, VMess协议）
2. **Claude Code + CCR + Gemini** - 飞书机器人
3. **feishu-claude-code** - 飞书WebSocket接收指令

### 飞书机器人
- 名称: openclaw急救医生
- App ID: cli_a9184ac97e78dbdf
- App Secret: C1Y6RQz3c4NxCQXDB2GFDfEwzHoqRUzy
- 配置: bypassPermissions (ccuser身份，完全权限跳过)
- 工作目录: /home/ccuser/feishu-workspace
- 启动: `su - ccuser -c "bash ~/start-fc.sh"`

### V2Ray配置
- 端口: 10086
- 协议: VMess
- UUID: 8285c54c-994e-4bc0-b923-2ba88cc7a7af
- AlterId: 0
- VMess链接: vmess://eyJ2IjoiMiIsInBzIjoiS29yZWEtVjJSYXkiLCJhZGQiOiI0My4xMDguMTguNzEiLCJwb3J0IjoiMTAwODYiLCJpZCI6IjgyODVjNTRjLTk5NGUtNGJjMC1iOTIzLTJiYTg4Y2M3YTdhZiIsImFpZCI6IjAiLCJuZXQiOiJ0Y3AiLCJzY3kiOiJhdXRvIiwidGxzIjoiIn0=

### 备份
- 备份位置: /root/*.bak
- CCR备份: /root/.claude-code-router.bak
- 应用备份: /root/feishu-claude-code.bak

### 用途
- 手机梯子（V2RayNG）
- 飞书Claude Code机器人（Gemini 2.5 Flash）
- 直连OpenAI/GitHub/Google AI
- 海外API代理

## 记忆管理规则 (2026-04-12更新)
- Obsidian文件：可以删除已总结过的文件
- 本地memory/：禁止删除，只能每月25号归档精华

### 韩国服务器安全加固 (2026-04-12)
- SSH密码认证：已关闭（PasswordAuthentication no）
- RootLogin：已改为without-password
- 管理方式：通过雪子助手（我）统一管理，不给笔记本存SSH密钥

---

## 韩国CC Codex后台调用体系 (2026-04-13)

### 核心工具链（韩国服务器）
| 工具 | 路径 | 用途 |
|------|------|------|
| acpx | /home/ccuser/.nvm/versions/node/v20.20.2/bin/acpx | ACP协议客户端，后台任务调度 |
| codex | PATH中（Node 20） | OpenAI Codex CLI |
| omx | PATH中（npm global） | oh-my-codex编排层（20个Agent） |
| ccr | /home/ccuser/.nvm/versions/node/v20.20.2/bin/ccr | Claude Code Router（127.0.0.1:3456） |

### acpx正确用法（关键！）
```bash
# 创建持久session
acpx codex sessions new

# 后台丢任务，立即返回（不超时！）
acpx codex --no-wait "任务描述" --cwd /项目路径

# 查看状态
acpx codex status

# 取消任务
acpx codex cancel

# 查看session列表
acpx codex sessions
```

**核心区别**：
- `codex exec` → 任务在会话里跑，会话超时即终止
- `acpx --no-wait` → 任务在独立后台进程跑，完全不超时

### oh-my-codex（omx）20个专业Agent
| Agent | 职责 |
|-------|------|
| architect | 系统设计 |
| planner | 任务拆解 |
| executor | 代码实现 |
| analyst | 需求澄清 |
| critic | 计划/设计审查 |
| code-reviewer | 全方位代码审查 |
| security-reviewer | 安全漏洞检查 |
| debugger | 根因分析 |
| test-engineer | 测试策略 |
| researcher | 外部文档调研 |
| designer | UX/UI设计 |
| git-master | Git提交策略 |
| verifier | 完成验证 |
| team-executor | 团队协作执行 |

### 我调用韩国CC的方法（2026-04-17验证更新）
```bash
# SSH到韩国服务器，用完整路径调用acpx
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && /home/ccuser/.nvm/versions/node/v20.20.2/bin/acpx codex sessions new --name <session-name>'"

# 后台任务（关键：必须在session的cwd目录下执行，即/home/ccuser）
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && cd /home/ccuser && /home/ccuser/.nvm/versions/node/v20.20.2/bin/acpx codex -s <session-name> --no-wait \"任务描述\"'"
```

**关键要点（2026-04-17验证）**：
1. ✅ acpx路径：`/home/ccuser/.nvm/versions/node/v20.20.2/bin/acpx`
2. ✅ 必须source nvm.sh加载Node环境
3. ✅ 必须cd到session的cwd目录（默认/home/ccuser）
4. ✅ 使用`-s <session-name>`指定session
5. ✅ `--no-wait`模式：任务在独立后台进程跑，完全不超时

### 韩国CC记忆文件位置
- `/home/ccuser/.claude/memory/acpx-and-oh-my-codex.md`（完整文档）

### 注意事项
1. acpx必须用完整路径（Node 20环境）
2. --no-wait依赖已创建的session，先sessions new
3. **必须在session的cwd目录下执行**（默认/home/ccuser）
4. ccr服务需手动管理（127.0.0.1:3456）

### 常见问题
| 问题 | 原因 | 解决 |
|------|------|------|
| `⚠ No acpx session found` | 不在session的cwd目录 | `cd /home/ccuser`后再执行 |
| `command not found` | nvm环境未加载 | 先执行`source ~/.nvm/nvm.sh` |
| `agent needs reconnect` | session已断开 | 重新创建session |

---

## 股票数据系统 (2026-04-13 更新)

### 数据库
- 路径：`/Volumes/cu/ocu/stock-screener/cache/tencent_cache.db`
- 格式：SQLite，约5826只股票
- 代码格式混用：sh600007 / 001201.SZ

### 增量更新
```bash
python3 /Volumes/cu/ocu/stock-screener/incremental_update.py
```
- 只更新date < '2026-04-10'的股票
- 支持混合格式代码
- 耗时约5-10分钟

### 策略B v5模拟盘
- Obsidian：`生活投资/模拟策略/模拟盘汇总.md`
- 本地持仓：`~/.openclaw/workspace/simulator/portfolio.json`
- 策略程序：`/Volumes/cu/ocu/stock-screener/strategies/strategy_b_final.py`

### 更新模拟盘
```bash
cd ~/.openclaw/workspace/simulator && python3 update_obsidian.py
```

### 完整每日检测
```bash
cd ~/.openclaw/workspace/simulator && python3 core.py
```

### 工作流文档
- `/Volumes/cu/ocu/stock-screener/README.md`


---

## AI Coder 脚本使用指南 (2026-04-17 新增，2026-04-19 重大更新)

**位置**: `~/.openclaw/workspace/ai_coder/`

### 功能
统一调用本地 Claude Code (MiniMax/Opus) 和韩国 Codex (GPT-5.4) 的安全 CLI 工具。

### 环境变量（已配置）
```bash
export AI_CODER_KR_HOST="43.108.18.71"
export AI_CODER_KR_USER="ccuser"
export AI_CODER_SSH_KEY="$HOME/.ssh/id_ed25519"
```

### 快速使用

```bash
# 本地执行（MiniMax/Opus）
cd ~/.openclaw/workspace/ai_coder
python3 -m ai_coder exec "任务" -p local -s SESSION --wait

# 韩国执行（Codex GPT-5.4）
PYTHONPATH=ai_coder python3 -m ai_coder exec "任务" -p kr -s SESSION --wait

# 后台模式（不阻塞）
PYTHONPATH=ai_coder python3 -m ai_coder exec "任务" -p local --no-wait
```

### 常用命令

| 命令 | 说明 |
|------|------|
| `exec` | 执行单次任务 |
| `session-new NAME` | 创建 session |
| `session-close NAME` | 关闭 session |
| `status -s NAME` | 查询状态 |
| `skills` | 列出 skills |

### 子 Agent 调用（推荐）

```python
sessions_spawn({
    "task": "cd ~/.openclaw/workspace && PYTHONPATH=ai_coder python3 -m ai_coder exec '任务' -p local -s SESSION --wait",
    "runtime": "subagent",
    "runTimeoutSeconds": 300
})
```

### 文档
- `ai_coder/README.md` - 完整文档
- `ai_coder/QUICKSTART.md` - 快速参考
- `skills/ai-coder/SKILL.md` - Skill 指南

---

## 韩国CC Codex调用更新 (2026-04-14)

### acpx codex ✅已验证可用
```bash
# 创建session
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c /home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx codex sessions new --name bg-task"

# 后台调用
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c /home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx codex -s bg-task --no-wait "任务""
```

### 详细文档（已过时，使用 AI Coder 替代）
- ~~~/.openclaw/workspace/docs/韩国CC-Codex后台调用指南.md~~ → 使用 `ai_coder exec '任务' -p kr`


## 双CC调度体系 (2026-04-14)

### 我有两个超级助手

| | 本地Codex (GPT-5.4) | 韩国Codex | 本地Claude (MiniMax) |
|---|---|---|---|
| **模型** | GPT-5.4 | GPT-5.4 | MiniMax M2.7 |
| **上下文** | 100万token | 100万token | 200k |
| **优势** | 编程最强、中文好 | 备选 | 快速问答 |
| **调度方式** | screen + proxy | screen | sessions_spawn |

### 模型分配（2026-04-22 更新）
| 任务类型 | 模型 | 说明 |
|---------|------|------|
| **执行开发** | **本地Codex** (GPT-5.4) ✅ | 主力干活，编程最强 |
| **架构设计** | Opus | 系统设计、技术选型 |
| **验收审查** | Opus | 质量把关 |
| **快速问答** | 本地Claude (MiniMax) | 中文、日常问题 |
| **复杂/大型** | 韩国Codex | 备选方案 |

### 核心记忆
- 本地CC：sessions_spawn(model="minimax-cn/MiniMax-M2.7")
- 韩国Codex：acpx codex sessions new + --no-wait

### 位置
~/.openclaw/workspace/.agents/skills/buffett-perspective/SKILL.md

### 触发词
- 「用巴菲特的视角」「巴菲特会怎么看」「巴菲特模式」「Buffett perspective」
- 「帮我用巴菲特的角度想想」「如果巴菲特会怎么做」「切换到巴菲特」

### 6个核心心智模型
1. 经济护城河 (Economic Moat)
2. 能力圈 (Circle of Competence)
3. 市场先生 (Mr. Market)
4. 复利滚雪球 (Compounding Snowball)
5. 制度性强制力 (Institutional Imperative)
6. 所有者思维 (Owner Mindset)

### 8条决策启发式
- 安全边际规则
- 管理层诚信优先
- 打孔卡规则
- 棒球甜蜜区规则
- 蟑螂规则
- 5分钟规则
- 报纸测试
- "太难"篮子

### 退出角色
用户说「退出」「切回正常」「不用扮演了」时恢复正常模式


## 备份系统修复记录 (2026-04-15)

### 问题描述
每日备份(cron任务)连续多天失败，日志显示 Operation not permitted

### 根因分析
macOS TCC权限限制：cron任务没有完全磁盘访问权限(FDA)，被系统安全机制拦截外置APFS卷写入。

### 修复步骤
1. 添加FDA权限：系统设置 > 隐私与安全性 > 完全磁盘访问权限 > 添加 /bin/bash、/usr/sbin/cron
2. 备份脚本升级：v2.3 > v2.4
   - safe_cp()替代cp 2>/dev/null（不再静默吞错误）
   - 新增backup_workspace_configs()（备份MEMORY.md等6个核心文件）
   - 改用白名单SKILLS_TO_BACKUP，只备份memory-suite-v4

### 关键文件
- 备份脚本：~/.openclaw/workspace/skills/system-backup/scripts/daily-backup-v2.sh
- 备份目标：/Volumes/cu/ocu/
- 核心配置备份：/Volumes/cu/ocu/workspace-configs/

### 经验教训
- macOS cron任务默认没有FDA权限，访问外置卷会被TCC拦截
- mkdir -p对已存在目录不触发TCC，但写入新文件会
- cp -r 2>/dev/null会静默吞掉所有错误

---

## 本地 Claude Code 调用规范（2026-04-16 记住）

### 调用流程
1. **检查 GUI 已关闭**：`pgrep -x "Claude" && echo "需关闭" || echo "OK"`
2. **切换模型**：
   - `~/.openclaw/workspace/scripts/cc-model-switch.sh opus`（架构/验收）
   - `~/.openclaw/workspace/scripts/cc-model-switch.sh minimax`（执行开发）
3. **创建 session**：`acpx claude sessions new --name <session名>`
4. **执行任务**：
   - `acpx claude -s <session名> --no-wait "任务"`（后台，不阻塞）
   - `acpx claude -s <session名> "任务"`（等待结果）
5. **查看结果**：`tail ~/.acpx/sessions/<id>.stream.ndjson`
6. **关闭 session**：`acpx claude sessions close <session名>`

### 关键事实
- acpx 用的是本地 Claude CLI，不是远程服务器
- `~/.claude/settings.json` 控制模型配置
- `model: default` = Opus 4.6（已配置在 settings.json）
- 切 opus 后用完记得切回 minimax，避免影响我自己的响应质量

## 韩国服务器 Claude Code 记忆文件

**位置：** `/home/ccuser/memory.json`

**内容结构：**
```json
{
  "last_updated": "2026-04-18",
  "user_profile": { "name": "用户", "language": "中文" },
  "long_term_memory": [
    { "key": "server_info", "content": "服务器状态" },
    { "key": "software_versions", "content": "oh-my-codex: 0.12.5, codex-cli: 0.121.0" }
  ],
  "recent_tasks": [ ... ]
}
```

**读取命令：**
```bash
ssh root@43.108.18.71 "cat /home/ccuser/memory.json"
```


## Right.codes GPT-5.4 API (2026-04-22 新增)

### API信息
| 项目 | 值 |
|------|-----|
| API地址 | `https://www.right.codes/codex/v1/responses` |
| API Key | `[已删除]` |
| 模型名 | `gpt-5.4-high`（内部映射到`gpt-5.4`） |
| API格式 | OpenAI Responses API |
| 上下文 | 100万token |
| 费用 | ~$0.004/K tokens（比Feinian便宜很多） |

### 调用格式
```python
requests.post(
    "https://www.right.codes/codex/v1/responses",
    headers={"Authorization": "Bearer [已删除]"},
    json={
        "model": "gpt-5.4-high",
        "input": [{"type": "message", "role": "user", "content": [{"type": "input_text", "text": "问题"}]}]
    }
)
```

### OpenClaw配置
- Provider名: `rightcodes`
- 模型ID: `rightcodes/gpt-5.4-high`
- 用途: 备用GPT-5.4代理，比Feinian更便宜

### 状态
- ✅ 已测试可用（2026-04-22）

## DeepSeek-V4 API (2026-04-24 新增)

### API信息
| 项目 | 值 |
|------|-----|
| API地址 | `https://api.deepseek.com/v1` |
| API Key | `sk-829a69f62a054d0f9a9ff3d79d7909b0` |
| 模型 | DeepSeek-V4-Flash (`deepseek-v4-flash`) |
| API格式 | OpenAI Completions (`openai-completions`) |
| 上下文 | 1M token |

### OpenClaw配置
- Provider名: `deepseek`
- 模型ID: `deepseek/deepseek-v4-flash` |
| 状态 | ✅ 已配置（2026-04-24）

### 雪子实测评价（2026-04-24）
- **文本分析**: 比 MiniMax 强，接近 GPT-5.4
- **代码能力**: 生成游戏代码（如植物大战僵尸）比 MiniMax 更丰富
- **结论**: 可作为生产主力模型，性价比极高（约为 GPT-5.4 的 1/10 价格）
