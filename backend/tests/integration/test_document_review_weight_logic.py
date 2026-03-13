"""Integration tests covering document review weight derivation behavior."""

from __future__ import annotations

from uuid import uuid4

from backend.app.domain import models as app_models
from backend.app.infra.file_storage import get_storage_root
from backend.tests.integration.document_review_test_support import (
    _extract_assigned_visits,
    _extract_top_level_fields_by_key,
    _insert_run,
    _insert_structured_interpretation,
    _upload_sample_document,
)


def test_document_review_weight_single_visit_assigned_to_visit_with_derived(test_client):
    """After P1-A: weight with visit-date snippet is assigned to the visit.
    A derived document-scoped weight is also created."""
    document_id = _upload_sample_document(test_client)
    run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    _insert_structured_interpretation(
        run_id=run_id,
        data={
            "document_id": document_id,
            "processing_run_id": run_id,
            "created_at": "2026-02-10T10:00:05+00:00",
            "fields": [
                {
                    "field_id": "f-visit-date-1",
                    "key": "visit_date",
                    "value": "2026-02-11",
                    "value_type": "date",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026"},
                },
                {
                    "field_id": "f-diagnosis-1",
                    "key": "diagnosis",
                    "value": "Otitis",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026: otitis"},
                },
                {
                    "field_id": "f-weight-1",
                    "key": "weight",
                    "value": "7.2 kg",
                    "value_type": "string",
                    "scope": "document",
                    "section": "patient",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026: Peso 7.2 kg"},
                },
            ],
            "visits": [],
            "other_fields": [],
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    data = response.json()["active_interpretation"]["data"]

    # Derived document-scoped weight exists
    top_level_weight_fields = _extract_top_level_fields_by_key(data, "weight")
    assert len(top_level_weight_fields) == 1
    derived = top_level_weight_fields[0]
    assert derived["value"] == "7.2 kg"
    assert derived["origin"] == "derived"

    # Weight is also assigned to the visit
    assigned_visits = _extract_assigned_visits(data.get("visits"))
    assert len(assigned_visits) >= 1
    visit_weight_found = False
    for visit in assigned_visits:
        visit_fields = visit.get("fields", [])
        for f in visit_fields:
            if isinstance(f, dict) and f.get("key") == "weight":
                assert f["value"] == "7.2 kg"
                visit_weight_found = True
    assert visit_weight_found


def test_document_review_weight_multi_visit_derived_is_most_recent(test_client):
    """After P1-A: each visit gets its own weight. The derived document-level
    weight equals the most-recent chronological visit weight (7.8 kg)."""
    document_id = _upload_sample_document(test_client)
    run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    _insert_structured_interpretation(
        run_id=run_id,
        data={
            "document_id": document_id,
            "processing_run_id": run_id,
            "created_at": "2026-02-10T10:00:05+00:00",
            "fields": [
                {
                    "field_id": "f-visit-date-1",
                    "key": "visit_date",
                    "value": "2026-02-11",
                    "value_type": "date",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026"},
                },
                {
                    "field_id": "f-visit-date-2",
                    "key": "visit_date",
                    "value": "2026-02-18",
                    "value_type": "date",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 18/02/2026"},
                },
                {
                    "field_id": "f-diagnosis-1",
                    "key": "diagnosis",
                    "value": "Otitis",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026: otitis"},
                },
                {
                    "field_id": "f-medication-2",
                    "key": "medication",
                    "value": "Gotas",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 18/02/2026: gotas"},
                },
                {
                    "field_id": "f-weight-1",
                    "key": "weight",
                    "value": "7.2 kg",
                    "value_type": "string",
                    "scope": "document",
                    "section": "patient",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026: Peso 7.2 kg"},
                },
                {
                    "field_id": "f-weight-2",
                    "key": "weight",
                    "value": "7.8 kg",
                    "value_type": "string",
                    "scope": "document",
                    "section": "patient",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 18/02/2026: Peso 7.8 kg"},
                },
            ],
            "visits": [],
            "other_fields": [],
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    data = response.json()["active_interpretation"]["data"]

    # Derived document-scoped weight = most recent chronological (7.8 kg)
    top_level_weight_fields = _extract_top_level_fields_by_key(data, "weight")
    assert len(top_level_weight_fields) == 1
    derived = top_level_weight_fields[0]
    assert derived["value"] == "7.8 kg"
    assert derived["origin"] == "derived"

    # Each visit has its own weight
    assigned_visits = _extract_assigned_visits(data.get("visits"))
    assert len(assigned_visits) >= 2
    visit_weights: dict[str, str] = {}
    for visit in assigned_visits:
        vd = visit.get("visit_date")
        for f in visit.get("fields", []):
            if isinstance(f, dict) and f.get("key") == "weight":
                visit_weights[vd] = f["value"]
    assert visit_weights.get("2026-02-11") == "7.2 kg"
    assert visit_weights.get("2026-02-18") == "7.8 kg"


def test_document_review_weight_global_only_stays_document_scoped(test_client):
    """Weight without any visit-context date stays document-scoped (not derived)."""
    document_id = _upload_sample_document(test_client)
    run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    _insert_structured_interpretation(
        run_id=run_id,
        data={
            "document_id": document_id,
            "processing_run_id": run_id,
            "created_at": "2026-02-10T10:00:05+00:00",
            "fields": [
                {
                    "field_id": "f-weight-global",
                    "key": "weight",
                    "value": "7.2 kg",
                    "value_type": "string",
                    "scope": "document",
                    "section": "patient",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Peso: 7.2 kg"},
                }
            ],
            "visits": [],
            "other_fields": [],
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    data = response.json()["active_interpretation"]["data"]

    top_level_weight_fields = _extract_top_level_fields_by_key(data, "weight")
    assert len(top_level_weight_fields) == 1
    # Global weight preserves original origin (not "derived")
    assert top_level_weight_fields[0]["value"] == "7.2 kg"
    assert top_level_weight_fields[0].get("origin") != "derived"

    visits = data.get("visits")
    assert isinstance(visits, list)
    assert visits == []
    for visit in visits:
        if not isinstance(visit, dict):
            continue
        visit_fields = visit.get("fields")
        if not isinstance(visit_fields, list):
            continue
        visit_keys = {field.get("key") for field in visit_fields if isinstance(field, dict)}
        assert "weight" not in visit_keys


def test_document_review_weight_mixed_global_and_visit_prefers_visit_value(test_client):
    """When both global and visit-scoped weight exist, derived value comes from visit."""
    document_id = _upload_sample_document(test_client)
    run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    _insert_structured_interpretation(
        run_id=run_id,
        data={
            "document_id": document_id,
            "processing_run_id": run_id,
            "created_at": "2026-02-10T10:00:05+00:00",
            "fields": [
                {
                    "field_id": "f-weight-global",
                    "key": "weight",
                    "value": "6.5 kg",
                    "value_type": "string",
                    "scope": "document",
                    "section": "patient",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Peso: 6.5 kg"},
                },
                {
                    "field_id": "f-visit-date-1",
                    "key": "visit_date",
                    "value": "2026-02-11",
                    "value_type": "date",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026"},
                },
                {
                    "field_id": "f-weight-visit",
                    "key": "weight",
                    "value": "7.2 kg",
                    "value_type": "string",
                    "scope": "document",
                    "section": "patient",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {
                        "page": 1,
                        "snippet": "Consulta 11/02/2026: Peso 7.2 kg",
                        "offset": 120,
                    },
                },
            ],
            "visits": [],
            "other_fields": [],
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    data = response.json()["active_interpretation"]["data"]

    top_level_weight_fields = _extract_top_level_fields_by_key(data, "weight")
    assert len(top_level_weight_fields) == 1
    derived = top_level_weight_fields[0]
    assert derived["value"] == "7.2 kg"
    assert derived["origin"] == "derived"


def test_document_review_weight_same_date_prefers_highest_offset(test_client):
    """For same visit_date weights, choose deterministic winner using evidence offset."""
    document_id = _upload_sample_document(test_client)
    run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    _insert_structured_interpretation(
        run_id=run_id,
        data={
            "document_id": document_id,
            "processing_run_id": run_id,
            "created_at": "2026-02-10T10:00:05+00:00",
            "fields": [
                {
                    "field_id": "f-visit-date-1",
                    "key": "visit_date",
                    "value": "2026-02-11",
                    "value_type": "date",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026"},
                },
                {
                    "field_id": "f-weight-early",
                    "key": "weight",
                    "value": "7.0 kg",
                    "value_type": "string",
                    "scope": "document",
                    "section": "patient",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {
                        "page": 1,
                        "snippet": "Consulta 11/02/2026: Peso 7.0 kg",
                        "offset": 30,
                    },
                },
                {
                    "field_id": "f-weight-late",
                    "key": "weight",
                    "value": "7.4 kg",
                    "value_type": "string",
                    "scope": "document",
                    "section": "patient",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {
                        "page": 1,
                        "snippet": "Consulta 11/02/2026: Peso 7.4 kg",
                        "offset": 90,
                    },
                },
            ],
            "visits": [],
            "other_fields": [],
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    data = response.json()["active_interpretation"]["data"]

    top_level_weight_fields = _extract_top_level_fields_by_key(data, "weight")
    assert len(top_level_weight_fields) == 1
    derived = top_level_weight_fields[0]
    assert derived["value"] == "7.4 kg"
    assert derived["origin"] == "derived"


def test_document_review_weight_uses_evidence_date_when_visit_date_is_not_normalizable(test_client):
    """Most-recent selection should fallback to evidence date.

    Applies when visit_date is non-normalizable.
    """
    document_id = _upload_sample_document(test_client)
    run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    _insert_structured_interpretation(
        run_id=run_id,
        data={
            "document_id": document_id,
            "processing_run_id": run_id,
            "created_at": "2026-02-10T10:00:05+00:00",
            "fields": [
                {
                    "field_id": "f-diagnosis-trigger",
                    "key": "diagnosis",
                    "value": "Otitis",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026: otitis"},
                }
            ],
            "visits": [
                {
                    "visit_id": "visit-001",
                    "visit_date": "2026-02-11",
                    "admission_date": None,
                    "discharge_date": None,
                    "reason_for_visit": None,
                    "fields": [
                        {
                            "field_id": "f-weight-v1",
                            "key": "weight",
                            "value": "7.0 kg",
                            "value_type": "string",
                            "scope": "visit",
                            "section": "visits",
                            "classification": "medical_record",
                            "origin": "machine",
                            "evidence": {"page": 1, "snippet": "Consulta 11/02/2026: Peso 7.0 kg"},
                        }
                    ],
                },
                {
                    "visit_id": "visit-002",
                    "visit_date": "2026-02-18",
                    "admission_date": None,
                    "discharge_date": None,
                    "reason_for_visit": None,
                    "fields": [
                        {
                            "field_id": "f-weight-v2",
                            "key": "weight",
                            "value": "7.2 kg",
                            "value_type": "string",
                            "scope": "visit",
                            "section": "visits",
                            "classification": "medical_record",
                            "origin": "machine",
                            "evidence": {"page": 1, "snippet": "Consulta 18/02/2026: Peso 7.2 kg"},
                        }
                    ],
                },
                {
                    "visit_id": "visit-003",
                    "visit_date": "viernes veinticinco de febrero",
                    "admission_date": None,
                    "discharge_date": None,
                    "reason_for_visit": None,
                    "fields": [
                        {
                            "field_id": "f-weight-v3",
                            "key": "weight",
                            "value": "7.8 kg",
                            "value_type": "string",
                            "scope": "visit",
                            "section": "visits",
                            "classification": "medical_record",
                            "origin": "machine",
                            "evidence": {"page": 1, "snippet": "Consulta 25/02/2026: Peso 7.8 kg"},
                        }
                    ],
                },
            ],
            "other_fields": [],
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    data = response.json()["active_interpretation"]["data"]

    top_level_weight_fields = _extract_top_level_fields_by_key(data, "weight")
    assert len(top_level_weight_fields) == 1
    derived = top_level_weight_fields[0]
    assert derived["value"] == "7.8 kg"
    assert derived["origin"] == "derived"


def test_document_review_weight_unassigned_latest_by_evidence_overrides_middle_visit(test_client):
    """If latest weight lands in unassigned but has a newer evidence date, it must win."""
    document_id = _upload_sample_document(test_client)
    run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    _insert_structured_interpretation(
        run_id=run_id,
        data={
            "document_id": document_id,
            "processing_run_id": run_id,
            "created_at": "2026-02-10T10:00:05+00:00",
            "fields": [
                {
                    "field_id": "f-diagnosis-trigger-unassigned",
                    "key": "diagnosis",
                    "value": "Otitis",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026: otitis"},
                }
            ],
            "visits": [
                {
                    "visit_id": "visit-001",
                    "visit_date": "2026-02-11",
                    "admission_date": None,
                    "discharge_date": None,
                    "reason_for_visit": None,
                    "fields": [
                        {
                            "field_id": "f-weight-v1",
                            "key": "weight",
                            "value": "7.0 kg",
                            "value_type": "string",
                            "scope": "visit",
                            "section": "visits",
                            "classification": "medical_record",
                            "origin": "machine",
                            "evidence": {"page": 1, "snippet": "Consulta 11/02/2026: Peso 7.0 kg"},
                        }
                    ],
                },
                {
                    "visit_id": "visit-002",
                    "visit_date": "2026-02-18",
                    "admission_date": None,
                    "discharge_date": None,
                    "reason_for_visit": None,
                    "fields": [
                        {
                            "field_id": "f-weight-v2",
                            "key": "weight",
                            "value": "7.2 kg",
                            "value_type": "string",
                            "scope": "visit",
                            "section": "visits",
                            "classification": "medical_record",
                            "origin": "machine",
                            "evidence": {"page": 1, "snippet": "Consulta 18/02/2026: Peso 7.2 kg"},
                        }
                    ],
                },
                {
                    "visit_id": "unassigned",
                    "visit_date": None,
                    "admission_date": None,
                    "discharge_date": None,
                    "reason_for_visit": None,
                    "fields": [
                        {
                            "field_id": "f-weight-unassigned-late",
                            "key": "weight",
                            "value": "7.8 kg",
                            "value_type": "string",
                            "scope": "visit",
                            "section": "visits",
                            "classification": "medical_record",
                            "origin": "machine",
                            "evidence": {"page": 1, "snippet": "Consulta 25/02/2026: Peso 7.8 kg"},
                        }
                    ],
                },
            ],
            "other_fields": [],
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    data = response.json()["active_interpretation"]["data"]

    top_level_weight_fields = _extract_top_level_fields_by_key(data, "weight")
    assert len(top_level_weight_fields) == 1
    derived = top_level_weight_fields[0]
    assert derived["value"] == "7.8 kg"
    assert derived["origin"] == "derived"


def test_document_review_weight_ambiguous_date_generates_visit_with_derived(test_client):
    """After P1-A: weight snippet with a visit-context date that doesn't match
    an existing visit generates a new visit. The derived document-level weight
    is derived from the most-recent visit weight."""
    document_id = _upload_sample_document(test_client)
    run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    _insert_structured_interpretation(
        run_id=run_id,
        data={
            "document_id": document_id,
            "processing_run_id": run_id,
            "created_at": "2026-02-10T10:00:05+00:00",
            "fields": [
                {
                    "field_id": "f-visit-date-1",
                    "key": "visit_date",
                    "value": "2026-02-11",
                    "value_type": "date",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026"},
                },
                {
                    "field_id": "f-diagnosis-1",
                    "key": "diagnosis",
                    "value": "Otitis",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026: otitis"},
                },
                {
                    "field_id": "f-weight-ambiguous",
                    "key": "weight",
                    "value": "8.0 kg",
                    "value_type": "string",
                    "scope": "document",
                    "section": "patient",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 20/02/2026: Peso 8.0 kg"},
                },
            ],
            "visits": [],
            "other_fields": [],
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    data = response.json()["active_interpretation"]["data"]

    # Derived document-scoped weight exists (from the most recent visit)
    top_level_weight_fields = _extract_top_level_fields_by_key(data, "weight")
    assert len(top_level_weight_fields) == 1
    derived = top_level_weight_fields[0]
    assert derived["value"] == "8 kg"
    assert derived["origin"] == "derived"

    # A visit was generated for 2026-02-20, weight assigned there
    assigned_visits = _extract_assigned_visits(data.get("visits"))
    assert len(assigned_visits) >= 2
    visit_weight_found = False
    for visit in assigned_visits:
        for f in visit.get("fields", []):
            if isinstance(f, dict) and f.get("key") == "weight":
                assert f["value"] == "8.0 kg"
                visit_weight_found = True
    assert visit_weight_found


def test_document_review_weight_absent_means_no_weight_field(test_client):
    """When no weight field exists, no document-level or visit-level weight appears."""
    document_id = _upload_sample_document(test_client)
    run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    _insert_structured_interpretation(
        run_id=run_id,
        data={
            "document_id": document_id,
            "processing_run_id": run_id,
            "created_at": "2026-02-10T10:00:05+00:00",
            "fields": [
                {
                    "field_id": "f-visit-date-1",
                    "key": "visit_date",
                    "value": "2026-02-11",
                    "value_type": "date",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026"},
                },
                {
                    "field_id": "f-diagnosis-1",
                    "key": "diagnosis",
                    "value": "Otitis",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026: otitis"},
                },
            ],
            "visits": [],
            "other_fields": [],
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    data = response.json()["active_interpretation"]["data"]

    top_level_weight_fields = _extract_top_level_fields_by_key(data, "weight")
    assert len(top_level_weight_fields) == 0

    assigned_visits = _extract_assigned_visits(data.get("visits"))
    for visit in assigned_visits:
        for f in visit.get("fields", []):
            if isinstance(f, dict):
                assert f.get("key") != "weight"



def test_document_review_derives_latest_weight_from_raw_timeline_without_seed_visit_fields(
    test_client,
):
    document_id = _upload_sample_document(test_client)
    run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    _insert_structured_interpretation(
        run_id=run_id,
        data={
            "document_id": document_id,
            "processing_run_id": run_id,
            "created_at": "2026-02-10T10:00:05+00:00",
            "fields": [
                {
                    "field_id": "f-weight-global",
                    "key": "weight",
                    "value": "6.3kg",
                    "value_type": "string",
                    "scope": "document",
                    "section": "patient",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "peso 6.3kg"},
                }
            ],
            "visits": [],
            "other_fields": [],
        },
    )

    raw_text_path = get_storage_root() / document_id / "runs" / run_id / "raw-text.txt"
    raw_text_path.parent.mkdir(parents=True, exist_ok=True)
    raw_text_path.write_text(
        (
            "- 08/12/19 - 16:12 -\n"
            "4.1kg\n"
            "- 28/12/19 - 10:44 -\n"
            "peso 6.3kg\n"
            "- 19/09/20 - 09:40 -\n"
            "29.6kg\n"
        ),
        encoding="utf-8",
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    data = response.json()["active_interpretation"]["data"]

    top_level_weight_fields = _extract_top_level_fields_by_key(data, "weight")
    assert len(top_level_weight_fields) == 1
    assert top_level_weight_fields[0].get("value") == "29.6 kg"


