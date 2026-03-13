from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

import pytest

from backend.app.domain.models import Document, ProcessingStatus, ReviewStatus
from backend.app.infra import database
from backend.app.infra.sqlite_document_repository import SqliteDocumentRepository


def _seed_document(repository: SqliteDocumentRepository) -> None:
    repository.create(
        Document(
            document_id="doc-1",
            original_filename="record.pdf",
            content_type="application/pdf",
            file_size=123,
            storage_path="storage/doc-1/original.pdf",
            created_at="2026-01-01T00:00:00+00:00",
            updated_at="2026-01-01T00:00:00+00:00",
            review_status=ReviewStatus.IN_REVIEW,
            reviewed_at=None,
            reviewed_by=None,
            reviewed_run_id=None,
        ),
        ProcessingStatus.UPLOADED,
    )


def test_concurrent_review_updates_remain_consistent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_path = tmp_path / "resilience.db"
    monkeypatch.setenv("VET_RECORDS_DB_PATH", str(db_path))
    database.ensure_schema()
    repository = SqliteDocumentRepository()
    _seed_document(repository)

    errors: list[Exception] = []
    barrier = threading.Barrier(2)

    def _worker(review_status: ReviewStatus, reviewed_by: str) -> None:
        try:
            barrier.wait(timeout=5)
            repository.update_review_status(
                document_id="doc-1",
                review_status=review_status.value,
                updated_at="2026-01-01T00:00:01+00:00",
                reviewed_at="2026-01-01T00:00:01+00:00"
                if review_status is ReviewStatus.REVIEWED
                else None,
                reviewed_by=reviewed_by if review_status is ReviewStatus.REVIEWED else None,
                reviewed_run_id="run-1" if review_status is ReviewStatus.REVIEWED else None,
            )
        except Exception as exc:  # pragma: no cover - assertion validates this never happens
            errors.append(exc)

    t1 = threading.Thread(target=_worker, args=(ReviewStatus.REVIEWED, "vet-a"))
    t2 = threading.Thread(target=_worker, args=(ReviewStatus.IN_REVIEW, "vet-b"))
    t1.start()
    t2.start()
    t1.join(timeout=5)
    t2.join(timeout=5)

    assert not t1.is_alive()
    assert not t2.is_alive()
    assert errors == []

    doc = repository.get("doc-1")
    assert doc is not None
    assert doc.review_status in {ReviewStatus.REVIEWED, ReviewStatus.IN_REVIEW}


def test_repository_surfaces_locked_database_error(monkeypatch: pytest.MonkeyPatch) -> None:
    repository = SqliteDocumentRepository()

    @contextmanager
    def _locked_connection():
        raise sqlite3.OperationalError("database is locked")
        yield  # pragma: no cover

    monkeypatch.setattr(database, "get_connection", _locked_connection)

    with pytest.raises(sqlite3.OperationalError, match="database is locked"):
        repository.count_documents()


def test_get_connection_fails_when_db_path_is_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_directory = tmp_path / "documents.db"
    db_directory.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("VET_RECORDS_DB_PATH", str(db_directory))

    with pytest.raises(sqlite3.OperationalError):
        with database.get_connection():
            pass


def test_ensure_schema_is_idempotent_on_existing_db(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_path = tmp_path / "idempotent.db"
    monkeypatch.setenv("VET_RECORDS_DB_PATH", str(db_path))

    database.ensure_schema()
    database.ensure_schema()

    with database.get_connection() as conn:
        tables = {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

    assert {
        "documents",
        "document_status_history",
        "processing_runs",
        "artifacts",
        "calibration_aggregates",
    }.issubset(tables)
