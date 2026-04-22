"""CEO Agent - High-level autonomous task coordinator.

Parses high-level goals, decomposes into sub-tasks, coordinates
multiple specialized agents, and summarizes results.
"""

from __future__ import annotations

from .planner import TaskDecomposer, TaskPlan, SubTask

__all__ = ["TaskDecomposer", "TaskPlan", "SubTask"]
