# 历史记忆精华总结 - 2026年4月（详细技术版）

*归档日期: 2026-04-16*
*来源: memory/ (2026-03-22 ~ 2026-04-16)*
*总览: 26天记忆精华 + 完整技术细节*

---

## 一、系统与工具升级

### 1. Claude Code 能力全面升级 (2026-04-04)

#### 核心能力
- **后台持久化**: openclaw cron + CC = 后台任务不被杀
- **多轮对话**: sessions_spawn 可后台多轮对话
- **OMC工作流**: autopilot、ultrawork、team-exec 全部可用

#### 模型切换脚本
```bash
# 切换到 Opus（架构/验收）
~/.openclaw/workspace/scripts/cc-model-switch.sh opus

# 切换到 MiniMax（执行开发）
~/.openclaw/workspace/scripts/cc-model-switch.sh minimax

# 查看当前模型
~/.openclaw/workspace/scripts/cc-model-switch.sh status
```

#### acpx 调用方式
```bash
# 创建 session
acpx claude sessions new --name <session名>

# 执行任务（等待结果）
acpx claude -s <session名> "任务描述"

# 后台执行（--no-wait）
acpx claude -s <session名> --no-wait "任务描述"

# 查看状态
acpx claude -s <session名> status

# 查看结果
tail ~/.acpx/sessions/<session-id>.stream.ndjson

# 关闭 session
acpx claude sessions close <session名>
```

#### 模型配置优先级
| 场景 | 模型 | 说明 |
|------|------|------|
| 日常对话 | MiniMax-M2.7 | 省钱、快速 |
| 架构设计 | Opus | 深度思考 |
| 代码审查 | Opus | 质量把关 |
| CC执行 | MiniMax-M2.7 | 主力开发 |

#### 调用规范文档
`~/.openclaw/workspace/docs/ClaudeCode-调用规范.md`

---

### 2. 记忆系统大改造 (2026-04-16)

#### 旧格式问题
```markdown
## 08:00 自动提取
### 用户消息
- [Thu 2026-04-16 07:39 GMT+8] <<<BEGIN_OPENCLAW_INTERNAL_CONTEXT>>>
...原始消息堆砌，噪音极高
```

#### 新格式
```markdown
## 08:57 自动记录
### 决策 (DECISION)
- 🔴 [决策] **jieba 工作正常** ✅

### 任务 (TASK)
- 📋 [任务] 已启动 Opus 架构设计中 🔍

### 知识 (KNOWLEDGE)
- 💡 [知识] 学会了 xxx

### 讨论 (DISCUSSION)
- 💬 讨论内容...
```

#### 分类关键词配置
```python
# session-to-memory.py
DECISION_KEYWORDS = [
    "决定用", "决定不", "决定改", "决定取消", "决定恢复",
    "就用", "就不改", "就不做", "就用它",
    "取消这个", "取消计划", "取消任务",
    "改用", "换成", "改回",
    "停止这个", "停止做", "先不做", "先不改",
    "开始干", "先这样", "就这样"
]
TASK_KEYWORDS = [
    "去做", "开始做", "完成了", "没完成",
    "待办", "还没做", "正在做", "进行中",
    "改完了", "改好了", "修好了", "搞定了", "搞定", "做完了", "部署了",
    "写好了", "提交了", "发给你", "发到", "发给你了"
]
KNOWLEDGE_KEYWORDS = [
    "学会了", "原来如此", "新发现", "第一次知道",
    "明白了", "懂了", "学到了", "记住了",
    "这就是", "原来是"
]
```

#### 改造脚本位置
`~/.openclaw/workspace/scripts/session-to-memory.py`

#### 定时任务配置
```bash
# crontab -l
0 8,16,23 * * * /Users/zhaoruicn/.openclaw/workspace/scripts/session-to-memory.sh
```

---

### 3. 模型配置清理 (2026-04-16)

#### 删除的配置
- **opus-proxy**: 配置错误，Opus 应通过 Claude Code 使用
- **qwen3.5-plus**: 阿里云灵码 Key 不能用于标准百炼 API

#### 当前有效配置
```json
// ~/.openclaw/openclaw.json
{
  "bailian": {
    "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",
    "apiKey": "sk-sp-26a5e11d3a8d47589a2ce4a4d0e3222b",
    "api": "openai-completions",
    "models": [{"id": "kimi-k2.5", ...}]
  },
  "kimi-coding": {
    "baseUrl": "https://api.kimi.com/coding",
    "apiKey": "sk-kimi-2sxCTUilQ9nPKSPAFHcO2gIm7EguvTWvmZwaVclW15ZKwWq4uWZxKAhIWbULJEmD",
    "api": "anthropic-messages",
    "models": [{"id": "kimi-for-coding", ...}]
  },
  "minimax-cn": {
    "baseUrl": "https://api.minimaxi.com/anthropic",
    "apiKey": "sk-cp-TaEn7XZHReif66-VaxR-UZJuHCoYYYqho4xu6pV22L3MtAL9oImB0iubia4dRjZDN-0avV5_rSS2ggBC6w2gHYz1tYN0semS3mps1PrA9lS-16qJhoh8l3Q",
    "api": "anthropic-messages",
    "models": [{"id": "MiniMax-M2.7", ...}]
  }
}
```

#### Claude Code 模型配置
```json
// ~/.claude/settings.json (Opus)
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://timesniper.club",
    "ANTHROPIC_AUTH_TOKEN": "sk-OLqePftCUT0kOGggfgGtgeMOE3km0hPXwxUf6FTpFFL7mdsJ",
    "ANTHROPIC_MODEL": "claude-opus-4-6"
  }
}

// ~/.claude/settings.json (MiniMax)
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.minimaxi.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "sk-cp-TaEn7XZHReif66-VaxR-UZJuHCoYYYqho4xu6pV22L3MtAL9oImB0iubia4dRjZDN-0avV5_rSS2ggBC6w2gHYz1tYN0semS3mps1PrA9lS-16qJhoh8l3Q",
    "ANTHROPIC_MODEL": "MiniMax-M2.7"
  }
}
```

---

### 4. OpenClaw版本更新 (2026-04-12)

#### 当前 vs 最新
- **当前**: 2026.4.2
- **最新**: 2026.4.11 (差9个版本)

#### 4.3-4.11 新功能
| 功能 | 说明 |
|------|------|
| /tasks | 后台任务看板 |
| Voice Wake | macOS语音唤醒 |
| SearXNG | 搜索聚合 |
| Cron工具白名单 | 定时任务增强 |
| 飞书文档评论 | 评论增强 |
| MiniMax OAuth | Bearer认证修复 |
| ChatGPT记忆导入 | Dreaming系统 |

#### Dreaming系统
- **三阶段睡眠**: Light/REM/Deep
- **功能**: 自动整理短期→长期记忆
- **状态**: 未启用

---

## 二、项目进展

### 1. PPT制作系统 (2026-03-22)

#### 工作流
```
Kimi深度思考生成内容 → 用户投喂给我 → 我生成PPTX
```

#### 技能包
- **名称**: powerpoint-pptx
- **功能**: Python-pptx 生成 PPT
- **状态**: ✅ 安装成功，测试通过

#### 模板位置
`~/.openclaw/workspace/zero_carbon_template_v2.pptx`

---

### 2. AIDC配储深度分析 (2026-04-04)

#### 分析资料
- 图片.docx
- 链接.docx
- 产品规格书.pdf
- 4篇文章

#### 分析维度
- 单柜容量
- 工况要求
- 电芯要求
- 自研参数

#### 输出
Word文档（Claude Code生成）

---

### 3. 十五五规划讨论 (2026-04-16)

#### 参会人
- 雪子
- 杨培
- 赵锐

#### 重点
- 场景业务：AIDC、零碳、工商业结合
- 模式整合：三种场景如何结合

#### 待续
第二部分整理后继续第三、四部分

---

## 三、重要修复与优化（详细技术）

### 1. 税务测算增值税Bug修复 (2026-03-25)

#### 问题代码
```javascript
// 错误：重复扣除增值税
profit = (income_with_tax - cost_with_tax) - vat - additional_tax;
// income_with_tax - cost_with_tax 已经消去增值税，又扣了一次
```

#### 修复后
```javascript
// 正确：使用不含税收入，只扣附加税
profit = income_without_tax - cost_without_tax - additional_tax;
```

#### 备份文件
`/usr/share/nginx/html/calculation.html.bak.20260325_174505`

---

### 2. 备份系统大修复 (2026-04-08)

#### 问题
- 备份大小：172MB（平时89MB）
- 大了近一倍

#### 根因分析
1. `skills-backup/` 目录积累旧备份包
   - `skills-backup-20260404.tar.gz` 83MB
   - `skills-backup-20260406.tar.gz` 83MB
2. `image-process/` 308MB 没被排除
3. `glmv-stock-analyst/venv/` 272MB 没被排除
4. `archived/` 目录被重复复制

#### 修复脚本关键代码
```bash
# backup-core.sh
create_archive() {
    # 排除规则
    EXCLUDES="--exclude=*.tar.gz \
              --exclude=image-process \
              --exclude=glmv-stock-analyst/venv \
              --exclude=archived"
    
    # 重建目录结构时排除 archived
    rsync -av $EXCLUDES $SOURCE/ $DEST/
}
```

#### 清理操作
```bash
# 删除废弃技能包
rm -rf ~/.openclaw/workspace/skills/archived  # 21MB

# 删除旧备份包
rm -f ~/.openclaw/workspace/skills-backup/*.tar.gz
```

#### 结果
| 指标 | 修复前 | 修复后 | 改善 |
|------|--------|--------|------|
| 备份大小 | 172MB | 1.1MB | -99% |
| OUC盘占用 | 585MB | 5.7MB | -99% |

---

### 3. 广播专员重复发送修复 (2026-04-08)

#### 问题
早8点日报发了好几次

#### 原因
飞书多设备同时在线导致重复推送

#### 修复
```bash
# 删除 08:00 早安问候 cron
# 保留：记忆提取 + 任务汇总
```

---

### 4. MEMORY.md精简 (2026-03-31)

#### 精简结果
| 指标 | 原始 | 精简后 | 减少 |
|------|------|--------|------|
| 行数 | 1149 | 662 | -42% |
| 字符 | 24006 | 13679 | -43% |

#### 删除内容
- Claude多Agent开发架构 → AGENTS.md已有
- 图片识别规则 → AGENTS.md新增
- Claude开发流程 → AGENTS.md已有
- 中创新航案例 → 过期
- 山东电力现货分析 → 过期
- 双电脑协同 → 过期

#### 新增至AGENTS.md
- 图片识别规则区块

---

## 四、关键决策记录

| 日期 | 决策 | 技术细节 |
|------|------|----------|
| 2026-04-04 | Claude Code能力升级 | cron + CC后台持久化 |
| 2026-04-08 | 备份系统修复 | 172MB→1.1MB，排除规则优化 |
| 2026-04-12 | Kimi Coding配置 | baseUrl: api.kimi.com/coding |
| 2026-04-16 | Memory格式改造 | 四段分类，关键词规则 |
| 2026-04-16 | 模型配置清理 | 删除opus-proxy、qwen3.5-plus |
| 2026-04-16 | 按月汇总归档 | 新建archive_summary_2026-04.md |

---

## 五、外部服务配置（完整）

### 坚果云WebDAV
```yaml
账号: 1034440765@qq.com
服务器: https://dav.jianguoyun.com/dav/BOSI/zhaorui/
密码: ai7eaer5mv2gixex
脚本: ~/.openclaw/workspace/obsidian-webdav/webdav.sh
```

### Kimi Coding
```yaml
Key: sk-kimi-2sxCTUilQ9nPKSPAFHcO2gIm7EguvTWvmZwaVclW15ZKwWq4uWZxKAhIWbULJEmD
baseUrl: https://api.kimi.com/coding
api: anthropic-messages
模型: kimi-for-coding
注意: 额度只剩2%，需充值
```

### 腾讯云服务器
```yaml
IP: 106.54.25.161
用户名: root
密码: Zr123456
网站目录: /usr/share/nginx/html/
```

### 韩国服务器
```yaml
IP: 43.108.18.71
用途: V2Ray + Claude Code + Codex
配置: 2核2G / 200M带宽
注意: 内存1.6G，需及时关闭session
```

---

## 六、定时任务配置

```bash
# crontab -l
0 8,16,23 * * * /Users/zhaoruicn/.openclaw/workspace/scripts/session-to-memory.sh
0 16,30 * * 1-5 /usr/bin/python3 /Users/zhaoruicn/.openclaw/workspace/scripts/stock_push_fast.py
0 22 * * * /usr/local/bin/openclaw cron run --job daily-backup
0 3 * * 0 /Users/zhaoruicn/.openclaw/workspace/scripts/weekly-cleanup.sh
0 9 * * 0 /Users/zhaoruicn/.openclaw/workspace/scripts/obsidian-weekly-sync.sh
```

---

## 七、教训与经验（详细）

### 1. 韩国服务器内存管理 (2026-04-16)
**问题**: MiniMax用完不关session，堆积3个Claude实例
**后果**: 内存占满1.0G/1.6G，服务器卡顿
**解决**: 
```bash
# 查看进程
ps aux | grep claude

# 杀掉旧进程
kill <PID>

# 及时关闭session
acpx claude sessions close <session-name>
```
**结果**: 内存从1.0G降到568M

### 2. API Key管理 (2026-04-16)
**问题**: MEMORY.md和openclaw.json的Key不一致
**后果**: 过几天就"连不上"
**解决**: 
- 测试有效后立即更新MEMORY.md
- 统一记录位置

### 3. acpx --no-wait模式
**用途**: 后台任务，不阻塞当前会话
**命令**: `acpx claude -s x --no-wait "task"`
**注意**: 结果写入 `~/.acpx/sessions/<id>.stream.ndjson`

---

## 八、文件归档

| 文件 | 说明 | 日期 |
|------|------|------|
| archive_summary_2026-03.md | Q1汇总（2-3月）| 2026-04-12 |
| archive_summary_2026-04.md | 4月汇总（3月22日-4月16日）| 2026-04-16 |

---

*此文件整合自 2026-03-22 ~ 2026-04-16 历史记忆，共26天*
*包含完整技术细节，可直接复制使用*
*可被FTS和jieba索引*
*最后更新: 2026-04-16*
