# Obsidian知识库整合工作流

*创建于2026-04-05*

## 目标

将雪子助手的知识管理升级为：
- 📝 Obsidian笔记 → ☁️ 坚果云同步 → 🧠 PARA组织 → 🔍 全文搜索

## 完整配置流程

### 第一阶段：基础设置

#### 1.1 Obsidian安装
- 在Windows上安装Obsidian
- 创建Vault（保险库）

#### 1.2 坚果云WebDAV配置
```
服务器: https://dav.jianguoyun.com/dav/
路径: /BOSI/zhaorui/雪子助手/
账号: 1034440765@qq.com
密码: ai7eaer5mv2gixex
```

#### 1.3 验证同步
- 在Obsidian中启用社区插件"Obsidian Sync"或使用第三方同步
- 或使用坚果云官方客户端同步到本地

### 第二阶段：OpenClaw配置

#### 2.1 创建WebDAV访问脚本
路径: `~/.openclaw/workspace/obsidian-webdav/webdav.sh`

#### 2.2 安装技能包
```bash
clawhub install obsidian-daily --dir ~/.openclaw/workspace/skills
clawhub install obsidian-task --dir ~/.openclaw/workspace/skills
```

#### 2.3 安装PARA Second Brain
```bash
clawhub install para-second-brain --dir ~/.openclaw/workspace/skills
```

#### 2.4 创建PARA目录结构
```bash
mkdir -p ~/.openclaw/workspace/notes/{projects,areas,resources/templates,archive}
mkdir -p ~/.openclaw/workspace/memory
ln -sfn ~/.openclaw/workspace/notes ~/.openclaw/workspace/memory/notes
```

### 第三阶段：知识库同步

#### 3.1 Obsidian目录结构（与OpenClaw对应）
```
雪子助手/
├── 技能索引/       → OpenClaw skills说明
├── 记忆/          → 雪子助手身份档案
├── 雪子档案/      → 雪子个人信息
└── 工作/          → 每日工作记录
```

#### 3.2 同步内容
- 身份档案更新时同步到Obsidian
- 工作记录自动同步
- 重要决策存档

### 第四阶段：验证

#### 4.1 验证同步
```bash
# 从Obsidian读取
~/.openclaw/workspace/obsidian-webdav/webdav.sh read "雪子助手/技能索引/index.md"

# 写入Obsidian
curl -u "账号:密码" -X PUT -d "内容" "URL"
```

#### 4.2 验证memory_search
```bash
memory_search "关键词"
# 应该能搜到MEMORY.md + memory笔记 + notes全部内容
```

## 技能包说明

### obsidian-daily
- 按日期创建/打开日记
- 追加条目、读取历史
- 支持自然语言日期

### obsidian-task
- 列出obsidian中的任务
- 勾选/取消任务
- 任务管理

### para-second-brain
- PARA方法组织知识
- 符号链接扩展搜索范围
- 记忆刷新协议

## 目录对应关系

| Obsidian (坚果云) | OpenClaw (本地) | 用途 |
|-------------------|-----------------|------|
| /雪子助手/技能索引/ | skills/*/SKILL.md | 技能包说明 |
| /雪子助手/记忆/ | MEMORY.md | 身份档案 |
| /雪子助手/工作/ | memory/YYYY-MM-DD.md | 每日记录 |
| /雪子助手/雪子档案/ | USER.md | 雪子信息 |

## PARA目录用途

| 目录 | 用途 | 示例 |
|------|------|------|
| projects | 活跃项目 | 零碳园区方案 |
| areas | 持续责任 | 健康追踪 |
| resources | 参考资料 | 储能知识 |
| archive | 归档 | 已完成项目 |

## 维护任务

### 每周日09:00 (crontab)
- obsidian-weekly-sync.sh → 同步笔记

### 每日
- memory自动归档
- 重要内容同步到Obsidian

## 故障排除

### 同步失败
1. 检查坚果云账号状态
2. 验证WebDAV配置
3. 检查网络连接

### memory_search不工作
1. 确认符号链接存在: `ls -la memory/notes`
2. 确认notes目录有内容

## 相关文件

- `obsidian-webdav/webdav.sh` - WebDAV访问脚本
- `skills/obsidian-daily/` - 日记技能包
- `skills/obsidian-task/` - 任务技能包
- `skills/para-second-brain/` - 知识组织技能包
- `memory/` - 日常记忆
- `notes/` - PARA知识库

---

*由雪子助手自动生成*
