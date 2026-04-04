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

## 🚀 雪子知识库 (XueziKB) - 项目已终止 [2026-04-04]

项目于2026-04-04终止，原因：需求不清晰，执行效果差。

### 备份信息
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

---

## 问题解决
- **问题**：MiniMax 显示 M2/M2.1 而不是 M2.7
- **原因**：模型 id 缺少 `minimax-cn/` 前缀，匹配到了内置别名
- **修复**：改为 `minimax-cn/MiniMax-M2.7` 后正常

## [PROJECT] 项目进展
- **股票分析**：新增璞泰来、贝特瑞负极材料分析能力

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

## 核心事件：第二代刀片电池+兆瓦闪充 (2026-03-05)
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

## API信息
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

## [PROJECT] 项目进展
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

## [DECISION] 微信插件放弃
- 微信插件连接成功但延迟严重
- 决定放弃微信通道，继续只用飞书
- 插件已删除（extensions目录已移除）

### [FIX] 飞书通知修复
- 问题：多个脚本发飞书消息时缺少 `--channel feishu`
- 修复脚本：stock_report.py, tushare_screener.py, stock_eastmoney_push.py, stock_daily_push_v2/v3.py, stock_feishu_push_fusion.py, broadcaster.py
- 所有发飞书消息的脚本现在都显式指定 `--channel feishu`

---

## MiniMax官方Skills仓库 (2026-03-23 新增)

**来源**: https://github.com/MiniMax-AI/skills/
**克隆位置**: `~/.openclaw/workspace/skills/minimax-skills/`
**链接位置**: `~/.openclaw/workspace/skills/`

### 已安装的10个Skill

| Skill | 功能 | API需求 |
|-------|------|--------|
| minimax-pdf | PDF生成/填写/重排版（设计系统、色板、模板） | 部分需要 |
| minimax-xlsx | Excel处理（XML模板，零损坏编辑，财务格式化） | 不需要 |
| minimax-docx | Word处理（OpenXML SDK、C#） | 不需要 |
| pptx-generator | PPT生成/编辑（PptxGenJS、设计系统） | 部分需要 |
| frontend-dev | React/Next.js + Framer Motion/GSAP/Three.js | 需要 |
| fullstack-dev | 全栈架构设计（12-Factor、Clean Architecture） | 不需要 |
| android-native-dev | Android原生开发（Kotlin/Jetpack Compose） | 不需要 |
| ios-application-dev | iOS开发（UIKit/SwiftUI） | 不需要 |
| shader-dev | GLSL着色器（Ray Marching/Fluid/Particle） | 不需要 |
| gif-sticker-maker | GIF制作（MiniMax图生视频） | 需要 |

### 关键使用流程

**1. minimax-pdf（CREATE/REFORMAT/FILL三模式）**
```bash
bash scripts/make.sh run --title "标题" --type proposal --accent "#2D5F8A" --content content.json --out report.pdf
```

**2. minimax-xlsx（READ/CREATE/EDIT/FIX/VALIDATE）**
- READ: `xlsx_reader.py` + pandas
- CREATE: XML模板 → 编辑XML → `xlsx_pack.py`
- EDIT: XML unpack → edit → pack（绝不破坏原文件）
- 核心规则：只修改指定单元格，其他不动

**3. pptx-generator**
- 尺寸: 10" x 5.625" (16:9)
- 中文字体: Microsoft YaHei
- 英文字体: Arial
- 创建: PptxGenJS
- 编辑: XML操作

**4. frontend-dev（5步工作流）**
1. 设计工程（UI设计）
2. 动效系统（Framer Motion/GSAP）
3. AI媒体生成（图/视频/音频）
4. 说服文案（AIDA框架）
5. 生成艺术（p5.js/Three.js）

**5. fullstack-dev（6步开发流程）**
1. 需求收集（Stack/DB/Auth/Real-time）
2. 架构决策
3. 后端开发
4. 前端开发
5. 集成测试
6. 部署上线

### Claude Code使用方式
Claude Code不能直接触发skill，但可以**读取SKILL.md作为指导**，遵循skill里的工作流程和最佳实践。

### 已删除重复Skill
- office-pro（被minimax-pdf/xlsx/docx替代）
- powerpoint-pptx（被pptx-generator替代）

---

## [PROJECT] Claude Code 使用
- 雪子在笔记本上通过 Trae 安装了 Claude Code
- 雪子自己先用懂，再教我怎么更好地调用
- 结论：OpenClaw(图形中枢) + Claude Code(命令行代码) 组合够用，不需要 Trae

## 网站备份位置 (2026-03-25 新增)

### 服务器备份
- **路径**: `/usr/share/nginx/html/downloads/website_backup_20260325_174925.tar.gz`
- **下载**: http://106.54.25.161/downloads/website_backup_20260325_174925.tar.gz
- **大小**: 376 MB
- **内容**: 包含主页(index.html)、全税务版测算(calculation.html)、储能收资清单等全部模块

### 恢复方法
```bash
# 1. 下载备份
sshpass -p 'Zr123456' scp root@106.54.25.161:/usr/share/nginx/html/downloads/website_backup_20260325_174925.tar.gz /tmp/

# 2. 解压覆盖
tar -xzvf website_backup_20260325_174925.tar.gz -C /usr/share/nginx/html/
```

### GitHub备份
- **仓库**: https://github.com/zhao-rui123/xuezi-tools-backup
- **原始index.html**: https://raw.githubusercontent.com/zhao-rui123/xuezi-tools-backup/main/index.html

## 深度思考实现方式 [2026-03-26]

### Claude Code 深度思考方法
Claude Code 有独立的深度思考机制，不依赖模型原生 CoT（思维链）。

**结论：MiniMax M2.7 + Claude Code = 可实现深度思考**

之前错误认为 MiniMax M2.7 没有深度思考就做不了复杂推理，这是错的。

Claude Code 内部有 `--thinking` 参数会自动启用思考模式分析问题，不管接什么模型。

### 组合方式
| 组件 | 作用 |
|------|------|
| MiniMax M2.7 | 默认模型，日常对话、调度 |
| Claude Code | 复杂推理、代码任务（自带深度思考） |
| kimi-coding/k2p5 | 代码辅助（已配置新key） |

---

## [DATA] 模式二修正计算（含税）
**1MW+3MWh，衰减1.5%，增值税13%，所得税25%**

| 含税储能卖电价 | IRR |
|---------------|-----|
| 0.65元 | 2.29% |
| 1.00元 | 7.63% |
| IRR=10%门槛 | ≥ 1.1744元（基本不可能）|

**纯光伏直售IRR（含税）**：
| 电价 | IRR |
|------|-----|
| 0.40元 | 9.31% |
| 0.50元 | 13.01% |

## [LESSON] 重要教训：开发流程铁律
- **复杂项目**必须走完整流程：Opus架构 → MiniMax开发 → Opus验收
- 不能图快省掉Opus审核环节
- 今天股票监控项目没走完整流程，虽然结果OK但不规范
- 以后记住：流程规范比省时更重要

---

## [FIX] 备份脚本U盘唤醒修复
- 问题：22:00 cron时U盘待机，写入报"Operation not permitted"
- 修复：backup-runner.sh 添加唤醒步骤
- 提交：a02b2d4

### [LESSON] 开发流程铁律
- 股票监控项目偷懒没用Opus做架构审核，虽然结果OK但不规范
- **规则**：复杂项目必须走完整流程：Opus架构 → MiniMax开发 → Opus验收
- 已写入SOUL.md、AGENTS.md、MEMORY.md

## ⚠️ 雪子知识库开发铁律（2026-04-03 强调）

### 必须严格遵守的开发流程
```
雪子需求
    ↓
Opus架构设计 → 雪子确认
    ↓
MiniMax执行开发
    ↓
Opus验收审查 → 雪子确认
    ↓
部署上线
```

### 7个专业Agent组合方式
- sisyphus：任务分解
- oracle：战略咨询、架构决策
- librarian：文档搜索、GitHub研究
- explore：代码库探索
- frontend-ui-ux-engineer：UI/UX设计
- document-writer：技术文档写作
- multimodal-looker：图片/PDF/视觉分析

### 绝对禁止的行为
1. 不确认方向就执行
2. 跳过Opus审核环节
3. 自己判断架构/技术方案
4. 觉得流程麻烦想走捷径

### 违反教训
- 今天：网页版完全不需要，我做了
- 股票分析：跳过Opus审核流程
- 打包问题：一直没彻底解决

### 核心原则
**所有决定必须经过雪子确认。没有捷径可走。**

## 雪子知识库 (XueziKB) 项目重启 [2026-04-04]

### 技术决策
- Windows端：WinUI 3 独立项目（C#）
- Android端：Android Studio + Kotlin + Jetpack Compose
- 共享类库：.NET Standard Library
- 本地数据库：SQLite
- 云端API：Python FastAPI + SQLite
- 架构文档：v6版本，已生成

### 当前状态
- 架构文档v6已生成，等待雪子确认
- 项目暂停中

### 雪子的指示
- 独立客户端，不要Electron浏览器模式
- 低并发同步场景

---

## 🌐 坚果云WebDAV访问Obsidian [2026-04-04]

### 连接信息
- **账号**: 1034440765@qq.com
- **服务器**: https://dav.jianguoyun.com/dav/
- **密码**: ai7eaer5mv2gixex
- **Vault路径**: /BOSI/zhaorui/（即坚果云/BOSI/zhaorui/）

### 使用方式
- 通过WebDAV直接读取/搜索雪子的Obsidian笔记
- 脚本位置: ~/.openclaw/workspace/obsidian-webdav/webdav.sh
- 配置: ~/.openclaw/workspace/obsidian-webdav/config.env

### 当前笔记结构
```
/BOSI/zhaorui/
├── .obsidian/           # Obsidian配置
├── 创建链接.md
├── 工作/
│   └── 2026.4.4.md     # 待办事项
├── 未命名/
└── 欢迎.md
```

### 可用命令
```bash
# 列出文件
~/.openclaw/workspace/obsidian-webdav/webdav.sh list

# 读取笔记
~/.openclaw/workspace/obsidian-webdav/webdav.sh read <文件名>

# 搜索
~/.openclaw/workspace/obsidian-webdav/webdav.sh search <关键词>
```

### 用途
- AI可以搜索雪子的Obsidian笔记内容
- 跨记忆关联（我的记忆 + 雪子的笔记）
- 工作记录同步
