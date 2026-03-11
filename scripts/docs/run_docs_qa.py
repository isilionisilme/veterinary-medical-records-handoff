#!/usr/bin/env python3
"""Run docs QA checks with PR base awareness.

This keeps local preflight and GitHub Actions aligned by running markdown
lint/format checks only for changed canonical docs, while preserving link and
frontmatter guards.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath

CANONICAL_GLOBS = (
    "docs/README.md",
    "docs/shared/**/*.md",
    "docs/projects/veterinary-medical-records/01-product/**/*.md",
    "docs/projects/veterinary-medical-records/02-tech/**/*.md",
    "docs/projects/veterinary-medical-records/03-ops/**/*.md",
    "docs/projects/veterinary-medical-records/04-delivery/*.md",
    "docs/projects/veterinary-medical-records/onboarding/**/*.md",
)


def _run(cmd: list[str]) -> None:
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def _resolve_cmd(command: str) -> str:
    candidates = [command]
    if sys.platform.startswith("win"):
        candidates.insert(0, f"{command}.cmd")

    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved

    raise FileNotFoundError(f"Unable to find required command on PATH: {command}")


def _changed_files(base_ref: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    files = [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]
    return sorted(set(files))


def _is_canonical_doc(path: str) -> bool:
    if not path.endswith(".md"):
        return False
    posix_path = PurePosixPath(path)
    return any(posix_path.match(pattern) for pattern in CANONICAL_GLOBS)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run docs QA checks against PR base")
    parser.add_argument("--base-ref", required=True, help="Git base ref or SHA for diff")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    try:
        changed = _changed_files(args.base_ref)
    except subprocess.CalledProcessError as exc:
        print(
            f"Unable to resolve changed files from base ref '{args.base_ref}': {exc}",
            file=sys.stderr,
        )
        return exc.returncode or 1

    changed_canonical_docs = [path for path in changed if _is_canonical_doc(path)]
    npx = _resolve_cmd("npx")
    node = _resolve_cmd("node")

    print("Changed canonical docs:")
    if changed_canonical_docs:
        for path in changed_canonical_docs:
            print(f" - {path}")
    else:
        print(" - none")
        print("Skipping docs QA checks (no canonical markdown changes).")
        print("Docs QA checks: PASS")
        return 0

    try:
        _run([npx, "markdownlint-cli2", *changed_canonical_docs])
        _run([npx, "prettier", "--check", *changed_canonical_docs])

        _run(
            [
                node,
                str(repo_root / "scripts/docs/check_docs_links.mjs"),
                "--base-ref",
                args.base_ref,
            ]
        )
        _run(
            [
                sys.executable,
                str(repo_root / "scripts/quality/validate-frontmatter.py"),
                "--paths",
                *changed_canonical_docs,
            ]
        )
    except subprocess.CalledProcessError as exc:
        return exc.returncode or 1

    print("Docs QA checks: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
