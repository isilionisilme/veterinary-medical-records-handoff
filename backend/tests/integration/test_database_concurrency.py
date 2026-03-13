from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

from backend.app.infra import database


def test_sqlite_connection_enforces_wal_and_busy_timeout(
    monkeypatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "documents.db"
    monkeypatch.setenv("VET_RECORDS_DB_PATH", str(db_path))

    database.ensure_schema()

    with database.get_connection() as conn:
        journal_mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        busy_timeout = conn.execute("PRAGMA busy_timeout;").fetchone()[0]

    assert str(journal_mode).lower() == "wal"
    assert int(busy_timeout) == 5000


def test_concurrent_read_during_write_does_not_raise_database_locked(
    monkeypatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "documents.db"
    monkeypatch.setenv("VET_RECORDS_DB_PATH", str(db_path))

    database.ensure_schema()

    with database.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO documents (
                document_id,
                original_filename,
                content_type,
                file_size,
                storage_path,
                created_at,
                updated_at,
                review_status,
                reviewed_at,
                reviewed_by,
                reviewed_run_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "doc-1",
                "record.pdf",
                "application/pdf",
                123,
                "storage/doc-1/original.pdf",
                "2026-02-25T00:00:00Z",
                "2026-02-25T00:00:00Z",
                "IN_REVIEW",
                None,
                None,
                None,
            ),
        )
        conn.commit()

    read_error: Exception | None = None
    read_result: int | None = None

    writer = sqlite3.connect(db_path)
    writer.row_factory = sqlite3.Row
    writer.execute("PRAGMA journal_mode=WAL;")
    writer.execute("PRAGMA busy_timeout=5000;")

    try:
        writer.execute("BEGIN IMMEDIATE;")
        writer.execute(
            "UPDATE documents SET updated_at = ? WHERE document_id = ?",
            ("2026-02-25T00:00:01Z", "doc-1"),
        )

        def _concurrent_reader() -> None:
            nonlocal read_error, read_result
            try:
                with database.get_connection() as conn:
                    row = conn.execute(
                        "SELECT COUNT(*) FROM documents WHERE document_id = ?",
                        ("doc-1",),
                    ).fetchone()
                    read_result = int(row[0]) if row is not None else None
            except Exception as exc:  # pragma: no cover - assertion validates no exception path
                read_error = exc

        thread = threading.Thread(target=_concurrent_reader)
        thread.start()
        thread.join(timeout=5)

        assert not thread.is_alive(), "Concurrent read thread did not finish in time."
        assert read_error is None
        assert read_result == 1
    finally:
        writer.rollback()
        writer.close()
