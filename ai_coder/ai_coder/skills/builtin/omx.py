"""Built-in OMX skill."""

from __future__ import annotations

from ..registry import SkillDefinition


def build_skill() -> SkillDefinition:
    return SkillDefinition(
        name="omx",
        description="Prefix the prompt for OMX-compatible execution.",
        template="omx: {command}",
    )
