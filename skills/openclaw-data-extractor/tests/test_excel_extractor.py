"""
Excel提取器测试
"""

import unittest
from pathlib import Path
import tempfile


class TestExcelExtractor(unittest.TestCase):
    """测试Excel提取器"""
    
    def setUp(self):
        """测试前准备"""
        try:
            from openclaw.extractors.excel_extractor import ExcelExtractor, ExcelConfig
            self.ExcelExtractor = ExcelExtractor
            self.ExcelConfig = ExcelConfig
        except ImportError:
            self.skipTest("Excel提取器依赖未安装")
    
    def test_config_creation(self):
        """测试配置创建"""
        config = self.ExcelConfig()
        self.assertEqual(config.header_row, 0)
        self.assertTrue(config.evaluate_formulas)
    
    def test_extractor_creation(self):
        """测试提取器创建"""
        config = self.ExcelConfig()
        extractor = self.ExcelExtractor(config)
        self.assertIsNotNone(extractor)


class TestExcelSheet(unittest.TestCase):
    """测试Excel工作表"""
    
    def test_sheet_creation(self):
        """测试工作表对象创建"""
        try:
            from openclaw.extractors.excel_extractor import ExcelSheet
        except ImportError:
            self.skipTest("Excel提取器依赖未安装")
        
        data = [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]]
        sheet = ExcelSheet(name="Sheet1", index=0, data=data)
        
        self.assertEqual(sheet.name, "Sheet1")
        self.assertEqual(sheet.max_row, 3)
        self.assertEqual(sheet.max_col, 2)


if __name__ == "__main__":
    unittest.main()
