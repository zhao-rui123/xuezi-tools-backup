#!/usr/bin/env python3
"""
Memory Suite v4.0 - 测试套件
"""

import unittest
import json
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCLI(unittest.TestCase):
    """CLI 测试"""
    
    def test_cli_import(self):
        """测试 CLI 导入"""
        try:
            from cli import MemorySuiteCLI
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"CLI 导入失败：{e}")
    
    def test_config_load(self):
        """测试配置加载"""
        from cli import load_config
        config = load_config()
        self.assertIn("version", config)
        self.assertEqual(config["version"], "4.0.0")


class TestScheduler(unittest.TestCase):
    """调度器测试"""
    
    def test_scheduler_import(self):
        """测试调度器导入"""
        try:
            from scheduler import Scheduler
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"调度器导入失败：{e}")
    
    def test_task_registration(self):
        """测试任务注册"""
        from scheduler import Scheduler
        scheduler = Scheduler()
        tasks = scheduler.list_tasks()
        self.assertGreater(len(tasks), 0)


class TestEvolution(unittest.TestCase):
    """自我进化模块测试"""
    
    def test_daily_analyzer(self):
        """测试每日分析器"""
        from apps.evolution.daily_analyzer import DailyAnalyzer
        analyzer = DailyAnalyzer()
        self.assertIsNotNone(analyzer)
    
    def test_long_term_planner(self):
        """测试长期规划器"""
        from apps.evolution.long_term_planner import LongTermPlanner
        planner = LongTermPlanner()
        self.assertIsNotNone(planner)
    
    def test_evolution_reporter(self):
        """测试进化报告器"""
        from apps.evolution.evolution_reporter import EvolutionReporter
        reporter = EvolutionReporter()
        self.assertIsNotNone(reporter)
    
    def test_skill_evaluator(self):
        """测试技能评估器"""
        from apps.evolution.skill_evaluator import SkillEvaluator
        evaluator = SkillEvaluator()
        self.assertIsNotNone(evaluator)


class TestKnowledge(unittest.TestCase):
    """知识管理模块测试"""
    
    def test_knowledge_manager(self):
        """测试知识管理器"""
        from knowledge.knowledge_manager import KnowledgeManager
        manager = KnowledgeManager()
        self.assertIsNotNone(manager)
    
    def test_knowledge_graph(self):
        """测试知识图谱"""
        from knowledge.knowledge_graph import KnowledgeGraph
        graph = KnowledgeGraph()
        self.assertIsNotNone(graph)
    
    def test_knowledge_search(self):
        """测试知识搜索"""
        from knowledge.knowledge_search import KnowledgeSearch
        searcher = KnowledgeSearch()
        self.assertIsNotNone(searcher)
    
    def test_knowledge_importer(self):
        """测试知识导入器"""
        from knowledge.knowledge_importer import KnowledgeImporter
        importer = KnowledgeImporter()
        self.assertIsNotNone(importer)
    
    def test_knowledge_sync(self):
        """测试知识同步器"""
        from knowledge.knowledge_sync import KnowledgeSync
        sync = KnowledgeSync()
        self.assertIsNotNone(sync)


class TestCore(unittest.TestCase):
    """核心模块测试"""
    
    def test_real_time_saver(self):
        """测试实时保存器"""
        from core.real_time import RealTimeSaver
        saver = RealTimeSaver()
        self.assertIsNotNone(saver)
    
    def test_archiver(self):
        """测试归档器"""
        from core.archiver import Archiver
        archiver = Archiver()
        self.assertIsNotNone(archiver)
    
    def test_indexer(self):
        """测试索引器"""
        from core.indexer import IndexManager
        indexer = IndexManager()
        self.assertIsNotNone(indexer)
    
    def test_analyzer(self):
        """测试分析器"""
        from core.analyzer import AnalysisManager
        analyzer = AnalysisManager()
        self.assertIsNotNone(analyzer)


class TestDoctor(unittest.TestCase):
    """诊断工具测试"""
    
    def test_doctor_run(self):
        """测试诊断运行"""
        from doctor import Doctor
        doc = Doctor()
        results = doc.run_check()
        self.assertIsInstance(results, list)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestCLI))
    suite.addTests(loader.loadTestsFromTestCase(TestScheduler))
    suite.addTests(loader.loadTestsFromTestCase(TestEvolution))
    suite.addTests(loader.loadTestsFromTestCase(TestKnowledge))
    suite.addTests(loader.loadTestsFromTestCase(TestCore))
    suite.addTests(loader.loadTestsFromTestCase(TestDoctor))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
