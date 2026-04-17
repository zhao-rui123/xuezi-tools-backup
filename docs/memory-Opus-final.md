# Memory系统优化方案 (Opus Final)

> 前提：memory search (jieba + FTS5 + embedding) 已接管全文检索，每日记忆文件的定位从"存档"转为"提炼"。

---

## 1. 格式优化

### 问题
当前每日 `.md` 是对话转录（用户消息 + 助手回复摘要），噪音极高：包含 internal context、exec output、系统消息。搜索系统已能检索原始对话，重复存储无意义。

### 方案：结构化三段式

```markdown
# YYYY-MM-DD

## DECISION
- [标签] 一句话决策 + 原因
  - 例：[架构] 选方案B(app-server)，理由：支持多轮会话

## TASK
- [done] 修复备份脚本路径bug
- [wip] Codex HTTP API 方案研究
- [todo] 飞书机器人直连Codex

## LEARNED
- codex exec 每次起新进程，无法保持会话状态
- ccr 可与后台 cc 共存，不冲突
```

### 规则
- 每条 ≤120 字
- 不存对话原文，只存结论
- 标签固定集合：`架构/修复/配置/部署/研究/需求`

---

## 2. 最佳触发时机

### 问题
当前 30 分钟 session-snapshot 与工作节奏脱节，空闲时无意义触发，关键时刻又错过。

### 方案：事件驱动 + 日终兜底

| 触发点 | 时机 | 动作 |
|--------|------|------|
| **session-end** | 每次会话结束 | 提取本次会话的 DECISION/TASK/LEARNED → 追加到当日 `.md` |
| **日终汇总** | 23:00 | 合并当日所有条目，去重，生成最终版 |
| ~~session-snapshot~~ | ~~每30分钟~~ | **砍掉** — 对记忆质量无贡献 |

### 实现
- session-end hook 已存在（OMC `session-end` hook），在其中调用提取脚本
- 日终汇总用现有 cron 机制，添加一个 23:00 的 job

---

## 3. 去重机制

### 问题
无去重 → 同一话题反复写入，文件膨胀，搜索结果冗余。

### 三层去重

```
写入时 ──→ 日终 ──→ 跨日
(实时)    (批量)   (索引)
```

#### 层1：写入时去重
- 新条目 → jieba 提取 top-3 关键词
- 与当日已有条目比较，关键词重叠 ≥2/3 → 合并（保留更完整的版本）

#### 层2：日终去重
- 23:00 汇总时，对所有条目按类别分组
- 同类别内用编辑距离比较，相似度 >70% → 合并

#### 层3：跨日索引去重
- SQLite chunks 表已有 hash 字段
- 写入索引前检查 hash，已存在 → 跳过
- 避免搜索结果出现重复 chunk

### 最简实现（session-snapshot.py 改动）

```python
import hashlib

def is_duplicate(new_text, existing_entries):
    """写入前去重检查"""
    new_hash = hashlib.md5(new_text.strip().encode()).hexdigest()[:16]
    for entry in existing_entries:
        if hashlib.md5(entry.strip().encode()).hexdigest()[:16] == new_hash:
            return True
    # 关键词重叠检查
    import jieba
    new_kw = set(jieba.analyse.extract_tags(new_text, topK=3))
    for entry in existing_entries:
        entry_kw = set(jieba.analyse.extract_tags(entry, topK=3))
        if len(new_kw & entry_kw) >= 2:
            return True
    return False
```

---

## 总结

| 维度 | 现状 | 优化后 |
|------|------|--------|
| 格式 | 对话转录，噪音高 | 结构化三段式（DECISION/TASK/LEARNED） |
| 触发 | 30min 定时 + 08:00 提取 | session-end 事件驱动 + 23:00 日终兜底 |
| 去重 | 无 | 三层：写入时/日终/跨日索引 |
| 文件大小 | 日均 5-15KB | 预计 1-3KB |
| 搜索质量 | 大量重复 chunk | 精准命中，无冗余 |
