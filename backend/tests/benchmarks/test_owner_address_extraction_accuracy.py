"""Benchmark: owner_address extraction accuracy against synthetic fixtures."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from backend.app.application.field_normalizers import normalize_canonical_fields
from backend.app.application.processing_runner import _build_interpretation_artifact

_FIXTURES_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "synthetic"
    / "owner_address"
    / "owner_address_cases.json"
)


def _load_cases() -> list[dict]:
    data = json.loads(_FIXTURES_PATH.read_text(encoding="utf-8"))
    return data["cases"]


_CASES = _load_cases()
# Locked after Phase 4 remediation:
# observed 94.7% EM and target floor set to -5pp (89.7%).
# Because benchmarks operate on discrete case counts, we enforce the nearest
# representable threshold via minimum exact-match count.
TARGET_MIN_EXACT_MATCH_RATE: float = 0.897


def _normalize_for_comparison(value: str | None) -> str | None:
    canonical = normalize_canonical_fields({"owner_address": value}).get("owner_address")
    if canonical is None:
        return None
    cleaned = " ".join(str(canonical).split()).strip(" .,:;\t\r\n")
    return cleaned.casefold() if cleaned else None


def _extract_owner_address(raw_text: str) -> str | None:
    payload = _build_interpretation_artifact(
        document_id="bench-doc",
        run_id="bench-run",
        raw_text=raw_text,
    )
    return payload["data"]["global_schema"].get("owner_address")


@pytest.mark.parametrize("case", _CASES, ids=[c["id"] for c in _CASES])
def test_owner_address_extraction_case(case: dict) -> None:
    extracted = _extract_owner_address(case["text"])
    expected = case["expected_owner_address"]

    norm_ext = _normalize_for_comparison(extracted)
    norm_exp = _normalize_for_comparison(expected)

    assert extracted is None or isinstance(extracted, str)
    if norm_ext != norm_exp:
        print(f"[owner_address mismatch] {case['id']}: expected={expected!r} got={extracted!r}")


def test_owner_address_accuracy_summary() -> None:
    total = len(_CASES)
    exact = 0
    nulls = 0
    false_positives = 0
    mismatches: list[str] = []

    for case in _CASES:
        extracted = _extract_owner_address(case["text"])
        expected = case["expected_owner_address"]

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
    min_exact_matches = math.floor(TARGET_MIN_EXACT_MATCH_RATE * total)
    effective_floor = (min_exact_matches / total) if total else 0.0

    if mismatches:
        print(
            "owner_address benchmark mismatches:\n"
            + "\n".join(mismatches)
            + "\n"
            + (
                f"Summary: exact={exact}/{total} ({exact_match_rate:.1%}), "
                f"null_misses={nulls}, false_positives={false_positives}, "
                f"effective_floor={min_exact_matches}/{total} ({effective_floor:.1%})"
            )
        )
    else:
        print(
            f"Summary: exact={exact}/{total} ({exact_match_rate:.1%}), "
            f"null_misses={nulls}, false_positives={false_positives}, "
            f"effective_floor={min_exact_matches}/{total} ({effective_floor:.1%})"
        )

    assert exact >= min_exact_matches, (
        "Exact matches "
        f"{exact}/{total} are below effective floor "
        f"{min_exact_matches}/{total} ({effective_floor:.1%}) "
        f"derived from target {TARGET_MIN_EXACT_MATCH_RATE:.1%}"
    )
