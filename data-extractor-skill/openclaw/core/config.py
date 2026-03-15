"""
配置管理模块

提供统一的配置管理，支持从文件、环境变量、代码中加载配置
"""

import os
import json
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Union
from pathlib import Path


@dataclass
class PDFConfig:
    """PDF提取配置"""
    # 文本提取配置
    extract_text: bool = True
    extract_tables: bool = True
    extract_images: bool = False
    extract_metadata: bool = True
    extract_forms: bool = True
    
    # 页面范围配置
    page_range: Optional[str] = None  # 例如: "1-5,7,10-12"
    
    # 表格提取配置
    table_settings: Dict[str, Any] = field(default_factory=lambda: {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "snap_tolerance": 3,
        "join_tolerance": 3,
        "edge_min_length": 10,
        "min_words_vertical": 3,
        "min_words_horizontal": 1,
    })
    
    # OCR配置（用于扫描版PDF）
    use_ocr: bool = False
    ocr_language: str = "chi_sim+eng"  # 中文简体+英文
    ocr_dpi: int = 300


@dataclass
class ExcelConfig:
    """Excel提取配置"""
    # 工作表配置
    sheet_names: Optional[List[str]] = None  # None表示所有工作表
    sheet_index: Optional[Union[int, List[int]]] = None
    
    # 数据范围配置
    header_row: Optional[int] = 0  # 表头行，None表示无表头
    start_row: Optional[int] = None
    end_row: Optional[int] = None
    start_col: Optional[Union[int, str]] = None
    end_col: Optional[Union[int, str]] = None
    
    # 数据处理配置
    evaluate_formulas: bool = True
    detect_merged_cells: bool = True
    handle_hidden_sheets: bool = False
    handle_hidden_rows: bool = False
    
    # 数据类型检测
    auto_detect_types: bool = True
    date_format: str = "%Y-%m-%d"
    datetime_format: str = "%Y-%m-%d %H:%M:%S"


@dataclass
class ImageConfig:
    """图片OCR配置"""
    # OCR引擎配置
    ocr_engine: str = "auto"  # auto, tesseract, paddle, easyocr
    language: str = "chi_sim+eng"
    
    # 图像预处理配置
    preprocess: bool = True
    resize_max_dim: Optional[int] = 4096
    contrast_enhance: bool = True
    denoise: bool = True
    deskew: bool = True
    
    # 表格识别配置
    detect_tables: bool = True
    table_structure_model: str = "auto"
    
    # 输出配置
    output_format: str = "structured"  # raw, structured, markdown, html
    preserve_layout: bool = True


@dataclass
class DataCleaningConfig:
    """数据清洗配置"""
    # 去重配置
    remove_duplicates: bool = True
    duplicate_subset: Optional[List[str]] = None
    keep: str = "first"  # first, last, False
    
    # 缺失值处理
    handle_missing: bool = True
    missing_strategy: str = "auto"  # auto, drop, fill, interpolate
    fill_value: Optional[Any] = None
    
    # 数据类型转换
    auto_convert_types: bool = True
    date_columns: Optional[List[str]] = None
    numeric_columns: Optional[List[str]] = None
    
    # 文本清洗
    strip_whitespace: bool = True
    normalize_unicode: bool = True
    remove_control_chars: bool = True
    
    # 异常值处理
    handle_outliers: bool = False
    outlier_method: str = "iqr"  # iqr, zscore, isolation_forest
    outlier_threshold: float = 3.0


@dataclass
class OutputConfig:
    """输出配置"""
    # 输出格式
    format: str = "auto"  # auto, json, csv, xlsx, parquet, sqlite
    
    # 文件配置
    output_dir: str = "./output"
    filename_template: str = "{source}_{timestamp}.{ext}"
    overwrite: bool = False
    
    # 数据配置
    include_metadata: bool = True
    include_source_info: bool = True
    pretty_print: bool = True
    encoding: str = "utf-8"
    
    # 分片配置（大数据量）
    chunk_size: Optional[int] = None
    max_rows_per_file: Optional[int] = None


@dataclass
class ProcessingConfig:
    """处理流程配置"""
    # 并行处理配置
    parallel: bool = True
    max_workers: int = 4
    chunk_size: int = 1000
    
    # 内存配置
    memory_limit_mb: Optional[int] = None
    streaming: bool = False
    
    # 错误处理
    on_error: str = "log"  # raise, skip, log
    max_errors: int = 100
    
    # 进度跟踪
    show_progress: bool = True
    progress_interval: int = 100


class Config:
    """
    统一配置管理类
    
    整合所有子模块配置，提供统一的配置加载、保存、验证功能
    
    Example:
        >>> config = Config()
        >>> config.pdf.extract_tables = True
        >>> config.excel.header_row = 1
        >>> config.save("config.json")
        
        >>> config2 = Config.load("config.json")
    """
    
    def __init__(
        self,
        pdf: Optional[PDFConfig] = None,
        excel: Optional[ExcelConfig] = None,
        image: Optional[ImageConfig] = None,
        cleaning: Optional[DataCleaningConfig] = None,
        output: Optional[OutputConfig] = None,
        processing: Optional[ProcessingConfig] = None,
    ):
        self.pdf = pdf or PDFConfig()
        self.excel = excel or ExcelConfig()
        self.image = image or ImageConfig()
        self.cleaning = cleaning or DataCleaningConfig()
        self.output = output or OutputConfig()
        self.processing = processing or ProcessingConfig()
    
    @classmethod
    def load(cls, path: Union[str, Path]) -> "Config":
        """从JSON文件加载配置"""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {path}")
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return cls(
            pdf=PDFConfig(**data.get("pdf", {})),
            excel=ExcelConfig(**data.get("excel", {})),
            image=ImageConfig(**data.get("image", {})),
            cleaning=DataCleaningConfig(**data.get("cleaning", {})),
            output=OutputConfig(**data.get("output", {})),
            processing=ProcessingConfig(**data.get("processing", {})),
        )
    
    def save(self, path: Union[str, Path]) -> None:
        """保存配置到JSON文件"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "pdf": asdict(self.pdf),
            "excel": asdict(self.excel),
            "image": asdict(self.image),
            "cleaning": asdict(self.cleaning),
            "output": asdict(self.output),
            "processing": asdict(self.processing),
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def from_env(self) -> "Config":
        """从环境变量加载配置"""
        # PDF配置
        if os.getenv("OPENCLAW_PDF_OCR"):
            self.pdf.use_ocr = os.getenv("OPENCLAW_PDF_OCR").lower() == "true"
        if os.getenv("OPENCLAW_PDF_OCR_LANG"):
            self.pdf.ocr_language = os.getenv("OPENCLAW_PDF_OCR_LANG")
        
        # Excel配置
        if os.getenv("OPENCLAW_EXCEL_HEADER_ROW"):
            self.excel.header_row = int(os.getenv("OPENCLAW_EXCEL_HEADER_ROW"))
        
        # Image配置
        if os.getenv("OPENCLAW_IMAGE_OCR_ENGINE"):
            self.image.ocr_engine = os.getenv("OPENCLAW_IMAGE_OCR_ENGINE")
        if os.getenv("OPENCLAW_IMAGE_LANGUAGE"):
            self.image.language = os.getenv("OPENCLAW_IMAGE_LANGUAGE")
        
        # 输出配置
        if os.getenv("OPENCLAW_OUTPUT_DIR"):
            self.output.output_dir = os.getenv("OPENCLAW_OUTPUT_DIR")
        if os.getenv("OPENCLAW_OUTPUT_FORMAT"):
            self.output.format = os.getenv("OPENCLAW_OUTPUT_FORMAT")
        
        # 处理配置
        if os.getenv("OPENCLAW_PARALLEL"):
            self.processing.parallel = os.getenv("OPENCLAW_PARALLEL").lower() == "true"
        if os.getenv("OPENCLAW_MAX_WORKERS"):
            self.processing.max_workers = int(os.getenv("OPENCLAW_MAX_WORKERS"))
        
        return self
    
    def validate(self) -> List[str]:
        """验证配置有效性，返回错误信息列表"""
        errors = []
        
        # 验证PDF配置
        if self.pdf.ocr_dpi < 72 or self.pdf.ocr_dpi > 2400:
            errors.append(f"PDF OCR DPI应在72-2400之间: {self.pdf.ocr_dpi}")
        
        # 验证Excel配置
        if self.excel.header_row is not None and self.excel.header_row < 0:
            errors.append(f"Excel表头行不能为负数: {self.excel.header_row}")
        
        # 验证Image配置
        valid_engines = ["auto", "tesseract", "paddle", "easyocr"]
        if self.image.ocr_engine not in valid_engines:
            errors.append(f"不支持的OCR引擎: {self.image.ocr_engine}")
        
        # 验证输出配置
        valid_formats = ["auto", "json", "csv", "xlsx", "parquet", "sqlite"]
        if self.output.format not in valid_formats:
            errors.append(f"不支持的输出格式: {self.output.format}")
        
        # 验证处理配置
        if self.processing.max_workers < 1:
            errors.append(f"工作线程数至少为1: {self.processing.max_workers}")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "pdf": asdict(self.pdf),
            "excel": asdict(self.excel),
            "image": asdict(self.image),
            "cleaning": asdict(self.cleaning),
            "output": asdict(self.output),
            "processing": asdict(self.processing),
        }
