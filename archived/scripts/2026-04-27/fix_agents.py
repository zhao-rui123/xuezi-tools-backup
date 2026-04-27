#!/usr/bin/env python3
with open('AGENTS.md', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''## 🔧 问题排查五步法（Codex方法论，2026-04-22）

*当系统出问题（配置丢失、功能异常、cron失效）时，按以下步骤排查*

### 第一步：找关键引用 + 断点定位
```bash
# 搜所有相关引用
rg "问题关键词" ~/.openclaw -g '!.git'

# 找时间线文件（cron、config、hook）
find ~/.openclaw -maxdepth 4 \\
  \\( -name 'BOOTSTRAP*' -o -name '*cron*' -o -name 'jobs.json*' \\
     -o -name 'openclaw.json*' -o -name '*config*' \\
  \\) 2>/dev/null

# 用时间节点定位断点（查 git log 或备份文件）
ls -la ~/.openclaw/*.save ~/.openclaw/cron/*.bak 2>/dev/null
```

### 第二步：并排对比新旧版本
- 旧配置 vs 新配置（找缺失项）
- 常用备份：`openclaw.json.save`、`jobs.json.bak`
- 逐段对比，确认"机制被删"还是"执行失败"

### 第三步：追踪调用链
```bash
# 哪些脚本在调用它
rg "目标脚本名" ~/.openclaw/workspace/scripts/ -l

# 脚本指向的文件还在吗
ls -la ~/.openclaw/workspace/scripts/目标脚本.py

# 常见断裂点：文件被移走但调用方没更新
```

### 第四步：本地验证（不依赖外部）
```bash
# 直接跑脚本本身，确保基础可用
python3 ~/.openclaw/workspace/scripts/目标脚本.py save "测试"

# 验证 cron 是否真的在跑
crontab -l | rg 目标脚本

# 测试代理是否通（网络相关）
curl -x http://127.0.0.1:1087 https://example.com --connect-timeout 3
```

### 第五步：修复分层交付
| 优先级 | 类型 | 说明 |
|--------|------|------|
| P0 | 立刻能修的 | 直接修，save+git commit |
| P1 | 改配置的 | 先问用户，加 git 快照再改 |
| P2 | 锦上添花的 | 记录下来，以后再做 |

**核心心法**：先找断点时间，再顺藤摸瓜引用链，最后小范围验证再推广。

---

## ⚠️ 记忆管理铁律（2026-04-12新增）'''

new_content = '''## 🤖 Codex 干活方法论（雪子助手行为准则）

*来源：Codex 实际案例提炼 + 问题排查经验，2026-04-26 整合*

### 核心6条铁律
1. **先读手册再动手** — 不熟悉的任务先读规范文档
2. **最小改动原则** — 只改问题点，其他不动
3. **改动前先备份** — git快照 + crontab回滚
4. **改完立刻验证** — 确认生效再收工
5. **找根因，不治标** — 找到断点时间+引用链追踪，从源头解决
6. **汇报清晰** — 说明改了什么、为什么改、不改什么

### 四条干活原则
1. **先读再评，不跳步** — 先把相关脚本全读一遍再判断
2. **聚焦核心，不跑题** — 收窄到子问题，不发散
3. **用证据diss，不空洞** — 精确到具体数据行/文件行号
4. **给路线，不只抛问题** — 发现问题就顺手提解决方案

### 问题排查五步法

*当系统出问题（配置丢失、功能异常、cron失效）时，按以下步骤排查*

**第一步：找关键引用 + 断点定位**
```bash
rg "问题关键词" ~/.openclaw -g '!.git'
find ~/.openclaw -maxdepth 4 \\
  \\( -name 'BOOTSTRAP*' -o -name '*cron*' -o -name 'jobs.json*' \\
     -o -name 'openclaw.json*' -o -name '*config*' \\
  \\) 2>/dev/null
ls -la ~/.openclaw/*.save ~/.openclaw/cron/*.bak 2>/dev/null
```

**第二步：并排对比新旧版本**
- 旧配置 vs 新配置（找缺失项）
- 常用备份：`openclaw.json.save`、`jobs.json.bak`

**第三步：追踪调用链**
```bash
rg "目标脚本名" ~/.openclaw/workspace/scripts/ -l
ls -la ~/.openclaw/workspace/scripts/目标脚本.py
```

**第四步：本地验证（不依赖外部）**
```bash
python3 ~/.openclaw/workspace/scripts/目标脚本.py save "测试"
crontab -l | rg 目标脚本
curl -x http://127.0.0.1:1087 https://example.com --connect-timeout 3
```

**第五步：修复分层交付**
| 优先级 | 类型 | 说明 |
|--------|------|------|
| P0 | 立刻能修的 | 直接修，save+git commit |
| P1 | 改配置的 | 先问用户，加 git 快照再改 |
| P2 | 锦上添花的 | 记录下来，以后再做 |

**核心心法**：先找断点时间，再顺藤摸瓜引用链，最后小范围验证再推广。

### 四条铁律（强制检查点）

*遇到以下场景时，必须先过一遍再开口*

| 场景 | 我必须做的 |
|------|-----------|
| 遇到不熟悉的机制 | 先读代码再说话，开口说"我看一下" |
| 被问方案/结论 | 确认证据在哪，具体文件第几行 |
| 被抓包/被纠正 | 不解释，直接认错 |
| 重大问题 | 搜索 Codex 干活方法论确认没有遗漏 |

**核心：不是"知道"，是"做到"**

---

## ⚠️ 记忆管理铁律（2026-04-12新增）'''

if old in content:
    content = content.replace(old, new_content)
    with open('AGENTS.md', 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK')
else:
    print('NOT FOUND')
