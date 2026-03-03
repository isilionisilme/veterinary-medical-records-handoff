from __future__ import annotations

import fnmatch
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_cmd(command: list[str], description: str) -> None:
    print(f"\n==> {description}")
    print("$ " + " ".join(command))
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def git_output(args: list[str]) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def pick_base_ref() -> str:
    upstream = git_output(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    if upstream:
        return upstream
    origin_main = git_output(["show-ref", "--verify", "refs/remotes/origin/main"])
    if origin_main:
        return "origin/main"
    return "HEAD~1"


def changed_files(base_ref: str) -> list[str]:
    output = git_output(["diff", "--name-only", f"{base_ref}...HEAD"])
    if not output:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def matches_any(path: str, patterns: list[str]) -> bool:
    normalized = path.replace("\\", "/")
    for pattern in patterns:
        if fnmatch.fnmatch(normalized, pattern):
            return True
    return False


def main() -> int:
    base_ref = pick_base_ref()
    files = changed_files(base_ref)
    print(f"pre-push quality gate: base_ref={base_ref}")

    if not files:
        print("No changed files detected against base. Running minimal gate (backend unit tests).")
        run_cmd(
            [sys.executable, "-m", "pytest", "backend/tests/unit", "-q", "-o", "addopts="],
            "Backend unit tests",
        )
        return 0

    backend_patterns = [
        "backend/**",
        "pyproject.toml",
        "pytest.ini",
        "requirements*.txt",
    ]
    frontend_patterns = [
        "frontend/**",
    ]
    docs_patterns = [
        "docs/**",
        "*.md",
        "scripts/docs/check_docs_links.mjs",
        "scripts/docs/check_doc_*.py",
        "scripts/docs/check_no_canonical_router_refs.py",
    ]

    backend_changed = any(matches_any(path, backend_patterns) for path in files)
    frontend_changed = any(matches_any(path, frontend_patterns) for path in files)
    docs_changed = any(matches_any(path, docs_patterns) for path in files)

    print("Changed files:")
    for file_path in files:
        print(f" - {file_path}")

    if backend_changed:
        run_cmd(
            [sys.executable, "-m", "pytest", "backend/tests/unit", "-q", "-o", "addopts="],
            "Backend unit tests",
        )

    if frontend_changed:
        run_cmd(["npm", "--prefix", "frontend", "run", "lint"], "Frontend lint + typecheck")
        run_cmd(["npm", "--prefix", "frontend", "run", "test"], "Frontend unit tests")

    if docs_changed:
        run_cmd(["npm", "run", "docs:lint"], "Docs markdown lint")
        run_cmd(["npm", "run", "docs:format:check"], "Docs format check")

    if not (backend_changed or frontend_changed or docs_changed):
        print("No scoped gate triggered by changed paths; skipping checks.")

    print("\npre-push quality gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
