"""Integration tests covering document review debug and observability endpoints."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from backend.app.domain import models as app_models
from backend.app.infra.file_storage import get_storage_root
from backend.tests.integration.document_review_test_support import (
    _insert_run,
    _insert_structured_interpretation,
    _upload_sample_document,
)


def test_document_review_debug_visit_page_renders_html_with_raw_context(test_client):
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
                },
                {
                    "field_id": "f-procedure-2",
                    "key": "procedure",
                    "value": "Limpieza",
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
            ],
            "visits": [],
            "other_fields": [],
        },
    )

    raw_text_path = get_storage_root() / document_id / "runs" / run_id / "raw-text.txt"
    raw_text_path.parent.mkdir(parents=True, exist_ok=True)
    raw_text_path.write_text(
        (
            "Consulta 11/02/2026: dolor de oido.\n"
            "Se prescribe tratamiento topico.\n"
            "Control 18/02/2026: limpieza auricular.\n"
            "Alta con seguimiento en 7 dias.\n"
        ),
        encoding="utf-8",
    )

    response = test_client.get(f"/documents/{document_id}/review/debug/visits")
    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("text/html")
    assert "Debug de visitas" in response.text
    assert "11/02/2026: dolor de oido." in response.text
    assert "18/02/2026: limpieza auricular." in response.text
    assert "Se prescribe tratamiento topico." in response.text


def test_document_review_debug_visit_page_handles_missing_raw_text(test_client):
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

    response = test_client.get(f"/documents/{document_id}/review/debug/visits")
    assert response.status_code == 200
    assert "Raw text no disponible para este run." in response.text


def test_document_review_debug_visit_page_handles_raw_text_read_error(test_client, monkeypatch):
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

    original_read_text = Path.read_text

    def _patched_read_text(self: Path, *args, **kwargs):  # type: ignore[no-untyped-def]
        if self == raw_text_path:
            raise OSError("simulated read failure")
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", _patched_read_text)

    response = test_client.get(f"/documents/{document_id}/review/debug/visits")
    assert response.status_code == 200
    assert "Raw text no disponible para este run." in response.text


def test_document_review_debug_visit_page_trims_next_visit_boundary_marker(test_client):
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
                    "field_id": "f-diagnosis-1",
                    "key": "diagnosis",
                    "value": "Otitis",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026: otitis externa"},
                },
                {
                    "field_id": "f-procedure-2",
                    "key": "procedure",
                    "value": "Limpieza",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 18/02/2026: limpieza auricular"},
                },
            ],
            "visits": [],
            "other_fields": [],
        },
    )

    raw_text_path = get_storage_root() / document_id / "runs" / run_id / "raw-text.txt"
    raw_text_path.parent.mkdir(parents=True, exist_ok=True)
    raw_text_path.write_text(
        (
            "Consulta 11/02/2026: otitis externa.\n"
            "Sin hallazgos adicionales.\n"
            "\uf133VISITA CONSULTA GENERAL DEL D\u00cdA\n"
            "Consulta 18/02/2026: limpieza auricular.\n"
        ),
        encoding="utf-8",
    )

    response = test_client.get(f"/documents/{document_id}/review/debug/visits")
    assert response.status_code == 200
    assert "11/02/2026: otitis externa." in response.text
    assert "18/02/2026: limpieza auricular." in response.text
    assert "VISITA CONSULTA GENERAL DEL D\u00cdA" not in response.text


def test_document_review_visit_scoping_observability_returns_metrics(test_client):
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
            "fields": [],
            "visits": [
                {
                    "visit_id": "visit-1",
                    "visit_date": "2026-02-11",
                    "fields": [
                        {
                            "field_id": "f-diagnosis-1",
                            "key": "diagnosis",
                            "value": "Otitis",
                            "value_type": "string",
                        }
                    ],
                },
                {
                    "visit_id": "visit-2",
                    "visit_date": "2026-02-18",
                    "fields": [
                        {
                            "field_id": "f-procedure-2",
                            "key": "procedure",
                            "value": "Limpieza",
                            "value_type": "string",
                        }
                    ],
                },
                {
                    "visit_id": "unassigned",
                    "visit_date": None,
                    "fields": [
                        {
                            "field_id": "f-unknown-3",
                            "key": "other",
                            "value": "Dato sin visita",
                            "value_type": "string",
                        }
                    ],
                },
            ],
            "other_fields": [],
        },
    )

    raw_text_path = get_storage_root() / document_id / "runs" / run_id / "raw-text.txt"
    raw_text_path.parent.mkdir(parents=True, exist_ok=True)
    raw_text_path.write_text(
        ("Consulta 11/02/2026: otitis externa.\nControl 18/02/2026: limpieza auricular.\n"),
        encoding="utf-8",
    )

    response = test_client.get(f"/documents/{document_id}/review/debug/visit-scoping")
    assert response.status_code == 200
    payload = response.json()
    assert payload["document_id"] == document_id
    assert payload["run_id"] == run_id
    assert payload["summary"] == {
        "total_visits": 3,
        "assigned_visits": 2,
        "anchored_visits": 2,
        "unassigned_field_count": 1,
        "raw_text_available": True,
    }
    assert len(payload["visits"]) == 2
    first_visit, second_visit = payload["visits"]
    assert first_visit["visit_index"] == 1
    assert first_visit["visit_id"] == "visit-1"
    assert first_visit["visit_date"] == "2026-02-11"
    assert first_visit["field_count"] >= 1
    assert first_visit["anchored_in_raw_text"] is True
    assert isinstance(first_visit["raw_context_chars"], int)
    assert first_visit["raw_context_chars"] > 0

    assert second_visit["visit_index"] == 2
    assert second_visit["visit_id"] == "visit-2"
    assert second_visit["visit_date"] == "2026-02-18"
    assert second_visit["field_count"] >= 1
    assert second_visit["anchored_in_raw_text"] is True
    assert isinstance(second_visit["raw_context_chars"], int)
    assert second_visit["raw_context_chars"] > 0


def test_document_review_visit_scoping_observability_handles_missing_raw_text(test_client):
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
            "fields": [],
            "visits": [
                {
                    "visit_id": "visit-1",
                    "visit_date": "2026-02-11",
                    "fields": [
                        {
                            "field_id": "f-diagnosis-1",
                            "key": "diagnosis",
                            "value": "Otitis",
                            "value_type": "string",
                        }
                    ],
                }
            ],
            "other_fields": [],
        },
    )

    response = test_client.get(f"/documents/{document_id}/review/debug/visit-scoping")
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"] == {
        "total_visits": 1,
        "assigned_visits": 1,
        "anchored_visits": 0,
        "unassigned_field_count": 0,
        "raw_text_available": False,
    }
    assert payload["visits"] == [
        {
            "visit_index": 1,
            "visit_id": "visit-1",
            "visit_date": "2026-02-11",
            "field_count": 1,
            "anchored_in_raw_text": False,
            "raw_context_chars": 0,
        }
    ]


def test_document_review_visit_scoping_observability_keeps_anchor_when_context_starts_with_sin(
    test_client,
):
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
            "fields": [],
            "visits": [
                {
                    "visit_id": "visit-1",
                    "visit_date": "2026-02-11",
                    "fields": [
                        {
                            "field_id": "f-diagnosis-1",
                            "key": "diagnosis",
                            "value": "Sin dolor",
                            "value_type": "string",
                        }
                    ],
                }
            ],
            "other_fields": [],
        },
    )

    raw_text_path = get_storage_root() / document_id / "runs" / run_id / "raw-text.txt"
    raw_text_path.parent.mkdir(parents=True, exist_ok=True)
    raw_text_path.write_text(
        "Consulta 11/02/2026: Sin dolor a la palpacion.\n",
        encoding="utf-8",
    )

    response = test_client.get(f"/documents/{document_id}/review/debug/visit-scoping")
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["assigned_visits"] == 1
    assert payload["summary"]["anchored_visits"] == 1
    assert len(payload["visits"]) == 1
    assert payload["visits"][0]["anchored_in_raw_text"] is True
    assert payload["visits"][0]["raw_context_chars"] > 0


def test_document_review_visit_scoping_observability_returns_404_for_missing_document(test_client):
    response = test_client.get(f"/documents/{uuid4()}/review/debug/visit-scoping")
    assert response.status_code == 404
    assert response.json() == {"error_code": "NOT_FOUND", "message": "Document not found."}


def test_document_review_visit_scoping_observability_returns_409_without_completed_run(test_client):
    document_id = _upload_sample_document(test_client)
    response = test_client.get(f"/documents/{document_id}/review/debug/visit-scoping")
    assert response.status_code == 409
    body = response.json()
    assert body["error_code"] == "CONFLICT"
    assert body["details"] == {"reason": "NO_COMPLETED_RUN"}
