# 雪子个人AI知识库 + 秘书App 技术架构设计 v2.0

> 文档版本：v2.0  
> 作者：雪子助手  
> 日期：2026-04-03  
> 状态：**可直接作为开发依据**

---

## 一、项目概述

### 1.1 项目定位
- **产品名称**：雪子知识库（XueziKB）
- **核心定位**：个人AI知识管理 + 智能秘书一体化平台
- **目标用户**：雪子（单人使用）
- **数据存储**：腾讯云服务器（106.54.25.161）

### 1.2 核心使用场景
| 场景 | 说明 |
|------|------|
| 会议纪要 | 快速记录 + AI整理 + 标签分类 |
| 随手记 | 全局快捷键 capture，碎片化想法 |
| 知识管理 | 笔记/文件/思维导图统一管理 |
| 日程提醒 | 定时提醒 → 飞书推送 |
| AI问答 | 基于个人知识库的RAG问答 |

### 1.3 Phase 1 砍掉的功能（不做的）
- 数据库视图（看板/表格/画廊）
- 插件系统
- 团队协作

---

## 二、技术架构总览

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        客户端层                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐  │
│  │ Web App │  │ Mac桌面 │  │Win桌面  │  │ Android App    │  │
│  │(React)  │  │(Electron)│ │(Electron)│ │ (React Native) │  │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────────┬────────┘  │
│       │            │            │                │           │
│       └────────────┴─────┬──────┴────────────────┘           │
│                          │                                   │
│                    本地 SQLite                               │
│                  (离线笔记缓存)                               │
└──────────────────────────┼───────────────────────────────────┘
                           │ HTTPS
┌──────────────────────────┼───────────────────────────────────┐
│                    腾讯云服务器 (106.54.25.161)                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                      Nginx (反向代理)                     │ │
│  │                    SSL + 静态资源服务                      │ │
│  └──────────────────────────┬──────────────────────────────┘ │
│                             │                                 │
│  ┌──────────────────────────┴──────────────────────────────┐ │
│  │                    API 网关 (Node.js)                     │ │
│  │              JWT认证 / 限流 / 请求路由                      │ │
│  └─┬────────┬────────┬────────┬────────┬────────┬────────┘ │
│    │        │        │        │        │        │           │
│  ┌─┴───┐┌──┴───┐┌───┴──┐┌───┴──┐┌───┴──┐┌───┴───┐          │
│  │笔记  ││文件  ││图谱  ││日程  ││AI    ││同步   │          │
│  │服务  ││服务  ││服务  ││服务  ││(RAG) ││服务   │          │
│  └──┬─┘└──┬──┘└──┬──┘└──┬──┘└──┬──┘└──┬──┘          │
│     │     │      │      │      │      │               │
│  ┌──┴──────┴──────┴──────┴──────┴──────┴──────────┐  │
│  │              PostgreSQL 15 (主数据库)             │  │
│  │  笔记/笔记本/标签/文件/图谱/日程/模板/回收站       │  │
│  └─────────────────────┬───────────────────────────┘  │
│                        │                                 │
│  ┌─────────────────────┴───────────────────────────┐  │
│  │           Elasticsearch 8.x (全文搜索)             │  │
│  │        笔记内容 + PDF/Word/Excel 全文索引          │  │
│  └─────────────────────┬───────────────────────────┘  │
│                        │                                 │
│  ┌─────────────────────┴───────────────────────────┐  │
│  │         Qdrant / Meilisearch (向量检索)           │  │
│  │              RAG 知识库向量存储                    │  │
│  └─────────────────────┬───────────────────────────┘  │
│                        │                                 │
│  ┌─────────────────────┴───────────────────────────┐  │
│  │              Redis 7.x (缓存 + 队列)               │  │
│  │         会话缓存 / 限流 / 任务队列                   │  │
│  └─────────────────────┬───────────────────────────┘  │
│                        │                                 │
│  ┌─────────────────────┴───────────────────────────┐  │
│  │           文件存储 (MinIO / 服务器本地)            │  │
│  │      PDF/Word/Excel/图片/附件 / Markdown文件      │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │              AI 服务层                             │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │  │
│  │  │ MiniMax API │  │ Tushare API │  │ 飞书 API  │ │  │
│  │  │  (对话/生成) │  │  (股票数据)  │  │ (推送)    │ │  │
│  │  └─────────────┘  └─────────────┘  └───────────┘ │  │
│  └──────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### 2.2 技术栈选型

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| **Web前端** | React 18 + TypeScript + Vite | 响应式设计，支持所有功能 |
| **桌面端** | Electron 28 | Mac/Windows 统一代码 |
| **移动端** | React Native (Phase 2) | Android App |
| **后端框架** | Node.js + Express / Fastify | 轻量、高性能 |
| **主数据库** | PostgreSQL 15 | 结构化数据存储 |
| **全文搜索** | Elasticsearch 8.x | 笔记/文件全文检索 |
| **向量数据库** | Qdrant | RAG 知识库向量检索 |
| **缓存/队列** | Redis 7.x | 会话缓存、任务队列 |
| **文件存储** | MinIO | S3兼容的对象存储 |
| **AI对话** | MiniMax API | 文字对话、知识整理 |
| **股票数据** | Tushare Pro | A股/港股数据 |
| **消息推送** | 飞书 Webhook | 日程提醒推送 |
| **离线存储** | SQLite (客户端) | 离线笔记缓存 |

### 2.3 目录结构

```
xuezi-kb/
├── client/                      # 前端项目
│   ├── web/                     # Web App
│   │   └── src/
│   │       ├── components/      # 通用组件
│   │       ├── pages/          # 页面
│   │       ├── stores/         # 状态管理 (Zustand)
│   │       ├── hooks/          # 自定义Hook
│   │       ├── services/       # API调用
│   │       ├── utils/          # 工具函数
│   │       └── App.tsx
│   ├── desktop/                 # Electron桌面端
│   │   ├── src/main/           # 主进程
│   │   ├── src/preload/        # 预加载脚本
│   │   └── src/renderer/       # 渲染进程 (复用Web代码)
│   └── mobile/                  # React Native (Phase 2)
│
├── server/                      # 后端项目
│   ├── src/
│   │   ├── routes/             # API路由
│   │   ├── controllers/       # 控制器
│   │   ├── services/          # 业务逻辑
│   │   ├── models/            # 数据模型
│   │   ├── middlewares/       # 中间件
│   │   ├── utils/             # 工具函数
│   │   ├── jobs/              # 定时任务
│   │   └── app.ts
│   ├── prisma/                # Prisma ORM
│   │   └── schema.prisma
│   └── package.json
│
├── shared/                      # 共享类型定义
│   └── types/
│
└── docs/                       # 文档
```

---

## 三、功能模块划分（覆盖全部20个功能）

### 3.1 功能矩阵

| # | 功能 | 模块 | 前端 | 后端 | 数据库 | 优先级 |
|---|------|------|------|------|--------|--------|
| 1 | 笔记（Markdown+富文本） | `note-service` | ✅ | ✅ | ✅ | P0 |
| 2 | 笔记本分类 | `notebook-service` | ✅ | ✅ | ✅ | P0 |
| 3 | 多标签 | `tag-service` | ✅ | ✅ | ✅ | P0 |
| 4 | Excel预览+编辑 | `file-service` | ✅ | ✅ | ✅ | P1 |
| 5 | 思维导图 | `mindmap-service` | ✅ | ✅ | ✅ | P1 |
| 6 | 回收站 | `recycle-service` | ✅ | ✅ | ✅ | P0 |
| 7 | 导入导出 | `import-export-service` | ✅ | ✅ | - | P1 |
| 8 | 语音转文字 | `speech-service` | ✅ | - | - | P2 |
| 9 | 文件预览+搜索 | `file-service` | ✅ | ✅ | ✅ | P1 |
| 10 | AI问答（RAG） | `ai-service` | ✅ | ✅ | ✅ | P1 |
| 11 | 日程提醒+飞书推送 | `schedule-service` | ✅ | ✅ | ✅ | P1 |
| 12 | 知识图谱 | `graph-service` | ✅ | ✅ | ✅ | P1 |
| 13 | 多设备支持 | `sync-service` | ✅ | ✅ | ✅ | P0 |
| 14 | 离线同步 | `sync-service` | ✅ | ✅ | ✅ | P0 |
| 15 | 模板系统 | `template-service` | ✅ | ✅ | ✅ | P0 |
| 16 | 命令面板 | `command-palette` | ✅ | ✅ | - | P1 |
| 17 | 加密笔记 | `crypto-service` | ✅ | ✅ | ✅ | P2 |
| 18 | 专注模式 | `focus-mode` | ✅ | - | - | P1 |
| 19 | 快速便签 | `quick-capture` | ✅ | ✅ | ✅ | P0 |
| 20 | 飞书推送 | `notify-service` | - | ✅ | - | P1 |

### 3.2 模块详细说明

#### 模块1：笔记服务 (`note-service`)
**功能**：笔记的CRUD、富文本编辑、Markdown渲染

**前端实现**：
- Markdown编辑：`@uiw/react-md-editor` 或 `Milkdown`
- 富文本：`TipTap` 或 `Slate`
- 自动保存：debounce 1秒后保存

**后端实现**：
- 笔记 CRUD API
- 版本历史（每次保存记录版本）
- 全文搜索同步到 Elasticsearch

#### 模块2：笔记本服务 (`notebook-service`)
**功能**：笔记本分类管理、层级结构

**数据结构**：
- 树形结构，支持多级嵌套
- 每个笔记本有 `parent_id`
- 排序字段支持拖拽排序

#### 模块3：标签服务 (`tag-service`)
**功能**：多标签支持、标签统计

**数据结构**：
- 笔记-标签多对多关系
- 标签颜色自定义
- 标签分组（可选）

#### 模块4：文件服务 (`file-service`)
**功能**：PDF/Word/Excel 预览 + 全文搜索

**前端实现**：
- PDF：`react-pdf`
- Word：`mammoth.js` (docx → html)
- Excel：`xlsx` 库预览，`ExcelJS` 编辑

**后端实现**：
- 文件上传到 MinIO
- 文本提取：`pdf-parse`、`mammoth`、`xlsx`
- 全文索引到 Elasticsearch

#### 模块5：思维导图服务 (`mindmap-service`)
**功能**：脑图笔记 + 图谱可视化

**前端实现**：
- 使用 `react-xmind` 或 `simple-mind-map`
- 支持导出 PNG/SVG/Markdown

**后端实现**：
- 脑图数据存储为 JSON
- 节点关联到笔记

#### 模块6：回收站服务 (`recycle-service`)
**功能**：软删除、自动清理

**实现**：
- 所有删除操作标记 `deleted_at` 时间戳
- 30天后自动永久删除（定时任务）
- 支持恢复到原位置

#### 模块7：导入导出服务 (`import-export-service`)
**功能**：Obsidian/Notion 迁移

**支持格式**：
- 导入：Obsidian Vault（Markdown文件夹）、Notion Export (JSON)
- 导出：Markdownzip、PDF、Notion JSON

**实现**：
- 大文件异步处理（Redis队列）
- 进度实时推送

#### 模块8：语音服务 (`speech-service`)
**功能**：语音转文字

**实现**：
- Phase 1：依赖输入法自带语音输入
- Phase 2：集成 Web Speech API 或 MiniMax ASR

#### 模块9：AI服务 (`ai-service`)
**功能**：RAG 知识库问答

**RAG流程**：
```
用户问题 → 向量检索(Qdrant) → 上下文组装 → MiniMax对话 → 返回答案
```

**实现细节**：
- 笔记切片：按段落或固定长度（512 tokens）
- 向量化：MiniMax Embedding API
- 检索：Qdrant 余弦相似度 top-k
- 对话：MiniMax Chat API

#### 模块10：日程服务 (`schedule-service`)
**功能**：日程管理 + 定时提醒 → 飞书推送

**实现**：
- 日程列表 API（按日期范围查询）
- 定时任务：每分钟检查是否有待推送日程
- 飞书推送：Webhook 或 飞书机器人

#### 模块11：知识图谱服务 (`graph-service`)
**功能**：交互式图谱 + 自动分类 + 定期清理

**图谱数据**：
- 节点：笔记、标签、文件、概念
- 边：关联关系（引用、共现、父子）

**前端实现**：
- 使用 `react-force-graph` 或 `cytoscape.js`
- 支持缩放、拖拽、筛选

**自动分类**：
- 工作类：笔记含「项目」「储能」「电气」等关键词
- 生活类：含「生活」「旅游」「购物」等
- 股票类：含「股票」「持仓」「行情」等
- 定期清理：每周清理孤立节点（30天无关联）

#### 模块12：同步服务 (`sync-service`)
**功能**：离线写 → 联网自动同步

**同步策略**：
```
本地变更 → 写入本地SQLite → 标记sync_status=pending
                                        ↓
                              检测到网络连接
                                        ↓
                              上传到服务器（冲突检测）
                                        ↓
                              server返回sync_result
                                        ↓
                              更新本地状态
```

**冲突处理**：
- Last-Write-Wins + 合并策略
- 手动解决：显示冲突让用户选择

#### 模块13：模板服务 (`template-service`)
**功能**：会议纪要/项目模板快速套用

**预置模板**：
1. 会议纪要模板
2. 项目启动模板
3. 周报模板
4. 随手记模板

**实现**：
- 模板存储为 Markdown
- 创建笔记时选择模板

#### 模块14：命令面板 (`command-palette`)
**功能**：Ctrl+K 快速搜索和执行命令

**支持命令**：
```
搜索笔记      → 模糊搜索笔记标题/内容
创建笔记      → 新建笔记
创建思维导图  → 新建脑图
切换笔记本    → 快速切换
打开设置      → 跳转设置页
切换主题      → 浅色/深色/跟随系统
```

**前端实现**：
- 使用 `cmdk` 或 `react-aria-components` 的 Command
- 全局监听 `Ctrl+K`

#### 模块15：加密服务 (`crypto-service`)
**功能**：敏感内容加密保护

**实现**：
- AES-256-GCM 加密
- 加密后的笔记内容存储为密文
- 解密密钥由用户密码派生（PBKDF2）
- 解密在客户端完成，服务端不存明文

#### 模块16：专注模式 (`focus-mode`)
**功能**：写作时隐藏干扰

**实现**：
- 前端 CSS 隐藏侧边栏/顶栏
- Zen Mode：全屏编辑，只显示当前段落
- 快捷键 ESC 退出

#### 模块17：快速便签 (`quick-capture`)
**功能**：全局快捷键快速 capture

**桌面端实现**：
- Electron 全局快捷键：`Cmd+Shift+N` (Mac) / `Ctrl+Shift+N` (Win)
- 弹出小型窗口，输入后回车保存
- 自动归档到「便签」笔记本

**Web端实现**：
- 浏览器扩展（Phase 2）

---

## 四、数据库详细设计

### 4.1 ER 图（实体关系）

```
users (1) ───< (N) notebooks (笔记本)
users (1) ───< (N) notes (笔记)
users (1) ───< (N) tags (标签)
users (1) ───< (N) schedules (日程)
users (1) ───< (N) templates (模板)
users (1) ───< (N) files (文件)
users (1) ───< (N) graph_nodes (图谱节点)
users (1) ───< (N) graph_edges (图谱边)
users (1) ───< (N) mindmaps (思维导图)
users (1) ───< (N) encrypted_notes (加密笔记)

notebooks (1) ───< (N) notes (笔记)
tags (N) ───< (N) notes (笔记) [note_tags]
notebooks (1) ───< (N) notebooks (子笔记本)
files (N) ───< (N) notes (笔记) [note_files]
schedules (1) ───< (N) schedule_reminders (日程提醒)
```

### 4.2 数据表详细设计

#### 表1：用户表 `users`

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username        VARCHAR(50) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    email           VARCHAR(100),
    settings        JSONB DEFAULT '{}',
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),
    last_login_at   TIMESTAMP,
    is_deleted      BOOLEAN DEFAULT FALSE
);
```

#### 表2：笔记本表 `notebooks`

```sql
CREATE TABLE notebooks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_id       UUID REFERENCES notebooks(id) ON DELETE CASCADE,
    name            VARCHAR(200) NOT NULL,
    icon            VARCHAR(50) DEFAULT '📁',
    color           VARCHAR(20) DEFAULT '#3B82F6',
    sort_order      INTEGER DEFAULT 0,
    is_default      BOOLEAN DEFAULT FALSE,
    note_count      INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),
    deleted_at      TIMESTAMP,
    sync_status     VARCHAR(20) DEFAULT 'synced',
    sync_version    BIGINT DEFAULT 0
);

CREATE INDEX idx_notebooks_user_id ON notebooks(user_id);
CREATE INDEX idx_notebooks_parent_id ON notebooks(parent_id);
```

#### 表3：笔记表 `notes`

```sql
CREATE TABLE notes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notebook_id    UUID NOT NULL REFERENCES notebooks(id) ON DELETE SET NULL,
    title           VARCHAR(500) NOT NULL,
    content         TEXT,
    content_html    TEXT,
    content_type    VARCHAR(20) DEFAULT 'markdown',
    is_encrypted    BOOLEAN DEFAULT FALSE,
    word_count      INTEGER DEFAULT 0,
    version         BIGINT DEFAULT 1,
    source          VARCHAR(50),
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),
    deleted_at      TIMESTAMP,
    permanent_deleted_at TIMESTAMP,
    sync_status     VARCHAR(20) DEFAULT 'synced',
    sync_version    BIGINT DEFAULT 0,
    search_vector   TSVECTOR
);

CREATE INDEX idx_notes_user_id ON notes(user_id);
CREATE INDEX idx_notes_notebook_id ON notes(notebook_id);
CREATE INDEX idx_notes_deleted_at ON notes(deleted_at);
CREATE INDEX idx_notes_search ON notes USING GIN(search_vector);
```

#### 表4：笔记版本历史 `note_versions`

```sql
CREATE TABLE note_versions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    note_id         UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    version         BIGINT NOT NULL,
    title           VARCHAR(500),
    content         TEXT,
    content_html    TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_note_versions_note_id ON note_versions(note_id);
```

#### 表5：标签表 `tags`

```sql
CREATE TABLE tags (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL,
    color           VARCHAR(20) DEFAULT '#6B7280',
    icon            VARCHAR(50),
    note_count      INTEGER DEFAULT 0,
    sort_order      INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),
    deleted_at      TIMESTAMP,
    sync_status     VARCHAR(20) DEFAULT 'synced',
    UNIQUE(user_id, name)
);

CREATE INDEX idx_tags_user_id ON tags(user_id);
```

#### 表6：笔记-标签关联表 `note_tags`

```sql
CREATE TABLE note_tags (
    note_id         UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    tag_id          UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at      TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (note_id, tag_id)
);
```

#### 表7：文件表 `files`

```sql
CREATE TABLE files (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    note_id         UUID REFERENCES notes(id) ON DELETE SET NULL,
    original_name   VARCHAR(500) NOT NULL,
    stored_name     VARCHAR(500) NOT NULL,
    file_path       VARCHAR(1000) NOT NULL,
    file_size       BIGINT NOT NULL,
    mime_type       VARCHAR(100) NOT NULL,
    file_ext        VARCHAR(20) NOT NULL,
    thumbnail_path  VARCHAR(500),
    text_content    TEXT,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),
    deleted_at      TIMESTAMP,
    sync_status     VARCHAR(20) DEFAULT 'synced'
);

CREATE INDEX idx_files_user_id ON files(user_id);
CREATE INDEX idx_files_note_id ON files(note_id);
CREATE INDEX idx_files_deleted_at ON files(deleted_at);
```

#### 表8：思维导图表 `mindmaps`

```sql
CREATE TABLE mindmaps (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    note_id         UUID REFERENCES notes(id) ON DELETE SET NULL,
    title           VARCHAR(500) NOT NULL,
    data            JSONB NOT NULL DEFAULT '{}',
    theme           VARCHAR(50) DEFAULT 'default',
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),
    deleted_at      TIMESTAMP,
    sync_status     VARCHAR(20) DEFAULT 'synced'
);
```

#### 表9：日程表 `schedules`

```sql
CREATE TABLE schedules (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title           VARCHAR(500) NOT NULL,
    description     TEXT,
    start_time      TIMESTAMP NOT NULL,
    end_time        TIMESTAMP,
    all_day         BOOLEAN DEFAULT FALSE,
    location        VARCHAR(500),
    color           VARCHAR(20) DEFAULT '#3B82F6',
    repeat_type     VARCHAR(20) DEFAULT 'none',
    repeat_end_date TIMESTAMP,
    status          VARCHAR(20) DEFAULT 'pending',
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),
    deleted_at      TIMESTAMP,
    sync_status     VARCHAR(20) DEFAULT 'synced'
);

CREATE INDEX idx_schedules_user_id ON schedules(user_id);
CREATE INDEX idx_schedules_start_time ON schedules(start_time);
```

#### 表10：日程提醒表 `schedule_reminders`

```sql
CREATE TABLE schedule_reminders (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_id     UUID NOT NULL REFERENCES schedules(id) ON DELETE CASCADE,
    remind_at       TIMESTAMP NOT NULL,
    remind_type     VARCHAR(20) DEFAULT 'feishu',
    is_sent         BOOLEAN DEFAULT FALSE,
    sent_at         TIMESTAMP,
    error_message   TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reminders_remind_at ON schedule_reminders(remind_at);
CREATE INDEX idx_reminders_is_sent ON schedule_reminders(is_sent);
```

#### 表11：模板表 `templates`

```sql
CREATE TABLE templates (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            VARCHAR(200) NOT NULL,
    description     VARCHAR(500),
    icon            VARCHAR(50) DEFAULT '📄',
    category        VARCHAR(50) DEFAULT 'general',
    content         TEXT NOT NULL,
    variables       JSONB DEFAULT '[]',
    is_builtin      BOOLEAN DEFAULT FALSE,
    use_count       INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),
    deleted_at      TIMESTAMP,
    sync_status     VARCHAR(20) DEFAULT 'synced',
    UNIQUE(user_id, name)
);
```

#### 表12：图谱节点表 `graph_nodes`

```sql
CREATE TABLE graph_nodes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    node_type       VARCHAR(50) NOT NULL,
    node_id         UUID NOT NULL,
    label           VARCHAR(500) NOT NULL,
    category        VARCHAR(50) DEFAULT 'uncategorized',
    properties      JSONB DEFAULT '{}',
    position_x      FLOAT,
    position_y      FLOAT,
    is_pinned       BOOLEAN DEFAULT FALSE,
    access_count    INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),
    deleted_at      TIMESTAMP,
    UNIQUE(user_id, node_type, node_id)
);

CREATE INDEX idx_graph_nodes_user_id ON graph_nodes(user_id);
CREATE INDEX idx_graph_nodes_category ON graph_nodes(category);
```

#### 表13：图谱边表 `graph_edges`

```sql
CREATE TABLE graph_edges (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_node_id  UUID NOT NULL REFERENCES graph_nodes(id) ON DELETE CASCADE,
    target_node_id  UUID NOT NULL REFERENCES graph_nodes(id) ON DELETE CASCADE,
    edge_type       VARCHAR(50) NOT NULL,
    weight          FLOAT DEFAULT 1.0,
    properties      JSONB DEFAULT '{}',
    created_at      TIMESTAMP DEFAULT NOW(),
    deleted_at      TIMESTAMP,
    UNIQUE(user_id, source_node_id, target_node_id, edge_type)
);
```

#### 表14：RAG向量表 `rag_vectors`

```sql
CREATE TABLE rag_vectors (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chunk_id        VARCHAR(100) NOT NULL,
    note_id         UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    chunk_text      TEXT NOT NULL,
    qdrant_id       VARCHAR(100),
    token_count     INTEGER,
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, chunk_id)
);

CREATE INDEX idx_rag_vectors_user_id ON rag_vectors(user_id);
CREATE INDEX idx_rag_vectors_note_id ON rag_vectors(note_id);
```

#### 表15：加密笔记表 `encrypted_notes`

```sql
CREATE TABLE encrypted_notes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    note_id         UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    encrypted_content TEXT NOT NULL,
    iv              VARCHAR(50) NOT NULL,
    salt            VARCHAR(50) NOT NULL,
    key_version     INTEGER DEFAULT 1,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, note_id)
);
```

#### 表16：便签表 `quick_captures`

```sql
CREATE TABLE quick_captures (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content         TEXT NOT NULL,
    source          VARCHAR(50) DEFAULT 'desktop',
    target_notebook_id UUID REFERENCES notebooks(id) ON DELETE SET NULL,
    status          VARCHAR(20) DEFAULT 'pending',
    note_id         UUID REFERENCES notes(id) ON DELETE SET NULL,
    created_at      TIMESTAMP DEFAULT NOW(),
    processed_at    TIMESTAMP
);

CREATE INDEX idx_quick_captures_user_status ON quick_captures(user_id, status);
```

#### 表17：导入导出任务表 `import_export_tasks`

```sql
CREATE TABLE import_export_tasks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_type       VARCHAR(20) NOT NULL,
    source_format   VARCHAR(50),
    target_format   VARCHAR(50),
    file_path       VARCHAR(1000),
    status          VARCHAR(20) DEFAULT 'pending',
    progress        INTEGER DEFAULT 0,
    total_items     INTEGER,
    processed_items INTEGER,
    error_message   TEXT,
    metadata        JSONB,
    created_at      TIMESTAMP DEFAULT NOW(),
    completed_at    TIMESTAMP
);
```

#### 表18：同步记录表 `sync_records`

```sql
CREATE TABLE sync_records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_id       VARCHAR(100) NOT NULL,
    entity_type     VARCHAR(50) NOT NULL,
    entity_id       UUID NOT NULL,
    action          VARCHAR(20) NOT NULL,
    payload         JSONB,
    client_version  BIGINT,
    server_version  BIGINT,
    conflict_resolved BOOLEAN DEFAULT FALSE,
    conflict_data   JSONB,
    synced_at       TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, entity_type, entity_id, action, client_version)
);

CREATE INDEX idx_sync_records_entity ON sync_records(user_id, entity_type, entity_id);
```

---

## 五、API接口设计

### 5.1 认证相关

#### POST /api/auth/register
注册用户
```json
// Request
{ "username": "xuezi", "password": "xxx", "email": "xuezi@xxx.com" }

// Response 201
{ "id": "uuid", "username": "xuezi", "token": "jwt..." }
```

#### POST /api/auth/login
用户登录
```json
// Request
{ "username": "xuezi", "password": "xxx" }

// Response 200
{ "id": "uuid", "username": "xuezi", "token": "jwt...", "settings": {} }
```

### 5.2 笔记本

#### GET /api/notebooks
获取笔记本列表（树形结构）
```json
// Response 200
{
  "notebooks": [
    {
      "id": "uuid",
      "name": "工作",
      "icon": "💼",
      "children": [
        { "id": "uuid", "name": "储能项目", "parent_id": "uuid", ... }
      ]
    }
  ]
}
```

#### POST /api/notebooks
创建笔记本
```json
// Request
{ "name": "新笔记本", "parent_id": "uuid|null", "icon": "📁", "color": "#3B82F6" }

// Response 201
{ "id": "uuid", "name": "新笔记本", ... }
```

#### PATCH /api/notebooks/:id
更新笔记本
```json
// Request
{ "name": "新名称", "parent_id": "uuid", "sort_order": 1 }

// Response 200
{ "id": "uuid", ... }
```

#### DELETE /api/notebooks/:id
删除笔记本（软删除）

### 5.3 笔记

#### GET /api/notes
获取笔记列表
```json
// Query: ?notebook_id=xxx&tag_ids=id1,id2&deleted=true&page=1&limit=20

// Response 200
{
  "notes": [...],
  "total": 100,
  "page": 1,
  "limit": 20
}
```

#### GET /api/notes/:id
获取单条笔记
```json
// Response 200
{
  "id": "uuid",
  "title": "会议纪要",
  "content": "# 标题\n...",
  "content_html": "<h1>标题</h1>...",
  "notebook_id": "uuid",
  "tags": [{"id": "uuid", "name": "工作", "color": "#3B82F6"}],
  "version": 5,
  "created_at": "2026-04-03T10:00:00Z",
  "updated_at": "2026-04-03T11:00:00Z"
}
```

#### POST /api/notes
创建笔记
```json
// Request
{
  "title": "新笔记",
  "content": "# 标题\n...",
  "content_type": "markdown",
  "notebook_id": "uuid",
  "tag_ids": ["uuid1", "uuid2"]
}

// Response 201
{ "id": "uuid", ... }
```

#### PATCH /api/notes/:id
更新笔记（自动保存，每1秒调用）
```json
// Request
{ "title": "新标题", "content": "...", "version": 4 }

// Response 200
// version冲突时返回409 Conflict
{ "error": "version_conflict", "server_version": 5 }
```

#### DELETE /api/notes/:id
删除笔记（软删除到回收站）

#### POST /api/notes/:id/restore
从回收站恢复

#### DELETE /api/notes/:id/permanent
永久删除

#### GET /api/notes/deleted
获取回收站笔记

### 5.4 标签

#### GET /api/tags
获取标签列表
```json
// Response 200
{ "tags": [{ "id": "uuid", "name": "工作", "color": "#3B82F6", "note_count": 10 }] }
```

#### POST /api/tags
创建标签
```json
// Request
{ "name": "新标签", "color": "#FF5733" }

// Response 201
```

#### PATCH /api/tags/:id
更新标签

#### DELETE /api/tags/:id
删除标签

### 5.5 文件

#### POST /api/files/upload
上传文件（multipart/form-data）
```json
// Response 201
{
  "id": "uuid",
  "original_name": "报告.pdf",
  "file_size": 1024000,
  "mime_type": "application/pdf"
}
```

#### GET /api/files/:id
下载/预览文件

#### GET /api/files/:id/text
获取文件文本内容（用于搜索）
```json
// Response 200
{ "text_content": "PDF/Word/Excel的文本内容..." }
```

#### DELETE /api/files/:id
删除文件

### 5.6 思维导图

#### GET /api/mindmaps
获取思维导图列表

#### GET /api/mindmaps/:id
获取思维导图详情
```json
// Response 200
{
  "id": "uuid",
  "title": "项目规划",
  "data": {
    "root": { "id": "root", "text": "项目规划", "children": [...] },
    ...
  },
  "theme": "default"
}
```

#### POST /api/mindmaps
创建思维导图
```json
// Request
{ "title": "新脑图", "notebook_id": "uuid
#### POST /api/mindmaps
创建思维导图
```json
// Request
{ "title": "新脑图", "notebook_id": "uuid", "data": {} }

// Response 201
{ "id": "uuid", "title": "新脑图", "data": {...} }
```

#### PATCH /api/mindmaps/:id
更新思维导图
```json
// Request
{ "title": "新标题", "data": {...}, "theme": "dark" }

// Response 200
```

#### DELETE /api/mindmaps/:id
删除思维导图

### 5.7 日程

#### GET /api/schedules
获取日程列表
```json
// Query: ?start=2026-04-01&end=2026-04-30&status=pending

// Response 200
{
  "schedules": [
    {
      "id": "uuid",
      "title": "团队会议",
      "start_time": "2026-04-03T14:00:00Z",
      "end_time": "2026-04-03T15:00:00Z",
      "all_day": false,
      "repeat_type": "weekly",
      "reminders": [{"id": "uuid", "remind_at": "...", "remind_type": "feishu"}]
    }
  ]
}
```

#### POST /api/schedules
创建日程
```json
// Request
{
  "title": "团队会议",
  "start_time": "2026-04-03T14:00:00Z",
  "end_time": "2026-04-03T15:00:00Z",
  "reminders": [
    { "remind_at": "2026-04-03T13:00:00Z", "remind_type": "feishu" }
  ]
}

// Response 201
```

#### PATCH /api/schedules/:id
更新日程

#### DELETE /api/schedules/:id
删除日程

### 5.8 模板

#### GET /api/templates
获取模板列表
```json
// Response 200
{
  "templates": [
    {
      "id": "uuid",
      "name": "会议纪要",
      "icon": "📝",
      "category": "meeting",
      "is_builtin": true
    }
  ]
}
```

#### POST /api/templates
创建模板
```json
// Request
{
  "name": "我的模板",
  "content": "# {{title}}\n\n## 基本信息\n日期：{{date}}\n\n## 内容\n{{content}}",
  "variables": [
    {"name": "{{title}}", "label": "标题", "type": "text"},
    {"name": "{{date}}", "label": "日期", "type": "date"}
  ]
}

// Response 201
```

#### POST /api/templates/:id/use
使用模板创建笔记
```json
// Request
{ "variables": { "title": "4月储能项目会议", "date": "2026-04-03" } }

// Response 201
// 返回创建的笔记
{ "id": "uuid", "title": "4月储能项目会议", ... }
```

### 5.9 知识图谱

#### GET /api/graph/nodes
获取图谱节点
```json
// Query: ?category=work&node_type=note

// Response 200
{
  "nodes": [
    { "id": "uuid", "node_type": "note", "node_id": "uuid", "label": "储能项目", "category": "work", "x": 100, "y": 200 }
  ]
}
```

#### GET /api/graph/edges
获取图谱边
```json
// Response 200
{ "edges": [...] }
```

#### PATCH /api/graph/nodes/:id
更新节点（位置、分类）
```json
// Request
{ "position_x": 150, "position_y": 250, "category": "work", "is_pinned": true }
```

#### POST /api/graph/build
触发图谱重建（从笔记/标签生成节点和边）
```json
// Response 202
{ "job_id": "uuid", "status": "processing" }
```

### 5.10 AI问答（RAG）

#### POST /api/ai/chat
RAG对话
```json
// Request
{
  "question": "储能项目的收益如何计算？",
  "history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "top_k": 5
}

// Response 200
{
  "answer": "根据你的笔记，储能项目的收益主要包括...",
  "sources": [
    { "note_id": "uuid", "title": "储能项目笔记", "chunk": "...相关段落...", "score": 0.92 }
  ],
  "model_used": "MiniMax-M2.7"
}
```

#### POST /api/ai/embedding
手动触发笔记向量化（用于重建索引）
```json
// Request
{ "note_ids": ["uuid1", "uuid2"] } // 空数组=全部重建

// Response 202
{ "job_id": "uuid", "status": "processing" }
```

### 5.11 加密笔记

#### POST /api/notes/:id/encrypt
加密笔记
```json
// Request
{ "password": "用户密码" }

// Response 200
// 加密后笔记content被替换为密文标记，原始内容存入encrypted_notes表
{ "id": "uuid", "is_encrypted": true }
```

#### POST /api/notes/:id/decrypt
解密笔记（客户端解密，服务端不接触明文）
```json
// Request
{ "password": "用户密码" }

// Response 200
{ "content": "解密后的原始内容..." }
```

### 5.12 快速便签

#### POST /api/captures
快速创建便签
```json
// Request
{ "content": "下午要联系王总", "source": "desktop" }

// Response 201
{ "id": "uuid", "status": "pending" }
```

#### POST /api/captures/:id/process
处理便签（转为正式笔记或归档）
```json
// Request
{ "action": "convert", "notebook_id": "uuid", "title": "联系王总" }

// Response 200
{ "note_id": "uuid", "status": "processed" }
```

### 5.13 导入导出

#### POST /api/import/obsidian
导入Obsidian Vault
```json
// Request (multipart/form-data)
// file: zip文件或文件夹

// Response 202
{ "task_id": "uuid", "status": "processing", "progress": 0 }
```

#### GET /api/import/:taskId/status
获取导入进度
```json
// Response 200
{ "progress": 50, "processed_items": 25, "total_items": 50, "status": "processing" }
```

#### POST /api/export
导出笔记
```json
// Request
{
  "format": "markdown_zip",
  "note_ids": ["uuid1", "uuid2"], // 空=全部
  "notebook_ids": ["uuid"]
}

// Response 202
{ "task_id": "uuid", "status": "processing" }
```

#### GET /api/export/:taskId/download
下载导出文件
```json
// Response 200 (application/zip)
```

### 5.14 同步

#### POST /api/sync/push
推送本地变更到服务器
```json
// Request
{
  "device_id": "mac-mini-001",
  "changes": [
    {
      "entity_type": "note",
      "entity_id": "uuid",
      "action": "update",
      "payload": { "title": "新标题", "content": "..." },
      "client_version": 5,
      "base_sync_version": 3
    }
  ]
}

// Response 200
{
  "results": [
    { "entity_id": "uuid", "status": "ok", "server_version": 6 }
  ],
  "conflicts": [
    { "entity_id": "uuid", "client_version": 5, "server_version": 7, "server_data": {...} }
  ]
}
```

#### GET /api/sync/pull
拉取服务器变更
```json
// Query: ?since_sync_version=3&device_id=mac-mini-001

// Response 200
{
  "changes": [
    { "entity_type": "note", "entity_id": "uuid", "action": "update", "payload": {...}, "server_version": 7 }
  ],
  "latest_sync_version": 7
}
```

### 5.15 命令面板（后端搜索）

#### GET /api/commands/search
全局搜索
```json
// Query: ?q=储能&types=notes,files,mindmaps&limit=20

// Response 200
{
  "results": [
    { "type": "note", "id": "uuid", "title": "储能项目笔记", "snippet": "...储能收益计算...", "score": 0.95 },
    { "type": "file", "id": "uuid", "title": "储能方案.pdf", "score": 0.80 }
  ]
}
```

---

## 六、开发路线图

### Phase 1：核心基础（8-10周）

**目标**：完成最小可用产品（MVP）

| 周次 | 模块 | 交付物 |
|------|------|--------|
| Week 1-2 | 项目搭建 | 前后端项目骨架、CI/CD、数据库初始化脚本 |
| Week 3-4 | 笔记本+笔记 | CRUD API、Web端笔记本树、笔记编辑器（Markdown） |
| Week 5 | 标签+搜索 | 标签管理、全文搜索（PostgreSQL TSVECTOR） |
| Week 6 | 回收站+版本 | 软删除、自动清理、笔记版本历史 |
| Week 7 | 模板系统 | 预置模板、Web端模板选择器 |
| Week 8 | 命令面板 | Ctrl+K 搜索、快捷命令 |
| Week 9 | 快速便签 | Electron全局快捷键、便签窗口 |
| Week 10 | 同步服务 | 离线SQLite、增量同步、冲突处理 |
| Week 11-12 | 专注模式+主题 | 专注模式、浅/深色主题 |
| Week 12 | 桌面端打包 | Mac/Windows安装包 |

**Phase 1 交付功能**：
- ✅ 笔记（Markdown）
- ✅ 笔记本分类
- ✅ 多标签
- ✅ 回收站
- ✅ 模板系统
- ✅ 命令面板
- ✅ 快速便签
- ✅ 多设备支持 + 离线同步
- ✅ 专注模式
- ✅ 桌面端（Mac/Windows）

### Phase 2：知识增强（6-8周）

**目标**：AI赋能 + 知识图谱

| 周次 | 模块 | 交付物 |
|------|------|--------|
| Week 13-14 | 文件管理 | 文件上传/预览、PDF全文提取、Excel预览 |
| Week 15 | 思维导图 | 脑图编辑器、导出PNG/SVG |
| Week 16-17 | RAG AI | 向量索引、问答界面、上下文组装 |
| Week 18 | 知识图谱 | 图谱可视化、自动分类、定期清理 |
| Week 19 | 导入导出 | Obsidian导入、Markdown/JSON导出 |
| Week 20 | 日程管理 | 日程CRUD、定时任务、飞书推送 |

**Phase 2 交付功能**：
- ✅ Excel预览+编辑
- ✅ 思维导图
- ✅ 导入导出（Obsidian/Notion）
- ✅ AI问答（RAG）
- ✅ 日程+飞书推送
- ✅ 知识图谱
- ✅ PDF/Word预览+全文搜索

### Phase 3：移动端+加密（4-6周）

**目标**：移动支持 + 安全加固

| 周次 | 模块 | 交付物 |
|------|------|--------|
| Week 21-22 | Android App | React Native App、基本功能 |
| Week 23 | 加密笔记 | AES-256加密/解密、密码保护 |
| Week 24 | 语音输入 | Web Speech API集成、输入法语音 |
| Week 25-26 | 优化打磨 | 性能优化、bug修复、用户体验 |

**Phase 3 交付功能**：
- ✅ Android App
- ✅ 加密笔记
- ✅ 语音转文字
- ✅ 性能优化

---

## 七、部署方案

### 7.1 服务器资源

| 服务 | 规格 | 说明 |
|------|------|------|
| 腾讯云服务器 | 2核4G 50G SSD | 主应用服务器 |
| 数据盘 | 500G CBS | 文件存储 + MinIO |
| 数据库 | PostgreSQL 15（自建） | 暂不迁移云数据库 |

### 7.2 Docker 部署架构

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
      - /data/www:/usr/share/nginx/html
    depends_on:
      - api
    restart: always

  # API 服务
  api:
    build: ./server
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://xuezi:xxx@db:5432/xuezikb
      - REDIS_URL=redis://redis:6379
      - MINIO_ENDPOINT=minio:9000
    depends_on:
      - db
      - redis
      - minio
    restart: always

  # PostgreSQL
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=xuezi
      - POSTGRES_PASSWORD=xxx
      - POSTGRES_DB=xuezikb
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: always

  # Redis
  redis:
    image: redis:7-alpine
    volumes:
      - redisdata:/data
    restart: always

  # MinIO 对象存储
  minio:
    image: minio/minio
    environment:
      - MINIO_ROOT_USER=xuezi
      - MINIO_ROOT_PASSWORD=xxx
    command: server /data --console-address ":9001"
    volumes:
      - miniodata:/data
    restart: always

  # Elasticsearch (可选，Phase 2)
  # elasticsearch:
  #   image: elasticsearch:8.12.0
  #   environment:
  #     - discovery.type=single-node
  #     - ES_JAVA_OPTS=-Xms1g -Xmx1g
  #   volumes:
  #     - esdata:/usr/share/elasticsearch/data

  # Qdrant 向量数据库 (Phase 2)
  # qdrant:
  #   image: qdrant/qdrant
  #   volumes:
  #     - qdrantdata:/qdrant/storage

volumes:
  pgdata:
  redisdata:
  miniodata:
  # esdata:
  # qdrantdata:
```

### 7.3 Nginx 配置

```nginx
# /etc/nginx/nginx.conf

worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    keepalive_timeout 65;
    client_max_body_size 100m;  # 大文件上传

    # Gzip 压缩
    gzip on;
    gzip_types text/plain application/javascript application/json text/css image/svg+xml;

    upstream api {
        server 127.0.0.1:3000;
        keepalive 32;
    }

    server {
        listen 80;
        server_name 106.54.25.161;

        # 重定向到 HTTPS（配置证书后启用）
        # return 301 https://$server_name$request_uri;

        # 静态资源
        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;
        }

        # API 代理
        location /api {
            proxy_pass http://api;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket 支持（如需要）
            proxy_ws_route on;
        }

        # 文件上传代理（大文件）
        location /api/files/upload {
            proxy_pass http://api;
            client_max_body_size 500m;
            proxy_read_timeout 300s;
        }

        # 静态文件下载
        location /files {
            alias /data/files;
            internal;  # 仅内部访问
        }
    }
}
```

### 7.4 环境变量配置

```bash
# server/.env.production

# 应用
NODE_ENV=production
PORT=3000
API_BASE_URL=https://106.54.25.161/api

# 数据库
DATABASE_URL=postgresql://xuezi:密码@127.0.0.1:5432/xuezikb
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://127.0.0.1:6379

# JWT
JWT_SECRET=随机生成64位密钥
JWT_EXPIRES_IN=30d

# MinIO
MINIO_ENDPOINT=127.0.0.1:9000
MINIO_ACCESS_KEY=xxx
MINIO_SECRET_KEY=xxx
MINIO_BUCKET=xuezikb-files
MINIO_USE_SSL=false

# AI 服务
MINIMAX_API_KEY=sk-cp-xxx
MINIMAX_API_BASE=https://api.minimaxi.com/v1

# 飞书推送
FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/xxx

# 股票数据
TUSHARE_TOKEN=d8d89556f8638c1d83426b6038fc04ea96b5da04841a07d99706f10027f3

# 邮件（可选）
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USER=xxx@qq.com
SMTP_PASS=xxx
```

### 7.5 部署步骤

```bash
# 1. 服务器初始化
ssh root@106.54.25.161
apt update && apt upgrade -y
apt install -y docker.io docker-compose nginx certbot

# 2. 创建数据目录
mkdir -p /data/{www,files,logs}
chmod 755 /data

# 3. 配置 SSL 证书（Let's Encrypt）
certbot --nginx -d 你的域名

# 4. 上传代码
git clone https://github.com/zhao-rui123/xuezi-kb.git /opt/xuezi-kb
cd /opt/xuezi-kb

# 5. 初始化数据库
docker-compose up -d db
sleep 5
docker-compose exec db psql -U xuezi -d xuezikb -f /docker-entrypoint-initdb.d/init.sql

# 6. 启动所有服务
docker-compose up -d

# 7. 初始化数据（预置模板等）
docker-compose exec api npm run db:seed

# 8. 配置 Nginx
cp deploy/nginx.conf /etc/nginx/nginx.conf
nginx -t
systemctl reload nginx

# 9. 配置定时任务（回收站清理、向量重建）
# crontab -e
# 0 2 * * * docker-compose -f /opt/xuezi-kb/docker-compose.yml exec api npm run jobs:cleanup
# 0 3 * * 0 docker-compose -f /opt/xuezi-kb/docker-compose.yml exec api npm run jobs:rebuild-vectors
```

### 7.6 数据库备份

```bash
# 每日凌晨3点自动备份
# crontab -e
0 3 * * * pg_dump -U xuezi -d xuezikb | gzip > /data/backup/xuezikb_$(date +\%Y\%m\%d).sql.gz

# 保留最近30天
0 3 * * * find /data/backup -name "xuezikb_*.sql.gz" -mtime +30 -delete
```

---

## 八、关键实现细节

### 8.1 RAG 向量化流程

```
1. 用户创建/更新笔记
         ↓
2. 后端检测到笔记变更
         ↓
3. 切片处理：
   - 按段落分割（保留语义完整性）
   - 每片 512 tokens，overlap 50 tokens
         ↓
4. 调用 MiniMax Embedding API
   POST https://api.minimaxi.com/v1/embeddings
   {
     "model": "embo-01",
     "input": "切片文本..."
   }
         ↓
5. 存储到 Qdrant
   - collection: xuezikb_user_{user_id}
   - payload: { note_id, chunk_text, chunk_index }
         ↓
6. 同时更新 PostgreSQL rag_vectors 表
```

### 8.2 知识图谱自动生成

```
触发时机：
1. 用户创建/更新笔记时（异步）
2. 每日凌晨定时任务（增量更新）
3. 手动触发（用户操作）

生成流程：
1. 提取笔记中的关键词（TF-IDF / AI提取）
2. 提取笔记间的引用关系（[[双链]]语法）
3. 生成节点：
   - 笔记节点（来自 notes 表）
   - 标签节点（来自 tags 表）
   - 文件节点（来自 files 表）
4. 生成边：
   - 同一笔记本 → parent_child 边
   - 共现标签 → co_occurs 边（权重=共现次数）
   - 笔记引用 → references 边
5. 自动分类：
   - 关键词匹配规则（如「储能」「电气」→ work）
   - 用户手动调整
6. 清理孤立节点（30天无关联）
```

### 8.3 飞书推送实现

```javascript
// server/src/services/notify.service.ts

async function sendFeishuReminder(schedule: Schedule, user: User) {
  const webhook = user.settings.feishuWebhook;
  if (!webhook) return;

  const message = {
    msg_type: 'interactive',
    card: {
      header: {
        title: { tag: 'plain_text', content: `📅 ${schedule.title}` },
        template: 'blue'
      },
      elements: [
        {
          tag: 'div',
          text: {
            tag: 'lark_md',
            content: `**时间**：${formatDateTime(schedule.start_time)}`
          }
        },
        ...(schedule.description ? [{
          tag: 'div',
          text: { tag: 'lark_md', content: schedule.description }
        }] : []),
        {
          tag: 'action',
          actions: [
            {
              tag: 'button',
              text: { tag: 'plain_text', content: '查看详情' },
              type: 'primary',
              url: `${WEB_APP_URL}/schedule/${schedule.id}`
            }
          ]
        }
      ]
    }
  };

  await axios.post(webhook, message);
}
```

### 8.4 离线同步冲突处理

```javascript
// 冲突检测算法
async function resolveConflict(localChange, serverData, entityType) {
  const localVersion = localChange.client_version;
  const serverVersion = serverData.sync_version;

  // 场景1：无冲突（本地版本 <= 服务器最新版本，说明本地是旧数据）
  if (localVersion >= serverVersion) {
    return { action: 'accept_local', server_version: localVersion + 1 };
  }

  // 场景2：有冲突（本地基于旧版本修改，服务器有新版本）
  // 策略：字段级别合并 + 人工介入

  // 自动合并：只看修改时间戳
  if (entityType === 'notebook') {
    // 笔记本：通常只改name，用最新修改
    const merged = {
      ...serverData,
      name: new Date(localChange.updated_at) > new Date(serverData.updated_at)
        ? localChange.name
        : serverData.name
    };
    return { action: 'merge', merged_data: merged };
  }

  // 笔记：返回冲突数据，让用户手动选择
  return {
    action: 'conflict',
    conflict_data: {
      local: localChange,
      server: serverData
    }
  };
}
```

---

## 九、测试策略

### 9.1 单元测试

```bash
# API 路由测试
npm run test:api

# 服务层测试
npm run test:service

# 覆盖率要求 > 80%
```

### 9.2 E2E 测试

```bash
# 使用 Playwright
npm run test:e2e

# 覆盖关键流程：
# 1. 注册 → 登录 → 创建笔记本 → 创建笔记
# 2. 上传文件 → 预览 → 全文搜索
# 3. 创建日程 → 定时提醒 → 飞书推送
# 4. 离线创建笔记 → 联网同步 → 冲突解决
```

---

## 十、安全考虑

### 10.1 认证与授权
- JWT Token：30天有效期，支持 refresh token 续期
- 密码：PBKDF2 + salt 存储（10万轮）
- 敏感操作（删除数据）需要二次确认

### 10.2 数据安全
- 加密笔记：AES-256-GCM，密钥不存储在服务端
- 传输：全站 HTTPS
- 文件：MinIO 私有桶，不公开访问

### 10.3 防注入
- SQL：使用 Prisma ORM 参数化查询
- XSS：React 自动转义，DOMPurify 清理富文本

---

*文档完*
