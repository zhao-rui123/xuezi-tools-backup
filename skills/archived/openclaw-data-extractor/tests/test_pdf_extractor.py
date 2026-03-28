"""
PDF提取器测试
"""

import unittest
from pathlib import Path
import tempfile
import json


class TestPDFExtractor(unittest.TestCase):
    """测试PDF提取器"""
    
    def setUp(self):
        """测试前准备"""
        try:
            from openclaw.extractors.pdf_extractor import PDFExtractor, PDFConfig
            self.PDFExtractor = PDFExtractor
            self.PDFConfig = PDFConfig
        except ImportError:
            self.skipTest("PDF提取器依赖未安装")
    
    def test_config_creation(self):
        """测试配置创建"""
        config = self.PDFConfig()
        self.assertTrue(config.extract_text)
        self.assertTrue(config.extract_tables)
        self.assertFalse(config.extract_images)
    
    def test_extractor_creation(self):
        """测试提取器创建"""
        config = self.PDFConfig()
        extractor = self.PDFExtractor(config)
        self.assertIsNotNone(extractor)
    
    def test_page_range_parsing(self):
        """测试页面范围解析"""
        config = self.PDFConfig()
        extractor = self.PDFExtractor(config)
        
        # 测试各种页面范围格式
        self.assertIsNone(extractor._parse_page_range(None))
        self.assertEqual(extractor._parse_page_range("1"), [1])
        self.assertEqual(extractor._parse_page_range("1-3"), [1, 2, 3])
        self.assertEqual(extractor._parse_page_range("1,3,5"), [1, 3, 5])
        self.assertEqual(extractor._parse_page_range("1-3,5,7-9"), [1, 2, 3, 5, 7, 8, 9])


class TestPDFMetadata(unittest.TestCase):
    """测试PDF元数据"""
    
    def test_metadata_creation(self):
        """测试元数据对象创建"""
        try:
            from openclaw.extractors.pdf_extractor import PDFMetadata
        except ImportError:
            self.skipTest("PDF提取器依赖未安装")
        
        metadata = PDFMetadata()
        self.assertEqual(metadata.pages, 0)
        self.assertFalse(metadata.encrypted)


class TestPDFTable(unittest.TestCase):
    """测试PDF表格"""
    
    def test_table_creation(self):
        """测试表格对象创建"""
        try:
            from openclaw.extractors.pdf_extractor import PDFTable
        except ImportError:
            self.skipTest("PDF提取器依赖未安装")
        
        data = [["Header1", "Header2"], ["Value1", "Value2"]]
        table = PDFTable(page=1, table_index=0, data=data)
        
        self.assertEqual(table.page, 1)
        self.assertEqual(table.rows, 2)
        self.assertEqual(table.cols, 2)


if __name__ == "__main__":
    unittest.main()
