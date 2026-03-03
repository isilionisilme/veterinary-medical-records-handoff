#!/usr/bin/env python3
"""Brand guard for frontend PR changes.

Checks only added lines in frontend files to keep noise low:
- Hex colors must belong to the approved brand palette.
- Added font-family lines must include Inter.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ALLOWED_HEX = {
    "#fc4e1b",  # Barkibu orange accent
    "#2fb3a3",  # Legacy primary accent
    "#ebf5ff",  # Page background
    "#ffffff",  # Card/surface background
    "#f7f9fa",  # Legacy secondary background
    "#1f2933",  # Primary text
    "#6b7280",  # Secondary text
    "#9ca3af",  # Muted text
    "#e5e7eb",  # Borders
    "#eef1f4",  # Subtle separators
    "#f2f5f8",  # Recovered surface-muted baseline
    "#cfd8e3",  # Recovered subtle border baseline
    "#4b5563",  # Recovered secondary text baseline
    "#d7dee7",  # Recovered border baseline
    "#e5603d",  # Recovered accent baseline
    "#3f9e86",  # Recovered success baseline
    "#c99645",  # Recovered warning baseline
    "#c45f5c",  # Recovered error baseline
    "#e7f4ef",  # Recovered success surface baseline
    "#f3f6f9",  # Recovered info surface baseline
    "#f9eceb",  # Recovered error surface baseline
    "#4caf93",  # Success
    "#e6b566",  # Warning
    "#d16d6a",  # Error
}

HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")
FONT_FAMILY_RE = re.compile(r"font-family\s*:", re.IGNORECASE)
INTER_RE = re.compile(r"\binter\b", re.IGNORECASE)


def _run_git_diff(base_ref: str) -> list[str]:
    cmd = [
        "git",
        "diff",
        "--unified=0",
        "--no-color",
        f"{base_ref}...HEAD",
        "--",
        "frontend",
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        print("Brand guard could not compute PR diff.", file=sys.stderr)
        print(result.stderr.strip(), file=sys.stderr)
        sys.exit(2)

    replacement_char = "\ufffd"
    if replacement_char in result.stdout or replacement_char in result.stderr:
        print(
            "Brand guard could not decode git diff output as UTF-8 without replacement characters.",
            file=sys.stderr,
        )
        print(
            "Ensure git diff content is UTF-8 compatible before running the guard.",
            file=sys.stderr,
        )
        sys.exit(2)

    return result.stdout.splitlines()


def _normalize_hex(hex_token: str) -> str:
    token = hex_token.lower()
    if len(token) == 4:
        return f"#{token[1] * 2}{token[2] * 2}{token[3] * 2}"
    return token


def _should_scan(path: str) -> bool:
    p = Path(path)
    normalized = p.as_posix()
    if not normalized.startswith("frontend/"):
        return False
    return p.suffix.lower() in {".css", ".scss", ".ts", ".tsx", ".js", ".jsx", ".html"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-ref", required=True, help="Base commit/ref for PR diff.")
    args = parser.parse_args()

    lines = _run_git_diff(args.base_ref)
    current_file = ""
    findings: list[str] = []
    scanned_added_lines = 0

    for line in lines:
        if line.startswith("+++ b/"):
            current_file = line[len("+++ b/") :]
            continue
        if not current_file or not _should_scan(current_file):
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue

        scanned_added_lines += 1
        added = line[1:]

        if FONT_FAMILY_RE.search(added) and not INTER_RE.search(added):
            findings.append(f"{current_file}: added font-family without Inter -> `{added.strip()}`")

        for token in HEX_RE.findall(added):
            normalized = _normalize_hex(token)
            if normalized not in ALLOWED_HEX:
                findings.append(
                    f"{current_file}: non-brand color `{token}` (normalized {normalized})"
                )

    if scanned_added_lines == 0:
        print("Brand guard: no added frontend lines to validate.")
        return 0

    if findings:
        print("Brand guard failed.")
        print(
            "Found frontend changes that do not match docs/shared/01-product/brand-guidelines.md:"
        )
        for item in findings:
            print(f"- {item}")
        return 1

    print("Brand guard passed for added frontend lines.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
