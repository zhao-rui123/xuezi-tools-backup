from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
TEST_DIR = ROOT / "tests"


def _iter_python_files() -> list[Path]:
    files: list[Path] = []
    for base in (SRC_DIR, TEST_DIR):
        files.extend(sorted(base.rglob("*.py")))
    return files


def _check_ast() -> None:
    files = _iter_python_files()
    for path in files:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    print(f"AST OK: {len(files)} files")


def _run_tests() -> None:
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(SRC_DIR) if not existing else str(SRC_DIR) + os.pathsep + existing
    command = [sys.executable, "-B", "-m", "unittest", "discover", "-s", str(TEST_DIR), "-p", "test_*.py"]
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def main() -> int:
    _check_ast()
    _run_tests()
    print("VERIFY OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
