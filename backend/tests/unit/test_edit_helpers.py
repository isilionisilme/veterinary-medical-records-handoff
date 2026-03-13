from __future__ import annotations

import math

from backend.app.application.documents._edit_helpers import (
    _build_field_change_log,
    _build_global_schema_from_fields,
    _compose_field_mapping_confidence,
    _is_noop_update,
    _normalize_value_for_noop,
    _resolve_human_edit_candidate_confidence,
    _sanitize_confidence_breakdown,
    _sanitize_field_candidate_confidence,
    _sanitize_field_mapping_confidence,
    _sanitize_field_review_history_adjustment,
    _sanitize_text_extraction_reliability,
    is_field_value_empty,
)
from backend.app.application.global_schema import REPEATABLE_KEYS


def test_normalize_value_for_noop_covers_string_numeric_and_boolean_branches() -> None:
    assert _normalize_value_for_noop(value="  Hola   Mundo  ", value_type="string") == "Hola Mundo"
    assert _normalize_value_for_noop(value=True, value_type="number") is True
    assert _normalize_value_for_noop(value=5, value_type="float") == 5.0
    assert _normalize_value_for_noop(value=math.inf, value_type="decimal") == math.inf
    assert _normalize_value_for_noop(value="", value_type="int") == ""
    assert _normalize_value_for_noop(value=" 12.5 ", value_type="number") == 12.5
    assert _normalize_value_for_noop(value="abc", value_type="number") == "abc"
    assert _normalize_value_for_noop(value="1", value_type="bool") is True
    assert _normalize_value_for_noop(value="false", value_type="boolean") is False
    assert _normalize_value_for_noop(value=" maybe ", value_type="bool") == "maybe"
    assert _normalize_value_for_noop(value="  trimmed  ", value_type="unknown") == "trimmed"


def test_is_noop_update_respects_type_and_normalized_values() -> None:
    assert not _is_noop_update(
        old_value="A",
        new_value="A",
        existing_value_type=None,
        incoming_value_type="string",
    )
    assert not _is_noop_update(
        old_value="A",
        new_value="A",
        existing_value_type="string",
        incoming_value_type="text",
    )
    assert _is_noop_update(
        old_value="   Maria   Lopez ",
        new_value="Maria Lopez",
        existing_value_type="string",
        incoming_value_type="string",
    )


def test_sanitize_text_extraction_reliability_only_accepts_0_to_1_finite_numbers() -> None:
    assert _sanitize_text_extraction_reliability(True) is None
    assert _sanitize_text_extraction_reliability(0.55) == 0.55
    assert _sanitize_text_extraction_reliability(-0.1) is None
    assert _sanitize_text_extraction_reliability(1.1) is None
    assert _sanitize_text_extraction_reliability(math.inf) is None


def test_sanitize_field_review_history_adjustment_returns_zero_for_invalid_values() -> None:
    assert _sanitize_field_review_history_adjustment(False) == 0.0
    assert _sanitize_field_review_history_adjustment(3.25) == 3.25
    assert _sanitize_field_review_history_adjustment(math.nan) == 0.0


def test_sanitize_field_confidences_clamp_and_reject_booleans() -> None:
    assert _sanitize_field_candidate_confidence(True) is None
    assert _sanitize_field_candidate_confidence(-2) == 0.0
    assert _sanitize_field_candidate_confidence(0.42) == 0.42
    assert _sanitize_field_candidate_confidence(7) == 1.0

    assert _sanitize_field_mapping_confidence(False) is None
    assert _sanitize_field_mapping_confidence(-1) == 0.0
    assert _sanitize_field_mapping_confidence(0.81) == 0.81
    assert _sanitize_field_mapping_confidence(9) == 1.0


def test_compose_field_mapping_confidence_applies_adjustment_and_bounds() -> None:
    assert (
        _compose_field_mapping_confidence(candidate_confidence=0.5, review_history_adjustment=20.0)
        == 0.7
    )
    assert (
        _compose_field_mapping_confidence(candidate_confidence=0.1, review_history_adjustment=-40.0)
        == 0.0
    )
    assert (
        _compose_field_mapping_confidence(candidate_confidence=0.95, review_history_adjustment=20.0)
        == 1.0
    )


def test_resolve_human_edit_candidate_confidence_prefers_candidate_then_mapping_then_neutral() -> (
    None
):
    assert (
        _resolve_human_edit_candidate_confidence(
            {"field_candidate_confidence": 0.35, "field_mapping_confidence": 0.8},
            neutral_candidate_confidence=0.5,
        )
        == 0.35
    )
    assert (
        _resolve_human_edit_candidate_confidence(
            {"field_mapping_confidence": 0.7},
            neutral_candidate_confidence=0.5,
        )
        == 0.7
    )
    assert (
        _resolve_human_edit_candidate_confidence(
            {"field_mapping_confidence": "bad"},
            neutral_candidate_confidence=0.5,
        )
        == 0.5
    )


def test_sanitize_confidence_breakdown_removes_confidence_and_computes_mapping_confidence() -> None:
    sanitized = _sanitize_confidence_breakdown(
        {
            "confidence": 0.9,
            "text_extraction_reliability": "bad",
            "field_review_history_adjustment": 10,
            "field_candidate_confidence": None,
            "field_mapping_confidence": 0.6,
            "other": "value",
        }
    )

    assert "confidence" not in sanitized
    assert sanitized["text_extraction_reliability"] is None
    assert sanitized["field_review_history_adjustment"] == 10.0
    assert sanitized["field_candidate_confidence"] == 0.6
    assert sanitized["field_mapping_confidence"] == 0.7
    assert sanitized["other"] == "value"


def test_build_field_change_log_contains_expected_contract_fields() -> None:
    event = _build_field_change_log(
        document_id="doc-1",
        run_id="run-1",
        interpretation_id="interp-1",
        base_version_number=1,
        new_version_number=2,
        field_id="field-1",
        field_key="pet_name",
        value_type="string",
        old_value="Luna",
        new_value="Luna II",
        change_type="updated",
        created_at="2026-01-01T00:00:00+00:00",
        occurred_at="2026-01-01T00:00:00+00:00",
        context_key="ctx",
        mapping_id="map-1",
        policy_version="v1",
    )

    assert event["event_type"] == "field_corrected"
    assert event["source"] == "reviewer_edit"
    assert event["field_path"] == "fields.field-1.value"
    assert event["new_version_number"] == 2
    assert isinstance(event["change_id"], str) and event["change_id"]


def test_build_global_schema_from_fields_handles_repeatable_keys_and_empty_values() -> None:
    repeatable_key = next(iter(REPEATABLE_KEYS))
    schema = _build_global_schema_from_fields(
        [
            {"key": "", "value": "ignored"},
            {"key": repeatable_key, "value": []},
            {"key": repeatable_key, "value": "amoxicillin"},
            {"key": repeatable_key, "value": "ibuprofen"},
            {"key": "pet_name", "value": "Luna"},
            {"key": "pet_name", "value": "Should not override"},
            {"key": "owner_name", "value": "   "},
        ]
    )

    assert schema[repeatable_key] == ["amoxicillin", "ibuprofen"]
    assert schema["pet_name"] == "Luna"
    assert schema["owner_name"] is None


def test_is_field_value_empty_detects_none_blank_and_empty_list() -> None:
    assert is_field_value_empty(None)
    assert is_field_value_empty("   ")
    assert is_field_value_empty([])
    assert not is_field_value_empty(0)
    assert not is_field_value_empty(["x"])
