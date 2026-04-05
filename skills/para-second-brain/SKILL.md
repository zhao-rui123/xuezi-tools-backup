# PARA Second Brain

Organize your knowledge using PARA (Projects, Areas, Resources, Archive) — then make it ALL searchable.

## What is PARA?

| Category | Description | Examples |
|----------|-------------|----------|
| **Projects** | Active work with end dates | "Redesign homepage", "Launch MVP" |
| **Areas** | Ongoing responsibilities | "Health", "Finances", "Career" |
| **Resources** | Reference material | "Cooking recipes", "Book notes" |
| **Archive** | Completed/inactive items | Old projects, past events |

## Directory Structure

```
workspace/
├── MEMORY.md          # Curated long-term memory
├── memory/
│   └── YYYY-MM-DD.md  # Daily raw logs
└── notes/
    ├── projects/      # Active work with end dates
    ├── areas/         # Ongoing responsibilities
    ├── resources/     # Reference material
    │   └── templates/
    └── archive/       # Completed/inactive items
```

## Setup

### 1. Create Directory Structure

```bash
mkdir -p memory notes/projects notes/areas notes/resources/templates notes/archive
```

### 2. Make Notes Searchable (The Symlink Trick)

```bash
ln -s /path/to/workspace/notes /path/to/workspace/memory/notes
```

This enables `memory_search` to find content in your entire PARA structure.

## Memory Flush Protocol

Monitor context usage with `session_status`. Before compaction:

| Context % | Action |
|-----------|--------|
| < 50% | Normal operation |
| 50-70% | Write key points after exchanges |
| 70-85% | Active flushing — write important stuff NOW |
| > 85% | Emergency flush — full summary before next response |

## Writing Rules

- If it has future value, write it down NOW
- Don't rely on "mental notes" — they don't survive restarts
- Text > Brain 📝

## Memory Flush Checklist

Before session ends:
- Key decisions documented?
- Action items captured?
- New learnings written?
- Open loops noted for follow-up?

## PARANotes Structure

### Projects (notes/projects/)
Active work with deadlines:
- "零碳园区方案.md"
- "储能项目测算.md"

### Areas (notes/areas/)
Ongoing responsibilities:
- "健康追踪.md"
- "财务管理.md"

### Resources (notes/resources/)
Reference material:
- "储能知识.md"
- "股票分析框架.md"

### Archive (notes/archive/)
Completed projects:
- "XueziKB开发记录.md"

---

*Your agent's memory just got a massive upgrade. Full semantic search across your entire knowledge base — not just MEMORY.md.*
