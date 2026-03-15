# OpenClaw 系统优化报告

## 📊 当前状态

| 指标 | 数值 |
|------|------|
| 技能包总数 | 83个 (53主要 + 24归档 + 6套件) |
| 定时任务 | 22个 |
| 服务目录 | 10个服务 |
| 磁盘使用 | 23% (43GB/228GB) |
| 大文件 | 1个 (>10MB) |

---

## 🚨 发现的问题

### 1. 服务层重复功能（高优先级）

| 服务 | 功能 | 与Memory Suite v4关系 | 建议 |
|------|------|----------------------|------|
| `services/knowledge/` | 知识提取 | **重复** - v4已有knowledge模块 | ❌ 停用 |
| `services/action/` | 任务生成、周报 | **可整合** - 与v4 evolution部分重叠 | ⚠️ 评估 |
| `services/monitor/` | 系统监控 | **独立** - 保持运行 | ✅ 保留 |
| `services/skill/` | 技能包审计 | **可整合** - 与v4 skill-eval重叠 | ⚠️ 评估 |
| `services/git/` | 自动提交 | **独立** - 保持运行 | ✅ 保留 |
| `services/backup/` | 备份服务 | **可整合** - 与v4 backup_helper重叠 | ⚠️ 评估 |
| `services/notify/` | 通知服务 | **独立** - 保持运行 | ✅ 保留 |
| `services/script/` | 脚本服务 | **未知** - 需检查 | ❓ 检查 |

### 2. 定时任务冗余

```
问题任务:
1. services/knowledge/smart_extractor.py (01:00)
   → 与 v4 knowledge-sync (06:00) 功能重复

2. services/action/task_generator.py (08:00)
   → 与 v4 evolution-daily (23:00) 部分重叠

3. services/action/weekly_reporter.py (22:00周日)
   → 与 v4 evolution-report (09:00每月2号) 部分重叠

4. services/skill/skill_service.py (03:00周一)
   → 与 v4 skill-eval (22:00周日) 重叠
```

### 3. 已归档但未清理

```
skills/archived/ 下有24个归档包:
- 部分可能是旧版本，可以删除
- 建议保留最近3个版本，其余删除
```

### 4. 套件技能包检查

```
skills/suites/ 下有6个套件:
- document-suite
- file-transfer-suite
- stock-analysis-suite
- system-ops-suite
需要确认是否都还在使用
```

---

## 💡 优化建议

### Phase 1: 停用重复服务（立即执行）

```bash
# 1. 停用 services/knowledge/ 定时任务
crontab -l | grep -v "smart_extractor.py" | crontab -
mv services/knowledge services/archived/services-knowledge-backup-$(date +%Y%m%d)

# 2. 评估 services/action/ 是否可以停用
# 如果 v4 evolution 功能足够，可以停用
```

### Phase 2: 整合重叠功能（本周完成）

- 将 `services/skill/` 功能整合到 v4 `skill-eval`
- 将 `services/backup/` 功能整合到 v4 `backup_helper`
- 统一通知机制，全部通过 v4 `notifier.py`

### Phase 3: 清理归档文件（本月完成）

- 清理 `skills/archived/` 中超过3个月的老版本
- 清理 `services/archived/` 中已停用的服务

### Phase 4: 统一监控（可选）

- 将 `services/monitor/` 整合到 v4 健康检查
- 统一日志格式和存储位置

---

## 📈 预期效果

| 指标 | 当前 | 优化后 | 减少 |
|------|------|--------|------|
| 定时任务 | 22个 | 15个 | -32% |
| 服务目录 | 10个 | 5个 | -50% |
| 技能包总数 | 83个 | 60个 | -28% |
| 维护复杂度 | 高 | 中 | -40% |

---

## 🎯 推荐执行顺序

1. **立即** - 停用 services/knowledge/ （确认重复）
2. **今天** - 检查 services/action/ 和 services/skill/
3. **本周** - 清理 skills/archived/ 老版本
4. **本月** - 完成服务层整合

---

## ❓ 需要用户确认

1. **services/action/** 的任务生成和周报功能，v4的evolution模块是否可以替代？
2. **services/skill/** 的技能包审计，是否需要保留独立运行？
3. **skills/archived/** 中的旧版本，是否可以删除3个月前的？
4. **services/monitor/** 的健康检查，是否需要整合到v4？
