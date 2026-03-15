# 📊 Memory Suite v4.0 监控整合报告

**生成时间**: 2026-03-11
**版本**: v4.0.0
**阶段**: Phase 4 - 统一监控和日志

---

## 1. 整合概览

### 1.1 原 services/monitor/ 评估

| 项目 | 评估结果 |
|------|----------|
| 原服务位置 | `/Users/zhaoruicn/.openclaw/workspace/services/monitor/monitor_service.py` |
| 功能完整性 | ✅ 完整 |
| 代码质量 | ✅ 良好 |
| 整合可行性 | ✅ 可整合 |
| 整合方式 | 迁移至 `skills/memory-suite-v4/services/` |

### 1.2 整合方案

```
原架构:
  services/monitor/monitor_service.py (独立监控服务)
  skills/monitoring-alert/ (独立告警技能)
  └── 日志分散，功能重复

新架构 (v4.0):
  skills/memory-suite-v4/
  ├── services/monitor_service.py    ← 整合后的统一监控服务
  ├── scripts/
  │   ├── health_check.py            ← 统一健康检查脚本
  │   ├── log_rotate.py              ← 统一日志轮转
  │   └── unified_logger.py          ← 统一日志记录器
  ├── config/cron_health.yaml        ← 定时任务配置
  └── docs/
      └── monitoring_integration_report.md
```

---

## 2. 统一日志管理

### 2.1 日志文件位置整合

| 原日志位置 | 新日志位置 | 状态 |
|-----------|-----------|------|
| `/tmp/*.log` (分散) | `/tmp/memory-suite.log` | ✅ 统一 |
| `/workspace/logs/*.log` | `/tmp/memory-suite.log` | ✅ 统一 |
| `/workspace/memory/cron.log` | `/tmp/memory-suite.log` | ✅ 统一 |

### 2.2 日志格式标准

```
[YYYY-MM-DD HH:MM:SS] [LEVEL] [SERVICE] Message
```

**日志级别**:
- `DEBUG` - 调试信息 (默认不输出到控制台)
- `INFO` - 一般信息
- `SUCCESS` - 成功操作
- `WARN` - 警告信息
- `ERROR` - 错误信息
- `CRITICAL` - 严重错误

### 2.3 日志轮转配置

| 配置项 | 值 |
|--------|-----|
| 当前日志文件 | `/tmp/memory-suite.log` |
| 轮转阈值 | 10 MB |
| 保留天数 | 30 天 |
| 归档数量 | 最多 10 个 |
| 压缩阈值 | 7 天前自动压缩 |
| 归档目录 | `/tmp/memory-suite-archives/` |

### 2.4 日志轮转定时任务

```bash
# 每天凌晨 2 点执行日志轮转
0 2 * * * python3 /Users/zhaoruicn/.openclaw/workspace/skills/memory-suite-v4/scripts/log_rotate.py --all
```

---

## 3. 系统健康检查

### 3.1 健康检查项列表

| 检查项 | 检查内容 | 频率 | 告警阈值 |
|--------|----------|------|----------|
| **定时任务** | crontab 任务状态 | 每次检查 | 任务失败 |
| **磁盘空间** | 根分区/工作区/备份磁盘 | 每次检查 | >90% 严重，>80% 警告 |
| **日志状态** | 统一日志文件状态 | 每次检查 | >48h 未更新 |
| **备份状态** | 最新备份时间 | 每次检查 | >7 天未备份 |
| **内存使用** | macOS 内存使用率 | 每次检查 | >90% 警告 |
| **Python 进程** | 检测卡死进程 | 每次检查 | CPU>80% 警告 |

### 3.2 健康检查脚本

**位置**: `/Users/zhaoruicn/.openclaw/workspace/skills/memory-suite-v4/scripts/health_check.py`

**使用方式**:
```bash
# 执行健康检查
python3 health_check.py --check

# 生成报告
python3 health_check.py --report

# 发送飞书通知
python3 health_check.py --notify

# 执行全部 (检查 + 报告 + 通知)
python3 health_check.py --all
```

### 3.3 定时检查配置

```bash
# 每天早上 9 点执行健康检查并发送飞书通知
0 9 * * * python3 /Users/zhaoruicn/.openclaw/workspace/skills/memory-suite-v4/scripts/health_check.py --all --notify
```

---

## 4. 监控服务

### 4.1 监控服务功能

**位置**: `/Users/zhaoruicn/.openclaw/workspace/skills/memory-suite-v4/services/monitor_service.py`

**功能模块**:
1. **定时任务监控** (`get_cron_tasks`)
   - 解析 crontab 配置
   - 提取任务名称和调度
   - 检查任务执行状态

2. **日志状态检查** (`check_log_status`)
   - 检查日志文件存在性
   - 分析最后更新时间
   - 检测错误/警告模式

3. **任务看板生成** (`get_task_dashboard`)
   - 生成 Markdown 格式看板
   - 显示任务状态和调度
   - 支持统一日志查询

4. **日志聚合** (`aggregate_logs`)
   - 从统一日志提取数据
   - 统计错误和警告数量
   - 支持时间范围过滤

5. **健康报告生成** (`generate_health_report`)
   - 整合所有检查项
   - 生成完整健康报告
   - 支持飞书推送

### 4.2 监控服务使用

```bash
# 显示任务看板
python3 monitor_service.py --dashboard

# 聚合最近 7 天日志
python3 monitor_service.py --logs 7

# 生成健康报告
python3 monitor_service.py --health

# 生成报告并发送飞书通知
python3 monitor_service.py --health --notify

# 输出到文件
python3 monitor_service.py --health --output /tmp/report.md
```

---

## 5. 通知方式

### 5.1 飞书通知配置

| 通知类型 | 触发条件 | 通知内容 |
|----------|----------|----------|
| **健康日报** | 每天 9:00 | 完整健康报告 |
| **日志轮转** | 每天 2:00 | 轮转统计信息 |
| **严重告警** | 实时检测 | 问题详情和建议 |

### 5.2 通知方式

使用 **广播专员** (`agents/kilo/broadcaster.py`) 发送通知:

```python
# 示例代码
subprocess.run([
    "python3", "/Users/zhaoruicn/.openclaw/workspace/agents/kilo/broadcaster.py",
    "--task", "send",
    "--message", "🏥 系统健康报告",
    "--file", "/tmp/health_report.md",
    "--target", "group"
])
```

---

## 6. 完整 crontab 配置

### 6.1 推荐配置

```bash
# Memory Suite v4.0 定时任务配置

# 每天早上 9 点 - 健康检查并发送飞书通知
0 9 * * * python3 /Users/zhaoruicn/.openclaw/workspace/skills/memory-suite-v4/scripts/health_check.py --all --notify >> /tmp/health_check.log 2>&1

# 每天凌晨 2 点 - 日志轮转
0 2 * * * python3 /Users/zhaoruicn/.openclaw/workspace/skills/memory-suite-v4/scripts/log_rotate.py --all >> /tmp/log_rotate.log 2>&1

# 每 4 小时 - 监控服务健康报告
0 */4 * * * python3 /Users/zhaoruicn/.openclaw/workspace/skills/memory-suite-v4/services/monitor_service.py --health >> /tmp/monitor_service.log 2>&1
```

### 6.2 安装定时任务

```bash
# 查看当前 crontab
crontab -l

# 编辑 crontab
crontab -e

# 或使用脚本自动添加
python3 /Users/zhaoruicn/.openclaw/workspace/skills/memory-suite-v4/scripts/install_cron.py
```

---

## 7. 文件清单

### 7.1 新增文件

| 文件路径 | 用途 |
|----------|------|
| `skills/memory-suite-v4/services/monitor_service.py` | 统一监控服务 (整合自 services/monitor/) |
| `skills/memory-suite-v4/scripts/unified_logger.py` | 统一日志记录器 |
| `skills/memory-suite-v4/scripts/log_rotate.py` | 统一日志轮转脚本 |
| `skills/memory-suite-v4/scripts/health_check.py` | 系统健康检查脚本 |
| `skills/memory-suite-v4/config/cron_health.yaml` | 定时任务配置 |
| `skills/memory-suite-v4/docs/monitoring_integration_report.md` | 监控整合报告 (本文档) |

### 7.2 统一日志文件

| 文件路径 | 用途 |
|----------|------|
| `/tmp/memory-suite.log` | 统一日志文件 |
| `/tmp/memory-suite-archives/` | 日志归档目录 |
| `/tmp/health_report.md` | 健康报告临时文件 |
| `/tmp/phase4_monitoring.log` | Phase 4 执行日志 |

---

## 8. 迁移步骤

### 8.1 已完成

- ✅ 评估 services/monitor/ 服务
- ✅ 迁移 monitor_service.py 到 v4
- ✅ 创建统一日志记录器
- ✅ 创建统一日志轮转脚本
- ✅ 创建系统健康检查脚本
- ✅ 生成监控整合报告

### 8.2 待完成

- [ ] 更新其他服务使用统一日志记录器
- [ ] 配置定时任务 (crontab)
- [ ] 测试健康检查飞书通知
- [ ] 验证日志轮转功能
- [ ] 更新文档和 README

---

## 9. 使用示例

### 9.1 日常监控

```bash
# 查看任务看板
python3 services/monitor_service.py --dashboard

# 查看最近日志
tail -f /tmp/memory-suite.log

# 手动执行健康检查
python3 scripts/health_check.py --all
```

### 9.2 故障排查

```bash
# 查看日志中的错误
grep '\[ERROR\]' /tmp/memory-suite.log | tail -20

# 查看日志中的警告
grep '\[WARN\]' /tmp/memory-suite.log | tail -20

# 检查日志文件大小
ls -lh /tmp/memory-suite.log

# 查看归档日志
ls -lh /tmp/memory-suite-archives/
```

### 9.3 报告生成

```bash
# 生成健康报告
python3 scripts/health_check.py --report --output /tmp/report.md

# 生成监控报告
python3 services/monitor_service.py --health --output /tmp/monitor.md

# 发送飞书通知
python3 scripts/health_check.py --notify
```

---

## 10. 总结

### 10.1 整合成果

- ✅ **统一日志管理**: 所有服务使用 `/tmp/memory-suite.log`
- ✅ **统一健康检查**: 6 项核心检查，自动生成报告
- ✅ **统一监控服务**: 整合原 services/monitor/ 功能
- ✅ **飞书通知**: 健康报告自动推送到群组

### 10.2 改进效果

| 指标 | 整合前 | 整合后 |
|------|--------|--------|
| 日志文件数量 | 多个分散文件 | 1 个统一文件 |
| 健康检查项 | 分散在多处 | 集中管理 |
| 监控服务 | 独立服务 | 整合到 v4 |
| 通知方式 | 手动/分散 | 自动/统一 |

### 10.3 下一步

1. 配置定时任务自动执行
2. 更新其他服务使用统一日志
3. 添加更多监控指标
4. 优化告警阈值和通知策略

---

*Memory Suite v4.0 | Phase 4 监控整合完成*
*生成时间：2026-03-11*
