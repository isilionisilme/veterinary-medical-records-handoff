"""Unit tests for weight post-processing helpers in visit_helpers.py."""

from __future__ import annotations

from backend.app.application.documents.visit_helpers import (
    _build_raw_text_weight_candidate,
    _collect_assigned_visit_weight_candidates,
    _collect_unassigned_date_weight_candidates,
    _collect_unassigned_weight_candidates,
    _select_and_derive_weight,
    postprocess_weights,
    resolve_visit_from_anchor,
)

# ---------------------------------------------------------------------------
# _collect_unassigned_weight_candidates
# ---------------------------------------------------------------------------


class TestCollectUnassignedWeightCandidates:
    def test_returns_empty_when_no_unassigned_visit(self) -> None:
        ftk: list[object] = [{"key": "name", "value": "Luna"}]
        result = _collect_unassigned_weight_candidates(unassigned_visit=None, fields_to_keep=ftk)
        assert result == []
        assert len(ftk) == 1

    def test_returns_empty_when_fields_not_list(self) -> None:
        visit: dict[str, object] = {"fields": "not-a-list"}
        ftk: list[object] = []
        result = _collect_unassigned_weight_candidates(unassigned_visit=visit, fields_to_keep=ftk)
        assert result == []

    def test_returns_empty_when_no_weight_fields(self) -> None:
        visit: dict[str, object] = {"fields": [{"key": "name", "value": "Luna"}]}
        ftk: list[object] = []
        result = _collect_unassigned_weight_candidates(unassigned_visit=visit, fields_to_keep=ftk)
        assert result == []
        assert len(ftk) == 0

    def test_restores_weight_fields_to_document_scope(self) -> None:
        wf: dict[str, object] = {"key": "weight", "value": "3,5 kg"}
        visit: dict[str, object] = {
            "fields": [wf, {"key": "name", "value": "Luna"}],
        }
        ftk: list[object] = []
        result = _collect_unassigned_weight_candidates(unassigned_visit=visit, fields_to_keep=ftk)

        assert len(result) == 1
        assert result[0]["scope"] == "document"
        assert result[0]["section"] == "patient"
        # Normalized value
        assert result[0]["value"] == "3.5 kg"
        # Appended to fields_to_keep
        assert len(ftk) == 1
        assert ftk[0] is result[0]
        # Weight removed from unassigned visit
        assert all(f.get("key") != "weight" for f in visit["fields"])

    def test_preserves_raw_value_when_normalization_fails(self) -> None:
        wf: dict[str, object] = {"key": "weight", "value": "unknown"}
        visit: dict[str, object] = {"fields": [wf]}
        ftk: list[object] = []
        result = _collect_unassigned_weight_candidates(unassigned_visit=visit, fields_to_keep=ftk)
        assert result[0]["value"] == "unknown"


# ---------------------------------------------------------------------------
# _collect_assigned_visit_weight_candidates
# ---------------------------------------------------------------------------


class TestCollectAssignedVisitWeightCandidates:
    def test_returns_empty_for_no_visits(self) -> None:
        assert _collect_assigned_visit_weight_candidates(assigned_visits=[]) == []

    def test_returns_empty_when_fields_not_list(self) -> None:
        visits = [{"visit_date": "2025-01-01", "fields": None}]
        assert _collect_assigned_visit_weight_candidates(assigned_visits=visits) == []

    def test_skips_weight_without_resolvable_date(self) -> None:
        visits = [
            {
                "visit_date": None,
                "fields": [{"key": "weight", "value": "5 kg"}],
            }
        ]
        assert _collect_assigned_visit_weight_candidates(assigned_visits=visits) == []

    def test_collects_weight_with_valid_date(self) -> None:
        field: dict[str, object] = {"key": "weight", "value": "5 kg"}
        visits: list[dict[str, object]] = [
            {"visit_date": "2025-03-10", "fields": [field]},
        ]
        result = _collect_assigned_visit_weight_candidates(assigned_visits=visits)
        assert len(result) == 1
        date, _, visit_idx, field_idx, fld = result[0]
        assert date == "2025-03-10"
        assert visit_idx == 0
        assert field_idx == 0
        assert fld is field

    def test_collects_multiple_visits(self) -> None:
        visits: list[dict[str, object]] = [
            {
                "visit_date": "2025-01-10",
                "fields": [{"key": "weight", "value": "4 kg"}],
            },
            {
                "visit_date": "2025-03-10",
                "fields": [{"key": "weight", "value": "5 kg"}],
            },
        ]
        result = _collect_assigned_visit_weight_candidates(assigned_visits=visits)
        assert len(result) == 2
        assert result[0][0] == "2025-01-10"
        assert result[1][0] == "2025-03-10"


# ---------------------------------------------------------------------------
# _collect_unassigned_date_weight_candidates
# ---------------------------------------------------------------------------


class TestCollectUnassignedDateWeightCandidates:
    def test_returns_empty_for_no_fields(self) -> None:
        assert (
            _collect_unassigned_date_weight_candidates(
                unassigned_weight_fields=[], assigned_visit_count=0
            )
            == []
        )

    def test_skips_field_without_date_evidence(self) -> None:
        field: dict[str, object] = {"key": "weight", "value": "5 kg"}
        result = _collect_unassigned_date_weight_candidates(
            unassigned_weight_fields=[field], assigned_visit_count=1
        )
        assert result == []

    def test_collects_field_with_date_evidence(self) -> None:
        field: dict[str, object] = {
            "key": "weight",
            "value": "5 kg",
            "evidence": {"snippet": "10/03/2025 - Peso: 5 kg"},
        }
        result = _collect_unassigned_date_weight_candidates(
            unassigned_weight_fields=[field], assigned_visit_count=2
        )
        assert len(result) == 1
        date, _, visit_idx, field_idx, fld = result[0]
        assert date == "2025-03-10"
        assert visit_idx == 2  # equals assigned_visit_count
        assert field_idx == 0
        assert fld is field


# ---------------------------------------------------------------------------
# _build_raw_text_weight_candidate
# ---------------------------------------------------------------------------


class TestBuildRawTextWeightCandidate:
    def test_returns_none_for_no_raw_text(self) -> None:
        assert _build_raw_text_weight_candidate(raw_text=None, base_index=0) is None

    def test_returns_none_for_empty_raw_text(self) -> None:
        assert _build_raw_text_weight_candidate(raw_text="", base_index=0) is None

    def test_returns_none_when_no_weight_found(self) -> None:
        result = _build_raw_text_weight_candidate(
            raw_text="Some text without weight data", base_index=0
        )
        assert result is None

    def test_extracts_candidate_from_raw_text(self) -> None:
        raw = "- 10/03/2025 - 14:30\nPeso: 5 kg\n"
        result = _build_raw_text_weight_candidate(raw_text=raw, base_index=3)
        assert result is not None
        date, offset, visit_idx, field_idx, field_dict = result
        assert date == "2025-03-10"
        assert offset == -1.0
        assert visit_idx == 3
        assert field_idx == 0
        assert field_dict["value"] == "5 kg"
        assert field_dict["value_type"] == "string"
        assert field_dict["classification"] == "medical_record"


class TestResolveVisitFromAnchor:
    def test_prefers_candidate_within_visit_boundaries(self) -> None:
        visit_a = {"visit_id": "visit-001", "visit_date": "2025-03-10"}
        visit_b = {"visit_id": "visit-002", "visit_date": "2025-03-12"}

        resolved = resolve_visit_from_anchor(
            candidate_dates=["2025-03-10", "2025-03-12"],
            anchor_offset=140,
            visit_by_date={"2025-03-10": visit_a, "2025-03-12": visit_b},
            visit_occurrences_by_date={"2025-03-10": [visit_a], "2025-03-12": [visit_b]},
            raw_text_offsets_by_date={"2025-03-10": [20], "2025-03-12": [150]},
            visit_boundary_offsets=[0, 120, 220],
        )

        assert resolved is visit_b

    def test_falls_back_to_nearest_offset_without_boundaries(self) -> None:
        visit_a = {"visit_id": "visit-001", "visit_date": "2025-03-10"}
        visit_b = {"visit_id": "visit-002", "visit_date": "2025-03-12"}

        resolved = resolve_visit_from_anchor(
            candidate_dates=["2025-03-10", "2025-03-12"],
            anchor_offset=88,
            visit_by_date={"2025-03-10": visit_a, "2025-03-12": visit_b},
            visit_occurrences_by_date={"2025-03-10": [visit_a], "2025-03-12": [visit_b]},
            raw_text_offsets_by_date={"2025-03-10": [15], "2025-03-12": [90]},
            visit_boundary_offsets=[],
        )

        assert resolved is visit_b


# ---------------------------------------------------------------------------
# _select_and_derive_weight
# ---------------------------------------------------------------------------


class TestSelectAndDeriveWeight:
    def test_returns_unchanged_when_no_candidates(self) -> None:
        ftk: list[object] = [{"key": "name", "value": "Luna"}]
        result = _select_and_derive_weight(visit_weights=[], fields_to_keep=ftk)
        assert result is ftk
        assert len(result) == 1

    def test_derives_from_single_candidate(self) -> None:
        candidate = (
            "2025-03-10",
            0.0,
            0,
            0,
            {"value": "5 kg", "value_type": "string", "classification": "medical_record"},
        )
        ftk: list[object] = [{"key": "name", "value": "Luna"}]
        result = _select_and_derive_weight(visit_weights=[candidate], fields_to_keep=ftk)
        weights = [f for f in result if isinstance(f, dict) and f.get("key") == "weight"]
        assert len(weights) == 1
        assert weights[0]["field_id"] == "derived-weight-current"
        assert weights[0]["origin"] == "derived"
        assert weights[0]["scope"] == "document"
        assert weights[0]["value"] == "5 kg"

    def test_selects_most_recent_by_date(self) -> None:
        older = (
            "2025-01-01",
            0.0,
            0,
            0,
            {"value": "4 kg", "value_type": "string"},
        )
        newer = (
            "2025-03-10",
            0.0,
            1,
            0,
            {"value": "5.5 kg", "value_type": "string"},
        )
        result = _select_and_derive_weight(visit_weights=[newer, older], fields_to_keep=[])
        weights = [f for f in result if isinstance(f, dict) and f.get("key") == "weight"]
        assert weights[0]["value"] == "5.5 kg"

    def test_removes_existing_weight_fields(self) -> None:
        candidate = (
            "2025-03-10",
            0.0,
            0,
            0,
            {"value": "5 kg", "value_type": "string"},
        )
        ftk: list[object] = [
            {"key": "weight", "value": "old"},
            {"key": "name", "value": "Luna"},
        ]
        result = _select_and_derive_weight(visit_weights=[candidate], fields_to_keep=ftk)
        weight_fields = [f for f in result if isinstance(f, dict) and f.get("key") == "weight"]
        assert len(weight_fields) == 1
        assert weight_fields[0]["value"] == "5 kg"

    def test_normalizes_derived_value(self) -> None:
        candidate = (
            "2025-03-10",
            0.0,
            0,
            0,
            {"value": "3,5 kg", "value_type": "string"},
        )
        result = _select_and_derive_weight(visit_weights=[candidate], fields_to_keep=[])
        weights = [f for f in result if isinstance(f, dict) and f.get("key") == "weight"]
        assert weights[0]["value"] == "3.5 kg"


# ---------------------------------------------------------------------------
# postprocess_weights (orchestrator end-to-end)
# ---------------------------------------------------------------------------


class TestPostprocessWeights:
    def test_no_weight_data_returns_unchanged(self) -> None:
        ftk: list[object] = [{"key": "name", "value": "Luna"}]
        result = postprocess_weights(
            fields_to_keep=ftk,
            assigned_visits=[],
            unassigned_visit=None,
            raw_text=None,
        )
        assert result == [{"key": "name", "value": "Luna"}]

    def test_weight_from_unassigned_visit_with_date_evidence(self) -> None:
        wf: dict[str, object] = {
            "key": "weight",
            "value": "5 kg",
            "evidence": {"snippet": "10/03/2025 - Peso: 5 kg"},
        }
        visit: dict[str, object] = {"fields": [wf]}
        result = postprocess_weights(
            fields_to_keep=[],
            assigned_visits=[],
            unassigned_visit=visit,
            raw_text=None,
        )
        weights = [f for f in result if isinstance(f, dict) and f.get("key") == "weight"]
        assert len(weights) == 1
        assert weights[0]["field_id"] == "derived-weight-current"
        assert weights[0]["origin"] == "derived"

    def test_weight_from_assigned_visit_only(self) -> None:
        result = postprocess_weights(
            fields_to_keep=[],
            assigned_visits=[
                {
                    "visit_date": "2025-03-10",
                    "fields": [{"key": "weight", "value": "5 kg"}],
                },
            ],
            unassigned_visit=None,
            raw_text=None,
        )
        weights = [f for f in result if isinstance(f, dict) and f.get("key") == "weight"]
        assert len(weights) == 1
        assert weights[0]["value"] == "5 kg"
        assert weights[0]["origin"] == "derived"

    def test_weight_from_raw_text_only(self) -> None:
        raw = "- 10/03/2025 - 14:30\nPeso: 5 kg\n"
        result = postprocess_weights(
            fields_to_keep=[],
            assigned_visits=[],
            unassigned_visit=None,
            raw_text=raw,
        )
        weights = [f for f in result if isinstance(f, dict) and f.get("key") == "weight"]
        assert len(weights) == 1
        assert weights[0]["origin"] == "derived"

    def test_all_sources_selects_most_recent(self) -> None:
        # Assigned visit has older date
        assigned: list[dict[str, object]] = [
            {
                "visit_date": "2025-01-01",
                "fields": [{"key": "weight", "value": "4 kg"}],
            },
        ]
        # Raw text has a newer date
        raw = "- 10/03/2025 - 14:30\nPeso: 6 kg\n"
        result = postprocess_weights(
            fields_to_keep=[],
            assigned_visits=assigned,
            unassigned_visit=None,
            raw_text=raw,
        )
        weights = [f for f in result if isinstance(f, dict) and f.get("key") == "weight"]
        assert len(weights) == 1
        # The raw text date (2025-03-10) is more recent than assigned (2025-01-01)
        assert weights[0]["value"] == "6 kg"

    def test_normalization_applied_to_derived_value(self) -> None:
        result = postprocess_weights(
            fields_to_keep=[],
            assigned_visits=[
                {
                    "visit_date": "2025-03-10",
                    "fields": [{"key": "weight", "value": "3,5 kg"}],
                },
            ],
            unassigned_visit=None,
            raw_text=None,
        )
        weights = [f for f in result if isinstance(f, dict) and f.get("key") == "weight"]
        assert weights[0]["value"] == "3.5 kg"

    def test_unassigned_weight_without_date_not_derived(self) -> None:
        """Unassigned weight with no date evidence is added to fields_to_keep
        but not selected as the derived weight (no candidate created)."""
        wf: dict[str, object] = {"key": "weight", "value": "5 kg"}
        visit: dict[str, object] = {"fields": [wf]}
        result = postprocess_weights(
            fields_to_keep=[],
            assigned_visits=[],
            unassigned_visit=visit,
            raw_text=None,
        )
        # No candidates → weight fields returned as-is (document-scoped)
        weights = [f for f in result if isinstance(f, dict) and f.get("key") == "weight"]
        assert len(weights) == 1
        assert weights[0]["scope"] == "document"
        assert weights[0].get("origin") is None  # not derived

    def test_mutations_on_unassigned_visit(self) -> None:
        """Verifies that weight fields are removed from unassigned_visit."""
        wf: dict[str, object] = {"key": "weight", "value": "5 kg"}
        nf: dict[str, object] = {"key": "name", "value": "Luna"}
        visit: dict[str, object] = {"fields": [wf, nf]}
        postprocess_weights(
            fields_to_keep=[],
            assigned_visits=[],
            unassigned_visit=visit,
            raw_text=None,
        )
        remaining = visit["fields"]
        assert isinstance(remaining, list)
        assert all(f.get("key") != "weight" for f in remaining)
        assert len(remaining) == 1
