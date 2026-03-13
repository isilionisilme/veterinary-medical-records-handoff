"""Integration tests covering baseline document review visit assignment behavior.

Scenario focus: canonical visit grouping and evidence-based multi-visit assignment.
"""

from __future__ import annotations

from uuid import uuid4

from backend.app.domain import models as app_models
from backend.tests.integration.document_review_test_support import (
    _insert_run,
    _insert_structured_interpretation,
    _upload_sample_document,
)


def test_document_review_moves_visit_scoped_keys_into_visits_group(test_client):
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
            "medical_record_view": {
                "version": "mvp-1",
                "sections": [
                    "clinic",
                    "patient",
                    "owner",
                    "visits",
                    "notes",
                    "other",
                    "report_info",
                ],
                "field_slots": [
                    {
                        "concept_id": "patient.pet_name",
                        "section": "patient",
                        "scope": "document",
                        "canonical_key": "pet_name",
                    },
                ],
            },
            "fields": [
                {
                    "field_id": "f-pet",
                    "key": "pet_name",
                    "value": "Luna",
                    "value_type": "string",
                    "scope": "document",
                    "section": "patient",
                    "classification": "medical_record",
                    "origin": "machine",
                },
                {
                    "field_id": "f-visit-date",
                    "key": "visit_date",
                    "value": "2026-02-11",
                    "value_type": "date",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                },
                {
                    "field_id": "f-diagnosis",
                    "key": "diagnosis",
                    "value": "Otitis",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
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
                },
                {
                    "field_id": "f-medication",
                    "key": "medication",
                    "value": "Gotas",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                },
                {
                    "field_id": "f-treatment",
                    "key": "treatment_plan",
                    "value": "7 dias",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                },
                {
                    "field_id": "f-lab",
                    "key": "lab_result",
                    "value": "Normal",
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

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    payload = response.json()
    data = payload["active_interpretation"]["data"]

    top_level_keys = {
        field.get("key") for field in data.get("fields", []) if isinstance(field, dict)
    }
    assert "visit_date" not in top_level_keys
    assert "diagnosis" not in top_level_keys
    assert "procedure" not in top_level_keys
    assert "medication" not in top_level_keys
    assert "treatment_plan" not in top_level_keys
    assert "lab_result" not in top_level_keys

    visits = data.get("visits")
    assert isinstance(visits, list)
    assert len(visits) > 0
    assigned_visit = next(
        (
            visit
            for visit in visits
            if isinstance(visit, dict) and visit.get("visit_id") != "unassigned"
        ),
        None,
    )
    assert isinstance(assigned_visit, dict)
    assert assigned_visit.get("visit_date") == "2026-02-11"

    visit_fields = assigned_visit.get("fields")
    assert isinstance(visit_fields, list)
    visit_keys = {field.get("key") for field in visit_fields if isinstance(field, dict)}
    assert "diagnosis" in visit_keys
    assert "procedure" in visit_keys
    assert "medication" in visit_keys
    assert "treatment_plan" in visit_keys
    assert "lab_result" in visit_keys


def test_document_review_detects_multiple_assigned_visits_from_field_evidence(test_client):
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
                    "field_id": "f-pet",
                    "key": "pet_name",
                    "value": "Luna",
                    "value_type": "string",
                    "scope": "document",
                    "section": "patient",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Paciente: Luna"},
                },
                {
                    "field_id": "f-symptoms-canonical",
                    "key": "symptoms",
                    "value": "Otalgia",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {
                        "page": 1,
                        "snippet": "Consulta 11/02/2026: dolor de oido",
                    },
                },
                {
                    "field_id": "f-medication-v2",
                    "key": "medication",
                    "value": "Gotas oticas",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {
                        "page": 1,
                        "snippet": "Consulta 18/02/2026: indicar gotas",
                    },
                },
                {
                    "field_id": "f-lab-v2",
                    "key": "lab_result",
                    "value": "Cultivo negativo",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {
                        "page": 1,
                        "snippet": "Control 18/02/2026: cultivo negativo",
                    },
                },
            ],
            "visits": [],
            "other_fields": [],
        },
    )

    first_response = test_client.get(f"/documents/{document_id}/review")
    assert first_response.status_code == 200
    first_visits = first_response.json()["active_interpretation"]["data"]["visits"]

    assigned_first = [
        visit
        for visit in first_visits
        if isinstance(visit, dict) and visit.get("visit_id") != "unassigned"
    ]
    assert len(assigned_first) >= 2
    assigned_by_date = {
        visit.get("visit_date"): visit
        for visit in assigned_first
        if isinstance(visit.get("visit_date"), str)
    }
    assert "2026-02-11" in assigned_by_date
    assert "2026-02-18" in assigned_by_date

    first_visit_keys = {
        field.get("key")
        for field in assigned_by_date["2026-02-11"].get("fields", [])
        if isinstance(field, dict)
    }
    second_visit_keys = {
        field.get("key")
        for field in assigned_by_date["2026-02-18"].get("fields", [])
        if isinstance(field, dict)
    }
    assert "symptoms" in first_visit_keys
    assert "medication" not in first_visit_keys
    assert "medication" in second_visit_keys
    assert "lab_result" in second_visit_keys

    second_response = test_client.get(f"/documents/{document_id}/review")
    assert second_response.status_code == 200
    second_visits = second_response.json()["active_interpretation"]["data"]["visits"]
    assert first_visits == second_visits
