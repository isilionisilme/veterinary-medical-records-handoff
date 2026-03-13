"""Benchmark: weight extraction accuracy against synthetic fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.app.application.field_normalizers import normalize_canonical_fields
from backend.app.application.processing_runner import _build_interpretation_artifact

_FIXTURES_PATH = (
    Path(__file__).resolve().parents[1] / "fixtures" / "synthetic" / "weight" / "weight_cases.json"
)


def _load_cases() -> list[dict]:
    data = json.loads(_FIXTURES_PATH.read_text(encoding="utf-8"))
    return data["cases"]


_CASES = _load_cases()

# Non-regression floor for this synthetic benchmark.
MIN_EXACT_MATCH_RATE: float = 0.95


def _normalize_for_comparison(value: str | None) -> str | None:
    canonical = normalize_canonical_fields({"weight": value}).get("weight")
    if canonical is None:
        return None
    cleaned = " ".join(str(canonical).split()).strip()
    if not cleaned:
        return None
    return cleaned.casefold()


def _extract_weight(raw_text: str) -> str | None:
    payload = _build_interpretation_artifact(
        document_id="bench-doc",
        run_id="bench-run",
        raw_text=raw_text,
    )
    return payload["data"]["global_schema"].get("weight")


@pytest.mark.parametrize("case", _CASES, ids=[c["id"] for c in _CASES])
def test_weight_extraction_case(case: dict) -> None:
    extracted = _extract_weight(case["text"])
    expected = case["expected_weight"]

    assert _normalize_for_comparison(extracted) == _normalize_for_comparison(expected), (
        f"[{case['id']}] expected={expected!r} got={extracted!r}"
    )


def test_weight_extraction_accuracy_summary() -> None:
    total = len(_CASES)
    exact = 0
    null_misses = 0
    false_positives = 0
    mismatches: list[str] = []

    for case in _CASES:
        extracted = _extract_weight(case["text"])
        expected = case["expected_weight"]

        norm_ext = _normalize_for_comparison(extracted)
        norm_exp = _normalize_for_comparison(expected)

        if norm_ext == norm_exp:
            exact += 1
        else:
            mismatches.append(f"  {case['id']}: expected={expected!r} got={extracted!r}")
            if expected is not None and extracted is None:
                null_misses += 1
            if expected is None and extracted is not None:
                false_positives += 1

    exact_match_rate = exact / total if total else 0.0

    if mismatches:
        pytest.fail(
            "weight benchmark mismatches:\n"
            + "\n".join(mismatches)
            + "\n"
            + (
                f"Summary: exact={exact}/{total} ({exact_match_rate:.1%}), "
                f"null_misses={null_misses}, false_positives={false_positives}"
            )
        )

    assert exact_match_rate >= MIN_EXACT_MATCH_RATE, (
        f"Exact-match rate {exact_match_rate:.1%} is below floor {MIN_EXACT_MATCH_RATE:.1%}"
    )
