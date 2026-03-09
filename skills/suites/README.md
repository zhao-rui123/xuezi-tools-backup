# 技能包套件 (Skill Suites)

**创建时间**: 2026-03-09  
**套件数量**: 4个  
**整合技能包**: 12个

---

## 📦 套件列表

### 1. 股票分析套件 (stock-analysis-suite)
**整合技能包**: 4个
- stock-screener
- stock-analysis-pro
- tushare-stock-datasource
- xueqiu-stock-client

**功能**: 一站式股票分析解决方案
- 股票筛选
- 深度分析
- 数据源
- 资讯客户端

**使用**:
```bash
cd stock-analysis-suite
python3 suite_runner.py --full-analysis
```

---

### 2. 系统运维套件 (system-ops-suite)
**整合技能包**: 3个
- system-backup
- system-guard
- system-maintenance

**功能**: 一站式系统运维解决方案
- 备份恢复
- 安全扫描
- 维护监控

**使用**:
```bash
cd system-ops-suite
python3 suite_runner.py --health-check
```

---

### 3. 文档处理套件 (document-suite)
**整合技能包**: 4个
- office-pro
- pdf-data-extractor
- data-processor
- chart-generator

**功能**: 一站式文档处理解决方案
- Office文档
- PDF处理
- 数据分析
- 图表生成

**使用**:
```bash
cd document-suite
python3 suite_runner.py --generate-report data.csv
```

---

### 4. 文件传输套件 (file-transfer-suite)
**整合技能包**: 1个
- file-sender (已整合多个功能)

**功能**: 一站式文件传输解决方案
- 多方式发送
- 文件管理
- Mac操作

**使用**:
```bash
cd file-transfer-suite
python3 suite_runner.py --send file.txt "说明"
```

---

## 📊 整合统计

| 阶段 | 内容 | 结果 |
|------|------|------|
| 第一阶段 | 合并重复功能 | 57 → 49个 (-8个) |
| 第二阶段 | 归档过时技能 | 49 → 44个 (-5个) |
| 第三阶段 | 创建套件 | 44个 + 4个套件 |

**最终状态**:
- 核心技能包: 44个
- 技能包套件: 4个
- 已归档: 13个

---

## 🎯 套件优势

1. **统一入口** - 一个命令访问全套功能
2. **简化使用** - 不需要记住多个技能包路径
3. **统一管理** - 统一配置和定时任务
4. **易于分享** - 套件化更易于分享和使用

---

## 🚀 快速使用

```bash
# 进入套件目录
cd ~/.openclaw/workspace/skills/suites/[套件名]

# 查看帮助
python3 suite_runner.py --help

# 运行完整功能
python3 suite_runner.py --full
```

---

*技能包套件化管理方案*
