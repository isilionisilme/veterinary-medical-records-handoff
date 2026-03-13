"""Benchmark: clinic_name extraction accuracy against synthetic fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.app.application.processing_runner import _build_interpretation_artifact

_FIXTURES_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "synthetic"
    / "clinic_name"
    / "clinic_name_cases.json"
)


def _load_cases() -> list[dict]:
    data = json.loads(_FIXTURES_PATH.read_text(encoding="utf-8"))
    return data["cases"]


_CASES = _load_cases()

# Flexible regression reference: keep tolerance for fixture evolution while
# still catching meaningful quality drift.
MIN_EXACT_MATCH_RATE: float = 0.90


def _normalize_for_comparison(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.split()).strip(" .,:;\t\r\n")
    return cleaned.casefold() if cleaned else None


def _extract_clinic_name(raw_text: str) -> str | None:
    payload = _build_interpretation_artifact(
        document_id="bench-doc",
        run_id="bench-run",
        raw_text=raw_text,
    )
    return payload["data"]["global_schema"].get("clinic_name")


@pytest.mark.parametrize("case", _CASES, ids=[c["id"] for c in _CASES])
def test_clinic_name_case(case: dict) -> None:
    extracted = _extract_clinic_name(case["text"])
    expected = case["expected_clinic_name"]

    assert _normalize_for_comparison(extracted) == _normalize_for_comparison(expected), (
        f"[{case['id']}] expected={expected!r} got={extracted!r}"
    )


def test_clinic_name_accuracy_summary() -> None:
    total = len(_CASES)
    exact = 0
    nulls = 0
    false_positives = 0
    mismatches: list[str] = []

    for case in _CASES:
        extracted = _extract_clinic_name(case["text"])
        expected = case["expected_clinic_name"]

        norm_ext = _normalize_for_comparison(extracted)
        norm_exp = _normalize_for_comparison(expected)

        if norm_ext == norm_exp:
            exact += 1
        else:
            mismatches.append(f"  {case['id']}: expected={expected!r} got={extracted!r}")
            if expected is not None and extracted is None:
                nulls += 1
            if expected is None and extracted is not None:
                false_positives += 1

    exact_rate = exact / total if total else 0.0
    null_rate = nulls / total if total else 0.0
    fp_rate = false_positives / total if total else 0.0

    report = [
        "",
        "=== clinic_name extraction accuracy ===",
        f"  Total cases     : {total}",
        f"  Exact matches   : {exact} / {total}  ({exact_rate:.1%})",
        f"  Null misses     : {nulls}  ({null_rate:.1%})",
        f"  False positives : {false_positives}  ({fp_rate:.1%})",
    ]
    if mismatches:
        report.append("  -- Mismatches --")
        report.extend(mismatches)
    report.append("=" * 42)
    print("\n".join(report))

    assert exact_rate >= MIN_EXACT_MATCH_RATE, (
        f"Exact-match rate {exact_rate:.1%} below minimum {MIN_EXACT_MATCH_RATE:.1%}"
    )
