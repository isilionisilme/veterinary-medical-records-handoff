from __future__ import annotations

from pathlib import Path

import pytest

from backend.app.domain.models import Document, ProcessingRunState, ProcessingStatus, ReviewStatus
from backend.app.infra import database
from backend.app.infra.sqlite_document_repo import SqliteDocumentRepo
from backend.app.infra.sqlite_run_repo import SqliteRunRepo


def _seed_document(doc_repo: SqliteDocumentRepo) -> None:
    doc_repo.create(
        Document(
            document_id="doc-1",
            original_filename="record.pdf",
            content_type="application/pdf",
            file_size=100,
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


def test_sqlite_run_repo_constructs_and_handles_basic_run_flow(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_path = tmp_path / "run-repo.db"
    monkeypatch.setenv("VET_RECORDS_DB_PATH", str(db_path))
    database.ensure_schema()

    doc_repo = SqliteDocumentRepo()
    run_repo = SqliteRunRepo()
    _seed_document(doc_repo)

    run_repo.create_processing_run(
        run_id="run-1",
        document_id="doc-1",
        state=ProcessingRunState.QUEUED,
        created_at="2026-01-01T00:00:01+00:00",
    )
    queued = run_repo.list_queued_runs(limit=10)
    assert len(queued) == 1
    assert queued[0].run_id == "run-1"
