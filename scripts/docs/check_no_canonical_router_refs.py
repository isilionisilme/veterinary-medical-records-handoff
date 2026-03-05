#!/usr/bin/env python3
"""Fail when canonical docs reference docs/agent_router.*"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_TARGETS = [
    REPO_ROOT / "docs" / "README.md",
    REPO_ROOT / "docs" / "projects",
    REPO_ROOT / "docs" / "shared",
]
# Plans are operational artifacts and may legitimately reference router paths.
EXCLUDED_CANONICAL_SUBPATHS = ("/04-delivery/plans/",)
FORBIDDEN_PATTERN = re.compile(r"docs/agent_router|agent_router", re.IGNORECASE)
ALLOWED_CANONICAL_NOTE_PATTERN = re.compile(
    r"^\s*>?\s*-?\s*Router files under `docs/agent_router/` "
    r"are derived outputs generated from this canonical source\.\s*$",
    re.IGNORECASE,
)
ALLOWED_HEADER_CONTENT_LINES = 30


def iter_markdown_files() -> list[Path]:
    files: list[Path] = []
    for target in CANONICAL_TARGETS:
        if target.is_file() and target.suffix.lower() == ".md":
            if not is_excluded_canonical_path(target):
                files.append(target)
            continue
        if target.is_dir():
            for file_path in sorted(target.rglob("*.md")):
                if not is_excluded_canonical_path(file_path):
                    files.append(file_path)
    return files


def is_excluded_canonical_path(path: Path) -> bool:
    relative = path.relative_to(REPO_ROOT).as_posix()
    normalized = f"/{relative}/"
    return any(excluded in normalized for excluded in EXCLUDED_CANONICAL_SUBPATHS)


def _is_allowed_governance_note(line: str, content_line_number: int) -> bool:
    return (
        content_line_number <= ALLOWED_HEADER_CONTENT_LINES
        and ALLOWED_CANONICAL_NOTE_PATTERN.match(line) is not None
    )


def find_violations_in_text(text: str) -> list[tuple[int, str]]:
    violations: list[tuple[int, str]] = []
    in_frontmatter = False
    frontmatter_consumed = False
    content_line_number = 0

    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()

        if not frontmatter_consumed and line_number == 1 and stripped == "---":
            in_frontmatter = True
            continue

        if in_frontmatter:
            if stripped == "---":
                in_frontmatter = False
                frontmatter_consumed = True
            continue

        content_line_number += 1

        if FORBIDDEN_PATTERN.search(line) and not _is_allowed_governance_note(
            line, content_line_number
        ):
            violations.append((line_number, line.strip()))

    return violations


def find_violations(path: Path) -> list[tuple[int, str]]:
    text = path.read_text(encoding="utf-8")
    violations = find_violations_in_text(text)
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
