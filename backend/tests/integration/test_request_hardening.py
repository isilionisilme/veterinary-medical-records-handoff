from __future__ import annotations

import asyncio
import json
from uuid import uuid4

from backend.app.domain import models as app_models
from backend.app.infra.file_storage import get_storage_root
from backend.tests.integration.document_review_test_support import (
    _insert_run,
    _insert_structured_interpretation,
    _upload_sample_document,
)


def _json_body_with_exact_size(template: dict[str, object], target_size: int) -> bytes:
    payload = json.loads(json.dumps(template))
    encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    if len(encoded) > target_size:
        raise ValueError("Template already exceeds target size")

    field_path = payload["changes"][0]
    if not isinstance(field_path, dict):
        raise ValueError("Unexpected payload structure")
    field_path["value"] = "x" * (target_size - len(encoded))
    encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    if len(encoded) != target_size:
        raise ValueError("Failed to generate exact-size JSON payload")
    return encoded


def _send_raw_http_request(
    app, *, path: str, body: bytes, chunk_size: int = 65536
) -> tuple[int, bytes]:
    headers = [
        (b"host", b"testserver"),
        (b"content-type", b"application/json"),
    ]
    chunks = [body[index : index + chunk_size] for index in range(0, len(body), chunk_size)]
    if not chunks:
        chunks = [b""]
    messages = [
        {
            "type": "http.request",
            "body": chunk,
            "more_body": index < len(chunks) - 1,
        }
        for index, chunk in enumerate(chunks)
    ]
    sent_messages: list[dict[str, object]] = []

    async def _receive() -> dict[str, object]:
        if messages:
            return messages.pop(0)
        return {"type": "http.request", "body": b"", "more_body": False}

    async def _send(message: dict[str, object]) -> None:
        sent_messages.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("utf-8"),
        "query_string": b"",
        "headers": headers,
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
        "state": {},
    }

    asyncio.run(app(scope, _receive, _send))

    status_code = next(
        int(message["status"])
        for message in sent_messages
        if message["type"] == "http.response.start"
    )
    response_body = b"".join(
        message.get("body", b"")
        for message in sent_messages
        if message["type"] == "http.response.body"
    )
    return status_code, response_body


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


def test_interpretation_edit_accepts_request_body_at_exactly_1mb(
    test_client_factory,
) -> None:
    client = test_client_factory()
    payload = _json_body_with_exact_size(
        {
            "base_version_number": 1,
            "changes": [
                {
                    "op": "ADD",
                    "key": "notes",
                    "value": "",
                    "value_type": "string",
                }
            ],
        },
        1024 * 1024,
    )

    with client:
        response = client.post(
            f"/runs/{uuid4()}/interpretations",
            content=payload,
            headers={"content-type": "application/json"},
        )

    assert response.status_code == 404
    assert response.json()["error_code"] == "NOT_FOUND"


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


def test_interpretation_edit_rejects_streamed_request_without_content_length(
    monkeypatch,
    db_path,
    storage_path,
) -> None:
    monkeypatch.setenv("VET_RECORDS_DB_PATH", str(db_path))
    monkeypatch.setenv("VET_RECORDS_STORAGE_PATH", str(storage_path))
    monkeypatch.setenv("VET_RECORDS_DISABLE_PROCESSING", "true")

    from backend.app.main import create_app

    app = create_app()
    payload = {
        "base_version_number": 1,
        "changes": [
            {
                "op": "ADD",
                "key": "notes",
                "value": "x" * (1024 * 1024 + 1),
                "value_type": "string",
            }
        ],
    }
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")

    status_code, response_body = _send_raw_http_request(
        app,
        path=f"/runs/{uuid4()}/interpretations",
        body=body,
    )

    assert status_code == 413
    assert json.loads(response_body)["error_code"] == "REQUEST_BODY_TOO_LARGE"
