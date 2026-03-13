"""Integration tests covering document review confidence and learning signals.

Scenario focus: calibration deltas, confidence composition, and learning updates.
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from backend.app.application.processing_runner import _build_interpretation_artifact
from backend.app.domain import models as app_models
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
