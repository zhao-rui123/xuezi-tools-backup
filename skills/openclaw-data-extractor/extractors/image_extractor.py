"""
图片OCR数据提取模块

提供全面的图片文字识别功能，包括:
- 普通文本OCR识别
- 表格结构识别
- 表单字段识别
- 手写文字识别
- 多语言支持
- 图像预处理
"""

import io
import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
from dataclasses import dataclass, field
import re

import numpy as np

# 设置日志
logger = logging.getLogger("openclaw.extractors.image")


@dataclass
class OCRTextBlock:
    """OCR文本块"""
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    language: Optional[str] = None
    is_handwritten: bool = False
    font_size: Optional[int] = None


@dataclass
class OCRTable:
    """OCR识别的表格"""
    bbox: Tuple[int, int, int, int]
    rows: int
    cols: int
    data: List[List[str]]
    confidence: float = 0.0


@dataclass
class OCRFormField:
    """OCR识别的表单字段"""
    label: str
    value: str
    label_bbox: Optional[Tuple[int, int, int, int]] = None
    value_bbox: Optional[Tuple[int, int, int, int]] = None
    confidence: float = 0.0


@dataclass
class OCRResult:
    """OCR识别结果"""
    raw_text: str = ""
    text_blocks: List[OCRTextBlock] = field(default_factory=list)
    tables: List[OCRTable] = field(default_factory=list)
    form_fields: List[OCRFormField] = field(default_factory=list)
    image_info: Dict[str, Any] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "raw_text": self.raw_text,
            "text_blocks": [
                {
                    "text": b.text,
                    "confidence": b.confidence,
                    "bbox": b.bbox,
                    "language": b.language,
                }
                for b in self.text_blocks
            ],
            "tables": [
                {
                    "rows": t.rows,
                    "cols": t.cols,
                    "data": t.data,
                    "confidence": t.confidence,
                }
                for t in self.tables
            ],
            "form_fields": [
                {
                    "label": f.label,
                    "value": f.value,
                    "confidence": f.confidence,
                }
                for f in self.form_fields
            ],
            "image_info": self.image_info,
            "processing_time_ms": self.processing_time_ms,
        }


class ImagePreprocessor:
    """图像预处理器"""
    
    def __init__(self):
        self.logger = logging.getLogger("openclaw.extractors.image.preprocessor")
        self._check_dependencies()
    
    def _check_dependencies(self) -> None:
        """检查依赖库"""
        try:
            import cv2
            self.cv2 = cv2
        except ImportError:
            self.logger.warning("OpenCV未安装，部分预处理功能受限")
            self.cv2 = None
        
        try:
            from PIL import Image, ImageEnhance, ImageFilter
            self.PILImage = Image
            self.ImageEnhance = ImageEnhance
            self.ImageFilter = ImageFilter
        except ImportError:
            self.logger.warning("PIL未安装，图像处理功能受限")
            self.PILImage = None
    
    def preprocess(
        self,
        image: Any,
        resize_max_dim: Optional[int] = 4096,
        contrast_enhance: bool = True,
        denoise: bool = True,
        deskew: bool = True,
    ) -> Any:
        """
        预处理图像
        
        Args:
            image: 输入图像（PIL Image或numpy数组）
            resize_max_dim: 最大尺寸限制
            contrast_enhance: 是否增强对比度
            denoise: 是否降噪
            deskew: 是否纠偏
        
        Returns:
            预处理后的图像
        """
        if self.PILImage and isinstance(image, self.PILImage.Image):
            img = image.copy()
        elif self.cv2 and isinstance(image, np.ndarray):
            img = self.PILImage.fromarray(image)
        else:
            return image
        
        # 调整大小
        if resize_max_dim:
            img = self._resize_image(img, resize_max_dim)
        
        # 转换为灰度图
        if img.mode != 'L':
            img = img.convert('L')
        
        # 增强对比度
        if contrast_enhance:
            img = self._enhance_contrast(img)
        
        # 降噪
        if denoise:
            img = self._denoise(img)
        
        # 纠偏
        if deskew:
            img = self._deskew(img)
        
        return img
    
    def _resize_image(self, img: Any, max_dim: int) -> Any:
        """调整图像大小"""
        width, height = img.size
        if max(width, height) > max_dim:
            ratio = max_dim / max(width, height)
            new_size = (int(width * ratio), int(height * ratio))
            img = img.resize(new_size, self.PILImage.LANCZOS)
        return img
    
    def _enhance_contrast(self, img: Any) -> Any:
        """增强对比度"""
        enhancer = self.ImageEnhance.Contrast(img)
        return enhancer.enhance(1.5)
    
    def _denoise(self, img: Any) -> Any:
        """降噪处理"""
        if self.cv2:
            img_array = np.array(img)
            denoised = self.cv2.fastNlMeansDenoising(img_array, None, 10, 7, 21)
            return self.PILImage.fromarray(denoised)
        else:
            return img.filter(self.ImageFilter.MedianFilter(size=3))
    
    def _deskew(self, img: Any) -> Any:
        """纠偏处理"""
        if not self.cv2:
            return img
        
        img_array = np.array(img)
        
        # 检测边缘
        edges = self.cv2.Canny(img_array, 50, 150, apertureSize=3)
        
        # 检测直线
        lines = self.cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        
        if lines is None or len(lines) == 0:
            return img
        
        # 计算倾斜角度
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 != x1:
                angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                if -45 < angle < 45:  # 只考虑小角度
                    angles.append(angle)
        
        if not angles:
            return img
        
        # 使用中位数角度
        median_angle = np.median(angles)
        
        if abs(median_angle) < 0.5:  # 角度太小，不需要旋转
            return img
        
        # 旋转图像
        (h, w) = img_array.shape[:2]
        center = (w // 2, h // 2)
        M = self.cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = self.cv2.warpAffine(img_array, M, (w, h), flags=self.cv2.INTER_CUBIC, borderMode=self.cv2.BORDER_REPLICATE)
        
        return self.PILImage.fromarray(rotated)


class ImageExtractor:
    """
    图片OCR数据提取器
    
    提供全面的图片文字识别功能，支持多种OCR引擎。
    
    Example:
        >>> from openclaw import ImageExtractor, Config
        >>> extractor = ImageExtractor(Config().image)
        >>> 
        >>> # 识别图片中的文字
        >>> result = extractor.extract("screenshot.png")
        >>> print(result.raw_text)
        >>> 
        >>> # 识别表格
        >>> tables = extractor.extract_tables("table_screenshot.png")
        >>> 
        >>> # 识别表单
        >>> fields = extractor.extract_form_fields("form_screenshot.png")
        
        >>> # 批量处理
        >>> for result in extractor.extract_batch(["1.png", "2.png"]):
        ...     print(result.raw_text)
    """
    
    def __init__(self, config=None):
        """
        初始化图片提取器
        
        Args:
            config: ImageConfig配置对象
        """
        self.config = config
        self.logger = logging.getLogger("openclaw.extractors.image")
        self.preprocessor = ImagePreprocessor()
        self._check_dependencies()
        self._init_ocr_engine()
    
    def _check_dependencies(self) -> None:
        """检查依赖库"""
        try:
            import pytesseract
            self.pytesseract = pytesseract
        except ImportError:
            self.logger.warning("pytesseract未安装，Tesseract OCR功能不可用")
            self.pytesseract = None
        
        try:
            from PIL import Image
            self.PILImage = Image
        except ImportError:
            self.logger.warning("PIL未安装，图像处理功能不可用")
            self.PILImage = None
        
        try:
            import easyocr
            self.easyocr = easyocr
        except ImportError:
            self.logger.warning("easyocr未安装，EasyOCR功能不可用")
            self.easyocr = None
        
        try:
            from paddleocr import PaddleOCR
            self.paddleocr_class = PaddleOCR
        except ImportError:
            self.logger.warning("paddleocr未安装，PaddleOCR功能不可用")
            self.paddleocr_class = None
        
        self.paddleocr = None  # 延迟初始化
    
    def _init_ocr_engine(self) -> None:
        """初始化OCR引擎"""
        engine = self.config.ocr_engine if self.config else "auto"
        
        if engine == "auto":
            # 自动选择最佳引擎
            if self.paddleocr_class:
                engine = "paddle"
            elif self.easyocr:
                engine = "easyocr"
            elif self.pytesseract:
                engine = "tesseract"
            else:
                raise RuntimeError("没有可用的OCR引擎")
        
        self.ocr_engine = engine
        self.logger.info(f"使用OCR引擎: {engine}")
        
        # 初始化PaddleOCR
        if engine == "paddle" and self.paddleocr_class and not self.paddleocr:
            language = self.config.language if self.config else "ch"
            # 转换语言代码
            lang_map = {
                "chi_sim": "ch",
                "chi_tra": "ch",
                "eng": "en",
                "chi_sim+eng": "ch",
            }
            paddle_lang = lang_map.get(language, "ch")
            self.paddleocr = self.paddleocr_class(use_angle_cls=True, lang=paddle_lang)
    
    def extract(
        self,
        image_path: Union[str, Path],
        preprocess: Optional[bool] = None,
    ) -> OCRResult:
        """
        提取图片中的所有数据
        
        Args:
            image_path: 图片文件路径
            preprocess: 是否预处理图像
        
        Returns:
            OCRResult: OCR识别结果
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"文件不存在: {image_path}")
        
        self.logger.info(f"开始OCR识别: {image_path}")
        
        import time
        start_time = time.time()
        
        # 加载图像
        img = self._load_image(image_path)
        
        # 预处理
        if preprocess is None:
            preprocess = self.config.preprocess if self.config else True
        
        if preprocess:
            img = self.preprocessor.preprocess(
                img,
                resize_max_dim=self.config.resize_max_dim if self.config else 4096,
                contrast_enhance=self.config.contrast_enhance if self.config else True,
                denoise=self.config.denoise if self.config else True,
                deskew=self.config.deskew if self.config else True,
            )
        
        # OCR识别
        result = OCRResult()
        result.image_info = {
            "path": str(image_path),
            "size": img.size if self.PILImage else None,
            "mode": img.mode if self.PILImage else None,
        }
        
        # 文本识别
        text_result = self._recognize_text(img)
        result.raw_text = text_result["text"]
        result.text_blocks = text_result["blocks"]
        
        # 表格识别
        if self.config and self.config.detect_tables:
            result.tables = self._recognize_tables(img)
        
        result.processing_time_ms = (time.time() - start_time) * 1000
        
        self.logger.info(
            f"OCR识别完成: {len(result.text_blocks)}个文本块, "
            f"{len(result.tables)}个表格, 耗时: {result.processing_time_ms:.2f}ms"
        )
        
        return result
    
    def _load_image(self, image_path: Union[str, Path]) -> Any:
        """加载图像"""
        if not self.PILImage:
            raise RuntimeError("PIL未安装，无法加载图像")
        
        return self.PILImage.open(image_path)
    
    def _recognize_text(self, img: Any) -> Dict[str, Any]:
        """识别文本"""
        if self.ocr_engine == "tesseract":
            return self._recognize_with_tesseract(img)
        elif self.ocr_engine == "easyocr":
            return self._recognize_with_easyocr(img)
        elif self.ocr_engine == "paddle":
            return self._recognize_with_paddle(img)
        else:
            raise RuntimeError(f"不支持的OCR引擎: {self.ocr_engine}")
    
    def _recognize_with_tesseract(self, img: Any) -> Dict[str, Any]:
        """使用Tesseract识别"""
        if not self.pytesseract:
            raise RuntimeError("pytesseract未安装")
        
        language = self.config.language if self.config else "chi_sim+eng"
        
        # 获取详细数据
        data = self.pytesseract.image_to_data(img, lang=language, output_type=self.pytesseract.Output.DICT)
        
        blocks = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            if int(data['conf'][i]) > 0:  # 只保留有置信度的文本
                text = data['text'][i].strip()
                if text:
                    block = OCRTextBlock(
                        text=text,
                        confidence=float(data['conf'][i]) / 100,
                        bbox=(
                            data['left'][i],
                            data['top'][i],
                            data['width'][i],
                            data['height'][i],
                        ),
                    )
                    blocks.append(block)
        
        # 获取完整文本
        full_text = self.pytesseract.image_to_string(img, lang=language)
        
        return {
            "text": full_text.strip(),
            "blocks": blocks,
        }
    
    def _recognize_with_easyocr(self, img: Any) -> Dict[str, Any]:
        """使用EasyOCR识别"""
        if not self.easyocr:
            raise RuntimeError("easyocr未安装")
        
        # 延迟初始化reader
        if not hasattr(self, '_easyocr_reader'):
            language = self.config.language if self.config else "ch_sim+en"
            lang_list = language.replace("chi_sim", "ch_sim").replace("chi_tra", "ch_tra").split("+")
            self._easyocr_reader = self.easyocr.Reader(lang_list)
        
        # 转换图像为numpy数组
        img_array = np.array(img)
        
        # 识别
        results = self._easyocr_reader.readtext(img_array)
        
        blocks = []
        texts = []
        
        for result in results:
            bbox, text, confidence = result
            blocks.append(OCRTextBlock(
                text=text,
                confidence=confidence,
                bbox=(
                    int(bbox[0][0]),
                    int(bbox[0][1]),
                    int(bbox[2][0] - bbox[0][0]),
                    int(bbox[2][1] - bbox[0][1]),
                ),
            ))
            texts.append(text)
        
        return {
            "text": "\n".join(texts),
            "blocks": blocks,
        }
    
    def _recognize_with_paddle(self, img: Any) -> Dict[str, Any]:
        """使用PaddleOCR识别"""
        if not self.paddleocr:
            raise RuntimeError("paddleocr未安装")
        
        # 转换图像为numpy数组
        img_array = np.array(img)
        
        # 识别
        result = self.paddleocr.ocr(img_array, cls=True)
        
        blocks = []
        texts = []
        
        if result and result[0]:
            for line in result[0]:
                if line:
                    bbox, (text, confidence) = line
                    blocks.append(OCRTextBlock(
                        text=text,
                        confidence=confidence,
                        bbox=(
                            int(bbox[0][0]),
                            int(bbox[0][1]),
                            int(bbox[2][0] - bbox[0][0]),
                            int(bbox[2][1] - bbox[0][1]),
                        ),
                    ))
                    texts.append(text)
        
        return {
            "text": "\n".join(texts),
            "blocks": blocks,
        }
    
    def _recognize_tables(self, img: Any) -> List[OCRTable]:
        """识别表格"""
        tables = []
        
        # 简单的表格检测逻辑
        # 实际应用中可以使用专门的表格检测模型
        if self.preprocessor.cv2:
            img_array = np.array(img)
            
            # 检测水平和垂直线
            horizontal_kernel = self.preprocessor.cv2.getStructuringElement(
                self.preprocessor.cv2.MORPH_RECT, (40, 1)
            )
            vertical_kernel = self.preprocessor.cv2.getStructuringElement(
                self.preprocessor.cv2.MORPH_RECT, (1, 40)
            )
            
            # 二值化
            _, binary = self.preprocessor.cv2.threshold(
                img_array, 150, 255, self.preprocessor.cv2.THRESH_BINARY_INV
            )
            
            # 检测线条
            horizontal_lines = self.preprocessor.cv2.morphologyEx(
                binary, self.preprocessor.cv2.MORPH_OPEN, horizontal_kernel, iterations=2
            )
            vertical_lines = self.preprocessor.cv2.morphologyEx(
                binary, self.preprocessor.cv2.MORPH_OPEN, vertical_kernel, iterations=2
            )
            
            # 合并线条
            table_structure = self.preprocessor.cv2.addWeighted(
                horizontal_lines, 0.5, vertical_lines, 0.5, 0.0
            )
            
            # 查找轮廓
            contours, _ = self.preprocessor.cv2.findContours(
                table_structure, self.preprocessor.cv2.RETR_TREE, self.preprocessor.cv2.CHAIN_APPROX_SIMPLE
            )
            
            # 分析轮廓以检测表格
            for contour in contours:
                x, y, w, h = self.preprocessor.cv2.boundingRect(contour)
                
                # 过滤太小的区域
                if w > 200 and h > 100:
                    # 这里可以进一步分析表格结构
                    # 简化处理，返回基本表格信息
                    table = OCRTable(
                        bbox=(x, y, w, h),
                        rows=0,
                        cols=0,
                        data=[],
                    )
                    tables.append(table)
        
        return tables
    
    def extract_text(
        self,
        image_path: Union[str, Path],
        preprocess: bool = True,
    ) -> str:
        """
        提取图片中的纯文本
        
        Args:
            image_path: 图片文件路径
            preprocess: 是否预处理图像
        
        Returns:
            str: 提取的文本
        """
        result = self.extract(image_path, preprocess)
        return result.raw_text
    
    def extract_tables(
        self,
        image_path: Union[str, Path],
    ) -> List[OCRTable]:
        """
        提取图片中的表格
        
        Args:
            image_path: 图片文件路径
        
        Returns:
            List[OCRTable]: 表格列表
        """
        result = self.extract(image_path)
        return result.tables
    
    def extract_form_fields(
        self,
        image_path: Union[str, Path],
    ) -> List[OCRFormField]:
        """
        提取图片中的表单字段
        
        Args:
            image_path: 图片文件路径
        
        Returns:
            List[OCRFormField]: 表单字段列表
        """
        result = self.extract(image_path)
        
        # 简单的表单字段检测
        # 基于文本块的位置关系识别标签-值对
        fields = []
        blocks = result.text_blocks
        
        # 按行分组
        rows = {}
        for block in blocks:
            y = block.bbox[1]
            # 找到最接近的行
            row_key = round(y / 20) * 20  # 20像素的容差
            if row_key not in rows:
                rows[row_key] = []
            rows[row_key].append(block)
        
        # 分析每行，寻找标签-值对
        for row_key in sorted(rows.keys()):
            row_blocks = sorted(rows[row_key], key=lambda b: b.bbox[0])
            
            # 简单的启发式：如果一行有两个文本块，可能是标签-值对
            if len(row_blocks) >= 2:
                # 检查是否有冒号或特定模式
                for i in range(len(row_blocks) - 1):
                    label = row_blocks[i].text.strip()
                    value = row_blocks[i + 1].text.strip()
                    
                    # 如果标签以冒号结尾，可能是表单字段
                    if label.endswith(":") or label.endswith("："):
                        fields.append(OCRFormField(
                            label=label.rstrip(":："),
                            value=value,
                            label_bbox=row_blocks[i].bbox,
                            value_bbox=row_blocks[i + 1].bbox,
                        ))
        
        return fields
    
    def extract_batch(
        self,
        image_paths: List[Union[str, Path]],
    ) -> List[OCRResult]:
        """
        批量提取多个图片
        
        Args:
            image_paths: 图片路径列表
        
        Returns:
            List[OCRResult]: 每个图片的识别结果
        """
        results = []
        for image_path in image_paths:
            try:
                result = self.extract(image_path)
                results.append(result)
            except Exception as e:
                self.logger.error(f"处理图片 {image_path} 失败: {e}")
                results.append(OCRResult())
        return results
    
    def extract_from_pdf_page(
        self,
        pdf_path: Union[str, Path],
        page_number: int = 1,
        dpi: int = 300,
    ) -> OCRResult:
        """
        从PDF页面提取（将PDF页面转为图片后OCR）
        
        Args:
            pdf_path: PDF文件路径
            page_number: 页码（从1开始）
            dpi: 转换分辨率
        
        Returns:
            OCRResult: OCR识别结果
        """
        try:
            from pdf2image import convert_from_path
        except ImportError:
            raise RuntimeError("pdf2image未安装，无法从PDF提取")
        
        # 转换PDF页面为图片
        images = convert_from_path(
            pdf_path,
            dpi=dpi,
            first_page=page_number,
            last_page=page_number,
        )
        
        if not images:
            raise ValueError(f"无法提取PDF第{page_number}页")
        
        # 对图片进行OCR
        img = images[0]
        
        import time
        start_time = time.time()
        
        # 预处理
        if self.config and self.config.preprocess:
            img = self.preprocessor.preprocess(img)
        
        # OCR识别
        result = OCRResult()
        text_result = self._recognize_text(img)
        result.raw_text = text_result["text"]
        result.text_blocks = text_result["blocks"]
        result.processing_time_ms = (time.time() - start_time) * 1000
        
        return result
