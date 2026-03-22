# OpenClaw Data Extractor - 智能数据提取技能包

## 描述

功能强大的数据采集工具，支持从 PDF、Excel、图片等多种来源精准提取数据，并提供数据清洗、整理、验证、格式转换等完整的数据处理流程。

## 功能

### 数据提取
- **PDF 提取**: 文本、表格、图片、表单、元数据，支持 OCR（扫描版 PDF）
- **Excel 提取**: 多工作表提取、公式计算、自定义表头
- **图片 OCR**: 截图文字识别、表格识别，支持 Tesseract/PaddleOCR/EasyOCR 多种引擎

### 数据处理
- **数据清洗**: 去重、缺失值处理（均值/中位数/众数/常量填充）、异常值去除、列名标准化
- **数据验证**: 类型验证、格式验证、范围验证、自定义规则
- **智能识别**: 自动识别数据类型、表头检测、数据分类

### 格式转换
- CSV ↔ Excel ↔ JSON ↔ Parquet 互转

### 批量处理
- 多文件并行处理、多线程/多进程支持

## 使用方法

```bash
# 提取 PDF 文本和表格
openclaw extract pdf document.pdf --tables -o result.json

# 提取 Excel 指定工作表
openclaw extract excel data.xlsx --sheet Sheet1 -o data.csv

# OCR 识别图片
openclaw extract image screenshot.png --language chi_sim+eng -o text.txt

# 清洗数据
openclaw clean data.csv --remove-duplicates --fill-missing mean -o cleaned.csv

# 格式转换
openclaw convert data.xlsx csv -o data.csv

# 分析数据结构
openclaw analyze data.xlsx --detailed
```

Python API：
```python
from openclaw import PDFExtractor, ExcelExtractor, ImageExtractor, DataCleaner

# PDF 提取
extractor = PDFExtractor(config)
result = extractor.extract("document.pdf")

# Excel 提取
extractor = ExcelExtractor(config)
result = extractor.extract("data.xlsx")

# 图片 OCR
extractor = ImageExtractor(config)
result = extractor.extract("screenshot.png")

# 数据清洗
cleaner = DataCleaner(config)
df_cleaned = cleaner.clean_dataframe(df)
```

## 依赖

- Python >= 3.8
- PDF 提取: `pdfplumber`, `pikepdf`
- Excel 提取: `openpyxl`, `xlrd`
- OCR 识别: `pytesseract`, `Pillow`, `paddleocr` 或 `easyocr`
- 数据处理: `pandas`, `numpy`
- 系统依赖: Tesseract OCR, Poppler（PDF 转图片）
