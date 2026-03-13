"""Integration tests covering visit-segment mining for grouped review payloads."""

from __future__ import annotations

from uuid import uuid4

from backend.app.domain import models as app_models
from backend.app.infra.file_storage import get_storage_root
from backend.tests.integration.document_review_test_support import (
    _extract_assigned_visits,
    _insert_run,
    _insert_structured_interpretation,
    _upload_sample_document,
)


def test_document_review_multi_visit_extracts_diagnosis_and_symptoms_from_segments(test_client):
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
                    "value": "11/02/2026",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                },
                {
                    "field_id": "f-visit-date-2",
                    "key": "visit_date",
                    "value": "18/02/2026",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
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
            "Sintomas: dolor de oido y prurito auricular.\n"
            "Diagnostico: otitis externa.\n\n"
            "Control 18/02/2026: mejora parcial.\n"
            "Sintomas: inflamacion leve.\n"
            "Diagnostico de seguimiento: otitis externa en resolucion.\n"
        ),
        encoding="utf-8",
    )
    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    visits = response.json()["active_interpretation"]["data"]["visits"]
    assigned = _extract_assigned_visits(visits)
    assigned_by_date = {
        visit.get("visit_date"): visit
        for visit in assigned
        if isinstance(visit.get("visit_date"), str)
    }
    first_visit_fields = assigned_by_date["2026-02-11"].get("fields", [])
    second_visit_fields = assigned_by_date["2026-02-18"].get("fields", [])
    first_keys = {field.get("key") for field in first_visit_fields if isinstance(field, dict)}
    second_keys = {field.get("key") for field in second_visit_fields if isinstance(field, dict)}
    assert "diagnosis" in first_keys
    assert "symptoms" in first_keys
    assert "diagnosis" in second_keys
    assert "symptoms" in second_keys


def test_document_review_multi_visit_segment_mining_does_not_duplicate_existing_diagnosis(
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
                    "field_id": "f-visit-date-1",
                    "key": "visit_date",
                    "value": "11/02/2026",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                }
            ],
            "visits": [
                {
                    "visit_id": "visit-existing-1",
                    "visit_date": "2026-02-11",
                    "admission_date": None,
                    "discharge_date": None,
                    "reason_for_visit": None,
                    "fields": [
                        {
                            "field_id": "vf-diagnosis-existing",
                            "key": "diagnosis",
                            "value": "Diagnostico preservado",
                            "value_type": "string",
                            "scope": "visit",
                            "section": "visits",
                            "classification": "medical_record",
                            "origin": "machine",
                        }
                    ],
                }
            ],
            "other_fields": [],
        },
    )
    raw_text_path = get_storage_root() / document_id / "runs" / run_id / "raw-text.txt"
    raw_text_path.parent.mkdir(parents=True, exist_ok=True)
    raw_text_path.write_text(
        (
            "Consulta 11/02/2026: dolor de oido.\n"
            "Diagnostico: otitis externa.\n"
            "Sintomas: prurito auricular.\n"
        ),
        encoding="utf-8",
    )
    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    visits = response.json()["active_interpretation"]["data"]["visits"]
    assigned = _extract_assigned_visits(visits)
    assert len(assigned) == 1
    fields = assigned[0].get("fields", [])
    diagnosis_values = [
        field.get("value")
        for field in fields
        if isinstance(field, dict) and field.get("key") == "diagnosis"
    ]
    assert diagnosis_values == ["Diagnostico preservado"]


def test_document_review_multi_visit_extracts_medication_and_procedure_from_segments(test_client):
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
                    "value": "11/02/2026",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                },
                {
                    "field_id": "f-visit-date-2",
                    "key": "visit_date",
                    "value": "18/02/2026",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
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
            "Medicacion: gotas oticas 4 gotas cada 12 horas.\n"
            "Procedimiento: limpieza auricular.\n\n"
            "Control 18/02/2026: mejora parcial.\n"
            "Tratamiento: mantener gotas oticas y revaluar en 5 dias.\n"
            "Procedimiento: limpieza auricular de control.\n"
        ),
        encoding="utf-8",
    )
    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    visits = response.json()["active_interpretation"]["data"]["visits"]
    assigned = _extract_assigned_visits(visits)
    assigned_by_date = {
        visit.get("visit_date"): visit
        for visit in assigned
        if isinstance(visit.get("visit_date"), str)
    }
    first_visit_fields = assigned_by_date["2026-02-11"].get("fields", [])
    second_visit_fields = assigned_by_date["2026-02-18"].get("fields", [])
    first_keys = {field.get("key") for field in first_visit_fields if isinstance(field, dict)}
    second_keys = {field.get("key") for field in second_visit_fields if isinstance(field, dict)}
    assert "medication" in first_keys
    assert "procedure" in first_keys
    assert "medication" in second_keys
    assert "procedure" in second_keys


def test_document_review_multi_visit_segment_mining_does_not_duplicate_existing_medication(
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
                    "field_id": "f-visit-date-1",
                    "key": "visit_date",
                    "value": "11/02/2026",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                }
            ],
            "visits": [
                {
                    "visit_id": "visit-existing-1",
                    "visit_date": "2026-02-11",
                    "admission_date": None,
                    "discharge_date": None,
                    "reason_for_visit": None,
                    "fields": [
                        {
                            "field_id": "vf-medication-existing",
                            "key": "medication",
                            "value": "Tratamiento preservado",
                            "value_type": "string",
                            "scope": "visit",
                            "section": "visits",
                            "classification": "medical_record",
                            "origin": "machine",
                        }
                    ],
                }
            ],
            "other_fields": [],
        },
    )
    raw_text_path = get_storage_root() / document_id / "runs" / run_id / "raw-text.txt"
    raw_text_path.parent.mkdir(parents=True, exist_ok=True)
    raw_text_path.write_text(
        (
            "Consulta 11/02/2026: dolor de oido.\n"
            "Medicacion: gotas oticas 4 gotas cada 12 horas.\n"
            "Procedimiento: limpieza auricular.\n"
        ),
        encoding="utf-8",
    )
    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    visits = response.json()["active_interpretation"]["data"]["visits"]
    assigned = _extract_assigned_visits(visits)
    assert len(assigned) == 1
    fields = assigned[0].get("fields", [])
    medication_values = [
        field.get("value")
        for field in fields
        if isinstance(field, dict) and field.get("key") == "medication"
    ]
    assert medication_values == ["Tratamiento preservado"]
