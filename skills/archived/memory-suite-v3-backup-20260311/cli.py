#!/usr/bin/env python3
"""
Memory Suite v3.0 - 统一命令行入口
提供统一的CLI接口管理记忆系统
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
WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
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
        "version": "3.0.0",
        "workspace": str(WORKSPACE),
        "memory_dir": str(MEMORY_DIR),
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
            
            print("=" * 50)
            print("🧠 Memory Suite v3.0 系统状态")
            print("=" * 50)
            print(f"\n📁 数据目录: {MEMORY_DIR}")
            print(f"📄 记忆文件: {len(memory_files)} 个")
            print(f"💾 会话快照: {len(snapshot_files)} 个")
            print(f"📦 归档文件: {len(archive_files)} 个")
            
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
                "version": "3.0.0",
                "workspace": str(WORKSPACE),
                "memory_dir": str(MEMORY_DIR),
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
        description='Memory Suite v3.0 - 统一记忆管理系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  memory-suite save                    # 立即保存会话
  memory-suite restore                 # 恢复会话
  memory-suite status                  # 查看系统状态
  memory-suite search "关键词"         # 语义搜索
  memory-suite qa "问题"               # 智能问答
  memory-suite archive list            # 列出归档
  memory-suite report daily            # 生成日报
  memory-suite doctor                  # 系统诊断
  memory-suite scheduler run real-time # 运行定时任务
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
