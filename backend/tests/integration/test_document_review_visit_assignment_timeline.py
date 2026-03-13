"""Integration tests covering raw-text timeline visit assignment behavior."""

from __future__ import annotations

from uuid import uuid4

from backend.app.domain import models as app_models
from backend.app.infra.file_storage import get_storage_root
from backend.tests.integration.document_review_test_support import (
    _insert_run,
    _insert_structured_interpretation,
    _upload_sample_document,
)


def test_document_review_detects_additional_visit_from_raw_text_context(test_client):
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
                    "field_id": "f-symptoms-visit-1",
                    "key": "symptoms",
                    "value": "Otalgia",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026: dolor de oido"},
                },
                {
                    "field_id": "f-medication-no-date",
                    "key": "medication",
                    "value": "Gotas oticas",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Ajustar dosis segun respuesta clinica"},
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
            "Control 18/02/2026: se revisa evolucion y medicacion.\n"
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
    assigned_dates = {
        visit.get("visit_date") for visit in assigned if isinstance(visit.get("visit_date"), str)
    }
    assert {"2026-02-11", "2026-02-18"}.issubset(assigned_dates)


def test_document_review_keeps_multiple_same_day_visits_from_raw_text_timeline(test_client):
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
                    "field_id": "f-symptoms-base",
                    "key": "symptoms",
                    "value": "Dolor",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026: dolor de oido"},
                }
            ],
            "visits": [],
            "other_fields": [],
        },
    )
    raw_text_path = get_storage_root() / document_id / "runs" / run_id / "raw-text.txt"
    raw_text_path.parent.mkdir(parents=True, exist_ok=True)
    raw_text_path.write_text(
        "- 19/09/20 - 12:10 -\n- 19/09/20 - 18:45 -\n- 03/09/20 - 16:36 - LLAMADA\n",
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
    same_day_count = sum(1 for visit in assigned if visit.get("visit_date") == "2020-09-19")
    assert same_day_count == 2
    assert any(visit.get("visit_date") == "2020-09-03" for visit in assigned)


def test_document_review_assigns_no_date_field_to_nearest_same_day_visit_from_raw_text(test_client):
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
                    "field_id": "f-symptoms-base",
                    "key": "symptoms",
                    "value": "Dolor",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 03/09/20: dolor de oido"},
                },
                {
                    "field_id": "f-medication-same-day-second",
                    "key": "medication",
                    "value": "Prednisona",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {
                        "page": 1,
                        "snippet": "se administra prednisona y se pauta control",
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
            "- 19/09/20 - 12:10 - consulta por dolor.\n"
            "- 19/09/20 - 18:45 - se administra prednisona y se pauta control.\n"
            "- 03/09/20 - 16:36 - llamada de seguimiento.\n"
        ),
        encoding="utf-8",
    )
    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    visits = response.json()["active_interpretation"]["data"]["visits"]
    same_day_visits = [
        visit
        for visit in visits
        if isinstance(visit, dict)
        and visit.get("visit_id") != "unassigned"
        and visit.get("visit_date") == "2020-09-19"
    ]
    assert len(same_day_visits) == 2
    same_day_medication_count = 0
    for visit in same_day_visits:
        fields = visit.get("fields")
        if not isinstance(fields, list):
            continue
        if any(
            isinstance(field, dict) and field.get("field_id") == "f-medication-same-day-second"
            for field in fields
        ):
            same_day_medication_count += 1
    assert same_day_medication_count == 1
    unassigned = next(
        (
            visit
            for visit in visits
            if isinstance(visit, dict) and visit.get("visit_id") == "unassigned"
        ),
        None,
    )
    if isinstance(unassigned, dict):
        unassigned_fields = unassigned.get("fields")
        if isinstance(unassigned_fields, list):
            assert all(
                not (
                    isinstance(field, dict)
                    and field.get("field_id") == "f-medication-same-day-second"
                )
                for field in unassigned_fields
            )
