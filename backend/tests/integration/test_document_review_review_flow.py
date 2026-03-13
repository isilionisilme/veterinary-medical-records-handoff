"""Integration tests covering document review confidence, review, and edit flows."""

from __future__ import annotations

import json
from datetime import datetime
from uuid import uuid4

import pytest

from backend.app.application.processing_runner import _build_interpretation_artifact
from backend.app.domain import models as app_models
from backend.app.infra import database
from backend.tests.integration.document_review_test_support import (
    _get_calibration_counts,
    _insert_run,
    _insert_structured_interpretation,
    _upload_sample_document,
)


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
