---
name: office-pro
description: Professional Office document generation and processing suite with AI-powered chart recommendation and intelligent data analysis. Supports Word, Excel, PowerPoint creation, conversion, templates, and advanced formatting.
---

# Office Pro - 专业办公文档处理套件 (完整版)

综合性的 Office 文档处理技能包，支持 Word、Excel、PowerPoint、PDF 的创建、编辑、转换和分析。

## 完整功能列表

### 1. Word 文档处理
- ✅ 文档创建和编辑
- ✅ 模板驱动文档生成
- ✅ 图表嵌入（静态图片）
- ✅ 自动目录生成
- ✅ 页眉页脚设置
- ✅ 页码自动编号
- ✅ 脚注和尾注
- ✅ 书签功能
- ✅ 文档加密保护
- ✅ 邮件合并（批量生成）
- ✅ 表格和样式管理

### 2. Excel 数据处理
- ✅ 工作簿/工作表创建
- ✅ 数据导入导出
- ✅ 公式计算
- ✅ 图表生成（柱状图、折线图、饼图）
- ✅ 条件格式设置（色阶、数据条）
- ✅ 数据验证（下拉列表等）
- ✅ 数据透视表
- ✅ 冻结窗格
- ✅ 自动筛选
- ✅ 7种专业样式风格

### 3. PowerPoint 演示文稿
- ✅ 幻灯片创建和编辑
- ✅ 7种专业样式风格
- ✅ 母版设计应用
- ✅ 图表和表格插入
- ✅ 批量幻灯片生成
- ✅ 演讲者备注
- ✅ 章节分隔页
- ✅ 双栏布局
- ✅ 进度条

### 4. 智能功能
- ✅ 智能图表推荐（根据数据自动选择图表类型）
- ✅ AI 智能数据分析
- ✅ 自然语言输入生成报告
- ✅ 异常数据检测
- ✅ 统计信息自动生成
- ✅ 洞察建议

### 5. 高级图表
- ✅ 热力图
- ✅ 甘特图
- ✅ 漏斗图
- ✅ 雷达图
- ✅ 词云图
- ✅ 瀑布图
- ✅ 箱线图
- ✅ 树图

### 6. 模板市场
- ✅ Word 组合模板
- ✅ Excel 模板（销售、财务、项目、KPI）
- ✅ PPT 模板（商务、季度回顾、产品发布、投资路演）
- ✅ 图表模板

### 7. 数据源支持
- ✅ CSV/Excel/JSON 文件
- ✅ REST API
- ✅ 数据库（SQLite/MySQL/PostgreSQL）
- ✅ 云存储（S3/OSS）

### 8. 格式转换
- ✅ Word ↔ Excel 互转
- ✅ Excel → Word（表格）
- ✅ Word → PPT
- ✅ Excel → PPT
- ✅ Office 转 Markdown
- ✅ Word ↔ PDF
- ✅ PPT 转图片

### 9. 批量处理
- ✅ 批量合并 Excel
- ✅ 批量生成报告
- ✅ 批量文档转换

### 10. 交互式报告
- ✅ HTML 交互式报告
- ✅ KPI 卡片展示
- ✅ 动态图表（Chart.js）
- ✅ 数据表格交互

### 11. PDF 处理
- ✅ PDF 创建
- ✅ 多 PDF 合并/拆分
- ✅ 文本提取
- ✅ 图片插入
- ✅ 密码保护

---

## 快速开始

### Word 文档
```python
from core import DocumentWithCharts

doc = DocumentWithCharts()
doc.add_title("月度报告")
doc.add_chart("bar", data, title="销售趋势")
doc.add_table(data)
doc.save("report.docx")

# 添加目录
from core import add_word_toc
add_word_toc("report.docx", "report_with_toc.docx")

# 文档保护
from core import protect_word_document
protect_word_document("report.docx", "protected.docx", "password123")
```

### Excel 专业报表
```python
from core import create_professional_excel, ExcelTemplateLibrary

# 使用样式创建
create_professional_excel(data, "report.xlsx", style="blue")

# 使用模板
from core import create_excel_with_template
create_excel_with_template("sales_monthly", data, "sales.xlsx")
create_excel_with_template("financial_report", data, "financial.xlsx")
create_excel_with_template("kpi_dashboard", data, "kpi.xlsx")

# 条件格式
from core import excel_add_conditional_format
excel_add_conditional_format("report.xlsx", "formatted.xlsx", "B2:B100")
```

### PowerPoint 演示文稿
```python
from core import create_professional_ppt, create_ppt_with_template

# 创建专业PPT
create_professional_ppt(
    "presentation.pptx",
    title="年度总结",
    style="corporate",
    slides=[
        {"type": "title", "title": "年度总结", "subtitle": "2024"},
        {"type": "content", "title": "目录", "bullets": ["业绩", "分析", "计划"]},
        {"type": "closing", "title": "谢谢"}
    ]
)

# 使用模板
create_ppt_with_template("quarterly_review", None, "quarterly.pptx")
create_ppt_with_template("business_report", None, "report.pptx")
```

### 智能图表推荐
```python
from core import recommend_chart

result = recommend_chart(data)
print(result["recommended_chart"])  # 自动推荐图表类型
print(result["reason"])  # 推荐理由
```

### AI 智能分析
```python
from ai import analyze_with_ai, generate_smart_report

# 分析数据
result = analyze_with_ai(data, "分析销售趋势")

# 自然语言生成报告
report = generate_smart_report(data, "生成月度销售报告")
```

### 格式转换
```python
from core import OfficeFormatConverter

converter = OfficeFormatConverter()

# Excel → Word
converter.excel_to_word_table("data.xlsx", "report.docx")

# Excel → PPT
converter.excel_to_ppt("data.xlsx", "presentation.pptx")

# Word → PPT
converter.word_to_ppt("document.docx", "slides.pptx")

# Word → Excel
converter.word_table_to_excel("document.docx", "data.xlsx")
```

### 批量处理
```python
from core import BatchOfficeProcessor

processor = BatchOfficeProcessor()

# 合并多个Excel
processor.batch_merge_excel(["file1.xlsx", "file2.xlsx"], "merged.xlsx")

# 批量生成报告
processor.batch_create_reports("data.xlsx", "template.docx", "output/", "report")
```

---

## CLI 命令行工具

```bash
# Word 报告
python cli.py report -i data.xlsx -o report.docx --title "月度报告"

# Excel 专业报表
python cli.py excel -i data.xlsx -o report.xlsx --style blue
python cli.py excel-template -t sales_monthly -i data.xlsx -o sales.xlsx

# PPT 演示文稿
python cli.py ppt -o presentation.pptx --style corporate --title "演示"
python cli.py ppt-template -t quarterly_review -o quarterly.pptx

# 格式转换
python cli.py convert -a excel2word -i data.xlsx -o report.docx
python cli.py convert -a excel2ppt -i data.xlsx -o slides.pptx

# 添加目录
python cli.py word-toc -i report.docx -o report_with_toc.docx

# 文档保护
python cli.py word-protect -i report.docx -o protected.docx -p password123

# Excel 条件格式
python cli.py excel-conditional -i data.xlsx -o formatted.xlsx -r "B2:B100"

# 智能分析
python cli.py analyze -i data.csv -p "分析销售趋势"
python cli.py smart-report -i data.csv -p "生成报告"

# 查看模板
python cli.py templates --target excel
python cli.py templates --target ppt
```

---

## 模板系统

### Excel 模板
| ID | 名称 | 说明 |
|----|------|------|
| `sales_monthly` | 月度销售报表 | 销售数据报表 |
| `financial_report` | 财务报表 | 资产负债表、利润表 |
| `project_tracker` | 项目跟踪表 | 任务管理、里程碑 |
| `kpi_dashboard` | KPI仪表盘 | 关键绩效指标 |

### PPT 模板
| ID | 名称 | 说明 |
|----|------|------|
| `business_report` | 商务报告 | 业务汇报演示 |
| `quarterly_review` | 季度回顾 | 季度总结演示 |
| `product_launch` | 产品发布 | 新品发布演示 |
| `investor_pitch` | 投资者演示 | 融资路演演示 |

### 样式风格
- **Excel**: professional, blue, green, red, purple, dark, orange
- **PPT**: corporate, modern, elegant, fresh, warm, purple, tech

---

## 依赖安装

```bash
pip install python-docx openpyxl python-pptx reportlab pandas numpy
pip install matplotlib seaborn wordcloud squarify
pip install requests
```

---

## 典型工作流

### 1. 数据驱动报告自动化
1. 读取 Excel/CSV 数据
2. AI 智能分析数据
3. 生成 Word 报告 + 图表
4. 生成 Excel 汇总表
5. 生成 PPT 演示
6. 输出 PDF

### 2. 批量文档生成
1. 准备数据源
2. 使用邮件合并或批量处理
3. 批量生成文档

### 3. 格式转换工作流
1. Excel 数据导入
2. 转换为 Word 报告
3. 转换为 PPT 演示
4. 导出 PDF

---
*版本: 3.0*
*更新日期: 2026-03-13*
*依赖: python-docx, openpyxl, python-pptx, pandas, numpy, matplotlib*
