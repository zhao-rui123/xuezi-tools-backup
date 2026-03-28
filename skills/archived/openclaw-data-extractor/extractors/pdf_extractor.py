"""
PDF数据提取模块

提供全面的PDF数据提取功能，包括:
- 文本提取（支持普通PDF和扫描版PDF）
- 表格提取（自动识别表格结构）
- 图片提取
- 表单数据提取
- 元数据提取
"""

import io
import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Union, Iterator
from pathlib import Path
from dataclasses import dataclass, field
import tempfile

import numpy as np

# 设置日志
logger = logging.getLogger("openclaw.extractors.pdf")


@dataclass
class PDFTextBlock:
    """PDF文本块"""
    text: str
    page: int
    x0: float
    y0: float
    x1: float
    y1: float
    font: Optional[str] = None
    size: Optional[float] = None
    is_bold: bool = False
    is_italic: bool = False


@dataclass
class PDFTable:
    """PDF表格"""
    page: int
    table_index: int
    data: List[List[str]]
    bbox: Optional[Tuple[float, float, float, float]] = None
    rows: int = 0
    cols: int = 0
    
    def __post_init__(self):
        if self.data:
            self.rows = len(self.data)
            self.cols = max(len(row) for row in self.data) if self.data else 0


@dataclass
class PDFImage:
    """PDF图片"""
    page: int
    image_index: int
    ext: str
    data: bytes
    width: Optional[int] = None
    height: Optional[int] = None
    name: Optional[str] = None


@dataclass
class PDFFormField:
    """PDF表单字段"""
    name: str
    field_type: str
    value: Optional[str] = None
    options: List[str] = field(default_factory=list)
    page: int = 0
    is_readonly: bool = False


@dataclass
class PDFMetadata:
    """PDF元数据"""
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None
    pages: int = 0
    encrypted: bool = False
    pdf_version: Optional[str] = None


@dataclass
class PDFExtractionResult:
    """PDF提取结果"""
    metadata: PDFMetadata = field(default_factory=PDFMetadata)
    text_blocks: List[PDFTextBlock] = field(default_factory=list)
    tables: List[PDFTable] = field(default_factory=list)
    images: List[PDFImage] = field(default_factory=list)
    form_fields: List[PDFFormField] = field(default_factory=list)
    raw_text: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "metadata": {
                "title": self.metadata.title,
                "author": self.metadata.author,
                "subject": self.metadata.subject,
                "pages": self.metadata.pages,
                "encrypted": self.metadata.encrypted,
            },
            "text": self.raw_text,
            "text_blocks": [
                {
                    "text": b.text,
                    "page": b.page,
                    "bbox": [b.x0, b.y0, b.x1, b.y1],
                }
                for b in self.text_blocks
            ],
            "tables": [
                {
                    "page": t.page,
                    "index": t.table_index,
                    "rows": t.rows,
                    "cols": t.cols,
                    "data": t.data,
                }
                for t in self.tables
            ],
            "form_fields": [
                {
                    "name": f.name,
                    "type": f.field_type,
                    "value": f.value,
                    "page": f.page,
                }
                for f in self.form_fields
            ],
            "images_count": len(self.images),
        }


class PDFExtractor:
    """
    PDF数据提取器
    
    提供全面的PDF数据提取功能，支持普通PDF和扫描版PDF。
    
    Example:
        >>> from openclaw import PDFExtractor, Config
        >>> extractor = PDFExtractor(Config().pdf)
        >>> 
        >>> # 提取所有数据
        >>> result = extractor.extract("document.pdf")
        >>> 
        >>> # 仅提取文本
        >>> text = extractor.extract_text("document.pdf")
        >>> 
        >>> # 仅提取表格
        >>> tables = extractor.extract_tables("document.pdf")
        
        >>> # 提取指定页面
        >>> result = extractor.extract("document.pdf", page_range="1-5,10")
    """
    
    def __init__(self, config=None):
        """
        初始化PDF提取器
        
        Args:
            config: PDFConfig配置对象
        """
        self.config = config
        self.logger = logging.getLogger("openclaw.extractors.pdf")
        self._check_dependencies()
    
    def _check_dependencies(self) -> None:
        """检查依赖库"""
        try:
            import pdfplumber
            self.pdfplumber = pdfplumber
        except ImportError:
            self.logger.warning("pdfplumber未安装，PDF提取功能受限")
            self.pdfplumber = None
        
        try:
            import pikepdf
            self.pikepdf = pikepdf
        except ImportError:
            self.logger.warning("pikepdf未安装，PDF表单和元数据提取功能受限")
            self.pikepdf = None
        
        try:
            import pytesseract
            self.pytesseract = pytesseract
        except ImportError:
            self.logger.warning("pytesseract未安装，OCR功能不可用")
            self.pytesseract = None
        
        try:
            from PIL import Image
            self.PILImage = Image
        except ImportError:
            self.logger.warning("PIL未安装，图片处理功能受限")
            self.PILImage = None
        
        try:
            import pdf2image
            self.pdf2image = pdf2image
        except ImportError:
            self.logger.warning("pdf2image未安装，PDF转图片功能受限")
            self.pdf2image = None
    
    def extract(
        self,
        file_path: Union[str, Path],
        page_range: Optional[str] = None,
    ) -> PDFExtractionResult:
        """
        提取PDF中的所有数据
        
        Args:
            file_path: PDF文件路径
            page_range: 页面范围，例如 "1-5,7,10-12"
        
        Returns:
            PDFExtractionResult: 提取结果
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        self.logger.info(f"开始提取PDF: {file_path}")
        
        result = PDFExtractionResult()
        
        # 提取元数据
        if self.config is None or self.config.extract_metadata:
            result.metadata = self.extract_metadata(file_path)
        
        # 提取文本
        if self.config is None or self.config.extract_text:
            result.text_blocks = self.extract_text_blocks(file_path, page_range)
            result.raw_text = "\n".join(block.text for block in result.text_blocks)
        
        # 提取表格
        if self.config is None or self.config.extract_tables:
            result.tables = self.extract_tables(file_path, page_range)
        
        # 提取图片
        if self.config and self.config.extract_images:
            result.images = self.extract_images(file_path, page_range)
        
        # 提取表单
        if self.config is None or self.config.extract_forms:
            result.form_fields = self.extract_form_fields(file_path)
        
        self.logger.info(
            f"PDF提取完成: {len(result.text_blocks)}个文本块, "
            f"{len(result.tables)}个表格, {len(result.images)}张图片"
        )
        
        return result
    
    def extract_metadata(self, file_path: Union[str, Path]) -> PDFMetadata:
        """
        提取PDF元数据
        
        Args:
            file_path: PDF文件路径
        
        Returns:
            PDFMetadata: 元数据对象
        """
        file_path = Path(file_path)
        metadata = PDFMetadata()
        
        if self.pdfplumber:
            try:
                with self.pdfplumber.open(file_path) as pdf:
                    meta = pdf.metadata or {}
                    metadata.title = meta.get("Title")
                    metadata.author = meta.get("Author")
                    metadata.subject = meta.get("Subject")
                    metadata.creator = meta.get("Creator")
                    metadata.producer = meta.get("Producer")
                    metadata.creation_date = meta.get("CreationDate")
                    metadata.modification_date = meta.get("ModDate")
                    metadata.pages = len(pdf.pages)
            except Exception as e:
                self.logger.warning(f"提取元数据失败: {e}")
        
        if self.pikepdf:
            try:
                with self.pikepdf.open(file_path) as pdf:
                    metadata.encrypted = pdf.is_encrypted
                    if pdf.pdf_version:
                        metadata.pdf_version = str(pdf.pdf_version)
            except Exception as e:
                self.logger.warning(f"使用pikepdf提取元数据失败: {e}")
        
        return metadata
    
    def extract_text(
        self,
        file_path: Union[str, Path],
        page_range: Optional[str] = None,
    ) -> str:
        """
        提取PDF文本内容
        
        Args:
            file_path: PDF文件路径
            page_range: 页面范围
        
        Returns:
            str: 提取的文本
        """
        blocks = self.extract_text_blocks(file_path, page_range)
        return "\n".join(block.text for block in blocks)
    
    def extract_text_blocks(
        self,
        file_path: Union[str, Path],
        page_range: Optional[str] = None,
    ) -> List[PDFTextBlock]:
        """
        提取PDF文本块（带位置信息）
        
        Args:
            file_path: PDF文件路径
            page_range: 页面范围
        
        Returns:
            List[PDFTextBlock]: 文本块列表
        """
        file_path = Path(file_path)
        blocks = []
        
        if not self.pdfplumber:
            self.logger.error("pdfplumber未安装，无法提取文本")
            return blocks
        
        page_numbers = self._parse_page_range(page_range)
        
        try:
            with self.pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages, 1):
                    if page_numbers and i not in page_numbers:
                        continue
                    
                    # 提取页面文本
                    page_text = page.extract_text()
                    if page_text:
                        words = page.extract_words()
                        for word in words:
                            block = PDFTextBlock(
                                text=word.get("text", ""),
                                page=i,
                                x0=word.get("x0", 0),
                                y0=word.get("top", 0),
                                x1=word.get("x1", 0),
                                y1=word.get("bottom", 0),
                                font=word.get("fontname"),
                                size=word.get("size"),
                            )
                            blocks.append(block)
                        
                        # 如果没有words但有文本，添加整个页面作为一个块
                        if not words:
                            blocks.append(PDFTextBlock(
                                text=page_text,
                                page=i,
                                x0=0, y0=0, x1=page.width, y1=page.height,
                            ))
        except Exception as e:
            self.logger.error(f"提取文本失败: {e}")
        
        return blocks
    
    def extract_tables(
        self,
        file_path: Union[str, Path],
        page_range: Optional[str] = None,
    ) -> List[PDFTable]:
        """
        提取PDF中的表格
        
        Args:
            file_path: PDF文件路径
            page_range: 页面范围
        
        Returns:
            List[PDFTable]: 表格列表
        """
        file_path = Path(file_path)
        tables = []
        
        if not self.pdfplumber:
            self.logger.error("pdfplumber未安装，无法提取表格")
            return tables
        
        page_numbers = self._parse_page_range(page_range)
        table_settings = self.config.table_settings if self.config else {}
        
        try:
            with self.pdfplumber.open(file_path) as pdf:
                table_index = 0
                for i, page in enumerate(pdf.pages, 1):
                    if page_numbers and i not in page_numbers:
                        continue
                    
                    page_tables = page.extract_tables(table_settings)
                    for table_data in page_tables:
                        if table_data:
                            table = PDFTable(
                                page=i,
                                table_index=table_index,
                                data=table_data,
                            )
                            tables.append(table)
                            table_index += 1
        except Exception as e:
            self.logger.error(f"提取表格失败: {e}")
        
        return tables
    
    def extract_images(
        self,
        file_path: Union[str, Path],
        page_range: Optional[str] = None,
    ) -> List[PDFImage]:
        """
        提取PDF中的图片
        
        Args:
            file_path: PDF文件路径
            page_range: 页面范围
        
        Returns:
            List[PDFImage]: 图片列表
        """
        file_path = Path(file_path)
        images = []
        
        if not self.pikepdf:
            self.logger.error("pikepdf未安装，无法提取图片")
            return images
        
        page_numbers = self._parse_page_range(page_range)
        
        try:
            with self.pikepdf.open(file_path) as pdf:
                image_index = 0
                for i, page in enumerate(pdf.pages, 1):
                    if page_numbers and i not in page_numbers:
                        continue
                    
                    if "/Resources" not in page:
                        continue
                    
                    resources = page.Resources
                    if "/XObject" not in resources:
                        continue
                    
                    xobjects = resources.XObject
                    for name, xobj in xobjects.items():
                        try:
                            obj = pdf.get_object(xobj.objgen)
                            if obj.get("/Subtype") != "/Image":
                                continue
                            
                            width = int(obj.get("/Width", 0))
                            height = int(obj.get("/Height", 0))
                            filter_type = obj.get("/Filter")
                            
                            # 确定图片格式
                            if filter_type == "/DCTDecode":
                                ext = "jpg"
                            elif filter_type == "/FlateDecode":
                                ext = "png"
                            else:
                                ext = "bin"
                            
                            raw_data = obj.read_raw_bytes()
                            
                            image = PDFImage(
                                page=i,
                                image_index=image_index,
                                ext=ext,
                                data=raw_data,
                                width=width,
                                height=height,
                                name=str(name),
                            )
                            images.append(image)
                            image_index += 1
                            
                        except Exception as e:
                            self.logger.warning(f"提取图片失败: {e}")
                            continue
        except Exception as e:
            self.logger.error(f"提取图片失败: {e}")
        
        return images
    
    def extract_form_fields(
        self,
        file_path: Union[str, Path],
    ) -> List[PDFFormField]:
        """
        提取PDF表单字段
        
        Args:
            file_path: PDF文件路径
        
        Returns:
            List[PDFFormField]: 表单字段列表
        """
        file_path = Path(file_path)
        fields = []
        
        if not self.pdfplumber:
            self.logger.error("pdfplumber未安装，无法提取表单")
            return fields
        
        try:
            with self.pdfplumber.open(file_path) as pdf:
                # 获取表单字段
                form_data = pdf.doc.catalog.get("AcroForm", {})
                if not form_data:
                    return fields
                
                fields_array = form_data.get("Fields", [])
                for field in fields_array:
                    field_name = field.get("T", "")
                    field_type = field.get("FT", "")
                    field_value = field.get("V", "")
                    
                    # 处理选项字段
                    options = []
                    if "/Opt" in field:
                        options = [str(opt) for opt in field["/Opt"]]
                    
                    form_field = PDFFormField(
                        name=str(field_name),
                        field_type=str(field_type).replace("/", ""),
                        value=str(field_value) if field_value else None,
                        options=options,
                    )
                    fields.append(form_field)
        except Exception as e:
            self.logger.error(f"提取表单失败: {e}")
        
        return fields
    
    def extract_with_ocr(
        self,
        file_path: Union[str, Path],
        page_range: Optional[str] = None,
        language: Optional[str] = None,
        dpi: Optional[int] = None,
    ) -> str:
        """
        使用OCR提取扫描版PDF文本
        
        Args:
            file_path: PDF文件路径
            page_range: 页面范围
            language: OCR语言
            dpi: 转换分辨率
        
        Returns:
            str: 提取的文本
        """
        file_path = Path(file_path)
        
        if not self.pytesseract:
            raise RuntimeError("pytesseract未安装，无法进行OCR")
        
        if not self.pdf2image:
            raise RuntimeError("pdf2image未安装，无法转换PDF为图片")
        
        language = language or (self.config.ocr_language if self.config else "chi_sim+eng")
        dpi = dpi or (self.config.ocr_dpi if self.config else 300)
        
        page_numbers = self._parse_page_range(page_range)
        texts = []
        
        try:
            # 转换PDF为图片
            images = self.pdf2image.convert_from_path(
                file_path,
                dpi=dpi,
                first_page=page_numbers[0] if page_numbers else None,
                last_page=page_numbers[-1] if page_numbers else None,
            )
            
            for i, image in enumerate(images, 1):
                page_num = (page_numbers[0] if page_numbers else 1) + i - 1
                self.logger.info(f"OCR处理页面: {page_num}")
                
                # OCR识别
                text = self.pytesseract.image_to_string(image, lang=language)
                texts.append(f"--- Page {page_num} ---\n{text}")
                
        except Exception as e:
            self.logger.error(f"OCR提取失败: {e}")
        
        return "\n\n".join(texts)
    
    def _parse_page_range(self, page_range: Optional[str]) -> Optional[List[int]]:
        """
        解析页面范围字符串
        
        Args:
            page_range: 页面范围字符串，如 "1-5,7,10-12"
        
        Returns:
            List[int]: 页面编号列表
        """
        if not page_range:
            return None
        
        pages = []
        parts = page_range.split(",")
        
        for part in parts:
            part = part.strip()
            if "-" in part:
                start, end = part.split("-", 1)
                pages.extend(range(int(start), int(end) + 1))
            else:
                pages.append(int(part))
        
        return sorted(set(pages))
    
    def save_images(
        self,
        images: List[PDFImage],
        output_dir: Union[str, Path],
    ) -> List[Path]:
        """
        保存提取的图片
        
        Args:
            images: 图片列表
            output_dir: 输出目录
        
        Returns:
            List[Path]: 保存的文件路径列表
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_paths = []
        for img in images:
            filename = f"page_{img.page}_img_{img.image_index}.{img.ext}"
            filepath = output_dir / filename
            
            with open(filepath, "wb") as f:
                f.write(img.data)
            
            saved_paths.append(filepath)
        
        return saved_paths
