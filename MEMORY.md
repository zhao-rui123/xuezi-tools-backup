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

- 电价查询工具在GitHub Pages备用站使用iframe嵌入主站
- 如主站无法访问，备用站的电价查询会显示错误提示，需下载离线包使用
- 其他五个工具在备用站可独立正常使用

**参考技能包**: `skills/feishu-image-send/SKILL.md`（支持图片、文档、文本等）

## 💡 Codex风格执行准则（精简版，2026-04-26）

### 核心6条

1. **先读上下文再动手** — 不熟悉的任务先读相关文件、日志、配置，再下结论
2. **先拿证据再判断** — 优先用搜索、读文件、日志、最小验证确认事实，不凭猜测回答
3. **改动最小且只改相关内容** — 只修改当前问题涉及的文件和逻辑，不顺手重构
4. **关键验证必须等结果** — 验证失败不能当成功交付
5. **汇报必须包含三件事** — 改了什么、为什么这么改、还剩什么风险或未验证项
6. **不是所有任务都后台跑** — 搜索/读文件/单次验证优先前台执行；只有长任务/易断任务才用screen

### 7条执行补充约束

1. **先说动作再动手** — 实质性工作前先说明意图和先查什么/改什么
2. **最终汇报固定格式** — 改了什么、怎么验证的、还有什么风险
3. **区分分析任务和执行任务** — 问方案先分析不急着改，让修让改默认直接动手
4. **不要把猜测当事实** — 不确定先查，明确说“这是推断”
5. **发现冲突先停** — 有冲突先汇报，不要直接覆盖
6. **能局部验证就不要全量折腾** — 先最小验证再决定扩大范围
7. **新旧规则冲突时优先删旧规则** — 避免文档自相矛盾

---

## 🤖 Claude Code / Codex screen 调用规范（2026-04-26 更新）

**原则：screen 用于长任务/易断任务；搜索/读文件/单次验证用前台执行**

| 工具 | 场景 | 命令 |
|------|------|------|
| **本地 Claude Code** | 长任务、易断任务 | `screen -dmS claude-task bash -c "claude --print '任务' 2>&1 | tee /tmp/claude-task.log"` |
| **本地 Codex** | 长任务、易断任务 | `screen -dmS codex-task bash -c "export https_proxy=http://127.0.0.1:1087 http_proxy=http://127.0.0.1:1087 && codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox '任务' 2>&1 | tee /tmp/codex-task.log"` |
| **韩国 Codex** | 长任务、易断任务 | `ssh ... "screen -dmS kr-task bash -c 'codex exec ...'"` |
| **快速验证/搜索** | 前台执行 | 直接调用，拿到结果再继续 |

**关键路径验证必须等待结果，不能只启动不确认。**
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
## AI模型矩阵（2026-04-27 更新）

**工具分工（三档架构）：**
| 工具 | 模型 | 用途 |
|------|------|------|
| **OpenClaw（我）** | MiniMax M2.7 | 飞书日常对话、轻执行 |
| **Claude Code CLI（Mac）** | DeepSeek V4 Flash | 本地开发主力（默认） |
| **Claude Code CLI（Mac）+ Feinian** | GPT-5.4 | 复杂任务/深度研究 |

**Claude Code 调用规范：**
- `sessions_spawn` → 适合快速任务（分钟级），会超时
- **大项目必须走screen**：
  - DeepSeek主力：`screen -dmS cc-task bash -c "claude --print '任务' 2>&1 | tee /tmp/cc-task.log"`
  - GPT-5.4复杂任务：`screen -dmS cc-gpt-task bash -c "claude --model opus --print '任务' 2>&1 | tee /tmp/cc-gpt-task.log"`
- 代理必须：Codex `export https_proxy=http://127.0.0.1:1087 http_proxy=http://127.0.0.1:1087`

**Feinian配置（GPT-5.4链路）：**
```bash
export ANTHROPIC_AUTH_TOKEN="sk-abcredai-..."
export ANTHROPIC_BASE_URL="https://ai.feinian.net"
export ANTHROPIC_MODEL="claude-sonnet-4-6"
```

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

- [x] GitHub 2FA 已完成 #GitHub #待办



## MiniMax MMX-CLI 命令行工具 (2026-04-26 更新)

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
vmess://eyJ2IjoiMiIsInBzIjoiS29yZWEtVjJSYXkiLCJhZGQiOiI0My4x...（完整链接已精简，详见 TOOLS.md）
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
- VMess链接: vmess://eyJ2IjoiMiIsInBzIjoiS29yZWEtVjJSYXkiLCJhZ...（完整链接已精简，详见 TOOLS.md）

### 备份
- 备份位置: /root/*.bak
- CCR备份: /root/.claude-code-router.bak
- 应用备份: /root/feishu-claude-code.bak

### 用途
- 手机梯子（V2RayNG）
- 直连OpenAI/GitHub/Google AI
- 海外API代理

### 核心定位：AI容灾备用机器人

**三级AI容灾体系（2026-04-26确认）：**
1. **本地Mac** → OpenClaw（我）+ Claude Code 主力
2. **本地Claude Code** → 本地开发主力
3. **韩国服务器Claude Code机器人** → 备用应急

**触发条件**：
- 笔记本不在身边 / 无法Tailscale进Mac命令行
- 本地AI进程挂了无法快速恢复
- 通过飞书直接唤醒韩国服务器CC处理紧急任务

**飞书机器人**：openclaw急救医生（Gemini 2.5 Flash）

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

## OpenClaw gpt-image-2 接入修复 (2026-04-26)

### 最终状态
- OpenClaw 已可通过本地插件 `~/.openclaw/local-plugins/openai-codex-image/` 调用 `openai-codex/gpt-image-2`
- 在线 gateway 实测已打通，用户反馈“通了通了”

### 根因
- 插件最初按普通 JSON responses 解析，实际 `chatgpt.com/backend-api/codex/responses` 图片接口要求：
  - 顶层必须有 `instructions`
  - 必须 `store: false`
  - 必须 `stream: true`
  - 图片结果从 SSE 事件 `response.image_generation_call.partial_image.partial_image_b64` 中取
- 自定义 HTTPS/CONNECT 传输最初过早 `socket.end()`，只收到前几帧 SSE，拿不到图片事件
- gateway 在线进程由 `launchd` 启动，没有 `HTTP_PROXY/HTTPS_PROXY` 环境变量；因此 smoke test 能过但在线调用仍可能报 `AggregateError`

### 关键修复
- 修改插件文件：`~/.openclaw/local-plugins/openai-codex-image/index.js`
  - 改成正确的 Codex 图片 SSE 协议
  - 加入本地 HTTP 代理隧道支持
  - 修复 SSE 读取时连接过早关闭问题
- 修改插件配置 schema：`~/.openclaw/local-plugins/openai-codex-image/openclaw.plugin.json`
- 修改 OpenClaw 配置：`~/.openclaw/openclaw.json`
  - `agents.defaults.imageGenerationModel.primary = "openai-codex/gpt-image-2"`
  - `plugins.entries["openai-codex-image"].config.proxyUrl = "http://127.0.0.1:1087"`

### 重要结论
- 不要给整个 gateway 挂全局代理，否则可能影响 Feishu
- 只给 `openai-codex-image` 插件单独配 `proxyUrl`，让图片请求走 `127.0.0.1:1087`
- 本机代理不通时，`gpt-image-2` 在线调用大概率会再次报 `AggregateError`
