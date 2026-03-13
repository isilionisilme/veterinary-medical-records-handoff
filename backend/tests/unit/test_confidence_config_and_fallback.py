from __future__ import annotations

from backend.app.application.document_service import _resolve_human_edit_candidate_confidence
from backend.app.config import human_edit_neutral_candidate_confidence


def test_human_edit_confidence_fallback_prefers_candidate() -> None:
    value = _resolve_human_edit_candidate_confidence(
        {
            "field_candidate_confidence": 0.66,
            "field_mapping_confidence": 0.9,
        },
        neutral_candidate_confidence=0.5,
    )

    assert value == 0.66


def test_human_edit_confidence_fallback_uses_mapping_when_candidate_missing() -> None:
    value = _resolve_human_edit_candidate_confidence(
        {
            "field_candidate_confidence": None,
            "field_mapping_confidence": 0.72,
        },
        neutral_candidate_confidence=0.5,
    )

    assert value == 0.72


def test_human_edit_confidence_fallback_uses_neutral_when_no_prior_signal() -> None:
    value = _resolve_human_edit_candidate_confidence(
        {
            "field_candidate_confidence": None,
            "field_mapping_confidence": None,
        },
        neutral_candidate_confidence=0.5,
    )

    assert value == 0.5


def test_human_edit_neutral_candidate_confidence_reads_valid_env(monkeypatch) -> None:
    monkeypatch.setenv("VET_RECORDS_HUMAN_EDIT_NEUTRAL_CANDIDATE_CONFIDENCE", "0.35")

    assert human_edit_neutral_candidate_confidence() == 0.35


def test_human_edit_neutral_candidate_confidence_falls_back_on_invalid_env(monkeypatch) -> None:
    monkeypatch.setenv("VET_RECORDS_HUMAN_EDIT_NEUTRAL_CANDIDATE_CONFIDENCE", "invalid")

    assert human_edit_neutral_candidate_confidence() == 0.5
