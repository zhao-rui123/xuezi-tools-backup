#!/usr/bin/env python3
"""
Memory Suite v4.0 - 定时任务调度器
统一调度所有记忆系统任务
扩展支持自我进化和知识管理任务
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('memory-scheduler')

# 路径配置
WORKSPACE = Path("/home/user/workspace")
MEMORY_DIR = WORKSPACE / "memory"
KNOWLEDGE_DIR = WORKSPACE / "knowledge-base"
CONFIG_DIR = Path(__file__).parent / "config"


class Task:
    """任务定义类"""
    
    def __init__(self, name: str, description: str, handler: Callable, enabled: bool = True):
        self.name = name
        self.description = description
        self.handler = handler
        self.enabled = enabled
        self.last_run = None
        self.last_result = None
    
    def run(self, **kwargs) -> bool:
        """执行任务"""
        logger.info(f"开始执行任务：{self.name}")
        self.last_run = datetime.now().isoformat()
        try:
            result = self.handler(**kwargs)
            self.last_result = {"success": True, "result": result}
            logger.info(f"任务完成：{self.name}")
            return True
        except Exception as e:
            self.last_result = {"success": False, "error": str(e)}
            logger.error(f"任务失败：{self.name} - {e}")
            # 发送错误通知
            self._notify_error(e)
            return False
    
    def _notify_error(self, error):
        """发送错误通知 - 修复命令注入漏洞"""
        try:
            notify_script = Path(__file__).parent / "scripts" / "error_notifier.py"
            if notify_script.exists():
                import subprocess
                import sys
                script_path = str(notify_script)
                error_task_name = str(self.name)
                error_msg = str(error)
                subprocess.run(
                    [sys.executable, script_path, error_task_name, error_msg],
                    capture_output=True,
                    timeout=30
                )
        except Exception:
            pass  # 通知失败不影响主任务
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "last_run": self.last_run,
            "last_result": self.last_result
        }


class Scheduler:
    """任务调度器主类"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.config = self._load_config()
        self._register_default_tasks()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载调度器配置"""
        config_file = CONFIG_DIR / "scheduler.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载调度器配置失败：{e}")
        return {"tasks": {}}
    
    def _save_config(self):
        """保存调度器配置"""
        config_file = CONFIG_DIR / "scheduler.json"
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            # 更新任务状态
            self.config["tasks"] = {
                name: {
                    "enabled": task.enabled,
                    "last_run": task.last_run,
                    "last_result": task.last_result
                }
                for name, task in self.tasks.items()
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存调度器配置失败：{e}")
    
    def _register_default_tasks(self):
        """注册默认任务"""
        # 核心任务 - 实时保存
        self.register_task(Task(
            name="real-time",
            description="实时保存会话快照",
            handler=self._task_real_time,
            enabled=self._is_task_enabled("real-time", True)
        ))
        
        # 核心任务 - 归档
        self.register_task(Task(
            name="archive",
            description="归档旧记忆文件",
            handler=self._task_archive,
            enabled=self._is_task_enabled("archive", True)
        ))
        
        # 核心任务 - 索引
        self.register_task(Task(
            name="index",
            description="更新语义索引",
            handler=self._task_index,
            enabled=self._is_task_enabled("index", True)
        ))
        
        # 核心任务 - 分析
        self.register_task(Task(
            name="analyze-daily",
            description="运行每日记忆分析",
            handler=self._task_analyze_daily,
            enabled=self._is_task_enabled("analyze-daily", True)
        ))
        
        # 自我进化任务 - 每日分析
        self.register_task(Task(
            name="evolution-daily",
            description="每日工作分析",
            handler=self._task_evolution_daily,
            enabled=self._is_task_enabled("evolution-daily", True)
        ))
        
        # 自我进化任务 - 月度规划
        self.register_task(Task(
            name="evolution-monthly",
            description="月度长期规划",
            handler=self._task_evolution_monthly,
            enabled=self._is_task_enabled("evolution-monthly", True)
        ))
        
        # 自我进化任务 - 进化报告
        self.register_task(Task(
            name="evolution-report",
            description="生成月度进化报告",
            handler=self._task_evolution_report,
            enabled=self._is_task_enabled("evolution-report", True)
        ))
        
        # 自我进化任务 - 技能评估
        self.register_task(Task(
            name="skill-eval",
            description="技能包使用评估",
            handler=self._task_skill_eval,
            enabled=self._is_task_enabled("skill-eval", True)
        ))
        
        # 知识管理任务 - 知识图谱
        self.register_task(Task(
            name="knowledge-graph",
            description="构建知识图谱",
            handler=self._task_knowledge_graph,
            enabled=self._is_task_enabled("knowledge-graph", True)
        ))
        
        # 知识管理任务 - 知识同步
        self.register_task(Task(
            name="knowledge-sync",
            description="同步知识库",
            handler=self._task_knowledge_sync,
            enabled=self._is_task_enabled("knowledge-sync", True)
        ))
        
        # 知识管理任务 - 知识导入
        self.register_task(Task(
            name="knowledge-import",
            description="从记忆导入知识",
            handler=self._task_knowledge_import,
            enabled=self._is_task_enabled("knowledge-import", True)
        ))
    
    def _is_task_enabled(self, task_name: str, default: bool = True) -> bool:
        """检查任务是否启用"""
        task_config = self.config.get("tasks", {}).get(task_name, {})
        return task_config.get("enabled", default)
    
    # ============ 核心任务处理器 ============
    
    def _task_real_time(self, **kwargs) -> Any:
        """实时保存任务"""
        logger.info("执行实时保存任务...")
        try:
            from core.real_time import RealTimeSaver
            manager = RealTimeSaver()
            result = manager.save()
            if result:
                logger.info(f"实时保存完成：{result}")
                return {"snapshot_path": str(result)}
            else:
                raise Exception("保存返回空结果")
        except ImportError as e:
            logger.warning(f"RealTimeSaver 错误：{e}")
            # 降级处理：简单保存当前会话信息
            snapshot_dir = MEMORY_DIR / "snapshots"
            snapshot_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_file = snapshot_dir / f"snapshot_{timestamp}.json"
            
            snapshot_data = {
                "timestamp": timestamp,
                "created_at": datetime.now().isoformat(),
                "type": "real-time",
                "status": "ok"
            }
            
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"基础快照已保存：{snapshot_file}")
            return {"snapshot_path": str(snapshot_file)}
    
    def _task_archive(self, **kwargs) -> Any:
        """归档任务"""
        logger.info("执行归档任务...")
        try:
            from core.archiver import ArchiveManager
            manager = ArchiveManager()
            result = manager.run_archive_cycle()
            logger.info(f"归档完成：{result}")
            return result
        except ImportError as e:
            logger.warning(f"ArchiveManager 未实现：{e}")
            return {"status": "degraded", "message": "使用降级模式"}
    
    def _task_index(self, **kwargs) -> Any:
        """索引任务"""
        logger.info("执行索引任务...")
        try:
            from core.indexer import IndexManager
            manager = IndexManager()
            result = manager.update_index()
            logger.info(f"索引更新完成：{result}")
            return result
        except ImportError as e:
            logger.warning(f"IndexManager 未实现：{e}")
            # 降级处理
            index_dir = MEMORY_DIR / "index"
            index_dir.mkdir(parents=True, exist_ok=True)
            
            memory_files = list(MEMORY_DIR.glob("*.md"))
            index_data = {
                "updated_at": datetime.now().isoformat(),
                "total_files": len(memory_files),
                "files": [f.name for f in memory_files[:100]]
            }
            
            index_file = index_dir / "file_index.json"
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"基础索引已更新：{index_file}")
            return {"indexed_files": len(memory_files)}
    
    def _task_analyze_daily(self, **kwargs) -> Any:
        """每日分析任务"""
        logger.info("执行每日分析任务...")
        try:
            from core.analyzer import AnalysisManager
            manager = AnalysisManager()
            result = manager.generate_daily_report()
            logger.info(f"每日分析完成：{result}")
            return result
        except ImportError as e:
            logger.warning(f"AnalysisManager 未实现：{e}")
            return {"status": "degraded", "message": "使用降级模式"}
    
    # ============ 自我进化任务处理器 ============
    
    def _task_evolution_daily(self, **kwargs) -> Any:
        """每日进化分析任务"""
        logger.info("执行每日进化分析任务...")
        try:
            from apps.evolution.daily_analyzer import DailyAnalyzer
            analyzer = DailyAnalyzer()
            result = analyzer.analyze()
            if result:
                logger.info(f"每日进化分析完成")
                return {
                    "tasks_completed": result.get('tasks_completed', 0),
                    "efficiency_score": result.get('efficiency_score', 0),
                    "report_path": str(result.get('report_path', ''))
                }
            else:
                return {"status": "no_data"}
        except ImportError as e:
            logger.warning(f"DailyAnalyzer 未实现：{e}")
            return {"status": "degraded", "message": "模块未实现"}
        except Exception as e:
            logger.error(f"每日进化分析失败：{e}")
            return {"status": "error", "error": str(e)}
    
    def _task_evolution_monthly(self, **kwargs) -> Any:
        """月度长期规划任务"""
        logger.info("执行月度长期规划任务...")
        try:
            from apps.evolution.long_term_planner import LongTermPlanner
            planner = LongTermPlanner()
            result = planner.generate_plan()
            if result:
                logger.info(f"月度长期规划完成")
                return {
                    "period": result.get('period', 'monthly'),
                    "goal_count": result.get('goal_count', 0),
                    "plan_path": str(result.get('plan_path', ''))
                }
            else:
                return {"status": "no_data"}
        except ImportError as e:
            logger.warning(f"LongTermPlanner 未实现：{e}")
            return {"status": "degraded", "message": "模块未实现"}
        except Exception as e:
            logger.error(f"月度长期规划失败：{e}")
            return {"status": "error", "error": str(e)}
    
    def _task_evolution_report(self, **kwargs) -> Any:
        """进化报告生成任务"""
        logger.info("执行进化报告生成任务...")
        try:
            from apps.evolution.evolution_reporter import EvolutionReporter
            reporter = EvolutionReporter()
            result = reporter.generate_report()
            if result:
                logger.info(f"进化报告生成完成")
                return {
                    "skill_growth": result.get('skill_growth', 0),
                    "suggestions_count": result.get('suggestions_count', 0),
                    "report_path": str(result.get('report_path', ''))
                }
            else:
                return {"status": "no_data"}
        except ImportError as e:
            logger.warning(f"EvolutionReporter 未实现：{e}")
            return {"status": "degraded", "message": "模块未实现"}
        except Exception as e:
            logger.error(f"进化报告生成失败：{e}")
            return {"status": "error", "error": str(e)}
    
    def _task_skill_eval(self, **kwargs) -> Any:
        """技能评估任务"""
        logger.info("执行技能评估任务...")
        try:
            from apps.evolution.skill_evaluator import SkillEvaluator
            evaluator = SkillEvaluator()
            result = evaluator.evaluate()
            if result:
                logger.info(f"技能评估完成")
                return {
                    "skills_evaluated": result.get('skills_evaluated', 0),
                    "high_frequency": result.get('high_frequency', 0),
                    "report_path": str(result.get('report_path', ''))
                }
            else:
                return {"status": "no_data"}
        except ImportError as e:
            logger.warning(f"SkillEvaluator 未实现：{e}")
            return {"status": "degraded", "message": "模块未实现"}
        except Exception as e:
            logger.error(f"技能评估失败：{e}")
            return {"status": "error", "error": str(e)}
    
    # ============ 知识管理任务处理器 ============
    
    def _task_knowledge_graph(self, **kwargs) -> Any:
        """知识图谱构建任务"""
        logger.info("执行知识图谱构建任务...")
        try:
            from knowledge.knowledge_graph import KnowledgeGraph
            graph = KnowledgeGraph()
            result = graph.build()
            if result:
                logger.info(f"知识图谱构建完成")
                return {
                    "entities": result.get('entities', 0),
                    "relations": result.get('relations', 0),
                    "graph_path": str(result.get('graph_path', ''))
                }
            else:
                return {"status": "no_data"}
        except ImportError as e:
            logger.warning(f"KnowledgeGraph 未实现：{e}")
            return {"status": "degraded", "message": "模块未实现"}
        except Exception as e:
            logger.error(f"知识图谱构建失败：{e}")
            return {"status": "error", "error": str(e)}
    
    def _task_knowledge_sync(self, **kwargs) -> Any:
        """知识同步任务"""
        logger.info("执行知识同步任务...")
        try:
            from knowledge.knowledge_sync import KnowledgeSync
            sync = KnowledgeSync()
            result = sync.sync_all()
            if result:
                logger.info(f"知识同步完成")
                return {
                    "exported": result.get('exported', 0),
                    "imported": result.get('imported', 0),
                    "conflicts": result.get('conflicts', 0)
                }
            else:
                return {"status": "no_data"}
        except ImportError as e:
            logger.warning(f"KnowledgeSync 未实现：{e}")
            return {"status": "degraded", "message": "模块未实现"}
        except Exception as e:
            logger.error(f"知识同步失败：{e}")
            return {"status": "error", "error": str(e)}
    
    def _task_knowledge_import(self, **kwargs) -> Any:
        """知识导入任务"""
        logger.info("执行知识导入任务...")
        try:
            from knowledge.knowledge_importer import KnowledgeImporter
            importer = KnowledgeImporter()
            result = importer.import_from_memory()
            if result:
                logger.info(f"知识导入完成")
                return {
                    "imported": result.get('imported', 0),
                    "duplicates": result.get('duplicates', 0),
                    "skipped": result.get('skipped', 0)
                }
            else:
                return {"status": "no_data"}
        except ImportError as e:
            logger.warning(f"KnowledgeImporter 未实现：{e}")
            return {"status": "degraded", "message": "模块未实现"}
        except Exception as e:
            logger.error(f"知识导入失败：{e}")
            return {"status": "error", "error": str(e)}
    
    # ============ 公共接口 ============
    
    def register_task(self, task: Task):
        """注册任务"""
        self.tasks[task.name] = task
        logger.debug(f"注册任务：{task.name}")
    
    def unregister_task(self, task_name: str) -> bool:
        """注销任务"""
        if task_name in self.tasks:
            del self.tasks[task_name]
            logger.debug(f"注销任务：{task_name}")
            return True
        return False
    
    def list_tasks(self) -> List[Dict[str, Any]]:
        """列出所有任务"""
        return [task.to_dict() for task in self.tasks.values()]
    
    def get_task(self, task_name: str) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_name)
    
    def run_task(self, task_name: str, **kwargs) -> bool:
        """运行指定任务"""
        task = self.tasks.get(task_name)
        if not task:
            logger.error(f"任务不存在：{task_name}")
            return False
        
        if not task.enabled:
            logger.warning(f"任务已禁用：{task_name}")
            return False
        
        result = task.run(**kwargs)
        self._save_config()
        return result
    
    def run_all(self) -> Dict[str, bool]:
        """运行所有启用的任务"""
        results = {}
        for name, task in self.tasks.items():
            if task.enabled:
                results[name] = task.run()
            else:
                results[name] = None
        self._save_config()
        return results
    
    def enable_task(self, task_name: str) -> bool:
        """启用任务"""
        task = self.tasks.get(task_name)
        if task:
            task.enabled = True
            self._save_config()
            logger.info(f"任务已启用：{task_name}")
            return True
        return False
    
    def disable_task(self, task_name: str) -> bool:
        """禁用任务"""
        task = self.tasks.get(task_name)
        if task:
            task.enabled = False
            self._save_config()
            logger.info(f"任务已禁用：{task_name}")
            return True
        return False


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        prog='memory-scheduler',
        description='Memory Suite v4.0 - 定时任务调度器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  scheduler list                       # 列出所有任务
  scheduler run real-time              # 运行实时保存任务
  scheduler run archive                # 运行归档任务
  scheduler run index                  # 运行索引任务
  scheduler run analyze-daily          # 运行每日分析
  scheduler run evolution-daily        # 运行每日进化分析
  scheduler run evolution-monthly      # 运行月度规划
  scheduler run evolution-report       # 运行进化报告
  scheduler run skill-eval             # 运行技能评估
  scheduler run knowledge-graph        # 运行知识图谱构建
  scheduler run knowledge-sync         # 运行知识同步
  scheduler run knowledge-import       # 运行知识导入
  scheduler run-all                    # 运行所有任务
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # list
    list_parser = subparsers.add_parser('list', help='列出所有任务')
    
    # run
    run_parser = subparsers.add_parser('run', help='运行指定任务')
    run_parser.add_argument('task_name', help='任务名称')
    run_parser.add_argument('--type', '-t', help='分析类型 (daily/weekly/monthly)', default='monthly')
    
    # run-all
    run_all_parser = subparsers.add_parser('run-all', help='运行所有任务')
    
    # enable
    enable_parser = subparsers.add_parser('enable', help='启用任务')
    enable_parser.add_argument('task_name', help='任务名称')
    
    # disable
    disable_parser = subparsers.add_parser('disable', help='禁用任务')
    disable_parser.add_argument('task_name', help='任务名称')
    
    # 解析参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # 执行命令
    scheduler = Scheduler()
    
    if args.command == 'list':
        tasks = scheduler.list_tasks()
        print("📋 定时任务列表:")
        print("-" * 60)
        for task in tasks:
            status = "✅ 启用" if task['enabled'] else "❌ 禁用"
            last_run = task.get('last_run') or "从未"
            print(f"\n{task['name']} [{status}]")
            print(f"   描述：{task['description']}")
            print(f"   上次运行：{last_run}")
            if task.get('last_result'):
                success = task['last_result'].get('success', False)
                result_status = "✅ 成功" if success else "❌ 失败"
                print(f"   上次结果：{result_status}")
        return 0
    
    elif args.command == 'run':
        kwargs = {}
        if hasattr(args, 'type'):
            kwargs['type'] = args.type
        result = scheduler.run_task(args.task_name, **kwargs)
        return 0 if result else 1
    
    elif args.command == 'run-all':
        results = scheduler.run_all()
        print("📋 任务执行结果:")
        print("-" * 40)
        for name, result in results.items():
            if result is None:
                status = "⏭️ 跳过 (禁用)"
            elif result:
                status = "✅ 成功"
            else:
                status = "❌ 失败"
            print(f"  {name}: {status}")
        return 0
    
    elif args.command == 'enable':
        if scheduler.enable_task(args.task_name):
            print(f"✅ 任务已启用：{args.task_name}")
            return 0
        else:
            print(f"❌ 任务不存在：{args.task_name}")
            return 1
    
    elif args.command == 'disable':
        if scheduler.disable_task(args.task_name):
            print(f"✅ 任务已禁用：{args.task_name}")
            return 0
        else:
            print(f"❌ 任务不存在：{args.task_name}")
            return 1
    
    else:
        print(f"❌ 未知命令：{args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
