#!/usr/bin/env python3
"""Fail when canonical docs reference docs/agent_router.*"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Literal

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
PLANNING_META_PATH_HINTS = ("/04-delivery/plans/", "/metrics/", "/tmp/")
ViolationCategory = Literal["operational", "planning/meta-doc"]


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


def _relative_posix(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def categorize_violation(path: Path, line: str) -> ViolationCategory:
    relative = f"/{_relative_posix(path)}/".lower()
    if any(hint in relative for hint in PLANNING_META_PATH_HINTS):
        return "planning/meta-doc"
    if path.name.upper().startswith("PLAN_"):
        return "planning/meta-doc"
    if "plan_" in line.lower():
        return "planning/meta-doc"
    return "operational"


def main() -> int:
    all_violations: list[tuple[Path, int, str]] = []
    for file_path in iter_markdown_files():
        for line_number, line in find_violations(file_path):
            all_violations.append((file_path, line_number, line))

    if not all_violations:
        print("Canonical docs guard passed: no agent_router references found.")
        return 0

    operational: list[tuple[Path, int, str]] = []
    planning_meta: list[tuple[Path, int, str]] = []
    for file_path, line_number, line in all_violations:
        category = categorize_violation(file_path, line)
        if category == "planning/meta-doc":
            planning_meta.append((file_path, line_number, line))
        else:
            operational.append((file_path, line_number, line))

    print("Canonical docs guard: categorized references to docs/agent_router.")
    print(
        f"- operational violations: {len(operational)}"
        f" | planning/meta-doc references: {len(planning_meta)}"
    )

    if operational:
        print(
            "Canonical docs guard failed: found forbidden operational references to "
            "docs/agent_router in canonical docs."
        )
        print(
            "Fix: remove agent_router mentions from docs/README.md, "
            "docs/projects/veterinary-medical-records/**, docs/shared/**."
        )
        for file_path, line_number, line in operational:
            print(f"- operational | {_relative_posix(file_path)}:{line_number}: {line}")

    if planning_meta:
        print(
            "Planning/meta-doc references detected (non-blocking): review allowlists "
            "or exclusions if these appear outside intended planning artifacts."
        )
        for file_path, line_number, line in planning_meta:
            print(f"- planning/meta-doc | {_relative_posix(file_path)}:{line_number}: {line}")

    return 1 if operational else 0


if __name__ == "__main__":
    sys.exit(main())
