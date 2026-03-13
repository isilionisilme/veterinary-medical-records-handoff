"""Integration tests covering ambiguous or non-visit date assignment guards.

Scenario focus: preserving unassigned state for ambiguous or non-visit dates.
"""

from __future__ import annotations

from uuid import uuid4

from backend.app.domain import models as app_models
from backend.app.infra.file_storage import get_storage_root
from backend.tests.integration.document_review_test_support import (
    _insert_run,
    _insert_structured_interpretation,
    _upload_sample_document,
)


def test_document_review_non_visit_dates_do_not_create_assigned_visits(test_client):
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
                    "field_id": "f-diagnosis",
                    "key": "diagnosis",
                    "value": "Otitis",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {
                        "page": 1,
                        "snippet": "Informe emitido 11/02/2026: otitis externa",
                    },
                },
                {
                    "field_id": "f-procedure",
                    "key": "procedure",
                    "value": "Limpieza",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Fecha de nacimiento 18/02/2020"},
                },
            ],
            "visits": [],
            "other_fields": [],
        },
    )
    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    data = response.json()["active_interpretation"]["data"]
    top_level_keys = {
        field.get("key") for field in data.get("fields", []) if isinstance(field, dict)
    }
    assert "diagnosis" not in top_level_keys
    assert "procedure" not in top_level_keys
    visits = data.get("visits")
    assert isinstance(visits, list)
    assigned = [
        visit
        for visit in visits
        if isinstance(visit, dict) and visit.get("visit_id") != "unassigned"
    ]
    assert assigned == []
    unassigned = next(
        (
            visit
            for visit in visits
            if isinstance(visit, dict) and visit.get("visit_id") == "unassigned"
        ),
        None,
    )
    assert isinstance(unassigned, dict)
    unassigned_keys = {
        field.get("key") for field in unassigned.get("fields", []) if isinstance(field, dict)
    }
    assert "diagnosis" in unassigned_keys
    assert "procedure" in unassigned_keys


def test_document_review_ambiguous_second_date_stays_unassigned(test_client):
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
                    "field_id": "f-symptoms-canonical",
                    "key": "symptoms",
                    "value": "Dolor",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026: dolor de oido"},
                },
                {
                    "field_id": "f-medication-v2",
                    "key": "medication",
                    "value": "Gotas",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "18/02/2026: medicacion indicada"},
                },
            ],
            "visits": [],
            "other_fields": [],
        },
    )
    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    visits = response.json()["active_interpretation"]["data"]["visits"]
    assigned = [
        visit
        for visit in visits
        if isinstance(visit, dict) and visit.get("visit_id") != "unassigned"
    ]
    assert len(assigned) == 1
    assert assigned[0].get("visit_date") == "2026-02-11"
    assigned_keys = {
        field.get("key") for field in assigned[0].get("fields", []) if isinstance(field, dict)
    }
    assert "symptoms" in assigned_keys
    assert "medication" not in assigned_keys
    unassigned = next(
        (
            visit
            for visit in visits
            if isinstance(visit, dict) and visit.get("visit_id") == "unassigned"
        ),
        None,
    )
    assert isinstance(unassigned, dict)
    unassigned_keys = {
        field.get("key") for field in unassigned.get("fields", []) if isinstance(field, dict)
    }
    assert "medication" in unassigned_keys


def test_document_review_ambiguous_date_token_with_raw_text_stays_unassigned(test_client):
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
                    "field_id": "f-symptoms-canonical",
                    "key": "symptoms",
                    "value": "Dolor",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026: dolor de oido"},
                },
                {
                    "field_id": "f-medication-ambiguous-raw-text",
                    "key": "medication",
                    "value": "Gotas",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {
                        "page": 1,
                        "snippet": "Informe emitido 18/02/2026: medicacion indicada",
                    },
                },
            ],
            "visits": [],
            "other_fields": [],
        },
    )
    raw_text_path = get_storage_root() / document_id / "runs" / run_id / "raw-text.txt"
    raw_text_path.parent.mkdir(parents=True, exist_ok=True)
    raw_text_path.write_text(
        (
            "Consulta 11/02/2026: dolor de oido.\n"
            "Control 18/02/2026: ajustar medicacion.\n"
            "Informe emitido 18/02/2026: medicacion indicada.\n"
        ),
        encoding="utf-8",
    )
    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    visits = response.json()["active_interpretation"]["data"]["visits"]
    assigned = [
        visit
        for visit in visits
        if isinstance(visit, dict) and visit.get("visit_id") != "unassigned"
    ]
    assert len(assigned) >= 2
    for visit in assigned:
        fields = visit.get("fields")
        if not isinstance(fields, list):
            continue
        assert all(
            not (
                isinstance(field, dict)
                and field.get("field_id") == "f-medication-ambiguous-raw-text"
            )
            for field in fields
        )
    unassigned = next(
        (
            visit
            for visit in visits
            if isinstance(visit, dict) and visit.get("visit_id") == "unassigned"
        ),
        None,
    )
    assert isinstance(unassigned, dict)
    unassigned_fields = unassigned.get("fields")
    assert isinstance(unassigned_fields, list)
    assert any(
        isinstance(field, dict) and field.get("field_id") == "f-medication-ambiguous-raw-text"
        for field in unassigned_fields
    )
