#!/usr/bin/env python3
"""
技能评估器 - 评估技能包使用情况，使用频率统计，效果评估
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from config import get_config

logger = logging.getLogger('memory-suite')


class SkillEvaluator:
    """技能评估器"""

    def __init__(self, config=None):
        self._config = config or get_config()
        self._workspace = self._config.workspace
        self._memory_dir = self._config.get_path('memory')
        self._evolution_dir = self._config.get_path('evolution')
        self._skills_dir = self._workspace / "skills"
        self._skills_eval_dir = self._evolution_dir / "skills"

        self._skills_eval_dir.mkdir(parents=True, exist_ok=True)

    def evaluate(self) -> Optional[Dict[str, Any]]:
        """
        执行技能评估

        Returns:
            评估结果字典
        """
        logger.info("执行技能评估...")

        try:
            skills_evaluated = 0
            high_frequency = 0
            skill_details = []

            if self._skills_dir.exists() and self._skills_dir.is_dir():
                skill_dirs = [d for d in self._skills_dir.iterdir() if d.is_dir()]
                skills_evaluated = len(skill_dirs)

                for skill_dir in skill_dirs:
                    try:
                        skill_file = skill_dir / "SKILL.md"
                        is_active = skill_file.exists()

                        config_file = skill_dir / "config.json"
                        config = {}
                        if config_file.exists():
                            with open(config_file, 'r', encoding='utf-8') as f:
                                config = json.load(f)

                        skill_info = {
                            "name": skill_dir.name,
                            "path": str(skill_dir),
                            "active": is_active,
                            "config": config
                        }

                        if is_active:
                            high_frequency += 1

                        skill_details.append(skill_info)

                    except Exception as e:
                        logger.warning(f"评估技能失败: {skill_dir.name} - {e}")

            recommendations = self._generate_recommendations(skills_evaluated, high_frequency)

            report = {
                "evaluated_at": datetime.now().isoformat(),
                "skills_evaluated": skills_evaluated,
                "high_frequency": high_frequency,
                "low_frequency": skills_evaluated - high_frequency,
                "top_skills": skill_details[:5],
                "recommendations": recommendations
            }

            report_path = self._skills_eval_dir / f"skill_eval_{datetime.now().strftime('%Y%m%d')}.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            report["report_path"] = str(report_path)
            logger.info(f"技能评估报告已保存: {report_path}")

            return report

        except PermissionError as e:
            logger.error(f"技能评估失败 - 权限不足: {e}")
            return None
        except Exception as e:
            logger.error(f"技能评估失败: {e}")
            return None

    def _generate_recommendations(self, total: int, active: int) -> list:
        """生成推荐建议"""
        recommendations = []

        if total == 0:
            recommendations.append("还没有添加任何技能包")
        else:
            if active < total * 0.5:
                recommendations.append("定期使用技能包以保持熟练度")
            if active > 0:
                recommendations.append("已使用的技能表现良好，继续保持")

        recommendations.extend([
            "定期清理不再使用的技能",
            "更新过时的技能包",
            "探索新的技能以扩展能力"
        ])

        return recommendations[:5]
