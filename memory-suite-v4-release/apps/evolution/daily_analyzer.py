#!/usr/bin/env python3
"""
每日分析器 - 分析每日工作内容，统计任务完成情况，生成效率报告
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from config import get_config

logger = logging.getLogger('memory-suite')


class DailyAnalyzer:
    """每日分析器"""

    def __init__(self, config=None):
        self._config = config or get_config()
        self._memory_dir = self._config.get_path('memory')
        self._evolution_dir = self._config.get_path('evolution')
        self._daily_dir = self._evolution_dir / "daily"

        self._daily_dir.mkdir(parents=True, exist_ok=True)

    def analyze(self, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        执行每日分析

        Args:
            date: 分析日期 (YYYY-MM-DD)，默认为今天

        Returns:
            分析结果字典
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        logger.info(f"执行每日分析: {date}")

        try:
            memory_file = self._memory_dir / f"{date}.md"
            tasks_completed = 0
            total_tasks = 0
            efficiency_score = 0

            if memory_file.exists():
                with open(memory_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tasks_completed = content.count('✅') + content.count('完成') + content.count('[x]')
                    total_tasks = tasks_completed + content.count('⬜') + content.count('[ ]') + content.count('TODO')
                    if total_tasks > 0:
                        efficiency_score = min(100, int(tasks_completed / total_tasks * 100))

            report = {
                "date": date,
                "analyzed_at": datetime.now().isoformat(),
                "tasks_completed": tasks_completed,
                "total_tasks": total_tasks,
                "efficiency_score": efficiency_score,
                "summary": f"完成 {tasks_completed}/{total_tasks} 项任务，效率评分 {efficiency_score}"
            }

            report_path = self._daily_dir / f"daily_{date}.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            report["report_path"] = str(report_path)
            logger.info(f"每日分析报告已保存: {report_path}")

            return report

        except PermissionError as e:
            logger.error(f"每日分析失败 - 权限不足: {e}")
            return None
        except IOError as e:
            logger.error(f"每日分析失败 - IO错误: {e}")
            return None
        except Exception as e:
            logger.error(f"每日分析失败: {e}")
            return None
