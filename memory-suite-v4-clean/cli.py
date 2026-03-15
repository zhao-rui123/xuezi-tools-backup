#!/usr/bin/env python3
"""
Memory Suite v4.0 - 统一命令行入口
提供统一的CLI接口管理记忆系统
融合自我进化和知识管理功能
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('memory-suite')

# 路径配置
WORKSPACE = Path("/path/to/workspace")
MEMORY_DIR = WORKSPACE / "memory"
KNOWLEDGE_DIR = WORKSPACE / "knowledge-base"
CONFIG_DIR = Path(__file__).parent / "config"


def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    config_file = CONFIG_DIR / "config.json"
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
    return {
        "version": "4.0.0",
        "workspace": str(WORKSPACE),
        "memory_dir": str(MEMORY_DIR),
        "knowledge_dir": str(KNOWLEDGE_DIR),
        "modules": {}
    }


def save_config(config: Dict[str, Any]) -> bool:
    """保存配置文件"""
    config_file = CONFIG_DIR / "config.json"
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存配置失败: {e}")
        return False


class MemorySuiteCLI:
    """Memory Suite CLI 主类"""
    
    def __init__(self):
        self.config = load_config()
        self.ensure_directories()
    
    def ensure_directories(self):
        """确保必要目录存在"""
        dirs = [
            MEMORY_DIR,
            MEMORY_DIR / "snapshots",
            MEMORY_DIR / "archive",
            MEMORY_DIR / "permanent",
            MEMORY_DIR / "index",
            MEMORY_DIR / "summary",
            MEMORY_DIR / "evolution",
            KNOWLEDGE_DIR,
            KNOWLEDGE_DIR / "graph",
            KNOWLEDGE_DIR / "sync",
            CONFIG_DIR
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    # ============ 实时操作命令 ============
    
    def cmd_save(self, args) -> int:
        """立即保存会话"""
        logger.info("执行保存命令...")
        try:
            from core.real_time import RealTimeSaver
            manager = RealTimeSaver()
            result = manager.save()
            if result:
                print(f"✅ 会话已保存: {result}")
                return 0
            else:
                print("❌ 保存失败")
                return 1
        except Exception as e:
            logger.error(f"保存失败: {e}")
            print(f"❌ 保存失败: {e}")
            return 1
    
    def cmd_restore(self, args) -> int:
        """恢复会话"""
        logger.info("执行恢复命令...")
        try:
            from core.real_time import RealTimeSaver
            manager = RealTimeSaver()
            snapshot_id = args.snapshot if hasattr(args, 'snapshot') and args.snapshot else None
            result = manager.load()
            if result:
                print(f"✅ 会话已恢复")
                return 0
            else:
                print("❌ 恢复失败")
                return 1
        except Exception as e:
            logger.error(f"恢复失败: {e}")
            print(f"❌ 恢复失败: {e}")
            return 1
    
    def cmd_status(self, args) -> int:
        """查看状态"""
        logger.info("获取系统状态...")
        try:
            # 统计信息
            memory_files = list(MEMORY_DIR.glob("*.md"))
            snapshot_files = list((MEMORY_DIR / "snapshots").glob("*.json"))
            archive_files = list((MEMORY_DIR / "archive").glob("*"))
            knowledge_files = list(KNOWLEDGE_DIR.glob("**/*.md"))
            evolution_files = list((MEMORY_DIR / "evolution").glob("*.json"))
            
            print("=" * 50)
            print("🧠 Memory Suite v4.0 系统状态")
            print("=" * 50)
            print(f"\n📁 数据目录: {MEMORY_DIR}")
            print(f"📄 记忆文件: {len(memory_files)} 个")
            print(f"💾 会话快照: {len(snapshot_files)} 个")
            print(f"📦 归档文件: {len(archive_files)} 个")
            print(f"📚 知识条目: {len(knowledge_files)} 个")
            print(f"🧬 进化记录: {len(evolution_files)} 个")
            
            # 模块状态
            print(f"\n🔧 模块状态:")
            modules = self.config.get("modules", {})
            for name, settings in modules.items():
                status = "✅ 启用" if settings.get("enabled", False) else "❌ 禁用"
                print(f"   {name}: {status}")
            
            print("\n" + "=" * 50)
            return 0
        except Exception as e:
            logger.error(f"获取状态失败: {e}")
            print(f"❌ 获取状态失败: {e}")
            return 1
    
    # ============ 搜索查询命令 ============
    
    def cmd_search(self, args) -> int:
        """语义搜索"""
        query = args.query if hasattr(args, 'query') else None
        if not query:
            print("❌ 请提供搜索关键词")
            return 1
        
        logger.info(f"搜索: {query}")
        try:
            from core.indexer import IndexManager
            indexer = IndexManager()
            results = indexer.search(query, top_k=args.limit if hasattr(args, 'limit') else 10)
            
            if results:
                print(f"🔍 找到 {len(results)} 条结果:")
                for i, r in enumerate(results, 1):
                    print(f"\n{i}. {r.get('title', '未知')}")
                    print(f"   相关度: {r.get('score', 0):.3f}")
                    print(f"   {r.get('snippet', '')[:100]}...")
            else:
                print("🔍 未找到相关结果")
            return 0
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            print(f"❌ 搜索失败: {e}")
            return 1
    
    def cmd_qa(self, args) -> int:
        """智能问答"""
        question = args.question if hasattr(args, 'question') else None
        if not question:
            print("❌ 请提供问题")
            return 1
        
        logger.info(f"问答: {question}")
        try:
            from apps.qa import QASystem
            qa = QASystem()
            answer = qa.answer(question)
            print(f"\n❓ 问题: {question}")
            print(f"\n💡 回答:\n{answer}")
            return 0
        except Exception as e:
            logger.error(f"问答失败: {e}")
            print(f"❌ 问答失败: {e}")
            return 1
    
    # ============ 归档管理命令 ============
    
    def cmd_archive(self, args) -> int:
        """归档管理"""
        action = args.archive_action if hasattr(args, 'archive_action') else 'list'
        
        try:
            from core.archiver import Archiver
            manager = Archiver()
            
            if action == 'list':
                stats = manager.get_stats()
                print(f"📦 归档统计:")
                print(f"  已归档: {stats.get('archived', 0)} 个")
                print(f"  永久记录: {stats.get('permanent', 0)} 个")
                print(f"  已压缩: {stats.get('compressed', 0)} 个")
                return 0
            
            elif action == 'restore':
                print("⚠️ 恢复功能暂未实现")
                return 0
            
            elif action == 'clean':
                result = manager.clean_old_archives()
                print(f"✅ 清理完成，删除 {result} 个旧归档")
                return 0
            
            else:
                print(f"❌ 未知操作: {action}")
                return 1
                
        except Exception as e:
            logger.error(f"归档操作失败: {e}")
            print(f"❌ 归档操作失败: {e}")
            return 1
    
    # ============ 报告命令 ============
    
    def cmd_report(self, args) -> int:
        """生成报告"""
        report_type = args.report_type if hasattr(args, 'report_type') else 'daily'
        
        try:
            from core.analyzer import AnalysisManager
            analyzer = AnalysisManager()
            
            if report_type == 'daily':
                result = analyzer.generate_daily_report()
            elif report_type == 'weekly':
                result = analyzer.generate_weekly_report()
            elif report_type == 'monthly':
                result = analyzer.generate_monthly_report()
            else:
                print(f"❌ 未知报告类型: {report_type}")
                return 1
            
            if result:
                print(f"✅ {report_type}报告已生成: {result}")
                return 0
            else:
                print(f"❌ 报告生成失败")
                return 1
                
        except Exception as e:
            logger.error(f"生成报告失败: {e}")
            print(f"❌ 生成报告失败: {e}")
            return 1
    
    # ============ 自我进化命令 ============
    
    def cmd_evolution(self, args) -> int:
        """自我进化命令"""
        action = args.evolution_action if hasattr(args, 'evolution_action') else 'status'
        
        try:
            if action == 'daily':
                # 每日分析
                from apps.evolution.daily_analyzer import DailyAnalyzer
                analyzer = DailyAnalyzer()
                result = analyzer.analyze()
                if result:
                    print(f"✅ 每日分析完成")
                    print(f"   任务完成: {result.get('tasks_completed', 0)}")
                    print(f"   效率评分: {result.get('efficiency_score', 0)}")
                    print(f"   报告路径: {result.get('report_path', 'N/A')}")
                    return 0
                else:
                    print("❌ 每日分析失败")
                    return 1
            
            elif action == 'plan':
                # 长期规划
                from apps.evolution.long_term_planner import LongTermPlanner
                planner = LongTermPlanner()
                result = planner.generate_plan()
                if result:
                    print(f"✅ 长期规划已生成")
                    print(f"   规划周期: {result.get('period', 'N/A')}")
                    print(f"   目标数量: {result.get('goal_count', 0)}")
                    print(f"   报告路径: {result.get('plan_path', 'N/A')}")
                    return 0
                else:
                    print("❌ 长期规划生成失败")
                    return 1
            
            elif action == 'report':
                # 进化报告
                from apps.evolution.evolution_reporter import EvolutionReporter
                reporter = EvolutionReporter()
                result = reporter.generate_report()
                if result:
                    print(f"✅ 进化报告已生成")
                    print(f"   技能成长: {result.get('skill_growth', 0)} 项")
                    print(f"   改进建议: {result.get('suggestions_count', 0)} 条")
                    print(f"   报告路径: {result.get('report_path', 'N/A')}")
                    return 0
                else:
                    print("❌ 进化报告生成失败")
                    return 1
            
            elif action == 'skills':
                # 技能评估
                from apps.evolution.skill_evaluator import SkillEvaluator
                evaluator = SkillEvaluator()
                result = evaluator.evaluate()
                if result:
                    print(f"✅ 技能评估完成")
                    print(f"   评估技能: {result.get('skills_evaluated', 0)} 个")
                    print(f"   高频使用: {result.get('high_frequency', 0)} 个")
                    print(f"   报告路径: {result.get('report_path', 'N/A')}")
                    return 0
                else:
                    print("❌ 技能评估失败")
                    return 1
            
            elif action == 'status':
                # 查看进化状态
                evolution_dir = MEMORY_DIR / "evolution"
                if evolution_dir.exists():
                    daily_reports = list((evolution_dir / "daily").glob("*.json")) if (evolution_dir / "daily").exists() else []
                    monthly_reports = list((evolution_dir / "monthly").glob("*.json")) if (evolution_dir / "monthly").exists() else []
                    skill_reports = list((evolution_dir / "skills").glob("*.json")) if (evolution_dir / "skills").exists() else []
                    
                    print("🧬 自我进化状态:")
                    print(f"   每日分析报告: {len(daily_reports)} 份")
                    print(f"   月度进化报告: {len(monthly_reports)} 份")
                    print(f"   技能评估报告: {len(skill_reports)} 份")
                    
                    # 显示最新报告
                    if monthly_reports:
                        latest = max(monthly_reports, key=lambda p: p.stat().st_mtime)
                        mtime = datetime.fromtimestamp(latest.stat().st_mtime)
                        print(f"\n   最新月度报告: {latest.name}")
                        print(f"   生成时间: {mtime.strftime('%Y-%m-%d %H:%M')}")
                else:
                    print("🧬 暂无进化记录")
                return 0
            
            else:
                print(f"❌ 未知操作: {action}")
                return 1
                
        except ImportError as e:
            logger.warning(f"进化模块未完全实现: {e}")
            print(f"⚠️ 进化模块功能降级 - 基础统计:")
            # 降级显示基础统计
            memory_files = list(MEMORY_DIR.glob("*.md"))
            print(f"   记忆文件数: {len(memory_files)}")
            return 0
        except Exception as e:
            logger.error(f"进化操作失败: {e}")
            print(f"❌ 进化操作失败: {e}")
            return 1
    
    # ============ 知识管理命令 ============
    
    def cmd_knowledge(self, args) -> int:
        """知识管理命令"""
        action = args.knowledge_action if hasattr(args, 'knowledge_action') else 'list'
        
        try:
            if action == 'list':
                # 列出知识
                from knowledge.knowledge_manager import KnowledgeManager
                manager = KnowledgeManager()
                entries = manager.list_entries(
                    category=args.category if hasattr(args, 'category') else None,
                    tag=args.tag if hasattr(args, 'tag') else None,
                    limit=args.limit if hasattr(args, 'limit') else 20
                )
                
                if entries:
                    print(f"📚 知识条目 ({len(entries)} 条):")
                    print("-" * 60)
                    for i, entry in enumerate(entries, 1):
                        title = entry.get('title', '未命名')
                        category = entry.get('category', '未分类')
                        tags = entry.get('tags', [])
                        print(f"{i}. {title} [{category}]")
                        if tags:
                            print(f"   标签: {', '.join(tags)}")
                else:
                    print("📚 暂无知识条目")
                return 0
            
            elif action == 'search':
                # 搜索知识
                query = args.query if hasattr(args, 'query') else None
                if not query:
                    print("❌ 请提供搜索关键词")
                    return 1
                
                from knowledge.knowledge_search import KnowledgeSearch
                searcher = KnowledgeSearch()
                results = searcher.search(
                    query=query,
                    search_type=args.type if hasattr(args, 'type') else 'fulltext',
                    limit=args.limit if hasattr(args, 'limit') else 10
                )
                
                if results:
                    print(f"🔍 找到 {len(results)} 条知识:")
                    for i, r in enumerate(results, 1):
                        print(f"\n{i}. {r.get('title', '未知')}")
                        print(f"   相关度: {r.get('score', 0):.3f}")
                        print(f"   {r.get('snippet', '')[:150]}...")
                else:
                    print("🔍 未找到相关知识")
                return 0
            
            elif action == 'add':
                # 添加知识
                title = args.title if hasattr(args, 'title') else None
                if not title:
                    print("❌ 请提供知识标题")
                    return 1
                
                from knowledge.knowledge_manager import KnowledgeManager
                manager = KnowledgeManager()
                
                # 交互式输入内容
                print(f"请输入知识内容 (输入空行结束):")
                lines = []
                while True:
                    try:
                        line = input()
                        if not line:
                            break
                        lines.append(line)
                    except EOFError:
                        break
                
                content = '\n'.join(lines)
                if not content:
                    print("❌ 内容不能为空")
                    return 1
                
                result = manager.add_entry(
                    title=title,
                    content=content,
                    category=args.category if hasattr(args, 'category') else 'general',
                    tags=args.tags.split(',') if hasattr(args, 'tags') and args.tags else [],
                    source=args.source if hasattr(args, 'source') else 'cli'
                )
                
                if result:
                    print(f"✅ 知识已添加: {result.get('id', 'N/A')}")
                    return 0
                else:
                    print("❌ 添加失败")
                    return 1
            
            elif action == 'graph':
                # 知识图谱
                from knowledge.knowledge_graph import KnowledgeGraph
                graph = KnowledgeGraph()
                
                if hasattr(args, 'visualize') and args.visualize:
                    result = graph.visualize()
                    print(f"✅ 知识图谱可视化已生成")
                    print(f"   节点数: {result.get('nodes', 0)}")
                    print(f"   边数: {result.get('edges', 0)}")
                    print(f"   输出路径: {result.get('output_path', 'N/A')}")
                else:
                    result = graph.build()
                    print(f"✅ 知识图谱已构建")
                    print(f"   实体数: {result.get('entities', 0)}")
                    print(f"   关系数: {result.get('relations', 0)}")
                    print(f"   图谱路径: {result.get('graph_path', 'N/A')}")
                return 0
            
            elif action == 'sync':
                # 知识同步
                from knowledge.knowledge_sync import KnowledgeSync
                sync = KnowledgeSync()
                result = sync.sync_all(
                    direction=args.direction if hasattr(args, 'direction') else 'bidirectional'
                )
                
                if result:
                    print(f"✅ 知识同步完成")
                    print(f"   导出: {result.get('exported', 0)} 条")
                    print(f"   导入: {result.get('imported', 0)} 条")
                    print(f"   冲突: {result.get('conflicts', 0)} 条")
                    return 0
                else:
                    print("❌ 同步失败")
                    return 1
            
            elif action == 'show':
                # 显示知识详情
                entry_id = args.entry_id if hasattr(args, 'entry_id') else None
                if not entry_id:
                    print("❌ 请提供知识ID")
                    return 1
                
                from knowledge.knowledge_manager import KnowledgeManager
                manager = KnowledgeManager()
                entry = manager.get_entry(entry_id)
                
                if entry:
                    print(f"📖 {entry.get('title', '未命名')}")
                    print(f"   ID: {entry.get('id')}")
                    print(f"   分类: {entry.get('category', '未分类')}")
                    print(f"   标签: {', '.join(entry.get('tags', []))}")
                    print(f"   来源: {entry.get('source', '未知')}")
                    print(f"   创建: {entry.get('created_at', '未知')}")
                    print(f"   更新: {entry.get('updated_at', '未知')}")
                    print(f"\n{entry.get('content', '无内容')}")
                else:
                    print(f"❌ 知识条目不存在: {entry_id}")
                    return 1
                return 0
            
            else:
                print(f"❌ 未知操作: {action}")
                return 1
                
        except ImportError as e:
            logger.warning(f"知识模块未完全实现: {e}")
            print(f"⚠️ 知识模块功能降级")
            # 降级显示文件列表
            knowledge_files = list(KNOWLEDGE_DIR.glob("**/*.md"))
            print(f"   知识文件数: {len(knowledge_files)}")
            return 0
        except Exception as e:
            logger.error(f"知识操作失败: {e}")
            print(f"❌ 知识操作失败: {e}")
            return 1
    
    # ============ 配置命令 ============
    
    def cmd_config(self, args) -> int:
        """配置管理"""
        action = args.config_action if hasattr(args, 'config_action') else 'show'
        
        if action == 'show':
            print("🔧 当前配置:")
            print(json.dumps(self.config, ensure_ascii=False, indent=2))
            return 0
        
        elif action == 'set':
            key = args.key if hasattr(args, 'key') else None
            value = args.value if hasattr(args, 'value') else None
            
            if not key or value is None:
                print("❌ 请提供键和值")
                return 1
            
            # 解析值类型
            try:
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif '.' in value and value.replace('.', '').isdigit():
                    value = float(value)
            except:
                pass
            
            # 支持嵌套键 (如 modules.real_time.enabled)
            keys = key.split('.')
            target = self.config
            for k in keys[:-1]:
                if k not in target:
                    target[k] = {}
                target = target[k]
            target[keys[-1]] = value
            
            if save_config(self.config):
                print(f"✅ 配置已更新: {key} = {value}")
                return 0
            else:
                print(f"❌ 配置保存失败")
                return 1
        
        elif action == 'reset':
            self.config = {
                "version": "4.0.0",
                "workspace": str(WORKSPACE),
                "memory_dir": str(MEMORY_DIR),
                "knowledge_dir": str(KNOWLEDGE_DIR),
                "modules": {}
            }
            if save_config(self.config):
                print("✅ 配置已重置")
                return 0
            else:
                print("❌ 配置重置失败")
                return 1
        
        else:
            print(f"❌ 未知操作: {action}")
            return 1
    
    # ============ 系统命令 ============
    
    def cmd_doctor(self, args) -> int:
        """系统诊断"""
        logger.info("运行系统诊断...")
        try:
            from doctor import Doctor
            doc = Doctor()
            results = doc.run_check()
            
            print("=" * 50)
            print("🏥 Memory Suite 系统诊断")
            print("=" * 50)
            
            issues = 0
            for check in results:
                status = "✅" if check['ok'] else "❌"
                print(f"{status} {check['name']}: {check['message']}")
                if not check['ok']:
                    issues += 1
            
            print("\n" + "=" * 50)
            if issues == 0:
                print("🎉 所有检查通过！系统健康")
                return 0
            else:
                print(f"⚠️ 发现 {issues} 个问题")
                return 1
                
        except Exception as e:
            logger.error(f"诊断失败: {e}")
            print(f"❌ 诊断失败: {e}")
            return 1
    
    def cmd_scheduler(self, args) -> int:
        """调度器命令"""
        action = args.scheduler_action if hasattr(args, 'scheduler_action') else 'list'
        
        try:
            from scheduler import Scheduler
            sched = Scheduler()
            
            if action == 'list':
                tasks = sched.list_tasks()
                print("📋 定时任务列表:")
                for task in tasks:
                    status = "✅" if task['enabled'] else "❌"
                    print(f"{status} {task['name']}: {task['description']}")
                return 0
            
            elif action == 'run':
                task_name = args.task_name if hasattr(args, 'task_name') else None
                if not task_name:
                    print("❌ 请指定任务名称")
                    return 1
                result = sched.run_task(task_name)
                if result:
                    print(f"✅ 任务执行完成: {task_name}")
                    return 0
                else:
                    print(f"❌ 任务执行失败: {task_name}")
                    return 1
            
            else:
                print(f"❌ 未知操作: {action}")
                return 1
                
        except Exception as e:
            logger.error(f"调度器操作失败: {e}")
            print(f"❌ 调度器操作失败: {e}")
            return 1


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        prog='memory-suite',
        description='Memory Suite v4.0 - 统一记忆管理系统（融合自我进化与知识管理）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 实时操作
  memory-suite save                    # 立即保存会话
  memory-suite restore                 # 恢复会话
  memory-suite status                  # 查看系统状态

  # 搜索查询
  memory-suite search "关键词"         # 语义搜索
  memory-suite qa "问题"               # 智能问答

  # 归档管理
  memory-suite archive list            # 列出归档
  memory-suite archive clean           # 清理旧归档

  # 报告生成
  memory-suite report daily            # 日报
  memory-suite report weekly           # 周报
  memory-suite report monthly          # 月报

  # 自我进化 (新增)
  memory-suite evolution daily         # 每日分析
  memory-suite evolution plan          # 长期规划
  memory-suite evolution report        # 进化报告
  memory-suite evolution skills        # 技能评估
  memory-suite evolution status        # 进化状态

  # 知识管理 (新增)
  memory-suite knowledge list          # 列出知识条目
  memory-suite knowledge search "query" # 搜索知识
  memory-suite knowledge add "标题"    # 添加知识
  memory-suite knowledge graph         # 构建知识图谱
  memory-suite knowledge sync          # 同步知识库

  # 系统管理
  memory-suite doctor                  # 系统诊断
  memory-suite scheduler list          # 列出定时任务
  memory-suite scheduler run real-time # 运行定时任务
  memory-suite config show             # 显示配置
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # ============ 实时操作子命令 ============
    
    # save
    save_parser = subparsers.add_parser('save', help='立即保存会话')
    
    # restore
    restore_parser = subparsers.add_parser('restore', help='恢复会话')
    restore_parser.add_argument('--snapshot', '-s', help='指定快照ID')
    
    # status
    status_parser = subparsers.add_parser('status', help='查看系统状态')
    
    # ============ 搜索查询子命令 ============
    
    # search
    search_parser = subparsers.add_parser('search', help='语义搜索')
    search_parser.add_argument('query', help='搜索关键词')
    search_parser.add_argument('--limit', '-l', type=int, default=10, help='结果数量限制')
    
    # qa
    qa_parser = subparsers.add_parser('qa', help='智能问答')
    qa_parser.add_argument('question', help='问题内容')
    
    # ============ 归档管理子命令 ============
    
    # archive
    archive_parser = subparsers.add_parser('archive', help='归档管理')
    archive_subparsers = archive_parser.add_subparsers(dest='archive_action')
    archive_subparsers.add_parser('list', help='列出归档')
    archive_restore = archive_subparsers.add_parser('restore', help='恢复归档')
    archive_restore.add_argument('date', help='归档日期')
    archive_subparsers.add_parser('clean', help='清理旧归档')
    
    # ============ 报告子命令 ============
    
    # report
    report_parser = subparsers.add_parser('report', help='生成报告')
    report_parser.add_argument('report_type', choices=['daily', 'weekly', 'monthly'], 
                               default='daily', help='报告类型')
    
    # ============ 自我进化子命令 (新增) ============
    
    # evolution
    evolution_parser = subparsers.add_parser('evolution', help='自我进化')
    evolution_subparsers = evolution_parser.add_subparsers(dest='evolution_action')
    evolution_subparsers.add_parser('daily', help='每日分析')
    evolution_subparsers.add_parser('plan', help='长期规划')
    evolution_subparsers.add_parser('report', help='进化报告')
    evolution_subparsers.add_parser('skills', help='技能评估')
    evolution_subparsers.add_parser('status', help='进化状态')
    
    # ============ 知识管理子命令 (新增) ============
    
    # knowledge
    knowledge_parser = subparsers.add_parser('knowledge', help='知识管理')
    knowledge_subparsers = knowledge_parser.add_subparsers(dest='knowledge_action')
    
    # knowledge list
    knowledge_list = knowledge_subparsers.add_parser('list', help='列出知识条目')
    knowledge_list.add_argument('--category', '-c', help='按分类筛选')
    knowledge_list.add_argument('--tag', '-t', help='按标签筛选')
    knowledge_list.add_argument('--limit', '-l', type=int, default=20, help='数量限制')
    
    # knowledge search
    knowledge_search = knowledge_subparsers.add_parser('search', help='搜索知识')
    knowledge_search.add_argument('query', help='搜索关键词')
    knowledge_search.add_argument('--type', choices=['fulltext', 'semantic'], 
                                   default='fulltext', help='搜索类型')
    knowledge_search.add_argument('--limit', '-l', type=int, default=10, help='结果数量')
    
    # knowledge add
    knowledge_add = knowledge_subparsers.add_parser('add', help='添加知识条目')
    knowledge_add.add_argument('title', help='知识标题')
    knowledge_add.add_argument('--category', '-c', default='general', help='分类')
    knowledge_add.add_argument('--tags', help='标签（逗号分隔）')
    knowledge_add.add_argument('--source', '-s', help='来源')
    
    # knowledge graph
    knowledge_graph = knowledge_subparsers.add_parser('graph', help='知识图谱')
    knowledge_graph.add_argument('--visualize', '-v', action='store_true', help='生成可视化')
    
    # knowledge sync
    knowledge_sync = knowledge_subparsers.add_parser('sync', help='同步知识库')
    knowledge_sync.add_argument('--direction', choices=['export', 'import', 'bidirectional'],
                                 default='bidirectional', help='同步方向')
    
    # knowledge show
    knowledge_show = knowledge_subparsers.add_parser('show', help='显示知识详情')
    knowledge_show.add_argument('entry_id', help='知识条目ID')
    
    # ============ 配置子命令 ============
    
    # config
    config_parser = subparsers.add_parser('config', help='配置管理')
    config_subparsers = config_parser.add_subparsers(dest='config_action')
    config_subparsers.add_parser('show', help='显示配置')
    config_set = config_subparsers.add_parser('set', help='设置配置')
    config_set.add_argument('key', help='配置键')
    config_set.add_argument('value', help='配置值')
    config_subparsers.add_parser('reset', help='重置配置')
    
    # ============ 系统子命令 ============
    
    # doctor
    doctor_parser = subparsers.add_parser('doctor', help='系统诊断')
    
    # scheduler
    scheduler_parser = subparsers.add_parser('scheduler', help='调度器')
    scheduler_subparsers = scheduler_parser.add_subparsers(dest='scheduler_action')
    scheduler_subparsers.add_parser('list', help='列出任务')
    scheduler_run = scheduler_subparsers.add_parser('run', help='运行任务')
    scheduler_run.add_argument('task_name', help='任务名称')
    
    # 解析参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # 执行命令
    cli = MemorySuiteCLI()
    
    command_map = {
        'save': cli.cmd_save,
        'restore': cli.cmd_restore,
        'status': cli.cmd_status,
        'search': cli.cmd_search,
        'qa': cli.cmd_qa,
        'archive': cli.cmd_archive,
        'report': cli.cmd_report,
        'evolution': cli.cmd_evolution,
        'knowledge': cli.cmd_knowledge,
        'config': cli.cmd_config,
        'doctor': cli.cmd_doctor,
        'scheduler': cli.cmd_scheduler,
    }
    
    handler = command_map.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"❌ 未知命令: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
