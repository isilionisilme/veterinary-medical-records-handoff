"""Integration tests covering raw-text-driven multi-visit assignment population.

Scenario focus: segment-derived field backfill and cross-visit raw-text extraction.
"""

from __future__ import annotations

from uuid import uuid4

from backend.app.domain import models as app_models
from backend.app.infra.file_storage import get_storage_root
from backend.tests.integration.document_review_test_support import (
    _coverage_ratio,
    _extract_assigned_visits,
    _extract_visit_field_value,
    _insert_run,
    _insert_structured_interpretation,
    _load_raw_text_fixture,
    _upload_sample_document,
)


def test_document_review_docb_raw_text_multi_visit_detects_multiple_assigned_visits(test_client):
    """docB shape: raw text with multiple visit contexts yields multiple visits."""

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
                    "evidence": {
                        "page": 1,
                        "snippet": "Consulta 11/02/2026: dolor de oido",
                    },
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
                    "evidence": {
                        "page": 1,
                        "snippet": "Se indica tratamiento topico",
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
            "Control 18/02/2026: persiste inflamacion y se ajusta medicacion.\n"
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


def test_document_review_multi_visit_rich_raw_text_populates_visit_fields_from_segments(
    test_client,
):
    """Per-visit segment mining should populate clinical fields for detected visits."""

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
    raw_text_path.write_text(_load_raw_text_fixture("docB_multi_visit_rich.txt"), encoding="utf-8")

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    visits = response.json()["active_interpretation"]["data"]["visits"]
    assigned = _extract_assigned_visits(visits)

    assert len(assigned) >= 2
    for visit in assigned:
        fields = visit.get("fields")
        assert isinstance(fields, list)
        keys = {field.get("key") for field in fields if isinstance(field, dict)}
        assert {"diagnosis", "symptoms"}.intersection(keys)


def test_document_review_multi_visit_rich_raw_text_extracts_reason_for_visit_from_segments(
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
    raw_text_path.write_text(_load_raw_text_fixture("docB_multi_visit_rich.txt"), encoding="utf-8")

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    visits = response.json()["active_interpretation"]["data"]["visits"]
    assigned = _extract_assigned_visits(visits)

    assert len(assigned) >= 2
    assigned_by_date = {
        visit.get("visit_date"): visit
        for visit in assigned
        if isinstance(visit.get("visit_date"), str)
    }

    assert (
        assigned_by_date["2026-02-11"].get("reason_for_visit")
        == "dolor de oido y prurito auricular"
    )
    assert (
        assigned_by_date["2026-02-18"].get("reason_for_visit")
        == "mejora parcial, persiste inflamacion leve"
    )


def test_document_review_multi_visit_docb_populates_observations_actions_with_high_coverage(
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
    raw_text_path.write_text(_load_raw_text_fixture("docB_multi_visit_rich.txt"), encoding="utf-8")

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    visits = response.json()["active_interpretation"]["data"]["visits"]
    assigned = _extract_assigned_visits(visits)
    assigned_by_date = {
        visit.get("visit_date"): visit
        for visit in assigned
        if isinstance(visit, dict) and isinstance(visit.get("visit_date"), str)
    }

    expected_segment_by_date = {
        "2026-02-11": (
            "Consulta 11/02/2026: dolor de oido y prurito auricular. "
            "Se diagnostica otitis externa y se realiza limpieza de oido. "
            "Se indica medicacion: gotas oticas 4 gotas cada 12 horas por 7 dias."
        ),
        "2026-02-18": (
            "Control 18/02/2026: mejora parcial, persiste inflamacion leve. "
            "Diagnostico de seguimiento: otitis externa en resolucion. "
            "Procedimiento: limpieza auricular de control. "
            "Tratamiento: mantener gotas oticas y revaluar en 5 dias."
        ),
    }

    for visit_date, expected_segment in expected_segment_by_date.items():
        visit = assigned_by_date.get(visit_date)
        assert isinstance(visit, dict)

        observations = _extract_visit_field_value(visit, key="observations")
        actions = _extract_visit_field_value(visit, key="actions")
        assert observations or actions

        coverage = _coverage_ratio(expected_segment, f"{observations} {actions}".strip())
        assert coverage >= 0.8


def test_document_review_multi_visit_reason_for_visit_does_not_override_existing_value(test_client):
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
                    "reason_for_visit": "Motivo original preservado",
                    "fields": [],
                }
            ],
            "other_fields": [],
        },
    )

    raw_text_path = get_storage_root() / document_id / "runs" / run_id / "raw-text.txt"
    raw_text_path.parent.mkdir(parents=True, exist_ok=True)
    raw_text_path.write_text(
        "Consulta 11/02/2026: dolor de oido y prurito auricular.\n", encoding="utf-8"
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    visits = response.json()["active_interpretation"]["data"]["visits"]
    assigned = _extract_assigned_visits(visits)
    assert len(assigned) == 1
    assert assigned[0].get("reason_for_visit") == "Motivo original preservado"


def test_document_review_multi_visit_reason_for_visit_backfills_when_existing_value_is_empty_string(
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
                    "reason_for_visit": "",
                    "fields": [],
                }
            ],
            "other_fields": [],
        },
    )

    raw_text_path = get_storage_root() / document_id / "runs" / run_id / "raw-text.txt"
    raw_text_path.parent.mkdir(parents=True, exist_ok=True)
    raw_text_path.write_text(
        "Consulta 11/02/2026: dolor de oido y prurito auricular.\n", encoding="utf-8"
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    visits = response.json()["active_interpretation"]["data"]["visits"]
    assigned = _extract_assigned_visits(visits)
    assert len(assigned) == 1
    assert assigned[0].get("reason_for_visit") == "dolor de oido y prurito auricular"
