#!/usr/bin/env python3
"""
多Agent协作系统 v2.2 - 完整开发流程版
集成：需求确认 → 评审 → 分配 → 开发 → 预览 → 审查 → 验收 → 部署 → 文档 → 迭代
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum

SUITE_DIR = Path("~/.openclaw/workspace/skills/multi-agent-suite").expanduser()
TASKS_DIR = SUITE_DIR / "tasks"
TASKS_DIR.mkdir(parents=True, exist_ok=True)

class WorkflowStage(Enum):
    """开发流程阶段"""
    REQUIREMENT_CONFIRM = "requirement_confirm"
    REQUIREMENT_REVIEW = "requirement_review"
    TASK_ASSIGN = "task_assign"
    PARALLEL_DEV = "parallel_dev"
    DEV_PREVIEW = "dev_preview"
    CODE_REVIEW = "code_review"
    USER_ACCEPT = "user_accept"
    BACKUP_ROLLBACK = "backup_rollback"
    UNIFIED_DEPLOY = "unified_deploy"
    DELIVER_DOC = "deliver_doc"
    ITERATION = "iteration"
    COMPLETED = "completed"

class StageStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    SKIPPED = "skipped"

@dataclass
class WorkflowStep:
    """工作流步骤"""
    stage: WorkflowStage
    status: StageStatus
    assigned_to: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    notes: str = ""
    deliverables: List[str] = field(default_factory=list)

@dataclass
class DevelopmentTask:
    """开发任务（完整流程）"""
    id: str
    title: str
    description: str
    requirements: List[str] = field(default_factory=list)
    workflow: List[WorkflowStep] = field(default_factory=list)
    current_stage: int = 0
    requirement_doc: str = ""
    design_doc: str = ""
    code_files: List[str] = field(default_factory=list)
    test_report: str = ""
    deploy_doc: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    version: str = "1.0.0"
    backup_tag: str = ""

class DevelopmentWorkflow:
    """完整开发流程管理"""

    def __init__(self):
        self.tasks: Dict[str, DevelopmentTask] = {}
        self.load_tasks()

    def load_tasks(self):
        """加载任务"""
        tasks_file = TASKS_DIR / "workflow_tasks.json"
        if tasks_file.exists():
            try:
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for task_id, task_data in data.items():
                        workflow = []
                        for step_data in task_data.get('workflow', []):
                            try:
                                stage = WorkflowStage(step_data['stage']) if isinstance(step_data['stage'], str) else step_data['stage']
                                status = StageStatus(step_data['status']) if isinstance(step_data['status'], str) else step_data['status']
                                step = WorkflowStep(
                                    stage=stage,
                                    status=status,
                                    assigned_to=step_data.get('assigned_to'),
                                    started_at=step_data.get('started_at'),
                                    completed_at=step_data.get('completed_at'),
                                    notes=step_data.get('notes', ''),
                                    deliverables=step_data.get('deliverables', [])
                                )
                                workflow.append(step)
                            except:
                                continue

                        task_data['workflow'] = workflow
                        self.tasks[task_id] = DevelopmentTask(**task_data)
            except Exception as e:
                print(f"加载任务失败: {e}")

    def save_tasks(self):
        """保存任务"""
        tasks_file = TASKS_DIR / "workflow_tasks.json"
        data = {}
        for task_id, task in self.tasks.items():
            task_dict = asdict(task)
            task_dict['workflow'] = [
                {
                    **asdict(step),
                    'stage': step.stage.value if hasattr(step.stage, 'value') else str(step.stage),
                    'status': step.status.value if hasattr(step.status, 'value') else str(step.status)
                }
                for step in task.workflow
            ]
            data[task_id] = task_dict

        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create_standard_workflow(self) -> List[WorkflowStep]:
        """创建标准开发流程"""
        return [
            WorkflowStep(WorkflowStage.REQUIREMENT_CONFIRM, StageStatus.PENDING),
            WorkflowStep(WorkflowStage.REQUIREMENT_REVIEW, StageStatus.PENDING),
            WorkflowStep(WorkflowStage.TASK_ASSIGN, StageStatus.PENDING),
            WorkflowStep(WorkflowStage.PARALLEL_DEV, StageStatus.PENDING),
            WorkflowStep(WorkflowStage.DEV_PREVIEW, StageStatus.PENDING),
            WorkflowStep(WorkflowStage.CODE_REVIEW, StageStatus.PENDING),
            WorkflowStep(WorkflowStage.USER_ACCEPT, StageStatus.PENDING),
            WorkflowStep(WorkflowStage.BACKUP_ROLLBACK, StageStatus.PENDING),
            WorkflowStep(WorkflowStage.UNIFIED_DEPLOY, StageStatus.PENDING),
            WorkflowStep(WorkflowStage.DELIVER_DOC, StageStatus.PENDING),
            WorkflowStep(WorkflowStage.ITERATION, StageStatus.PENDING),
        ]

    def create_task(self, title: str, description: str, requirements: List[str], template: str = "web_app") -> str:
        """创建新任务"""
        task_id = f"dev-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        task = DevelopmentTask(
            id=task_id,
            title=title,
            description=description,
            requirements=requirements,
            workflow=self.create_standard_workflow()
        )

        self.tasks[task_id] = task
        self.save_tasks()

        print(f"✅ 创建开发任务: {title}")
        print(f"   ID: {task_id}")
        print(f"   模板: {template}")
        print(f"   流程: 11个阶段")
        print(f"\n📋 下一步: 需求确认 (用户确认需求文档)")
        print(f"   命令: python3 workflow.py --progress {task_id} --approve")

        return task_id

    def progress_stage(self, task_id: str, approved: bool = True, notes: str = ""):
        """推进到下一阶段"""
        task = self.tasks.get(task_id)
        if not task:
            print(f"❌ 任务不存在: {task_id}")
            return

        if task.current_stage >= len(task.workflow):
            print(f"✅ 任务已完成: {task.title}")
            return

        current_step = task.workflow[task.current_stage]

        current_step.status = StageStatus.APPROVED if approved else StageStatus.REJECTED
        current_step.completed_at = datetime.now().isoformat()
        current_step.notes = notes

        if approved:
            task.current_stage += 1

            if task.current_stage < len(task.workflow):
                next_step = task.workflow[task.current_stage]
                next_step.status = StageStatus.IN_PROGRESS
                next_step.started_at = datetime.now().isoformat()

                print(f"✅ 阶段完成: {current_step.stage.value}")
                print(f"\n🔄 进入下一阶段: {next_step.stage.value}")
                print(f"   {self.get_stage_description(next_step.stage)}")
            else:
                task.completed_at = datetime.now().isoformat()
                print(f"🎉 任务全部完成: {task.title}")
        else:
            print(f"❌ 阶段被拒绝: {current_step.stage.value}")
            print(f"   需要重新处理")

        self.save_tasks()

    def get_stage_description(self, stage: WorkflowStage) -> str:
        """获取阶段描述"""
        descriptions = {
            WorkflowStage.REQUIREMENT_CONFIRM: "用户确认需求文档，明确功能清单",
            WorkflowStage.REQUIREMENT_REVIEW: "评估任务等级，确认技术方案",
            WorkflowStage.TASK_ASSIGN: "拆解任务，分配给Agent团队",
            WorkflowStage.PARALLEL_DEV: "Agent并行开发",
            WorkflowStage.DEV_PREVIEW: "启动本地服务器，用户整体体验",
            WorkflowStage.CODE_REVIEW: "审查代码，检查质量",
            WorkflowStage.USER_ACCEPT: "用户测试通过后再部署",
            WorkflowStage.BACKUP_ROLLBACK: "部署前自动备份服务器旧版本",
            WorkflowStage.UNIFIED_DEPLOY: "部署上线",
            WorkflowStage.DELIVER_DOC: "README + 使用说明一起交付",
            WorkflowStage.ITERATION: "根据反馈继续完善",
        }
        return descriptions.get(stage, "")

    def get_next_action(self, task_id: str) -> str:
        """获取下一步操作"""
        task = self.tasks.get(task_id)
        if not task:
            return "任务不存在"

        if task.current_stage >= len(task.workflow):
            return "任务已完成"

        current_step = task.workflow[task.current_stage]

        actions = {
            WorkflowStage.REQUIREMENT_CONFIRM: "python3 workflow.py --progress {task_id} --approve",
            WorkflowStage.REQUIREMENT_REVIEW: "python3 workflow.py --progress {task_id} --approve",
            WorkflowStage.TASK_ASSIGN: "python3 workflow.py --progress {task_id} --approve",
            WorkflowStage.PARALLEL_DEV: "python3 workflow.py --progress {task_id} --approve",
            WorkflowStage.DEV_PREVIEW: "python3 workflow.py --progress {task_id} --approve",
            WorkflowStage.CODE_REVIEW: "python3 workflow.py --progress {task_id} --approve",
            WorkflowStage.USER_ACCEPT: "python3 workflow.py --progress {task_id} --approve",
            WorkflowStage.BACKUP_ROLLBACK: "python3 workflow.py --progress {task_id} --approve",
            WorkflowStage.UNIFIED_DEPLOY: "python3 workflow.py --progress {task_id} --approve",
            WorkflowStage.DELIVER_DOC: "python3 workflow.py --progress {task_id} --approve",
            WorkflowStage.ITERATION: "python3 workflow.py --progress {task_id} --approve",
        }

        return actions.get(current_step.stage, "未知").format(task_id=task_id)

    def show_task_status(self, task_id: str):
        """显示任务状态"""
        task = self.tasks.get(task_id)
        if not task:
            print(f"❌ 任务不存在: {task_id}")
            return

        print("=" * 70)
        print(f"📋 开发任务: {task.title}")
        print("=" * 70)
        print(f"ID: {task.id}")
        print(f"描述: {task.description}")
        print(f"需求: {', '.join(task.requirements) if task.requirements else '无'}")
        print()

        print("🔄 开发流程进度:")
        print("-" * 70)

        for i, step in enumerate(task.workflow):
            status_emoji = {
                StageStatus.PENDING: "⏳",
                StageStatus.IN_PROGRESS: "🔄",
                StageStatus.REVIEWING: "👀",
                StageStatus.APPROVED: "✅",
                StageStatus.REJECTED: "❌",
                StageStatus.COMPLETED: "✅",
                StageStatus.SKIPPED: "⏭️"
            }.get(step.status, "⚪")

            current_marker = " >>" if i == task.current_stage else "   "

            stage_name = step.stage.value if hasattr(step.stage, 'value') else str(step.stage)
            status_name = step.status.value if hasattr(step.status, 'value') else str(step.status)
            print(f"{current_marker} {status_emoji} {i+1:2d}. {stage_name:<20} [{status_name}]")

            if step.notes:
                print(f"       备注: {step.notes}")

        print("-" * 70)

        if task.current_stage < len(task.workflow):
            current = task.workflow[task.current_stage]
            stage_name = current.stage.value if hasattr(current.stage, 'value') else str(current.stage)
            print(f"\n🎯 当前阶段: {stage_name}")
            print(f"   说明: {self.get_stage_description(current.stage)}")
            print(f"\n📌 推进任务: python3 workflow.py --progress {task_id} --approve")
        else:
            print(f"\n🎉 任务已完成!")

        print("=" * 70)

    def list_all_tasks(self):
        """列出所有任务"""
        if not self.tasks:
            print("📋 暂无任务")
            return

        print("\n📋 开发任务列表:")
        print("-" * 80)
        print(f"{'ID':<25} {'标题':<25} {'当前阶段':<20} {'状态'}")
        print("-" * 80)

        for task in self.tasks.values():
            current_stage_name = "已完成"
            if task.current_stage < len(task.workflow):
                current = task.workflow[task.current_stage]
                current_stage_name = current.stage.value if hasattr(current.stage, 'value') else str(current.stage)

            status = "✅ 完成" if task.completed_at else "🔄 进行中"
            print(f"{task.id:<25} {task.title:<25} {current_stage_name:<20} {status}")

        print("-" * 80)
        print(f"总计: {len(self.tasks)} 个任务")

    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        if task_id not in self.tasks:
            print(f"❌ 任务不存在: {task_id}")
            return False

        task = self.tasks.pop(task_id)
        self.save_tasks()
        print(f"✅ 已删除任务: {task.title}")
        return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description='完整开发流程管理 v2.2')
    parser.add_argument('--create', type=str, help='创建任务')
    parser.add_argument('--description', type=str, help='任务描述')
    parser.add_argument('--requirements', type=str, nargs='+', help='需求列表')
    parser.add_argument('--status', type=str, help='查看任务状态')
    parser.add_argument('--progress', type=str, help='推进任务到下一阶段')
    parser.add_argument('--approve', action='store_true', help='批准当前阶段')
    parser.add_argument('--reject', action='store_true', help='拒绝当前阶段')
    parser.add_argument('--notes', type=str, help='阶段备注')
    parser.add_argument('--list', action='store_true', help='列出所有任务')
    parser.add_argument('--delete', type=str, help='删除任务')

    args = parser.parse_args()

    workflow = DevelopmentWorkflow()

    if args.list:
        workflow.list_all_tasks()
    elif args.create:
        reqs = args.requirements or []
        task_id = workflow.create_task(args.create, args.description or "", reqs)
        print(f"\n📌 使用以下命令查看进度:")
        print(f"   python3 workflow.py --status {task_id}")
    elif args.status:
        workflow.show_task_status(args.status)
    elif args.progress:
        approved = not args.reject
        workflow.progress_stage(args.progress, approved, args.notes or "")
    elif args.delete:
        workflow.delete_task(args.delete)
    else:
        parser.print_help()
        print("\n💡 快速使用示例:")
        print("   python3 workflow.py --create '我的项目' --description '一个Web应用'")
        print("   python3 workflow.py --list")
        print("   python3 workflow.py --status dev-2026-0309-123456")


if __name__ == '__main__':
    main()
