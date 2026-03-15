#!/usr/bin/env python3
"""
长期规划器 - 基于历史数据生成长期规划，目标设定和追踪
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from config import get_config

logger = logging.getLogger('memory-suite')


class LongTermPlanner:
    """长期规划器"""

    def __init__(self, config=None):
        self._config = config or get_config()
        self._memory_dir = self._config.get_path('memory')
        self._evolution_dir = self._config.get_path('evolution')
        self._monthly_dir = self._evolution_dir / "monthly"

        self._monthly_dir.mkdir(parents=True, exist_ok=True)

    def generate_plan(self, period: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        生成长期规划

        Args:
            period: 规划周期 (monthly/quarterly)，默认为 monthly

        Returns:
            规划结果字典
        """
        if period is None:
            period = "monthly"

        now = datetime.now()
        period_label = now.strftime("%Y-%m") if period == "monthly" else f"{now.year}-Q{(now.month-1)//3 + 1}"

        logger.info(f"生成长期规划: {period_label} ({period})")

        try:
            memory_files = list(self._memory_dir.glob("*.md"))
            total_files = len(memory_files)

            recent_files = [f for f in memory_files if
                datetime.fromtimestamp(f.stat().st_mtime) > now.replace(day=1)]

            goals = self._generate_goals(total_files, len(recent_files), period)

            plan = {
                "period": period_label,
                "period_type": period,
                "generated_at": datetime.now().isoformat(),
                "goal_count": len(goals),
                "goals": goals,
                "review_date": (now.replace(day=28) if period == "monthly" else now).isoformat(),
                "status": "active"
            }

            plan_path = self._monthly_dir / f"plan_{period_label}.json"
            with open(plan_path, 'w', encoding='utf-8') as f:
                json.dump(plan, f, ensure_ascii=False, indent=2)

            plan["plan_path"] = str(plan_path)
            logger.info(f"长期规划已保存: {plan_path}")

            return plan

        except PermissionError as e:
            logger.error(f"长期规划生成失败 - 权限不足: {e}")
            return None
        except IOError as e:
            logger.error(f"长期规划生成失败 - IO错误: {e}")
            return None
        except Exception as e:
            logger.error(f"长期规划生成失败: {e}")
            return None

    def _generate_goals(self, total_files: int, recent_files: int, period: str) -> list:
        """基于历史数据生成目标"""
        goals = []

        if recent_files > 0:
            goals.append({
                "id": 1,
                "title": "保持记忆记录习惯",
                "description": f"本月已记录 {recent_files} 个记忆文件",
                "status": "in_progress" if recent_files >= 10 else "pending",
                "priority": "high"
            })

        if total_files > 50:
            goals.append({
                "id": 2,
                "title": "整理和归档历史记忆",
                "description": "对积累的记忆进行分类整理",
                "status": "pending",
                "priority": "medium"
            })

        goals.append({
            "id": 3,
            "title": "持续改进工作效率",
            "description": "通过每日分析追踪效率提升",
            "status": "pending",
            "priority": "high"
        })

        goals.append({
            "id": 4,
            "title": "学习新技能",
            "description": "探索新的工具和方法",
            "status": "pending",
            "priority": "medium"
        })

        return goals[:5]

    def update_goal_status(self, plan_period: str, goal_id: int, status: str) -> bool:
        """更新目标状态"""
        try:
            plan_path = self._monthly_dir / f"plan_{plan_period}.json"
            if not plan_path.exists():
                logger.warning(f"规划文件不存在: {plan_period}")
                return False

            with open(plan_path, 'r', encoding='utf-8') as f:
                plan = json.load(f)

            for goal in plan.get("goals", []):
                if goal.get("id") == goal_id:
                    goal["status"] = status
                    goal["updated_at"] = datetime.now().isoformat()
                    break

            with open(plan_path, 'w', encoding='utf-8') as f:
                json.dump(plan, f, ensure_ascii=False, indent=2)

            logger.info(f"目标状态已更新: {goal_id} -> {status}")
            return True

        except Exception as e:
            logger.error(f"更新目标状态失败: {e}")
            return False
