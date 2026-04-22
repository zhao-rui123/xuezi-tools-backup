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
    """
    Whitelist-based input sanitization.

    Only truly dangerous patterns are blocked:
    - Shell command injection (operators + dangerous commands)
    - Path traversal attacks
    - Null bytes and other control characters

    Backticks, $(), and most code syntax are ALLOWED since they are
    normal in code analysis tasks.
    """

    # Control chars that should never appear in valid input
    DANGEROUS_CHARS = ("\x00", "\x1b")

    # Truly dangerous patterns only — shell command injection and path traversal
    # These block patterns like:  ; rm -rf  or  | cat /etc/passwd  or  ../..
    DANGEROUS_PATTERNS = (
        # Shell operators followed by dangerous commands (command injection)
        r"[;&|]\s*(?:rm|mv|cp|cat|sh|bash|python|curl|wget|npm|git|chmod|chown)\b",
        # Path traversal
        r"(?:^|[\\/])\.\.(?:[\\/]|$)",
    )
    SESSION_NAME_RE = re.compile(r"^[a-zA-Z0-9-]+$")

    def __init__(self, max_length: int = 10_000):
        self.max_length = max_length
        self.patterns = tuple(re.compile(pattern) for pattern in self.DANGEROUS_PATTERNS)

    def sanitize(self, input_str: str) -> SanitizationResult:
        """Validate input using whitelist approach — only block truly dangerous patterns."""

        violations: list[str] = []
        if len(input_str) > self.max_length:
            violations.append(f"Input exceeds max length: {len(input_str)} > {self.max_length}")

        # Block null bytes and escape sequences only
        for char in self.DANGEROUS_CHARS:
            if char in input_str:
                violations.append(f"Dangerous character found: {repr(char)}")

        # Block only truly dangerous injection patterns
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
