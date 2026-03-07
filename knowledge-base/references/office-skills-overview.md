# ClawHub Office 办公软件技能包整理

> 来源：ClawHub 搜索
> 整理时间：2026-03-06

---

## 1. Office Document Specialist Suite

| 属性 | 内容 |
|------|------|
| 作者 | Robert-Janssen |
| 下载量 | 3.3k |
| 评分 | 1星 |
| 版本 | v1.0.2 |

**功能概述**
专业 Office 文档处理套件，专门用于创建、编辑和分析 Microsoft Office 文档。支持 Word、Excel、PowerPoint 三种格式。

**Word 功能**
- 创建编辑专业报告
- 管理样式
- 插入表格和图片

**Excel 功能**
- 数据分析
- 自动生成电子表格
- 复杂格式设置

**PowerPoint 功能**
- 从结构化数据自动生成幻灯片

**适用场景**
- 自动化报告生成
- 批量文档处理
- 专业文档排版

**安装说明**
提供 setup.sh 脚本自动初始化 Python 虚拟环境和依赖

---

## 2. Office

| 属性 | 内容 |
|------|------|
| 作者 | ivangdavila |
| 下载量 | 3.1k |
| 评分 | 11星 |
| 版本 | v1.0.0 |

**功能概述**
最全面的 Office 办公套件指南，涵盖 Microsoft 365 和 Google Workspace 的公式、格式设置和自动化。

**Excel / Google Sheets**
- VLOOKUP 和 XLOOKUP 查找功能
- SUMIF 和 COUNTIF 条件统计
- INDEX MATCH 灵活匹配
- IF 逻辑判断
- 数据透视表创建

**Word / Google Docs**
- 样式设置（Heading 1/2/3）
- 自动生成目录
- 页码设置
- 邮件合并功能
- 分节符管理

**PowerPoint / Slides**
- 幻灯片母版设置
- 6x6 原则（每页最多6点，每点最多6词）
- 动画设置
- 演讲者视图使用

**办公行政**
- 办公用品库存管理
- 供应商管理
- 空间规划
- 工位预订系统

**特色**
- 详细的故障排除指南
- 快速参考表格
- 适合日常办公问题查询

---

## 3. Office To Md V2

| 属性 | 内容 |
|------|------|
| 作者 | Lkyyyy320 |
| 下载量 | 617 |
| 评分 | 2星 |
| 版本 | v0.1.0 |

**⚠️ 安全提示**
VirusTotal 标记为 Suspicious，建议审查后使用

**功能**
将 Office 文档转换为 Markdown 格式，支持 PDF、DOC、DOCX、PPTX，特别支持旧版 .doc 文件的文本提取和基本格式保留。

**技术实现**
- PDF: 使用 pdf-parse 提取文本
- Word docx: 使用 mammoth + turndown 保留格式
- 旧版 Word doc: 使用 word-extractor 提取，支持中文编码
- PowerPoint pptx: 使用 python-pptx 进行基本文本提取

**使用方式**
1. 直接 exec 调用
2. 使用包装函数
3. 完整的 OpenClaw 集成函数

**限制**
- 不提取图片
- 复杂格式可能无法完全保留
- 表格转换可能不完美
- 不支持密码保护文件

---

## 4. PLS Office Docs

| 属性 | 内容 |
|------|------|
| 作者 | mattvalenta |
| 下载量 | 299 |
| 评分 | 0星 |
| 版本 | v1.0.0 |

**功能概述**
专业级的文档生成和处理技能，支持 PDF、DOCX、XLSX、PPTX 四种格式的创建、读取、编辑和内容提取。

**PDF 格式**
- 创建: fpdf, reportlab
- 读取: pdfplumber, pymupdf
- 编辑: pypdf

**DOCX 格式**
- 创建/读取/编辑: python-docx

**XLSX 格式**
- 创建/读取: openpyxl, pandas
- 编辑: openpyxl

**PPTX 格式**
- 创建/读取/编辑: python-pptx

**PDF 核心功能**
- 创建文档
- 插入图片
- 文本提取
- 合并拆分 PDF

**Word 核心功能**
- 创建文档
- 添加表格/图片/列表
- 读取内容

**Excel 核心功能**
- 创建工作簿
- 公式计算
- 添加图表
- 单元格格式化
- Pandas 集成

**PowerPoint 核心功能**
- 创建演示文稿
- 添加幻灯片
- 插入图片表格

**典型工作流**
- 月度报告自动生成
- 数据导出到 Excel 并添加图表
- 带图表的 PDF 报告生成

---

## 5. office-generator（本地已安装）

| 属性 | 内容 |
|------|------|
| 位置 | ~/.openclaw/workspace/skills/office-generator |

**功能概述**
使用 Python 生成和编辑 Word docx 和 Excel xlsx 文件。

**Word 功能**
- 文档创建
- 标题/段落/列表
- 表格
- 图片插入
- 文字格式（字体/颜色/对齐）

**Excel 功能**
- 工作簿创建
- 单元格格式
- 公式计算
- 图表（柱状图/折线图）
- 数据处理

**数据处理**
- 结合 pandas 导出 DataFrame 到 Excel
- 多 sheet 管理

**完整示例**
提供报告生成器，一键生成 Word + Excel 双版本报告

---

## 推荐选择

| 需求场景 | 推荐技能包 | 说明 |
|----------|-----------|------|
| 全面学习 Office 技能 | Office | 涵盖 M365 和 G Suite |
| 专业文档生成 | PLS Office Docs / Office Document Specialist Suite | 功能全面 |
| 文档转 Markdown | Office To Md V2 | ⚠️ 注意安全性 |
| 简单快速生成 Word/Excel | office-generator | 本地已有，开箱即用 |
| 批量报告自动化 | Office Document Specialist Suite | 专业自动化 |
