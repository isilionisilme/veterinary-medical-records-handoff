"""Benchmark: microchip_id extraction accuracy against synthetic fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.app.application.field_normalizers import normalize_canonical_fields
from backend.app.application.processing_runner import _build_interpretation_artifact

_FIXTURES_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "synthetic"
    / "microchip"
    / "microchip_cases.json"
)


def _load_cases() -> list[dict]:
    data = json.loads(_FIXTURES_PATH.read_text(encoding="utf-8"))
    return data["cases"]


_CASES = _load_cases()

MIN_EXACT_MATCH_RATE: float = 0.95


def _normalize_for_comparison(value: str | None) -> str | None:
    canonical = normalize_canonical_fields({"microchip_id": value}).get("microchip_id")
    if canonical is None:
        return None
    cleaned = "".join(str(canonical).split()).strip()
    return cleaned.casefold() if cleaned else None


def _extract_microchip_id(raw_text: str) -> str | None:
    payload = _build_interpretation_artifact(
        document_id="bench-doc",
        run_id="bench-run",
        raw_text=raw_text,
    )
    return payload["data"]["global_schema"].get("microchip_id")


@pytest.mark.parametrize("case", _CASES, ids=[c["id"] for c in _CASES])
def test_microchip_case(case: dict) -> None:
    extracted = _extract_microchip_id(case["text"])
    expected = case["expected_microchip_id"]

    assert _normalize_for_comparison(extracted) == _normalize_for_comparison(expected), (
        f"[{case['id']}] expected={expected!r} got={extracted!r}"
    )


def test_microchip_accuracy_summary() -> None:
    total = len(_CASES)
    exact = 0
    nulls = 0
    false_positives = 0
    mismatches: list[str] = []

    for case in _CASES:
        extracted = _extract_microchip_id(case["text"])
        expected = case["expected_microchip_id"]

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

    exact_match_rate = exact / total if total else 0.0

    if mismatches:
        pytest.fail(
            "microchip_id benchmark mismatches:\n"
            + "\n".join(mismatches)
            + "\n"
            + (
                f"Summary: exact={exact}/{total} ({exact_match_rate:.1%}), "
                f"null_misses={nulls}, false_positives={false_positives}"
            )
        )

    assert exact_match_rate >= MIN_EXACT_MATCH_RATE, (
        f"Exact-match rate {exact_match_rate:.1%} is below floor {MIN_EXACT_MATCH_RATE:.1%}"
    )
