from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")


def _git_show_text(repo_root: Path, commit_sha: str, doc_path: str) -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "show", f"{commit_sha}:{doc_path}"],
            cwd=repo_root,
            text=True,
            encoding="utf-8",
            errors="replace",
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return None
    return out


def _parse_date_utc(value: str) -> None:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    datetime.fromisoformat(value)


def _load_scenarios(scenarios_path: Path) -> set[str]:
    text = scenarios_path.read_text(encoding="utf-8")
    scenario_ids: set[str] = set()
    for line in text.splitlines():
        if line.startswith("## "):
            scenario_id = line[3:].strip()
            if scenario_id:
                scenario_ids.add(scenario_id)
    return scenario_ids


def _assert_nonneg_int(value: object, field: str) -> int:
    if not isinstance(value, int):
        raise ValueError(f"{field} must be an int.")
    if value < 0:
        raise ValueError(f"{field} must be >= 0.")
    return value


def _validate_run(repo_root: Path, scenario_ids: set[str], run: dict[str, object]) -> None:
    def _get_str(key: str) -> str:
        value = run.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} must be a non-empty string.")
        return value

    date_utc = _get_str("date_utc")
    _parse_date_utc(date_utc)

    commit_sha = _get_str("commit_sha")
    if commit_sha != "unknown" and not _SHA_RE.match(commit_sha):
        raise ValueError("commit_sha must be a git SHA (7-40 hex chars) or 'unknown'.")

    scenario_id = _get_str("scenario_id")
    if scenario_id not in scenario_ids:
        raise ValueError(f"scenario_id '{scenario_id}' is not in SCENARIOS.md.")

    _get_str("run_id")
    _get_str("agent")
    _get_str("model")
    _get_str("reasoning_effort")

    metrics = run.get("metrics")
    if not isinstance(metrics, dict):
        raise ValueError("metrics must be an object.")

    docs = metrics.get("docs")
    if not isinstance(docs, list) or not all(isinstance(d, str) and d for d in docs):
        raise ValueError("metrics.docs must be an array of strings (paths).")
    if len(set(docs)) != len(docs):
        raise ValueError("metrics.docs must not contain duplicates.")

    doc_char_counts: list[int] = []
    missing_at_commit = False
    if commit_sha != "unknown":
        for doc in docs:
            content = _git_show_text(repo_root, commit_sha, doc)
            if content is None:
                missing_at_commit = True
                break
            doc_char_counts.append(len(content))

    if commit_sha == "unknown" or missing_at_commit:
        doc_char_counts = []
        for doc in docs:
            path = repo_root / doc
            if not path.exists():
                raise ValueError(f"metrics.docs path does not exist: {doc}")
            content = path.read_text(encoding="utf-8")
            doc_char_counts.append(len(content))

    chars_read_expected = sum(doc_char_counts)
    max_doc_chars_expected = max(doc_char_counts) if doc_char_counts else 0
    tok_est_expected = round(chars_read_expected / 4)

    unique_docs_opened = _assert_nonneg_int(
        metrics.get("unique_docs_opened"),
        "metrics.unique_docs_opened",
    )
    if unique_docs_opened != len(docs):
        raise ValueError("metrics.unique_docs_opened must match len(metrics.docs).")

    chars_read = _assert_nonneg_int(metrics.get("chars_read"), "metrics.chars_read")
    if chars_read != chars_read_expected:
        raise ValueError("metrics.chars_read must equal sum(chars) of metrics.docs.")

    tok_est = _assert_nonneg_int(metrics.get("tok_est"), "metrics.tok_est")
    if tok_est != tok_est_expected:
        raise ValueError("metrics.tok_est must equal round(metrics.chars_read / 4).")

    max_doc_chars = _assert_nonneg_int(
        metrics.get("max_doc_chars"),
        "metrics.max_doc_chars",
    )
    if max_doc_chars != max_doc_chars_expected:
        raise ValueError("metrics.max_doc_chars must equal max(chars) of metrics.docs.")

    _assert_nonneg_int(metrics.get("fallback_count"), "metrics.fallback_count")
    _assert_nonneg_int(metrics.get("clarifying_questions"), "metrics.clarifying_questions")

    violations = metrics.get("violations")
    if not isinstance(violations, list) or not all(isinstance(v, str) for v in violations):
        raise ValueError("metrics.violations must be an array of strings.")

    real_tokens = run.get("real_tokens")
    if real_tokens is not None:
        if not isinstance(real_tokens, dict):
            raise ValueError("real_tokens must be an object.")
        _assert_nonneg_int(real_tokens.get("prompt_tokens"), "real_tokens.prompt_tokens")
        _assert_nonneg_int(real_tokens.get("completion_tokens"), "real_tokens.completion_tokens")
        _assert_nonneg_int(real_tokens.get("total_tokens"), "real_tokens.total_tokens")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate benchmark runs.jsonl.")
    parser.add_argument("--runs", default="metrics/llm_benchmarks/runs.jsonl")
    parser.add_argument("--scenarios", default="metrics/llm_benchmarks/SCENARIOS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[3]
    runs_path = (repo_root / args.runs).resolve()
    scenarios_path = (repo_root / args.scenarios).resolve()

    scenario_ids = _load_scenarios(scenarios_path)
    if not scenario_ids:
        raise SystemExit(
            "No scenarios found in SCENARIOS.md (expected '## <scenario_id>' headings)."
        )

    if not runs_path.exists():
        raise SystemExit(f"Runs file does not exist: {runs_path}")

    lines = runs_path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            run = json.loads(line)
        except json.JSONDecodeError as e:
            raise SystemExit(f"{runs_path}:{i}: invalid JSON: {e}") from e
        if not isinstance(run, dict):
            raise SystemExit(f"{runs_path}:{i}: expected JSON object.")
        try:
            _validate_run(repo_root, scenario_ids, run)
        except ValueError as e:
            raise SystemExit(f"{runs_path}:{i}: {e}") from e

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
