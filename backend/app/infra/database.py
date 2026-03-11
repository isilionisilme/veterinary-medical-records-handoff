"""SQLite database connection utilities and schema initialization.

This module centralizes the SQLite file location, connection creation, and the
minimal schema used for the current release.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from backend.app.settings import get_settings

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = BASE_DIR / "data" / "documents.db"
_SCHEMA_TABLE_INFO_SQL = {
    "documents": "PRAGMA table_info(documents)",
    "document_status_history": "PRAGMA table_info(document_status_history)",
    "processing_runs": "PRAGMA table_info(processing_runs)",
    "artifacts": "PRAGMA table_info(artifacts)",
    "calibration_aggregates": "PRAGMA table_info(calibration_aggregates)",
}


def get_database_path() -> Path:
    """Resolve the SQLite database file path.

    The path can be overridden via the `VET_RECORDS_DB_PATH` environment
    variable. The parent directory is created if it does not exist.

    Returns:
        Path to the SQLite database file.

    Side Effects:
        Creates the parent directory for the database file when missing.
    """

    path = Path(get_settings().vet_records_db_path or str(DEFAULT_DB_PATH))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Yield a configured SQLite connection.

    The connection uses `sqlite3.Row` for row mapping and is always closed after
    the context exits.

    Yields:
        An open SQLite connection.
    """

    conn = sqlite3.connect(get_database_path(), detect_types=sqlite3.PARSE_DECLTYPES)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def ensure_schema() -> None:
    """Ensure required tables exist for the current application slice.

    Side Effects:
        Creates tables when they do not already exist.
    """

    with get_connection() as conn:
        _ensure_documents_schema(conn)
        _ensure_status_history_schema(conn)
        _ensure_processing_runs_schema(conn)
        _ensure_artifacts_schema(conn)
        _ensure_calibration_aggregates_schema(conn)
        conn.commit()


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    pragma_sql = _SCHEMA_TABLE_INFO_SQL.get(table)
    if pragma_sql is None:
        raise ValueError(f"Unsupported schema table for PRAGMA lookup: {table}")
    rows = conn.execute(pragma_sql).fetchall()
    return {row["name"] for row in rows}


def _ensure_documents_schema(conn: sqlite3.Connection) -> None:
    columns = _table_columns(conn, "documents")
    if not columns:
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
                review_status TEXT NOT NULL,
                reviewed_at TEXT,
                reviewed_by TEXT,
                reviewed_run_id TEXT
            );
            """
        )
        return

    if "reviewed_at" not in columns:
        conn.execute("ALTER TABLE documents ADD COLUMN reviewed_at TEXT;")
    if "reviewed_by" not in columns:
        conn.execute("ALTER TABLE documents ADD COLUMN reviewed_by TEXT;")
    if "reviewed_run_id" not in columns:
        conn.execute("ALTER TABLE documents ADD COLUMN reviewed_run_id TEXT;")

    if "original_filename" in columns and "storage_path" in columns:
        return

    conn.executescript(
        """
        CREATE TABLE documents_new (
            document_id TEXT PRIMARY KEY,
            original_filename TEXT NOT NULL,
            content_type TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            storage_path TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            review_status TEXT NOT NULL,
            reviewed_at TEXT,
            reviewed_by TEXT,
            reviewed_run_id TEXT
        );
        """
    )
    conn.execute(
        """
        INSERT INTO documents_new (
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
        SELECT
            document_id,
            filename,
            content_type,
            0,
            document_id || '/original.pdf',
            created_at,
            created_at,
            'IN_REVIEW',
            NULL,
            NULL,
            NULL
        FROM documents;
        """
    )
    conn.execute("DROP TABLE documents;")
    conn.execute("ALTER TABLE documents_new RENAME TO documents;")


def _ensure_status_history_schema(conn: sqlite3.Connection) -> None:
    columns = _table_columns(conn, "document_status_history")
    if not columns:
        conn.execute(
            """
            CREATE TABLE document_status_history (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                status TEXT NOT NULL,
                run_id TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(document_id) REFERENCES documents(document_id)
            );
            """
        )
    elif not {"id", "document_id", "status", "run_id", "created_at"}.issubset(columns):
        conn.executescript(
            """
            CREATE TABLE document_status_history_new (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                status TEXT NOT NULL,
                run_id TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(document_id) REFERENCES documents(document_id)
            );
            """
        )
        historical_rows = conn.execute(
            """
            SELECT document_id, state, created_at
            FROM document_status_history
            """
        ).fetchall()
        for row in historical_rows:
            conn.execute(
                """
                INSERT INTO document_status_history_new (
                    id, document_id, status, run_id, created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (str(uuid4()), row["document_id"], row["state"], None, row["created_at"]),
            )
        conn.execute("DROP TABLE document_status_history;")
        conn.execute("ALTER TABLE document_status_history_new RENAME TO document_status_history;")
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_document_status_history_document_id
        ON document_status_history (document_id);
        """
    )


def _ensure_processing_runs_schema(conn: sqlite3.Connection) -> None:
    columns = _table_columns(conn, "processing_runs")
    if not columns:
        conn.execute(
            """
            CREATE TABLE processing_runs (
                run_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                state TEXT NOT NULL,
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                failure_type TEXT,
                FOREIGN KEY(document_id) REFERENCES documents(document_id)
            );
            """
        )
    else:
        required_columns = {
            "run_id",
            "document_id",
            "state",
            "created_at",
            "started_at",
            "completed_at",
            "failure_type",
        }
        if not required_columns.issubset(columns):
            conn.executescript(
                """
                CREATE TABLE processing_runs_new (
                    run_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    failure_type TEXT,
                    FOREIGN KEY(document_id) REFERENCES documents(document_id)
                );
                """
            )
            conn.execute(
                """
                INSERT INTO processing_runs_new (
                    run_id,
                    document_id,
                    state,
                    created_at,
                    started_at,
                    completed_at,
                    failure_type
                )
                SELECT
                    run_id,
                    document_id,
                    state,
                    created_at,
                    started_at,
                    completed_at,
                    failure_type
                FROM processing_runs;
                """
            )
            conn.execute("DROP TABLE processing_runs;")
            conn.execute("ALTER TABLE processing_runs_new RENAME TO processing_runs;")
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_processing_runs_document_id
        ON processing_runs (document_id);
        """
    )


def _ensure_artifacts_schema(conn: sqlite3.Connection) -> None:
    columns = _table_columns(conn, "artifacts")
    if not columns:
        conn.execute(
            """
            CREATE TABLE artifacts (
                artifact_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                artifact_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(run_id) REFERENCES processing_runs(run_id)
            );
            """
        )
    else:
        required_columns = {"artifact_id", "run_id", "artifact_type", "payload", "created_at"}
        if not required_columns.issubset(columns):
            conn.executescript(
                """
                CREATE TABLE artifacts_new (
                    artifact_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    artifact_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(run_id) REFERENCES processing_runs(run_id)
                );
                """
            )
            conn.execute(
                """
                INSERT INTO artifacts_new (artifact_id, run_id, artifact_type, payload, created_at)
                SELECT artifact_id, run_id, artifact_type, payload, created_at
                FROM artifacts;
                """
            )
            conn.execute("DROP TABLE artifacts;")
            conn.execute("ALTER TABLE artifacts_new RENAME TO artifacts;")
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_artifacts_run_id
        ON artifacts (run_id);
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_artifacts_run_id_type
        ON artifacts (run_id, artifact_type);
        """
    )


def _ensure_calibration_aggregates_schema(conn: sqlite3.Connection) -> None:
    columns = _table_columns(conn, "calibration_aggregates")
    if not columns:
        conn.execute(
            """
            CREATE TABLE calibration_aggregates (
                context_key TEXT NOT NULL,
                field_key TEXT NOT NULL,
                mapping_id TEXT,
                mapping_id_scope_key TEXT NOT NULL,
                policy_version TEXT NOT NULL,
                accept_count INTEGER NOT NULL DEFAULT 0,
                edit_count INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (context_key, field_key, mapping_id_scope_key, policy_version)
            );
            """
        )
        conn.execute(
            """
            CREATE INDEX idx_calibration_aggregates_lookup
            ON calibration_aggregates (
                context_key,
                field_key,
                mapping_id_scope_key,
                policy_version
            );
            """
        )
        return

    required_columns = {
        "context_key",
        "field_key",
        "mapping_id",
        "mapping_id_scope_key",
        "policy_version",
        "accept_count",
        "edit_count",
        "updated_at",
    }
    if required_columns.issubset(columns):
        return

    conn.executescript(
        """
        CREATE TABLE calibration_aggregates_new (
            context_key TEXT NOT NULL,
            field_key TEXT NOT NULL,
            mapping_id TEXT,
            mapping_id_scope_key TEXT NOT NULL,
            policy_version TEXT NOT NULL,
            accept_count INTEGER NOT NULL DEFAULT 0,
            edit_count INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (context_key, field_key, mapping_id_scope_key, policy_version)
        );
        """
    )
    if columns:
        conn.execute(
            """
            INSERT INTO calibration_aggregates_new (
                context_key,
                field_key,
                mapping_id,
                mapping_id_scope_key,
                policy_version,
                accept_count,
                edit_count,
                updated_at
            )
            SELECT
                context_key,
                field_key,
                mapping_id,
                COALESCE(mapping_id_scope_key, '__null__'),
                policy_version,
                accept_count,
                edit_count,
                updated_at
            FROM calibration_aggregates;
            """
        )
    conn.execute("DROP TABLE calibration_aggregates;")
    conn.execute("ALTER TABLE calibration_aggregates_new RENAME TO calibration_aggregates;")
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_calibration_aggregates_lookup
        ON calibration_aggregates (context_key, field_key, mapping_id_scope_key, policy_version);
        """
    )
