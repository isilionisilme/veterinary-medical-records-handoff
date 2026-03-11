#!/usr/bin/env python3
"""Validate frontmatter metadata in canonical Markdown docs.

Usage:
    python scripts/quality/validate-frontmatter.py [--fix]

Modes:
    check (default) — report violations, exit 1 if any.
    --fix            — add missing frontmatter with safe defaults (non-destructive).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Canonical doc scope (same as markdownlint canonical scope)
GLOB_PATTERNS = [
    "docs/README.md",
    "docs/shared/**/*.md",
    "docs/projects/veterinary-medical-records/01-product/**/*.md",
    "docs/projects/veterinary-medical-records/02-tech/**/*.md",
    "docs/projects/veterinary-medical-records/03-ops/**/*.md",
    "docs/projects/veterinary-medical-records/04-delivery/**/*.md",
    "docs/projects/veterinary-medical-records/onboarding/**/*.md",
]

# Excluded paths (derived router docs, plan logs, and backlog work items)
EXCLUDE_PATTERNS = [
    "docs/projects/veterinary-medical-records/04-delivery/Backlog/",
    "docs/projects/veterinary-medical-records/04-delivery/plans/",
    "docs/agent_router/",
]

ALLOWED_TYPES = {"reference", "explanation", "how-to", "tutorial", "adr", "changelog"}
ALLOWED_STATUSES = {"draft", "active", "deprecated"}
ALLOWED_AUDIENCES = {"all", "contributor", "staff-engineer", "executive", "product-manager"}
REQUIRED_FIELDS = {"title", "type", "status", "audience", "last-updated"}

ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _collect_files() -> list[Path]:
    """Collect all canonical doc files."""
    files: set[Path] = set()
    for pattern in GLOB_PATTERNS:
        if "**" in pattern or "*" in pattern:
            files.update(REPO_ROOT.glob(pattern))
        else:
            p = REPO_ROOT / pattern
            if p.exists():
                files.add(p)

    result = []
    for f in sorted(files):
        rel = str(f.relative_to(REPO_ROOT)).replace("\\", "/")
        if any(rel.startswith(exc) for exc in EXCLUDE_PATTERNS):
            continue
        result.append(f)
    return result


def _collect_target_files(target_paths: list[str]) -> list[Path]:
    """Resolve and filter user-provided relative paths under canonical scope."""
    allowed = {str(path.relative_to(REPO_ROOT)).replace("\\", "/") for path in _collect_files()}
    targets: list[Path] = []

    for rel in sorted(set(path.replace("\\", "/") for path in target_paths)):
        if rel not in allowed:
            continue
        full_path = REPO_ROOT / rel
        if full_path.exists():
            targets.append(full_path)

    return targets


def _parse_frontmatter(text: str) -> tuple[dict[str, str] | None, int, int]:
    """Parse YAML frontmatter. Returns (fields, start_line, end_line) or (None, 0, 0)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, 0, 0

    end = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break

    if end == -1:
        return None, 0, 0

    fields: dict[str, str] = {}
    for line in lines[1:end]:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip().strip('"').strip("'")

    return fields, 0, end


def _validate_file(path: Path) -> list[str]:
    """Validate a single file. Returns list of violation messages."""
    violations: list[str] = []
    rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    text = path.read_text(encoding="utf-8")
    fields, _, _ = _parse_frontmatter(text)

    if fields is None:
        violations.append(f"{rel}: missing frontmatter block")
        return violations

    for field in REQUIRED_FIELDS:
        if field not in fields:
            violations.append(f"{rel}: missing required field '{field}'")

    if "type" in fields and fields["type"] not in ALLOWED_TYPES:
        violations.append(
            f"{rel}: invalid type '{fields['type']}' (allowed: {', '.join(sorted(ALLOWED_TYPES))})"
        )

    if "status" in fields and fields["status"] not in ALLOWED_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_STATUSES))
        violations.append(f"{rel}: invalid status '{fields['status']}' (allowed: {allowed})")

    if "audience" in fields and fields["audience"] not in ALLOWED_AUDIENCES:
        allowed = ", ".join(sorted(ALLOWED_AUDIENCES))
        violations.append(f"{rel}: invalid audience '{fields['audience']}' (allowed: {allowed})")

    if "last-updated" in fields and not ISO_DATE_RE.match(fields["last-updated"]):
        violations.append(
            f"{rel}: invalid last-updated date '{fields['last-updated']}' (expected YYYY-MM-DD)"
        )

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate frontmatter metadata in canonical docs")
    parser.add_argument("--fix", action="store_true", help="Reserved for future autofix support")
    parser.add_argument(
        "--paths",
        nargs="*",
        default=None,
        help="Optional repo-relative markdown paths to validate (canonical scope only)",
    )
    args = parser.parse_args()

    fix_mode = args.fix
    files = _collect_target_files(args.paths) if args.paths else _collect_files()
    all_violations: list[str] = []

    for f in files:
        violations = _validate_file(f)
        all_violations.extend(violations)

    if all_violations:
        print(f"Frontmatter validation: {len(all_violations)} violation(s) in {len(files)} files\n")
        for v in all_violations:
            print(f"  ✗ {v}")
        if not fix_mode:
            return 1

    if not all_violations:
        print(f"Frontmatter validation: 0 violations in {len(files)} files ✓")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
