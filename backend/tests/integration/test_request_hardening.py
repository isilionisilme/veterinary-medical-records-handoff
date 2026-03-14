from __future__ import annotations

from uuid import uuid4

from backend.app.domain import models as app_models
from backend.app.infra.file_storage import get_storage_root
from backend.tests.integration.document_review_test_support import (
    _insert_run,
    _insert_structured_interpretation,
    _upload_sample_document,
)


def test_review_debug_endpoint_returns_403_when_flag_disabled(
    monkeypatch, test_client_factory
) -> None:
    monkeypatch.delenv("VET_RECORDS_DEBUG_ENDPOINTS", raising=False)
    client = test_client_factory()

    with client:
        response = client.get(f"/documents/{uuid4()}/review/debug/visits")

    assert response.status_code == 403
    assert response.json() == {
        "error_code": "FORBIDDEN",
        "message": "Debug endpoints are disabled.",
    }


def test_review_debug_endpoint_returns_200_when_flag_enabled(
    monkeypatch, test_client_factory
) -> None:
    monkeypatch.setenv("VET_RECORDS_DEBUG_ENDPOINTS", "true")
    client = test_client_factory()

    with client:
        document_id = _upload_sample_document(client)
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
                        "field_id": "f-symptoms-1",
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
                    }
                ],
                "visits": [],
                "other_fields": [],
            },
        )

        raw_text_path = get_storage_root() / document_id / "runs" / run_id / "raw-text.txt"
        raw_text_path.parent.mkdir(parents=True, exist_ok=True)
        raw_text_path.write_text(
            "Consulta 11/02/2026: dolor de oido.\n",
            encoding="utf-8",
        )

        response = client.get(f"/documents/{document_id}/review/debug/visits")

    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("text/html")


def test_mark_reviewed_rejects_request_bodies_larger_than_1mb(
    test_client_factory,
) -> None:
    client = test_client_factory()

    with client:
        document_id = _upload_sample_document(client)
        response = client.post(
            f"/documents/{document_id}/reviewed",
            content="x" * (1024 * 1024 + 1),
            headers={"content-type": "text/plain"},
        )

    assert response.status_code == 413
    assert response.json()["error_code"] == "REQUEST_BODY_TOO_LARGE"


def test_interpretation_edit_rejects_request_bodies_larger_than_1mb(
    test_client_factory,
) -> None:
    client = test_client_factory()

    with client:
        response = client.post(
            f"/runs/{uuid4()}/interpretations",
            json={
                "base_version_number": 1,
                "changes": [
                    {
                        "op": "ADD",
                        "key": "notes",
                        "value": "x" * (1024 * 1024 + 1),
                        "value_type": "string",
                    }
                ],
            },
        )

    assert response.status_code == 413
    assert response.json()["error_code"] == "REQUEST_BODY_TOO_LARGE"


def test_extraction_debug_post_rejects_request_bodies_larger_than_1mb(
    test_client_factory,
) -> None:
    client = test_client_factory(extraction_obs="1")

    with client:
        response = client.post(
            "/debug/extraction-runs",
            json={
                "runId": "run-large",
                "documentId": "doc-large",
                "createdAt": "2026-02-13T20:00:00Z",
                "schemaVersion": "canonical",
                "fields": {
                    "notes": {
                        "status": "accepted",
                        "confidence": "high",
                        "valueNormalized": "x" * (1024 * 1024 + 1),
                        "valueRaw": "x" * 16,
                        "reason": None,
                    }
                },
                "counts": {
                    "totalFields": 1,
                    "accepted": 1,
                    "rejected": 0,
                    "missing": 0,
                    "low": 0,
                    "mid": 0,
                    "high": 1,
                },
            },
        )

    assert response.status_code == 413
    assert response.json()["error_code"] == "REQUEST_BODY_TOO_LARGE"
