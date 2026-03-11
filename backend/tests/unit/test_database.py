from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.app.infra import database


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    return conn


def _index_names(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'index'").fetchall()
    return {row["name"] for row in rows}


def test_table_columns_returns_existing_column_names() -> None:
    conn = _conn()
    conn.execute("CREATE TABLE documents (id TEXT PRIMARY KEY, name TEXT NOT NULL)")

    columns = database._table_columns(conn, "documents")

    assert columns == {"id", "name"}


def test_table_columns_rejects_non_allowlisted_table() -> None:
    conn = _conn()
    conn.execute("CREATE TABLE sample (id TEXT PRIMARY KEY, name TEXT NOT NULL)")

    with pytest.raises(ValueError, match="Unsupported schema table"):
        database._table_columns(conn, "sample")


def test_ensure_documents_schema_creates_table_from_scratch() -> None:
    conn = _conn()

    database._ensure_documents_schema(conn)

    columns = database._table_columns(conn, "documents")
    assert {
        "document_id",
        "original_filename",
        "content_type",
        "file_size",
        "storage_path",
        "created_at",
        "updated_at",
        "review_status",
        "reviewed_at",
        "reviewed_by",
        "reviewed_run_id",
    }.issubset(columns)


def test_get_database_path_uses_settings_and_creates_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "nested" / "db.sqlite3"
    monkeypatch.setattr(
        database, "get_settings", lambda: SimpleNamespace(vet_records_db_path=str(target))
    )

    resolved = database.get_database_path()

    assert resolved == target
    assert target.parent.exists()


def test_get_connection_sets_row_factory_and_pragmas(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_path = tmp_path / "connection.db"
    monkeypatch.setattr(database, "get_database_path", lambda: db_path)

    with database.get_connection() as conn:
        journal_mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        busy_timeout = conn.execute("PRAGMA busy_timeout;").fetchone()[0]
        assert conn.row_factory is sqlite3.Row
        assert str(journal_mode).lower() == "wal"
        assert busy_timeout == 5000


def test_ensure_schema_runs_all_schema_steps() -> None:
    conn = _conn()

    @contextmanager
    def _fake_connection():
        yield conn

    original_get_connection = database.get_connection
    database.get_connection = _fake_connection  # type: ignore[assignment]
    try:
        database.ensure_schema()
    finally:
        database.get_connection = original_get_connection  # type: ignore[assignment]

    expected_tables = {
        "documents",
        "document_status_history",
        "processing_runs",
        "artifacts",
        "calibration_aggregates",
    }
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    present = {row["name"] for row in rows}
    assert expected_tables.issubset(present)
    assert {
        "idx_document_status_history_document_id",
        "idx_processing_runs_document_id",
        "idx_artifacts_run_id",
        "idx_artifacts_run_id_type",
    }.issubset(_index_names(conn))
    conn.close()


def test_ensure_documents_schema_adds_missing_review_columns() -> None:
    conn = _conn()
    conn.execute(
        """
        CREATE TABLE documents (
            document_id TEXT PRIMARY KEY,
            original_filename TEXT NOT NULL,
            content_type TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            storage_path TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            review_status TEXT NOT NULL
        )
        """
    )

    database._ensure_documents_schema(conn)

    columns = database._table_columns(conn, "documents")
    assert {"reviewed_at", "reviewed_by", "reviewed_run_id"}.issubset(columns)


def test_ensure_documents_schema_migrates_legacy_filename_storage_shape() -> None:
    conn = _conn()
    conn.execute(
        """
        CREATE TABLE documents (
            document_id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            content_type TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        (
            "INSERT INTO documents "
            "(document_id, filename, content_type, created_at) "
            "VALUES (?, ?, ?, ?)"
        ),
        ("doc-1", "legacy.pdf", "application/pdf", "2026-01-01T00:00:00+00:00"),
    )

    database._ensure_documents_schema(conn)

    migrated = conn.execute(
        (
            "SELECT original_filename, file_size, storage_path, review_status "
            "FROM documents WHERE document_id = ?"
        ),
        ("doc-1",),
    ).fetchone()
    assert migrated is not None
    assert migrated["original_filename"] == "legacy.pdf"
    assert migrated["file_size"] == 0
    assert migrated["storage_path"] == "doc-1/original.pdf"
    assert migrated["review_status"] == "IN_REVIEW"


def test_status_history_schema_migrates_legacy_state_column() -> None:
    conn = _conn()
    conn.execute(
        """
        CREATE TABLE document_status_history (
            document_id TEXT NOT NULL,
            state TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "INSERT INTO document_status_history (document_id, state, created_at) VALUES (?, ?, ?)",
        ("doc-1", "UPLOADED", "2026-01-01T00:00:00+00:00"),
    )

    database._ensure_status_history_schema(conn)

    row = conn.execute(
        "SELECT id, document_id, status, run_id, created_at FROM document_status_history"
    ).fetchone()
    assert row is not None
    assert row["id"]
    assert row["document_id"] == "doc-1"
    assert row["status"] == "UPLOADED"
    assert row["run_id"] is None


def test_status_history_schema_creates_table_when_missing() -> None:
    conn = _conn()

    database._ensure_status_history_schema(conn)

    columns = database._table_columns(conn, "document_status_history")
    assert {"id", "document_id", "status", "run_id", "created_at"}.issubset(columns)
    assert "idx_document_status_history_document_id" in _index_names(conn)


def test_processing_runs_schema_migrates_when_required_columns_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    conn = _conn()
    conn.execute(
        """
        CREATE TABLE processing_runs (
            run_id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            state TEXT NOT NULL,
            created_at TEXT NOT NULL,
            started_at TEXT,
            completed_at TEXT,
            failure_type TEXT
        )
        """
    )
    conn.execute(
        """
        INSERT INTO processing_runs (
            run_id,
            document_id,
            state,
            created_at,
            started_at,
            completed_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            "run-1",
            "doc-1",
            "RUNNING",
            "2026-01-01T00:00:00+00:00",
            "2026-01-01T00:00:01+00:00",
            None,
        ),
    )

    original_table_columns = database._table_columns

    def _patched_table_columns(target_conn: sqlite3.Connection, table: str) -> set[str]:
        columns = original_table_columns(target_conn, table)
        if table == "processing_runs":
            return columns - {"failure_type"}
        return columns

    monkeypatch.setattr(database, "_table_columns", _patched_table_columns)

    database._ensure_processing_runs_schema(conn)

    columns = original_table_columns(conn, "processing_runs")
    assert "failure_type" in columns
    row = conn.execute(
        "SELECT run_id, document_id FROM processing_runs WHERE run_id = ?", ("run-1",)
    ).fetchone()
    assert row is not None


def test_processing_runs_schema_creates_table_when_missing() -> None:
    conn = _conn()

    database._ensure_processing_runs_schema(conn)

    columns = database._table_columns(conn, "processing_runs")
    assert {"run_id", "document_id", "state", "created_at", "failure_type"}.issubset(columns)
    assert "idx_processing_runs_document_id" in _index_names(conn)


def test_artifacts_schema_migrates_when_required_columns_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    conn = _conn()
    conn.execute(
        """
        CREATE TABLE artifacts (
            artifact_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            artifact_type TEXT NOT NULL,
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        (
            "INSERT INTO artifacts "
            "(artifact_id, run_id, artifact_type, payload, created_at) "
            "VALUES (?, ?, ?, ?, ?)"
        ),
        ("artifact-1", "run-1", "STEP_STATUS", "{}", "2026-01-01T00:00:00+00:00"),
    )

    original_table_columns = database._table_columns

    def _patched_table_columns(target_conn: sqlite3.Connection, table: str) -> set[str]:
        columns = original_table_columns(target_conn, table)
        if table == "artifacts":
            return columns - {"created_at"}
        return columns

    monkeypatch.setattr(database, "_table_columns", _patched_table_columns)

    database._ensure_artifacts_schema(conn)

    columns = original_table_columns(conn, "artifacts")
    assert "created_at" in columns
    rows = conn.execute("SELECT artifact_id FROM artifacts").fetchall()
    assert len(rows) == 1


def test_artifacts_schema_creates_table_when_missing() -> None:
    conn = _conn()

    database._ensure_artifacts_schema(conn)

    columns = database._table_columns(conn, "artifacts")
    assert {"artifact_id", "run_id", "artifact_type", "payload", "created_at"}.issubset(columns)
    assert {"idx_artifacts_run_id", "idx_artifacts_run_id_type"}.issubset(_index_names(conn))


def test_calibration_schema_migrates_and_normalizes_scope_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    conn = _conn()
    conn.execute(
        """
        CREATE TABLE calibration_aggregates (
            context_key TEXT NOT NULL,
            field_key TEXT NOT NULL,
            mapping_id TEXT,
            mapping_id_scope_key TEXT,
            policy_version TEXT NOT NULL,
            accept_count INTEGER NOT NULL DEFAULT 0,
            edit_count INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (context_key, field_key, policy_version)
        )
        """
    )
    conn.execute(
        """
        INSERT INTO calibration_aggregates (
            context_key,
            field_key,
            mapping_id,
            mapping_id_scope_key,
            policy_version,
            accept_count,
            edit_count,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("ctx", "diagnosis", None, None, "v1", 3, 1, "2026-01-01T00:00:00+00:00"),
    )

    original_table_columns = database._table_columns

    def _patched_table_columns(target_conn: sqlite3.Connection, table: str) -> set[str]:
        columns = original_table_columns(target_conn, table)
        if table == "calibration_aggregates":
            return columns - {"mapping_id_scope_key"}
        return columns

    monkeypatch.setattr(database, "_table_columns", _patched_table_columns)

    database._ensure_calibration_aggregates_schema(conn)

    columns = original_table_columns(conn, "calibration_aggregates")
    assert "mapping_id_scope_key" in columns
    row = conn.execute(
        "SELECT mapping_id_scope_key, accept_count, edit_count FROM calibration_aggregates"
    ).fetchone()
    assert row is not None
    assert row["mapping_id_scope_key"] == "__null__"
    assert row["accept_count"] == 3
    assert row["edit_count"] == 1


def test_calibration_schema_creates_table_and_index_when_missing() -> None:
    conn = _conn()

    database._ensure_calibration_aggregates_schema(conn)

    columns = database._table_columns(conn, "calibration_aggregates")
    assert {
        "context_key",
        "field_key",
        "mapping_id",
        "mapping_id_scope_key",
        "policy_version",
        "accept_count",
        "edit_count",
        "updated_at",
    }.issubset(columns)
    index_names = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'index'").fetchall()
    }
    assert "idx_calibration_aggregates_lookup" in index_names
