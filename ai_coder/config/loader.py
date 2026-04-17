"""Settings loader for env, TOML, JSON, and simple YAML."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

from ..exceptions import ConfigError
from .schema import Settings

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]


def _parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigError(f"Invalid .env line: {raw_line!r}")
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if ":" not in line:
            raise ConfigError(f"Unsupported YAML line: {raw_line!r}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise ConfigError(f"Invalid YAML indentation near: {raw_line!r}")
        current = stack[-1][1]
        if value == "":
            next_section: dict[str, Any] = {}
            current[key] = next_section
            stack.append((indent, next_section))
            continue
        if value.lower() in {"true", "false"}:
            parsed: Any = value.lower() == "true"
        else:
            parsed = value.strip("\"'")
            if parsed.isdigit():
                parsed = int(parsed)
        current[key] = parsed
    return root


def _load_config_file(path: Path) -> Mapping[str, Any]:
    suffix = path.suffix.lower()
    if suffix == ".toml":
        if tomllib is None:
            raise ConfigError("TOML loading requires Python 3.11+")
        return tomllib.loads(path.read_text(encoding="utf-8"))
    if suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    if suffix in {".yaml", ".yml"}:
        return _parse_simple_yaml(path.read_text(encoding="utf-8"))
    raise ConfigError(f"Unsupported config file type: {path.name}")


def load_settings(config_path: str | None = None, environ: Mapping[str, str] | None = None) -> Settings:
    """Load settings with lazy local/remote/security sections."""

    env = dict(environ or os.environ)
    raw: Mapping[str, Any] = {}
    if config_path:
        path = Path(config_path).expanduser()
        if not path.exists():
            raise ConfigError(f"Config file not found: {path}")
        if path.suffix.lower() == ".env":
            env = {**_parse_env_file(path), **env}
        else:
            raw = _load_config_file(path)
    return Settings(raw=raw, env=env)
