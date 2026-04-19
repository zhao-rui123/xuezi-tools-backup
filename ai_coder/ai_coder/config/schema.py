"""Validated settings models with lazy section loading."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any, Mapping

from ..exceptions import ConfigError
from . import defaults


_HOST_RE = re.compile(r"^[a-zA-Z0-9._-]+$")
_USER_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_-]*$")


def _expand_path(value: str) -> str:
    return os.path.expanduser(value)


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    raise ConfigError(f"Invalid boolean value: {value!r}")


def _coerce_int(value: Any) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip():
        try:
            return int(value.strip())
        except ValueError as exc:
            raise ConfigError(f"Invalid integer value: {value!r}") from exc
    raise ConfigError(f"Invalid integer value: {value!r}")


@dataclass(frozen=True)
class LocalConfig:
    """Local Claude/Opus runtime configuration."""

    acpx_path: str = defaults.LOCAL_ACPX_PATH
    workspace: str = defaults.LOCAL_WORKSPACE
    model: str | None = None

    @property
    def resolved_workspace(self) -> str:
        return _expand_path(self.workspace)


@dataclass(frozen=True)
class RemoteConfig:
    """Remote Codex runtime configuration."""

    host: str
    user: str
    ssh_key: str
    acpx_path: str = defaults.REMOTE_ACPX_PATH
    known_hosts: str = defaults.REMOTE_KNOWN_HOSTS
    model: str | None = None

    def __post_init__(self) -> None:
        if not _HOST_RE.match(self.host):
            raise ConfigError(f"Invalid remote host: {self.host!r}")
        if not _USER_RE.match(self.user):
            raise ConfigError(f"Invalid remote user: {self.user!r}")
        if not self.ssh_key:
            raise ConfigError("Remote ssh_key is required")

    @property
    def resolved_ssh_key(self) -> str:
        return _expand_path(self.ssh_key)

    @property
    def resolved_known_hosts(self) -> str:
        return _expand_path(self.known_hosts)


@dataclass(frozen=True)
class SecurityConfig:
    """Security and auditing settings."""

    max_task_length: int = defaults.SECURITY_MAX_TASK_LENGTH
    enable_audit: bool = defaults.SECURITY_ENABLE_AUDIT
    audit_log_path: str = defaults.SECURITY_AUDIT_LOG_PATH

    @property
    def resolved_audit_log_path(self) -> str:
        return _expand_path(self.audit_log_path)


class Settings:
    """Lazy configuration container."""

    def __init__(self, raw: Mapping[str, Any] | None = None, env: Mapping[str, str] | None = None):
        self._raw = dict(raw or {})
        self._env = dict(env or os.environ)
        self._local: LocalConfig | None = None
        self._remote: RemoteConfig | None = None
        self._security: SecurityConfig | None = None

    @property
    def local(self) -> LocalConfig:
        if self._local is None:
            self._local = self._load_local()
        return self._local

    @property
    def remote(self) -> RemoteConfig:
        if self._remote is None:
            self._remote = self._load_remote()
        return self._remote

    @property
    def security(self) -> SecurityConfig:
        if self._security is None:
            self._security = self._load_security()
        return self._security

    def has_remote_config(self) -> bool:
        try:
            self._build_remote_payload()
        except ConfigError:
            return False
        return True

    def _section(self, name: str) -> Mapping[str, Any]:
        section = self._raw.get(name, {})
        if section is None:
            return {}
        if not isinstance(section, Mapping):
            raise ConfigError(f"Config section {name!r} must be a mapping")
        return section

    def _first_value(self, section: str, field: str, *env_names: str, default: Any = None) -> Any:
        value = self._section(section).get(field, default)
        for env_name in env_names:
            env_value = self._env.get(env_name)
            if env_value is not None and env_value != "":
                value = env_value
        return value

    def _load_local(self) -> LocalConfig:
        return LocalConfig(
            acpx_path=str(
                self._first_value("local", "acpx_path", "AI_CODER_LOCAL_ACPX", "AI_CODER_LOCAL_ACPX_PATH", default=defaults.LOCAL_ACPX_PATH)
            ),
            workspace=str(
                self._first_value("local", "workspace", "AI_CODER_WORKSPACE", "AI_CODER_LOCAL_WORKSPACE", default=defaults.LOCAL_WORKSPACE)
            ),
            model=self._first_value("local", "model", "AI_CODER_MODEL", default=None),
        )

    def _build_remote_payload(self) -> dict[str, str]:
        host = self._first_value("remote", "host", "AI_CODER_KR_HOST")
        user = self._first_value("remote", "user", "AI_CODER_KR_USER")
        ssh_key = self._first_value("remote", "ssh_key", "AI_CODER_SSH_KEY", "AI_CODER_KR_SSH_KEY")
        if not host or not user or not ssh_key:
            raise ConfigError("Remote provider requires AI_CODER_KR_HOST, AI_CODER_KR_USER, and AI_CODER_SSH_KEY")
        return {
            "host": str(host),
            "user": str(user),
            "ssh_key": str(ssh_key),
            "acpx_path": str(
                self._first_value("remote", "acpx_path", "AI_CODER_KR_ACPX", default=defaults.REMOTE_ACPX_PATH)
            ),
            "known_hosts": str(
                self._first_value(
                    "remote",
                    "known_hosts",
                    "AI_CODER_KR_KNOWN_HOSTS",
                    "AI_CODER_KNOWN_HOSTS",
                    default=defaults.REMOTE_KNOWN_HOSTS,
                )
            ),
            "model": self._first_value("remote", "model", "AI_CODER_REMOTE_MODEL", default=None),
        }

    def _load_remote(self) -> RemoteConfig:
        return RemoteConfig(**self._build_remote_payload())

    def _load_security(self) -> SecurityConfig:
        max_task_length = self._first_value(
            "security",
            "max_task_length",
            "AI_CODER_SECURITY_MAX_TASK_LENGTH",
            default=defaults.SECURITY_MAX_TASK_LENGTH,
        )
        enable_audit = self._first_value(
            "security",
            "enable_audit",
            "AI_CODER_SECURITY_ENABLE_AUDIT",
            default=defaults.SECURITY_ENABLE_AUDIT,
        )
        audit_log_path = self._first_value(
            "security",
            "audit_log_path",
            "AI_CODER_SECURITY_AUDIT_LOG_PATH",
            default=defaults.SECURITY_AUDIT_LOG_PATH,
        )
        return SecurityConfig(
            max_task_length=_coerce_int(max_task_length),
            enable_audit=_coerce_bool(enable_audit),
            audit_log_path=str(audit_log_path),
        )
