"""Integration tests for extraction observability debug endpoints."""

from __future__ import annotations

import io
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.application import extraction_observability
from backend.app.main import create_app


def _wait_until(predicate, *, timeout_seconds: float = 4.0, interval_seconds: float = 0.05) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while True:
        if predicate():
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(interval_seconds)


@pytest.fixture
def test_client(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("VET_RECORDS_DB_PATH", str(tmp_path / "documents.db"))
    monkeypatch.setenv("VET_RECORDS_STORAGE_PATH", str(tmp_path / "storage"))
    monkeypatch.setenv("VET_RECORDS_DISABLE_PROCESSING", "true")
    monkeypatch.delenv("VET_RECORDS_EXTRACTION_OBS", raising=False)
    monkeypatch.setattr(extraction_observability, "_OBSERVABILITY_DIR", tmp_path / "obs")

    app = create_app()
    with TestClient(app) as client:
        yield client


def _snapshot_payload() -> dict[str, object]:
    return {
        "runId": "run-1",
        "documentId": "doc-1",
        "createdAt": "2026-02-13T20:00:00Z",
        "schemaVersion": "canonical",
        "fields": {
            "pet_name": {
                "status": "accepted",
                "confidence": "mid",
                "valueNormalized": "Luna",
                "valueRaw": "Luna",
                "reason": None,
            }
        },
        "counts": {
            "totalFields": 1,
            "accepted": 1,
            "rejected": 0,
            "missing": 0,
            "low": 0,
            "mid": 1,
            "high": 0,
        },
    }


def _triage_snapshot_payload() -> dict[str, object]:
    return {
        "runId": "run-triage-1",
        "documentId": "doc-triage-1",
        "createdAt": "2026-02-13T20:01:00Z",
        "schemaVersion": "canonical",
        "fields": {
            "claim_id": {
                "status": "missing",
                "confidence": None,
                "valueNormalized": None,
                "valueRaw": None,
                "reason": None,
            },
            "weight": {
                "status": "rejected",
                "confidence": None,
                "valueNormalized": None,
                "valueRaw": "cien kilos",
                "reason": "invalid-format",
                "rawCandidate": "cien kilos",
                "sourceHint": "page:2",
            },
            "microchip_id": {
                "status": "accepted",
                "confidence": "mid",
                "valueNormalized": "Maria Lopez Calle 123",
                "valueRaw": "Maria Lopez Calle 123",
                "reason": None,
                "rawCandidate": "Maria Lopez Calle 123",
                "sourceHint": "page:1",
            },
            "species": {
                "status": "accepted",
                "confidence": "low",
                "valueNormalized": "equino",
                "valueRaw": "equino",
                "reason": None,
                "rawCandidate": "equino",
                "sourceHint": "page:1",
            },
            "sex": {
                "status": "accepted",
                "confidence": "low",
                "valueNormalized": "desconocido",
                "valueRaw": "desconocido",
                "reason": None,
                "rawCandidate": "desconocido",
                "sourceHint": "page:1",
            },
            "notes": {
                "status": "accepted",
                "confidence": "high",
                "valueNormalized": "A" * 90,
                "valueRaw": "A" * 90,
                "reason": None,
                "rawCandidate": "A" * 90,
                "sourceHint": "page:3",
            },
        },
        "counts": {
            "totalFields": 6,
            "accepted": 4,
            "rejected": 1,
            "missing": 1,
            "low": 2,
            "mid": 1,
            "high": 1,
        },
    }


def test_debug_extraction_endpoints_return_forbidden_when_disabled(test_client: TestClient) -> None:
    post_response = test_client.post("/debug/extraction-runs", json=_snapshot_payload())
    get_response = test_client.get("/debug/extraction-runs/doc-1")
    triage_response = test_client.get("/debug/extraction-runs/doc-1/triage")

    assert post_response.status_code == 403
    assert post_response.json() == {
        "error": "extraction_observability_disabled",
        "hint": "Set VET_RECORDS_EXTRACTION_OBS=1 and restart backend",
    }
    assert get_response.status_code == 403
    assert get_response.json() == {
        "error": "extraction_observability_disabled",
        "hint": "Set VET_RECORDS_EXTRACTION_OBS=1 and restart backend",
    }
    assert triage_response.status_code == 403
    assert triage_response.json() == {
        "error": "extraction_observability_disabled",
        "hint": "Set VET_RECORDS_EXTRACTION_OBS=1 and restart backend",
    }


def test_debug_extraction_endpoints_persist_and_list_when_enabled(
    test_client: TestClient, monkeypatch
) -> None:
    monkeypatch.setenv("VET_RECORDS_EXTRACTION_OBS", "1")

    first_post_response = test_client.post("/debug/extraction-runs", json=_snapshot_payload())
    assert first_post_response.status_code == 201
    assert first_post_response.json()["document_id"] == "doc-1"

    second_post_response = test_client.post("/debug/extraction-runs", json=_snapshot_payload())
    assert second_post_response.status_code == 200
    assert second_post_response.json()["document_id"] == "doc-1"

    get_response = test_client.get("/debug/extraction-runs/doc-1")
    assert get_response.status_code == 200
    payload = get_response.json()
    assert payload["document_id"] == "doc-1"
    assert len(payload["runs"]) == 1
    assert payload["runs"][0]["runId"] == "run-1"


def test_debug_extraction_triage_endpoint_returns_expected_shape(
    test_client: TestClient, monkeypatch
) -> None:
    monkeypatch.setenv("VET_RECORDS_EXTRACTION_OBS", "1")

    post_response = test_client.post("/debug/extraction-runs", json=_triage_snapshot_payload())
    assert post_response.status_code == 201

    triage_response = test_client.get("/debug/extraction-runs/doc-triage-1/triage")
    assert triage_response.status_code == 200
    payload = triage_response.json()

    assert payload["documentId"] == "doc-triage-1"
    assert payload["runId"] == "run-triage-1"
    assert payload["createdAt"] == "2026-02-13T20:01:00Z"
    assert payload["summary"] == {
        "accepted": 4,
        "missing": 1,
        "rejected": 1,
        "low": 2,
        "mid": 1,
        "high": 1,
    }

    assert payload["missing"] == [
        {
            "field": "claim_id",
            "value": None,
            "reason": "missing",
            "flags": [],
            "rawCandidate": None,
            "sourceHint": None,
        }
    ]

    assert payload["rejected"] == [
        {
            "field": "weight",
            "value": "cien kilos",
            "reason": "invalid-format",
            "flags": [],
            "rawCandidate": "cien kilos",
            "sourceHint": "page:2",
        }
    ]

    suspicious_by_field = {item["field"]: item for item in payload["suspiciousAccepted"]}
    assert "microchip_id" in suspicious_by_field
    assert "species" in suspicious_by_field
    assert "sex" in suspicious_by_field
    assert "notes" in suspicious_by_field
    assert "microchip_non_digit_characters" in suspicious_by_field["microchip_id"]["flags"]
    assert "species_outside_allowed_set" in suspicious_by_field["species"]["flags"]
    assert "sex_outside_allowed_set" in suspicious_by_field["sex"]["flags"]
    assert "value_too_long" in suspicious_by_field["notes"]["flags"]


def test_debug_extraction_triage_endpoint_returns_not_found_without_runs(
    test_client: TestClient, monkeypatch
) -> None:
    monkeypatch.setenv("VET_RECORDS_EXTRACTION_OBS", "1")

    triage_response = test_client.get("/debug/extraction-runs/doc-without-runs/triage")

    assert triage_response.status_code == 404
    assert triage_response.json() == {
        "error_code": "NOT_FOUND",
        "message": "No extraction snapshots found for this document.",
    }


def test_debug_extraction_summary_endpoint_returns_ranked_aggregate(
    test_client: TestClient, monkeypatch
) -> None:
    monkeypatch.setenv("VET_RECORDS_EXTRACTION_OBS", "1")

    payload = _triage_snapshot_payload()
    payload["runId"] = "run-triage-2"
    payload["fields"]["visit_date"] = {
        "status": "rejected",
        "confidence": None,
        "valueRaw": "08/12/19",
        "reason": "invalid-date",
        "rawCandidate": "08/12/19",
        "topCandidates": [{"value": "08/12/19", "confidence": 0.84}],
    }
    payload["counts"] = {
        "totalFields": 7,
        "accepted": 4,
        "rejected": 2,
        "missing": 1,
        "low": 2,
        "mid": 1,
        "high": 1,
    }

    post_response = test_client.post("/debug/extraction-runs", json=payload)
    assert post_response.status_code == 201

    summary_response = test_client.get("/debug/extraction-runs/doc-triage-1/summary?limit=20")
    assert summary_response.status_code == 200
    body = summary_response.json()

    assert body["document_id"] == "doc-triage-1"
    assert body["considered_runs"] == 1
    assert "missing_fields_with_candidates" in body
    assert "missing_fields_without_candidates" in body
    assert isinstance(body["fields"], list)
    assert isinstance(body["most_missing_fields"], list)
    assert isinstance(body["most_rejected_fields"], list)

    missing_by_field = {item["field"]: item for item in body["most_missing_fields"]}
    assert missing_by_field["claim_id"]["has_candidates"] is False
    assert missing_by_field["claim_id"]["top_key_tokens"] is None

    rejected_by_field = {item["field"]: item for item in body["most_rejected_fields"]}
    assert rejected_by_field["visit_date"]["rejected_count"] == 1
    assert rejected_by_field["visit_date"]["top1_sample"] == "08/12/19"


def test_debug_extraction_summary_endpoint_filters_by_run_id(
    test_client: TestClient, monkeypatch
) -> None:
    monkeypatch.setenv("VET_RECORDS_EXTRACTION_OBS", "1")

    first_payload = _triage_snapshot_payload()
    first_payload["runId"] = "run-triage-filter-a"
    post_first = test_client.post("/debug/extraction-runs", json=first_payload)
    assert post_first.status_code == 201

    second_payload = _triage_snapshot_payload()
    second_payload["runId"] = "run-triage-filter-b"
    second_payload["fields"]["claim_id"] = {
        "status": "accepted",
        "confidence": "mid",
        "valueNormalized": "CLM-2026-02",
        "valueRaw": "CLM-2026-02",
        "reason": None,
    }
    second_payload["counts"] = {
        "totalFields": 6,
        "accepted": 5,
        "rejected": 1,
        "missing": 0,
        "low": 2,
        "mid": 2,
        "high": 1,
    }
    post_second = test_client.post("/debug/extraction-runs", json=second_payload)
    assert post_second.status_code == 201

    filtered = test_client.get(
        "/debug/extraction-runs/doc-triage-1/summary?limit=20&run_id=run-triage-filter-b"
    )
    assert filtered.status_code == 200
    body = filtered.json()

    assert body["total_runs"] == 2
    assert body["considered_runs"] == 1
    missing_by_field = {item["field"]: item for item in body["most_missing_fields"]}
    assert "claim_id" not in missing_by_field

    filtered_missing = test_client.get(
        "/debug/extraction-runs/doc-triage-1/summary?limit=20&run_id=run-triage-filter-a"
    )
    assert filtered_missing.status_code == 200
    missing_body = filtered_missing.json()
    missing_by_field_a = {item["field"]: item for item in missing_body["most_missing_fields"]}
    assert missing_by_field_a["claim_id"]["missing_count"] == 1


def test_debug_extraction_summary_endpoint_returns_not_found_for_unknown_run_id(
    test_client: TestClient, monkeypatch
) -> None:
    monkeypatch.setenv("VET_RECORDS_EXTRACTION_OBS", "1")

    payload = _triage_snapshot_payload()
    payload["runId"] = "run-triage-existing"
    post_response = test_client.post("/debug/extraction-runs", json=payload)
    assert post_response.status_code == 201

    summary_response = test_client.get(
        "/debug/extraction-runs/doc-triage-1/summary?limit=20&run_id=run-triage-missing"
    )
    assert summary_response.status_code == 404
    assert summary_response.json() == {
        "error_code": "NOT_FOUND",
        "message": "No extraction snapshots found for this document.",
    }


def test_debug_extraction_summary_endpoint_reads_auto_persisted_snapshot_after_processing(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("VET_RECORDS_DB_PATH", str(tmp_path / "documents.db"))
    monkeypatch.setenv("VET_RECORDS_STORAGE_PATH", str(tmp_path / "storage"))
    monkeypatch.delenv("VET_RECORDS_DISABLE_PROCESSING", raising=False)
    monkeypatch.setenv("VET_RECORDS_EXTRACTION_OBS", "1")
    monkeypatch.setattr(extraction_observability, "_OBSERVABILITY_DIR", tmp_path / "obs")
    monkeypatch.setattr(
        "backend.app.application.processing.pdf_extraction._extract_pdf_text_with_extractor",
        lambda _path: (
            "Paciente: Luna\nEspecie: canino\nRaza: mestizo\nDiagnostico: control",
            "test",
        ),
    )

    app = create_app()
    with TestClient(app) as processing_client:
        files = {
            "file": (
                "record.pdf",
                io.BytesIO(b"%PDF-1.5 auto snapshot processing test"),
                "application/pdf",
            )
        }
        upload_response = processing_client.post("/documents/upload", files=files)
        assert upload_response.status_code == 201
        document_id = upload_response.json()["document_id"]

        run_id: str | None = None

        def _review_ready() -> bool:
            nonlocal run_id
            review_response = processing_client.get(f"/documents/{document_id}/review")
            if review_response.status_code == 200:
                run_id = review_response.json()["latest_completed_run"]["run_id"]
                return True
            return False

        assert _wait_until(_review_ready)

        assert run_id is not None

        summary_response = processing_client.get(
            f"/debug/extraction-runs/{document_id}/summary?limit=20&run_id={run_id}"
        )
        assert summary_response.status_code == 200
        summary = summary_response.json()
        assert summary["considered_runs"] == 1
        assert summary["total_runs"] >= 1
