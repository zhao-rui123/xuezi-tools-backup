# OpenClaw - 智能数据提取技能包

OpenClaw 是一个功能强大的数据采集工具，支持从 PDF、Excel、截图等多种来源精准提取数据，并提供数据清洗、整理、验证等完整的数据处理流程。

## 功能特性

### 数据提取
- **PDF 数据提取**: 文本、表格、图片、表单、元数据
- **Excel 数据提取**: 多工作表、公式计算、数据透视
- **图片 OCR 识别**: 截图文字提取、表格识别、结构化数据

### 数据处理
- **数据清洗整理**: 去重、格式化、类型转换、缺失值处理
- **数据验证**: 类型验证、格式验证、范围验证、自定义规则
- **智能数据识别**: 自动识别数据类型、表头检测、数据分类

### 批量处理
- **多文件并行处理**: 支持多线程/多进程
- **格式转换**: CSV、Excel、JSON 互转
- **进度跟踪**: 实时显示处理进度

## 安装

### 基础安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/openclaw.git
cd openclaw

# 安装基础依赖
pip install -r requirements.txt

# 安装可选依赖（根据需求）
# PDF 处理
pip install pdfplumber pikepdf pdf2image

# Excel 处理
pip install openpyxl xlrd

# OCR 识别
pip install pytesseract pillow
pip install paddleocr  # 或 easyocr

# 数据处理
pip install pandas numpy
```

### 系统依赖

**Tesseract OCR** (用于图片文字识别):
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim

# macOS
brew install tesseract tesseract-lang

# Windows
# 下载安装包: https://github.com/UB-Mannheim/tesseract/wiki
```

**Poppler** (用于 PDF 转图片):
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler
```

## 快速开始

### 命令行使用

```bash
# 提取 PDF 文本和表格
openclaw extract pdf document.pdf --tables --output result.json

# 提取 Excel 数据
openclaw extract excel data.xlsx --sheet Sheet1 --output data.csv

# OCR 识别图片
openclaw extract image screenshot.png --language chi_sim+eng --output text.txt

# 清洗数据
openclaw clean data.csv --remove-duplicates --fill-missing --output cleaned.csv

# 转换格式
openclaw convert data.xlsx csv --output data.csv

# 分析数据结构
openclaw analyze data.xlsx --detailed
```

### Python API 使用

```python
from openclaw import PDFExtractor, ExcelExtractor, ImageExtractor
from openclaw import DataCleaner, DataValidator, Config

# PDF 提取
config = Config().pdf
config.extract_tables = True
extractor = PDFExtractor(config)
result = extractor.extract("document.pdf")
print(result.raw_text)
print(result.tables)

# Excel 提取
extractor = ExcelExtractor(Config().excel)
result = extractor.extract("data.xlsx")
df = extractor.to_dataframe("data.xlsx", sheet_name="Sheet1")

# 图片 OCR
extractor = ImageExtractor(Config().image)
result = extractor.extract("screenshot.png")
print(result.raw_text)

# 数据清洗
cleaner = DataCleaner(Config().cleaning)
df_cleaned = cleaner.clean_dataframe(df)
report = cleaner.get_report()

# 数据验证
validator = DataValidator()
rules = [
    ValidationRule("email", "format", {"format": "email"}),
    ValidationRule("age", "range", {"min": 0, "max": 150}),
]
result = validator.validate_record(record, rules)
```

## 模块说明

### 核心模块 (core)
- `config.py`: 配置管理
- `pipeline.py`: 数据处理流程管道

### 提取器模块 (extractors)
- `pdf_extractor.py`: PDF 数据提取
- `excel_extractor.py`: Excel 数据提取
- `image_extractor.py`: 图片 OCR 识别

### 清洗器模块 (cleaners)
- `data_cleaner.py`: 数据清洗和整理

### 工具模块 (utils)
- `validator.py`: 数据验证
- `formatter.py`: 数据格式化
- `batch_processor.py`: 批量处理
- `smart_recognizer.py`: 智能数据识别

## 配置说明

### 配置文件示例 (config.json)

```json
{
  "pdf": {
    "extract_text": true,
    "extract_tables": true,
    "extract_images": false,
    "extract_metadata": true,
    "use_ocr": false,
    "ocr_language": "chi_sim+eng",
    "ocr_dpi": 300
  },
  "excel": {
    "header_row": 0,
    "evaluate_formulas": true,
    "auto_detect_types": true
  },
  "image": {
    "ocr_engine": "auto",
    "language": "chi_sim+eng",
    "preprocess": true,
    "detect_tables": true
  },
  "cleaning": {
    "remove_duplicates": true,
    "handle_missing": true,
    "missing_strategy": "auto",
    "auto_convert_types": true
  },
  "output": {
    "format": "json",
    "include_metadata": true,
    "pretty_print": true
  }
}
```

### 加载配置

```python
from openclaw import Config

# 从文件加载
config = Config.load("config.json")

# 从环境变量加载
config = Config().from_env()

# 手动设置
config = Config()
config.pdf.extract_tables = True
config.excel.header_row = 1
```

## 高级用法

### 自定义数据处理流程

```python
from openclaw import DataPipeline, Config
from openclaw.core.pipeline import StageProcessor, PipelineStage

class CustomProcessor(StageProcessor):
    def process(self, data, context):
        # 自定义处理逻辑
        processed_data = data  # 处理数据
        return self._create_result(True, processed_data)

config = Config()
pipeline = DataPipeline(config)
pipeline.register_stage(CustomProcessor(PipelineStage.TRANSFORM))

context = pipeline.process_file("data.pdf")
```

### 批量处理

```python
from openclaw import BatchProcessor

processor = BatchProcessor(max_workers=4, parallel=True)

def process_file(file_path):
    # 处理逻辑
    return result

results = processor.process_files(file_list, process_file)
report = processor.get_report()
```

### 智能数据识别

```python
from openclaw import SmartRecognizer

recognizer = SmartRecognizer()

# 识别数据结构
schema = recognizer.recognize_dataframe(df, table_name="users")

# 数据分类
categories = recognizer.classify_data(df)

# 列名匹配
matches = recognizer.match_column_name("手机号", df.columns.tolist())
```

## 测试

```bash
# 运行所有测试
python -m unittest discover -s tests

# 运行特定测试
python -m unittest tests.test_pdf_extractor
python -m unittest tests.test_excel_extractor
python -m unittest tests.test_data_cleaner
```

## 示例

查看 `examples/` 目录获取更多使用示例：

```bash
python examples/basic_usage.py
```

## 依赖说明

### 必需依赖
- Python >= 3.8

### 可选依赖
| 功能 | 依赖包 |
|------|--------|
| PDF 提取 | pdfplumber, pikepdf |
| Excel 提取 | openpyxl, xlrd |
| OCR 识别 | pytesseract, paddleocr, easyocr |
| 数据处理 | pandas, numpy |
| 图像处理 | Pillow, opencv-python |
| PDF 转图片 | pdf2image |

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0
- 初始版本发布
- 支持 PDF、Excel、图片数据提取
- 支持数据清洗和验证
- 支持批量处理
- 支持智能数据识别
