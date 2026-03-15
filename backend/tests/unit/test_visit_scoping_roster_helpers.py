"""Unit tests for extracted helpers in visit_scoping.py (Q-11)."""

from __future__ import annotations

from backend.app.application.documents.visit_scoping import (
    _classify_fields_into_scopes,
    _generate_missing_visits,
    _parse_existing_visits,
    _should_scope_weight_as_visit,
)


class TestShouldScopeWeightAsVisit:
    def test_returns_true_for_explicit_visit_scope(self) -> None:
        cache: dict[str, list[str]] = {}

        assert _should_scope_weight_as_visit(
            {"key": "weight", "scope": "visit", "section": "patient"},
            snippet_date_cache=cache,
        )

    def test_returns_true_for_weight_with_date_evidence(self) -> None:
        cache: dict[str, list[str]] = {}

        assert _should_scope_weight_as_visit(
            {
                "key": "weight",
                "value": "7.2 kg",
                "evidence": {"snippet": "Consulta 10/03/2025: Peso 7.2 kg"},
            },
            snippet_date_cache=cache,
        )

    def test_returns_false_for_document_weight_without_visit_context(self) -> None:
        cache: dict[str, list[str]] = {}

        assert not _should_scope_weight_as_visit(
            {
                "key": "weight",
                "value": "7.2 kg",
                "evidence": {"snippet": "Paciente estable. Peso actual: 7.2 kg"},
            },
            snippet_date_cache=cache,
        )


class TestClassifyFieldsIntoScopes:
    def test_keeps_global_weight_document_scoped(self) -> None:
        result = _classify_fields_into_scopes(
            [{"key": "weight", "value": "7.2 kg", "evidence": {"snippet": "Peso actual: 7.2 kg"}}],
            raw_text_detected_visit_dates=[],
        )

        assert len(result.fields_to_keep) == 1
        assert result.visit_scoped_fields == []

    def test_promotes_weight_with_visit_date_evidence(self) -> None:
        result = _classify_fields_into_scopes(
            [
                {
                    "key": "weight",
                    "value": "7.2 kg",
                    "evidence": {"snippet": "Consulta 10/03/2025: Peso 7.2 kg"},
                }
            ],
            raw_text_detected_visit_dates=[],
        )

        assert result.fields_to_keep == []
        assert len(result.visit_scoped_fields) == 1
        assert result.visit_scoped_fields[0]["scope"] == "visit"
        assert result.detected_visit_dates == ["2025-03-10"]


class TestParseExistingVisits:
    """Tests for _parse_existing_visits."""

    def test_multiple_visits_with_dates(self) -> None:
        projected = {
            "visits": [
                {"visit_id": "visit-001", "visit_date": "2024-01-15", "fields": []},
                {"visit_id": "visit-002", "visit_date": "2024-02-20", "fields": []},
            ]
        }
        detected: list[str] = []
        seen: set[str] = set()
        assigned, by_date, occ_by_date, unassigned = _parse_existing_visits(
            projected, detected_visit_dates=detected, seen_detected_visit_dates=seen
        )
        assert len(assigned) == 2
        assert "2024-01-15" in by_date
        assert "2024-02-20" in by_date
        assert unassigned is None
        assert set(detected) == {"2024-01-15", "2024-02-20"}

    def test_unassigned_visit_handling(self) -> None:
        projected = {
            "visits": [
                {"visit_id": "unassigned", "fields": ["f1"]},
                {"visit_id": "visit-001", "visit_date": "2024-03-01", "fields": []},
            ]
        }
        detected: list[str] = []
        seen: set[str] = set()
        assigned, _by_date, _occ, unassigned = _parse_existing_visits(
            projected, detected_visit_dates=detected, seen_detected_visit_dates=seen
        )
        assert len(assigned) == 1
        assert unassigned is not None
        assert unassigned["visit_id"] == "unassigned"

    def test_date_normalization(self) -> None:
        projected = {
            "visits": [
                {"visit_id": "visit-001", "visit_date": "15/01/2024", "fields": []},
            ]
        }
        detected: list[str] = []
        seen: set[str] = set()
        assigned, by_date, _occ, _unassigned = _parse_existing_visits(
            projected, detected_visit_dates=detected, seen_detected_visit_dates=seen
        )
        assert len(assigned) == 1
        # Normalized date should be in the lookup (exact format depends on normalizer)
        assert len(by_date) == 1

    def test_duplicate_date_handling(self) -> None:
        projected = {
            "visits": [
                {"visit_id": "visit-001", "visit_date": "2024-01-15", "fields": []},
                {"visit_id": "visit-002", "visit_date": "2024-01-15", "fields": []},
            ]
        }
        detected: list[str] = []
        seen: set[str] = set()
        assigned, by_date, occ_by_date, _unassigned = _parse_existing_visits(
            projected, detected_visit_dates=detected, seen_detected_visit_dates=seen
        )
        assert len(assigned) == 2
        assert len(occ_by_date.get("2024-01-15", [])) == 2
        # by_date keeps first occurrence only (setdefault)
        assert by_date["2024-01-15"]["visit_id"] == "visit-001"


class TestGenerateMissingVisits:
    """Tests for _generate_missing_visits."""

    def test_single_missing_date(self) -> None:
        assigned: list[dict[str, object]] = []
        by_date: dict[str, dict[str, object]] = {}
        occ: dict[str, list[dict[str, object]]] = {}
        _generate_missing_visits(
            assigned_visits=assigned,
            visit_by_date=by_date,
            visit_occurrences_by_date=occ,
            detected_visit_dates=["2024-06-01"],
            raw_text_detected_visit_dates=["2024-06-01"],
        )
        assert len(assigned) == 1
        assert assigned[0]["visit_date"] == "2024-06-01"
        assert assigned[0]["visit_id"] == "visit-001"

    def test_multiple_occurrences_of_same_date(self) -> None:
        assigned: list[dict[str, object]] = []
        by_date: dict[str, dict[str, object]] = {}
        occ: dict[str, list[dict[str, object]]] = {}
        _generate_missing_visits(
            assigned_visits=assigned,
            visit_by_date=by_date,
            visit_occurrences_by_date=occ,
            detected_visit_dates=["2024-06-01"],
            raw_text_detected_visit_dates=["2024-06-01", "2024-06-01", "2024-06-01"],
        )
        # 3 occurrences in raw text → 1 base + 2 extra = 3 total
        assert len(assigned) == 3
        dates = [v["visit_date"] for v in assigned]
        assert all(d == "2024-06-01" for d in dates)

    def test_all_dates_already_present(self) -> None:
        existing = {"visit_id": "visit-001", "visit_date": "2024-06-01", "fields": []}
        assigned: list[dict[str, object]] = [existing]
        by_date = {"2024-06-01": existing}
        occ: dict[str, list[dict[str, object]]] = {"2024-06-01": [existing]}
        _generate_missing_visits(
            assigned_visits=assigned,
            visit_by_date=by_date,
            visit_occurrences_by_date=occ,
            detected_visit_dates=["2024-06-01"],
            raw_text_detected_visit_dates=["2024-06-01"],
        )
        assert len(assigned) == 1  # No new visits generated
