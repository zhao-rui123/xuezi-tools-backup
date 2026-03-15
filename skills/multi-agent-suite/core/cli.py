"""
Multi-Agent Suite 统一入口
提供简洁的命令行接口

使用方法:
    python -m core.cli --help
    python -m core.cli agent list
    python -m core.cli task create "项目名称"
    python -m core.cli web
"""

import sys
import subprocess
from pathlib import Path

SUITE_DIR = Path(__file__).parent.parent

def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("""
🤖 Multi-Agent Suite v3.2
=========================

使用方法:
  python -m core.cli <command> [options]

命令:
  agent          Agent 管理
  task           任务管理
  web            启动Web界面
  status         系统状态
  version        显示版本
  help           显示帮助

快速示例:
  python -m core.cli agent list
  python -m core.cli task create "新项目"
  python -m core.cli task list
  python -m core.cli web
  python -m core.cli status
        """)
        return

    command = sys.argv[1]

    if command in ['help', '--help', '-h']:
        print("""
🤖 Multi-Agent Suite v3.3 - 帮助
====================================

命令列表:

  agent <action>      Agent 管理
    list              列出所有Agent
    stats             Agent统计信息
    <agent-id>        查看指定Agent详情

  task <action>       任务管理
    create <name>     创建新任务
    list              列出所有任务
    status <id>       查看任务状态
    progress <id>     推进任务

  web                 启动Web管理界面

  status              查看系统整体状态

  version             显示版本信息

  checkpoint <action> 状态持久化
    save              保存检查点
    load              加载检查点

  perf                性能报告

  load                Agent负载监控

  circuit             熔断状态查看

  review [<base>] [<target>]  增量代码审查

  template            工作流模板
    list              列出所有模板

  parse <文本>        自然语言任务解析

  dag                 任务依赖DAG示例

  config              配置中心
    get [key]         获取配置
    set <key> <value> 设置配置
    reload            重新加载

  queue               异步任务队列
    submit            提交任务
    status            队列状态
    list              任务列表

  audit               审计日志
    report            生成报告
    stats             统计信息

  approval            人工审批
    list              待审批列表
    create            创建审批
    approve <id>      批准请求
    reject <id>       拒绝请求

示例:
  python -m core.cli agent list
  python -m core.cli web
  python -m core.cli perf
  python -m core.cli template list
  python -m core.cli parse "帮我做一个登录页面"
  python -m core.cli queue submit "通知任务" notify
  python -m core.cli audit report
  python -m core.cli approval list
        """)
        return

    if command == 'version' or command == '--version':
        print("Multi-Agent Suite v3.2.0")
        print("11-Agent 超级团队 + 工作流管理 + Web看板 + 多渠道通知")
        return

    if command == 'agent':
        from core.orchestrator import MultiAgentOrchestrator
        orch = MultiAgentOrchestrator()

        if len(sys.argv) > 2:
            action = sys.argv[2]
            if action == 'list' or action == 'ls':
                orch.list_agents()
            elif action == 'stats':
                stats = orch.get_system_stats()
                print("\n📊 Agent 统计:")
                print(f"   总数: {stats['agents']['total']}")
                print(f"   空闲: {stats['agents']['idle']}")
                print(f"   工作中: {stats['agents']['busy']}")
            else:
                agent = orch.get_agent_by_id(action)
                if agent:
                    print(f"\n👤 Agent: {agent.name}")
                    print(f"   ID: {agent.id}")
                    print(f"   角色: {agent.role.value}")
                    print(f"   状态: {agent.status}")
                    print(f"   能力: {', '.join(agent.capabilities)}")
                else:
                    print(f"❌ 未找到Agent: {action}")
        else:
            orch.list_agents()

    elif command == 'task':
        if len(sys.argv) < 3:
            print("用法: task <create|list|status|progress> [参数]")
            print("示例: python -m core.cli task create '项目名称'")
            return

        action = sys.argv[2]

        if action in ['create', 'new']:
            name = sys.argv[3] if len(sys.argv) > 3 else "新任务"
            desc = sys.argv[4] if len(sys.argv) > 4 else ""
            from core.workflow import DevelopmentWorkflow
            wf = DevelopmentWorkflow()
            wf.create_task(name, desc, [])

        elif action in ['list', 'ls']:
            from core.workflow import DevelopmentWorkflow
            wf = DevelopmentWorkflow()
            wf.list_all_tasks()

        elif action == 'status':
            if len(sys.argv) > 3:
                from core.workflow import DevelopmentWorkflow
                wf = DevelopmentWorkflow()
                wf.show_task_status(sys.argv[3])
            else:
                print("用法: task status <task_id>")

        elif action == 'progress':
            if len(sys.argv) > 3:
                from core.workflow import DevelopmentWorkflow
                wf = DevelopmentWorkflow()
                wf.progress_stage(sys.argv[3], approved=True)
            else:
                print("用法: task progress <task_id>")
        else:
            print(f"未知操作: {action}")

    elif command == 'web':
        print("🌐 启动Web管理界面...")
        print("📍 访问: http://localhost:8080")
        print("\n按 Ctrl+C 停止服务\n")
        subprocess.run([sys.executable, str(SUITE_DIR / "web-ui" / "app.py")])

    elif command == 'status':
        from core.orchestrator import MultiAgentOrchestrator
        orch = MultiAgentOrchestrator()
        stats = orch.get_system_stats()
        print("\n📊 系统状态:")
        print(f"  🤖 Agent: {stats['agents']['idle']} 空闲 | {stats['agents']['busy']} 工作中 | {stats['agents']['total']} 总数")
        print(f"  📋 任务: {stats['tasks']['completed']} 完成 | {stats['tasks']['pending']} 待处理 | {stats['tasks']['total']} 总数")

    elif command == 'notify':
        if len(sys.argv) > 2:
            notif_type = sys.argv[2]
            from agents.kilo_notification import NotificationAgent
            kilo = NotificationAgent()

            if notif_type == 'daily':
                kilo.send_daily_summary()
            elif notif_type == 'backup':
                kilo.send_backup_notification('success', 'CLI触发')
            elif notif_type == 'alert':
                msg = sys.argv[3] if len(sys.argv) > 3 else "测试告警"
                kilo.send_system_alert('info', msg)
            else:
                print(f"未知通知类型: {notif_type}")
        else:
            print("用法: notify <daily|backup|alert>")

    elif command == 'checkpoint':
        from core.enhancements import checkpoint_manager
        if len(sys.argv) > 2:
            action = sys.argv[2]
            if action == 'save':
                from core.orchestrator import MultiAgentOrchestrator
                orch = MultiAgentOrchestrator()
                state = {
                    'agents': {k: asdict(v) for k, v in orch.agents.items()},
                    'tasks': {k: asdict(v) for k, v in orch.tasks.items()},
                    'subtasks': {k: asdict(v) for k, v in orch.subtasks.items()}
                }
                checkpoint_manager.save_checkpoint(state)
            elif action == 'load':
                data = checkpoint_manager.load_checkpoint()
                if data:
                    print("✅ 检查点加载成功")
                else:
                    print("❌ 加载失败")
            elif action == 'list':
                cps = sorted((SUITE_DIR / "checkpoints").glob("*.json"))
                print("📂 可用检查点:")
                for cp in cps:
                    print(f"  - {cp.stem}")
        else:
            print("用法: checkpoint <save|load|list>")

    elif command == 'perf':
        from core.enhancements import performance_monitor
        print(performance_monitor.generate_report())

    elif command == 'load':
        from core.enhancements import load_balancer
        from core.orchestrator import MultiAgentOrchestrator
        orch = MultiAgentOrchestrator()
        report = load_balancer.get_load_report(orch.agents)
        print("📊 Agent负载报告:")
        for agent_id, info in report.items():
            bar = "█" * int(info['load'] * 10) + "░" * (10 - int(info['load'] * 10))
            print(f"  {agent_id:<8} [{bar}] {info['load']:.0%} - {info['status']}")

    elif command == 'circuit':
        from core.enhancements import retry_policy
        status = retry_policy.get_status()
        if not status:
            print("🛡️ 所有Agent正常运行，无熔断")
        else:
            print("🛡️ 熔断状态:")
            for agent_id, info in status.items():
                emoji = "🔴" if info['state'] == 'open' else "🟡"
                print(f"  {emoji} {agent_id}: {info['state']} (失败 {info['failures']} 次)")

    elif command == 'review':
        from core.incremental_reviewer import IncrementalReviewer
        reviewer = IncrementalReviewer()
        base = sys.argv[2] if len(sys.argv) > 2 else "HEAD~1"
        target = sys.argv[3] if len(sys.argv) > 3 else "HEAD"
        changes = reviewer.get_changes(base, target)
        print(reviewer.generate_summary(changes))

    elif command == 'template' or command == 'templates':
        from core.templates import template_registry
        if len(sys.argv) > 2:
            action = sys.argv[2]
            if action == 'list':
                templates = template_registry.list_templates()
                print("📋 可用模板:")
                for t in templates:
                    print(f"  • {t['id']}: {t['name']} ({t['stage_count']}个阶段, ~{t['estimated_hours']}小时)")
            elif action == 'show' or action == 'view':
                template_id = sys.argv[3] if len(sys.argv) > 3 else "web_app"
                stages = template_registry.get_template_stages(template_id)
                print(f"📋 模板: {template_id}")
                for i, s in enumerate(stages, 1):
                    print(f"  {i}. {s['name']} → {s['agent']}")
        else:
            templates = template_registry.list_templates()
            print("📋 可用模板:")
            for t in templates:
                print(f"  • {t['id']}: {t['name']}")

    elif command == 'parse' or command == 'nlp':
        from core.nlp_parser import NaturalLanguageParser
        if len(sys.argv) > 2:
            user_input = " ".join(sys.argv[2:])
            parser = NaturalLanguageParser()
            task = parser.parse(user_input)
            print(parser.explain_parsing(task))
        else:
            print("用法: python -m core.cli parse '帮我做一个登录页面'")

    elif command == 'dag':
        from core.task_dag import TaskDAG
        dag = TaskDAG()
        dag.add_task("A", "任务A")
        dag.add_task("B", "任务B", dependencies=["A"])
        dag.add_task("C", "任务C", dependencies=["B"])
        print(dag.visualize())

    elif command == 'config':
        from core.config_center import config_center
        if len(sys.argv) > 2:
            action = sys.argv[2]
            if action == 'get':
                key = sys.argv[3] if len(sys.argv) > 3 else "*"
                if key == "*":
                    print(json.dumps(config_center.get_all(), ensure_ascii=False, indent=2))
                else:
                    print(config_center.get(key))
            elif action == 'set':
                if len(sys.argv) > 4:
                    key = sys.argv[3]
                    value = sys.argv[4]
                    config_center.set(key, value)
                    print(f"✅ 已设置 {key} = {value}")
            elif action == 'reload':
                config_center.reload()
                print("✅ 配置已重新加载")
            elif action == 'history':
                history = config_center.get_change_history()
                print("📜 配置变更历史:")
                for h in history[-5:]:
                    print(f"  {h.timestamp}: {h.key} = {h.new_value}")
        else:
            print("用法: config <get|set|reload|history> [key] [value]")

    elif command == 'queue':
        from core.task_queue import task_queue
        if len(sys.argv) > 2:
            action = sys.argv[2]
            if action == 'submit' or action == 'add':
                task_id = task_queue.submit(
                    name=sys.argv[3] if len(sys.argv) > 3 else "任务",
                    func=sys.argv[4] if len(sys.argv) > 4 else "notify",
                    message="测试消息" if len(sys.argv) <= 4 else " ".join(sys.argv[4:])
                )
                print(f"✅ 任务已提交: {task_id}")
            elif action == 'status':
                status = task_queue.get_queue_status()
                print("📋 任务队列状态:")
                print(f"  待处理: {status['pending']}")
                print(f"  执行中: {status['running']}")
                print(f"  已完成: {status['completed']}")
                print(f"  失败: {status['failed']}")
            elif action == 'list':
                for tid, task in task_queue.tasks.items():
                    print(f"  {tid}: {task.name} [{task.status.value}]")
        else:
            print("用法: queue <submit|status|list>")

    elif command == 'audit':
        from core.audit_logger import audit_logger
        if len(sys.argv) > 2:
            action = sys.argv[2]
            if action == 'report':
                print(audit_logger.generate_report())
            elif action == 'stats':
                stats = audit_logger.get_statistics()
                print("📊 审计统计:")
                print(f"  总记录: {stats.get('total', 0)}")
                print(f"  按类别: {stats.get('by_category', {})}")
            else:
                entries = audit_logger.query(limit=10)
                for e in entries:
                    print(f"  {e.timestamp[:19]} [{e.level}] {e.action}")
        else:
            print(audit_logger.generate_report())

    elif command == 'approval' or command == 'approve':
        from core.approval_system import approval_system
        if len(sys.argv) > 2:
            action = sys.argv[2]
            if action == 'list' or action == 'pending':
                print(approval_system.visualize_pending())
            elif action == 'create':
                from core.approval_system import ApprovalType
                req_id = approval_system.create_request(
                    approval_type=ApprovalType.CUSTOM,
                    title=sys.argv[3] if len(sys.argv) > 3 else "测试审批",
                    description=sys.argv[4] if len(sys.argv) > 4 else "测试描述",
                    requester="cli"
                )
                print(f"✅ 审批请求已创建: {req_id}")
            elif action == 'approve':
                if len(sys.argv) > 3:
                    result = approval_system.approve(sys.argv[3], "admin", "已批准")
                    print(f"✅ 已批准: {sys.argv[3]}" if result else "❌ 批准失败")
            elif action == 'reject':
                if len(sys.argv) > 3:
                    result = approval_system.reject(sys.argv[3], "admin", "不符合要求")
                    print(f"✅ 已拒绝: {sys.argv[3]}" if result else "❌ 拒绝失败")
            elif action == 'status':
                print(approval_system.get_status())
        else:
            print(approval_system.visualize_pending())

    elif command == 'project':
        from core.workflow_engine import WaterfallWorkflowEngine, ProjectPhase, PhaseStatus
        engine = WaterfallWorkflowEngine()
        if len(sys.argv) > 2:
            action = sys.argv[2]
            if action in ['create', 'new']:
                name = sys.argv[3] if len(sys.argv) > 3 else "新项目"
                desc = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""
                template = "web_app"
                for i, arg in enumerate(sys.argv):
                    if arg == '--template' and i + 1 < len(sys.argv):
                        template = sys.argv[i + 1]
                proj_id = engine.create_project(name, desc, template)
                print(f"\n📌 查看项目: python -m core.cli project status {proj_id}")
            elif action in ['list', 'ls']:
                projects = engine.list_projects()
                print("\n📋 项目列表:")
                print("-" * 80)
                for p in projects:
                    status = engine.get_project_status(p.id)
                    print(f"{p.id:<25} {p.name:<25} {status['phase_name']:<15} {status['progress']}")
                print("-" * 80)
            elif action == 'status':
                if len(sys.argv) > 3:
                    status = engine.get_project_status(sys.argv[3])
                    if "error" in status:
                        print(f"❌ {status['error']}")
                    else:
                        print(f"\n📊 项目状态: {status['name']}")
                        print(f"  当前阶段: {status['phase_name']}")
                        print(f"  进度: {status['progress']} ({status['progress_percent']}%)")
                        print(f"  任务: {status['completed_tasks']}/{status['total_tasks']}")
                        print(f"  产出物: {status['artifacts_count']} 个")
            elif action == 'report':
                if len(sys.argv) > 3:
                    print(engine.generate_project_report(sys.argv[3]))
        else:
            print("用法: project <create|list|status|report> [参数]")

    elif command == 'doc':
        from core.document_generator import DocumentGenerator
        gen = DocumentGenerator()
        if len(sys.argv) > 2:
            action = sys.argv[2]
            if action == 'prd':
                name = sys.argv[3] if len(sys.argv) > 3 else "项目"
                output = gen.generate_prd(name, "项目描述", [], [])
                print(f"✅ 文档已生成: {output}")
            elif action == 'architecture':
                name = sys.argv[3] if len(sys.argv) > 3 else "项目"
                output = gen.generate_architecture_doc(name, [], {})
                print(f"✅ 文档已生成: {output}")
            elif action == 'api':
                name = sys.argv[3] if len(sys.argv) > 3 else "项目"
                output = gen.generate_api_doc(name, [], [])
                print(f"✅ 文档已生成: {output}")
            elif action == 'er':
                name = sys.argv[3] if len(sys.argv) > 3 else "项目"
                output = gen.generate_er_diagram(name, [])
                print(f"✅ 文档已生成: {output}")
            elif action == 'manual':
                name = sys.argv[3] if len(sys.argv) > 3 else "项目"
                output = gen.generate_user_manual(name, [])
                print(f"✅ 文档已生成: {output}")
            elif action == 'deploy':
                name = sys.argv[3] if len(sys.argv) > 3 else "项目"
                output = gen.generate_deploy_doc(name, {}, {})
                print(f"✅ 文档已生成: {output}")
        else:
            print("用法: doc <prd|architecture|api|er|manual|deploy> [项目名]")

    elif command == 'deploy':
        from core.deployment_manager import DeploymentManager, DeployType
        manager = DeploymentManager()
        if len(sys.argv) > 2:
            action = sys.argv[2]
            if action == 'list':
                deps = manager.list_deployments()
                print("\n📋 部署列表:")
                print("-" * 80)
                for d in deps:
                    print(f"{d.id:<25} {d.project_name:<20} {d.version:<10} {d.status.value}")
                print("-" * 80)
            elif action == 'servers':
                servers = manager.list_servers()
                print("\n🖥️ 服务器列表:")
                for s in servers:
                    print(f"  {s.name}: {s.host}:{s.port}")
            elif action == 'add-server':
                if len(sys.argv) > 4:
                    name, host = sys.argv[3], sys.argv[4]
                    port = int(sys.argv[5]) if len(sys.argv) > 5 else 22
                    manager.add_server(name, host, port)
            elif action == 'status':
                if len(sys.argv) > 3:
                    status = manager.get_deployment_status(sys.argv[3])
                    if "error" in status:
                        print(f"❌ {status['error']}")
                    else:
                        print(f"\n📊 部署状态:")
                        for k, v in status.items():
                            print(f"  {k}: {v}")
        else:
            print("用法: deploy <list|servers|add-server|status> [参数]")

    elif command == 'qa':
        from core.quality_assurance import QualityAssurance
        qa = QualityAssurance()
        if len(sys.argv) > 2:
            action = sys.argv[2]
            if action == 'summary' or action == 'stats':
                summary = qa.get_qa_summary()
                print(f"\n📊 QA总结:")
                print(f"  测试套件: {summary['test_suites']}")
                print(f"  测试用例: {summary['test_cases']}")
                print(f"  缺陷: {summary['bugs']}")
                print(f"  代码审查: {summary['code_reviews']}")
                print(f"  安全问题: {summary['security_issues']}")
            elif action == 'bugs':
                stats = qa.get_bug_statistics()
                print(f"\n🐛 缺陷统计:")
                print(f"  总数: {stats['total']}")
                print(f"  待处理: {stats['open_count']}")
                print(f"  已解决: {stats['resolved_count']}")
            elif action == 'suite':
                name = sys.argv[3] if len(sys.argv) > 3 else "测试套件"
                suite_id = qa.create_test_suite(name, "", "unit")
                print(f"✅ 测试套件已创建: {suite_id}")
            elif action == 'scan':
                if len(sys.argv) > 3:
                    project_path = sys.argv[3]
                    issues = qa.scan_security(project_path)
                    print(f"\n🔒 安全扫描结果: {len(issues)} 个问题")
                    for issue in issues[:10]:
                        print(f"  [{issue.severity.value}] {issue.title}")
            elif action == 'report':
                report = qa.generate_bug_report()
                print(f"✅ 缺陷报告已生成: {report}")
        else:
            print("用法: qa <summary|bugs|suite|scan|report> [参数]")

    else:
        print(f"未知命令: {command}")
        print("使用 python -m core.cli help 查看帮助")

from dataclasses import asdict

if __name__ == '__main__':
    main()
