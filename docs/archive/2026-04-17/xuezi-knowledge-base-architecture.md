# 雪子个人AI知识库 + 秘书App
## 技术架构设计方案 v1.0

**文档状态**：✅ 可作为开发依据  
**制定日期**：2026-04-03  
**负责人**：雪子助手架构组  
**服务器**：106.54.25.161  

---

## 一、项目愿景与设计原则

### 1.1 核心愿景

> 做一个陪伴雪子一辈子的AI知识伙伴——随手记录，问我即答，主动关怀。

这不是一个普通的笔记App。核心区别在于：
- **AI-native**：不是"笔记+AI功能"，而是"AI记忆+知识管理"一体化
- **主动式秘书**：不是被动查询，是AI主动提醒、主动整理、主动关联
- **可进化**：随着使用，AI越来越懂雪子，答案越来越精准

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| **数据主权** | 所有数据存储在雪子自己的服务器，不依赖第三方云 |
| **隐私优先** | 个人数据不离开私有环境，AI调用走私有部署 |
| **简单上手** | Phase 1 先做核心体验，不要一开始就做所有功能 |
| **可扩展** | 模块之间松耦合，Phase 2/3可以独立演进 |
| **稳定可靠** | 笔记是雪子的第二大脑，不能丢、不能乱 |

---

## 二、系统架构总览

### 2.1 架构分层图

```
┌─────────────────────────────────────────────────────────────────────┐
│                         用户层 (Client)                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  Web App │  │ Mac桌面  │  │ Windows  │  │ Android  │            │
│  │(Next.js) │  │(Tauri)   │  │(Tauri)   │  │(React    │            │
│  │          │  │          │  │          │  │ Native)  │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
└───────┼─────────────┼─────────────┼─────────────┼──────────────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       API网关层 (Gateway)                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Nginx (反向代理 + SSL)                    │   │
│  │              + Docker Gateway (鉴权/限流/路由)               │   │
│  └─────────────────────────────────────────────────────────────┘   │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  应用服务层    │     │  AI服务层      │     │  定时任务层    │
│  (Node.js)    │     │ (Python/FastAPI)│    │  (BullMQ)     │
│               │     │               │     │               │
│ · 用户认证    │     │ · 语义搜索    │     │ · 日程提醒    │
│ · 笔记CRUD   │     │ · RAG问答     │     │ · AI主动提醒  │
│ · 知识图谱   │     │ · 图片理解    │     │ · 数据备份    │
│ · 文件管理   │     │ · 语音转写    │     │ · 清理任务    │
│ · 同步服务   │     │ · Embedding   │     │               │
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        数据层 (Data Layer)                           │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ PostgreSQL   │  │   Meilisearch │  │  Redis        │             │
│  │ (主数据库)    │  │  (全文搜索)   │  │ (缓存/队列)   │             │
│  │              │  │              │  │              │             │
│  │ · 用户信息   │  │ · 笔记索引   │  │ · Session   │             │
│  │ · 笔记内容   │  │ · 语义向量   │  │ · 任务队列  │             │
│  │ · 日程事件   │  │ · AI搜索    │  │ · 实时缓存  │             │
│  │ · 知识图谱   │  │              │  │              │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ MinIO/S3     │  │   QDrant     │  │  文件存储     │             │
│  │ (对象存储)   │  │ (向量数据库)  │  │ (/data/files)│             │
│  │              │  │              │  │              │             │
│  │ · 笔记附件   │  │ · 笔记向量   │  │ · 原生文件   │             │
│  │ · 图片       │  │ · 知识图谱   │  │ · 备份       │             │
│  │ · 语音       │  │   关系向量   │  │              │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 技术选型总表

| 层级 | 组件 | 技术选型 | 理由 |
|------|------|---------|------|
| **前端** | Web应用 | Next.js 14 (App Router) | SSR首屏快，支持PWA |
| | 桌面端 | Tauri 2.0 | 体积小，原生体验，可本地运行 |
| | 移动端 | React Native (Expo) | 跨平台，统一体验 |
| **后端** | API服务 | Node.js + Fastify | 高性能，生态丰富 |
| | AI服务 | Python + FastAPI | AI模型生态，异步处理 |
| | 任务队列 | BullMQ + Redis | 定时任务，异步队列 |
| **数据库** | 关系型 | PostgreSQL 16 | 稳定，功能强，支持JSON |
| | 向量 | QDrant | 轻量，Rust实现，高性能 |
| | 搜索 | Meilisearch | 全文搜索，中文支持好 |
| | 缓存 | Redis 7 | 缓存、会话、队列 |
| | 对象存储 | MinIO | S3兼容，自建存储 |
| **AI能力** | LLM推理 | ollama / vLLM (私有部署) | 数据不外流，自主可控 |
| | Embedding | bge-m3 (本地) | 中文优化，多语言 |
| | 语音识别 | Whisper (本地) | 隐私保护 |
| **部署** | 容器 | Docker + Docker Compose | 快速部署 |
| | 域名/SSL | Nginx + Let's Encrypt | 已有方案可复用 |

---

## 三、核心功能模块划分

### 3.1 模块总览

```
┌─────────────────────────────────────────────────────────────────┐
│                    雪子AI知识库系统                               │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  📝 笔记模块 │  │  🧠 AI模块  │  │  📅 日程模块 │              │
│  │             │  │             │  │             │              │
│  │ · 随手记    │  │ · 语义搜索  │  │ · 日历视图  │              │
│  │ · 富文本    │  │ · RAG问答   │  │ · 定时提醒  │              │
│  │ · 图片附件  │  │ · 知识图谱  │  │ · 重复任务  │              │
│  │ · 语音转写  │  │ · AI摘要    │  │ · AI主动    │              │
│  │ · Markdown  │  │ · 智能标签  │  │   提醒      │              │
│  │ · 双链笔记  │  │ · 图片理解  │  │ · 多日历    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  📂 文件模块 │  │  🔗 图谱模块 │  │  🔔 通知模块 │              │
│  │             │  │             │  │             │              │
│  │ · 文件上传  │  │ · 实体管理  │  │ · WebPush  │              │
│  │ · PDF预览   │  │ · 关系管理  │  │ · 邮件通知  │              │
│  │ · Word预览  │  │ · 可视化   │  │ · 微信/飞书 │              │
│  │ · 全文搜索  │  │ · 智能推荐  │  │ · 多端同步  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  🔐 认证模块 │  │  🔄 同步模块 │  │  ⚙️ 系统模块 │              │
│  │             │  │             │  │             │              │
│  │ · 用户注册  │  │ · 多设备    │  │ · 数据备份  │              │
│  │ · 登录/登出 │  │   同步      │  │ · 导入导出  │              │
│  │ · 权限管理  │  │ · 增量同步  │  │ · 系统设置  │              │
│  │ · API Token │  │ · 冲突处理  │  │ · 操作日志  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 模块详细说明

#### 3.2.1 📝 笔记模块 (Notes Module)

**核心功能**：
- **随手记**：秒级启动，语音/文字/图片一键记录
- **富文本编辑**：支持标题、列表、代码块、引用、表格
- **Markdown支持**：即时渲染，支持双链 `[[笔记名]]`
- **图片附件**：拖拽上传，自动OCR识别文字
- **语音记录**：录音实时转文字，自动创建笔记
- **版本历史**：每次编辑自动保存，支持回滚

**数据结构**：

```sql
-- 笔记主表
CREATE TABLE notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(500) NOT NULL,
    content TEXT,                    -- Markdown/Rich Text
    content_html TEXT,               -- 渲染后的HTML
    summary TEXT,                    -- AI生成的摘要
    source VARCHAR(20) DEFAULT 'manual',  -- manual/voice/ai/file
    is_archived BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    synced_at TIMESTAMP
);

-- 笔记附件表
CREATE TABLE note_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    note_id UUID REFERENCES notes(id) ON DELETE CASCADE,
    filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,  -- MinIO存储路径
    file_size BIGINT,
    mime_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 笔记标签表
CREATE TABLE note_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    note_id UUID REFERENCES notes(id) ON DELETE CASCADE,
    tag_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 3.2.2 🧠 AI模块 (AI Module)

**核心功能**：
- **语义搜索**：输入自然语言，AI理解意图后找到相关笔记
- **RAG问答**：基于笔记内容回答"我上周记录的那个项目叫什么？"
- **知识图谱问答**："我和哪些人讨论过储能项目？"
- **AI摘要**：长笔记一键生成摘要
- **智能标签**：AI自动推荐标签（如：#工作 #储能 #待跟进）
- **图片理解**：截图/照片中的文字和内容自动识别

**RAG问答流程**：

```
用户问题: "我去年做的那个储能项目收益怎么样？"
    │
    ▼
┌──────────────┐
│  Query理解   │ ← AI分析用户意图，提取关键词
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  语义检索    │ ← 从QDrant向量数据库检索相关笔记 Top5
│  (QDrant)    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  上下文组装  │ ← 将检索到的笔记片段组装成上下文
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  LLM生成答案 │ ← 基于上下文生成答案，引用来源
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  答案呈现    │ ← 返回答案 + 引用笔记列表
└──────────────┘
```

**Embedding流程**（新笔记入库时）：

```
新笔记创建/更新
    │
    ▼
┌──────────────┐
│  内容预处理  │ ← 清洗、分段(Chunking 512 tokens)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Embedding   │ ← bge-m3 模型生成向量
│  (bge-m3)    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  向量存储    │ ← 存入QDrant (collection: notes)
└──────────────┘
```

#### 3.2.3 📅 日程模块 (Calendar Module)

**核心功能**：
- **日历视图**：月/周/日视图，日程一览
- **定时提醒**：支持微信/邮件/系统推送
- **重复日程**：每天/每周/每月/每年/工作日
- **AI主动提醒**：
  - "根据你记录的，明天要交储能项目方案"
  - "检测到你有3个未完成待办，要不要现在处理？"
- **自然语言创建**："下周三下午3点约了王总开会"

**数据结构**：

```sql
-- 日历表
CREATE TABLE calendars (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(200) NOT NULL,
    color VARCHAR(20) DEFAULT '#3788d8',
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 日程事件表
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    calendar_id UUID REFERENCES calendars(id),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    location VARCHAR(500),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    all_day BOOLEAN DEFAULT FALSE,
    reminder_minutes_before INTEGER DEFAULT 30,
    repeat_rule JSONB,  -- {"type":"weekly","days":[1,3,5]}
    is_completed BOOLEAN DEFAULT FALSE,
    source_note_id UUID REFERENCES notes(id),  -- 关联来源笔记
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- AI提醒记录表
CREATE TABLE ai_reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    event_id UUID REFERENCES events(id),
    reminder_time TIMESTAMP NOT NULL,
    message TEXT NOT NULL,
    is_sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP,
    is_dismissed BOOLEAN DEFAULT FALSE
);
```

#### 3.2.4 🔗 知识图谱模块 (Knowledge Graph Module)

**核心功能**：
- **双链笔记**：`[[笔记标题]]` 自动创建链接
- **实体提取**：AI自动从笔记中提取人物、项目、地点、概念
- **关系建立**：自动关联相关实体（如：项目←→负责人）
- **图谱可视化**：交互式查看实体关系网络
- **智能推荐**：写笔记时AI推荐相关笔记/人物/项目

**图谱数据结构**：

```sql
-- 实体表（人、项目、地点、概念等）
CREATE TABLE kg_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(300) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,  -- person/project/location/concept/tag
    description TEXT,
    metadata JSONB,  -- 扩展属性 {"company":"xxx","role":"xxx"}
    mention_count INTEGER DEFAULT 1,
    first_seen_at TIMESTAMP DEFAULT NOW(),
    last_seen_at TIMESTAMP DEFAULT NOW()
);

-- 关系表
CREATE TABLE kg_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    source_entity_id UUID REFERENCES kg_entities(id),
    target_entity_id UUID REFERENCES kg_entities(id),
    relation_type VARCHAR(100) NOT NULL,  -- works_at/mentioned_in/related_to
    weight FLOAT DEFAULT 1.0,
    source_note_id UUID REFERENCES notes(id),  -- 来源笔记
    created_at TIMESTAMP DEFAULT NOW()
);

-- 实体别名（同一实体的不同叫法）
CREATE TABLE kg_aliases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID REFERENCES kg_entities(id),
    alias VARCHAR(300) NOT NULL
);
```

#### 3.2.5 🔔 通知模块 (Notification Module)

**核心功能**：
- **多渠道推送**：WebPush / 邮件 / 飞书（复用现有渠道）
- **主动提醒**：AI判断时机主动发起提醒
- **静默模式**：支持免打扰时段
- **已读回执**：确认用户看到重要提醒

---

## 四、数据流设计

### 4.1 笔记创建数据流

```
用户输入（文字/语音/图片）
         │
         ▼
┌─────────────────┐
│   Client API    │ ← 移动/桌面/网页端
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│   Nginx Gateway │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Node.js API    │ ① 鉴权 → ② 保存笔记 → ③ 触发后续流程
│  (Fastify)      │
└────────┬────────┘
         │
    ┌────┴────┬──────────────┐
    │         │              │
    ▼         ▼              ▼
┌───────┐ ┌───────┐    ┌──────────────┐
│Postgres│ │ MinIO │    │  AI Queue    │
│笔记存储│ │ 文件存储│    │  (BullMQ)   │
└───┬───┘ └───┬───┘    └──────┬───────┘
    │         │               │
    │         │               ▼
    │         │        ┌──────────────┐
    │         │        │ Python AI    │
    │         │        │ Worker       │
    │         │        │              │
    │         │        │ ① OCR识别   │
    │         │        │ ② 语音转写  │
    │         │        │ ③ Embedding │
    │         │        │ ④ 实体提取  │
    │         │        │ ⑤ 摘要生成  │
    │         │        └──────┬───────┘
    │         │               │
    │         │               ▼
    │         │        ┌──────────────┐
    │         │        │   QDrant    │
    │         │        │ (向量存储)  │
    │         │        └──────────────┘
    │         │
    │         ▼
    │  ┌──────────────┐
    │  │  更新Postgres│
    │  │  AI结果写回  │
    │  └──────────────┘
    │
    └──────────────────→ 笔记同步队列 → 其他设备
```

### 4.2 AI问答数据流

```
用户提问: "我记得讨论过一个储能收益的计算，是和谁？"
         │
         ▼
┌─────────────────┐
│   Client UI     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Query API   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Query理解      │ ← LLM解析问题，提取关键实体
│  (FastAPI)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  向量检索       │ ← 从QDrant检索相关笔记Top5
│  (QDrant)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  上下文组装      │ ← 拼接检索结果为prompt
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM生成答案    │ ← 调用本地Ollama/vLLM
│  (Ollama)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  答案 + 引用    │ ← 返回答案，附带参考笔记链接
└─────────────────┘
```

### 4.3 同步数据流

```
设备A (手机)                    服务器                    设备B (Mac)
    │                            │                          │
    │ ──── 笔记变更 ──────────► │                          │
    │                            │ ──── 广播/轮询 ────────► │
    │                            │                          │
    │  ◄── 同步冲突处理 ──────── │                          │
    │                            │                          │
    │ ◄── 其他设备变更 ◄───────── │                          │
```

**同步策略**：
- **增量同步**：只同步变更的部分（基于 updated_at）
- **冲突处理**：Last-Write-Wins + 用户手动选择
- **离线支持**：本地优先，联网后合并
- **同步协议**：基于WebSocket实时同步 + HTTP轮询兜底

---

## 五、开发路线图

### Phase 1：核心基础（第1-4周）

**目标**：MVP版本，具备核心笔记+AI搜索能力

| 序号 | 功能 | 详细说明 | 优先级 |
|------|------|---------|--------|
| 1.1 | 用户认证 | 注册/登录/JWT/Session | P0 |
| 1.2 | 基础笔记CRUD | 创建/编辑/删除/搜索 | P0 |
| 1.3 | Markdown渲染 | 实时预览，代码高亮 | P0 |
| 1.4 | 图片上传 | MinIO存储，缩略图 | P0 |
| 1.5 | 全文搜索 | Meilisearch集成 | P0 |
| 1.6 | 语义搜索 | Embedding + QDrant | P0 |
| 1.7 | RAG问答 | 基于笔记的AI问答 | P0 |
| 1.8 | Web端UI | 响应式设计，移动端适配 | P0 |

**Phase 1 技术交付物**：
```
xuezi-knowledge/
├── backend/               # Node.js API
│   ├── src/
│   │   ├── routes/        # API路由
│   │   ├── services/      # 业务逻辑
│   │   ├── models/        # 数据模型
│   │   └── middleware/     # 中间件
│   └── package.json
├── ai-service/            # Python AI服务
│   ├── src/
│   │   ├── embedding.py   # Embedding服务
│   │   ├── rag.py         # RAG问答
│   │   └── worker.py      # 异步任务
│   └── requirements.txt
├── frontend/              # Next.js Web
│   ├── app/
│   ├── components/
│   └── public/
├── docker-compose.yml
└── README.md
```

### Phase 2：知识增强（第5-10周）

**目标**：知识图谱+日程管理+多设备同步

| 序号 | 功能 | 详细说明 | 优先级 |
|------|------|---------|--------|
| 2.1 | 双链笔记 | `[[笔记]]` 链接， backlink展示 | P0 |
| 2.2 | 知识图谱 | 实体提取，关系建立，图谱可视化 | P0 |
| 2.3 | 语音记录 | 录音转文字，自动创建笔记 | P1 |
| 2.4 | 文件附件 | PDF/Word预览，全文搜索 | P1 |
| 2.5 | 日历管理 | 日程创建/编辑/提醒 | P0 |
| 2.6 | 定时提醒 | BullMQ + 多渠道推送 | P0 |
| 2.7 | 多设备同步 | WebSocket + 增量同步 | P1 |
| 2.8 | AI主动提醒 | 基于上下文的智能提醒 | P1 |
| 2.9 | 桌面端 | Tauri Mac/Windows | P2 |
| 2.10 | 移动端 | React Native iOS/Android | P2 |

**Phase 2 新增模块**：

```
├── knowledge-graph/       # 知识图谱服务
│   ├── entity_extractor.py
│   ├── relation_builder.py
│   └── graph_visualizer.py
├── calendar/             # 日程服务
│   ├── event_scheduler.py
│   └── reminder_worker.py
├── sync-service/         # 同步服务
│   ├── websocket_server.py
│   └── conflict_resolver.py
└── mobile/               # React Native App
```

### Phase 3：智能化+生态（第11-16周）

**目标**：AI全面升级，开放生态

| 序号 | 功能 | 详细说明 | 优先级 |
|------|------|---------|--------|
| 3.1 | AI记忆进化 | 记录用户反馈，持续优化 | P1 |
| 3.2 | 多模态理解 | 图片/表格/图表深度理解 | P1 |
| 3.3 | 插件系统 | 开放API，第三方集成 | P2 |
| 3.4 | 数据导出 | 全量导出，格式兼容 | P1 |
| 3.5 | API开放 | 个人使用API Token | P2 |
| 3.6 | 性能优化 | 大规模笔记(10000+)优化 | P1 |

---

## 六、部署方案

### 6.1 服务器资源规划

**当前服务器**：106.54.25.161（腾讯云）

| 资源 | 规格 | 用途 |
|------|------|------|
| CPU | 2核+ | 应用服务+AI推理 |
| 内存 | 4GB+ | PostgreSQL+Redis+AI模型 |
| 磁盘 | 100GB+ | 数据+备份 |
| 带宽 | 5Mbps+ | 用户访问 |

**如果资源紧张**：
- AI服务可以先用API方式（OpenAI/MiniMax）过渡
- 逐步迁移到私有部署

### 6.2 Docker Compose 部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - ai-service
    restart: unless-stopped

  # Node.js 后端API
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://xuezi:xxx@postgres:5432/xuezi_kb
      - REDIS_URL=redis://redis:6379
      - MINIO_ENDPOINT=minio:9000
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - postgres
      - redis
      - minio
    restart: unless-stopped

  # Python AI服务
  ai-service:
    build: ./ai-service
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - QDRANT_URL=http://qdrant:6333
      - MEILI_URL=http://meilisearch:7700
    depends_on:
      - ollama
      - qdrant
      - meilisearch
    restart: unless-stopped

  # PostgreSQL 主数据库
  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=xuezi_kb
      - POSTGRES_USER=xuezi
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  # Redis 缓存/队列
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # Meilisearch 全文搜索
  meilisearch:
    image: getmeili/meilisearch:latest
    environment:
      - MEILI_MASTER_KEY=${MEILI_KEY}
    volumes:
      - meili_data:/meili_data
    restart: unless-stopped

  # QDrant 向量数据库
  qdrant:
    image: qdrant/qdrant:latest
    volumes:
      - qdrant_data:/qdrant/storage
    restart: unless-stopped

  # MinIO 对象存储
  minio:
    image: minio/minio:latest
    environment:
      - MINIO_ROOT_USER=${MINIO_USER}
      - MINIO_ROOT_PASSWORD=${MINIO_PASSWORD}
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"
    restart: unless-stopped

  # Ollama 本地LLM（如果资源够）
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  meili_data:
  qdrant_data:
  minio_data:
  ollama_data:
```

### 6.3 域名与SSL

```
域名: knowledge.xuezi.cn (或复用现有子域名)
SSL: Let's Encrypt 自动续期
Nginx配置: 反向代理到后端服务
```

### 6.4 备份策略

| 备份类型 | 频率 | 保留时间 | 存储位置 |
|---------|------|---------|---------|
| 数据库全量 | 每天 02:00 | 30天 | 本地 + 异地 |
| 文件存储 | 每天 03:00 | 7天 | 本地 |
| 配置备份 | 每次修改 | 10个版本 | Git仓库 |

---

## 七、AI服务配置

### 7.1 LLM选型（按优先级）

| 方案 | 模型 | 适用场景 | 资源要求 |
|------|------|---------|---------|
| **推荐** | Ollama + Qwen2.5 | 通用对话+知识问答 | 4GB+显存 |
| 备选 | Ollama + DeepSeek | 更强推理能力 | 6GB+显存 |
| 备选 | MiniMax API | 早期快速验证 | 无(云端) |

### 7.2 Embedding模型

```python
# ai-service/src/embedding.py
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('BAAI/bge-m3')

def embed_text(text: str) -> list[float]:
    """生成文本向量"""
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()
```

### 7.3 RAG配置

```python
# ai-service/src/rag.py
from qdrant_client import QDrantClient
from qdrant_client.models import Distance, VectorParams

# 初始化QDrant
client = QDrantClient("localhost", port=6333)

# 创建笔记集合
client.create_collection(
    collection_name="notes",
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
)

# 检索配置
SEARCH_LIMIT = 5  # 返回Top5相关笔记
SCORE_THRESHOLD = 0.5  # 相关性阈值
CHUNK_SIZE = 512  # 分块大小
```

---

## 八、安全设计

### 8.1 认证与授权

```
用户注册 → 密码加盐Hash (bcrypt)
    ↓
登录 → JWT Token (1小时有效)
    ↓
Token刷新 → Refresh Token (7天有效)
    ↓
API请求 → JWT验证 + 用户绑定
```

### 8.2 数据安全

| 安全措施 | 说明 |
|---------|------|
| HTTPS | 全站强制HTTPS |
| 密码Hash | bcrypt，不可逆 |
| SQL注入 | 参数化查询，ORM |
| XSS | Content-Security-Policy |
| CORS | 严格域名白名单 |
| 速率限制 | API限流防滥用 |
| 数据加密 | 敏感字段AES加密 |

### 8.3 隐私保护

- 笔记数据仅存储在雪子自己的服务器
- AI处理优先使用本地模型
- 外部API调用时脱敏处理
- 支持数据完全导出/删除

---

## 九、非功能性需求

| 指标 | 目标值 |
|------|--------|
| **首屏加载** | < 2秒 |
| **笔记搜索响应** | < 500ms |
| **AI问答响应** | < 5秒 |
| **系统可用性** | 99.5% |
| **数据可靠性** | 99.99% |
| **支持用户数** | 1-5人（个人场景） |

---

## 十、项目启动检查清单

### 环境准备（第0周）

- [ ] 服务器环境确认（SSH访问）
- [ ] 域名解析配置
- [ ] Docker + Docker Compose 安装
- [ ] PostgreSQL / Redis / MinIO 初始化
- [ ] Git仓库初始化

### Phase 1 开发（第1-4周）

- [ ] 用户认证模块
- [ ] 笔记CRUD + Markdown
- [ ] 图片上传 + 存储
- [ ] Meilisearch 全文搜索
- [ ] Embedding + QDrant 向量检索
- [ ] RAG 问答基础
- [ ] Web端 UI

### Phase 2 开发（第5-10周）

- [ ] 知识图谱（实体+关系）
- [ ] 语音转笔记
- [ ] 日历 + 定时提醒
- [ ] 多设备同步
- [ ] 桌面端 App
- [ ] AI主动提醒

### Phase 3 开发（第11-16周）

- [ ] AI记忆进化
- [ ] 插件系统
- [ ] 性能优化
- [ ] 文档完善

---

## 附录

### A. 参考项目

| 项目 | 参考点 |
|------|--------|
| **Notion** | 笔记编辑体验 |
| **Obsidian** | 双链笔记 + 图谱 |
| **Logseq** | 大纲笔记 + 图谱 |
| **Mem** | AI知识管理 |
| **Apple Notes** | 简单随手记体验 |

### B. 关键依赖版本

```
node: >=20.0.0
python: >=3.11
postgres: >=16
redis: >=7
nextjs: 14.x
fastify: 4.x
fastapi: 0.115.x
qdrant: 1.7.x
meilisearch: 1.6.x
```

### C. 开发优先级建议

**如果只有一个人开发**，建议分工：

| 阶段 | 重点 | 时间 |
|------|------|------|
| Phase 1 | 雪子助手(我)负责架构 + Code执行 | 4周 |
| Phase 2 | 继续用Code执行开发 | 6周 |
| Phase 3 | 根据需要选择性开发 | 灵活 |

**核心原则**：Phase 1 先做核心体验，MVP验证后再迭代。

---

*文档版本：v1.0*  
*制定日期：2026-04-03*  
*下次审查：Phase 1 完成后*
