"""Skill registry."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core.models import ExecutorType
from ..exceptions import SkillError


@dataclass(frozen=True)
class SkillDefinition:
    """Declarative skill definition."""

    name: str
    description: str
    template: str
    executor: ExecutorType | None = None
    source: str = "builtin"
    metadata: dict[str, str] = field(default_factory=dict)

    def render(self, command: str, metadata: dict[str, object] | None = None) -> str:
        values = {"command": command}
        if metadata:
            values.update(metadata)
        return self.template.format(**values)


class SkillRegistry:
    """In-memory skill registry."""

    def __init__(self):
        self._skills: dict[str, SkillDefinition] = {}

    def register(self, skill: SkillDefinition) -> None:
        self._skills[skill.name] = skill

    def load_many(self, skills: list[SkillDefinition]) -> None:
        for skill in skills:
            self.register(skill)

    def get(self, name: str) -> SkillDefinition:
        try:
            return self._skills[name]
        except KeyError as exc:
            raise SkillError(f"Unknown skill: {name}") from exc

    def list(self) -> list[SkillDefinition]:
        return sorted(self._skills.values(), key=lambda skill: skill.name)
