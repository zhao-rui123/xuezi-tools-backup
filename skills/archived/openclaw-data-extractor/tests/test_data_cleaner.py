"""
数据清洗器测试
"""

import unittest


class TestDataCleaner(unittest.TestCase):
    """测试数据清洗器"""
    
    def setUp(self):
        """测试前准备"""
        try:
            from openclaw.cleaners.data_cleaner import DataCleaner, DataCleaningConfig
            self.DataCleaner = DataCleaner
            self.DataCleaningConfig = DataCleaningConfig
        except ImportError:
            self.skipTest("数据清洗器依赖未安装")
    
    def test_config_creation(self):
        """测试配置创建"""
        config = self.DataCleaningConfig()
        self.assertTrue(config.remove_duplicates)
        self.assertTrue(config.handle_missing)
    
    def test_cleaner_creation(self):
        """测试清洗器创建"""
        config = self.DataCleaningConfig()
        cleaner = self.DataCleaner(config)
        self.assertIsNotNone(cleaner)
    
    def test_text_cleaning(self):
        """测试文本清洗"""
        config = self.DataCleaningConfig()
        cleaner = self.DataCleaner(config)
        
        # 测试空白去除
        result = cleaner._clean_text("  hello world  ")
        self.assertEqual(result, "hello world")
        
        # 测试Unicode规范化
        result = cleaner._normalize_unicode("café")
        self.assertEqual(result, "café")
        
        # 测试控制字符去除
        result = cleaner._remove_control_chars("hello\x00world")
        self.assertEqual(result, "helloworld")


class TestCleaningReport(unittest.TestCase):
    """测试清洗报告"""
    
    def test_report_creation(self):
        """测试报告对象创建"""
        try:
            from openclaw.cleaners.data_cleaner import CleaningReport
        except ImportError:
            self.skipTest("数据清洗器依赖未安装")
        
        report = CleaningReport()
        self.assertEqual(report.rows_before, 0)
        self.assertEqual(report.rows_after, 0)


if __name__ == "__main__":
    unittest.main()
