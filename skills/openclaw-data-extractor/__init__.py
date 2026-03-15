"""
OpenClaw - 智能数据提取技能包

一个功能强大的数据采集工具，支持从PDF、Excel、截图等多种来源精准提取数据，
并提供数据清洗、整理、验证等完整的数据处理流程。

主要功能:
    - PDF数据提取: 文本、表格、图片、表单、元数据
    - Excel数据提取: 多工作表、公式计算、数据透视
    - 图片OCR识别: 截图文字提取、表格识别、结构化数据
    - 数据清洗整理: 去重、格式化、类型转换、缺失值处理
    - 智能数据识别: 自动识别数据类型、表头检测、数据分类
    - 批量处理: 多文件并行处理、格式转换、数据合并

作者: OpenClaw Team
版本: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "OpenClaw Team"

from .core.pipeline import DataPipeline
from .core.config import Config
from .extractors.pdf_extractor import PDFExtractor
from .extractors.excel_extractor import ExcelExtractor
from .extractors.image_extractor import ImageExtractor
from .cleaners.data_cleaner import DataCleaner
from .utils.validator import DataValidator
from .utils.formatter import DataFormatter

__all__ = [
    "DataPipeline",
    "Config",
    "PDFExtractor",
    "ExcelExtractor", 
    "ImageExtractor",
    "DataCleaner",
    "DataValidator",
    "DataFormatter",
]
