"""Integration tests covering core document review endpoint behavior."""

from __future__ import annotations

import re
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.app.domain import models as app_models
from backend.app.infra.file_storage import get_storage_root
from backend.tests.integration.document_review_test_support import (
    _extract_top_level_fields_by_key,
    _insert_run,
    _insert_structured_interpretation,
    _upload_sample_document,
)


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
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200
    data = response.json()["active_interpretation"]["data"]

    assert data.get("schema_contract") == "visit-grouped-canonical"
    assert "schema_version" not in data
    medical_record_view = data.get("medical_record_view")
    assert isinstance(medical_record_view, dict)
    assert isinstance(medical_record_view.get("sections"), list)
    assert isinstance(medical_record_view.get("field_slots"), list)
    assert isinstance(data.get("visits"), list)
    assert isinstance(data.get("other_fields"), list)


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
            "global_schema": {"microchip_id": "00023035139"},
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


def test_document_review_derives_age_from_dob_using_latest_visit_date(test_client):
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
            "global_schema": {
                "dob": "15/03/2018",
                "document_date": "01/02/2026",
                "age": "",
            },
            "fields": [
                {
                    "field_id": "field-dob",
                    "key": "dob",
                    "value": "15/03/2018",
                    "value_type": "date",
                    "is_critical": False,
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Nacimiento: 15/03/2018"},
                },
                {
                    "field_id": "field-visit-date-a",
                    "key": "visit_date",
                    "value": "01/02/2026",
                    "value_type": "date",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 01/02/2026"},
                },
                {
                    "field_id": "field-visit-date-b",
                    "key": "visit_date",
                    "value": "14/03/2026",
                    "value_type": "date",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 14/03/2026"},
                },
            ],
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200

    data = response.json()["active_interpretation"]["data"]
    assert data["global_schema"]["age"] == "7"
    assert data["global_schema"]["age_origin"] == "derived"
    assert data["global_schema"]["age_display"] == "7 a\u00f1os"
    assert (
        re.fullmatch(r"\d+ (a\u00f1o|a\u00f1os|meses)", data["global_schema"]["age_display"])
        is not None
    )

    age_fields = _extract_top_level_fields_by_key(data, "age")
    assert len(age_fields) == 1
    assert age_fields[0]["value"] == "7"
    assert age_fields[0]["origin"] == "derived"
    assert age_fields[0]["display_value"] == "7 a\u00f1os"
    assert age_fields[0]["display_value"] == data["global_schema"]["age_display"]


def test_document_review_keeps_manual_age_when_global_schema_is_out_of_sync(test_client):
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
            "global_schema": {
                "dob": "15/03/2018",
                "document_date": "01/02/2026",
            },
            "fields": [
                {
                    "field_id": "field-age-human",
                    "key": "age",
                    "value": "99",
                    "value_type": "string",
                    "is_critical": True,
                    "origin": "human",
                    "evidence": {"page": 1, "snippet": "Edad: 99"},
                },
                {
                    "field_id": "field-dob",
                    "key": "dob",
                    "value": "15/03/2018",
                    "value_type": "date",
                    "is_critical": False,
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Nacimiento: 15/03/2018"},
                },
                {
                    "field_id": "field-visit-date-b",
                    "key": "visit_date",
                    "value": "14/03/2026",
                    "value_type": "date",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 14/03/2026"},
                },
            ],
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200

    data = response.json()["active_interpretation"]["data"]
    assert data["global_schema"]["age"] == "99"
    assert data["global_schema"]["age_origin"] == "human"
    assert data["global_schema"]["age_display"] == "99 a\u00f1os"

    age_fields = _extract_top_level_fields_by_key(data, "age")
    assert len(age_fields) == 1
    assert age_fields[0]["value"] == "99"
    assert age_fields[0]["origin"] == "human"
    assert age_fields[0]["display_value"] == "99 a\u00f1os"
    assert age_fields[0]["display_value"] == data["global_schema"]["age_display"]


def test_document_review_exposes_months_for_derived_age_under_one_year(test_client):
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
            "global_schema": {
                "dob": "01/10/2025",
                "age": "",
                "document_date": "14/03/2026",
            },
            "fields": [
                {
                    "field_id": "field-dob-under-one",
                    "key": "dob",
                    "value": "01/10/2025",
                    "value_type": "date",
                    "is_critical": False,
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Nacimiento: 01/10/2025"},
                }
            ],
        },
    )

    response = test_client.get(f"/documents/{document_id}/review")
    assert response.status_code == 200

    data = response.json()["active_interpretation"]["data"]
    assert data["global_schema"]["age"] == "0"
    assert data["global_schema"]["age_origin"] == "derived"
    assert data["global_schema"]["age_display"] == "5 meses"
    assert (
        re.fullmatch(r"\d+ (a\u00f1o|a\u00f1os|meses)", data["global_schema"]["age_display"])
        is not None
    )

    age_fields = _extract_top_level_fields_by_key(data, "age")
    assert len(age_fields) == 1
    assert age_fields[0]["value"] == "0"
    assert age_fields[0]["display_value"] == "5 meses"
    assert age_fields[0]["display_value"] == data["global_schema"]["age_display"]


