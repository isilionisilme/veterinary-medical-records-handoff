"""Benchmark: pet_name extraction accuracy against synthetic fixtures.

Exercises the full interpretation pipeline on each synthetic case and reports:
  - Exact Match rate  (extracted == expected after normalization)
  - Null rate          (extracted None when expected non-null)
  - False Positive rate (extracted non-null when expected None)

The test suite is parametrized so each case appears as its own test item,
making regressions immediately visible in CI output.

A summary test collects aggregate metrics and enforces a minimum Exact Match
threshold (configurable via ``MIN_EXACT_MATCH_RATE``).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.app.application.processing_runner import _build_interpretation_artifact

# ---------------------------------------------------------------------------
# Fixtures dir & loader
# ---------------------------------------------------------------------------

_FIXTURES_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "synthetic"
    / "pet_name"
    / "pet_name_cases.json"
)


def _load_cases() -> list[dict]:
    data = json.loads(_FIXTURES_PATH.read_text(encoding="utf-8"))
    return data["cases"]


_CASES = _load_cases()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Minimum Exact-Match rate to pass the aggregate gate.
# After P1 improvements we hit 100 % on synthetic fixtures.
MIN_EXACT_MATCH_RATE: float = 1.0


def _normalize_for_comparison(value: str | None) -> str | None:
    """Light normalization so comparison is case- and whitespace-insensitive."""
    if value is None:
        return None
    cleaned = " ".join(value.split()).strip()
    return cleaned.casefold() if cleaned else None


def _extract_pet_name(raw_text: str) -> str | None:
    """Run the full interpretation pipeline and return pet_name."""
    payload = _build_interpretation_artifact(
        document_id="bench-doc",
        run_id="bench-run",
        raw_text=raw_text,
    )
    return payload["data"]["global_schema"].get("pet_name")


# ---------------------------------------------------------------------------
# Per-case parametrized tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "case",
    _CASES,
    ids=[c["id"] for c in _CASES],
)
def test_pet_name_case(case: dict) -> None:
    """Each synthetic case produces the expected pet_name (or null)."""
    extracted = _extract_pet_name(case["text"])
    expected = case["expected_pet_name"]

    norm_ext = _normalize_for_comparison(extracted)
    norm_exp = _normalize_for_comparison(expected)

    # Hard assertion — all synthetic cases must now pass after P1 improvements.
    assert norm_ext == norm_exp, f"[{case['id']}] expected={expected!r}  got={extracted!r}"


# ---------------------------------------------------------------------------
# Aggregate accuracy gate
# ---------------------------------------------------------------------------


def test_pet_name_accuracy_summary() -> None:
    """Aggregate metrics across all cases; enforce minimum threshold."""
    total = len(_CASES)
    exact = 0
    nulls = 0
    false_positives = 0
    mismatches: list[str] = []

    for case in _CASES:
        extracted = _extract_pet_name(case["text"])
        expected = case["expected_pet_name"]

        norm_ext = _normalize_for_comparison(extracted)
        norm_exp = _normalize_for_comparison(expected)

        if norm_ext == norm_exp:
            exact += 1
        else:
            mismatches.append(f"  {case['id']}: expected={expected!r}  got={extracted!r}")
            if expected is not None and extracted is None:
                nulls += 1
            if expected is None and extracted is not None:
                false_positives += 1

    exact_rate = exact / total if total else 0.0
    null_rate = nulls / total if total else 0.0
    fp_rate = false_positives / total if total else 0.0

    # ── Report (always printed) ──────────────────────────────────────────
    report_lines = [
        "",
        "=== pet_name extraction accuracy ===",
        f"  Total cases     : {total}",
        f"  Exact matches   : {exact} / {total}  ({exact_rate:.1%})",
        f"  Null misses     : {nulls}  ({null_rate:.1%})",
        f"  False positives : {false_positives}  ({fp_rate:.1%})",
    ]
    if mismatches:
        report_lines.append("  -- Mismatches --")
        report_lines.extend(mismatches)
    report_lines.append("=" * 39)

    print("\n".join(report_lines))

    # ── Gate ──────────────────────────────────────────────────────────────
    assert exact_rate >= MIN_EXACT_MATCH_RATE, (
        f"Exact-match rate {exact_rate:.1%} below minimum {MIN_EXACT_MATCH_RATE:.1%}"
    )
