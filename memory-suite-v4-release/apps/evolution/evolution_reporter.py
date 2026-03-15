#!/usr/bin/env python3
"""
进化报告生成器 - 生成自我进化报告，技能成长追踪，改进建议
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

from config import get_config

logger = logging.getLogger('memory-suite')


class EvolutionReporter:
    """进化报告生成器"""

    def __init__(self, config=None):
        self._config = config or get_config()
        self._evolution_dir = self._config.get_path('evolution')
        self._daily_dir = self._evolution_dir / "daily"
        self._monthly_dir = self._evolution_dir / "monthly"
        self._skills_dir = self._evolution_dir / "skills"
        self._reports_dir = self._evolution_dir / "reports"

        self._ensure_directories()

    def _ensure_directories(self):
        """确保目录存在"""
        for d in [self._daily_dir, self._monthly_dir, self._skills_dir, self._reports_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def generate_report(self, period: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        生成进化报告

        Args:
            period: 报告周期 (monthly)，默认为当前月份

        Returns:
            报告结果字典
        """
        if period is None:
            period = datetime.now().strftime("%Y-%m")

        logger.info(f"生成进化报告: {period}")

        try:
            daily_reports = list(self._daily_dir.glob("*.json")) if self._daily_dir.exists() else []
            skill_reports = list(self._skills_dir.glob("*.json")) if self._skills_dir.exists() else []
            monthly_reports = list(self._monthly_dir.glob("*.json")) if self._monthly_dir.exists() else []

            tasks_completed = 0
            total_efficiency = 0.0

            for daily_file in daily_reports:
                try:
                    with open(daily_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        tasks_completed += data.get("tasks_completed", 0)
                        total_efficiency += data.get("efficiency_score", 0)
                except Exception:
                    continue

            avg_efficiency = total_efficiency / len(daily_reports) if daily_reports else 0

            suggestions = self._generate_suggestions(len(daily_reports), tasks_completed, avg_efficiency)

            report = {
                "period": period,
                "generated_at": datetime.now().isoformat(),
                "skill_growth": len(skill_reports),
                "suggestions_count": len(suggestions),
                "daily_analyses": len(daily_reports),
                "monthly_plans": len(monthly_reports),
                "tasks_completed": tasks_completed,
                "avg_efficiency": round(avg_efficiency, 2),
                "suggestions": suggestions,
                "highlights": self._generate_highlights(len(daily_reports), tasks_completed, len(skill_reports))
            }

            report_path = self._reports_dir / f"evolution_{period}.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            report["report_path"] = str(report_path)
            logger.info(f"进化报告已保存: {report_path}")

            return report

        except PermissionError as e:
            logger.error(f"进化报告生成失败 - 权限不足: {e}")
            return None
        except IOError as e:
            logger.error(f"进化报告生成失败 - IO错误: {e}")
            return None
        except Exception as e:
            logger.error(f"进化报告生成失败: {e}")
            return None

    def _generate_suggestions(self, daily_count: int, tasks: int, efficiency: float) -> List[str]:
        """生成改进建议"""
        suggestions = []

        if daily_count == 0:
            suggestions.append("建议开始每日分析以追踪您的进步")
        elif daily_count < 20:
            suggestions.append("继续保持每日分析的习惯")

        if tasks < 10:
            suggestions.append("尝试增加每日任务数量以提高产出")
        elif tasks > 100:
            suggestions.append("注意休息，避免过度工作")

        if efficiency < 50:
            suggestions.append("建议优化工作流程以提高效率")
        elif efficiency > 90:
            suggestions.append("效率很高！继续保持")

        if not suggestions:
            suggestions = [
                "继续保持高效的工作节奏",
                "定期回顾和总结经验",
                "尝试新的工具和方法"
            ]

        return suggestions[:5]

    def _generate_highlights(self, daily_count: int, tasks: int, skills: int) -> str:
        """生成亮点总结"""
        highlights = []
        highlights.append(f"本月完成 {daily_count} 次每日分析")
        highlights.append(f"共完成 {tasks} 项任务")
        if skills > 0:
            highlights.append(f"评估了 {skills} 个技能")
        return " | ".join(highlights)

    def get_evolution_trend(self, months: int = 3) -> Dict[str, Any]:
        """获取进化趋势数据"""
        try:
            reports = []
            for report_file in self._reports_dir.glob("evolution_*.json"):
                try:
                    with open(report_file, 'r', encoding='utf-8') as f:
                        reports.append(json.load(f))
                except Exception:
                    continue

            reports.sort(key=lambda x: x.get("generated_at", ""), reverse=True)

            return {
                "total_reports": len(reports),
                "recent_reports": reports[:months],
                "trend": self._analyze_trend(reports[:months])
            }

        except Exception as e:
            logger.error(f"获取进化趋势失败: {e}")
            return {"error": str(e)}

    def _analyze_trend(self, reports: List[Dict]) -> Dict[str, Any]:
        """分析趋势"""
        if not reports:
            return {"status": "no_data"}

        avg_tasks = sum(r.get("tasks_completed", 0) for r in reports) / len(reports)
        avg_efficiency = sum(r.get("avg_efficiency", 0) for r in reports) / len(reports)

        trend = "stable"
        if len(reports) >= 2:
            first_half = sum(r.get("tasks_completed", 0) for r in reports[len(reports)//2:]) / (len(reports) // 2)
            second_half = sum(r.get("tasks_completed", 0) for r in reports[:len(reports)//2]) / (len(reports) // 2)
            if second_half > first_half * 1.2:
                trend = "improving"
            elif second_half < first_half * 0.8:
                trend = "declining"

        return {
            "avg_tasks": round(avg_tasks, 2),
            "avg_efficiency": round(avg_efficiency, 2),
            "trend": trend
        }
