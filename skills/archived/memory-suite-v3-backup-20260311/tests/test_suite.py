#!/usr/bin/env python3
"""
Memory Suite v3.0 - 测试套件
"""

import sys
import unittest
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCoreModules(unittest.TestCase):
    """测试核心模块"""
    
    def test_real_time_import(self):
        """测试实时保存模块导入"""
        from core.real_time import RealTimeSaver
        self.assertTrue(True)
    
    def test_archiver_import(self):
        """测试归档模块导入"""
        from core.archiver import Archiver
        self.assertTrue(True)
    
    def test_indexer_import(self):
        """测试索引模块导入"""
        from core.indexer import IndexManager
        self.assertTrue(True)
    
    def test_analyzer_import(self):
        """测试分析模块导入"""
        from core.analyzer import AnalysisManager
        self.assertTrue(True)


class TestAppModules(unittest.TestCase):
    """测试应用模块"""
    
    def test_qa_import(self):
        """测试问答模块导入"""
        from apps.qa import QASystem
        self.assertTrue(True)
    
    def test_advisor_import(self):
        """测试决策支持模块导入"""
        from apps.advisor import DecisionAdvisor
        self.assertTrue(True)
    
    def test_recommender_import(self):
        """测试推荐模块导入"""
        from apps.recommender import Recommender
        self.assertTrue(True)
    
    def test_profiler_import(self):
        """测试画像模块导入"""
        from apps.profiler import UserProfile
        self.assertTrue(True)


class TestIntegrationModules(unittest.TestCase):
    """测试集成模块"""
    
    def test_kb_sync_import(self):
        """测试知识库同步导入"""
        from integration.kb_sync import KBSync
        self.assertTrue(True)
    
    def test_notifier_import(self):
        """测试通知模块导入"""
        from integration.notifier import Notifier
        self.assertTrue(True)
    
    def test_backup_helper_import(self):
        """测试备份协助导入"""
        from integration.backup_helper import BackupHelper
        self.assertTrue(True)


class TestSystem(unittest.TestCase):
    """测试系统功能"""
    
    def test_config_exists(self):
        """测试配置文件存在"""
        config_path = Path(__file__).parent.parent / "config" / "config.json"
        self.assertTrue(config_path.exists())
    
    def test_cli_exists(self):
        """测试CLI文件存在"""
        cli_path = Path(__file__).parent.parent / "cli.py"
        self.assertTrue(cli_path.exists())
    
    def test_scheduler_exists(self):
        """测试调度器存在"""
        scheduler_path = Path(__file__).parent.parent / "scheduler.py"
        self.assertTrue(scheduler_path.exists())


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Memory Suite v3.0 - 测试套件")
    print("=" * 60)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestCoreModules))
    suite.addTests(loader.loadTestsFromTestCase(TestAppModules))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationModules))
    suite.addTests(loader.loadTestsFromTestCase(TestSystem))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "=" * 60)
    print(f"测试完成: {result.testsRun} 个")
    print(f"通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
