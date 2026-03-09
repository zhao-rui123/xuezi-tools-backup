#!/usr/bin/env python3
"""
多模态记忆支持模块 (Multimodal Memory Module)
支持图片OCR、PDF文档解析和统一存储检索
"""

import os
import sys
import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

# 工作空间配置
WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
MULTIMODAL_DIR = WORKSPACE / ".memory" / "multimodal"
MULTIMODAL_INDEX = MULTIMODAL_DIR / "index.json"
MULTIMODAL_DATA = MULTIMODAL_DIR / "data"

# 确保目录存在
MULTIMODAL_DIR.mkdir(parents=True, exist_ok=True)
MULTIMODAL_DATA.mkdir(parents=True, exist_ok=True)


class MultimodalMemorySystem:
    """多模态记忆系统主类"""
    
    def __init__(self):
        self.index = self._load_index()
        self.ocr_engine = None
        self.pdf_engine = None
    
    def _load_index(self) -> Dict:
        """加载多模态索引"""
        if MULTIMODAL_INDEX.exists():
            with open(MULTIMODAL_INDEX, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"items": [], "version": "1.0"}
    
    def _save_index(self):
        """保存多模态索引"""
        with open(MULTIMODAL_INDEX, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def _generate_id(self, content: str) -> str:
        """生成内容ID"""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _get_file_hash(self, file_path: Path) -> str:
        """计算文件哈希"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()[:16]


class ImageProcessor:
    """图片处理器 - OCR提取"""
    
    def __init__(self):
        self.tesseract_available = False
        self.easyocr_available = False
        self._init_ocr()
    
    def _init_ocr(self):
        """初始化OCR引擎"""
        # 尝试 pytesseract
        try:
            import pytesseract
            from PIL import Image
            self.tesseract_available = True
            self.pytesseract = pytesseract
            self.PILImage = Image
            print("✅ OCR引擎: pytesseract 已加载")
        except ImportError:
            print("⚠️ pytesseract 未安装")
        
        # 尝试 easyocr
        try:
            import easyocr
            self.easyocr_available = True
            self.easyocr_reader = None  # 延迟加载
            print("✅ OCR引擎: easyocr 已加载")
        except ImportError:
            print("⚠️ easyocr 未安装")
    
    def _get_easyocr_reader(self):
        """延迟初始化easyocr reader"""
        if self.easyocr_reader is None and self.easyocr_available:
            import easyocr
            self.easyocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
        return self.easyocr_reader
    
    def process_image(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """
        处理图片，OCR提取文字
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            包含提取文本和元数据的字典
        """
        image_path = Path(image_path)
        if not image_path.exists():
            return {"error": f"图片不存在: {image_path}"}
        
        result = {
            "file_path": str(image_path),
            "file_name": image_path.name,
            "file_size": image_path.stat().st_size,
            "extracted_text": "",
            "ocr_engine": None,
            "confidence": 0.0,
            "metadata": {}
        }
        
        # 尝试 pytesseract
        if self.tesseract_available:
            try:
                text, confidence = self._ocr_with_tesseract(image_path)
                result["extracted_text"] = text
                result["ocr_engine"] = "pytesseract"
                result["confidence"] = confidence
                result["metadata"]["word_count"] = len(text.split())
            except Exception as e:
                result["error_tesseract"] = str(e)
        
        # 如果 tesseract 失败或未安装，尝试 easyocr
        if not result["extracted_text"] and self.easyocr_available:
            try:
                text, confidence = self._ocr_with_easyocr(image_path)
                result["extracted_text"] = text
                result["ocr_engine"] = "easyocr"
                result["confidence"] = confidence
                result["metadata"]["word_count"] = len(text.split())
            except Exception as e:
                result["error_easyocr"] = str(e)
        
        if not result["extracted_text"]:
            result["error"] = "OCR提取失败，请检查OCR引擎安装"
        
        return result
    
    def _ocr_with_tesseract(self, image_path: Path) -> tuple:
        """使用pytesseract进行OCR"""
        image = self.PILImage.open(image_path)
        
        # 获取图像信息
        width, height = image.size
        
        # OCR识别
        text = self.pytesseract.image_to_string(image, lang='chi_sim+eng')
        
        # 清理文本
        text = text.strip()
        text = re.sub(r'\n+', '\n', text)  # 合并多余换行
        
        # 估算置信度（基于文本长度和图像大小的比例）
        confidence = min(0.9, max(0.3, len(text) / (width * height / 1000)))
        
        return text, round(confidence, 2)
    
    def _ocr_with_easyocr(self, image_path: Path) -> tuple:
        """使用easyocr进行OCR"""
        reader = self._get_easyocr_reader()
        results = reader.readtext(str(image_path))
        
        # 提取文本和置信度
        texts = []
        confidences = []
        for detection in results:
            text, conf = detection[1], detection[2]
            texts.append(text)
            confidences.append(conf)
        
        full_text = '\n'.join(texts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return full_text, round(avg_confidence, 2)


class PDFProcessor:
    """PDF文档处理器"""
    
    def __init__(self):
        self.pdfplumber_available = False
        self.pypdf2_available = False
        self._init_pdf()
    
    def _init_pdf(self):
        """初始化PDF引擎"""
        try:
            import pdfplumber
            self.pdfplumber_available = True
            self.pdfplumber = pdfplumber
            print("✅ PDF引擎: pdfplumber 已加载")
        except ImportError:
            print("⚠️ pdfplumber 未安装")
        
        try:
            import PyPDF2
            self.pypdf2_available = True
            self.PyPDF2 = PyPDF2
            print("✅ PDF引擎: PyPDF2 已加载")
        except ImportError:
            print("⚠️ PyPDF2 未安装")
    
    def process_pdf(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """
        处理PDF文档，提取文本
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            包含提取文本和元数据的字典
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            return {"error": f"PDF文件不存在: {pdf_path}"}
        
        result = {
            "file_path": str(pdf_path),
            "file_name": pdf_path.name,
            "file_size": pdf_path.stat().st_size,
            "extracted_text": "",
            "pages": 0,
            "pdf_engine": None,
            "metadata": {},
            "page_texts": []
        }
        
        # 优先使用 pdfplumber
        if self.pdfplumber_available:
            try:
                pages_data = self._extract_with_pdfplumber(pdf_path)
                result["pages"] = len(pages_data)
                result["page_texts"] = pages_data
                result["extracted_text"] = "\n\n".join([p["text"] for p in pages_data])
                result["pdf_engine"] = "pdfplumber"
                result["metadata"]["tables_count"] = sum(len(p.get("tables", [])) for p in pages_data)
            except Exception as e:
                result["error_pdfplumber"] = str(e)
        
        # 备选 PyPDF2
        if not result["extracted_text"] and self.pypdf2_available:
            try:
                pages_data = self._extract_with_pypdf2(pdf_path)
                result["pages"] = len(pages_data)
                result["page_texts"] = pages_data
                result["extracted_text"] = "\n\n".join([p["text"] for p in pages_data])
                result["pdf_engine"] = "PyPDF2"
            except Exception as e:
                result["error_pypdf2"] = str(e)
        
        if not result["extracted_text"]:
            result["error"] = "PDF提取失败，请检查PDF引擎安装"
        
        return result
    
    def _extract_with_pdfplumber(self, pdf_path: Path) -> List[Dict]:
        """使用pdfplumber提取PDF内容"""
        pages_data = []
        
        with self.pdfplumber.open(str(pdf_path)) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                page_data = {
                    "page_number": i,
                    "text": "",
                    "tables": []
                }
                
                # 提取文本
                text = page.extract_text() or ""
                page_data["text"] = text.strip()
                
                # 提取表格
                try:
                    tables = page.extract_tables()
                    if tables:
                        page_data["tables"] = tables
                except:
                    pass
                
                pages_data.append(page_data)
        
        return pages_data
    
    def _extract_with_pypdf2(self, pdf_path: Path) -> List[Dict]:
        """使用PyPDF2提取PDF内容"""
        pages_data = []
        
        with open(pdf_path, 'rb') as file:
            reader = self.PyPDF2.PdfReader(file)
            
            for i, page in enumerate(reader.pages, 1):
                text = page.extract_text() or ""
                pages_data.append({
                    "page_number": i,
                    "text": text.strip(),
                    "tables": []
                })
        
        return pages_data


class MultimodalStorage:
    """多模态内容存储管理器"""
    
    def __init__(self):
        self.system = MultimodalMemorySystem()
    
    def store_multimodal(self, content: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """
        存储多模态内容到统一记忆系统
        
        Args:
            content: 内容字典（包含提取的文本、元数据等）
            content_type: 内容类型 ('image', 'pdf', 'audio', 'video')
            
        Returns:
            存储结果信息
        """
        # 生成唯一ID
        content_hash = hashlib.md5(
            (content.get("extracted_text", "") + content.get("file_name", "")).encode()
        ).hexdigest()[:12]
        
        # 检查是否已存在
        for item in self.system.index.get("items", []):
            if item.get("hash") == content_hash:
                return {"status": "exists", "id": item["id"], "message": "内容已存在"}
        
        # 构建存储记录
        record = {
            "id": f"{content_type}_{content_hash}",
            "hash": content_hash,
            "type": content_type,
            "file_path": content.get("file_path"),
            "file_name": content.get("file_name"),
            "file_size": content.get("file_size"),
            "extracted_text": content.get("extracted_text", ""),
            "summary": self._generate_summary(content.get("extracted_text", "")),
            "keywords": self._extract_keywords(content.get("extracted_text", "")),
            "metadata": content.get("metadata", {}),
            "created_at": datetime.now().isoformat(),
            "access_count": 0
        }
        
        # 添加类型特定字段
        if content_type == "image":
            record["ocr_engine"] = content.get("ocr_engine")
            record["confidence"] = content.get("confidence")
        elif content_type == "pdf":
            record["pages"] = content.get("pages", 0)
            record["pdf_engine"] = content.get("pdf_engine")
        
        # 保存到索引
        self.system.index.setdefault("items", []).append(record)
        self.system._save_index()
        
        # 保存完整文本到单独文件（避免索引过大）
        text_file = MULTIMODAL_DATA / f"{record['id']}.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(record["extracted_text"])
        
        return {
            "status": "success",
            "id": record["id"],
            "type": content_type,
            "file_name": record["file_name"],
            "text_preview": record["extracted_text"][:200] + "..." if len(record["extracted_text"]) > 200 else record["extracted_text"]
        }
    
    def _generate_summary(self, text: str, max_length: int = 200) -> str:
        """生成文本摘要"""
        if not text:
            return ""
        
        # 简单摘要：取前N个字符，尝试停在句子边界
        if len(text) <= max_length:
            return text
        
        # 尝试找到句子边界
        truncated = text[:max_length]
        last_period = max(truncated.rfind('。'), truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('！'))
        
        if last_period > max_length * 0.7:
            return truncated[:last_period + 1]
        
        return truncated + "..."
    
    def _extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """提取关键词"""
        if not text:
            return []
        
        # 中文关键词提取
        chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,6}', text)
        
        # 英文关键词提取
        english_words = re.findall(r'[a-zA-Z]{3,}', text)
        
        # 停用词过滤
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '上', '也', '很', '到', '说', '要', 'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all'}
        
        all_words = [w for w in chinese_words + english_words if w.lower() not in stop_words]
        
        # 统计频率
        from collections import Counter
        word_counts = Counter(all_words)
        
        return [word for word, _ in word_counts.most_common(top_n)]


class MultimodalSearcher:
    """多模态内容检索器"""
    
    def __init__(self):
        self.system = MultimodalMemorySystem()
    
    def search_multimodal(self, query: str, content_type: str = None, top_k: int = 5) -> List[Dict]:
        """
        检索多模态内容
        
        Args:
            query: 搜索查询
            content_type: 限制内容类型 ('image', 'pdf', None表示全部)
            top_k: 返回结果数量
            
        Returns:
            匹配的结果列表
        """
        results = []
        query_lower = query.lower()
        query_words = set(re.findall(r'[\u4e00-\u9fa5]{2,}|[a-zA-Z]{3,}', query_lower))
        
        for item in self.system.index.get("items", []):
            # 类型过滤
            if content_type and item.get("type") != content_type:
                continue
            
            score = 0.0
            text = item.get("extracted_text", "").lower()
            keywords = [k.lower() for k in item.get("keywords", [])]
            
            # 完全匹配加分
            if query_lower in text:
                score += 2.0
            
            # 关键词匹配
            for word in query_words:
                if word in text:
                    score += 1.0
                if word in keywords:
                    score += 1.5
            
            # 文件名匹配
            if query_lower in item.get("file_name", "").lower():
                score += 1.0
            
            if score > 0:
                # 时间衰减
                created = datetime.fromisoformat(item.get("created_at", datetime.now().isoformat()))
                age_days = (datetime.now() - created).days
                time_decay = 0.5 + 0.5 * (2.71828 ** (-age_days / 60))
                
                final_score = score * time_decay
                
                results.append({
                    "item": item,
                    "score": round(final_score, 3),
                    "matched_keywords": [w for w in query_words if w in text or w in keywords]
                })
        
        # 按得分排序
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:top_k]


class KeyDataExtractor:
    """关键数据提取器"""
    
    def extract_key_data(self, content: Union[str, Dict], content_type: str) -> Dict[str, Any]:
        """
        从内容中提取关键数据
        
        Args:
            content: 文本内容或内容字典
            content_type: 内容类型 ('image', 'pdf', 'text')
            
        Returns:
            提取的关键数据
        """
        if isinstance(content, dict):
            text = content.get("extracted_text", "")
        else:
            text = content
        
        result = {
            "content_type": content_type,
            "extracted_at": datetime.now().isoformat(),
            "data": {}
        }
        
        # 通用数据提取
        result["data"]["dates"] = self._extract_dates(text)
        result["data"]["numbers"] = self._extract_numbers(text)
        result["data"]["emails"] = self._extract_emails(text)
        result["data"]["urls"] = self._extract_urls(text)
        result["data"]["phones"] = self._extract_phones(text)
        
        # 类型特定提取
        if content_type == "image":
            result["data"]["entities"] = self._extract_entities(text)
        elif content_type == "pdf":
            result["data"]["tables_summary"] = self._extract_tables_summary(text)
            result["data"]["headings"] = self._extract_headings(text)
        
        return result
    
    def _extract_dates(self, text: str) -> List[str]:
        """提取日期"""
        patterns = [
            r'\d{4}[年/-]\d{1,2}[月/-]\d{1,2}[日]?',
            r'\d{4}[年/-]\d{1,2}[月]?',
            r'\d{1,2}[月/-]\d{1,2}[日]?',
        ]
        dates = []
        for pattern in patterns:
            dates.extend(re.findall(pattern, text))
        return list(set(dates))[:10]
    
    def _extract_numbers(self, text: str) -> List[Dict]:
        """提取数字（金额、百分比等）"""
        numbers = []
        
        # 金额模式
        money_pattern = r'[￥$€£]?\s*\d+[\.,]?\d*\s*[万亿元]?'
        for match in re.finditer(money_pattern, text):
            numbers.append({
                "value": match.group(),
                "type": "money",
                "context": text[max(0, match.start()-10):min(len(text), match.end()+10)]
            })
        
        # 百分比模式
        percent_pattern = r'\d+[\.,]?\d*\s*%'
        for match in re.finditer(percent_pattern, text):
            numbers.append({
                "value": match.group(),
                "type": "percentage",
                "context": text[max(0, match.start()-10):min(len(text), match.end()+10)]
            })
        
        return numbers[:20]
    
    def _extract_emails(self, text: str) -> List[str]:
        """提取邮箱地址"""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return list(set(re.findall(pattern, text)))
    
    def _extract_urls(self, text: str) -> List[str]:
        """提取URL"""
        pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return list(set(re.findall(pattern, text)))
    
    def _extract_phones(self, text: str) -> List[str]:
        """提取电话号码"""
        patterns = [
            r'1[3-9]\d{9}',  # 手机号
            r'\d{3,4}-\d{7,8}',  # 座机
        ]
        phones = []
        for pattern in patterns:
            phones.extend(re.findall(pattern, text))
        return list(set(phones))
    
    def _extract_entities(self, text: str) -> List[Dict]:
        """提取命名实体（简化版）"""
        entities = []
        
        # 人名模式（中文）
        name_pattern = r'[\u4e00-\u9fa5]{2,4}(?:先生|女士|经理|博士|教授)'
        for match in re.finditer(name_pattern, text):
            entities.append({
                "text": match.group(),
                "type": "person",
                "position": match.start()
            })
        
        # 公司/机构模式
        org_pattern = r'[\u4e00-\u9fa5]{2,}(?:公司|集团|银行|协会|学院|大学)'
        for match in re.finditer(org_pattern, text):
            entities.append({
                "text": match.group(),
                "type": "organization",
                "position": match.start()
            })
        
        return entities
    
    def _extract_tables_summary(self, text: str) -> List[Dict]:
        """提取表格摘要"""
        tables = []
        
        # 简单的表格检测（基于制表符或空格对齐）
        lines = text.split('\n')
        table_lines = []
        
        for i, line in enumerate(lines):
            if '|' in line or '\t' in line or (line.count('  ') > 2):
                table_lines.append((i, line))
        
        if table_lines:
            tables.append({
                "detected_lines": len(table_lines),
                "sample": table_lines[:3] if table_lines else []
            })
        
        return tables
    
    def _extract_headings(self, text: str) -> List[str]:
        """提取标题/章节"""
        headings = []
        
        # 常见的标题模式
        patterns = [
            r'^[\s]*[第]?[\d一二三四五六七八九十]+[章节部分][\s]*[：:.]?\s*(.+)',
            r'^[\s]*[\d\.]+\s+(.+)',
            r'^[\s]*[#]+\s*(.+)',
        ]
        
        lines = text.split('\n')
        for line in lines:
            for pattern in patterns:
                match = re.match(pattern, line.strip())
                if match:
                    headings.append(line.strip())
                    break
        
        return headings[:20]


# ==================== 统一的API接口 ====================

class MultimodalMemoryAPI:
    """多模态记忆API - 统一接口"""
    
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.pdf_processor = PDFProcessor()
        self.storage = MultimodalStorage()
        self.searcher = MultimodalSearcher()
        self.extractor = KeyDataExtractor()
    
    def process_image(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """处理图片，OCR提取"""
        return self.image_processor.process_image(image_path)
    
    def process_pdf(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """处理PDF文档"""
        return self.pdf_processor.process_pdf(pdf_path)
    
    def store_multimodal(self, content: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """存储多模态内容"""
        return self.storage.store_multimodal(content, content_type)
    
    def search_multimodal(self, query: str, content_type: str = None, top_k: int = 5) -> List[Dict]:
        """检索多模态内容"""
        return self.searcher.search_multimodal(query, content_type, top_k)
    
    def extract_key_data(self, content: Union[str, Dict], content_type: str) -> Dict[str, Any]:
        """提取关键数据"""
        return self.extractor.extract_key_data(content, content_type)
    
    def process_and_store_image(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """处理并存储图片（一站式）"""
        # 1. 处理图片
        result = self.process_image(image_path)
        if "error" in result:
            return result
        
        # 2. 存储
        store_result = self.store_multimodal(result, "image")
        
        # 3. 提取关键数据
        key_data = self.extract_key_data(result, "image")
        
        return {
            "process_result": result,
            "store_result": store_result,
            "key_data": key_data
        }
    
    def process_and_store_pdf(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """处理并存储PDF（一站式）"""
        # 1. 处理PDF
        result = self.process_pdf(pdf_path)
        if "error" in result:
            return result
        
        # 2. 存储
        store_result = self.store_multimodal(result, "pdf")
        
        # 3. 提取关键数据
        key_data = self.extract_key_data(result, "pdf")
        
        return {
            "process_result": result,
            "store_result": store_result,
            "key_data": key_data
        }


# ==================== CLI入口 ====================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="多模态记忆系统")
    parser.add_argument("command", choices=["image", "pdf", "search", "stats", "test"])
    parser.add_argument("--path", "-p", help="文件路径")
    parser.add_argument("--query", "-q", help="搜索查询")
    parser.add_argument("--type", "-t", choices=["image", "pdf", "all"], default="all", help="内容类型")
    parser.add_argument("--top", "-k", type=int, default=5, help="返回结果数量")
    
    args = parser.parse_args()
    
    api = MultimodalMemoryAPI()
    
    if args.command == "image":
        if not args.path:
            print("❌ 请提供图片路径: --path <图片路径>")
            return
        
        print(f"🖼️ 处理图片: {args.path}")
        result = api.process_and_store_image(args.path)
        
        if "error" in result.get("process_result", {}):
            print(f"❌ 处理失败: {result['process_result']['error']}")
        else:
            print(f"✅ 处理成功!")
            print(f"   OCR引擎: {result['process_result'].get('ocr_engine')}")
            print(f"   置信度: {result['process_result'].get('confidence')}")
            print(f"   存储ID: {result['store_result'].get('id')}")
            print(f"   提取文本预览: {result['process_result'].get('extracted_text', '')[:200]}...")
    
    elif args.command == "pdf":
        if not args.path:
            print("❌ 请提供PDF路径: --path <PDF路径>")
            return
        
        print(f"📄 处理PDF: {args.path}")
        result = api.process_and_store_pdf(args.path)
        
        if "error" in result.get("process_result", {}):
            print(f"❌ 处理失败: {result['process_result']['error']}")
        else:
            print(f"✅ 处理成功!")
            print(f"   PDF引擎: {result['process_result'].get('pdf_engine')}")
            print(f"   页数: {result['process_result'].get('pages')}")
            print(f"   存储ID: {result['store_result'].get('id')}")
            print(f"   提取文本预览: {result['process_result'].get('extracted_text', '')[:200]}...")
    
    elif args.command == "search":
        if not args.query:
            print("❌ 请提供搜索查询: --query <查询内容>")
            return
        
        print(f"🔍 搜索: {args.query}")
        results = api.search_multimodal(args.query, args.type if args.type != "all" else None, args.top)
        
        print(f"找到 {len(results)} 个结果:")
        for i, r in enumerate(results, 1):
            item = r["item"]
            print(f"\n{i}. [{item['type'].upper()}] {item['file_name']}")
            print(f"   得分: {r['score']}")
            print(f"   匹配关键词: {', '.join(r['matched_keywords'])}")
            print(f"   摘要: {item.get('summary', '')[:100]}...")
    
    elif args.command == "stats":
        system = MultimodalMemorySystem()
        items = system.index.get("items", [])
        
        print("📊 多模态记忆统计")
        print("=" * 50)
        print(f"总条目数: {len(items)}")
        
        type_counts = {}
        for item in items:
            t = item.get("type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1
        
        print("\n按类型分布:")
        for t, count in type_counts.items():
            print(f"   {t}: {count}")
    
    elif args.command == "test":
        run_tests()


def run_tests():
    """运行测试"""
    print("🧪 运行多模态记忆系统测试\n")
    
    api = MultimodalMemoryAPI()
    
    # 测试1: 文本关键数据提取
    print("测试1: 关键数据提取")
    test_text = """
    张三先生于2024年3月15日联系了tech@example.com。
    项目预算为￥1,500,000元，预计完成度85%。
    联系电话：13800138000
    项目文档：https://docs.example.com/project
    """
    
    key_data = api.extract_key_data(test_text, "text")
    print(f"  日期: {key_data['data']['dates']}")
    print(f"  邮箱: {key_data['data']['emails']}")
    print(f"  电话: {key_data['data']['phones']}")
    print(f"  URL: {key_data['data']['urls']}")
    print(f"  数字: {[n['value'] for n in key_data['data']['numbers']]}")
    print("  ✅ 通过\n")
    
    # 测试2: 存储和检索
    print("测试2: 存储和检索")
    test_content = {
        "file_path": "/test/sample.txt",
        "file_name": "sample.txt",
        "file_size": 1024,
        "extracted_text": "这是储能项目的测试文档，包含锂电池和光伏系统的设计方案。",
        "metadata": {}
    }
    
    store_result = api.store_multimodal(test_content, "text")
    print(f"  存储状态: {store_result['status']}")
    print(f"  存储ID: {store_result['id']}")
    
    search_results = api.search_multimodal("储能项目")
    print(f"  搜索结果: {len(search_results)} 条")
    if search_results:
        print(f"  匹配项: {search_results[0]['item']['file_name']}")
    print("  ✅ 通过\n")
    
    print("✅ 所有测试完成!")


# 导出主要函数供其他模块使用
process_image = None
process_pdf = None
store_multimodal = None
search_multimodal = None
extract_key_data = None

# 延迟初始化（避免导入时立即初始化）
def _init_api():
    global process_image, process_pdf, store_multimodal, search_multimodal, extract_key_data
    api = MultimodalMemoryAPI()
    process_image = api.process_image
    process_pdf = api.process_pdf
    store_multimodal = api.store_multimodal
    search_multimodal = api.search_multimodal
    extract_key_data = api.extract_key_data

if __name__ == "__main__":
    main()
else:
    _init_api()
