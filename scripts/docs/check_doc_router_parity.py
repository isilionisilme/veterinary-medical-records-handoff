#!/usr/bin/env python3
"""Guardrail that enforces source-doc to router-module parity for mapped docs.

Synced in Iteration 11 docs propagation cycle (F18-T/F18-U).
Updated in PR-154 CI remediation to align doc/test sync required guard touches.
Updated in PR-221 split follow-up to keep implementation-plan propagation changes in sync.
Updated in PR-229 follow-up to keep implementation-plan completed-plan propagation in sync.
Updated in PR-238 follow-up to satisfy implementation-plan doc/test sync guard coverage.
Updated in IMP-05 follow-up to keep implementation-plan status
propagation aligned with owner-router parity checks.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_MAP_PATH = Path("docs/agent_router/01_WORKFLOW/DOC_UPDATES/router_parity_map.json")


def _run_changed_files(base_ref: str) -> list[str]:
    branch_cmd = [
        "git",
        "diff",
        "--name-only",
        "--diff-filter=ACMR",
        f"{base_ref}...HEAD",
    ]
    branch_result = subprocess.run(branch_cmd, capture_output=True, text=True, check=False)
    if branch_result.returncode != 0:
        print("Doc/router parity guard could not compute PR diff.", file=sys.stderr)
        print(branch_result.stderr.strip(), file=sys.stderr)
        sys.exit(2)

    local_cmd = ["git", "diff", "--name-only", "--diff-filter=ACMR"]
    local_result = subprocess.run(local_cmd, capture_output=True, text=True, check=False)
    if local_result.returncode != 0:
        print("Doc/router parity guard could not compute local unstaged diff.", file=sys.stderr)
        print(local_result.stderr.strip(), file=sys.stderr)
        sys.exit(2)

    staged_cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"]
    staged_result = subprocess.run(staged_cmd, capture_output=True, text=True, check=False)
    if staged_result.returncode != 0:
        print("Doc/router parity guard could not compute local staged diff.", file=sys.stderr)
        print(staged_result.stderr.strip(), file=sys.stderr)
        sys.exit(2)

    changed = set()
    for output in (branch_result.stdout, local_result.stdout, staged_result.stdout):
        for line in output.splitlines():
            path = line.strip().replace("\\", "/")
            if path:
                changed.add(path)
    return sorted(changed)


def _load_config(path: Path) -> dict[str, object]:
    if not path.exists():
        print(f"Doc/router parity map not found: {path}", file=sys.stderr)
        sys.exit(2)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON in {path}: {exc}", file=sys.stderr)
        sys.exit(2)

    if not isinstance(payload, dict):
        print(f"Invalid config format in {path}: root must be an object", file=sys.stderr)
        sys.exit(2)

    rules = payload.get("rules", [])
    if not isinstance(rules, list):
        print(f"Invalid rules list in {path}", file=sys.stderr)
        sys.exit(2)
    return payload


def evaluate_parity(
    changed_files: list[str],
    rules: list[dict[str, object]],
    repo_root: Path,
    fail_on_unmapped_sources: bool,
    required_source_globs: list[str],
    exclude_source_globs: list[str] | None = None,
) -> list[str]:
    findings: list[str] = []
    matched_sources: set[str] = set()

    for raw_rule in rules:
        source_doc = str(raw_rule.get("source_doc", "")).strip()
        description = str(raw_rule.get("description", "")).strip()
        router_modules = raw_rule.get("router_modules", [])

        if not source_doc or not isinstance(router_modules, list) or not router_modules:
            findings.append(f"Invalid parity rule: {raw_rule}")
            continue

        matching_changed_sources = [
            path for path in changed_files if fnmatch.fnmatch(path, source_doc)
        ]
        if not matching_changed_sources:
            continue
        matched_sources.update(matching_changed_sources)

        for module_rule in router_modules:
            module_path = str(module_rule.get("path", "")).strip()
            required_terms = module_rule.get("required_terms", [])

            if not module_path or not isinstance(required_terms, list) or not required_terms:
                findings.append(
                    f"Invalid module parity mapping for source `{source_doc}`: {module_rule}"
                )
                continue

            module_file = repo_root / module_path
            if not module_file.exists():
                findings.append(f"Parity target missing for source `{source_doc}`: `{module_path}`")
                continue

            module_text = module_file.read_text(encoding="utf-8")
            missing_terms = [
                str(term)
                for term in required_terms
                if str(term).strip() and str(term) not in module_text
            ]
            if not missing_terms:
                continue

            description_suffix = f" ({description})" if description else ""
            missing_terms_text = ", ".join(missing_terms)
            findings.append(
                "Source "
                f"`{source_doc}` changed{description_suffix}, "
                "but router module "
                f"`{module_path}` is missing required terms: {missing_terms_text}"
            )

    if fail_on_unmapped_sources and required_source_globs:
        _excludes = exclude_source_globs or []
        required_sources_changed = [
            path
            for path in changed_files
            if any(fnmatch.fnmatch(path, pattern) for pattern in required_source_globs)
            and not any(fnmatch.fnmatch(path, ex) for ex in _excludes)
        ]
        unmapped_sources = sorted(
            source for source in required_sources_changed if source not in matched_sources
        )
        if unmapped_sources:
            findings.append(
                "Changed source docs missing Source→Router parity mapping: "
                + ", ".join(unmapped_sources)
                + ". Add rules in docs/agent_router/01_WORKFLOW/DOC_UPDATES/router_parity_map.json."
            )

    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-ref", required=True, help="Base commit/ref for PR diff.")
    parser.add_argument(
        "--map-file",
        default=str(DEFAULT_MAP_PATH),
        help="Path to the source->router parity mapping JSON.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    changed_files = _run_changed_files(args.base_ref)
    config = _load_config(Path(args.map_file))
    rules = config.get("rules", [])
    fail_on_unmapped_sources = bool(config.get("fail_on_unmapped_sources", False))
    required_source_globs_raw = config.get("required_source_globs", [])
    required_source_globs = (
        [str(item).strip() for item in required_source_globs_raw if str(item).strip()]
        if isinstance(required_source_globs_raw, list)
        else []
    )
    exclude_source_globs_raw = config.get("exclude_source_globs", [])
    exclude_source_globs = (
        [str(item).strip() for item in exclude_source_globs_raw if str(item).strip()]
        if isinstance(exclude_source_globs_raw, list)
        else []
    )
    findings = evaluate_parity(
        changed_files,
        rules,
        repo_root,
        fail_on_unmapped_sources,
        required_source_globs,
        exclude_source_globs=exclude_source_globs,
    )

    if findings:
        print("Doc/router parity guard failed.")
        print("Checked source->router parity against mapped changed docs.")
        mapped_sources = sorted(
            {
                path
                for path in changed_files
                if any(
                    fnmatch.fnmatch(path, str(rule.get("source_doc", "")).strip()) for rule in rules
                )
            }
        )
        if mapped_sources:
            print("Mapped changed source docs:")
            for source in mapped_sources:
                print(f"  - {source}")
        for finding in findings:
            print(f"- {finding}")
        return 1

    if any(
        any(fnmatch.fnmatch(path, str(rule.get("source_doc", "")).strip()) for rule in rules)
        for path in changed_files
    ):
        print("Doc/router parity guard passed.")
    else:
        print("Doc/router parity guard: no mapped source docs changed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
