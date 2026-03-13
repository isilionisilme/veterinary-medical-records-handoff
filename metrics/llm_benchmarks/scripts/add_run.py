from __future__ import annotations

import argparse
import json
import secrets
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class ParsedMetricsLine:
    scenario_id: str
    docs: list[str]
    fallback_count: int
    clarifying_questions: int
    violations: list[str]


def _now_utc_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _run_id(now_utc_iso: str) -> str:
    ts = now_utc_iso.replace("-", "").replace(":", "").replace(".", "")
    ts = ts.replace("Z", "Z")
    return f"{ts}-{secrets.token_hex(3)}"


def _git_commit_sha() -> str | None:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None
    return out or None


def _parse_metrics_line(line: str) -> ParsedMetricsLine:
    line = line.strip()
    if not line.startswith("METRICS "):
        raise ValueError("Expected line to start with 'METRICS '.")

    fields: dict[str, str] = {}
    for token in line[len("METRICS ") :].split():
        if "=" not in token:
            raise ValueError(f"Invalid token '{token}' (expected key=value).")
        key, value = token.split("=", 1)
        fields[key] = value

    scenario_id = fields.get("scenario", "").strip()
    if not scenario_id:
        raise ValueError("Missing scenario=<scenario_id>.")

    docs_raw = fields.get("docs", "").strip()
    docs = [p for p in docs_raw.split("|") if p] if docs_raw else []

    def _parse_int(key: str) -> int:
        raw = fields.get(key, "").strip()
        if raw == "":
            raise ValueError(f"Missing {key}=<int>.")
        value = int(raw)
        if value < 0:
            raise ValueError(f"{key} must be >= 0.")
        return value

    fallback_count = _parse_int("fallback")
    clarifying_questions = _parse_int("clarifying")

    violations_raw = fields.get("violations", "")
    violations = [v for v in violations_raw.split(",") if v] if violations_raw else []

    return ParsedMetricsLine(
        scenario_id=scenario_id,
        docs=docs,
        fallback_count=fallback_count,
        clarifying_questions=clarifying_questions,
        violations=violations,
    )


def _compute_doc_metrics(repo_root: Path, docs: list[str]) -> tuple[int, int]:
    max_doc_chars = 0
    chars_read = 0
    for doc in docs:
        path = repo_root / doc
        content = path.read_text(encoding="utf-8")
        n = len(content)
        chars_read += n
        max_doc_chars = max(max_doc_chars, n)
    return chars_read, max_doc_chars


def main() -> int:
    parser = argparse.ArgumentParser(description="Append a benchmark run to runs.jsonl.")
    parser.add_argument("--runs", default="metrics/llm_benchmarks/runs.jsonl")
    parser.add_argument("--agent", default="codex_cli")
    parser.add_argument("--model", required=True)
    parser.add_argument("--reasoning-effort", required=True)
    parser.add_argument("--commit-sha", default=None)
    parser.add_argument("--from-stdin", action="store_true", help="Read a METRICS line from stdin.")
    parser.add_argument("--metrics-line", default=None, help="Pass the METRICS line explicitly.")
    args = parser.parse_args()

    if bool(args.from_stdin) + bool(args.metrics_line) != 1:
        raise SystemExit("Provide exactly one of: --from-stdin or --metrics-line.")

    if args.from_stdin:
        line = sys.stdin.read().strip()
    else:
        line = args.metrics_line or ""

    parsed = _parse_metrics_line(line)

    repo_root = Path(__file__).resolve().parents[3]
    for doc in parsed.docs:
        path = repo_root / doc
        if not path.exists():
            raise SystemExit(f"Doc path does not exist: {doc}")

    chars_read, max_doc_chars = _compute_doc_metrics(repo_root, parsed.docs)
    tok_est = round(chars_read / 4)

    commit_sha = args.commit_sha or _git_commit_sha() or "unknown"
    now = _now_utc_iso()
    run = {
        "date_utc": now,
        "commit_sha": commit_sha,
        "scenario_id": parsed.scenario_id,
        "run_id": _run_id(now),
        "agent": args.agent,
        "model": args.model,
        "reasoning_effort": args.reasoning_effort,
        "metrics": {
            "docs": parsed.docs,
            "unique_docs_opened": len(parsed.docs),
            "chars_read": chars_read,
            "tok_est": tok_est,
            "max_doc_chars": max_doc_chars,
            "fallback_count": parsed.fallback_count,
            "clarifying_questions": parsed.clarifying_questions,
            "violations": parsed.violations,
        },
    }

    runs_path = (repo_root / args.runs).resolve()
    runs_path.parent.mkdir(parents=True, exist_ok=True)
    with runs_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(run, ensure_ascii=False) + "\n")

    print(f"Appended run to {runs_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
