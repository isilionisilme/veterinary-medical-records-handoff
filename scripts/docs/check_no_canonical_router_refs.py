#!/usr/bin/env python3
"""Fail when canonical docs reference docs/agent_router.*"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_TARGETS = [
    REPO_ROOT / "docs" / "README.md",
    REPO_ROOT / "docs" / "project",
    REPO_ROOT / "docs" / "shared",
]
FORBIDDEN_PATTERN = re.compile(r"docs/agent_router|agent_router", re.IGNORECASE)


def iter_markdown_files() -> list[Path]:
    files: list[Path] = []
    for target in CANONICAL_TARGETS:
        if target.is_file() and target.suffix.lower() == ".md":
            files.append(target)
            continue
        if target.is_dir():
            files.extend(sorted(target.rglob("*.md")))
    return files


def find_violations(path: Path) -> list[tuple[int, str]]:
    violations: list[tuple[int, str]] = []
    text = path.read_text(encoding="utf-8")
    for line_number, line in enumerate(text.splitlines(), start=1):
        if FORBIDDEN_PATTERN.search(line):
            violations.append((line_number, line.strip()))
    return violations


def main() -> int:
    all_violations: list[tuple[Path, int, str]] = []
    for file_path in iter_markdown_files():
        for line_number, line in find_violations(file_path):
            all_violations.append((file_path, line_number, line))

    if not all_violations:
        print("Canonical docs guard passed: no agent_router references found.")
        return 0

    print(
        "Canonical docs guard failed: found forbidden references to docs/agent_router "
        "in canonical docs."
    )
    print(
        "Fix: remove agent_router mentions from docs/README.md, "
        "docs/projects/veterinary-medical-records/**, docs/shared/**."
    )
    for file_path, line_number, line in all_violations:
        relative = file_path.relative_to(REPO_ROOT).as_posix()
        print(f"- {relative}:{line_number}: {line}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
