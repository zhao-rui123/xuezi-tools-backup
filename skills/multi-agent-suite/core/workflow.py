#!/usr/bin/env python3
"""
多Agent协作系统 v2.1 - 完整开发流程版
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
    REQUIREMENT_CONFIRM = "requirement_confirm"    # 需求确认
    REQUIREMENT_REVIEW = "requirement_review"      # 需求评审
    TASK_ASSIGN = "task_assign"                    # 任务分配
    PARALLEL_DEV = "parallel_dev"                  # 并行开发
    DEV_PREVIEW = "dev_preview"                    # 开发预览
    CODE_REVIEW = "code_review"                    # 代码审查
    USER_ACCEPT = "user_accept"                    # 用户验收
    BACKUP_ROLLBACK = "backup_rollback"            # 备份回滚
    UNIFIED_DEPLOY = "unified_deploy"              # 统一部署
    DELIVER_DOC = "deliver_doc"                    # 交付文档
    ITERATION = "iteration"                        # 迭代优化
    COMPLETED = "completed"                        # 已完成

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
    
    # 工作流
    workflow: List[WorkflowStep] = field(default_factory=list)
    current_stage: int = 0
    
    # 文件
    requirement_doc: str = ""           # 需求文档路径
    design_doc: str = ""                # 设计文档路径
    code_files: List[str] = field(default_factory=list)
    test_report: str = ""               # 测试报告路径
    deploy_doc: str = ""                # 部署文档路径
    
    # 状态
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    # 版本
    version: str = "1.0.0"
    backup_tag: str = ""                # 备份标签

class DevelopmentWorkflow:
    """完整开发流程管理"""
    
    def __init__(self):
        self.tasks: Dict[str, DevelopmentTask] = {}
        self.load_tasks()
    
    def load_tasks(self):
        """加载任务"""
        tasks_file = TASKS_DIR / "workflow_tasks.json"
        if tasks_file.exists():
            with open(tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for task_id, task_data in data.items():
                    # 重建WorkflowStep对象
                    workflow = []
                    for step_data in task_data.get('workflow', []):
                        step = WorkflowStep(
                            stage=WorkflowStage(step_data['stage']),
                            status=StageStatus(step_data['status']),
                            assigned_to=step_data.get('assigned_to'),
                            started_at=step_data.get('started_at'),
                            completed_at=step_data.get('completed_at'),
                            notes=step_data.get('notes', ''),
                            deliverables=step_data.get('deliverables', [])
                        )
                        workflow.append(step)
                    
                    task_data['workflow'] = workflow
                    self.tasks[task_id] = DevelopmentTask(**task_data)
    
    def save_tasks(self):
        """保存任务"""
        tasks_file = TASKS_DIR / "workflow_tasks.json"
        data = {}
        for task_id, task in self.tasks.items():
            task_dict = asdict(task)
            # 转换枚举为字符串
            task_dict['workflow'] = [
                {
                    **asdict(step),
                    'stage': step.stage.value,
                    'status': step.status.value
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
    
    def create_task(self, title: str, description: str, requirements: List[str]) -> str:
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
        print(f"   流程: 11个阶段")
        print(f"\n📋 下一步: 需求确认 (用户确认需求文档)")
        print(f"   命令: python3 workflow.py --confirm-requirement {task_id}")
        
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
        
        # 完成当前阶段
        current_step.status = StageStatus.APPROVED if approved else StageStatus.REJECTED
        current_step.completed_at = datetime.now().isoformat()
        current_step.notes = notes
        
        if approved:
            task.current_stage += 1
            
            # 开始下一阶段
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
            WorkflowStage.TASK_ASSIGN: "拆解任务，分配给5-Agent团队",
            WorkflowStage.PARALLEL_DEV: "Alpha/Bravo/Charlie并行开发",
            WorkflowStage.DEV_PREVIEW: "全部做完启动本地服务器，用户整体体验",
            WorkflowStage.CODE_REVIEW: "Delta审查代码，检查质量",
            WorkflowStage.USER_ACCEPT: "用户测试通过后再部署",
            WorkflowStage.BACKUP_ROLLBACK: "部署前自动备份服务器旧版本",
            WorkflowStage.UNIFIED_DEPLOY: "Echo统一部署上线",
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
            WorkflowStage.REQUIREMENT_CONFIRM: "用户确认需求文档 (confirm-requirement)",
            WorkflowStage.REQUIREMENT_REVIEW: "评审需求并评估 (review-requirement)",
            WorkflowStage.TASK_ASSIGN: "分配任务给Agent (assign-task)",
            WorkflowStage.PARALLEL_DEV: "开始并行开发 (start-development)",
            WorkflowStage.DEV_PREVIEW: "启动预览服务器 (start-preview)",
            WorkflowStage.CODE_REVIEW: "代码审查 (code-review)",
            WorkflowStage.USER_ACCEPT: "用户验收 (user-accept)",
            WorkflowStage.BACKUP_ROLLBACK: "备份旧版本 (backup)",
            WorkflowStage.UNIFIED_DEPLOY: "部署上线 (deploy)",
            WorkflowStage.DELIVER_DOC: "交付文档 (deliver)",
            WorkflowStage.ITERATION: "迭代优化 (iterate)",
        }
        
        return actions.get(current_step.stage, "未知")
    
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
        print(f"需求: {', '.join(task.requirements)}")
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
            
            print(f"{current_marker} {status_emoji} {i+1:2d}. {step.stage.value:<20} [{step.status.value}]")
            
            if step.notes:
                print(f"       备注: {step.notes}")
        
        print("-" * 70)
        
        if task.current_stage < len(task.workflow):
            current = task.workflow[task.current_stage]
            print(f"\n🎯 当前阶段: {current.stage.value}")
            print(f"   说明: {self.get_stage_description(current.stage)}")
            print(f"\n📌 下一步: {self.get_next_action(task_id)}")
        else:
            print(f"\n🎉 任务已完成!")
        
        print("=" * 70)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='完整开发流程管理')
    parser.add_argument('--create', type=str, help='创建任务')
    parser.add_argument('--description', type=str, help='任务描述')
    parser.add_argument('--requirements', type=str, nargs='+', help='需求列表')
    parser.add_argument('--status', type=str, help='查看任务状态')
    parser.add_argument('--progress', type=str, help='推进任务到下一阶段')
    parser.add_argument('--approve', action='store_true', help='批准当前阶段')
    parser.add_argument('--reject', action='store_true', help='拒绝当前阶段')
    parser.add_argument('--notes', type=str, help='阶段备注')
    
    args = parser.parse_args()
    
    workflow = DevelopmentWorkflow()
    
    if args.create:
        reqs = args.requirements or []
        workflow.create_task(args.create, args.description or "", reqs)
    elif args.status:
        workflow.show_task_status(args.status)
    elif args.progress:
        approved = not args.reject
        workflow.progress_stage(args.progress, approved, args.notes or "")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
