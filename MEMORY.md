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
| `/model qwen` | bailian/qwen3.5-plus | 通义千问 |
| `/model k2p5` | kimi-coding/k2p5 | Kimi Coding |

### 修复记录

**问题**：模型名称不匹配，显示 M2/M2.1 而不是 M2.7
**原因**：配置里模型 id 缺少 `minimax-cn/` 前缀，导致匹配到 OpenClaw 内置别名
**修复**：
- `openclaw.json`: 模型 id 从 `MiniMax-M2.7` 改为 `minimax-cn/MiniMax-M2.7`
- `models.json`: 同上
- `kimi-coding`: 更新 API Key 为 `sk-kimi-vmWHuNEuueGIo1Cc9zRy7PTTrQLIs3gAEgHkDCUMphSbXpcb6xAiwznaIs5KSKQn`

---

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
