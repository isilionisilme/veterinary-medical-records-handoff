"""Integration tests covering document review endpoint behavior."""

from __future__ import annotations

import io
import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.app.application.processing_runner import _build_interpretation_artifact
from backend.app.domain import models as app_models
from backend.app.infra import database
from backend.app.infra.file_storage import get_storage_root

_US46_BASELINE_VERSION = "mixed_multi_visit_assignment.baseline.canonical"
_US46_BASELINE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "review_baselines"
    / f"{_US46_BASELINE_VERSION}.json"
)

_US46_VISIT_SCOPED_KEYS = {
    "symptoms",
    "diagnosis",
    "procedure",
    "medication",
    "treatment_plan",
    "allergies",
    "vaccinations",
    "lab_result",
    "imaging",
}


def _load_us46_mixed_multi_visit_assignment_baseline() -> dict[str, object]:
    payload = json.loads(_US46_BASELINE_PATH.read_text(encoding="utf-8"))
    visit_ids = payload.get("visit_ids")
    normalized_visit_ids = {
        str(visit_id)
        for visit_id in visit_ids
        if isinstance(visit_ids, list) and isinstance(visit_id, str)
    }

    return {
        "version": payload.get("version"),
        "visit_ids": normalized_visit_ids,
        "assigned_visit_scoped_fields": payload.get("assigned_visit_scoped_fields"),
        "unassigned_visit_scoped_fields": payload.get("unassigned_visit_scoped_fields"),
    }


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    db_path = tmp_path / "documents.db"
    monkeypatch.setenv("VET_RECORDS_DB_PATH", str(db_path))
    monkeypatch.setenv("VET_RECORDS_STORAGE_PATH", str(tmp_path / "storage"))
    monkeypatch.setenv("VET_RECORDS_DISABLE_PROCESSING", "true")
    database.ensure_schema()
    return db_path


@pytest.fixture
def test_client(test_db):
    from backend.app.main import app

    with TestClient(app) as client:
        yield client


def _upload_sample_document(test_client: TestClient) -> str:
    content = b"%PDF-1.5 sample"
    files = {"file": ("record.pdf", io.BytesIO(content), "application/pdf")}
    response = test_client.post("/documents/upload", files=files)
    assert response.status_code == 201
    return response.json()["document_id"]


def _insert_run(
    *, document_id: str, run_id: str, state: app_models.ProcessingRunState, failure_type: str | None
) -> None:
    with database.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO processing_runs (
                run_id, document_id, state, created_at, started_at, completed_at, failure_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                document_id,
                state.value,
                "2026-02-10T10:00:00+00:00",
                "2026-02-10T10:00:01+00:00",
                (
                    "2026-02-10T10:00:05+00:00"
                    if state == app_models.ProcessingRunState.COMPLETED
                    else None
                ),
                failure_type,
            ),
        )
        conn.commit()


def _insert_structured_interpretation(
    *,
    run_id: str,
    data: dict[str, object] | None = None,
) -> None:
    payload_data = data or {
        "document_id": "doc",
        "processing_run_id": run_id,
        "created_at": "2026-02-10T10:00:05+00:00",
        "fields": [
            {
                "field_id": "field-1",
                "key": "pet_name",
                "value": "Luna",
                "value_type": "string",
                "is_critical": False,
                "origin": "machine",
                "evidence": {"page": 1, "snippet": "Paciente: Luna"},
            }
        ],
    }

    payload = {
        "interpretation_id": "interp-1",
        "version_number": 1,
        "data": payload_data,
    }

    with database.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO artifacts (artifact_id, run_id, artifact_type, payload, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                f"artifact-review-{run_id}",
                run_id,
                "STRUCTURED_INTERPRETATION",
                json.dumps(payload, separators=(",", ":")),
                "2026-02-10T10:00:06+00:00",
            ),
        )
        conn.commit()


def _collect_visit_grouping_stats(visits: object) -> dict[str, object]:
    assigned_visit_ids: set[str] = set()
    assigned_keys: set[str] = set()
    assigned_count = 0
    unassigned_count = 0

    if not isinstance(visits, list):
        return {
            "assigned_visit_ids": assigned_visit_ids,
            "assigned_keys": assigned_keys,
            "assigned_count": assigned_count,
            "unassigned_count": unassigned_count,
        }

    for visit in visits:
        if not isinstance(visit, dict):
            continue

        visit_id = visit.get("visit_id")
        fields = visit.get("fields")
        if not isinstance(fields, list):
            continue

        if isinstance(visit_id, str) and visit_id != "unassigned":
            assigned_visit_ids.add(visit_id)
            for field in fields:
                if not isinstance(field, dict):
                    continue
                assigned_count += 1
                field_key = field.get("key")
                if isinstance(field_key, str):
                    assigned_keys.add(field_key)
            continue

        unassigned_count += sum(1 for field in fields if isinstance(field, dict))

    return {
        "assigned_visit_ids": assigned_visit_ids,
        "assigned_keys": assigned_keys,
        "assigned_count": assigned_count,
        "unassigned_count": unassigned_count,
    }


def _get_calibration_counts(
    *,
    context_key: str,
    field_key: str,
    mapping_id: str | None,
    policy_version: str,
) -> tuple[int, int]:
    mapping_scope_key = mapping_id if mapping_id is not None else "__null__"
    with database.get_connection() as conn:
        row = conn.execute(
            """
            SELECT accept_count, edit_count
            FROM calibration_aggregates
            WHERE context_key = ?
              AND field_key = ?
              AND mapping_id_scope_key = ?
              AND policy_version = ?
            """,
            (context_key, field_key, mapping_scope_key, policy_version),
        ).fetchone()
    if row is None:
        return (0, 0)
    return (int(row["accept_count"]), int(row["edit_count"]))


def test_document_review_returns_latest_completed_run_context(test_client):
    document_id = _upload_sample_document(test_client)
    run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    _insert_structured_interpretation(run_id=run_id)

    raw_text_path = get_storage_root() / document_id / "runs" / run_id / "raw-text.txt"
    raw_text_path.parent.mkdir(parents=True, exist_ok=True)
    raw_text_path.write_text("Paciente: Luna", encoding="utf-8")

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    payload = response.json()
    assert payload["document_id"] == document_id
    assert payload["latest_completed_run"]["run_id"] == run_id
    assert payload["active_interpretation"]["version_number"] == 1
    assert payload["active_interpretation"]["data"].get("schema_contract") == (
        "visit-grouped-canonical"
    )
    assert "schema_version" not in payload["active_interpretation"]["data"]
    medical_record_view = payload["active_interpretation"]["data"].get("medical_record_view")
    assert isinstance(medical_record_view, dict)
    field_slots = medical_record_view.get("field_slots")
    assert isinstance(field_slots, list)
    patient_slots = [
        slot for slot in field_slots if isinstance(slot, dict) and slot.get("section") == "patient"
    ]
    patient_slot_keys = {
        slot.get("canonical_key")
        for slot in patient_slots
        if isinstance(slot.get("canonical_key"), str)
    }
    assert {
        "pet_name",
        "species",
        "breed",
        "sex",
        "age",
        "dob",
        "microchip_id",
        "weight",
        "reproductive_status",
    }.issubset(patient_slot_keys)
    nhc_slot = next(
        (
            slot
            for slot in field_slots
            if isinstance(slot, dict) and slot.get("canonical_key") == "nhc"
        ),
        None,
    )
    assert nhc_slot is not None
    assert nhc_slot.get("aliases") == ["medical_record_number"]
    assert payload["raw_text_artifact"]["available"] is True
    assert payload["review_status"] == "IN_REVIEW"
    assert payload["reviewed_at"] is None


def test_document_review_payload_uses_canonical_global_schema_key_only(test_client):
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
            "global_schema": {"pet_name": "Luna"},
            "fields": [
                {
                    "field_id": "field-1",
                    "key": "pet_name",
                    "value": "Luna",
                    "value_type": "string",
                    "is_critical": False,
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Paciente: Luna"},
                }
            ],
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    payload = response.json()

    data = payload["active_interpretation"]["data"]
    assert "global_schema" in data
    assert isinstance(data["global_schema"], dict)
    unexpected_prefixed_keys = [
        key for key in data.keys() if isinstance(key, str) and key.startswith("global_schema_")
    ]
    assert unexpected_prefixed_keys == []


def test_document_review_normalizes_partial_medical_record_view_to_canonical_shape(test_client):
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
            "schema_contract": "visit-grouped-canonical",
            "medical_record_view": {"version": "mvp-1"},
            "global_schema": {"pet_name": "Luna"},
            "fields": [],
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    data = response.json()["active_interpretation"]["data"]

    assert data.get("schema_contract") == "visit-grouped-canonical"
    medical_record_view = data.get("medical_record_view")
    assert isinstance(medical_record_view, dict)
    assert isinstance(medical_record_view.get("sections"), list)
    assert isinstance(medical_record_view.get("field_slots"), list)


def test_document_review_omits_confidence_policy_when_config_missing(
    test_client: TestClient, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.delenv("VET_RECORDS_CONFIDENCE_POLICY_VERSION", raising=False)
    monkeypatch.delenv("VET_RECORDS_CONFIDENCE_LOW_MAX", raising=False)
    monkeypatch.delenv("VET_RECORDS_CONFIDENCE_MID_MAX", raising=False)

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
                    "field_id": "field-1",
                    "key": "pet_name",
                    "value": "Luna",
                    "value_type": "string",
                    "field_mapping_confidence": 0.82,
                    "is_critical": False,
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Paciente: Luna"},
                }
            ],
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    payload = response.json()
    assert "confidence_policy" not in payload["active_interpretation"]["data"]


def test_document_review_returns_conflict_when_no_completed_run(test_client):
    document_id = _upload_sample_document(test_client)
    _insert_run(
        document_id=document_id,
        run_id=str(uuid4()),
        state=app_models.ProcessingRunState.RUNNING,
        failure_type=None,
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 409
    payload = response.json()
    assert payload["error_code"] == "CONFLICT"
    assert payload["details"]["reason"] == "NO_COMPLETED_RUN"


def test_document_review_returns_conflict_when_interpretation_is_missing(test_client):
    document_id = _upload_sample_document(test_client)
    _insert_run(
        document_id=document_id,
        run_id=str(uuid4()),
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 409
    payload = response.json()
    assert payload["error_code"] == "CONFLICT"
    assert payload["details"]["reason"] == "INTERPRETATION_MISSING"


def test_document_review_normalizes_microchip_suffix_to_digits_only(test_client):
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
            "global_schema": {"microchip_id": "00023035139 NHC"},
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    payload = response.json()
    assert (
        payload["active_interpretation"]["data"]["global_schema"]["microchip_id"] == "00023035139"
    )
    microchip_fields = [
        field
        for field in payload["active_interpretation"]["data"].get("fields", [])
        if isinstance(field, dict) and field.get("key") == "microchip_id"
    ]
    assert microchip_fields
    assert microchip_fields[0].get("value") == "00023035139"


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


def test_document_review_drops_non_digit_microchip_value(test_client):
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
            "global_schema": {"microchip_id": "BEATRIZ ABARCA C/ ORTEGA"},
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    payload = response.json()
    assert payload["active_interpretation"]["data"]["global_schema"]["microchip_id"] is None


def test_document_review_keeps_canonical_microchip_digits_unchanged(test_client):
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
            "global_schema": {"microchip_id": "00023035139"},
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    payload = response.json()
    assert (
        payload["active_interpretation"]["data"]["global_schema"]["microchip_id"] == "00023035139"
    )


def test_document_review_sanitizes_confidence_breakdown_payload_values(test_client):
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
                    "field_id": "field-1",
                    "key": "pet_name",
                    "value": "Luna",
                    "value_type": "string",
                    "field_mapping_confidence": 0.82,
                    "field_candidate_confidence": 0.82,
                    "text_extraction_reliability": 1.7,
                    "field_review_history_adjustment": "invalid",
                    "is_critical": False,
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Paciente: Luna"},
                }
            ],
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    payload = response.json()
    field = payload["active_interpretation"]["data"]["fields"][0]
    assert field["text_extraction_reliability"] is None
    assert field["field_review_history_adjustment"] == 0
    assert field["field_candidate_confidence"] == 0.82
    assert field["field_mapping_confidence"] == 0.82


def test_document_review_composes_mapping_confidence_from_candidate_and_adjustment(test_client):
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
                    "field_id": "field-1",
                    "key": "pet_name",
                    "value": "Luna",
                    "value_type": "string",
                    "field_candidate_confidence": 0.66,
                    "field_review_history_adjustment": -10,
                    "field_mapping_confidence": 0.9,
                    "is_critical": False,
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Paciente: Luna"},
                },
                {
                    "field_id": "field-2",
                    "key": "species",
                    "value": "Canino",
                    "value_type": "string",
                    "field_candidate_confidence": 0.95,
                    "field_review_history_adjustment": 10,
                    "field_mapping_confidence": 0.2,
                    "is_critical": False,
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Canino"},
                },
            ],
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    payload = response.json()
    fields = payload["active_interpretation"]["data"]["fields"]
    by_key = {field["key"]: field for field in fields}
    assert by_key["pet_name"]["field_mapping_confidence"] == pytest.approx(0.56, abs=1e-9)
    assert by_key["species"]["field_mapping_confidence"] == pytest.approx(1.0, abs=1e-9)


def test_cross_document_learning_applies_negative_adjustment_after_edit_signal(test_client):
    repository = test_client.app.state.document_repository
    baseline = _build_interpretation_artifact(
        document_id="doc-baseline",
        run_id=str(uuid4()),
        raw_text="Paciente: Luna",
        repository=repository,
    )
    baseline_fields = baseline["data"]["fields"]
    baseline_pet_name = next(field for field in baseline_fields if field["key"] == "pet_name")
    assert baseline_pet_name["field_review_history_adjustment"] == 0

    for _index, value in enumerate(["Kira", "Nala", "Mika"], start=1):
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
                "global_schema": baseline["data"]["global_schema"],
                "fields": [
                    {
                        "field_id": "field-1",
                        "key": "pet_name",
                        "value": "Luna",
                        "value_type": "string",
                        "field_candidate_confidence": 0.66,
                        "field_mapping_confidence": 0.66,
                        "field_review_history_adjustment": 0.0,
                        "mapping_id": baseline_pet_name.get("mapping_id"),
                        "context_key": baseline_pet_name["context_key"],
                        "policy_version": baseline_pet_name["policy_version"],
                        "is_critical": True,
                        "origin": "machine",
                        "evidence": {"page": 1, "snippet": "Paciente: Luna"},
                    }
                ],
            },
        )

        edit_response = test_client.post(
            f"/runs/{run_id}/interpretations",
            json={
                "base_version_number": 1,
                "changes": [
                    {
                        "op": "UPDATE",
                        "field_id": "field-1",
                        "value": value,
                        "value_type": "string",
                    }
                ],
            },
        )
        assert edit_response.status_code == 201

        reviewed_response = test_client.post(f"/documents/{document_id}/reviewed")
        assert reviewed_response.status_code == 200

    calibrated = _build_interpretation_artifact(
        document_id="doc-after-edit",
        run_id=str(uuid4()),
        raw_text="Paciente: Luna",
        repository=repository,
    )
    calibrated_fields = calibrated["data"]["fields"]
    calibrated_pet_name = next(field for field in calibrated_fields if field["key"] == "pet_name")
    assert calibrated_pet_name["field_review_history_adjustment"] < 0


def test_mark_document_reviewed_applies_accept_delta_for_non_critical_machine_field(test_client):
    document_id = _upload_sample_document(test_client)
    run_id = str(uuid4())
    context_key = "review:canonical:pet_name"
    mapping_id = "mapping-non-critical-machine"
    policy_version = "v1"
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
                    "field_id": "field-1",
                    "key": "coat_color",
                    "value": "Negro",
                    "value_type": "string",
                    "field_candidate_confidence": 0.66,
                    "field_mapping_confidence": 0.66,
                    "field_review_history_adjustment": 0.0,
                    "mapping_id": mapping_id,
                    "context_key": context_key,
                    "policy_version": policy_version,
                    "is_critical": False,
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Color: Negro"},
                }
            ],
        },
    )

    assert _get_calibration_counts(
        context_key=context_key,
        field_key="coat_color",
        mapping_id=mapping_id,
        policy_version=policy_version,
    ) == (0, 0)

    reviewed = test_client.post(f"/documents/{document_id}/reviewed")
    assert reviewed.status_code == 200

    assert _get_calibration_counts(
        context_key=context_key,
        field_key="coat_color",
        mapping_id=mapping_id,
        policy_version=policy_version,
    ) == (1, 0)


def test_mark_document_reviewed_is_idempotent(test_client):
    document_id = _upload_sample_document(test_client)

    first = test_client.post(f"/documents/{document_id}/reviewed")
    assert first.status_code == 200
    first_payload = first.json()
    assert first_payload["document_id"] == document_id
    assert first_payload["review_status"] == "REVIEWED"
    assert isinstance(first_payload["reviewed_at"], str)

    second = test_client.post(f"/documents/{document_id}/reviewed")
    assert second.status_code == 200
    second_payload = second.json()
    assert second_payload["review_status"] == "REVIEWED"
    assert second_payload["reviewed_at"] == first_payload["reviewed_at"]


def test_reopen_document_review_is_idempotent(test_client):
    document_id = _upload_sample_document(test_client)
    marked = test_client.post(f"/documents/{document_id}/reviewed")
    assert marked.status_code == 200

    reopened = test_client.delete(f"/documents/{document_id}/reviewed")
    assert reopened.status_code == 200
    reopened_payload = reopened.json()
    assert reopened_payload["review_status"] == "IN_REVIEW"
    assert reopened_payload["reviewed_at"] is None

    reopened_again = test_client.delete(f"/documents/{document_id}/reviewed")
    assert reopened_again.status_code == 200
    reopened_again_payload = reopened_again.json()
    assert reopened_again_payload["review_status"] == "IN_REVIEW"
    assert reopened_again_payload["reviewed_at"] is None


def test_reopen_review_reverts_reviewed_calibration_deltas_and_allows_reapply(test_client):
    repository = test_client.app.state.document_repository
    baseline = _build_interpretation_artifact(
        document_id="doc-snapshot-baseline",
        run_id=str(uuid4()),
        raw_text="Paciente: Luna",
        repository=repository,
    )
    baseline_pet_name = next(
        field for field in baseline["data"]["fields"] if field["key"] == "pet_name"
    )
    context_key = str(baseline_pet_name["context_key"])
    mapping_id = baseline_pet_name.get("mapping_id")
    policy_version = str(baseline_pet_name["policy_version"])

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
            "global_schema": baseline["data"]["global_schema"],
            "fields": [
                {
                    "field_id": "field-1",
                    "key": "pet_name",
                    "value": "Luna",
                    "value_type": "string",
                    "field_candidate_confidence": 0.66,
                    "field_mapping_confidence": 0.66,
                    "field_review_history_adjustment": 0.0,
                    "mapping_id": mapping_id,
                    "context_key": context_key,
                    "policy_version": policy_version,
                    "is_critical": True,
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Paciente: Luna"},
                }
            ],
        },
    )

    marked = test_client.post(f"/documents/{document_id}/reviewed")
    assert marked.status_code == 200
    assert _get_calibration_counts(
        context_key=context_key,
        field_key="pet_name",
        mapping_id=mapping_id,
        policy_version=policy_version,
    ) == (1, 0)

    reopened = test_client.delete(f"/documents/{document_id}/reviewed")
    assert reopened.status_code == 200
    assert _get_calibration_counts(
        context_key=context_key,
        field_key="pet_name",
        mapping_id=mapping_id,
        policy_version=policy_version,
    ) == (0, 0)

    reopened_again = test_client.delete(f"/documents/{document_id}/reviewed")
    assert reopened_again.status_code == 200
    assert _get_calibration_counts(
        context_key=context_key,
        field_key="pet_name",
        mapping_id=mapping_id,
        policy_version=policy_version,
    ) == (0, 0)

    reviewed_again = test_client.post(f"/documents/{document_id}/reviewed")
    assert reviewed_again.status_code == 200
    assert _get_calibration_counts(
        context_key=context_key,
        field_key="pet_name",
        mapping_id=mapping_id,
        policy_version=policy_version,
    ) == (1, 0)


def test_reopen_review_reverts_snapshot_from_reviewed_run_even_with_newer_completed_run(
    test_client,
):
    repository = test_client.app.state.document_repository
    baseline = _build_interpretation_artifact(
        document_id="doc-reviewed-run-baseline",
        run_id=str(uuid4()),
        raw_text="Paciente: Luna",
        repository=repository,
    )
    baseline_pet_name = next(
        field for field in baseline["data"]["fields"] if field["key"] == "pet_name"
    )
    context_key = str(baseline_pet_name["context_key"])
    mapping_id = baseline_pet_name.get("mapping_id")
    policy_version = str(baseline_pet_name["policy_version"])

    document_id = _upload_sample_document(test_client)
    reviewed_run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=reviewed_run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    _insert_structured_interpretation(
        run_id=reviewed_run_id,
        data={
            "document_id": document_id,
            "processing_run_id": reviewed_run_id,
            "created_at": "2026-02-10T10:00:05+00:00",
            "global_schema": baseline["data"]["global_schema"],
            "fields": [
                {
                    "field_id": "field-1",
                    "key": "pet_name",
                    "value": "Luna",
                    "value_type": "string",
                    "field_candidate_confidence": 0.66,
                    "field_mapping_confidence": 0.66,
                    "field_review_history_adjustment": 0.0,
                    "mapping_id": mapping_id,
                    "context_key": context_key,
                    "policy_version": policy_version,
                    "is_critical": True,
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Paciente: Luna"},
                }
            ],
        },
    )

    marked = test_client.post(f"/documents/{document_id}/reviewed")
    assert marked.status_code == 200
    assert _get_calibration_counts(
        context_key=context_key,
        field_key="pet_name",
        mapping_id=mapping_id,
        policy_version=policy_version,
    ) == (1, 0)

    newer_run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=newer_run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    _insert_structured_interpretation(run_id=newer_run_id)

    reopened = test_client.delete(f"/documents/{document_id}/reviewed")
    assert reopened.status_code == 200
    assert _get_calibration_counts(
        context_key=context_key,
        field_key="pet_name",
        mapping_id=mapping_id,
        policy_version=policy_version,
    ) == (0, 0)


def test_reviewed_toggle_returns_not_found_for_unknown_document(test_client):
    response = test_client.post("/documents/00000000-0000-0000-0000-000000000000/reviewed")
    assert response.status_code == 404
    assert response.json()["error_code"] == "NOT_FOUND"

    reopen_response = test_client.delete("/documents/00000000-0000-0000-0000-000000000000/reviewed")
    assert reopen_response.status_code == 404
    assert reopen_response.json()["error_code"] == "NOT_FOUND"


def test_interpretation_edit_creates_new_version_and_change_logs(test_client):
    document_id = _upload_sample_document(test_client)
    run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    _insert_structured_interpretation(run_id=run_id)

    response = test_client.post(
        f"/runs/{run_id}/interpretations",
        json={
            "base_version_number": 1,
            "changes": [
                {
                    "op": "UPDATE",
                    "field_id": "field-1",
                    "value": "Nala",
                    "value_type": "string",
                },
                {
                    "op": "ADD",
                    "key": "new_custom_key",
                    "value": "new-value",
                    "value_type": "string",
                },
            ],
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["run_id"] == run_id
    assert payload["version_number"] == 2
    edited_fields = payload["data"]["fields"]
    edited_pet_name = next(field for field in edited_fields if field["field_id"] == "field-1")
    added_custom_field = next(field for field in edited_fields if field["key"] == "new_custom_key")
    assert any(
        field["field_id"] == "field-1" and field["value"] == "Nala" and field["origin"] == "human"
        for field in edited_fields
    )
    assert any(
        field["key"] == "new_custom_key"
        and field["value"] == "new-value"
        and field["origin"] == "human"
        for field in edited_fields
    )
    assert edited_pet_name["field_candidate_confidence"] == pytest.approx(0.5, abs=1e-9)
    assert edited_pet_name["field_mapping_confidence"] == pytest.approx(0.5, abs=1e-9)
    assert added_custom_field["field_candidate_confidence"] == pytest.approx(0.5, abs=1e-9)
    assert added_custom_field["field_mapping_confidence"] == pytest.approx(0.5, abs=1e-9)

    with database.get_connection() as conn:
        interpretation_rows = conn.execute(
            """
            SELECT payload
            FROM artifacts
            WHERE run_id = ? AND artifact_type = 'STRUCTURED_INTERPRETATION'
            ORDER BY created_at ASC
            """,
            (run_id,),
        ).fetchall()
        change_log_rows = conn.execute(
            """
            SELECT payload
            FROM artifacts
            WHERE run_id = ? AND artifact_type = 'FIELD_CHANGE_LOG'
            ORDER BY created_at ASC
            """,
            (run_id,),
        ).fetchall()

    assert len(interpretation_rows) == 2
    assert len(change_log_rows) == 2
    parsed_logs = [json.loads(row["payload"]) for row in change_log_rows]
    assert {entry["change_type"] for entry in parsed_logs} == {"ADD", "UPDATE"}
    assert all(str(entry["field_path"]).startswith("fields.") for entry in parsed_logs)


def test_interpretation_edit_noop_update_keeps_origin_and_skips_change_log(test_client):
    document_id = _upload_sample_document(test_client)
    run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    _insert_structured_interpretation(run_id=run_id)

    response = test_client.post(
        f"/runs/{run_id}/interpretations",
        json={
            "base_version_number": 1,
            "changes": [
                {
                    "op": "UPDATE",
                    "field_id": "field-1",
                    "value": "Luna",
                    "value_type": "string",
                }
            ],
        },
    )

    assert response.status_code == 201
    payload = response.json()
    field = next(item for item in payload["data"]["fields"] if item["field_id"] == "field-1")
    assert field["value"] == "Luna"
    assert field["origin"] == "machine"

    with database.get_connection() as conn:
        change_log_rows = conn.execute(
            """
            SELECT payload
            FROM artifacts
            WHERE run_id = ? AND artifact_type = 'FIELD_CHANGE_LOG'
            ORDER BY created_at ASC
            """,
            (run_id,),
        ).fetchall()
    assert len(change_log_rows) == 0


def test_interpretation_edit_whitespace_only_update_is_noop_for_strings(test_client):
    document_id = _upload_sample_document(test_client)
    run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    _insert_structured_interpretation(run_id=run_id)

    response = test_client.post(
        f"/runs/{run_id}/interpretations",
        json={
            "base_version_number": 1,
            "changes": [
                {
                    "op": "UPDATE",
                    "field_id": "field-1",
                    "value": "   Luna   ",
                    "value_type": "string",
                }
            ],
        },
    )

    assert response.status_code == 201
    payload = response.json()
    field = next(item for item in payload["data"]["fields"] if item["field_id"] == "field-1")
    assert field["value"] == "Luna"
    assert field["origin"] == "machine"

    with database.get_connection() as conn:
        change_log_rows = conn.execute(
            """
            SELECT payload
            FROM artifacts
            WHERE run_id = ? AND artifact_type = 'FIELD_CHANGE_LOG'
            ORDER BY created_at ASC
            """,
            (run_id,),
        ).fetchall()
    assert len(change_log_rows) == 0


def test_interpretation_edit_real_update_still_marks_human_and_logs_change(test_client):
    document_id = _upload_sample_document(test_client)
    run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    _insert_structured_interpretation(run_id=run_id)

    response = test_client.post(
        f"/runs/{run_id}/interpretations",
        json={
            "base_version_number": 1,
            "changes": [
                {
                    "op": "UPDATE",
                    "field_id": "field-1",
                    "value": "Nala",
                    "value_type": "string",
                }
            ],
        },
    )

    assert response.status_code == 201
    payload = response.json()
    field = next(item for item in payload["data"]["fields"] if item["field_id"] == "field-1")
    assert field["value"] == "Nala"
    assert field["origin"] == "human"
    assert field["field_candidate_confidence"] == pytest.approx(0.5, abs=1e-9)
    assert field["field_mapping_confidence"] == pytest.approx(0.5, abs=1e-9)

    with database.get_connection() as conn:
        change_log_rows = conn.execute(
            """
            SELECT payload
            FROM artifacts
            WHERE run_id = ? AND artifact_type = 'FIELD_CHANGE_LOG'
            ORDER BY created_at ASC
            """,
            (run_id,),
        ).fetchall()
    assert len(change_log_rows) == 1
    change_log = json.loads(change_log_rows[0]["payload"])
    assert change_log["change_type"] == "UPDATE"
    assert change_log["old_value"] == "Luna"
    assert change_log["new_value"] == "Nala"


def test_interpretation_edit_update_preserves_prior_candidate_confidence(test_client):
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
                    "field_id": "field-1",
                    "key": "pet_name",
                    "value": "Luna",
                    "value_type": "string",
                    "field_candidate_confidence": 0.66,
                    "field_review_history_adjustment": -10,
                    "field_mapping_confidence": 0.56,
                    "is_critical": False,
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Paciente: Luna"},
                }
            ],
        },
    )

    response = test_client.post(
        f"/runs/{run_id}/interpretations",
        json={
            "base_version_number": 1,
            "changes": [
                {
                    "op": "UPDATE",
                    "field_id": "field-1",
                    "value": "Nala",
                    "value_type": "string",
                }
            ],
        },
    )

    assert response.status_code == 201
    payload = response.json()
    field = next(item for item in payload["data"]["fields"] if item["field_id"] == "field-1")
    assert field["origin"] == "human"
    assert field["field_candidate_confidence"] == pytest.approx(0.66, abs=1e-9)
    assert field["field_review_history_adjustment"] == pytest.approx(0.0, abs=1e-9)
    assert field["field_mapping_confidence"] == pytest.approx(0.66, abs=1e-9)


def test_interpretation_edit_returns_conflict_when_active_run_exists(test_client):
    document_id = _upload_sample_document(test_client)
    completed_run_id = str(uuid4())
    running_run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=completed_run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    _insert_structured_interpretation(run_id=completed_run_id)
    _insert_run(
        document_id=document_id,
        run_id=running_run_id,
        state=app_models.ProcessingRunState.RUNNING,
        failure_type=None,
    )

    response = test_client.post(
        f"/runs/{completed_run_id}/interpretations",
        json={
            "base_version_number": 1,
            "changes": [
                {
                    "op": "UPDATE",
                    "field_id": "field-1",
                    "value": "Nala",
                    "value_type": "string",
                }
            ],
        },
    )

    assert response.status_code == 409
    payload = response.json()
    assert payload["error_code"] == "CONFLICT"
    assert payload["details"]["reason"] == "REVIEW_BLOCKED_BY_ACTIVE_RUN"


def test_interpretation_edit_returns_conflict_when_base_version_mismatches(test_client):
    document_id = _upload_sample_document(test_client)
    run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    _insert_structured_interpretation(run_id=run_id)

    response = test_client.post(
        f"/runs/{run_id}/interpretations",
        json={
            "base_version_number": 2,
            "changes": [
                {
                    "op": "UPDATE",
                    "field_id": "field-1",
                    "value": "Nala",
                    "value_type": "string",
                }
            ],
        },
    )

    assert response.status_code == 409
    payload = response.json()
    assert payload["error_code"] == "CONFLICT"
    assert payload["details"]["reason"] == "BASE_VERSION_MISMATCH"


def test_interpretation_edit_returns_conflict_when_interpretation_is_missing(test_client):
    document_id = _upload_sample_document(test_client)
    run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )

    response = test_client.post(
        f"/runs/{run_id}/interpretations",
        json={
            "base_version_number": 1,
            "changes": [
                {
                    "op": "UPDATE",
                    "field_id": "field-1",
                    "value": "Nala",
                    "value_type": "string",
                }
            ],
        },
    )

    assert response.status_code == 409
    payload = response.json()
    assert payload["error_code"] == "CONFLICT"
    assert payload["details"]["reason"] == "INTERPRETATION_MISSING"


def test_interpretation_edits_append_correction_signals_without_changing_review_flow(test_client):
    document_id = _upload_sample_document(test_client)
    run_id = str(uuid4())
    _insert_run(
        document_id=document_id,
        run_id=run_id,
        state=app_models.ProcessingRunState.COMPLETED,
        failure_type=None,
    )
    _insert_structured_interpretation(run_id=run_id)

    first_edit = test_client.post(
        f"/runs/{run_id}/interpretations",
        json={
            "base_version_number": 1,
            "changes": [
                {
                    "op": "UPDATE",
                    "field_id": "field-1",
                    "value": "Nala",
                    "value_type": "string",
                }
            ],
        },
    )
    assert first_edit.status_code == 201
    first_payload = first_edit.json()
    assert first_payload["version_number"] == 2
    assert set(first_payload.keys()) == {"run_id", "interpretation_id", "version_number", "data"}

    second_edit = test_client.post(
        f"/runs/{run_id}/interpretations",
        json={
            "base_version_number": 2,
            "changes": [
                {
                    "op": "UPDATE",
                    "field_id": "field-1",
                    "value": "Kira",
                    "value_type": "string",
                }
            ],
        },
    )
    assert second_edit.status_code == 201
    second_payload = second_edit.json()
    assert second_payload["version_number"] == 3
    assert set(second_payload.keys()) == {"run_id", "interpretation_id", "version_number", "data"}

    with database.get_connection() as conn:
        change_log_rows = conn.execute(
            """
            SELECT payload
            FROM artifacts
            WHERE run_id = ? AND artifact_type = 'FIELD_CHANGE_LOG'
            ORDER BY created_at ASC, rowid ASC
            """,
            (run_id,),
        ).fetchall()
        run_state_row = conn.execute(
            """
            SELECT state
            FROM processing_runs
            WHERE run_id = ?
            """,
            (run_id,),
        ).fetchone()

    parsed_logs = [json.loads(row["payload"]) for row in change_log_rows]
    assert len(parsed_logs) == 2
    assert parsed_logs[0]["old_value"] == "Luna"
    assert parsed_logs[0]["new_value"] == "Nala"
    assert parsed_logs[1]["old_value"] == "Nala"
    assert parsed_logs[1]["new_value"] == "Kira"
    for entry in parsed_logs:
        assert "event_type" in entry
        assert "source" in entry
        assert "document_id" in entry
        assert "run_id" in entry
        assert "interpretation_id" in entry
        assert "base_version_number" in entry
        assert "new_version_number" in entry
        assert "occurred_at" in entry
        assert entry["event_type"] == "field_corrected"
        assert entry["source"] == "reviewer_edit"
        assert entry["document_id"] == document_id
        assert entry["run_id"] == run_id
        assert isinstance(entry["interpretation_id"], str)
        assert entry["interpretation_id"].strip() != ""
        occurred_at = str(entry["occurred_at"])
        assert "T" in occurred_at
        assert occurred_at.endswith("Z")
        datetime.fromisoformat(occurred_at.replace("Z", "+00:00"))
        assert "context_key" in entry
        assert "mapping_id" in entry
        assert "policy_version" in entry
        assert isinstance(entry["context_key"], str)
        assert entry["context_key"].strip() != ""
        assert isinstance(entry["policy_version"], str)
        assert entry["policy_version"].strip() != ""
        assert entry["mapping_id"] is None or (
            isinstance(entry["mapping_id"], str) and entry["mapping_id"].strip() != ""
        )
    assert parsed_logs[0]["base_version_number"] == 1
    assert parsed_logs[0]["new_version_number"] == 2
    assert parsed_logs[1]["base_version_number"] == 2
    assert parsed_logs[1]["new_version_number"] == 3
    assert all(str(entry["field_path"]).startswith("fields.") for entry in parsed_logs)
    assert run_state_row is not None
    assert run_state_row["state"] == app_models.ProcessingRunState.COMPLETED.value
