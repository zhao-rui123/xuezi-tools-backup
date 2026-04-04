# 雪子知识库 - 独立客户端版 架构设计 v4

> 文档版本：v4.0（修正版）
> 作者：雪子助手
> 日期：2026-04-03
> 状态：**架构设计稿**

## ⚠️ 与v3的关键差异
| 对比项 | v3（错误版） | v4（修正版） |
|--------|-------------|-------------|
| 知识图谱 | ❌ 砍掉 | ✅ 保留，通过API调用 |
| 日程管理+飞书推送 | ❌ 砍掉 | ✅ 保留，通过API调用 |
| 文件预览(PDF/Word/Excel) | ❌ 砍掉 | ✅ 保留，通过API调用 |
| 思维导图 | ❌ 砍掉 | ✅ 保留，通过API调用 |
| 模板系统 | ❌ 砍掉 | ✅ 保留，通过API调用 |
| 加密笔记 | ❌ 砍掉 | ✅ 保留，通过API调用 |
| AI RAG问答 | ❌ 砍掉 | ✅ 保留，通过API调用 |

**原则：客户端不重复造轮子，所有功能通过调用后端API实现。客户端只做本地离线缓存+同步。**

---

## 一、项目定位

### 1.1 核心变化（vs v2网页版）
| 对比项 | v2（旧） | v4（新版） |
|--------|---------|-----------|
| 客户端 | Web（加载外部网页） | **独立客户端，无Web** |
| 离线能力 | 弱（依赖服务器） | **强（本地SQLite优先）** |
| 网页版 | ✅ 有 | ❌ **砍掉** |
| 后端API | 所有功能 | **所有功能不变，客户端直接调用** |

### 1.2 产品定位
- **产品名称**：雪子知识库（XueziKB）v4
- **核心定位**：离线优先 + 全功能API调用
- **目标用户**：雪子
- **客户端**：Windows桌面端 + Android手机端
- **后端**：不变（所有已实现功能继续可用）

---

## 二、系统架构图

### 2.1 整体架构

```
┌──────────────────────────────────────────────────────────────┐
│                        用户设备层                              │
├────────────────────────────┬─────────────────────────────────┤
│    Windows PC              │       Android 手机              │
│ ┌────────────────────┐     │   ┌────────────────────┐        │
│ │ Electron App       │     │   │ React Native App  │        │
│ │ (自带React UI)      │     │   │ (Expo SDK)        │        │
│ │                    │     │   │                   │        │
│ │ 本地SQLite优先      │     │   │ 本地SQLite优先     │        │
│ │ 联网同步至后端API   │     │   │ 联网同步至后端API  │        │
│ │                    │     │   │                   │        │
│ │ 调用所有后端API:    │     │   │ 调用所有后端API:   │        │
│ │ - 笔记/笔记本/标签  │     │   │ - 笔记/笔记本/标签 │        │
│ │ - 知识图谱          │     │   │ - 知识图谱         │        │
│ │ - 日程+飞书推送     │     │   │ - 日程+飞书推送    │        │
│ │ - 文件预览          │     │   │ - 文件预览         │        │
│ │ - 思维导图          │     │   │ - 思维导图         │        │
│ │ - 模板系统          │     │   │ - 模板系统         │        │
│ │ - 加密笔记          │     │   │ - 加密笔记(桌面端) │        │
│ │ - AI RAG问答        │     │   │ - AI RAG问答      │        │
│ │ - 导入导出          │     │   │ - 导入导出        │        │
│ │ - 快速便签          │     │   │ - 快速便签        │        │
│ └────────────────────┘     │   └────────────────────┘        │
│           ↕ 联网同步+API调用            ↕ 联网同步+API调用     │
└────────────┼───────────────┴──────────────┼──────────────────┘
             │                                │
             │   HTTPS REST API               │
             │   WSS (实时)                   │
             │                                │
┌────────────▼────────────────────────────────▼──────────────────┐
│                      腾讯云服务器 (106.54.25.161)                  │
│                  所有后端API不变，继续服务                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Nginx (反向代理 + SSL)                          │ │
│  └──────────────────────────┬───────────────────────────────────┘ │
│                             │                                     │
│  ┌──────────────────────────▼───────────────────────────────────┐ │
│  │                    API 网关 (Node.js)                          │ │
│  │              JWT认证 / 限流 / 请求路由                          │ │
│  └─┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬──────┘ │
│    │    │    │    │    │    │    │    │    │    │    │           │
│ ┌──┴──┐┌┴───┐┌┴───┐┌┴───┐┌┴───┐┌┴───┐┌┴───┐┌┴───┐┌┴───┐┌┴───┐ │
│ │笔记  ││笔记本│ │标签  ││便签  ││AI   ││图谱  ││日程 ││文件 ││模板 │ │
│ │CRUD ││CRUD │ │CRUD │ │CRUD │ │RAG  ││节点+边│ │CRUD ││预览 ││CRUD │ │
│ └──┬──┘└─┬──┘└─┬──┘└─┬──┘└─┬──┘└─┬──┘└─┬──┘└─┬──┘└─┬──┘    │
│    │     │     │     │     │     │     │     │     │           │
│ ┌──┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴─────────┐ │
│ │              PostgreSQL 15 (主数据库)                          │ │
│ │  笔记/笔记本/标签/便签/AI向量/图谱/日程/模板/文件/加密            │ │
│ └─────────────────────┬────────────────────────────────────────┘ │
│                        │                                          │
│  ┌─────────────────────┴────────────────────────────────────────┐  │
│  │           Elasticsearch 8.x (全文搜索)                        │  │
│  │        笔记内容 + PDF/Word/Excel 全文索引                      │  │
│  └─────────────────────┬────────────────────────────────────────┘  │
│                        │                                          │
│  ┌─────────────────────┴────────────────────────────────────────┐  │
│  │         Qdrant / Meilisearch (向量检索)                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 三、桌面端 Electron 架构

### 3.1 技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| Electron | 28+ | 成熟稳定 |
| 前端 | React 18 + TypeScript | 组件化 |
| 构建 | Vite | 快速热更新 |
| 本地数据库 | better-sqlite3 | 同步API，原生编译 |
| Markdown编辑 | @uiw/react-md-editor | 功能完整 |
| 状态管理 | Zustand | 轻量，TS友好 |
| 同步引擎 | 自研 | 核心能力 |
| IPC | contextBridge + ipcRenderer | 安全进程通信 |
| 打包 | electron-builder | exe/msi |
| 全局快捷键 | electron-globalShortcut | Cmd+Shift+N |
| 托盘 | electron Tray | 最小化到托盘 |
| 自动更新 | electron-updater | 差量更新 |

### 3.2 进程架构

```
Electron App
│
├── Main Process (主进程)
│   ├── WindowManager              # 窗口管理（主窗口+便签弹窗）
│   ├── GlobalShortcutManager      # 全局快捷键注册
│   ├── TrayManager                # 系统托盘（同步状态指示）
│   ├── SQLiteEngine               # better-sqlite3 封装
│   │   ├── LocalDB               # 本地SQLite（离线数据）
│   │   └── SyncQueue             # 待同步队列
│   ├── CryptoService             # 加密笔记（AES-256-GCM）
│   ├── FileSystemService         # 文件读写、附件管理
│   ├── AutoUpdater               # 差量更新
│   └── IPCHandlers               # 100+ IPC通道（对应所有API）
│
├── Preload Scripts
│   └── contextBridge.exposeInMainWorld('api', {
│         // 安全暴露到渲染进程
│       })
│
└── Renderer Process (渲染进程)
    └── React App
        ├── UI Components
        │   ├── NoteEditor           # Markdown编辑器
        │   ├── NotebookTree         # 笔记本树形结构
        │   ├── TagManager          # 标签管理
        │   ├── QuickCaptureModal   # 便签弹窗
        │   ├── SyncStatusBar       # 同步状态栏
        │   ├── SearchPanel         # 本地全文搜索
        │   ├── ConflictResolver    # 冲突解决UI
        │   ├── KnowledgeGraphView  # 知识图谱（API渲染）
        │   ├── MindMapEditor        # 思维导图（API渲染）
        │   ├── ScheduleCalendar    # 日程管理（API调用）
        │   ├── FilePreviewPanel     # PDF/Word/Excel预览
        │   ├── TemplatePicker      # 模板选择器
        │   ├── AIFeedbackPanel      # AI RAG问答界面
        │   └── EncryptionLock      # 加密笔记解锁
        │
        ├── Business Layer
        │   ├── SyncEngine           # 同步引擎（核心）
        │   ├── OfflineDBService     # 本地SQLite读写
        │   ├── APIClient            # 后端API调用（所有功能）
        │   ├── ConflictResolver    # 冲突处理
        │   └── EncryptionService   # 加密服务
        │
        └── State Layer
            └── Zustand Stores
                ├── noteStore       # 笔记状态
                ├── notebookStore   # 笔记本状态
                ├── tagStore        # 标签状态
                ├── syncStore       # 同步状态
                ├── graphStore      # 知识图谱状态
                ├── scheduleStore    # 日程状态
                └── uiStore         # UI状态（侧边栏、弹窗）
```

### 3.3 IPC通道设计（对应所有后端API）

```typescript
// Preload暴露的API（按模块分组）
interface ElectronAPI {
  // 笔记模块
  notes: {
    list(notebookId?: string): Promise<Note[]>
    get(id: string): Promise<Note>
    create(data: CreateNoteDTO): Promise<Note>
    update(id: string, data: UpdateNoteDTO): Promise<Note>
    delete(id: string): Promise<void>
    search(query: string): Promise<Note[]>        // 本地优先，fallback到API
  }

  // 笔记本模块
  notebooks: {
    list(): Promise<Notebook[]>
    create(data: CreateNotebookDTO): Promise<Notebook>
    update(id: string, data: UpdateNotebookDTO): Promise<Notebook>
    delete(id: string): Promise<void>
    reorder(id: string, newOrder: number): Promise<void>
  }

  // 标签模块
  tags: {
    list(): Promise<Tag[]>
    create(data: CreateTagDTO): Promise<Tag>
    update(id: string, data: UpdateTagDTO): Promise<Tag>
    delete(id: string): Promise<void>
  }

  // 知识图谱模块
  graph: {
    getNodes(): Promise<GraphNode[]>
    getEdges(): Promise<GraphEdge[]>
    addNode(data: CreateNodeDTO): Promise<GraphNode>
    updateNode(id: string, data: UpdateNodeDTO): Promise<GraphNode>
    deleteNode(id: string): Promise<void>
    addEdge(data: CreateEdgeDTO): Promise<GraphEdge>
    deleteEdge(id: string): Promise<void>
  }

  // AI RAG模块
  ai: {
    ask(question: string, context?: string): Promise<AIFeedback>
    rebuildIndex(): Promise<void>                  // 重建向量索引
  }

  // 日程模块
  schedules: {
    list(start: number, end: number): Promise<Schedule[]>
    create(data: CreateScheduleDTO): Promise<Schedule>
    update(id: string, data: UpdateScheduleDTO): Promise<Schedule>
    delete(id: string): Promise<void>
    setReminder(id: string, remindAt: number): Promise<void>
  }

  // 文件预览模块
  files: {
    upload(file: File, noteId: string): Promise<Attachment>
    preview(attachmentId: string): Promise<string>   // 返回预览URL/数据
    download(attachmentId: string): Promise<Blob>
    delete(attachmentId: string): Promise<void>
  }

  // 思维导图模块
  mindmap: {
    get(noteId: string): Promise<MindMapData>
    save(noteId: string, data: MindMapData): Promise<void>
  }

  // 模板模块
  templates: {
    list(): Promise<Template[]>
    create(data: CreateTemplateDTO): Promise<Template>
    apply(templateId: string, notebookId: string): Promise<Note>
    delete(id: string): Promise<void>
  }

  // 加密笔记模块
  encryption: {
    lock(noteId: string, password: string): Promise<void>
    unlock(noteId: string, password: string): Promise<Note>
    changePassword(noteId: string, oldPw: string, newPw: string): Promise<void>
  }

  // 便签模块
  quickCapture: {
    create(content: string): Promise<QuickCapture>
    list(): Promise<QuickCapture[]>
    convert(id: string, notebookId: string): Promise<Note>
    delete(id: string): Promise<void>
  }

  // 导入导出
  importExport: {
    exportNote(noteId: string, format: 'md' | 'pdf' | 'docx'): Promise<string>
    exportNotebook(notebookId: string): Promise<string>
    importFile(file: File): Promise<Note>
  }

  // 同步模块
  sync: {
    push(): Promise<SyncResult>
    pull(): Promise<SyncResult>
    getStatus(): Promise<SyncStatus>
    resolveConflict(id: string, resolution: 'local' | 'server' | 'merge'): Promise<void>
  }

  // 系统
  system: {
    setTrayIcon(status: 'syncing' | 'synced' | 'offline' | 'error'): void
    showNotification(title: string, body: string): void
    openQuickCapture(): void
  }
}
```

---

## 四、移动端 React Native 架构

### 4.1 技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| 框架 | Expo SDK 52+ | 开发体验好 |
| 语言 | TypeScript | 保持一致 |
| 本地数据库 | expo-sqlite | SQLite支持 |
| 网络检测 | @react-native-community/netinfo | 网络状态 |
| 导航 | expo-router | 文件路由 |
| Markdown渲染 | react-native-markdown-display | 只读渲染 |
| 状态管理 | Zustand | 与桌面端统一 |
| 打包 | expo prebuild + android build | APK |

### 4.2 应用架构

```
React Native App (Expo)
│
├── Native Layer
│   ├── expo-sqlite              # 本地SQLite数据库
│   ├── expo-file-system         # 文件访问
│   ├── expo-notifications       # 本地通知（日程提醒）
│   ├── NetInfo                  # 网络状态检测
│   └── SplashScreen / AppLoading
│
└── JS Layer
    ├── UI Components
    │   ├── NoteEditorScreen     # 笔记编辑
    │   ├── NotebookListScreen   # 笔记本列表
    │   ├── TagFilterScreen      # 标签筛选
    │   ├── SearchScreen         # 搜索（含AI RAG入口）
    │   ├── QuickCaptureSheet    # 便签底部弹窗
    │   ├── ScheduleScreen      # 日程日历
    │   ├── GraphViewScreen      # 知识图谱简易视图
    │   ├── FilePreviewScreen    # 文件预览
    │   ├── TemplatePickerModal  # 模板选择
    │   ├── AIFeedbackScreen     # AI RAG问答
    │   ├── SyncStatusBanner     # 同步状态条
    │   └── ConflictScreen       # 冲突解决
    │
    ├── Business Layer
    │   ├── SyncEngine           # 同步引擎（复用桌面端逻辑）
    │   ├── OfflineDBService     # 本地SQLite封装
    │   ├── APIClient            # 后端API调用
    │   ├── ConflictResolver    # 冲突处理
    │   └── LocalSearchService  # 本地FTS5搜索
    │
    └── State Layer
        └── Zustand Stores       # 与桌面端同构
```

### 4.3 移动端功能限制说明

| 功能 | 桌面端 | 移动端 | 原因 |
|------|--------|--------|------|
| 加密笔记 | ✅ 完整 | ⚠️ 解锁查看，不支持创建加密 | 密码输入在移动端体验差 |
| 思维导图 | ✅ 完整编辑 | ⚠️ 只读查看 | 触控编辑复杂 |
| 文件预览 | ✅ 完整 | ⚠️ PDF/图片可预览，Word/Excel降级 | 大文件预览性能问题 |
| 知识图谱 | ✅ 完整交互 | ⚠️ 节点列表+简易关系图 | 复杂图形渲染性能 |
| Markdown编辑 | ✅ 完整编辑器 | ⚠️ 简化textarea+预览 | 富编辑器触控体验差 |

---

## 五、离线同步设计（核心）

### 5.1 离线优先原则

```
所有操作 → 本地SQLite立即写入 → sync_status=pending → 后台同步到服务器
所有读取 → 本地SQLite优先 → 后台增量更新服务器数据
```

### 5.2 数据流图

```
用户操作（创建/编辑/删除）
         │
         ▼
┌─────────────────────────┐
│  React组件 onChange      │
│  debounce 500ms         │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Zustand Store 更新      │
│  (内存状态立即响应)        │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  OfflineDB Service       │
│  SQLite INSERT/UPDATE    │
│  sync_status = 'pending' │
└───────────┬─────────────┘
            │
    ┌───────┴───────┐
    │  网络可用？     │
    └───────┬───────┘
   Yes ↙         ↘ No
    │              │
    ▼              ▼
┌─────────┐  ┌──────────────┐
│SyncEngine│  │ 队列积压     │
│推送pending│  │ 等待网络恢复 │
│到服务器  │  └──────────────┘
└────┬────┘
     │ POST /api/sync/push
     ▼
┌─────────────────────────────────┐
│  服务器响应                       │
│  - ok → sync_status='synced'    │
│  - conflict → sync_status='conflict'
│  - error → retry (最多3次)       │
└─────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────┐
│  同时：定时拉取服务器变更          │
│  GET /api/sync/pull?since=version│
│  合并到本地SQLite                 │
└─────────────────────────────────┘
```

### 5.3 SQLite核心表结构

```sql
-- 实体表（笔记/笔记本/标签/便签/日程等）
-- 所有表统一字段：sync_status, local_version, server_version, local_updated_at

CREATE TABLE notes (
    id              TEXT PRIMARY KEY,
    user_id         TEXT NOT NULL,
    notebook_id     TEXT,
    title           TEXT NOT NULL DEFAULT '无标题',
    content         TEXT DEFAULT '',
    content_type    TEXT DEFAULT 'markdown',
    word_count      INTEGER DEFAULT 0,
    is_encrypted    INTEGER DEFAULT 0,
    sync_status     TEXT DEFAULT 'synced',  -- synced | pending | conflict | deleted
    sync_version    INTEGER DEFAULT 0,
    local_version   INTEGER DEFAULT 0,
    server_version  INTEGER DEFAULT 0,
    deleted_at      INTEGER,
    created_at      INTEGER NOT NULL,
    updated_at      INTEGER NOT NULL,
    local_updated_at INTEGER NOT NULL
);

CREATE TABLE notebooks (
    id              TEXT PRIMARY KEY,
    user_id         TEXT NOT NULL,
    parent_id       TEXT,
    name            TEXT NOT NULL,
    icon            TEXT DEFAULT '📁',
    color           TEXT DEFAULT '#3B82F6',
    sort_order      INTEGER DEFAULT 0,
    is_default      INTEGER DEFAULT 0,
    sync_status     TEXT DEFAULT 'synced',
    sync_version    INTEGER DEFAULT 0,
    local_version   INTEGER DEFAULT 0,
    server_version  INTEGER DEFAULT 0,
    deleted_at      INTEGER,
    created_at      INTEGER NOT NULL,
    updated_at      INTEGER NOT NULL,
    local_updated_at INTEGER NOT NULL
);

CREATE TABLE tags (
    id              TEXT PRIMARY KEY,
    user_id         TEXT NOT NULL,
    name            TEXT NOT NULL,
    color           TEXT DEFAULT '#6B7280',
    icon            TEXT,
    sort_order      INTEGER DEFAULT 0,
    sync_status     TEXT DEFAULT 'synced',
    sync_version    INTEGER DEFAULT 0,
    local_version   INTEGER DEFAULT 0,
    deleted_at      INTEGER,
    created_at      INTEGER NOT NULL,
    updated_at      INTEGER NOT NULL,
    local_updated_at INTEGER NOT NULL,
    UNIQUE(user_id, name)
);

CREATE TABLE note_tags (
    note_id         TEXT NOT NULL,
    tag_id          TEXT NOT NULL,
    sync_status     TEXT DEFAULT 'synced',
    created_at      INTEGER NOT NULL,
    PRIMARY KEY (note_id, tag_id)
);

CREATE TABLE quick_captures (
    id              TEXT PRIMARY KEY,
    user_id         TEXT NOT NULL,
    content         TEXT NOT NULL,
    source          TEXT DEFAULT 'mobile',
    target_notebook_id TEXT,
    status          TEXT DEFAULT 'pending',
    note_id         TEXT,
    created_at      INTEGER NOT NULL,
    processed_at    INTEGER
);

CREATE TABLE schedules (
    id              TEXT PRIMARY KEY,
    user_id         TEXT NOT NULL,
    title           TEXT NOT NULL,
    description     TEXT,
    start_time      INTEGER NOT NULL,
    end_time        INTEGER,
    location        TEXT,
    reminder_at     INTEGER,
    feishu_remind   INTEGER DEFAULT 1,
    sync_status     TEXT DEFAULT 'synced',
    sync_version    INTEGER DEFAULT 0,
    local_version   INTEGER DEFAULT 0,
    server_version  INTEGER DEFAULT 0,
    deleted_at      INTEGER,
    created_at      INTEGER NOT NULL,
    updated_at      INTEGER NOT NULL,
    local_updated_at INTEGER NOT NULL
);

CREATE TABLE attachments (
    id              TEXT PRIMARY KEY,
    note_id         TEXT NOT NULL,
    filename        TEXT NOT NULL,
    file_type       TEXT NOT NULL,
    file_size       INTEGER,
    file_path       TEXT,
    sync_status     TEXT DEFAULT 'synced',
    sync_version    INTEGER DEFAULT 0,
    local_version   INTEGER DEFAULT 0,
    server_version  INTEGER DEFAULT 0,
    created_at      INTEGER NOT NULL,
    local_updated_at INTEGER NOT NULL
);

-- 同步队列（离线操作缓冲）
CREATE TABLE sync_queue (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type     TEXT NOT NULL,    -- note|notebook|tag|schedule|quick_capture|attachment
    entity_id       TEXT NOT NULL,
    action          TEXT NOT NULL,    -- create|update|delete
    payload         TEXT NOT NULL,    -- JSON
    priority        INTEGER DEFAULT 0,
    retry_count     INTEGER DEFAULT 0,
    max_retries     INTEGER DEFAULT 3,
    created_at      INTEGER NOT NULL,
    scheduled_at    INTEGER
);

-- 冲突记录
CREATE TABLE conflicts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type     TEXT NOT NULL,
    entity_id       TEXT NOT NULL,
    local_data      TEXT NOT NULL,
    server_data     TEXT NOT NULL,
    conflict_type   TEXT NOT NULL,
    resolved        INTEGER DEFAULT 0,
    resolved_data   TEXT,
    resolved_at     INTEGER,
    created_at      INTEGER NOT NULL
);

-- 设备注册
CREATE TABLE devices (
    id              TEXT PRIMARY KEY,
    device_name     TEXT NOT NULL,
    device_type     TEXT NOT NULL,
    last_sync_at    INTEGER,
    sync_version    INTEGER DEFAULT 0,
    created_at      INTEGER NOT NULL
);

-- 本地设置
CREATE TABLE settings (
    key             TEXT PRIMARY KEY,
    value           TEXT NOT NULL
);

-- 索引
CREATE INDEX idx_notes_sync_status ON notes(sync_status);
CREATE INDEX idx_notes_notebook ON notes(notebook_id);
CREATE INDEX idx_notes_updated ON notes(local_updated_at);
CREATE INDEX idx_sync_queue_priority ON sync_queue(priority DESC, scheduled_at);
CREATE INDEX idx_conflicts_unresolved ON conflicts(resolved) WHERE resolved=0;
```

### 5.4 同步引擎核心逻辑

```typescript
// SyncEngine 伪代码
class SyncEngine {
  private db: SQLiteDB
  private api: APIClient
  private networkStatus: 'online' | 'offline'

  // 核心同步循环
  async sync() {
    if (this.networkStatus === 'offline') return

    // 1. 推：上传本地pending变更
    await this.pushPendingChanges()

    // 2. 拉：拉取服务器变更
    await this.pullServerChanges()

    // 3. 处理冲突
    await this.resolveConflicts()
  }

  // 推送本地变更
  private async pushPendingChanges() {
    const pending = await this.db.query(`
      SELECT * FROM sync_queue
      WHERE retry_count < max_retries
      ORDER BY priority DESC, scheduled_at ASC
      LIMIT 50
    `)

    for (const item of pending) {
      try {
        const result = await this.api.sync.push({
          entity_type: item.entity_type,
          entity_id: item.entity_id,
          action: item.action,
          payload: JSON.parse(item.payload),
          base_version: this.getBaseVersion(item)
        })

        if (result.status === 'ok') {
          await this.markSynced(item.entity_type, item.entity_id, result.version)
          await this.removeFromQueue(item.id)
        } else if (result.status === 'conflict') {
          await this.createConflict(item, result.server_data)
          await this.removeFromQueue(item.id)
        }
      } catch (error) {
        await this.incrementRetry(item.id)
      }
    }
  }

  // 拉取服务器变更
  private async pullServerChanges() {
    const lastVersion = await this.getLastSyncVersion()
    const changes = await this.api.sync.pull({ since: lastVersion })

    for (const change of changes) {
      const local = await this.db.get(change.entity_type, change.id)

      if (!local || change.version > local.server_version) {
        // 服务器更新较新，直接应用
        await this.applyServerChange(change)
      } else if (local.sync_status === 'pending') {
        // 本地也有变更，产生冲突
        await this.createConflictFromChange(local, change)
      }
    }

    await this.updateLastSyncVersion(changes.max_version)
  }

  // Last-Write-Wins 冲突解决
  private resolveConflictAutomatically(local: Entity, server: Entity): Entity | null {
    // 规则：时间戳最新者胜出
    if (local.local_updated_at > server.updated_at) {
      return local  // 用本地版本
    } else if (server.updated_at > local.local_updated_at) {
      return server // 用服务器版本
    }
    // 时间相同，字段级合并
    return this.fieldLevelMerge(local, server)
  }

  // 字段级自动合并（仅标签等简单场景）
  private fieldLevelMerge(local: any, server: any): any {
    const merged = { ...server }
    // 取并集
    for (const key of Object.keys(local)) {
      if (local[key] !== server[key]) {
        // 标记冲突，用户手动确认
        return null
      }
    }
    return merged
  }
}
```

### 5.5 冲突处理策略

| 冲突场景 | 自动处理 | 用户确认 |
|---------|---------|---------|
| 版本号连续（本地=服务器+1） | ✅ 自动接受本地 | ❌ 不需要 |
| 服务器更新较新，本地无变更 | ✅ 自动接受服务器 | ❌ 不需要 |
| 双方都有修改（相同字段） | ❌ | ✅ 需要 |
| 服务器已删除，本地有修改 | ❌ | ✅ 需要 |
| 本地已删除，服务器有修改 | ❌ | ✅ 需要 |

### 5.6 同步触发时机

| 时机 | 触发动作 |
|------|---------|
| App启动 | 全量同步（后台） |
| 网络恢复 | 全量同步（后台） |
| 前台每5分钟 | 增量同步 |
| 用户下拉刷新 | 强制全量同步 |
| 退出App | 尝试同步（最多等3秒） |
| 笔记保存debounce后 | 标记pending，30秒后批量同步 |

---

## 六、API调用策略（客户端如何调用后端）

### 6.1 统一API Client

```typescript
// packages/shared/src/api-client.ts
class APIClient {
  private baseURL: string
  private token: string

  async get(endpoint: string, params?: object): Promise<any>
  async post(endpoint: string, data?: object): Promise<any>
  async put(endpoint: string, data?: object): Promise<any>
  async delete(endpoint: string): Promise<any>

  // 每个后端模块对应一个方法组
  notes = new NotesAPI(this)
  notebooks = new NotebooksAPI(this)
  tags = new TagsAPI(this)
  graph = new GraphAPI(this)
  ai = new AIAPI(this)
  schedules = new SchedulesAPI(this)
  files = new FilesAPI(this)
  mindmap = new MindMapAPI(this)
  templates = new TemplatesAPI(this)
  encryption = new EncryptionAPI(this)
  quickCapture = new QuickCaptureAPI(this)
  importExport = new ImportExportAPI(this)
  sync = new SyncAPI(this)
}
```

### 6.2 在线/离线自动路由

```typescript
// 核心原则：本地优先，读写都先本地，再同步
class NoteService {
  constructor(
    private db: OfflineDB,
    private api: APIClient,
    private syncEngine: SyncEngine
  ) {}

  // 读取：始终从本地读（最快）
  async listNotes(notebookId?: string): Promise<Note[]> {
    return this.db.notes.list(notebookId)
  }

  // 写入：先本地，同步队列
  async createNote(data: CreateNoteDTO): Promise<Note> {
    const note = { ...data, id: uuid(), local_updated_at: Date.now(), sync_status: 'pending' }
    await this.db.notes.insert(note)
    await this.syncEngine.enqueue('note', note.id, 'create', note)
    return note
  }

  async updateNote(id: string, data: UpdateNoteDTO): Promise<Note> {
    const note = { ...data, local_updated_at: Date.now(), sync_status: 'pending' }
    await this.db.notes.update(id, note)
    await this.syncEngine.enqueue('note', id, 'update', note)
    return note
  }

  // 搜索：本地FTS优先，API搜索兜底
  async search(query: string): Promise<Note[]> {
    const local = await this.db.notes.search(query)  // FTS5
    if (local.length > 0) return local
    // 本地没有，尝试API搜索（需要联网）
    return this.api.notes.search(query)
  }

  // 知识图谱：直接调API，不本地缓存（图谱数据量小，实时性要求高）
  async getGraphData(): Promise<GraphData> {
    return this.api.graph.getFullGraph()
  }

  // AI RAG：直接调API（需要联网，本地无法处理）
  async askAI(question: string): Promise<AIFeedback> {
    return this.api.ai.ask(question)
  }

  // 日程：本地缓存+同步
  async getSchedules(start: number, end: number): Promise<Schedule[]> {
    return this.db.schedules.listRange(start, end)
  }
}
```

---

## 七、开发优先级

### 7.1 功能优先级矩阵

| 优先级 | 功能 | 桌面端 | 移动端 | 说明 |
|-------|------|--------|--------|------|
| **P0** | 笔记CRUD（Markdown） | ✅ | ✅ | 核心MVP |
| **P0** | 笔记本分类（树形） | ✅ | ✅ | 核心MVP |
| **P0** | 标签管理 | ✅ | ✅ | 核心MVP |
| **P0** | 本地SQLite存储 | ✅ | ✅ | 离线基础 |
| **P0** | 同步引擎 | ✅ | ✅ | 核心能力 |
| **P0** | 快速便签 | ✅ | ✅ | 核心场景 |
| **P0** | 同步状态指示器 | ✅ | ✅ | UX必需 |
| **P1** | 冲突检测+解决UI | ✅ | ✅ | 多设备必备 |
| **P1** | 本地全文搜索（FTS5） | ✅ | ✅ | 实用功能 |
| **P1** | 知识图谱（API渲染） | ✅ | ✅ | 已有API支持 |
| **P1** | 日程管理+飞书推送 | ✅ | ✅ | 已有API支持 |
| **P1** | AI RAG问答 | ✅ | ✅ | 已有API支持 |
| **P1** | 导入导出 | ✅ | ✅ | 已有API支持 |
| **P1** | 文件预览 | ✅ | ⚠️ | 桌面端完整，移动端降级 |
| **P1** | 模板系统 | ✅ | ✅ | 已有API支持 |
| **P1** | 多设备管理 | ✅ | ✅ | 设备列表/解绑 |
| **P1** | 笔记本/标签拖拽排序 | ✅ | ✅ | 体验优化 |
| **P2** | 思维导图 | ✅ | ⚠️ | 桌面端完整，移动端只读 |
| **P2** | 加密笔记 | ✅ | ⚠️ | 桌面端完整，移动端解锁 |
| **P2** | 笔记历史版本 | ✅ | ❌ | 后悔药，桌面端即可 |
| **P2** | 深色/浅色主题 | ✅ | ✅ | 体验优化 |

### 7.2 不做的功能

| 功能 | 原因 |
|------|------|
| ~~网页版~~ | 砍掉，专注客户端 |
| ~~插件系统~~ | 过于复杂 |
| ~~数据库视图（看板/画廊）~~ | 过于复杂 |
| ~~团队协作~~ | 单人使用 |

### 7.3 开发周期预估

| 阶段 | 周期 | 交付内容 |
|------|------|---------|
| Phase 0: 脚手架 | 1周 | 项目初始化+公用模块 |
| Phase 1: 桌面端MVP | 3-4周 | 笔记/同步/便签核心 |
| Phase 2: 移动端MVP | 2-3周 | Android核心功能 |
| Phase 3: 全功能对接 | 2-3周 | 所有后端API对接 |
| Phase 4: 收尾测试 | 1-2周 | 打包/Bug修复 |
| **合计** | **9-13周** | 约2-3个月 |

---

## 八、关键设计决策

### 8.1 为什么所有功能都保留？
后端所有API已经实现，客户端只需调用即可。
- 知识图谱：API返回节点+边，客户端渲染
- 日程：API处理CRUD+飞书推送，客户端只调用
- 文件预览：API返回预览数据，客户端展示
- 思维导图：API存储结构，客户端渲染+编辑
- 模板/便签/加密/AI：都是API能力，客户端调用

### 8.2 为什么不用CRDT/OT同步？
单人使用场景，Last-Write-Wins足够。CRDT/OT适合多人协作，过于复杂。

### 8.3 为什么移动端部分功能降级？
- 加密笔记：移动端密码输入体验差，只支持解锁查看
- 思维导图：触控编辑复杂，只读查看
- 文件预览：大文件传输+渲染性能问题，PDF/图片优先

### 8.4 为什么SQLite而不是sql.js？
- better-sqlite3（桌面端）：原生模块，同步API，性能好
- expo-sqlite（移动端）：原生SQLite，成熟稳定
- sql.js：WASM版本，体积大，性能差

---

## 九、风险与对策

| 风险 | 概率 | 影响 | 对策 |
|------|------|------|------|
| Electron打包>100MB | 高 | 低 | 已知问题，接受 |
| better-sqlite3编译 | 中 | 中 | 使用prebuild-binary |
| 移动端后台同步延迟 | 高 | 中 | 前台主动同步，系统限制无法完全解决 |
| API接口需要改造 | 低 | 高 | 现有API已支持同步操作 |
| Android权限问题 | 低 | 低 | Expo处理大部分权限 |

---

## 十、后续步骤

1. 雪子确认架构
2. Phase 0：初始化项目（monorepo结构，shared包）
3. Phase 1：桌面端MVP（笔记+同步引擎+便签）
4. Phase 2：移动端MVP（核心CRUD+同步）
5. Phase 3：全功能对接（所有API）
6. Phase 4：收尾打包发布

---

*架构设计完成，待确认后启动开发*
