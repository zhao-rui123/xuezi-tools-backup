# OpenClaw 功能特性详解

## 功能总览

OpenClaw 是一个功能齐全的数据提取和处理技能包，包含以下核心模块：

```
openclaw/
├── core/               # 核心模块
│   ├── config.py       # 统一配置管理
│   └── pipeline.py     # 数据处理流程管道
├── extractors/         # 数据提取器
│   ├── pdf_extractor.py    # PDF数据提取
│   ├── excel_extractor.py  # Excel数据提取
│   └── image_extractor.py  # 图片OCR识别
├── cleaners/           # 数据清洗
│   └── data_cleaner.py     # 数据清洗和整理
├── utils/              # 工具模块
│   ├── validator.py        # 数据验证
│   ├── formatter.py        # 数据格式化
│   ├── batch_processor.py  # 批量处理
│   └── smart_recognizer.py # 智能数据识别
├── cli.py              # 命令行接口
└── tests/              # 测试模块
```

## 详细功能列表

### 1. PDF数据提取 (PDFExtractor)

#### 功能特性
- ✅ 文本提取（支持普通PDF和扫描版PDF）
- ✅ 表格提取（自动识别表格结构）
- ✅ 图片提取
- ✅ 表单数据提取
- ✅ 元数据提取
- ✅ 页面范围选择
- ✅ OCR支持（扫描版PDF）

#### 提取内容
| 类型 | 说明 | 输出格式 |
|------|------|----------|
| 文本块 | 带位置信息的文本块 | JSON/TXT |
| 表格 | 结构化表格数据 | JSON/CSV |
| 图片 | 内嵌图片 | 原始格式 |
| 表单 | 表单字段和值 | JSON |
| 元数据 | 标题、作者、页数等 | JSON |

#### 使用示例
```python
from openclaw import PDFExtractor, Config

config = Config().pdf
config.extract_tables = True
config.extract_images = True
config.page_range = "1-5,10"

extractor = PDFExtractor(config)
result = extractor.extract("document.pdf")

# 访问提取结果
print(result.raw_text)           # 纯文本
print(result.tables[0].data)     # 表格数据
print(result.metadata.pages)     # 页数
```

### 2. Excel数据提取 (ExcelExtractor)

#### 功能特性
- ✅ 多工作表提取
- ✅ 公式计算结果提取
- ✅ 合并单元格处理
- ✅ 数据透视表提取
- ✅ 图表信息提取
- ✅ 定义名称提取
- ✅ 数据类型自动检测

#### 提取内容
| 类型 | 说明 | 输出格式 |
|------|------|----------|
| 工作表数据 | 单元格值和格式 | JSON/CSV/DataFrame |
| 合并单元格 | 合并范围信息 | JSON |
| 图表 | 图表类型和位置 | JSON |
| 数据透视表 | 透视表结构 | JSON |
| 定义名称 | 命名范围 | JSON |

#### 使用示例
```python
from openclaw import ExcelExtractor, Config

config = Config().excel
config.header_row = 0
config.evaluate_formulas = True

extractor = ExcelExtractor(config)
result = extractor.extract("data.xlsx")

# 提取为DataFrame
df = extractor.to_dataframe("data.xlsx", sheet_name="Sheet1")

# 比较两个Excel文件
diff = extractor.compare_sheets("file1.xlsx", "file2.xlsx", "Sheet1")
```

### 3. 图片OCR识别 (ImageExtractor)

#### 功能特性
- ✅ 多引擎支持（Tesseract/PaddleOCR/EasyOCR）
- ✅ 多语言识别（中文/英文/混合）
- ✅ 图像预处理（降噪、纠偏、增强）
- ✅ 表格结构识别
- ✅ 表单字段识别
- ✅ 布局保留

#### OCR引擎对比
| 引擎 | 优点 | 缺点 |
|------|------|------|
| Tesseract | 轻量、快速 | 中文识别率一般 |
| PaddleOCR | 中文识别率高 | 模型较大 |
| EasyOCR | 多语言支持好 | 速度较慢 |

#### 使用示例
```python
from openclaw import ImageExtractor, Config

config = Config().image
config.language = "chi_sim+eng"
config.ocr_engine = "paddle"
config.detect_tables = True

extractor = ImageExtractor(config)
result = extractor.extract("screenshot.png")

# 获取识别结果
print(result.raw_text)

# 识别表单字段
fields = extractor.extract_form_fields("form.png")
for field in fields:
    print(f"{field.label}: {field.value}")
```

### 4. 数据清洗 (DataCleaner)

#### 功能特性
- ✅ 重复数据处理
- ✅ 缺失值处理（多种策略）
- ✅ 数据类型转换
- ✅ 文本清洗（空白、Unicode、控制字符）
- ✅ 异常值检测与处理
- ✅ 列名标准化

#### 缺失值处理策略
| 策略 | 说明 | 适用场景 |
|------|------|----------|
| auto | 自动选择（数值用中位数，文本用众数） | 通用 |
| drop | 删除包含缺失值的行 | 缺失较少 |
| fill | 使用固定值或统计值填充 | 需要保留行 |
| interpolate | 插值填充 | 时间序列 |

#### 使用示例
```python
from openclaw import DataCleaner, Config

config = Config().cleaning
config.remove_duplicates = True
config.handle_missing = True
config.missing_strategy = "fill"

cleaner = DataCleaner(config)
df_cleaned = cleaner.clean_dataframe(df)

# 获取清洗报告
report = cleaner.get_report()
print(f"去除了 {report.duplicates_removed} 行重复数据")
print(f"填充了 {report.missing_values_filled} 个缺失值")
```

### 5. 数据验证 (DataValidator)

#### 功能特性
- ✅ 数据类型验证
- ✅ 格式验证（邮箱、手机号、身份证号等）
- ✅ 范围验证
- ✅ 必填项验证
- ✅ 正则模式验证
- ✅ 自定义规则验证
- ✅ 数据质量评分

#### 预定义验证格式
| 格式 | 说明 | 示例 |
|------|------|------|
| email | 邮箱地址 | user@example.com |
| phone_cn | 中国手机号 | 13800138000 |
| idcard_cn | 中国身份证号 | 110101199001011234 |
| url | URL地址 | https://example.com |
| ipv4 | IPv4地址 | 192.168.1.1 |
| date_iso | ISO日期 | 2024-01-15 |
| uuid | UUID | 550e8400-e29b-41d4-a716-446655440000 |

#### 使用示例
```python
from openclaw import DataValidator, ValidationRule

validator = DataValidator()

# 定义验证规则
rules = [
    ValidationRule("email", "format", {"format": "email"}),
    ValidationRule("age", "range", {"min": 0, "max": 150}),
    ValidationRule("name", "required"),
]

# 验证数据
result = validator.validate_record(record, rules)
if not result.is_valid:
    for error in result.errors:
        print(f"{error.field}: {error.message}")

# 计算数据质量评分
scores = validator.calculate_quality_score(df)
print(f"完整性: {scores['completeness']:.2%}")
print(f"唯一性: {scores['uniqueness']:.2%}")
print(f"总体评分: {scores['overall']:.2%}")
```

### 6. 数据格式化 (DataFormatter)

#### 功能特性
- ✅ 日期时间格式化
- ✅ 数值格式化
- ✅ 货币格式化
- ✅ 百分比格式化
- ✅ 布尔值格式化
- ✅ 多格式输出（JSON/CSV/Excel/Markdown/HTML）

#### 使用示例
```python
from openclaw import DataFormatter, FormatOptions

options = FormatOptions(
    date_format="%Y/%m/%d",
    currency_symbol="¥",
    number_decimal_places=2,
)

formatter = DataFormatter(options)

# 格式化各种类型
print(formatter.format_currency(1234.56))      # ¥1,234.56
print(formatter.format_percentage(0.25))       # 25.00%
print(formatter.format_date(datetime.now()))   # 2024/01/15

# DataFrame格式化
df_formatted = formatter.format_dataframe(df)

# 输出为不同格式
json_str = formatter.to_json(data)
markdown = formatter.to_markdown(df)
html = formatter.to_html(df, classes="table table-striped")
```

### 7. 批量处理 (BatchProcessor)

#### 功能特性
- ✅ 多文件并行处理
- ✅ 顺序/并行模式切换
- ✅ 进度跟踪
- ✅ 错误处理
- ✅ 结果合并
- ✅ 处理报告生成

#### 使用示例
```python
from openclaw import BatchProcessor

processor = BatchProcessor(
    max_workers=4,
    parallel=True,
    show_progress=True,
)

# 定义处理函数
def process_file(file_path):
    # 处理逻辑
    return result

# 批量处理
results = processor.process_files(file_list, process_func)

# 合并结果
merged = processor.merge_results(results)

# 获取报告
report = processor.get_report()
print(f"成功率: {report.success_rate:.2%}")
```

### 8. 格式转换 (FileConverter)

#### 支持格式
| 源格式 | 目标格式 |
|--------|----------|
| CSV | Excel, JSON |
| Excel | CSV, JSON |
| JSON | CSV |

#### 使用示例
```python
from openclaw import FileConverter

converter = FileConverter()

# 各种转换
converter.csv_to_excel("data.csv", "data.xlsx")
converter.excel_to_csv("data.xlsx", "data.csv", sheet_name="Sheet1")
converter.json_to_csv("data.json", "data.csv")

# 批量转换
converter.convert_batch(
    file_paths=["1.xlsx", "2.xlsx"],
    output_dir="./output",
    target_format="csv",
)
```

### 9. 智能数据识别 (SmartRecognizer)

#### 功能特性
- ✅ 数据类型自动检测
- ✅ 表头自动识别
- ✅ 语义类型识别（邮箱、手机号等）
- ✅ 列名智能匹配
- ✅ 数据分类
- ✅ 主键检测
- ✅ 数据关系检测

#### 使用示例
```python
from openclaw import SmartRecognizer

recognizer = SmartRecognizer()

# 识别数据结构
schema = recognizer.recognize_dataframe(df, table_name="users")

# 数据分类
categories = recognizer.classify_data(df)
print(f"个人身份信息: {categories['personal_info']}")
print(f"联系信息: {categories['contact_info']}")

# 列名匹配
matches = recognizer.match_column_name("手机号", df.columns.tolist())

# 生成自然语言描述
description = recognizer.generate_schema_description(schema)
print(description)
```

### 10. 命令行接口 (CLI)

#### 支持的命令
```bash
# 数据提取
openclaw extract pdf <file> [options]
openclaw extract excel <file> [options]
openclaw extract image <file> [options]

# 数据处理
openclaw clean <file> [options]
openclaw validate <file> [options]
openclaw convert <file> <format> [options]

# 数据分析
openclaw analyze <file> [options]
```

#### 使用示例
```bash
# 提取PDF
openclaw extract pdf document.pdf --tables --output result.json

# 提取Excel
openclaw extract excel data.xlsx --sheet Sheet1 --output data.csv

# OCR识别
openclaw extract image screenshot.png --language chi_sim+eng

# 数据清洗
openclaw clean data.csv --remove-duplicates --fill-mean -o cleaned.csv

# 格式转换
openclaw convert data.xlsx csv --output data.csv

# 数据分析
openclaw analyze data.xlsx --detailed
```

## 配置系统

### 配置文件结构
```json
{
  "pdf": {
    "extract_text": true,
    "extract_tables": true,
    "extract_images": false,
    "use_ocr": false,
    "ocr_language": "chi_sim+eng"
  },
  "excel": {
    "header_row": 0,
    "evaluate_formulas": true
  },
  "image": {
    "ocr_engine": "auto",
    "language": "chi_sim+eng",
    "preprocess": true
  },
  "cleaning": {
    "remove_duplicates": true,
    "handle_missing": true,
    "missing_strategy": "auto"
  },
  "output": {
    "format": "json",
    "pretty_print": true
  }
}
```

### 配置加载方式
```python
from openclaw import Config

# 从文件加载
config = Config.load("config.json")

# 从环境变量加载
config = Config().from_env()

# 手动配置
config = Config()
config.pdf.extract_tables = True
config.excel.header_row = 1
```

## 性能优化

### 并行处理
- 使用 `BatchProcessor` 进行多文件并行处理
- 可配置工作线程数
- 支持进程池（CPU密集型任务）

### 内存优化
- 流式处理大文件
- 分块读取数据
- 及时释放资源

### OCR优化
- 图像预处理（降噪、纠偏）
- 分辨率控制
- 语言包选择

## 错误处理

### 异常类型
- `FileNotFoundError`: 文件不存在
- `RuntimeError`: 依赖未安装
- `TypeError`: 数据类型错误
- `ValueError`: 参数值错误

### 错误处理策略
```python
from openclaw import DataPipeline, Config

config = Config()
config.processing.on_error = "log"  # raise, skip, log

pipeline = DataPipeline(config)
context = pipeline.process_file("data.pdf")

# 检查处理结果
for result in context.intermediate_results:
    if not result.success:
        print(f"阶段 {result.stage} 失败: {result.errors}")
```

## 扩展开发

### 自定义提取器
```python
from openclaw.core.pipeline import StageProcessor, PipelineStage

class CustomExtractor(StageProcessor):
    def process(self, data, context):
        # 自定义提取逻辑
        extracted_data = self._extract(data)
        return self._create_result(True, extracted_data)

pipeline.register_stage(CustomExtractor(PipelineStage.EXTRACT))
```

### 自定义验证器
```python
from openclaw import DataValidator

def custom_validator(value, params):
    is_valid = value.startswith(params.get("prefix", ""))
    return is_valid, "值必须以指定前缀开头"

validator = DataValidator()
validator.register_custom_validator("prefix_check", custom_validator)
```

## 测试覆盖

### 测试模块
- `test_pdf_extractor.py`: PDF提取器测试
- `test_excel_extractor.py`: Excel提取器测试
- `test_data_cleaner.py`: 数据清洗器测试
- `test_validator.py`: 数据验证器测试

### 运行测试
```bash
# 运行所有测试
python -m unittest discover -s tests

# 运行特定测试
python -m unittest tests.test_pdf_extractor
```
