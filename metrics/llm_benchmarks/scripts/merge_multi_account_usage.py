from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

PRICE_PER_PREMIUM_REQUEST_USD = 0.04
INCLUDED_PREMIUM_REQUESTS_PER_ACCOUNT = 300


@dataclass(frozen=True)
class UsageRow:
    date: str
    actions: float
    copilot: float


def _to_float(value: str) -> float:
    normalized = (value or "0").strip().replace(",", ".")
    try:
        return float(normalized)
    except ValueError:
        return 0.0


def _load_usage_csv(path: Path) -> list[UsageRow]:
    rows: list[UsageRow] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = (row.get("DateTime") or "").strip()
            if not date:
                continue
            rows.append(
                UsageRow(
                    date=date,
                    actions=_to_float(row.get("Actions") or "0"),
                    copilot=_to_float(row.get("Copilot") or "0"),
                )
            )
    rows.sort(key=lambda item: item.date)
    return rows


def _daily_deltas(rows: list[UsageRow]) -> list[UsageRow]:
    result: list[UsageRow] = []
    prev_actions = 0.0
    prev_copilot = 0.0

    for row in rows:
        da = row.actions - prev_actions
        dc = row.copilot - prev_copilot
        if da < 0:
            da = row.actions
        if dc < 0:
            dc = row.copilot

        result.append(UsageRow(date=row.date, actions=max(da, 0.0), copilot=max(dc, 0.0)))
        prev_actions = row.actions
        prev_copilot = row.copilot

    return result


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _series_hash(rows: list[UsageRow], field: str) -> str:
    if field == "copilot":
        payload = "|".join(f"{r.date}:{r.copilot}" for r in rows)
    else:
        payload = "|".join(f"{r.date}:{r.actions}" for r in rows)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _write_merged_csv(path: Path, merged: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "DateTime",
                "accounts_reporting",
                "actions_daily",
                "copilot_daily",
                "actions_cumulative",
                "copilot_cumulative",
                "copilot_usd_daily",
                "copilot_usd_cumulative",
                "premium_requests_daily_est",
                "premium_requests_cumulative_est",
            ],
        )
        writer.writeheader()
        for row in merged:
            writer.writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Merge multi-account usage exports into one daily series."
    )
    parser.add_argument("--input-dir", default="tmp/usage")
    parser.add_argument(
        "--out-csv",
        default="metrics/llm_benchmarks/account_usage_merged_daily.csv",
    )
    parser.add_argument(
        "--out-quality",
        default="metrics/llm_benchmarks/account_usage_quality.json",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[3]
    input_dir = (repo_root / args.input_dir).resolve()
    out_csv = (repo_root / args.out_csv).resolve()
    out_quality = (repo_root / args.out_quality).resolve()

    files = sorted(input_dir.glob("*.csv"))
    if not files:
        raise SystemExit(f"No CSV files found in {input_dir}")

    by_file: dict[str, list[UsageRow]] = {}
    exact_hash_groups: defaultdict[str, list[str]] = defaultdict(list)
    copilot_series_groups: defaultdict[str, list[str]] = defaultdict(list)

    for path in files:
        rows = _load_usage_csv(path)
        by_file[path.name] = rows
        exact_hash_groups[_file_hash(path)].append(path.name)
        copilot_series_groups[_series_hash(rows, "copilot")].append(path.name)

    daily_actions: defaultdict[str, float] = defaultdict(float)
    daily_copilot: defaultdict[str, float] = defaultdict(float)
    accounts_reporting: defaultdict[str, int] = defaultdict(int)

    for _, rows in by_file.items():
        deltas = _daily_deltas(rows)
        for d in deltas:
            daily_actions[d.date] += d.actions
            daily_copilot[d.date] += d.copilot
            accounts_reporting[d.date] += 1

    all_days = sorted(set(daily_actions.keys()) | set(daily_copilot.keys()))
    merged: list[dict[str, object]] = []
    actions_cumulative = 0.0
    copilot_cumulative = 0.0
    for day in all_days:
        actions_daily = round(daily_actions[day], 4)
        copilot_daily = round(daily_copilot[day], 4)
        copilot_usd_daily = copilot_daily
        premium_requests_daily_est = round(copilot_usd_daily / PRICE_PER_PREMIUM_REQUEST_USD, 4)
        actions_cumulative = round(actions_cumulative + actions_daily, 4)
        copilot_cumulative = round(copilot_cumulative + copilot_daily, 4)
        copilot_usd_cumulative = copilot_cumulative
        premium_requests_cumulative_est = round(
            copilot_usd_cumulative / PRICE_PER_PREMIUM_REQUEST_USD,
            4,
        )
        merged.append(
            {
                "DateTime": day,
                "accounts_reporting": accounts_reporting[day],
                "actions_daily": actions_daily,
                "copilot_daily": copilot_daily,
                "actions_cumulative": actions_cumulative,
                "copilot_cumulative": copilot_cumulative,
                "copilot_usd_daily": copilot_usd_daily,
                "copilot_usd_cumulative": copilot_usd_cumulative,
                "premium_requests_daily_est": premium_requests_daily_est,
                "premium_requests_cumulative_est": premium_requests_cumulative_est,
            }
        )

    _write_merged_csv(out_csv, merged)

    quality = {
        "input_dir": str(input_dir),
        "files": sorted(by_file.keys()),
        "exact_duplicate_files": [names for names in exact_hash_groups.values() if len(names) > 1],
        "copilot_series_duplicate_files": [
            names for names in copilot_series_groups.values() if len(names) > 1
        ],
        "daily_rows": len(merged),
        "first_day": merged[0]["DateTime"] if merged else None,
        "last_day": merged[-1]["DateTime"] if merged else None,
        "copilot_total": merged[-1]["copilot_cumulative"] if merged else 0,
        "copilot_usd_total": merged[-1]["copilot_usd_cumulative"] if merged else 0,
        "premium_requests_total_est": (
            merged[-1]["premium_requests_cumulative_est"] if merged else 0
        ),
        "price_per_premium_request_usd": PRICE_PER_PREMIUM_REQUEST_USD,
        "included_premium_requests_per_account": INCLUDED_PREMIUM_REQUESTS_PER_ACCOUNT,
        "included_usd_per_account": round(
            INCLUDED_PREMIUM_REQUESTS_PER_ACCOUNT * PRICE_PER_PREMIUM_REQUEST_USD,
            2,
        ),
        "accounts_detected": len(by_file),
        "included_usd_all_accounts": round(
            len(by_file) * INCLUDED_PREMIUM_REQUESTS_PER_ACCOUNT * PRICE_PER_PREMIUM_REQUEST_USD,
            2,
        ),
        "actions_total": merged[-1]["actions_cumulative"] if merged else 0,
    }

    out_quality.parent.mkdir(parents=True, exist_ok=True)
    out_quality.write_text(
        json.dumps(quality, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Merged {len(files)} files into {out_csv}")
    print(f"Wrote quality report to {out_quality}")
    if quality["exact_duplicate_files"]:
        print("Exact duplicate files detected:")
        for group in quality["exact_duplicate_files"]:
            print("  - " + ", ".join(group))
    if quality["copilot_series_duplicate_files"]:
        print("Duplicate Copilot series detected:")
        for group in quality["copilot_series_duplicate_files"]:
            print("  - " + ", ".join(group))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
