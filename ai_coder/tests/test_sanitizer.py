from __future__ import annotations

import unittest

from ai_coder.security.sanitizer import InputSanitizer


class SanitizerTests(unittest.TestCase):
    def test_valid_input_is_returned_unchanged(self) -> None:
        sanitizer = InputSanitizer()
        result = sanitizer.sanitize("solve the bug in parser.py")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.value, "solve the bug in parser.py")
        self.assertEqual(result.violations, ())

    def test_newline_is_rejected(self) -> None:
        sanitizer = InputSanitizer()
        result = sanitizer.sanitize("hello\nworld")
        self.assertFalse(result.is_valid)
        self.assertIn("Dangerous character found: '\\n'", result.violations)

    def test_invalid_session_name_is_rejected(self) -> None:
        sanitizer = InputSanitizer()
        result = sanitizer.validate_session_name("bad/name")
        self.assertFalse(result.is_valid)
