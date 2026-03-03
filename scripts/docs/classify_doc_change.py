#!/usr/bin/env python3
"""Classify changed docs as Rule, Clarification, or Navigation."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

OUTPUT_PATH = Path("doc_change_classification.json")

RULE_SIGNALS = re.compile(
    r"\b("
    r"MUST|SHALL|REQUIRED|SHOULD NOT|MUST NOT|threshold|policy|"
    r"mandatory|hard rule|fail-closed"
    r")\b",
    re.IGNORECASE,
)
NAV_PATTERNS = re.compile(
    r"^\s*(\[[^\]]+\]\([^)]+\)|#{1,6}\s+.+|-\s*\[[^\]]+\].*|(?:from\s+\S+\s+)?import\s+.+|export\s+.+)\s*$",
    re.IGNORECASE,
)


def _run_git(cmd: list[str], error_prefix: str) -> str:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{error_prefix}: {result.stderr.strip()}")
    return result.stdout


def _changed_markdown_files(base_ref: str) -> list[str]:
    commands = [
        [
            "git",
            "diff",
            "--name-only",
            "--diff-filter=ACMR",
            f"{base_ref}...HEAD",
        ],
        ["git", "diff", "--name-only", "--diff-filter=ACMR"],
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
    ]
    changed: set[str] = set()
    for cmd in commands:
        output = _run_git(cmd, "Could not compute changed files")
        for line in output.splitlines():
            path = line.strip().replace("\\", "/")
            if path.startswith("docs/") and path.endswith(".md"):
                changed.add(path)
    return sorted(changed)


def _commit_tag_override(base_ref: str) -> str | None:
    log_text = _run_git(
        ["git", "log", "--format=%B", f"{base_ref}..HEAD"],
        "Could not read commit messages",
    )
    text = log_text.lower()
    if "[doc:rule]" in text:
        return "Rule"
    if "[doc:nav]" in text:
        return "Navigation"
    if "[doc:clar]" in text:
        return "Clarification"
    return None


def _changed_added_lines(base_ref: str, path: str) -> list[str]:
    output = _run_git(
        ["git", "diff", "--no-color", "--unified=0", f"{base_ref}...HEAD", "--", path],
        f"Could not compute diff for {path}",
    )
    lines: list[str] = []
    for raw_line in output.splitlines():
        if raw_line.startswith("+++"):
            continue
        if raw_line.startswith("+"):
            lines.append(raw_line[1:])
    return lines


def _classify_file(base_ref: str, path: str) -> str:
    changed_lines = _changed_added_lines(base_ref, path)
    if any(RULE_SIGNALS.search(line) for line in changed_lines):
        return "Rule"
    if changed_lines and all(NAV_PATTERNS.match(line) for line in changed_lines):
        return "Navigation"
    return "Clarification"


def _overall_classification(values: list[str]) -> str:
    if "Rule" in values:
        return "Rule"
    if "Clarification" in values:
        return "Clarification"
    return "Navigation"


def _write_output(payload: dict[str, object]) -> None:
    OUTPUT_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-ref", required=True, help="Base commit/ref for PR diff.")
    args = parser.parse_args()

    try:
        changed_docs = _changed_markdown_files(args.base_ref)
        if not changed_docs:
            raise RuntimeError("No changed docs found.")

        override = _commit_tag_override(args.base_ref)
        if override:
            files = {path: override for path in changed_docs}
            overall = override
        else:
            files = {path: _classify_file(args.base_ref, path) for path in changed_docs}
            overall = _overall_classification(list(files.values()))

        _write_output({"files": files, "overall": overall})
        print(f"Doc change classification written to {OUTPUT_PATH}. overall={overall}")
        return 0
    except Exception as exc:  # noqa: BLE001 - fail-closed by design
        payload = {"files": {}, "overall": "Rule"}
        _write_output(payload)
        print(
            f"Doc change classifier fail-closed to Rule due to error: {exc}",
            file=sys.stderr,
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
