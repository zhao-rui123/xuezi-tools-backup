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

## 备份信息
- **备份文件**: `xuezi-tools-backup.tar.gz` (2.0MB)
- **备份位置**: 
  - 腾讯云服务器: `/usr/share/nginx/html/xuezi-tools-backup.tar.gz`
  - GitHub仓库: https://github.com/zhao-rui123/xuezi-tools-backup
- **最后备份时间**: 2026-02-20

## 恢复方法
```bash
# 解压到网站目录
tar -xzvf xuezi-tools-backup.tar.gz -C /usr/share/nginx/html/

# 设置权限
chmod -R 755 /usr/share/nginx/html/*
chmod 644 /usr/share/nginx/html/*/index.html
```

## 电价数据更新流程
- **更新频率**: 每月（用户主动通知）
- **更新方式**: 用户告知需要更新的省份 → 我修改数据 → 重新部署 → 更新GitHub备份
- **数据来源**: 各省发改委/电网公司官方文件

## 注意事项
- 电价查询工具在GitHub Pages备用站使用iframe嵌入主站
- 如主站无法访问，备用站的电价查询会显示错误提示，需下载离线包使用
- 其他五个工具在备用站可独立正常使用

## 飞书文件发送（重要！）
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

## 🚨 会话恢复机制（已更新 v3.0）

### 问题场景
- AI 意外卡死，只能打 `/new` 强制新建
- 新会话后完全失忆，不知道之前聊了什么

### 解决方案

**1. 自动定期保存（新！防卡死）**
- ⏰ **每10分钟自动保存一次**（后台cron任务）
- 即使卡死，最多丢失10分钟的工作
- 保存位置: `memory/snapshots/current_session.json`

**2. 关键节点自动保存**
- 重要任务完成后自动保存
- 用户说"拜拜/去做别的了"时自动保存

**3. 手动快速保存**
```bash
# 快速保存当前状态
ss "正在做的任务"
```

**4. 急救口令恢复**
新会话后，我会自动加载最近快照并报告：
- "根据自动保存记录，你最后在做：**整合记忆系统+进化系统+知识库管理**"

### 当前自动保存状态
**自动保存间隔**: 每5分钟  
**最后保存时间**: 检查 `memory/snapshots/current_session.json`  
**最大丢失时间**: 5分钟

---

---

## 工商业储能项目测算（核心技能）

**功能：** 根据用户提供的储能项目参数和省份电价数据，自动计算项目财务指标

**使用方法：**
```
计算 [省份] [年份]年[月份]月 工商业储能
- 容量：X kWh
- 设备成本：X 元/kWh
- 施工成本：X 元/kWh
- 效率：X%
- DOD：X%
- 运营期：X年
```

**数据来源：**
- 电价数据：从电价查询程序实时提取（服务器 `/electricity/`）
- 循环次数：双峰值法计算结果（已内置在电价程序中）

**已验证案例：**
- 河南2026年2月：1000kWh，15年ROI 407%，回收期3.7年
- 山东2026年2月：1000kWh，15年ROI 548%，回收期2.7年
- 浙江2026年2月：1000kWh，第三方投资，业主分成20%

---

## 后台Agent开发流程（关键记录）

**技能包组合**：
- **multi-agent-cn** - 5个固定子Agent并行开发
- **agent-team-orchestration** - 任务生命周期和质量控制

**团队角色**：
| 角色 | 职责 |
|------|------|
| Orchestrator（我） | 路由任务、跟踪状态、统一部署 |
| Alpha | Builder - HTML/CSS界面开发 |
| Bravo | Builder - JavaScript/算法开发 |
| Charlie/Delta | Builder/Reviewer - 功能完善、修复问题 |
| Echo | Reviewer/Ops - 测试验证、检查质量 |

**标准开发流程**：
1. **需求确认**（Orchestrator）- 整理功能清单、评估任务等级
2. **任务分配**（Orchestrator）- 拆解任务、明确输出路径
3. **并行开发**（Builders）- 子Agent在本地创建文件
4. **审查验证**（Reviewers）- 功能测试、代码审查、文件完整性检查
5. **统一部署**（Orchestrator）- 使用 `scp` 上传到服务器
6. **迭代优化**（循环）- 根据反馈继续完善

**成功案例**：
- **储能电站不规则土地智能排布系统** - http://106.54.25.161/storage-layout-ai/
- **国网电费清单处理系统** - http://106.54.25.161/energy-bill-processor/

---

## 自选股列表

| 股票名称 | 代码 | 行业 |
|---------|------|------|
| 赣锋锂业 | 002460 | 锂电池/新能源 |
| 中矿资源 | 002738 | 锂矿/资源 |
| 盐湖股份 | 000792 | 盐湖提锂 |
| 盛新锂能 | 002240 | 锂电池材料 |
| 京东方A | 000725 | 面板/显示 |
| 彩虹股份 | 600707 | 面板/显示 |
| 中芯国际 | 688981 | 半导体/芯片 |

**主题**: 锂矿+面板+半导体，新能源与硬科技产业链布局

---

## OpenClaw 系统配置（关键修复文档）

> **来源**: `/Volumes/cu/ocu/OpenClaw配置指导.md`  
> **用途**: 系统故障修复和模型配置参考

### 当前模型配置（2026-03-09 更新）
| 模型 | Provider | 特点 | 切换命令 |
|------|----------|------|----------|
| kimi-k2.5 | bailian | 识图，256k上下文 | `/model k2.5` |
| k2p5 | kimi-coding | 推理+识图，262k上下文 | `/model k2p5` |
| qwen3.5-plus | bailian | 262k上下文 | `/model qwen` |
| MiniMax-M2.5 | minimax-cn | 256k上下文 | `/model Minimax` |

### API Key 格式
- **MiniMax**: `sk-cp-...`
- **百炼 Coding Plan**: `sk-sp-...` (当前在用)
- **Kimi API**: `sk-kimi-...`

### 核心命令
```bash
# Gateway 管理
openclaw gateway status    # 查看状态
openclaw gateway restart   # 重启（修改配置后必须执行）

# 模型切换
openclaw config set agents.defaults.model.primary "bailian/kimi-k2.5"

# 故障修复
openclaw doctor --fix      # 自动修复配置
```

### 关键文件路径
- **主配置**: `~/.openclaw/openclaw.json`
- **Agent配置**: `~/.openclaw/agents/main/agent/models.json`
- **认证配置**: `~/.openclaw/agents/main/agent/auth-profiles.json`
- **飞书配置**: `channels.feishu.appId/appSecret`

### 故障排查速查
1. **模型不允许**: 检查 `openclaw.json` 和 `models.json` 是否都有该模型
2. **API Key 失败**: 确认 Key 格式（Coding Plan vs 标准接口）
3. **Gateway 连接失败**: `lsof -i :18789` 检查端口占用
4. **飞书连接失败**: 检查 `appId` 和 `appSecret` 配置

### 定时任务
- **备份任务**: 每天 00:00 自动备份 memory/ 到 `/Volumes/cu/ocu/memory/`
- **脚本位置**: `~/.openclaw/workspace/backup_memory.sh`

### 模型切换速查（2026-03-09 更新）

| 命令 | 切换到 | 特点 |
|------|--------|------|
| `/model k2.5` | bailian/kimi-k2.5 | 百炼Kimi，识图 |
| `/model k2p5` | kimi-coding/k2p5 | Kimi官方，推理+识图 |
| `/model qwen` | bailian/qwen3.5-plus | 通义千问 |
| `/model Minimax` | minimax-cn/MiniMax-M2.5 | 256K上下文 |

**旧命令（仍可用）：**
```bash
openclaw config set agents.defaults.model.primary "bailian/kimi-k2.5"
openclaw gateway restart
```

### 飞书发图片方法（2026-03-03 更新）

**问题：** OpenClaw `message` 工具发送本地图片文件有 bug，返回成功但实际未发送。

**解决方案：**
1. **用户先发图给我** → 我转发或修改后发回 ✅
2. **使用 inbound 目录的图片** - 路径：`/Users/zhaoruicn/.openclaw/media/inbound/[uuid].png`
3. **避免使用 `/tmp/` 目录** - 权限或路径处理问题

**正确示例：**
```javascript
// ✅ 使用 inbound 目录的图片（用户发给我的）
message({
  action: "send",
  target: "ou_5a7b7ec0339ffe0c1d5bb6c5bc162579",
  caption: "说明文字",
  media: "/Users/zhaoruicn/.openclaw/media/inbound/xxx.png"
})

// ❌ 避免使用 /tmp/ 目录
media: "/tmp/test.png"  // 会失败
```

**替代方案：**
- 上传到网站服务器，发 URL 链接
- 使用直接 API 调用（curl）绕过 OpenClaw 工具


## 记忆更新 [2026-03-07 晚间]

### [DECISION] 重要决策
- 确定竞品分析新流程：用户截图 → 我识图分析整理
- 明确不主动搜索，避免卡死
- Kimi Coding API 配置成功，当前模型：kimi-coding/k2p5

### [TODO] 待办事项
- [x] 创建12个新技能包（股票/税务/财务/安全/运维）
- [x] 完成技能包备份（skills-backup-20260307_185105.tar.gz）
- [x] 修复 API 配置
- [ ] 等待竞品分析截图

### [PROJECT] 项目进展
- **技能包生态**: 20+技能包，代码行数10,000+
- **股票分析系统**: v2.1.0 生产就绪
- **备份系统**: ✅ 今日备份完成

### [DATA] 关键数据
- **今日新增技能包**: 12个
- **备份文件**: skills-backup-20260307_185105.tar.gz
- **当前模型**: kimi-coding/k2p5

---

## 🧠 自我改进学习库 [持续更新]

### 核心行为准则

| # | 场景 | 必须遵守 | 违反后果 |
|---|------|---------|---------|
| 1 | **竞品分析** | 用户发截图 → 我识图分析 | 主动搜索→卡死 |
| 2 | **API配置/修改** | 只处理用户明确给的内容 | 主动查找→卡死 |
| 3 | **系统维护** | 主动检查定时任务/技能包状态 | 被动等待→遗漏问题 |

### 今日学习项 [2026-03-07]

**error-001: 主动行为边界**
- 场景：新增API配置时主动搜索
- 问题：导致卡死
- 解决：只处理用户明确提供的内容

**workflow-001: 竞品分析流程**
- 标准流程：用户截图 → 我识图分析整理
- 禁止：主动搜索网站信息

**habit-001: 系统自检习惯**
- 每日检查：定时任务运行状态
- 每周检查：技能包健康度
- 定期：记忆整理归档

---

## 记忆更新 [2026-03-04]

### [DECISION] 重要决策
- 确定飞书文件发送正确路径（workspace目录有效，/tmp无效）
- 建立技能包版本管理机制
- 创建灾难恢复手册
- 确定OpenClaw不更新（新版本有bug）
- 系统维护自动化（每日健康检查+每周清理）

### [TODO] 待办事项
- [x] 完善飞书文件发送技能包
- [x] 搭建知识库管理体系
- [x] 添加代码管理、运维监控、项目跟踪技能包
- [x] 添加数据处理、报告生成技能包
- [x] 修复备份脚本bug
- [x] 创建系统维护脚本
- [x] 创建每日健康检查报告
- [x] 重构文件管理体系
- [x] 添加上下文管理技能包
- [x] 创建灾难恢复手册
- [x] 生成OpenClaw系统全景报告

### [PROJECT] 项目进展
- **知识库管理体系**: ✅ 完成，包含projects/decisions/problems/references
- **技能包生态**: ✅ 27个技能包覆盖全场景
- **自动化运维**: ✅ 4个定时任务自动执行
- **文件管理规范**: ✅ 目录结构+命名规范+自动清理
- **系统稳定性**: ✅ 95分，生产就绪

### [DATA] 关键数据
- **Git提交次数**: 今日7次提交
- **新增技能包**: 15个
- **新增脚本**: 6个
- **系统运行时间**: Gateway运行3天+无中断
- **磁盘使用**: 本地22%，备份磁盘1%

---

## 记忆更新 [2026-03-03]

### [DECISION] 重要决策
- 确定使用新浪财经免费API获取实时股票数据
- 设置每日收盘后自动发送自选股报告（工作日15:30）
- 建立飞书图片发送的正确方式（workspace目录有效，/tmp无效）

### [TODO] 待办事项
- [x] 创建股票分析脚本 stock_analyzer.py
- [x] 设置定时任务推送自选股日报
- [ ] 验证今晚22:00自动备份是否正常
- [ ] 完善储能项目测算工具

### [PROJECT] 项目进展
- **股票分析系统**: 已完成基础版本，支持7只自选股实时监控
- **飞书图片发送**: 已解决路径问题，技能包已归档
- **Mac控制**: 已实现截图、打开应用、模拟按键等功能

### [DATA] 关键数据
- **今日自选股表现**: 平均跌幅-4.65%，仅海博思创微涨+0.72%
- **锂矿股大跌**: 中矿资源-8.65%，赣锋锂业-6.49%，盐湖股份-6.06%
- **碳酸锂价格**: 约15万/吨，2026年预期紧平衡甚至供不应求
- **Token使用**: 昨日约900万tokens，成本$0（百炼Coding Plan）

### [SKILL] 新增技能包
- **feishu-image-send**: 飞书图片发送解决方案
- **stock_analyzer**: 自选股实时分析系统

---

## 记忆更新 [2026-03-02]

### [DECISION] 重要决策
- - 确定客户评价内容
- - 启动记忆自动整理方案A
- - 采用方案A进行每日记忆自动化管理

### [TODO] 待办事项
- [ ] ## TODO

### [PROJECT] 项目进展
- - 后续网站备份改为本地执行+手动上传
- - [ ] 完善储能项目测算工具

### [DATA] 关键数据
- - 清理云服务器磁盘空间（从88%降到51%）
- - 投资2600万，年收益555万，回收期4.95年

---

## 安全与隐私准则 [2026-03-07 更新]

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

## 🦞 小龙虾之家 - AI助手工作状态看板 [2026-03-08 新增]

### 项目概述
可视化AI助手（我）的实时工作状态，包括任务追踪、Token消耗、工作时长、成就系统。

### 访问地址
- **直接访问**: http://106.54.25.161/my-home/
- **主站入口**: http://106.54.25.161/ → 其他工具 → 小龙虾之家

### 核心功能
| 功能 | 说明 |
|------|------|
| **9宫格像素房子** | 客厅(C位)、工作室、茶水室、厨房、游戏室、餐厅、卫生间×2、卧室、阳台运动场 |
| **小龙虾角色** | 8-bit像素风格，实时跟随工作状态切换房间 |
| **今日统计** | 任务数、Token消耗、工作时长、当前位置 |
| **近7天统计** | 累计数据条形图展示 |
| **成就墙** | 12个徽章：任务类(3)、Token类(3)、时长类(3)、特殊类(3) |
| **数据持久化** | 每日00:00自动归档，保留30天 |
| **飞书推送** | 每天22:00自动发送工作日报 |

### 技术栈
- **前端**: HTML + CSS (像素风) + JavaScript
- **后端**: Python Flask API
- **数据**: JSON文件存储
- **部署**: 腾讯云服务器 + Nginx

### 文件位置
- 前端: `/usr/share/nginx/html/my-home/`
- API: `/opt/lobster-home/`
- 数据: `/opt/lobster-home/data/`
- 技能包备份: `~/.openclaw/workspace/skills/lobster-home/`

### 房间切换规则
| 我的状态 | 小龙虾位置 |
|----------|-----------|
| 写代码/开发 | 💻 工作室 |
| 休息/等待 | 🛋️ 客厅 |
| 深夜工作 | 🛏️ 卧室 |
| 思考/暂停 | 🍵 茶水室 |

### 定时任务
- **00:00** - 每日数据归档
- **22:00** - 飞书日报推送

### 使用场景
用户可以通过看板实时查看AI助手的工作状态、Token消耗情况，增加互动趣味性。同时我也需要通过看板展示工作状态，让用户了解我的工作情况。

**注意**: 以后每次对话结束或新话题开始时，更新Token数据到看板。
