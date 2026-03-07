# 本地技能包索引

> 自定义开发的技能包清单
> 
> 位置: `~/.openclaw/workspace/skills/`

---

## 已安装技能包

### 1. office-pro

| 属性 | 内容 |
|------|------|
| **位置** | `skills/office-pro/` |
| **创建时间** | 2026-03-06 |
| **状态** | ✅ 已部署 |
| **功能** | Office 文档生成和处理套件 |

**包含脚本：**
- `word_report_generator.py` - Word 报告生成
- `excel_analyzer.py` - Excel 数据分析 + 图表
- `pptx_generator.py` - PPT 批量生成
- `pdf_processor.py` - PDF 合并/拆分/水印
- `format_converter.py` - 格式转换
- `batch_processor.py` - 批量文档处理

**参考文档：**
- [Word 处理指南](../skills/office-pro/references/word_guide.md)
- [Excel 处理指南](../skills/office-pro/references/excel_guide.md)
- [PPT 处理指南](../skills/office-pro/references/pptx_guide.md)
- [API 参考](../skills/office-pro/references/api_reference.md)

**使用场景：**
- 储能项目报告生成
- 股票分析报表导出
- 批量文档处理

---

### 2. system-backup

| 属性 | 内容 |
|------|------|
| **位置** | `skills/system-backup/` |
| **创建时间** | 2026-03-06 |
| **状态** | ✅ 已部署 |
| **功能** | OpenClaw 系统备份恢复套件 |

**包含脚本：**
- `daily-backup.sh` - 每日增量备份（Memory + Skills + Config）
- `monthly-archive.sh` - 月度归档（tar.gz）
- `restore.sh` - 恢复工具

**参考文档：**
- [恢复指南](../skills/system-backup/references/restore.md)

**定时任务：**
```cron
# 每日 22:00 - 增量备份
0 22 * * * skills/system-backup/scripts/daily-backup.sh

# 每月 1号 03:00 - 归档打包
0 3 1 * * skills/system-backup/scripts/monthly-archive.sh
```

**备份位置：**
```
/Volumes/cu/ocu/
├── memory/              # Memory 文件
├── skills/              # 系统技能包
├── workspace-skills/    # 自定义技能包
├── openclaw-config/     # OpenClaw 配置（新增）
└── archives/            # 月度归档 tar.gz
```

**使用场景：**
- 日常数据保护
- 系统灾难恢复
- 环境迁移

---

### 3. stock-analysis-pro

| 属性 | 内容 |
|------|------|
| **位置** | `skills/stock-analysis-pro/` |
| **创建时间** | 2026-03-07 |
| **版本** | v2.0.0 |
| **状态** | ✅ 已部署 |
| **功能** | 专业股票分析系统（A股+港股） |

**核心功能：**
- **数据源融合**：新浪财经 + 雪球 + 腾讯财经
- **技术指标**：MA5/MA10/MA20、RSI、趋势判断、偏离度
- **形态识别**：杯柄形态、双底(W底)、头肩底
- **估值策略**：PB-ROE、PEG、综合估值评分
- **深度分析**：盈利能力、成长性、财务健康、估值分位

**包含模块：**
- `core/data_fetcher.py` - 多源数据获取
- `core/pattern_recognition.py` - 技术形态识别
- `core/valuation.py` - 估值策略筛选
- `core/deep_analysis.py` - 深度四维度分析
- `core/daily_report.py` - 日报生成与推送

**CLI命令：**
```bash
# 生成日报
python3 -m stock_analysis_pro daily

# 发送日报到飞书
python3 -m stock_analysis_pro daily --send-feishu

# 深度分析单股
python3 -m stock_analysis_pro analyze 002460 --name "赣锋锂业"

# 形态识别
python3 -m stock_analysis_pro pattern 002460

# 估值筛选
python3 -m stock_analysis_pro screen
```

**Python API：**
```python
from stock_analysis_pro import deep_analyze, scan_patterns, valuation_screen

# 深度分析
report = deep_analyze("002460", "赣锋锂业")

# 形态扫描
patterns = scan_patterns(["002460", "000725"])

# 估值筛选
results = valuation_screen(["002460", "000725"])
```

**定时任务：**
```cron
# 工作日 16:30 - 日报推送（港股16:10收盘后）
30 16 * * 1-5 skills/stock-analysis-pro/scripts/daily_push.sh
```

**参考文档：**
- [详细文档](../references/stock-analysis-pro.md)
- [技能包 SKILL.md](../skills/stock-analysis-pro/SKILL.md)

**使用场景：**
- 自选股每日监控
- 技术形态自动识别
- 估值策略筛选
- 个股深度研究

---

## 技能包开发规范

### 标准结构
```
skill-name/
├── SKILL.md              # 主文档（必需）
├── scripts/              # 可执行脚本
│   └── *.sh / *.py
├── references/           # 参考文档
│   └── *.md
└── assets/               # 资源文件
    └── templates/
```

### SKILL.md 模板
```markdown
---
name: skill-name
description: 描述... Use when ...
---

# 技能名称

## 功能概述
...

## 使用方法
...

## 脚本参考
...
```

### 命名规范
- 使用小写字母、数字和连字符
- 动词开头，描述功能
- 例如：`system-backup`, `office-pro`, `data-processor`

---

## 待开发技能包

| 名称 | 功能 | 优先级 | 来源 |
|------|------|--------|------|
| pdf-ocr-pro | PDF OCR + 表格提取 | ⭐⭐⭐⭐⭐ | 国网电费清单处理 |
| stock-data-enhanced | 股票数据源增强（Tushare） | ⭐⭐⭐⭐ | stock-watcher |
| chart-generator-pro | 专业图表生成 | ⭐⭐⭐⭐ | chart-image |
| web-monitor | 网站监控 | ⭐⭐⭐ | ClawHub |
| data-scraper | 数据爬虫 | ⭐⭐⭐ | deep-scraper |

---

## 更新记录

| 日期 | 更新内容 |
|------|----------|
| 2026-03-06 | 创建 office-pro 技能包 |
| 2026-03-06 | 创建 system-backup 技能包 |
| 2026-03-07 | 创建 stock-analysis-pro v2.0.0 技能包 |

---

*最后更新: 2026-03-07*
