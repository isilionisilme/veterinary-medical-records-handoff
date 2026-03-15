"""Integration tests covering document review status transitions.

Scenario focus: idempotency and calibration rollback on reviewed-state toggles.
"""

from __future__ import annotations

from uuid import uuid4

from backend.app.application.processing.interpretation import _build_interpretation_artifact
from backend.app.domain import models as app_models
from backend.tests.integration.document_review_test_support import (
    _get_calibration_counts,
    _insert_run,
    _insert_structured_interpretation,
    _upload_sample_document,
)


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
