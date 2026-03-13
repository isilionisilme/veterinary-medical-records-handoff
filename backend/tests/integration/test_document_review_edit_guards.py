"""Integration tests covering guarded interpretation edit flows and correction signals."""

from __future__ import annotations

import json
from datetime import datetime
from uuid import uuid4

from backend.app.domain import models as app_models
from backend.app.infra import database
from backend.tests.integration.document_review_test_support import (
    _insert_run,
    _insert_structured_interpretation,
    _upload_sample_document,
)


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
