"""Credential helpers."""

from __future__ import annotations

import os

from ..exceptions import ConfigError


def get_env_credential(name: str, *, required: bool = True) -> str | None:
    value = os.environ.get(name)
    if required and not value:
        raise ConfigError(f"Missing required credential: {name}")
    return value


def mask_secret(value: str | None) -> str:
    if not value:
        return ""
    if len(value) <= 4:
        return "*" * len(value)
    return f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"
