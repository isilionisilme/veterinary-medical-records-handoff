from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
EXCLUDED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__"}
ALLOWED_INCLUDE_PREFIXES = ("-r", "--requirement", "-c", "--constraint")
ALLOWED_OPTION_PREFIXES = (
    "--index-url",
    "--extra-index-url",
    "--trusted-host",
    "--find-links",
    "--no-binary",
    "--only-binary",
)
DISALLOWED_SPECIFIERS = ("~=", "!=", "<=", ">=", "<", ">", "===")
URL_PREFIXES = ("http://", "https://", "git+", "svn+", "hg+", "bzr+", "ftp://", "file://")


def _iter_requirement_files() -> list[Path]:
    files: list[Path] = []
    patterns = ("*requirements*.txt", "constraints*.txt")
    for pattern in patterns:
        for path in REPO_ROOT.rglob(pattern):
            if path.is_dir():
                continue
            if any(part in EXCLUDED_DIRS for part in path.parts):
                continue
            files.append(path)
    return sorted(set(files))


def _strip_inline_comment(line: str) -> str:
    return re.split(r"\s+#", line, maxsplit=1)[0].strip()


def _is_include_directive(line: str) -> bool:
    lowered = line.lower()
    for prefix in ALLOWED_INCLUDE_PREFIXES:
        if (
            lowered == prefix
            or lowered.startswith(prefix + " ")
            or lowered.startswith(prefix + "=")
        ):
            return True
    return False


def _is_allowed_option_line(line: str) -> bool:
    lowered = line.lower()
    for prefix in ALLOWED_OPTION_PREFIXES:
        if (
            lowered == prefix
            or lowered.startswith(prefix + " ")
            or lowered.startswith(prefix + "=")
        ):
            return True
    return False


def _find_violation(line: str) -> str | None:
    lowered = line.lower()
    if lowered.startswith("-e ") or lowered.startswith("--editable ") or lowered == "-e":
        return "editable install is not allowed"
    if lowered.startswith(URL_PREFIXES):
        return "direct URL install is not allowed"
    if " @ " in line and any(scheme in lowered for scheme in URL_PREFIXES):
        return "direct URL install is not allowed"
    if "==" not in line:
        return "dependency is not pinned with =="
    for specifier in DISALLOWED_SPECIFIERS:
        if specifier in line:
            return f"specifier '{specifier}' is not allowed; use exact pins with =="
    return None


def test_requirement_files_use_exact_pins_only() -> None:
    requirement_files = _iter_requirement_files()
    if not requirement_files:
        pytest.skip("No requirement/constraint files found to validate.")

    violations: list[str] = []
    for file_path in requirement_files:
        relative_path = file_path.relative_to(REPO_ROOT)
        lines = file_path.read_text(encoding="utf-8").splitlines()
        for line_number, raw_line in enumerate(lines, start=1):
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            candidate = _strip_inline_comment(stripped)
            if not candidate or candidate.startswith("#"):
                continue
            if _is_include_directive(candidate):
                continue
            if _is_allowed_option_line(candidate):
                continue
            reason = _find_violation(candidate)
            if reason:
                violations.append(f"{relative_path}:{line_number} -> {candidate} ({reason})")

    assert not violations, (
        "Requirements pinning guard failed.\n"
        "Use exact pins with == for every dependency line; only -r/--requirement and "
        "-c/--constraint include directives are allowed.\n" + "\n".join(violations)
    )
