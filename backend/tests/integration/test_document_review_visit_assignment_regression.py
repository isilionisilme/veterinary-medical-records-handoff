"""Integration tests covering visit-assignment regression guards."""

from __future__ import annotations

from uuid import uuid4

from backend.app.domain import models as app_models
from backend.app.infra.file_storage import get_storage_root
from backend.tests.integration.document_review_test_support import (
    _US46_BASELINE_VERSION,
    _US46_VISIT_SCOPED_KEYS,
    _collect_visit_grouping_stats,
    _insert_run,
    _insert_structured_interpretation,
    _load_us46_mixed_multi_visit_assignment_baseline,
    _upload_sample_document,
)


def test_document_review_boundary_marker_guides_undated_field_assignment(test_client):
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
                    "field_id": "f-diagnosis-v1",
                    "key": "diagnosis",
                    "value": "Otitis externa",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026: otitis externa"},
                },
                {
                    "field_id": "f-medication-undated-after-boundary",
                    "key": "medication",
                    "value": "Mantener gotas oticas",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Mantener gotas oticas cada 12 horas"},
                },
                {
                    "field_id": "f-procedure-v2",
                    "key": "procedure",
                    "value": "Limpieza auricular",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 18/02/2026: limpieza auricular"},
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
            "Consulta 11/02/2026: otitis externa.\n"
            "Plan inicial con lavado y control.\n"
            "\uf133VISITA CONSULTA GENERAL DEL D\u00cdA\n"
            "Mantener gotas oticas cada 12 horas.\n"
            "Texto administrativo adicional para separar la fecha de control.\n"
            "Texto administrativo adicional para separar la fecha de control.\n"
            "Texto administrativo adicional para separar la fecha de control.\n"
            "Consulta 18/02/2026: limpieza auricular.\n"
        ),
        encoding="utf-8",
    )
    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    visits = response.json()["active_interpretation"]["data"]["visits"]
    assigned_visits = [
        visit
        for visit in visits
        if isinstance(visit, dict) and isinstance(visit.get("visit_date"), str)
    ]
    assigned_by_date = {
        str(visit["visit_date"]): visit for visit in assigned_visits if isinstance(visit, dict)
    }
    assert "2026-02-11" in assigned_by_date
    assert "2026-02-18" in assigned_by_date
    first_visit_field_ids = {
        field.get("field_id")
        for field in assigned_by_date["2026-02-11"].get("fields", [])
        if isinstance(field, dict)
    }
    second_visit_field_ids = {
        field.get("field_id")
        for field in assigned_by_date["2026-02-18"].get("fields", [])
        if isinstance(field, dict)
    }
    assert "f-medication-undated-after-boundary" not in first_visit_field_ids
    assert "f-medication-undated-after-boundary" in second_visit_field_ids


def test_document_review_merges_prepopulated_and_inferred_visits_deterministically(test_client):
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
                    "value": "Otalgia",
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
                    "value": "Gotas oticas",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 18/02/2026: indicar gotas"},
                },
            ],
            "visits": [
                {
                    "visit_id": "visit-existing",
                    "visit_date": "2026-02-18",
                    "admission_date": None,
                    "discharge_date": None,
                    "reason_for_visit": "Control",
                    "fields": [
                        {
                            "field_id": "vf-existing-lab",
                            "key": "lab_result",
                            "value": "Cultivo negativo",
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
    first_response = test_client.get(f"/documents/{document_id}/review")
    assert first_response.status_code == 200
    first_visits = first_response.json()["active_interpretation"]["data"]["visits"]
    assigned_visits = [
        visit
        for visit in first_visits
        if isinstance(visit, dict) and visit.get("visit_id") != "unassigned"
    ]
    assert [visit.get("visit_date") for visit in assigned_visits] == ["2026-02-11", "2026-02-18"]
    first_visit_keys = {
        field.get("key")
        for field in assigned_visits[0].get("fields", [])
        if isinstance(field, dict)
    }
    second_visit_keys = {
        field.get("key")
        for field in assigned_visits[1].get("fields", [])
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


def test_document_review_us46_mixed_multi_visit_assignment_regression_guardrail(test_client):
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
                    "field_id": "f-diagnosis-canonical",
                    "key": "diagnosis",
                    "value": "Otitis externa",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {
                        "page": 1,
                        "snippet": "Consulta 11/02/2026: diagnostico de otitis externa",
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
                    "evidence": {"page": 1, "snippet": "Visita 18/02/2026: medicacion indicada"},
                },
                {
                    "field_id": "f-procedure-v2",
                    "key": "procedure",
                    "value": "Limpieza auricular",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Control 18/02/2026: limpieza auricular"},
                },
                {
                    "field_id": "f-lab-unassigned",
                    "key": "lab_result",
                    "value": "Cortisol basal elevado",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {
                        "page": 1,
                        "snippet": "Informe emitido 01/03/2026: cortisol basal elevado",
                    },
                },
                {
                    "field_id": "f-treatment-unassigned",
                    "key": "treatment_plan",
                    "value": "Reevaluar en 7 dias",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "01/03/2026: reevaluar en 7 dias"},
                },
            ],
            "visits": [
                {
                    "visit_id": "visit-2026-02-11",
                    "visit_date": "2026-02-11",
                    "admission_date": None,
                    "discharge_date": None,
                    "reason_for_visit": "Consulta",
                    "fields": [],
                },
                {
                    "visit_id": "visit-2026-02-18",
                    "visit_date": "2026-02-18",
                    "admission_date": None,
                    "discharge_date": None,
                    "reason_for_visit": "Control",
                    "fields": [],
                },
            ],
            "other_fields": [],
        },
    )
    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    data = response.json()["active_interpretation"]["data"]
    top_level_keys = {
        field.get("key") for field in data.get("fields", []) if isinstance(field, dict)
    }
    assert _US46_VISIT_SCOPED_KEYS.isdisjoint(top_level_keys)
    stats = _collect_visit_grouping_stats(data.get("visits"))
    baseline = _load_us46_mixed_multi_visit_assignment_baseline()
    assert baseline["version"] == _US46_BASELINE_VERSION
    assert stats["assigned_visit_ids"] == baseline["visit_ids"]
    assert stats["assigned_count"] >= baseline["assigned_visit_scoped_fields"] + 2
    assert stats["unassigned_count"] <= baseline["unassigned_visit_scoped_fields"] - 2
    assert {"diagnosis", "medication", "procedure"}.intersection(stats["assigned_keys"])
