from __future__ import annotations

from pathlib import Path

import pytest

from backend.app.domain.models import Document, ProcessingStatus, ReviewStatus
from backend.app.infra import database
from backend.app.infra.sqlite_document_repo import SqliteDocumentRepo


def test_sqlite_document_repo_constructs_and_persists_document(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_path = tmp_path / "document-repo.db"
    monkeypatch.setenv("VET_RECORDS_DB_PATH", str(db_path))
    database.ensure_schema()

    repo = SqliteDocumentRepo()
    repo.create(
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

    stored = repo.get("doc-1")
    assert stored is not None
    assert stored.original_filename == "record.pdf"
    assert repo.count_documents() == 1
