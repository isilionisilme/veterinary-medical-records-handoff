from __future__ import annotations

import argparse
import csv
from pathlib import Path


def _to_float(value: str) -> float:
    normalized = (value or "0").strip().replace(",", ".")
    try:
        return float(normalized)
    except ValueError:
        return 0.0


def _load_real_usage_rows(repo_root: Path) -> list[dict[str, object]]:
    merged_path = repo_root / "metrics/llm_benchmarks/account_usage_merged_daily.csv"
    if not merged_path.exists():
        return []

    rows: list[dict[str, object]] = []
    with merged_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            day = (row.get("DateTime") or "").strip()
            if not day:
                continue
            copilot_usd_daily = _to_float(
                row.get("copilot_usd_daily") or row.get("copilot_daily") or "0"
            )
            copilot_usd_cumulative = _to_float(
                row.get("copilot_usd_cumulative") or row.get("copilot_cumulative") or "0"
            )
            premium_requests_daily_est = _to_float(row.get("premium_requests_daily_est") or "0")
            premium_requests_cumulative_est = _to_float(
                row.get("premium_requests_cumulative_est") or "0"
            )

            rows.append(
                {
                    "date": day,
                    "accounts_reporting": int(_to_float(row.get("accounts_reporting") or "0")),
                    "copilot_usd_daily": copilot_usd_daily,
                    "copilot_usd_cumulative": copilot_usd_cumulative,
                    "premium_requests_daily_est": premium_requests_daily_est,
                    "premium_requests_cumulative_est": premium_requests_cumulative_est,
                }
            )

    rows.sort(key=lambda item: str(item["date"]))
    return rows


def _render_summary(repo_root: Path) -> str:
    rows = _load_real_usage_rows(repo_root)
    if not rows:
        return (
            "# LLM Benchmarks — Summary\n\n"
            "No merged multi-account usage found yet.\n\n"
            "Update this file by running:\n\n"
            "`python metrics/llm_benchmarks/scripts/"
            "merge_multi_account_usage.py --input-dir tmp/usage`\n"
            "`python metrics/llm_benchmarks/scripts/"
            "summarize.py --write metrics/llm_benchmarks/summary.md`\n"
        )

    lines: list[str] = ["# LLM Benchmarks — Summary", ""]
    lines.append("## Final merged usage table")
    lines.append("")
    lines.append(
        "Source: `metrics/llm_benchmarks/account_usage_merged_daily.csv` "
        "generated from `tmp/usage/`."
    )
    lines.append(
        "Interpretation: CSV `Copilot` values are USD; Premium Requests are "
        "estimated as `USD / 0.04`."
    )
    lines.append("")
    lines.append(
        "| Date | Accounts reporting | Copilot USD daily | Copilot USD cumulative | "
        "Premium Requests daily (est) | Premium Requests cumulative (est) |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|")

    for row in rows:
        lines.append(
            f"| {row['date']} | {row['accounts_reporting']} | "
            f"{row['copilot_usd_daily']:.2f} | {row['copilot_usd_cumulative']:.2f} | "
            f"{row['premium_requests_daily_est']:.2f} | "
            f"{row['premium_requests_cumulative_est']:.2f} |"
        )

    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize runs.jsonl into a Markdown table.")
    parser.add_argument("--runs", default="metrics/llm_benchmarks/runs.jsonl")
    parser.add_argument("--write", default=None, help="Write output to the given path.")
    parser.add_argument("--check", action="store_true", help="Fail if --write is out of date.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[3]
    _ = args.runs
    summary = _render_summary(repo_root)

    if args.write:
        out_path = (repo_root / args.write).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if args.check and out_path.exists():
            existing = out_path.read_text(encoding="utf-8")
            if existing != summary:
                raise SystemExit(f"Summary is out of date: {args.write}")
        out_path.write_text(summary, encoding="utf-8")
    else:
        print(summary, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
