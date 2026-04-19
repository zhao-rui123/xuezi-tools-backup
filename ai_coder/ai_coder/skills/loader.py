"""YAML skill loader."""

from __future__ import annotations

from pathlib import Path

from ..config.loader import _parse_simple_yaml
from ..core.models import ExecutorType
from ..exceptions import ConfigError, SkillError
from .registry import SkillDefinition


class SkillLoader:
    """Load simple declarative skills from YAML files."""

    def load_file(self, path: str | Path) -> SkillDefinition:
        file_path = Path(path)
        if file_path.suffix.lower() not in {".yaml", ".yml"}:
            raise SkillError(f"Unsupported skill file: {file_path.name}")
        payload = _parse_simple_yaml(file_path.read_text(encoding="utf-8"))
        try:
            executor_value = payload.get("executor")
            executor = ExecutorType(executor_value) if executor_value else None
            return SkillDefinition(
                name=str(payload["name"]),
                description=str(payload.get("description", "")),
                template=str(payload["template"]),
                executor=executor,
                source=str(file_path),
            )
        except KeyError as exc:
            raise ConfigError(f"Skill file missing required key: {exc.args[0]}") from exc

    def load_directory(self, directory: str | Path) -> list[SkillDefinition]:
        dir_path = Path(directory)
        if not dir_path.exists():
            return []
        skills: list[SkillDefinition] = []
        for file_path in sorted(dir_path.glob("*.y*ml")):
            skills.append(self.load_file(file_path))
        return skills
