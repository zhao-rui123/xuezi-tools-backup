#!/usr/bin/env python3
"""
分析引擎 - 记忆分析
"""

import json
import re
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from config import get_config

logger = logging.getLogger('memory-suite')


class AnalysisManager:
    """分析引擎"""

    def __init__(self, config=None):
        self._config = config or get_config()
        self._summary_dir = self._config.get_path('summary')
        self._memory_dir = self._config.get_path('memory')
        self._evolution_dir = self._config.get_path('evolution')

        self._summary_dir.mkdir(parents=True, exist_ok=True)

    @property
    def summary_dir(self) -> Path:
        return self._summary_dir

    def generate_daily_report(self) -> Optional[str]:
        """生成日报"""
        return self._generate_report("daily")

    def generate_weekly_report(self) -> Optional[str]:
        """生成周报"""
        return self._generate_report("weekly")

    def generate_monthly_report(self) -> Optional[str]:
        """生成月报"""
        return self._generate_report("monthly")

    def _generate_report(self, report_type: str) -> Optional[str]:
        """生成报告"""
        try:
            today = datetime.now()

            if report_type == "daily":
                date_str = today.strftime("%Y-%m-%d")
                period_start = today.replace(hour=0, minute=0, second=0)
            elif report_type == "weekly":
                date_str = f"W{today.isocalendar()[1]}"
                period_start = today - timedelta(days=today.weekday())
            else:
                date_str = today.strftime("%Y-%m")
                period_start = today.replace(day=1, hour=0, minute=0, second=0)

            report_file = self._summary_dir / f"{report_type}_{date_str}.json"

            memory_files = list(self._memory_dir.glob("*.md"))
            total_content_size = 0
            total_words = 0

            period_files = []
            for f in memory_files:
                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    if mtime >= period_start:
                        period_files.append(f)
                        with open(f, 'r', encoding='utf-8') as fp:
                            content = fp.read()
                            total_content_size += len(content)
                            total_words += len(content.split())
                except Exception:
                    continue

            # 统计今日会话数（从文件内容中统计）
            session_count = 0
            for f in period_files:
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        content = fp.read()
                        # 统计 "## [" 出现的次数（每个会话的标记）
                        session_count += content.count("## [")
                except Exception:
                    continue

            report = {
                "type": report_type,
                "period": date_str,
                "generated_at": datetime.now().isoformat(),
                "total_memory_files": len(memory_files),
                "period_files": len(period_files),
                "session_count": session_count,
                "total_content_size": total_content_size,
                "total_words": total_words,
                "summary": self._generate_summary(report_type, date_str, session_count, len(memory_files))
            }

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            logger.info(f"{report_type}报告已生成: {report_file}")
            return str(report_file)

        except PermissionError as e:
            logger.error(f"生成报告失败 - 权限不足: {e}")
            return None
        except IOError as e:
            logger.error(f"生成报告失败 - IO错误: {e}")
            return None
        except Exception as e:
            logger.error(f"生成报告失败: {e}")
            return None

    def _generate_summary(self, report_type: str, date_str: str, session_count: int, total_files: int) -> str:
        """生成摘要文本"""
        summaries = {
            "daily": f"日报 - {date_str}: 今日 {session_count} 个会话，累计 {total_files} 个记忆文件",
            "weekly": f"周报 - {date_str}: 本周 {session_count} 个会话，累计 {total_files} 个记忆文件",
            "monthly": f"月报 - {date_str}: 本月 {session_count} 个会话，累计 {total_files} 个记忆文件"
        }
        return summaries.get(report_type, f"{report_type} 报告 - {date_str}")

    def get_analysis(self, days: int = 7) -> Dict[str, Any]:
        """获取近期分析数据"""
        try:
            threshold = datetime.now() - timedelta(days=days)
            memory_files = list(self._memory_dir.glob("*.md"))

            files_data = []
            for f in memory_files:
                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    if mtime >= threshold:
                        with open(f, 'r', encoding='utf-8') as fp:
                            content = fp.read()
                            files_data.append({
                                "name": f.name,
                                "size": f.stat().st_size,
                                "words": len(content.split()),
                                "modified": mtime.isoformat()
                            })
                except Exception:
                    continue

            return {
                "period_days": days,
                "files_count": len(files_data),
                "total_size": sum(f["size"] for f in files_data),
                "total_words": sum(f["words"] for f in files_data),
                "files": files_data
            }

        except Exception as e:
            logger.error(f"获取分析数据失败: {e}")
            return {"error": str(e)}

    def analyze_keyword_frequency(self, days: int = 30) -> Dict[str, int]:
        """分析关键词频率"""
        try:
            threshold = datetime.now() - timedelta(days=days)
            memory_files = list(self._memory_dir.glob("*.md"))

            keyword_counter = {}
            for f in memory_files:
                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    if mtime >= threshold:
                        with open(f, 'r', encoding='utf-8') as fp:
                            content = fp.read().lower()
                            words = re.findall(r'\b[a-zA-Z\u4e00-\u9fff]{2,}\b', content)
                            for w in words:
                                keyword_counter[w] = keyword_counter.get(w, 0) + 1
                except Exception:
                    continue

            sorted_keywords = sorted(keyword_counter.items(), key=lambda x: x[1], reverse=True)
            return dict(sorted_keywords[:100])

        except Exception as e:
            logger.error(f"关键词分析失败: {e}")
            return {}
