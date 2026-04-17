"""Built-in OMC skill."""

from __future__ import annotations

from ..registry import SkillDefinition


def build_skill() -> SkillDefinition:
    return SkillDefinition(
        name="omc",
        description="Prefix the prompt for OMC-compatible execution.",
        template="omc: {command}",
    )
