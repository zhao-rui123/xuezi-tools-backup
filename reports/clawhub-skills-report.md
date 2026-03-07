# ClawHub 技能包调研报告

**调研时间**: 2026-03-07
**调研范围**: clawhub.com 公开技能包
**评估标准**: 评分 > 3.0，与现有技能互补性

---

## 📊 当前已安装技能（本地）

| 技能名称 | 版本 | 用途 |
|---------|------|------|
| summarize | 1.0.0 | 内容摘要 |
| apple-notes | 1.0.0 | Apple Notes 管理 |
| openai-whisper | 1.0.0 | 语音转文字 |

**本地 Workspace 技能（27个）**:
- stock-screener, stock-analysis - 股票分析
- storage-calc, user-infra - 储能计算
- data-processor, pdf-data-extractor - 数据处理
- report-generator, office-pro, office-generator - 报告生成
- feishu-doc, feishu-wiki, feishu-drive - 飞书集成
- multi-agent-cn, agent-team-orchestration - 多Agent开发
- system-backup, server-monitor, daily-health-check - 系统运维
- git-workflow, project-tracker, knowledge-base - 项目管理
- chart-generator, cad-generator - 可视化
- session-persistence, context-management - 会话管理
- file-management, skill-version-control - 文件管理

---

## 🎯 推荐技能分类

### 一、股票金融类 ⭐⭐⭐⭐⭐

**高优先级**:
| 技能名称 | 评分 | 特点 | 是否推荐 |
|---------|------|------|---------|
| **stock-watcher** | 3.595 | 股票监控 | ✅ 推荐 |
| **tushare-finance** | 3.562 | Tushare数据源 | ✅ 推荐 |
| **a-stock-monitor** | 3.501 | A股监控 | ✅ 推荐 |
| **finnhub-pro** | 2.092 | Finnhub金融API | ⚠️ 备选 |
| **stock-strategy-backtester** | 3.384 | 策略回测 | ✅ 推荐 |
| **manus-stock-analysis** | 3.365 | 股票分析 | ⚠️ 备选 |
| **stock-daily-report** | 3.290 | 日报生成 | ⚠️ 已有 |

**评估**: 
- `stock-watcher` 和 `a-stock-monitor` 可作为现有股票分析的补充
- `tushare-finance` 提供专业金融数据接口，比新浪财经更稳定
- `stock-strategy-backtester` 可扩展投资策略分析能力

---

### 二、飞书集成类 ⭐⭐⭐⭐⭐

**高优先级**:
| 技能名称 | 评分 | 特点 | 是否推荐 |
|---------|------|------|---------|
| **feishu-doc-manager** | 3.579 | 飞书文档管理器 | ✅ 推荐 |
| **feishu-bridge** | 3.573 | 飞书桥接 | ✅ 推荐 |
| **feishu-messaging** | 3.558 | 飞书消息 | ⚠️ 已有 |
| **feishu-docx-powerwrite** | 3.497 | 飞书文档增强 | ✅ 推荐 |
| **feishu-leave-request** | 3.493 | 请假流程 | ❌ 不适用 |
| **feishu-card** | 3.460 | 卡片消息 | ✅ 推荐 |
| **feishu-bitable** | 3.448 | Bitable表格 | ⚠️ 已有 |
| **feishu-memory-recall** | 3.438 | 记忆召回 | ⚠️ 备选 |

**评估**:
- `feishu-doc-manager` 可扩展飞书文档管理能力
- `feishu-docx-powerwrite` 可能支持更丰富的文档格式
- `feishu-card` 支持交互式卡片，提升消息体验

---

### 三、数据处理类 ⭐⭐⭐⭐

**中优先级**:
| 技能名称 | 评分 | 特点 | 是否推荐 |
|---------|------|------|---------|
| **data-analyst** | 3.541 | 数据分析 | ⚠️ 已有 |
| **data-analysis** | 3.533 | 数据分析 | ⚠️ 已有 |
| **deep-scraper** | 3.716 | 深度爬虫 | ✅ 推荐 |
| **playwright-scraper-skill** | 3.709 | Playwright爬虫 | ✅ 推荐 |
| **ai-data-scraper** | 3.526 | AI数据爬取 | ⚠️ 备选 |

**评估**:
- `deep-scraper` 和 `playwright-scraper-skill` 可用于电价数据自动抓取
- 可替代部分手动数据更新流程

---

### 四、PDF/文档类 ⭐⭐⭐⭐

**中优先级**:
| 技能名称 | 评分 | 特点 | 是否推荐 |
|---------|------|------|---------|
| **nano-pdf** | 3.708 | PDF编辑 | ✅ 推荐 |
| **pdf-extract** | 3.569 | PDF提取 | ⚠️ 已有 |
| **pdf-text-extractor** | 3.549 | 文本提取 | ⚠️ 已有 |
| **pdf-generator** | 3.482 | PDF生成 | ⚠️ 已有 |
| **compress-pdf** | 3.421 | PDF压缩 | ⚠️ 备选 |
| **pdf-ocr** | 3.383 | OCR识别 | ⚠️ 已有 |

**评估**:
- `nano-pdf` 评分最高，支持自然语言编辑PDF
- 可作为现有 PDF 处理能力的补充

---

### 五、Excel/办公类 ⭐⭐⭐⭐

**中优先级**:
| 技能名称 | 评分 | 特点 | 是否推荐 |
|---------|------|------|---------|
| **microsoft-excel** | 3.616 | Excel操作 | ✅ 推荐 |
| **excel-xlsx** | 3.585 | XLSX处理 | ⚠️ 已有 |
| **excel-weekly-dashboard** | 3.512 | 周报仪表板 | ✅ 推荐 |

**评估**:
- `excel-weekly-dashboard` 适合生成周报/月报
- 可与现有的 `report-generator` 配合使用

---

### 六、图表可视化类 ⭐⭐⭐

**中优先级**:
| 技能名称 | 评分 | 特点 | 是否推荐 |
|---------|------|------|---------|
| **chart-image** | 3.600 | 图表生成 | ✅ 推荐 |
| **chart-splat** | 3.302 | 图表工具 | ⚠️ 备选 |

**评估**:
- `chart-image` 可与 `chart-generator` 形成互补

---

### 七、定时任务类 ⭐⭐⭐⭐

**高优先级**:
| 技能名称 | 评分 | 特点 | 是否推荐 |
|---------|------|------|---------|
| **cron-mastery** | 3.618 | Cron高级功能 | ✅ 推荐 |
| **cron-scheduling** | 3.552 | 定时调度 | ⚠️ 已有 |
| **cron-doctor** | 3.411 | Cron诊断 | ✅ 推荐 |
| **cron-health-check** | 3.303 | 健康检查 | ⚠️ 已有 |

**评估**:
- `cron-mastery` 提供更强大的定时任务管理
- `cron-doctor` 可诊断定时任务问题

---

### 八、GitHub类 ⭐⭐⭐

**低优先级**:
| 技能名称 | 评分 | 特点 | 是否推荐 |
|---------|------|------|---------|
| **github** | 3.801 | GitHub操作 | ⚠️ 已有 |
| **openclaw-github-assistant** | 3.621 | GitHub助手 | ⚠️ 备选 |
| **github-trending-cn** | 3.475 | 热门趋势 | ⚠️ 备选 |
| **github-pages-auto-deploy** | 3.317 | 自动部署 | ✅ 推荐 |

**评估**:
- `github-pages-auto-deploy` 可简化网站部署流程

---

### 九、Web/爬虫类 ⭐⭐⭐

**中优先级**:
| 技能名称 | 评分 | 特点 | 是否推荐 |
|---------|------|------|---------|
| **web-deploy-github** | 3.486 | GitHub部署 | ✅ 推荐 |
| **desearch-web-search** | 3.474 | 网页搜索 | ⚠️ 备选 |
| **web-pilot** | 3.461 | 网页导航 | ⚠️ 备选 |
| **web** | 3.460 | Web开发 | ⚠️ 已有 |

---

### 十、其他值得关注的技能

| 类别 | 技能名称 | 评分 | 推荐度 |
|-----|---------|------|--------|
| 财务 | **financial-calculator** | 3.579 | ✅ 推荐 |
| 天气 | **weather** | 3.831 | ⚠️ 备选 |
| 提醒 | **reminder** | 3.546 | ⚠️ 备选 |
| 同步 | **obsidian-sync** | 3.488 | ⚠️ 备选 |
| 监控 | **web-monitor** | 3.467 | ✅ 推荐 |
| 备份 | **openclaw-backup** | 3.635 | ⚠️ 已有 |
| 多Agent | **agent-team-orchestration** | 3.564 | ⚠️ 已有 |
| Notion | **notion** | 3.755 | ⚠️ 备选 |

---

## 🏆 最终推荐清单

### 🔥 高优先级（立即安装）

1. **stock-watcher** (3.595) - 股票监控，补充现有股票分析
2. **tushare-finance** (3.562) - 专业金融数据，替代新浪财经
3. **feishu-doc-manager** (3.579) - 飞书文档管理增强
4. **deep-scraper** (3.716) - 深度爬虫，自动抓取电价数据
5. **playwright-scraper-skill** (3.709) - Playwright爬虫，更稳定的网页抓取
6. **cron-mastery** (3.618) - 高级定时任务管理
7. **cron-doctor** (3.411) - 定时任务诊断

### ⭐ 中优先级（按需安装）

8. **stock-strategy-backtester** (3.384) - 股票策略回测
9. **feishu-docx-powerwrite** (3.497) - 飞书文档增强
10. **feishu-card** (3.460) - 卡片消息
11. **nano-pdf** (3.708) - PDF自然语言编辑
12. **microsoft-excel** (3.616) - Excel高级操作
13. **excel-weekly-dashboard** (3.512) - 周报仪表板
14. **chart-image** (3.600) - 图表生成
15. **web-monitor** (3.467) - 网站监控
16. **github-pages-auto-deploy** (3.317) - 自动部署

### 💡 低优先级（备选）

17. **weather** (3.831) - 天气查询（如需要）
18. **reminder** (3.546) - 提醒功能（如需要）
19. **notion** (3.755) - Notion集成（如迁移使用）
20. **openclaw-backup** (3.635) - 备份增强（评估现有备份）

---

## 📋 安装命令

```bash
# 高优先级
clawhub install stock-watcher
clawhub install tushare-finance
clawhub install feishu-doc-manager
clawhub install deep-scraper
clawhub install playwright-scraper-skill
clawhub install cron-mastery
clawhub install cron-doctor

# 中优先级
clawhub install stock-strategy-backtester
clawhub install feishu-docx-powerwrite
clawhub install feishu-card
clawhub install nano-pdf
clawhub install microsoft-excel
clawhub install excel-weekly-dashboard
clawhub install chart-image
clawhub install web-monitor
clawhub install github-pages-auto-deploy
```

---

## 🎯 建议开发方向

基于现有技能缺口，建议优先开发以下技能：

1. **电价数据自动更新器** - 结合 deep-scraper，自动抓取各省发改委电价文件
2. **储能项目智能排布优化器** - 基于现有排布系统，加入AI优化算法
3. **电费清单智能分析器** - 结合 nano-pdf，自动解析国网PDF电费清单
4. **股票组合风险分析器** - 结合 tushare-finance，提供组合风险分析
5. **飞书日报自动生成器** - 结合 feishu-doc-manager，自动生成项目日报

---

*报告生成时间: 2026-03-07*
*数据来源: clawhub.com*
