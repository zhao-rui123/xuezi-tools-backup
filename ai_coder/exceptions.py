"""Shared exception hierarchy for ai_coder."""


class AICoderError(Exception):
    """Base error for all package exceptions."""


class ConfigError(AICoderError):
    """Raised when configuration is invalid or incomplete."""


class ValidationError(AICoderError):
    """Raised when user input or task data is invalid."""


class ExecutionError(AICoderError):
    """Raised when an executor cannot run a task."""


class SkillError(AICoderError):
    """Raised when skill discovery or execution fails."""


class StoreError(AICoderError):
    """Raised when background state persistence fails."""


class DependencyUnavailableError(AICoderError):
    """Raised when an optional runtime dependency is missing."""
