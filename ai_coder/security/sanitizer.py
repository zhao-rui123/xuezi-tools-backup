"""Input validation without mutating user prompts."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SanitizationResult:
    """Validation result for a user-supplied string."""

    is_valid: bool
    value: str
    violations: tuple[str, ...]


class InputSanitizer:
    """Reject obviously dangerous control sequences before execution."""

    DANGEROUS_CHARS = ("\x00", "\n", "\r", "\x1b")
    DANGEROUS_PATTERNS = (
        r"`[^`]+`",
        r"\$\([^)]+\)",
        r"[;&|]\s*(?:rm|mv|cp|cat|sh|bash|python|curl|wget)\b",
        r"(?:^|[\\/])\.\.(?:[\\/]|$)",
    )
    SESSION_NAME_RE = re.compile(r"^[a-zA-Z0-9-]+$")

    def __init__(self, max_length: int = 10_000):
        self.max_length = max_length
        self.patterns = tuple(re.compile(pattern) for pattern in self.DANGEROUS_PATTERNS)

    def sanitize(self, input_str: str) -> SanitizationResult:
        """Validate input and return the original string unchanged when valid."""

        violations: list[str] = []
        if len(input_str) > self.max_length:
            violations.append(f"Input exceeds max length: {len(input_str)} > {self.max_length}")
        for char in self.DANGEROUS_CHARS:
            if char in input_str:
                violations.append(f"Dangerous character found: {repr(char)}")
        for pattern in self.patterns:
            if pattern.search(input_str):
                violations.append(f"Dangerous pattern matched: {pattern.pattern}")
        return SanitizationResult(not violations, input_str, tuple(violations))

    def validate_session_name(self, name: str) -> SanitizationResult:
        if not self.SESSION_NAME_RE.match(name):
            return SanitizationResult(
                False,
                name,
                (f"Invalid session name: {name}. Only alphanumeric and hyphen allowed.",),
            )
        return SanitizationResult(True, name, ())
