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

## 🚨 会话恢复机制（新！）

### 问题场景
- AI 意外卡死，只能打 `/new` 强制新建
- 新会话后完全失忆，不知道之前聊了什么

### 解决方案

**1. 自动保存**
- 每次重要操作后自动保存会话快照
- 快照位置: `memory/snapshots/current_session.json`

**2. 急救口令**
新会话时说以下口令之一，我会自动恢复上下文：

| 口令 | 恢复内容 |
|------|----------|
| `继续之前的工作` | 通用恢复 |
| `继续修复定时任务` | 恢复定时任务相关内容 |
| `继续模型测试` | 恢复模型切换测试内容 |
| `我是雪子` | 恢复个人上下文 |

**3. 手动恢复**
```bash
# 查看最新快照
python3 ~/.openclaw/workspace/scripts/session-snapshot.py card

# 加载快照
python3 ~/.openclaw/workspace/scripts/session-snapshot.py load
```

### 当前会话状态
**最后更新**: 2026-03-06 12:38  
**当前任务**: 修复定时任务通知 + 模型切换上下文测试  
**急救口令**: `继续修复定时任务` 或 `继续模型测试`  
**模型**: kimi-coding/k2p5

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

**主题**: 锂矿+面板，新能源产业链布局

---

## OpenClaw 系统配置（关键修复文档）

> **来源**: `/Volumes/cu/ocu/OpenClaw配置指导.md`  
> **用途**: 系统故障修复和模型配置参考

### 当前模型配置
| 模型 | Provider | 特点 |
|------|----------|------|
| MiniMax-M2.5 | openai | 主模型，256k上下文 |
| qwen3.5-plus | bailian | 备用，262k上下文 |
| kimi-k2.5 | bailian | 支持识图，256k上下文 |

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

### 模型切换速查
```bash
# 切换到 MiniMax
openclaw config set agents.defaults.model.primary "openai/MiniMax-M2.5"
openclaw gateway restart

# 切换到 qwen3.5-plus
openclaw config set agents.defaults.model.primary "bailian/qwen3.5-plus"
openclaw gateway restart

# 切换回 kimi-k2.5（支持识图）
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

