from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

BRANCH_RE = re.compile(r"\*\*Branch:\*\*\s*`([^`]+)`")
CHECKBOX_LINE_RE = re.compile(r"^\s*- \[(?P<state>[ xX])]\s*(?P<text>.*)$")
INLINE_CODE_RE = re.compile(r"`[^`]*`")

IN_PROGRESS_LABEL_RE = re.compile(r"(?:^|\s)(?:⏳\s*)?IN PROGRESS(?:\s*\(|\s*$)")
STEP_LOCKED_LABEL_RE = re.compile(r"(?:^|\s)(?:🔒\s*)?STEP LOCKED(?:\s*\(|\s*$)")


class PlanResolutionError(RuntimeError):
    """Raised when active plan resolution is ambiguous."""


def safe_print(message: str) -> None:
    """Print robustly on consoles that cannot encode some Unicode characters."""
    try:
        print(message)
    except UnicodeEncodeError:
        fallback = message.encode("ascii", errors="backslashreplace").decode("ascii")
        print(fallback)


def get_current_branch() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def extract_branch(plan_content: str) -> str | None:
    match = BRANCH_RE.search(plan_content)
    if not match:
        return None
    return match.group(1).strip()


def iter_plan_files(plan_root: Path) -> list[Path]:
    candidates = sorted(plan_root.rglob("PLAN_*.md"))
    return [path for path in candidates if "completed" not in path.parts]


def resolve_active_plan(branch: str, plan_root: Path) -> Path | None:
    matches: list[Path] = []

    for plan_path in iter_plan_files(plan_root):
        content = plan_path.read_text(encoding="utf-8")
        extracted_branch = extract_branch(content)
        if extracted_branch == branch:
            matches.append(plan_path)

    if len(matches) == 0:
        return None

    if len(matches) > 1:
        match_lines = "\n".join(f"- {path.as_posix()}" for path in matches)
        raise PlanResolutionError(
            "Ambiguous active plan resolution for branch "
            f"'{branch}'. Multiple plans match:\n"
            f"{match_lines}\n"
            "Keep exactly one active plan per branch outside completed/."
        )

    return matches[0]


def validate_execution_status(plan_content: str, plan_path: Path) -> list[str]:
    if "## Execution Status" not in plan_content:
        return [f"Plan {plan_path.as_posix()} is missing '## Execution Status' section."]
    return []


def collect_active_labels(plan_content: str) -> tuple[list[str], list[str], list[str], list[str]]:
    in_progress_open: list[str] = []
    step_locked_open: list[str] = []
    active_open: list[str] = []
    active_closed: list[str] = []

    for raw_line in plan_content.splitlines():
        match = CHECKBOX_LINE_RE.match(raw_line)
        if not match:
            continue

        state = match.group("state").lower()
        text = match.group("text")
        # Ignore mentions in inline code snippets and detect label-like tokens only.
        text_without_code = INLINE_CODE_RE.sub("", text)
        has_in_progress = bool(IN_PROGRESS_LABEL_RE.search(text_without_code))
        has_step_locked = bool(STEP_LOCKED_LABEL_RE.search(text_without_code))

        if state == " ":
            if has_in_progress:
                in_progress_open.append(raw_line.strip())
                active_open.append(raw_line.strip())
            if has_step_locked:
                step_locked_open.append(raw_line.strip())
                if raw_line.strip() not in active_open:
                    active_open.append(raw_line.strip())
        elif state == "x" and (has_in_progress or has_step_locked):
            active_closed.append(raw_line.strip())

    return in_progress_open, step_locked_open, active_open, active_closed


def validate_single_active_step(plan_content: str) -> list[str]:
    _, _, active_open, active_closed = collect_active_labels(plan_content)
    errors: list[str] = []

    if len(active_open) > 1:
        listed = "\n".join(f"- {line}" for line in active_open)
        errors.append(
            "Multiple active steps found. At most one step may be IN PROGRESS "
            f"or STEP LOCKED.\n{listed}"
        )

    if active_closed:
        listed_closed = "\n".join(f"- {line}" for line in active_closed)
        errors.append(
            "Closed steps cannot keep active labels (IN PROGRESS/STEP LOCKED). "
            "Remove active labels from closed checkboxes.\n"
            f"{listed_closed}"
        )

    return errors


def validate_no_start_while_locked(plan_content: str) -> list[str]:
    in_progress_open, step_locked_open, _, _ = collect_active_labels(plan_content)
    if in_progress_open and step_locked_open:
        return ["Cannot start step while STEP LOCKED is active. Resolve the locked step first."]
    return []


def run_guard(branch: str, plan_root: Path) -> int:
    try:
        plan_path = resolve_active_plan(branch=branch, plan_root=plan_root)
    except PlanResolutionError as exc:
        safe_print(f"ERROR: {exc}")
        safe_print("plan-execution-guard: FAIL (1 invariant(s) violated)")
        return 1

    if plan_path is None:
        safe_print("plan-execution-guard: PASS")
        return 0

    plan_content = plan_path.read_text(encoding="utf-8")

    errors: list[str] = []
    errors.extend(validate_execution_status(plan_content, plan_path))
    errors.extend(validate_single_active_step(plan_content))
    errors.extend(validate_no_start_while_locked(plan_content))

    if errors:
        for error in errors:
            safe_print(f"ERROR: {error}")
        safe_print(f"plan-execution-guard: FAIL ({len(errors)} invariant(s) violated)")
        return 1

    safe_print("plan-execution-guard: PASS")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate active plan execution invariants.")
    parser.add_argument(
        "--branch",
        default=None,
        help="Target branch. Defaults to current git branch.",
    )
    parser.add_argument(
        "--plan-root",
        default="docs/projects/veterinary-medical-records/04-delivery/plans",
        help="Root folder where PLAN_*.md files are searched.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    branch = args.branch or get_current_branch()
    plan_root = Path(args.plan_root)
    return run_guard(branch=branch, plan_root=plan_root)


if __name__ == "__main__":
    sys.exit(main())
