"""Unit tests for extracted helpers in visit_population.py (Q-8)."""

from __future__ import annotations

from backend.app.application.documents.visit_population import (
    _build_derived_visit_field,
    _select_best_candidate_for_key,
)


class TestSelectBestCandidateForKey:
    """Tests for _select_best_candidate_for_key."""

    def test_returns_first_dict_candidate_for_non_weight_key(self) -> None:
        candidates = [
            {"value": "Labrador", "evidence": {"snippet": "Labrador"}},
            {"value": "Golden", "evidence": {"snippet": "Golden"}},
        ]
        result = _select_best_candidate_for_key("breed", candidates)
        assert result is not None
        assert result["value"] == "Labrador"

    def test_weight_selects_max_offset(self) -> None:
        candidates = [
            {"value": "5 kg", "evidence": {"offset": 10}},
            {"value": "8 kg", "evidence": {"offset": 50}},
            {"value": "3 kg", "evidence": {"offset": 30}},
        ]
        result = _select_best_candidate_for_key("weight", candidates)
        assert result is not None
        assert result["value"] == "8 kg"

    def test_weight_fallback_when_no_offset(self) -> None:
        candidates = [
            {"value": "5 kg", "evidence": {}},
            {"value": "8 kg", "evidence": {"snippet": "8kg"}},
        ]
        result = _select_best_candidate_for_key("weight", candidates)
        assert result is not None
        # Both have offset=-1.0 fallback, max picks first dict encountered by max()
        assert result["value"] in {"5 kg", "8 kg"}

    def test_empty_list_returns_none(self) -> None:
        assert _select_best_candidate_for_key("breed", []) is None

    def test_non_dict_candidate_returns_none(self) -> None:
        assert _select_best_candidate_for_key("breed", ["not-a-dict"]) is None

    def test_empty_value_returns_none(self) -> None:
        candidates = [{"value": "  ", "evidence": {}}]
        assert _select_best_candidate_for_key("breed", candidates) is None

    def test_missing_value_returns_none(self) -> None:
        candidates = [{"evidence": {"snippet": "something"}}]
        assert _select_best_candidate_for_key("breed", candidates) is None


class TestBuildDerivedVisitField:
    """Tests for _build_derived_visit_field."""

    def test_builds_correct_structure(self) -> None:
        candidate = {"value": "Labrador", "evidence": {"snippet": "Lab"}}
        result = _build_derived_visit_field("breed", "visit-1", candidate)

        assert result["field_id"] == "derived-breed-visit-1"
        assert result["key"] == "breed"
        assert result["value"] == "Labrador"
        assert result["value_type"] == "string"
        assert result["scope"] == "visit"
        assert result["section"] == "visits"
        assert result["classification"] == "medical_record"
        assert result["origin"] == "derived"
        assert result["evidence"] == {"snippet": "Lab"}

    def test_non_dict_evidence_becomes_none(self) -> None:
        candidate = {"value": "5kg", "evidence": "not-a-dict"}
        result = _build_derived_visit_field("weight", "v-2", candidate)
        assert result["evidence"] is None

    def test_missing_evidence_becomes_none(self) -> None:
        candidate = {"value": "5kg"}
        result = _build_derived_visit_field("weight", "v-3", candidate)
        assert result["evidence"] is None
