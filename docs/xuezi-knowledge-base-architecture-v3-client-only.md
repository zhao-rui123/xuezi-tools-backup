# 雪子知识库 - 独立客户端版 架构设计

> 文档版本：v1.0（新架构）
> 作者：雪子助手
> 日期：2026-04-03
> 状态：**架构设计稿，待确认后开发**

---

## 一、项目定位

### 1.1 核心变化（vs v2）
| 对比项 | v2（旧） | v3（新版） |
|--------|---------|-----------|
| 客户端 | Web + Electron + RN(Phase2) | **Electron桌面 + React Native** |
| 离线能力 | SQLite缓存（弱） | **本地SQLite优先（强）** |
| 网页版 | ✅ 有 | ❌ **砍掉** |
| 知识图谱 | ✅ 有 | ❌ **砍掉** |
| 日程管理 | ✅ 有 | ❌ **砍掉** |
| 文件预览 | ✅ 有 | ❌ **砍掉** |
| 同步策略 | 服务器为主 | **离线优先 + 联网同步** |

### 1.2 产品定位
- **产品名称**：雪子知识库（XueziKB）v3
- **核心定位**：离线优先的跨设备笔记知识管理
- **目标用户**：雪子（单人使用）
- **客户端**：Windows桌面端 + Android手机端

---

## 二、系统架构图

### 2.1 整体架构

```
┌──────────────────────────────────────────────────────────────┐
│                        用户设备层                              │
├────────────────────────────┬─────────────────────────────────┤
│    Windows PC              │       Android 手机              │
│ ┌────────────────────┐     │   ┌────────────────────┐        │
│ │ Electron App       │     │   │ React Native App   │        │
│ │                    │     │   │                    │        │
│ │ ┌────────────────┐ │     │   │ ┌────────────────┐ │        │
│ │ │ React UI       │ │     │   │ │ Native UI      │ │        │
│ │ │ (编辑器/列表)  │ │     │   │ │ (组件)         │ │        │
│ │ └───────┬────────┘ │     │   │ └───────┬────────┘ │        │
│ │         │          │     │   │         │          │        │
│ │ ┌───────▼────────┐ │     │   │ ┌───────▼────────┐ │        │
│ │ │ Sync Engine   │ │     │   │ │ Sync Engine   │ │        │
│ │ │ (同步引擎)    │ │     │   │ │ (同步引擎)    │ │        │
│ │ └───────┬────────┘ │     │   │ └───────┬────────┘ │        │
│ │         │          │     │   │         │          │        │
│ │ ┌───────▼────────┐ │     │   │ ┌───────▼────────┐ │        │
│ │ │ Local SQLite  │ │     │   │ │ Local SQLite  │ │        │
│ │ │ (本地数据库)  │ │     │   │ │ (本地数据库)  │ │        │
│ │ └────────────────┘ │     │   │ └────────────────┘ │        │
│ └────────────────────┘     │   └────────────────────┘        │
│           ↕ 联网同步         │          ↕ 联网同步              │
└────────────┼───────────────┴──────────────┼──────────────────┘
             │                                │
             │      HTTPS / WSS               │
             │      (现有API接口)              │
             │                                │
┌────────────▼────────────────────────────────▼──────────────────┐
│                      腾讯云服务器 (不变)                          │
│                  http://106.54.25.161                           │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Nginx (反向代理 + SSL)                      │  │
│  └──────────────────────────┬──────────────────────────────┘  │
│                             │                                    │
│  ┌──────────────────────────▼──────────────────────────────┐  │
│  │                    API 网关 (Node.js)                      │  │
│  │              JWT认证 / 限流 / 请求路由 (现有不变)           │  │
│  └─┬────────┬────────┬────────┬────────┬────────┬──────────┘  │
│    │        │        │        │        │        │              │
│ ┌──┴──┐ ┌───┴──┐ ┌───┴──┐ ┌───┴──┐ ┌───┴──┐ ┌───┴───┐         │
│ │笔记  │ │笔记本│ │标签  │ │便签  │ │AI    │ │同步   │         │
│ │服务  │ │服务  │ │服务  │ │服务  │ │RAG   │ │服务   │         │
│ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬───┘         │
│    │        │        │        │        │        │              │
│ ┌──┴────────┴────────┴────────┴────────┴────────┴──────────┐  │
│ │              PostgreSQL 15 (主数据库)                      │  │
│ │        笔记/笔记本/标签/便签/AI向量/同步记录                 │  │
│ └───────────────────────┬───────────────────────────────────┘  │
│                         │                                      │
│  ┌──────────────────────▼───────────────────────────────────┐  │
│  │              Redis 7.x (缓存 + 队列)                        │  │
│  │           会话缓存 / 限流 / AI任务队列                      │  │
│  └───────────────────────┬───────────────────────────────────┘  │
│                          │                                      │
│  ┌───────────────────────▼───────────────────────────────────┐  │
│  │     Qdrant / Meilisearch (向量检索) ← AI RAG (P2可选)      │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 客户端内部架构（桌面端）

```
Electron App
├── Main Process (主进程)
│   ├── Window Manager        # 窗口管理
│   ├── Global Shortcut        # 全局快捷键（Cmd+Shift+N）
│   ├── Tray Icon             # 系统托盘
│   ├── SQLite Engine         # better-sqlite3 原生模块
│   ├── File System           # 文件读写
│   └── Auto-updater          # 自动更新
│
├── Preload Scripts (预加载)
│   ├── exposeInMainWorld     # 安全暴露API到渲染进程
│   └── ipcRenderer.invoke    # 进程间通信
│
└── Renderer Process (渲染进程)
    └── React App
        ├── UI Layer
        │   ├── Markdown Editor    # @uiw/react-md-editor / Milkdown
        │   ├── Note List          # 笔记列表
        │   ├── Notebook Tree      # 笔记本树形结构
        │   ├── Tag Manager        # 标签管理
        │   └── Quick Capture     # 便签弹窗
        │
        ├── Business Layer
        │   ├── SyncEngine        # 同步引擎（核心）
        │   ├── OfflineDB         # 本地SQLite封装
        │   ├── ConflictResolver  # 冲突解决
        │   └── CryptoService      # 加密（可选）
        │
        └── State Layer
            └── Zustand Store     # 状态管理
```

### 2.3 客户端内部架构（移动端）

```
React Native App (Expo)
├── Native Layer
│   ├── SQLite (expo-sqlite)   # 本地数据库
│   ├── NetInfo                # 网络状态检测
│   └── Background Sync        # 后台同步（有限）
│
└── JS Layer
    ├── UI Components
    │   ├── Markdown Editor    # react-native-markdown-display
    │   ├── FlatList           # 笔记列表
    │   ├── SectionList        # 笔记本列表
    │   └── FAB                # 快速便签按钮
    │
    ├── Business Layer
    │   ├── SyncEngine         # 同步引擎（复用桌面端逻辑）
    │   ├── OfflineDB          # 本地SQLite封装
    │   └── API Client         # REST API调用
    │
    └── State Layer
        └── Zustand / Context  # 状态管理
```

---

## 三、技术栈选型

### 3.1 桌面端（Electron）

| 组件 | 技术选型 | 备选 | 说明 |
|------|---------|------|------|
| 框架 | Electron 28+ | - | 成熟稳定，生态完善 |
| 前端框架 | React 18 + TypeScript | - | 与桌面端统一 |
| 构建工具 | Vite | - | 快速热更新 |
| 本地数据库 | better-sqlite3 | - | 同步API，性能好，原生编译 |
| Markdown编辑器 | @uiw/react-md-editor | Milkdown | 开源、功能完整 |
| 状态管理 | Zustand | - | 轻量、TypeScript友好 |
| 同步引擎 | 自研 | - | 核心差异化能力 |
| 自动构建 | electron-builder | - | 打包exe/msi |
| 全局快捷键 | electron-globalshortcut | - | 系统级快捷键 |
| 窗口管理 | electron BrowserWindow | - | 原生窗口控制 |
| 系统托盘 | electron Tray | - | 最小化到托盘 |
| 自动更新 | electron-updater | - | 差量更新 |

### 3.2 移动端（React Native）

| 组件 | 技术选型 | 备选 | 说明 |
|------|---------|------|------|
| 框架 | Expo SDK 52+ | - | 开发体验好，踩坑少 |
| 语言 | TypeScript | - | 保持一致 |
| 本地数据库 | expo-sqlite | - | SQLite支持，性能好 |
| Markdown渲染 | react-native-markdown-display | - | 纯渲染，只读 |
| Markdown编辑 | 自研/textarea | - | 简化编辑能力 |
| 状态管理 | Zustand | - | 与桌面端统一 |
| 网络检测 | @react-native-community/netinfo | - | 监听网络状态 |
| 导航 | expo-router | react-navigation | 文件路由，更现代 |
| APK打包 | expo prebuild + android build | - | 原生打包 |

### 3.3 后端（保持不变）

| 组件 | 现状 | 说明 |
|------|------|------|
| Node.js + Express | 现有 | API服务不变 |
| PostgreSQL | 现有 | 主数据库不变 |
| Redis | 现有 | 缓存/队列不变 |
| Qdrant | 现有（可选） | AI RAG用 |
| JWT认证 | 现有 | Auth不变 |

### 3.4 技术栈汇总对比

| 层级 | 桌面端 | 移动端 | 后端 |
|------|--------|--------|------|
| 框架 | Electron 28 | Expo SDK 52 | Node.js |
| 语言 | TypeScript | TypeScript | TypeScript |
| UI | React 18 | React Native | - |
| 数据库 | better-sqlite3 | expo-sqlite | PostgreSQL 15 |
| 状态管理 | Zustand | Zustand | - |
| Markdown | @uiw/react-md-editor | markdown-display | - |
| 构建打包 | electron-builder | expo prebuild | - |
| 同步 | 自研 | 自研 | 现有API |

---

## 四、数据流设计（离线优先）

### 4.1 离线优先核心原则

```
1. 写入：始终写入本地SQLite，标记sync_status=pending
2. 读取：始终读本地SQLite，后台异步从服务器拉取最新
3. 同步：联网后自动触发同步，支持手动强制同步
4. 冲突：Last-Write-Wins + 用户确认双写场景
```

### 4.2 完整数据流图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户操作                              │
│                  (创建/编辑/删除笔记)                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      React 组件层                            │
│              onChange → debounce 500ms                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Zustand Store                             │
│         setNote(note) → 更新内存状态                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    OfflineDB (SQLite)                       │
│  INSERT OR REPLACE INTO notes                                │
│    (id, title, content, sync_status='pending',              │
│     local_updated_at, sync_version)                         │
│                                                             │
│  status: pending → in_sync → synced / conflict              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    ┌───────▼───────┐
                    │  网络可用？    │
                    └───────┬───────┘
                   Yes ↙       ↘ No
                    │            │
                    ▼            │   (任务进入待同步队列)
        ┌───────────────────┐    │
        │   SyncEngine       │    │
        │   (同步引擎)       │    │
        └───────┬───────────┘    │
                │                 │
                ▼                 │
        ┌───────────────────┐     │
        │  POST /api/sync   │     │
        │  push (批量上传)  │     │
        └───────┬───────────┘     │
                │                 │
    ┌───────────▼──────────┐     │
    │   服务器返回结果      │     │
    │   - ok → 更新sync_version   │
    │   - conflict → 标记冲突    │
    └───────────┬──────────┘     │
                │                 │
    ┌───────────▼──────────┐     │
    │   冲突处理策略        │     │
    └───────────┬──────────┘     │
                │                 │
    ┌───────────┼─────────────────────┐
    │           │                     │
    ▼           ▼                     ▼
┌────────┐ ┌──────────┐ ┌──────────────────┐
│自动合并│ │用户确认  │ │ Last-Write-Wins  │
│(字段级)│ │(双写冲突)│ │ (默认策略)        │
└────────┘ └──────────┘ └──────────────────┘
```

### 4.3 本地SQLite表结构设计

```sql
-- 设备注册表（每台设备唯一）
CREATE TABLE devices (
    id              TEXT PRIMARY KEY,        -- 设备UUID
    device_name     TEXT NOT NULL,           -- "Windows-PC-锐" / "Pixel-7"
    device_type     TEXT NOT NULL,           -- 'desktop' / 'mobile'
    last_sync_at    INTEGER,                 -- Unix timestamp
    sync_version    INTEGER DEFAULT 0,       -- 全局同步版本号
    created_at      INTEGER NOT NULL
);

-- 笔记本表（本地镜像服务器notebooks表）
CREATE TABLE notebooks (
    id              TEXT PRIMARY KEY,       -- UUID，与服务器一致
    user_id         TEXT NOT NULL,
    parent_id       TEXT,                   -- 父笔记本UUID
    name            TEXT NOT NULL,
    icon            TEXT DEFAULT '📁',
    color           TEXT DEFAULT '#3B82F6',
    sort_order      INTEGER DEFAULT 0,
    is_default      INTEGER DEFAULT 0,
    sync_status     TEXT DEFAULT 'synced',  -- synced | pending | conflict | deleted
    sync_version    INTEGER DEFAULT 0,
    local_version   INTEGER DEFAULT 0,      -- 本地变更版本
    server_version  INTEGER DEFAULT 0,      -- 服务器版本（冲突时用）
    deleted_at      INTEGER,                -- Unix timestamp，软删
    created_at      INTEGER NOT NULL,
    updated_at      INTEGER NOT NULL,
    local_updated_at INTEGER NOT NULL       -- 本地最后修改时间
);

-- 笔记表（核心表）
CREATE TABLE notes (
    id              TEXT PRIMARY KEY,       -- UUID
    user_id         TEXT NOT NULL,
    notebook_id    TEXT,
    title           TEXT NOT NULL DEFAULT '无标题',
    content         TEXT DEFAULT '',
    content_type    TEXT DEFAULT 'markdown',
    word_count      INTEGER DEFAULT 0,
    sync_status     TEXT DEFAULT 'synced',  -- synced | pending | conflict | deleted
    sync_version    INTEGER DEFAULT 0,
    local_version   INTEGER DEFAULT 0,
    server_version  INTEGER DEFAULT 0,
    deleted_at      INTEGER,                -- 软删除时间戳
    created_at      INTEGER NOT NULL,
    updated_at      INTEGER NOT NULL,
    local_updated_at INTEGER NOT NULL
);

-- 笔记-标签关联表
CREATE TABLE note_tags (
    note_id         TEXT NOT NULL,
    tag_id          TEXT NOT NULL,
    created_at      INTEGER NOT NULL,
    sync_status     TEXT DEFAULT 'synced',
    PRIMARY KEY (note_id, tag_id)
);

-- 标签表
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

-- 便签表（快速capture）
CREATE TABLE quick_captures (
    id              TEXT PRIMARY KEY,
    user_id         TEXT NOT NULL,
    content         TEXT NOT NULL,
    source          TEXT DEFAULT 'desktop',  -- desktop | mobile
    target_notebook_id TEXT,
    status          TEXT DEFAULT 'pending',   -- pending | converted | archived
    note_id         TEXT,                      -- 转换后的笔记ID
    created_at      INTEGER NOT NULL,
    processed_at    INTEGER
);

-- 同步任务队列表（离线操作的缓冲队列）
CREATE TABLE sync_queue (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type     TEXT NOT NULL,             -- note | notebook | tag | quick_capture
    entity_id       TEXT NOT NULL,
    action          TEXT NOT NULL,             -- create | update | delete
    payload         TEXT NOT NULL,             -- JSON序列化
    priority        INTEGER DEFAULT 0,         -- 数字越大优先级越高
    retry_count     INTEGER DEFAULT 0,
    max_retries     INTEGER DEFAULT 3,
    created_at      INTEGER NOT NULL,
    scheduled_at    INTEGER                    -- 计划执行时间
);

-- 冲突记录表
CREATE TABLE conflicts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type     TEXT NOT NULL,
    entity_id       TEXT NOT NULL,
    local_data      TEXT NOT NULL,             -- JSON
    server_data     TEXT NOT NULL,             -- JSON
    conflict_type   TEXT NOT NULL,             -- version_mismatch | deleted_on_server | deleted_locally
    resolved        INTEGER DEFAULT 0,         -- 0=未解决 1=已解决
    resolved_data   TEXT,                       -- 解决后的数据
    resolved_at     INTEGER,
    created_at      INTEGER NOT NULL
);

-- 向量索引记录表（RAG用，P2可选）
CREATE TABLE rag_index (
    id              TEXT PRIMARY KEY,
    note_id         TEXT NOT NULL,
    chunk_index     INTEGER NOT NULL,
    chunk_text      TEXT NOT NULL,
    vector_id       TEXT,                       -- 服务器返回的向量ID
    indexed_at      INTEGER NOT NULL,
    sync_status     TEXT DEFAULT 'pending'
);

-- 本地设置
CREATE TABLE settings (
    key             TEXT PRIMARY KEY,
    value           TEXT NOT NULL
);

-- 索引
CREATE INDEX idx_notes_sync_status ON notes(sync_status);
CREATE INDEX idx_notes_notebook_id ON notes(notebook_id);
CREATE INDEX idx_notebooks_sync_status ON notebooks(sync_status);
CREATE INDEX idx_tags_sync_status ON tags(sync_status);
CREATE INDEX idx_sync_queue_entity ON sync_queue(entity_type, entity_id);
CREATE INDEX idx_conflicts_resolved ON conflicts(resolved);
```

### 4.4 同步状态机

```
                    ┌──────────────────────────────────┐
                    │                                  │
    用户操作 ──►  pending ──►  syncing ──►  synced      │
                                         │             │
                                         │ 失败         │
                                         ▼             │
                                      retry ──► pending │
                                         │             │
                                    重试3次后           │
                                         ▼             │
                                      conflict ◄───────┘
                                         │
                                         ▼
                               ┌─────────────────┐
                               │  冲突解决       │
                               │  (自动/手动)    │
                               └────────┬────────┘
                                        │
                                        ▼
                                    synced
```

### 4.5 冲突处理策略

#### 4.5.1 冲突类型

| 冲突类型 | 说明 | 自动解决？ |
|---------|------|----------|
| `version_mismatch` | 双方都有修改 | ❌ 需确认 |
| `deleted_on_server` | 服务器已删，本地修改 | ❌ 需确认 |
| `deleted_locally` | 本地已删，服务器修改 | ❌ 需确认 |
| `field_conflict` | 部分字段冲突 | ✅ 自动合并 |

#### 4.5.2 冲突处理流程

```
冲突检测（POST /api/sync/push）
         │
         ▼
┌─────────────────────────────────┐
│  场景1: 版本号连续              │
│  local.base_version + 1 == server.version  │
│  → 无冲突，接受本地，覆盖服务器   │
│  → sync_status = 'synced'       │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  场景2: 版本号不连续             │
│  local.base_version + 1 < server.version   │
│  → 有冲突，记录到conflicts表    │
│  → sync_status = 'conflict'     │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  冲突解决界面（用户可见）         │
│                                 │
│  "笔记「储能项目」存在冲突：     │
│   ┌─────────────┬────────────┐ │
│   │  本地版本    │  服务器版本 │ │
│   ├─────────────┼────────────┤ │
│   │  修改了标题  │  修改了内容 │ │
│   │  2026-04-03 │  2026-04-02 │ │
│   └─────────────┴────────────┘ │
│   [用本地版本] [用服务器版本]    │
│   [手动合并]                    │
└─────────────────────────────────┘
```

#### 4.5.3 自动合并策略（字段级）

```typescript
// 笔记自动合并规则
function autoMerge(local: Note, server: Note): Note {
  const merged: Note = { ...server };

  // 规则1: 标题 - 用最新修改的
  if (local.local_updated_at > server.updated_at) {
    merged.title = local.title;
  }

  // 规则2: 内容 - 用最新修改的
  if (local.local_updated_at > server.updated_at) {
    merged.content = local.content;
  }

  // 规则3: 标签 - 合并去重
  const localTags = new Set(local.tag_ids);
  const serverTags = new Set(server.tag_ids);
  merged.tag_ids = [...new Set([...localTags, ...serverTags])];

  return merged;
}
```

### 4.6 同步触发时机

| 触发条件 | 动作 |
|---------|------|
| App启动 | 立即同步一次（后台） |
| 网络恢复 | 立即同步一次 |
| 每5分钟（前台） | 增量同步 |
| 用户下拉刷新 | 强制同步 |
| 退出App | 尝试同步（最多等3秒） |
| 笔记保存debounce后 | 标记pending，排队同步 |

---

## 五、开发优先级（P0/P1/P2）

### 5.1 功能优先级矩阵

| 优先级 | 功能模块 | 桌面端 | 移动端 | 说明 |
|-------|---------|--------|--------|------|
| **P0** | 笔记CRUD（Markdown） | ✅ | ✅ | **核心，MVP必须** |
| **P0** | 笔记本分类（树形） | ✅ | ✅ | **核心，MVP必须** |
| **P0** | 标签管理 | ✅ | ✅ | **核心，MVP必须** |
| **P0** | 离线SQLite存储 | ✅ | ✅ | **核心，MVP必须** |
| **P0** | 联网自动同步 | ✅ | ✅ | **核心，MVP必须** |
| **P0** | 同步状态指示器 | ✅ | ✅ | **同步进度可见** |
| **P0** | 快速便签（全局快捷键） | ✅ | ✅ | **核心使用场景** |
| **P1** | 笔记搜索（本地全文） | ✅ | ✅ | **实用功能** |
| **P1** | 同步冲突处理界面 | ✅ | ✅ | **多设备必备** |
| **P1** | 多设备管理 | ✅ | ✅ | **设备列表/解绑** |
| **P1** | 笔记本/标签拖拽排序 | ✅ | ✅ | **体验优化** |
| **P1** | 笔记历史版本 | ✅ | ❌ | **后悔药** |
| **P1** | 导出为Markdown | ✅ | ✅ | **数据可迁移** |
| **P2** | AI RAG问答 | ✅ | ✅ | **可选，有服务器支持** |
| **P2** | 加密笔记 | ✅ | ❌ | **P2后期** |
| **P2** | 深色/浅色主题 | ✅ | ✅ | **P2后期** |
| **P2** | 模板系统 | ✅ | ❌ | **P2后期** |

### 5.2 不做的功能（砍掉）

| 功能 | 原因 |
|------|------|
| ~~网页版~~ | 专注客户端，离线优先 |
| ~~知识图谱可视化~~ | 过于复杂，非核心 |
| ~~日程管理~~ | 过于复杂，非核心 |
| ~~文件预览(PDF/Word/Excel)~~ | 过于复杂，非核心 |
| ~~思维导图~~ | 过于复杂，非核心 |
| ~~Obsidian/Notion导入~~ | P2以后考虑 |
| ~~语音转文字~~ | P2以后考虑 |

---

## 六、预估开发周期

### 6.1 总周期预估

| 阶段 | 周期 | 交付内容 |
|------|------|---------|
| **Phase 0: 架构+脚手架** | **1周** | 项目初始化、公用模块 |
| **Phase 1: 桌面端MVP** | **3-4周** | 核心功能+同步引擎 |
| **Phase 2: 移动端MVP** | **2-3周** | Android核心功能 |
| **Phase 3: 收尾+测试** | **1-2周** | 打磨、bug修复、打包 |
| **合计** | **7-9周** | 约2个月 |

### 6.2 详细周次计划

```
Phase 0: 架构+脚手架（Week 1）
├── Day 1-2: 架构设计评审（已在本文档）
├── Day 3-4: 项目初始化
│   ├── Electron桌面端项目搭建（Vite + React + TS）
│   ├── React Native Expo项目搭建
│   └── 统一代码仓库结构（monorepo: packages/shared）
│
└── Day 5: 公用模块
    ├── 统一TypeScript类型定义（shared/types）
    ├── 统一API Client（shared/api-client）
    └── 统一数据模型（shared/models）

Phase 1: 桌面端MVP（Week 2-5）

Week 2: 数据库+笔记本+笔记CRUD
├── 本地SQLite初始化（better-sqlite3）
├── 笔记本CRUD（增删改查、树形结构）
├── 笔记CRUD（Markdown编辑器）
├── 标签CRUD
└── 基础UI（列表、详情、编辑）

Week 3: 同步引擎+便签
├── SyncEngine核心逻辑
│   ├── 离线写入 + sync_status管理
│   ├── 增量同步算法
│   └── 同步队列处理
├── 冲突检测+解决
├── 全局快捷键（Cmd+Shift+N）
├── 快速便签弹窗
└── 同步状态指示器（托盘图标）

Week 4: 搜索+多设备
├── 本地全文搜索（FTS5）
├── 笔记本/标签拖拽排序
├── 设备管理界面
└── 手动同步触发

Week 5: 收尾+打包
├── 笔记历史版本
├── Markdown导出
├── electron-builder打包exe
├── 自动更新配置
└── Bug修复+体验打磨

Phase 2: 移动端MVP（Week 6-8）

Week 6: 基础框架+核心CRUD
├── Expo项目配置
├── expo-sqlite初始化
├── 笔记本+笔记+标签CRUD
├── 基础UI组件适配
└── 导航框架

Week 7: 同步引擎+便签
├── SyncEngine移动端适配
├── 冲突处理UI
├── 快速便签FAB
└── 离线状态UI

Week 8: 收尾+打包APK
├── 本地搜索
├── 深色主题
├── APK打包（expo prebuild）
└── Bug修复

Phase 3: 收尾（Week 9）
├── 全量测试
├── 桌面端+移动端联调
├── 打包发布
└── 文档编写
```

### 6.3 资源需求

| 资源 | 需求 | 说明 |
|------|------|------|
| 开发机器 | Windows PC（主开发）+ Android手机（测试） | 已具备 |
| 服务器 | 腾讯云（现有106.54.25.161） | 不变 |
| Git仓库 | GitHub（现有） | xuezi-kb |
| API文档 | 复用现有v2 API | 无需修改 |

---

## 七、关键设计决策

### 7.1 为什么选择Electron而不是Tauri？
- 生态成熟，踩坑少
- better-sqlite3原生模块支持好
- electron-builder打包Windows exe成熟稳定
- 雪子已有Electron开发经验（v2）
- Tauri的Rust后端学习成本高

### 7.2 为什么选择Expo而不是纯React Native CLI？
- 开发体验好，Hot Reload快
- expo-sqlite对SQLite支持成熟
- 踩坑少，社区资源丰富
- APK打包流程简单
- 后续可eas build云端打包

### 7.3 为什么本地数据库用SQLite而不是其他？
- 离线优先场景下，SQLite是最成熟的嵌入式数据库
- better-sqlite3（桌面端）和expo-sqlite（移动端）都是同步API，易于理解和维护
- 支持FTS5全文搜索
- 体积小，性能好
- 数据可迁移（跨平台都是同一格式）

### 7.4 为什么不直接用服务器PostgreSQL？
- 网络依赖：断网完全不可用
- 延迟高：每次操作都有网络开销
- 服务器压力大：所有设备都连同一个DB
- 离线场景：无网络时无法工作

### 7.5 同步策略选择（为什么不选CRDT/OT？）
- CRDT（Conflict-free Replicated Data Types）：适合多人协作，本项目单人使用过于复杂
- OT（Operational Transform）：适合富文本编辑，实现复杂
- 本方案（Last-Write-Wins + 字段级合并）：实现简单，满足单人使用场景

---

## 八、风险与对策

| 风险 | 概率 | 影响 | 对策 |
|------|------|------|------|
| Electron打包体积大（>100MB） | 高 | 低 | 已知问题， Electron固有缺陷，接受 |
| better-sqlite3编译问题 | 中 | 中 | 使用prebuild-binary，或切换到sql.js（WASM） |
| 移动端后台同步限制 | 高 | 中 | 依赖系统，后台同步可能延迟；前台时主动同步 |
| 同步冲突处理复杂 | 中 | 中 | 简化冲突类型，先只处理最常见的version_mismatch |
| API接口需要改造 | 低 | 高 | 现有API已支持同步操作（/api/sync/push/pull） |
| Android权限问题 | 低 | 低 | Expo处理好了大部分权限 |

---

## 九、后续步骤

1. **确认架构** → 雪子确认后进入开发
2. **Phase 0** → 初始化项目，搭建脚手架
3. **Phase 1** → 桌面端MVP
4. **Phase 2** → 移动端MVP
5. **Phase 3** → 收尾发布

---

*架构设计完，待雪子确认后启动开发*
