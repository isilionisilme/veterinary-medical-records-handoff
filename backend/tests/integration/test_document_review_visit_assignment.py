"""Integration tests covering document review visit assignment and scoping."""

from __future__ import annotations

from uuid import uuid4

from backend.app.domain import models as app_models
from backend.app.infra.file_storage import get_storage_root
from backend.tests.integration.document_review_test_support import (
    _US46_BASELINE_VERSION,
    _US46_VISIT_SCOPED_KEYS,
    _collect_visit_grouping_stats,
    _coverage_ratio,
    _extract_assigned_visits,
    _extract_visit_field_value,
    _insert_run,
    _insert_structured_interpretation,
    _load_raw_text_fixture,
    _load_us46_mixed_multi_visit_assignment_baseline,
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


def test_document_review_docb_raw_text_multi_visit_detects_multiple_assigned_visits(
    test_client,
):
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
    raw_text_path.write_text(
        _load_raw_text_fixture("docB_multi_visit_rich.txt"),
        encoding="utf-8",
    )

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
    raw_text_path.write_text(
        _load_raw_text_fixture("docB_multi_visit_rich.txt"),
        encoding="utf-8",
    )

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
    raw_text_path.write_text(
        _load_raw_text_fixture("docB_multi_visit_rich.txt"),
        encoding="utf-8",
    )

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
        "Consulta 11/02/2026: dolor de oido y prurito auricular.\n",
        encoding="utf-8",
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
        "Consulta 11/02/2026: dolor de oido y prurito auricular.\n",
        encoding="utf-8",
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    visits = response.json()["active_interpretation"]["data"]["visits"]
    assigned = _extract_assigned_visits(visits)
    assert len(assigned) == 1
    assert assigned[0].get("reason_for_visit") == "dolor de oido y prurito auricular"


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


def test_document_review_multi_visit_extracts_medication_and_procedure_from_segments(
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
                        "snippet": "Ajustar dosis segun respuesta clinica",
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
                    "evidence": {
                        "page": 1,
                        "snippet": "Consulta 11/02/2026: dolor de oido",
                    },
                }
            ],
            "visits": [],
            "other_fields": [],
        },
    )

    raw_text_path = get_storage_root() / document_id / "runs" / run_id / "raw-text.txt"
    raw_text_path.parent.mkdir(parents=True, exist_ok=True)
    raw_text_path.write_text(
        ("- 19/09/20 - 12:10 -\n- 19/09/20 - 18:45 -\n- 03/09/20 - 16:36 - LLAMADA\n"),
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
                    "evidence": {
                        "page": 1,
                        "snippet": "Consulta 03/09/20: dolor de oido",
                    },
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
    assert isinstance(visits, list)

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
                    "evidence": {
                        "page": 1,
                        "snippet": "Fecha de nacimiento 18/02/2020",
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
                    "evidence": {
                        "page": 1,
                        "snippet": "Consulta 11/02/2026: dolor de oido",
                    },
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
                    "evidence": {
                        "page": 1,
                        "snippet": "18/02/2026: medicacion indicada",
                    },
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
                    "evidence": {
                        "page": 1,
                        "snippet": "Consulta 11/02/2026: dolor de oido",
                    },
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
                    "evidence": {
                        "page": 1,
                        "snippet": "Visita 18/02/2026: medicacion indicada",
                    },
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
                    "evidence": {
                        "page": 1,
                        "snippet": "Control 18/02/2026: limpieza auricular",
                    },
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
                    "evidence": {
                        "page": 1,
                        "snippet": "01/03/2026: reevaluar en 7 dias",
                    },
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
