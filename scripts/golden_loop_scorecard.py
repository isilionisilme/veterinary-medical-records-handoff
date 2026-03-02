from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    expected: str | None
    extracted: str | None


def _normalize(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(str(value).split()).strip()
    return cleaned.casefold() if cleaned else None


def _default_extract(field_key: str, raw_text: str, case_id: str) -> str | None:
    from backend.app.application.processing_runner import _build_interpretation_artifact

    payload = _build_interpretation_artifact(
        document_id=f"golden-loop-{case_id}",
        run_id="golden-loop-scorecard",
        raw_text=raw_text,
    )
    global_schema = payload.get("data", {}).get("global_schema", {})
    value = global_schema.get(field_key)
    return value if isinstance(value, str) else None


def _resolve_expected(case: dict[str, object], field_key: str) -> str | None:
    for key in ("expected", "expected_value", f"expected_{field_key}"):
        if key in case:
            value = case[key]
            return value if isinstance(value, str) else None
    return None


def evaluate_cases(
    cases: list[dict[str, object]],
    field_key: str,
    extractor: Callable[[str, str, str], str | None],
) -> dict[str, object]:
    total = len(cases)
    exact = 0
    null_misses = 0
    false_positives = 0
    mismatches: list[dict[str, str | None]] = []
    per_case: list[CaseResult] = []

    for index, case in enumerate(cases, start=1):
        case_id_obj = case.get("id")
        case_id = str(case_id_obj) if case_id_obj is not None else f"case-{index}"
        raw_text_obj = case.get("text")
        raw_text = str(raw_text_obj) if raw_text_obj is not None else ""

        expected = _resolve_expected(case, field_key)
        extracted = extractor(field_key, raw_text, case_id)

        per_case.append(CaseResult(case_id=case_id, expected=expected, extracted=extracted))

        if _normalize(expected) == _normalize(extracted):
            exact += 1
            continue

        mismatches.append(
            {
                "id": case_id,
                "expected": expected,
                "extracted": extracted,
            }
        )
        if expected is not None and extracted is None:
            null_misses += 1
        if expected is None and extracted is not None:
            false_positives += 1

    exact_rate = (exact / total) if total else 0.0
    null_miss_rate = (null_misses / total) if total else 0.0
    false_positive_rate = (false_positives / total) if total else 0.0

    return {
        "total_cases": total,
        "exact_matches": exact,
        "null_misses": null_misses,
        "false_positives": false_positives,
        "exact_match_rate": exact_rate,
        "null_miss_rate": null_miss_rate,
        "false_positive_rate": false_positive_rate,
        "mismatches": mismatches,
        "case_results": [case.__dict__ for case in per_case],
    }


def _build_snapshot(
    *,
    cases_path: Path,
    field_key: str,
    metrics: dict[str, object],
    baseline_metrics: dict[str, object] | None,
) -> dict[str, object]:
    deltas = None
    if baseline_metrics is not None:
        deltas = {
            "exact_match_rate": float(metrics["exact_match_rate"])
            - float(baseline_metrics.get("exact_match_rate", 0.0)),
            "null_miss_rate": float(metrics["null_miss_rate"])
            - float(baseline_metrics.get("null_miss_rate", 0.0)),
            "false_positive_rate": float(metrics["false_positive_rate"])
            - float(baseline_metrics.get("false_positive_rate", 0.0)),
        }

    return {
        "captured_at": datetime.now(tz=UTC).isoformat(),
        "field_key": field_key,
        "cases_path": str(cases_path).replace("\\", "/"),
        "metrics": metrics,
        "baseline_metrics": baseline_metrics,
        "delta_vs_baseline": deltas,
    }


def evaluate_gates(
    *,
    metrics: dict[str, object],
    baseline_metrics: dict[str, object] | None,
    min_exact_match_rate: float,
    max_null_miss_rate: float,
    max_false_positive_rate: float,
    allow_regression: bool,
) -> list[str]:
    failures: list[str] = []

    exact_rate = float(metrics["exact_match_rate"])
    null_miss_rate = float(metrics["null_miss_rate"])
    false_positive_rate = float(metrics["false_positive_rate"])

    if exact_rate < min_exact_match_rate:
        failures.append(f"exact_match_rate {exact_rate:.1%} < required {min_exact_match_rate:.1%}")
    if null_miss_rate > max_null_miss_rate:
        failures.append(f"null_miss_rate {null_miss_rate:.1%} > allowed {max_null_miss_rate:.1%}")
    if false_positive_rate > max_false_positive_rate:
        failures.append(
            f"false_positive_rate {false_positive_rate:.1%} > allowed {max_false_positive_rate:.1%}"
        )

    if baseline_metrics is not None and not allow_regression:
        base_exact_rate = float(baseline_metrics.get("exact_match_rate", 0.0))
        base_null_miss_rate = float(baseline_metrics.get("null_miss_rate", 0.0))
        base_false_positive_rate = float(baseline_metrics.get("false_positive_rate", 0.0))

        if exact_rate < base_exact_rate:
            failures.append(
                f"regression: exact_match_rate {exact_rate:.1%} < baseline {base_exact_rate:.1%}"
            )
        if null_miss_rate > base_null_miss_rate:
            failures.append(
                "regression: null_miss_rate "
                f"{null_miss_rate:.1%} > baseline {base_null_miss_rate:.1%}"
            )
        if false_positive_rate > base_false_positive_rate:
            failures.append(
                "regression: false_positive_rate "
                f"{false_positive_rate:.1%} > baseline {base_false_positive_rate:.1%}"
            )

    return failures


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _format_scorecard(snapshot: dict[str, object]) -> str:
    metrics = snapshot["metrics"]
    baseline_metrics = snapshot.get("baseline_metrics")
    deltas = snapshot.get("delta_vs_baseline") or {}

    lines = [
        "Golden Loop Scorecard",
        f"- Field: {snapshot['field_key']}",
        f"- Cases: {snapshot['cases_path']}",
        "",
        "| Metric | Baseline | Current | Delta |",
        "|---|---:|---:|---:|",
    ]

    def _row(metric_key: str, label: str) -> str:
        current = float(metrics[metric_key])
        if baseline_metrics is None:
            return f"| {label} | n/a | {current:.1%} | n/a |"
        baseline = float(baseline_metrics.get(metric_key, 0.0))
        delta = float(deltas.get(metric_key, 0.0))
        return f"| {label} | {baseline:.1%} | {current:.1%} | {delta:+.1%} |"

    lines.append(_row("exact_match_rate", "Exact Match Rate"))
    lines.append(_row("null_miss_rate", "Null Miss Rate"))
    lines.append(_row("false_positive_rate", "False Positive Rate"))
    return "\n".join(lines)


def _resolve_config_float(
    *,
    cli_value: float | None,
    cases_payload: dict[str, object],
    key: str,
    default_value: float,
) -> float:
    if cli_value is not None:
        return float(cli_value)

    gates_obj = cases_payload.get("gates")
    if isinstance(gates_obj, dict):
        gate_value = gates_obj.get(key)
        if isinstance(gate_value, int | float):
            return float(gate_value)

    top_level_value = cases_payload.get(key)
    if isinstance(top_level_value, int | float):
        return float(top_level_value)

    return default_value


def _resolve_optional_path(
    *,
    cli_value: str | None,
    cases_payload: dict[str, object],
    payload_key: str,
    cases_path: Path,
) -> Path | None:
    selected = cli_value
    if selected is None:
        payload_value = cases_payload.get(payload_key)
        if isinstance(payload_value, str) and payload_value.strip():
            selected = payload_value.strip()

    if not selected:
        return None

    candidate = Path(selected)
    if candidate.is_absolute():
        return candidate
    return (cases_path.parent / candidate).resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate a golden-loop field extraction dataset, persist a snapshot, "
            "and enforce regression gates against thresholds/baseline."
        )
    )
    parser.add_argument(
        "--cases",
        required=True,
        help="Path to JSON file with shape: {field_key?, cases:[{id,text,expected?}]}",
    )
    parser.add_argument(
        "--field-key",
        required=False,
        help="Global schema field key (if omitted, uses field_key from cases file).",
    )
    parser.add_argument(
        "--baseline",
        required=False,
        help="Optional path to previous snapshot JSON generated by this script.",
    )
    parser.add_argument(
        "--output",
        required=False,
        help="Optional output path for the new snapshot JSON.",
    )
    parser.add_argument(
        "--min-exact-match-rate",
        type=float,
        default=None,
        help="Minimum allowed exact_match_rate (0..1).",
    )
    parser.add_argument(
        "--max-null-miss-rate",
        type=float,
        default=None,
        help="Maximum allowed null_miss_rate (0..1).",
    )
    parser.add_argument(
        "--max-false-positive-rate",
        type=float,
        default=None,
        help="Maximum allowed false_positive_rate (0..1).",
    )
    parser.add_argument(
        "--allow-regression",
        action="store_true",
        help="Disable baseline non-regression checks when --baseline is provided.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    cases_path = Path(args.cases)
    if not cases_path.exists():
        raise FileNotFoundError(f"Cases file not found: {cases_path}")

    cases_payload = _load_json(cases_path)
    field_key = args.field_key or str(cases_payload.get("field_key") or "").strip()
    if not field_key:
        raise ValueError("field_key is required via --field-key or cases JSON field_key")

    cases_obj = cases_payload.get("cases")
    if not isinstance(cases_obj, list) or not cases_obj:
        raise ValueError("cases JSON must include a non-empty 'cases' array")

    min_exact_match_rate = _resolve_config_float(
        cli_value=args.min_exact_match_rate,
        cases_payload=cases_payload,
        key="min_exact_match_rate",
        default_value=0.0,
    )
    max_null_miss_rate = _resolve_config_float(
        cli_value=args.max_null_miss_rate,
        cases_payload=cases_payload,
        key="max_null_miss_rate",
        default_value=1.0,
    )
    max_false_positive_rate = _resolve_config_float(
        cli_value=args.max_false_positive_rate,
        cases_payload=cases_payload,
        key="max_false_positive_rate",
        default_value=1.0,
    )

    baseline_path = _resolve_optional_path(
        cli_value=args.baseline,
        cases_payload=cases_payload,
        payload_key="baseline",
        cases_path=cases_path,
    )
    output_path = _resolve_optional_path(
        cli_value=args.output,
        cases_payload=cases_payload,
        payload_key="snapshot_output",
        cases_path=cases_path,
    )

    metrics = evaluate_cases(
        cases=cases_obj,
        field_key=field_key,
        extractor=_default_extract,
    )

    baseline_metrics: dict[str, object] | None = None
    if baseline_path is not None:
        baseline_payload = _load_json(baseline_path)
        loaded = baseline_payload.get("metrics")
        if isinstance(loaded, dict):
            baseline_metrics = loaded

    snapshot = _build_snapshot(
        cases_path=cases_path,
        field_key=field_key,
        metrics=metrics,
        baseline_metrics=baseline_metrics,
    )

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    print(_format_scorecard(snapshot))

    failures = evaluate_gates(
        metrics=metrics,
        baseline_metrics=baseline_metrics,
        min_exact_match_rate=min_exact_match_rate,
        max_null_miss_rate=max_null_miss_rate,
        max_false_positive_rate=max_false_positive_rate,
        allow_regression=bool(args.allow_regression),
    )
    if failures:
        print("\nGate failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
