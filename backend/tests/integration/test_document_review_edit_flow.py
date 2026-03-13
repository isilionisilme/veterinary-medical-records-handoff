"""Integration tests covering successful interpretation edit flows.

Scenario focus: edit versioning, noop handling, and confidence preservation.
"""

from __future__ import annotations

import json
from uuid import uuid4

import pytest

from backend.app.domain import models as app_models
from backend.app.infra import database
from backend.tests.integration.document_review_test_support import (
    _insert_run,
    _insert_structured_interpretation,
    _upload_sample_document,
)


def test_interpretation_edit_creates_new_version_and_change_logs(test_client):
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
            "schema_version": "legacy-review-v1",
            "medical_record_view": {"version": "mvp-1"},
            "global_schema": {"microchip_id": "00023035139"},
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
    assert payload["data"].get("schema_contract") == "visit-grouped-canonical"
    assert "schema_version" not in payload["data"]
    medical_record_view = payload["data"].get("medical_record_view")
    assert isinstance(medical_record_view, dict)
    assert isinstance(medical_record_view.get("sections"), list)
    assert isinstance(medical_record_view.get("field_slots"), list)
    assert isinstance(payload["data"].get("global_schema"), dict)
    assert isinstance(payload["data"].get("visits"), list)
    assert isinstance(payload["data"].get("other_fields"), list)
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
