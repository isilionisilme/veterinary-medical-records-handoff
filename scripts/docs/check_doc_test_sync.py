#!/usr/bin/env python3
"""Guardrail that enforces doc/test synchronization for mapped docs.

Synced in Iteration 11 CI remediation to track router-module propagation edits.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_MAP_PATH = Path("docs/agent_router/01_WORKFLOW/DOC_UPDATES/test_impact_map.json")


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
        print("Doc/test sync guard could not compute PR diff.", file=sys.stderr)
        print(branch_result.stderr.strip(), file=sys.stderr)
        sys.exit(2)

    local_cmd = ["git", "diff", "--name-only", "--diff-filter=ACMR"]
    local_result = subprocess.run(local_cmd, capture_output=True, text=True, check=False)
    if local_result.returncode != 0:
        print("Doc/test sync guard could not compute local unstaged diff.", file=sys.stderr)
        print(local_result.stderr.strip(), file=sys.stderr)
        sys.exit(2)

    staged_cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"]
    staged_result = subprocess.run(staged_cmd, capture_output=True, text=True, check=False)
    if staged_result.returncode != 0:
        print("Doc/test sync guard could not compute local staged diff.", file=sys.stderr)
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
        print(f"Doc/test sync guard config not found: {path}", file=sys.stderr)
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


def _matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def evaluate_sync(
    changed_files: list[str],
    rules: list[dict[str, object]],
    fail_on_unmapped_docs: bool,
    required_doc_globs: list[str] | None = None,
    exclude_doc_globs: list[str] | None = None,
) -> list[str]:
    changed_docs = [
        path for path in changed_files if path.startswith("docs/") and path.endswith(".md")
    ]
    findings: list[str] = []

    if not changed_docs:
        return findings

    valid_rules: list[dict[str, object]] = []
    normalized_required_globs = [
        pattern.strip()
        for pattern in (required_doc_globs or [])
        if isinstance(pattern, str) and pattern.strip()
    ]

    _excludes = exclude_doc_globs or []
    if fail_on_unmapped_docs and normalized_required_globs:
        scoped_docs = [
            doc
            for doc in changed_docs
            if _matches_any(doc, normalized_required_globs) and not _matches_any(doc, _excludes)
        ]
    else:
        scoped_docs = []
    relaxed_mode = os.environ.get("DOC_SYNC_RELAXED") == "1"

    mapped_scoped_docs: set[str] = set()
    for raw_rule in rules:
        doc_glob = str(raw_rule.get("doc_glob", "")).strip()
        if not doc_glob:
            findings.append(f"Invalid mapping rule: {raw_rule}")
            continue

        required_any = raw_rule.get("required_any", [])
        owner_any = raw_rule.get("owner_any", [])
        if not isinstance(required_any, list) or not isinstance(owner_any, list):
            findings.append(f"Invalid mapping rule: {raw_rule}")
            continue

        required_patterns = [str(item).strip() for item in required_any if str(item).strip()]
        owner_patterns = [str(item).strip() for item in owner_any if str(item).strip()]
        valid_rules.append(
            {
                "doc_glob": doc_glob,
                "required_patterns": required_patterns,
                "owner_patterns": owner_patterns,
                "description": str(raw_rule.get("description", "")).strip(),
            }
        )

    doc_to_rules: dict[str, list[dict[str, object]]] = {doc: [] for doc in changed_docs}
    for rule in valid_rules:
        doc_glob = str(rule["doc_glob"])
        matched_docs = [doc for doc in changed_docs if fnmatch.fnmatch(doc, doc_glob)]
        for doc in matched_docs:
            doc_to_rules[doc].append(rule)
            if doc in scoped_docs:
                mapped_scoped_docs.add(doc)

    if fail_on_unmapped_docs:
        if normalized_required_globs:
            unmapped_docs = [doc for doc in scoped_docs if doc not in mapped_scoped_docs]
        else:
            unmapped_docs = [doc for doc, matched in doc_to_rules.items() if not matched]
        if unmapped_docs:
            if normalized_required_globs:
                findings.append(
                    "Changed docs in required source scope are not mapped in test_impact_map.json: "
                    + ", ".join(sorted(unmapped_docs))
                )
            else:
                findings.append(
                    "Changed docs with no mapping coverage: "
                    + ", ".join(sorted(unmapped_docs))
                    + ". Add/adjust mapping rules in "
                    + "docs/agent_router/01_WORKFLOW/DOC_UPDATES/test_impact_map.json."
                )

    for doc, matched_rules in doc_to_rules.items():
        for rule in matched_rules:
            required_patterns = list(rule["required_patterns"])
            owner_patterns = list(rule["owner_patterns"])
            description = str(rule["description"])
            doc_glob = str(rule["doc_glob"])
            description_suffix = f" ({description})" if description else ""

            if (
                not relaxed_mode
                and required_patterns
                and not _matches_any_from_files(changed_files, required_patterns)
            ):
                findings.append(
                    f"Doc `{doc}` matched `{doc_glob}`{description_suffix}, "
                    "but none of the related tests/guards changed: "
                    f"{', '.join(required_patterns)}"
                )

            if owner_patterns and not _matches_any_from_files(changed_files, owner_patterns):
                findings.append(
                    f"Doc `{doc}` matched `{doc_glob}`{description_suffix}, "
                    "but no owner propagation file changed. Expected one of: "
                    f"{', '.join(owner_patterns)}"
                )
    return findings


def _matches_any_from_files(changed_files: list[str], patterns: list[str]) -> bool:
    return any(_matches_any(path, patterns) for path in changed_files)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-ref", required=True, help="Base commit/ref for PR diff.")
    parser.add_argument(
        "--map-file",
        default=str(DEFAULT_MAP_PATH),
        help="Path to the doc->test impact mapping JSON.",
    )
    args = parser.parse_args()

    changed_files = _run_changed_files(args.base_ref)
    config = _load_config(Path(args.map_file))
    rules = config.get("rules", [])
    fail_on_unmapped_docs = bool(config.get("fail_on_unmapped_docs", False))
    required_doc_globs_raw = config.get("required_doc_globs", [])
    if required_doc_globs_raw is None:
        required_doc_globs_raw = []
    if not isinstance(required_doc_globs_raw, list):
        print(
            f"Invalid required_doc_globs list in {args.map_file}",
            file=sys.stderr,
        )
        return 2

    classification_path = Path("doc_change_classification.json")
    if classification_path.exists():
        try:
            classification = json.loads(classification_path.read_text(encoding="utf-8"))
            overall = classification.get("overall", "Rule")
        except (json.JSONDecodeError, KeyError):
            overall = "Rule"

        if overall == "Navigation":
            print("Doc/test sync guard: Navigation-only changes detected. Skipping.")
            return 0

        if overall == "Clarification":
            os.environ["DOC_SYNC_RELAXED"] = "1"

    required_doc_globs = [str(item).strip() for item in required_doc_globs_raw if str(item).strip()]
    exclude_doc_globs_raw = config.get("exclude_doc_globs", [])
    exclude_doc_globs = (
        [str(item).strip() for item in exclude_doc_globs_raw if str(item).strip()]
        if isinstance(exclude_doc_globs_raw, list)
        else []
    )
    findings = evaluate_sync(
        changed_files,
        rules,
        fail_on_unmapped_docs,
        required_doc_globs=required_doc_globs,
        exclude_doc_globs=exclude_doc_globs,
    )
    changed_docs = [
        path for path in changed_files if path.startswith("docs/") and path.endswith(".md")
    ]

    if findings:
        print("Doc/test sync guard failed.")
        if changed_docs:
            print(f"Changed docs inspected: {len(changed_docs)}")
        print("Documentation changed without related test/guard updates:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    if changed_docs:
        print("Doc/test sync guard passed.")
    else:
        print("Doc/test sync guard: no markdown docs changed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
