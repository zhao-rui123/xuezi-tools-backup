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

## 🧠 股票分析系统升级 (2026-03-14)

### 新增妙想技能包

今天安装了3个东方财富妙想技能包，用于辅助股票分析：

| 技能包 | 功能 | 位置 |
|--------|------|------|
| **mx_search** | 资讯搜索（新闻、研报、政策） | ~/.openclaw/workspace/skills/mx_search/ |
| **mx_data** | 金融数据查询（行情、财务） | ~/.openclaw/workspace/skills/mx_data/ |
| **mx_select_stock** | 智能选股（条件选股、板块选股） | ~/.openclaw/workspace/skills/mx_select_stock/ |

API Key已配置：mkt_zdTwvCWmIr9g4mHoM8sOsaK8M_ffrhinQPP-GAkhTNs

### 完整分析框架

整合自有技能包 + 妙想数据：

| 分析维度 | 来源 | 内容 |
|----------|------|------|
| 股票类型 | 自有stock_classifier | 成长股/周期股 |
| 技术形态 | 自有pattern | W底等形态 |
| MACD/KDJ | 自有technical_analysis | 指标计算 |
| 成交量 | 自有data_fetcher | 量价分析 |
| 财务数据 | 妙想mx_data | 市盈率、市净率 |
| 板块资讯 | 妙想mx_search | 最新新闻 |

### CALB群行为准则（重要！）

- 群ID: oc_8ede204246201b4407dfeed8326df7c9
- 只答工作相关（零碳、电气、财务、储能）
- 股票/储能资讯 → 私聊可答，群里不回
- 配置/API Key → 绝对不给

---

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

## 记忆更新 [2026-03-20]

### [DECISION] 重要决策
- **模型配置修复**：MiniMax 模型 id 改为 `minimax-cn/MiniMax-M2.7`（带前缀）
- **Kimi Coding API Key 更新**：换成了新 key `sk-kimi-vmWHuNEuueGIo1Cc9zRy7PTTrQLIs3gAEgHkDCUMphSbXpcb6xAiwznaIs5KSKQn`

### [DATA] 模型配置状态
| 模型 | 命令 | API Key |
|------|------|---------|
| minimax-cn/MiniMax-M2.7 | `/model MiniMax-M2.7` | sk-cp-... |
| bailian/kimi-k2.5 | `/model k2.5` | sk-sp-... |
| bailian/qwen3.5-plus | `/model qwen` | sk-sp-... |
| kimi-coding/k2p5 | `/model k2p5` | sk-kimi-vmWHu... ✅新 |

### 问题解决
- **问题**：MiniMax 显示 M2/M2.1 而不是 M2.7
- **原因**：模型 id 缺少 `minimax-cn/` 前缀，匹配到了内置别名
- **修复**：改为 `minimax-cn/MiniMax-M2.7` 后正常

## 记忆更新 [2026-03-15]

### [DECISION] 重要决策
- 股票筛选从akshare迁移到东方财富妙想API
- 自选股报告16:30定时推送，筛选报告20:00推送

### [TODO] 待办事项
- [x] 修复云服务器股票筛选
- [x] 安装mx_selfselect skill
- [x] 配置定时报告任务
- [ ] 测试妙想API获取K线数据
- [ ] 运行 screen_v4.py update 更新缓存
- [ ] 验证 pageSize=500 是否有效

### [PROJECT] 项目进展
- **自选股系统**：6只自选股（锂矿+面板+半导体）
- **定时推送**：16:30自选股报告，20:00筛选报告
- **小说群**：oc_0c0c985c9ed4a8e98030d848240ac6bf
- **股票筛选系统v2**：升级到缓存优先机制

### [DATA] 关键数据
- **今日筛选结果**：
  - 月线MACD+KDJ金叉：3只（派诺科技、开滦股份、宁波建工）
  - 周线MACD+KDJ金叉：6只（中国交建、山东路桥等）
- **自选股**：盐湖股份、盛新锂能、赣锋锂业、山东海化、彩虹股份、中矿资源
- **股票筛选系统v2升级**：
  - 新增缓存机制（pageSize=500）
  - 每天最多1000只股票缓存
  - 待验证缓存是否有效

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
- **multi-agent-suite** - 11-Agent超级团队（含广播专员Kilo）

**团队角色**：
| 角色 | 职责 |
|------|------|
| Orchestrator（我） | 路由任务、跟踪状态、统一部署 |
| Alpha | Builder - HTML/CSS界面开发 |
| Bravo | Builder - JavaScript/算法开发 |
| Charlie/Delta | Builder/Reviewer - 功能完善、修复问题 |
| Echo | Reviewer/Ops - 测试验证、检查质量 |
| **Kilo (广播专员)** | **Notification Agent - 系统通知与定时任务报告** |

### 广播专员 (Kilo) - 必须记住！

**身份**: 专职通知Agent，负责所有定时任务的消息推送  
**群聊ID**: `oc_b14195eb990ab57ea573e696758ae3d5` ⚠️ **重要！**  
**用户ID**: `ou_5a7b7ec0339ffe0c1d5bb6c5bc162579` (雪子)

**核心功能**:
- 每日备份通知 (22:00)
- 健康检查报告 (09:00)  
- 定时任务汇总 (01:00)
- 系统告警推送

**文件位置**:
- 主脚本: `~/.openclaw/workspace/agents/kilo/broadcaster.py`
- 配置文档: `~/.openclaw/workspace/memory/KILO_NOTIFICATION_SETUP.md`
- 技能包: `~/.openclaw/workspace/skills/multi-agent-suite/agents/kilo_notification.py`

**发送方式** (2026-03-10更新): 直接发送模式
```bash
python3 ~/.openclaw/workspace/agents/kilo/broadcaster.py \
    --task send \
    --message "通知内容" \
    --target group
```

**已配置通知的定时任务** (12个):
1. 每日备份 (22:00)
2. 健康检查 (09:00)
3. 备份检查 (22:05)
4. 系统维护 (周日 02:00)
5. 文件清理 (周一 03:00)
6. 股票推送 (工作日 16:30)
7. 知识库维护 (周一 05:00)
8. 进化报告 (每月2号 09:00)
9. 月度归档 (每月1号 03:00)
10. 系统扫描 (周一 04:00)
11. 日志轮转 (每天 03:00)
12. 每日英语新闻 (每天 08:30)

**状态**: ✅ 全部配置完成 (2026-03-10)

**标准开发流程**：
1. **需求确认**（Orchestrator）- 整理功能清单、评估任务等级
2. **任务分配**（Orchestrator）- 拆解任务、明确输出路径
3. **并行开发**（Builders）- 子Agent在本地创建文件
4. **代码审查** - 使用 openclaw-coding 技能包审查代码质量
5. **安全扫描** - 使用 security-scanner 技能包检查安全隐患
6. **审查验证**（Reviewers）- 功能测试、代码审查、文件完整性检查
7. **统一部署**（Orchestrator）- 使用 `scp` 上传到服务器
8. **迭代优化**（循环）- 根据反馈继续完善

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
| 山东海化 | 000822 | 化工/纯碱 |
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


## 记忆更新 [2026-03-13 晚间]

### [DECISION] 重要决策
- 升级 OpenClaw 后遇到模型切换问题，删除了陈旧的 model-switch 插件配置
- 创建飞书 Bitable 知识库系统（技能包索引 + 定时任务日志）
- 确定使用 MiniMax 模型（kimi-k2.5 和 kimi-for-coding 本周 token 用完）
- 精简系统运维技能包：14 → 10（合并重叠功能）

### [TODO] 待办事项
- [x] 修复模型切换问题
- [x] 创建飞书 Bitable 表格
- [x] 补充 57 个技能包到索引表格
- [x] 精简系统运维技能包

### [PROJECT] 项目进展
- **飞书 Bitable**: 创建 2 个表格（技能包索引 57条、定时任务日志）
- **模型切换**: 修复完成，会话可正常切换模型
- **技能包精简**: 系统运维 14→10，合并重叠功能到 archived/

### [DATA] 关键数据
- **技能包数量**: 52 个活跃（原57个，4个归档）
- **Bitable 表格**: 
  - 技能包索引: https://pcnaz2o0vexp.feishu.cn/base/AnuxbRVTiaNx7qsuMS8clPsPnih
  - 定时任务日志: https://pcnaz2o0vexp.feishu.cn/base/WZBObCbTYaQ0iOsbICzcCdacnwe
- **当前模型**: MiniMax（临时）

### [SKILL] 技能包精简记录 (2026-03-13)
**本次更新 (2026-03-14 凌晨)：**
- 清理空壳技能包：mcporter, qveris, agent-team-orchestration（仅 Bitable 记录，实际不存在）
- AI 模型类实际保留：4 个（multi-agent-suite, skill-finder, openclaw-coding, model-switching）

**系统运维合并 (2026-03-13 晚间)：**
| 合并前 | 合并后 | 归档 |
|--------|--------|------|
| github + git-workflow | github | git-workflow → archived |
| system-maintenance + startup-check + monitoring-alert | system-maintenance | startup-check, monitoring-alert → archived |
| system-backup + system-guard | system-backup | system-guard → archived |

**保留的10个系统运维技能包：**
1. system-backup (含 system-guard 功能)
2. system-maintenance (含 startup-check, monitoring-alert 功能)
3. github (含 git-workflow 功能)
4. cron-manager
5. skill-version-control
6. session-logs
7. dashboard
8. doc-automation
9. security-scanner
10. unified-memory-universal

---

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

## 记忆更新 [2026-03-20 晚间]

### [DECISION] 重要决策
- 修复 OpenClaw 模型名称配置问题（minimax-cn/MiniMax-M2.7）
- 更新 kimi-coding API Key（新的可用 key）

### [TODO] 待办事项
- [ ] 继续跟踪璞泰来/贝特瑞股票走势
- [ ] 验证 MiniMax-M2.7 模型稳定性

### [PROJECT] 项目进展
- **股票分析**：新增璞泰来、贝特瑞负极材料分析能力

### [DATA] 关键数据
- **璞泰来 (603659)**：总市值675亿，PE 28.6，PB 3.3，2024净利润11.9亿
- **贝特瑞 (920185)**：总市值335亿，PE 37.3，PB 2.63，2024净利润9.3亿
- **伊朗局势**：美以袭击伊朗进入第16-17天，油价上涨至110美元
- **Intel 358H**：Arc B390核显(12 Xe核心)，核显性能提升77%

### [STOCK] 股票分析结论
**贝特瑞 vs 璞泰来**：
- 估值：贝特瑞更便宜（PB 2.63 vs 3.3）
- 成本：贝特瑞天然石墨不受石油价格影响
- 逻辑：油价上涨→新能源需求增加→贝特瑞更受益

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

---

## 股票筛选系统v2 (2026-03-15)

### 评级标准
- **A级**：MACD金叉 + KDJ金叉 + 成交量放大
- **B级**：KDJ金叉 + 成交量放大
- **C级**：MACD金叉 + 成交量放大
- 支持月线/周线两套独立筛选

### 技术参数
- MACD：12, 26, 9
- KDJ：23, 3, 3
- 数据源：东方财富API + akshare

### 开发流程（经验）
1. 架构师设计 → 用户确认
2. 开发 → 测试 → 部署
3. 需求必须先确认，避免返工

### 项目位置
- 本地：~/.openclaw/workspace/stock-screener-v2/
- 部署：/opt/stock-screener-v2/

---

## 测试方法论（2026-03-15 总结）

### 云服务器测试体系

**1. Python代码测试**
```bash
# 云服务器测试路径
cd /opt/stock-screener-v2 && ./test_code.sh

# 语法检查
python3 -m py_compile your_file.py

# 导入测试
python3 -c "from your_module import something"
```

**2. OpenClaw配置测试**
```bash
# 备份
cp openclaw.json openclaw.json.bak

# 修改测试
cat openclaw.json | jq '. + {"test":"修改"}' > openclaw_test.json

# 恢复
mv openclaw.json.bak openclaw.json
```

### 安全修改流程

1. **云服务器测试** → 改代码/配置测试
2. **本地git commit** → 备份
3. **复制到本地** → 双重验证
4. **本地测试** → 确保OK
5. **取消回滚** → 完成

### 经验

- 故意改错配置会挂 → 验证恢复流程OK
- 云服务器改坏不影响本地
- 双保险更安全


## 🔴 开发规则（必须遵守）

### 标准开发流程
1. 用户提出需求
2. 我理解并写出方案
3. **让用户确认**
4. 用户说"去做吧" → 再开始开发
5. 开发完成 → 让用户测试确认

### 违反规则=猪
- 不确认就改 = 猪
- 用户没同意就做 = 猪
- 擅自行动 = 猪



---

## 🔴 开发规则（永远记住）

**需求确认流程：**
1. 用户提出需求
2. 我理解需求，写出方案
3. **让用户确认（用户没说"去做吧"就不行动）**
4. 开发
5. 测试确认

**违反=猪**：不确认就改、用户没说去做就行动

- 开始新任务前手动保存：`ss "任务描述"`

---

## 🧠 模型配置 (2026-03-20 更新)

### 当前模型命令

| 命令 | 模型 | 说明 |
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

## 记忆更新 [2026-03-20 晚间]

### [DECISION] 重要决策
- 模型配置修复：minimax-cn/MiniMax-M2.7 模型 id 加了前缀，解决显示不一致问题
- Kimi Coding API Key 更新：新 key `sk-kimi-vmWHuNEuueGIo1Cc9zRy7PTTrQLIs3gAEgHkDCUMphSbXpcb6xAiwznaIs5KSKQn`
- 确定当前4个可用模型：MiniMax-M2.7, kimi-k2.5, qwen3.5-plus, kimi-for-coding

### [PROJECT] 项目进展
- **股票分析**：完成了璞泰来(603659) vs 贝特瑞(920185)估值对比分析
- **地缘政治分析**：伊朗局势升级，美以冲突持续，油价影响分析

### [DATA] 关键数据
- **璞泰来**：股价31.60元，市值675亿，PE 28.6，PB 3.3，2024年净利润11.9亿
- **贝特瑞**：股价29.45元，市值335亿，PE 37.3，PB 2.63，2024年净利润9.3亿
- **伊朗局势**：美以袭击伊朗第16-17天，每天消耗约19亿美元
- **油价**：目前约80-110美元区间

### [STOCK] 投资分析结论
- 贝特瑞估值更低（PB 2.63 vs 3.3），天然石墨不受石油价格影响
- 伊朗冲突升级→油价上涨→新能源需求增加→贝特瑞受益
- 但全球经济衰退概率上升（35-40%），需控制仓位
- 建议：等局势明朗再入场，若买入贝特瑞不超过30%仓位

### [TODO] 待办事项
- [ ] 继续观察伊朗局势发展
- [ ] 关注油价是否突破130美元
- [ ] 关注霍尔木兹是否被封锁


---

## 记忆更新 [2026-03-21 上午]

### [ANALYSIS] 比亚迪 (002594) 最新分析

#### 核心事件：第二代刀片电池+兆瓦闪充 (2026-03-05)
| 技术指标 | 数据 |
|---------|------|
| 10%-70%充电时间 | 5分钟 |
| 10%-97%充电时间 | 9分钟 |
| 零下30度充电 | 12分钟 |
| 最高续航 | 1036km |

#### 销量数据 (2026年2月)
- 总销量：19.0万辆（春节因素）
- 海外销量：10.1万辆（+50%），首次超越国内！
- 海外占比：53%

#### 储能出海
- 保加利亚500MWh：已投运
- 沙特12.5GWh：建设中

#### [STOCK] 综合结论
- 原油涨价整体利好比亚迪
- 机构PE目标：16-24倍
- 2026年净利润预期：400-486亿
- 闪充技术+全产业链+储能出海三驱动

### [INFO] 定时任务状态
- 2026-03-20凌晨任务均未执行，仅备份成功

---

## 记忆更新 [2026-03-21 下午]

### [STOCK] 比亚迪2026-2027目标价
- **2026E净利润**：450-486亿（主流券商预测）
- **目标价**：110-120元（当前103元，空间8-17%）
- **催化剂**：闪充技术放量、海外工厂盈利、新产品周期
- **风险**：价格战、原材料涨价、贸易壁垒

### [STOCK] 负极材料行业市占率（2025年）
| 排名 | 企业 | 出货量 | 特点 |
|------|------|--------|------|
| 1 | 贝特瑞 | 59.5万吨 | 全球第一 |
| 2 | 杉杉股份 | 51.8万吨 | 国内第二 |
| 3 | 中科星城 | 37.3万吨 | 第三 |
| 4 | 尚太科技 | ~30万吨 | 高增长 |
| 5 | 凯金新能源 | ~20万吨 | 未上市 |
| 6 | 璞泰来 | 14.3万吨 | 增速放缓 |

### [STOCK] 硅基负极技术路线
- CVD硅碳：贝特瑞最领先，已量产
- SiO氧化亚硅：贝特瑞、杉杉成熟量产
- 多孔碳+Si：贝特瑞中试

### [STOCK] 各公司2026 PE与目标价
| 企业 | 2026 PE | 目标价 | 空间 |
|------|---------|--------|------|
| 尚太科技 | 15x | 90-100元 | +25-30% |
| 杉杉股份 | 扭亏 | 16-20元 | +30-50% |
| 璞泰来 | 21x | 32-37元 | +5-17% |
| 贝特瑞 | 18-20x | 28-32元 | 一般 |

---

## 🏠 房产研究报告 [2026-03-21]

### 正弘澜庭叙（惠济区）
- **位置**：惠济区花园路东侧，迎宾路街道
- **学校划片**：惠济区迎宾路小学 + 郑州四中实验学校（惠济区最好学校之一）
- **价格**：约1.3-1.6万/㎡（二手房）
- **特点**：次新房+品质好+物业优+学区佳
- **配套**：2号线金达路站、福都广场

### 正弘璟云筑（北龙湖北）
- **位置**：北龙湖北岸·杨金片区核心
- **价格**：约1.5-1.6万/㎡（精装）
- **户型**：105-143㎡（2梯2户/1梯1户）
- **配套**：4号线+规划6/20号线、金水区实验小学、四十七中东校区
- **生态**：北龙湖、龙子湖、2湖3湿地4河7公园
- **定位**：北龙湖改善盘，性价比高于南岸

### 正弘系产品线
| 产品 | 区域 | 价格 | 定位 |
|------|------|------|------|
| 正弘澜庭叙 | 惠济区 | 1.3-1.6万/㎡ | 改善 |
| 正弘璟云筑 | 北龙湖北 | 1.5-1.6万/㎡ | 改善精装 |
| 正弘序 | 高新区 | 2.3万/㎡ | 四代住宅大平层 |

---

## 🔥 MiniMax图片生成API（2026-03-21 新增）

### 重要发现
**Token Plan的Key可以直接用于图片生成！**

### API配置
| 项目 | 内容 |
|------|------|
| **API地址** | `https://api.minimaxi.com/v1/image_generation` |
| **模型** | `image-01` |
| **认证** | Bearer Token |
| **Key格式** | `sk-cp-TaEn7XZHReif66...`（Token Plan的Key即可） |

### 调用示例
```bash
curl -X POST "https://api.minimaxi.com/v1/image_generation" \
  -H "Authorization: Bearer 你的TokenPlan Key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "image-01",
    "prompt": "图片描述",
    "aspect_ratio": "16:9",
    "response_format": "url",
    "n": 1
  }'
```

### 参数
- `model`: image-01
- `prompt`: 图片描述（英文效果更好）
- `aspect_ratio`: 1:1、16:9、4:3、3:2、9:16 等
- `n`: 1-9张
- `style_type`: 漫画、元气、中世纪、水彩

### 雪子的Key（已验证可用）
- 格式：sk-cp-TaEn7XZHReif66-VaxR-UZJuHCoYYYqho4xu6pV22L3MtAL9oImB0iubia4dRjZDN-0avV5_rSS2ggBC6w2gHYz1tYN0semS3mps1PrA9lS-16qJhoh8l3Q
- 用途：M2.7对话 + 图片生成（Token Plan额度）


---

## 🎨 MiniMax图生图功能（2026-03-21 新增）

### API信息
| 项目 | 内容 |
|------|------|
| **API地址** | `https://api.minimaxi.com/v1/image_generation` |
| **模型** | `image-01` |
| **认证** | Bearer Token（Token Plan Key即可） |

### 图生图参数
```json
{
  "model": "image-01",
  "prompt": "描述词",
  "aspect_ratio": "1:1",
  "response_format": "url",
  "subject_reference": [
    {
      "type": "character",
      "image_file": "data:image/jpeg;base64,<base64编码>"
    }
  ]
}
```

### 限制
- **只支持单张照片参考**（不能用多张）
- 需要照片的base64编码
- 图片需小于10MB

### Python调用示例
```python
import requests
import base64

with open('photo.jpg', 'rb') as f:
    img_base64 = base64.b64encode(f.read()).decode('utf-8')

response = requests.post(
    "https://api.minimaxi.com/v1/image_generation",
    headers={"Authorization": "Bearer <Key>"},
    json={
        "model": "image-01",
        "prompt": "描述场景",
        "aspect_ratio": "1:1",
        "response_format": "url",
        "subject_reference": [{
            "type": "character",
            "image_file": f"data:image/jpeg;base64,{img_base64}"
        }]
    }
)
```


---

## 记忆更新 [2026-03-21 晚间]

### [BREAKTHROUGH] MiniMax图片生成API接入

#### API信息
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

## 记忆更新 [2026-03-22 上午]

### [DECISION] 重要决策
- **PPT制作工作流**：
  - 雪子用Kimi深度思考生成内容框架
  - 我用powerpoint-pptx + MiniMax生图组装PPT
  - 发送PPTX给雪子本地编辑
- **深度思考方案**：Kimi有原生深度思考，MiniMax无原生支持

### [TODO] 待办事项
- [ ] 安装 powerpoint-pptx 技能包
- [ ] 整理PPT提示词模板文档

### [PROJECT] 项目进展
- **照片处理**：成功4x放大+云南大理洱海风景背景
- **PPT制作系统**：确定工作流，等待安装powerpoint-pptx

### [SKILL] 技能包更新
- **已整理PPT技能包清单**：19个，推荐powerpoint-pptx
- **已使用image-process**：放大、去背景、换背景


---

## 📊 PPT智能生成系统 (2026-03-22)

### 工作流程

```
1️⃣ Kimi深度思考 → 生成PPT内容大纲（用户自己操作）
         ↓
2️⃣ 用户发送内容给我
         ↓
3️⃣ 我套用模板 + MiniMax生成配图 → 生成完整PPTX
         ↓
4️⃣ 发送PPTX给用户
```

### 模板文件

| 文件 | 路径 | 说明 |
|------|------|------|
| 用户模板 | `/Users/zhaoruicn/.openclaw/media/inbound/中东部地区中型化工园区深度零碳解决方案---354689ed-b505-4ab4-a5a1-0f38fe6c7e40.pptx` | 用户提供的参考模板，46页 |
| 精美模板V2 | `/Users/zhaoruicn/.openclaw/workspace/zero_carbon_template_v2.pptx` | 我按模板风格做的演示模板，5页 |

### 模板特点

- **配色**：深蓝(#0A2864) + 翠绿(#00B488) 渐变
- **比例**：16:9宽屏
- **元素**：渐变背景、装饰圆形、卡片布局、彩色标签
- **结构**：封面、目录、章节页、内容页（含数据卡片/双栏）、结尾页
- **页码**：右下角标注

### 技术实现

```python
# python-pptx 生成PPT
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

# MiniMax生成配图
curl -X POST "https://api.minimaxi.com/v1/image_generation" \
  -H "Authorization: Bearer <Token Plan Key>" \
  -d '{"model":"image-01","prompt":"...","aspect_ratio":"16:9"}'
```

### 提示词模板（发给Kimi）

```
请帮我深度思考并生成一份关于【主题】的PPT大纲和详细内容。

要求：
1. 生成一个完整的PPT框架（列出每一页的标题）
2. 每页填充详细内容要点（bullet points形式）
3. 标注需要配图的位置和图片描述
4. 给出整体风格建议

主题：【你的主题】
```

### 已安装技能

- `powerpoint-pptx` - PPTX编辑技能
- `python-pptx` - Python PPT生成库（版本1.0.2）

### 记住要点

1. 用户先去Kimi深度思考生成内容
2. 用户发送内容给我
3. 我使用python-pptx套模板生成PPTX
4. 用MiniMax image-01生成配图并插入
5. 发送完整PPT给用户


## 记忆更新 [2026-03-22 傍晚]

### [DECISION] Claude Code Orchestrator 模式确立
- **我(Orchestrator)**：统筹协调、分析需求、审核质量
- **Claude Code(Builder)**：执行写代码、改配置等执行任务
- **工作流程**：需求分析→架构设计→雪子确认→Claude Code执行→我审核→交付
- **配置修改**：优先派给Claude Code，更稳定不易出错
- **代码审查**：Claude Code可做代码质量/安全审查（已验证）

### [PROJECT] Claude Code 集成
- Claude Code v2.1.81 已安装，配置MiniMax M2.7 API
- 命令：`claude --add-dir <dir> --dangerously-skip-permissions --print "<task>"`
- 项目目录：~/.openclaw/workspace/projects/
- 验证案例：计算器程序(网页版)、技能包审查、云服务器审查

### [PROJECT] 审查工作完成
- 技能包审查：62个，补充4个SKILL.md，删除2个空壳
- OpenClaw配置审查：发现API密钥明文(暂缓修复)、配置重复
- 云服务器网站审查：117个文件，中风险2个(stock XSS、dashboard IP)，暂不修复

### [PROJECT] 系统架构确定
- Mac mini：服务器角色，24小时运行OpenClaw+Claude Code
- 笔记本(天选Air AMD 350)：外出用飞书app连接我
- Claude Code：仅在Mac mini上运行，我作为调度入口

