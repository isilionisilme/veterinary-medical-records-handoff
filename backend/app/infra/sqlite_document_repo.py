"""SQLite document aggregate repository."""

from __future__ import annotations

from uuid import uuid4

from backend.app.domain.models import (
    Document,
    DocumentWithLatestRun,
    ProcessingRunState,
    ProcessingRunSummary,
    ProcessingStatus,
    ReviewStatus,
)
from backend.app.infra import database


class SqliteDocumentRepo:
    """SQLite-backed repository for document CRUD and review metadata."""

    def create(self, document: Document, status: ProcessingStatus) -> None:
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
                    document.document_id,
                    document.original_filename,
                    document.content_type,
                    document.file_size,
                    document.storage_path,
                    document.created_at,
                    document.updated_at,
                    document.review_status.value,
                    document.reviewed_at,
                    document.reviewed_by,
                    document.reviewed_run_id,
                ),
            )
            conn.execute(
                """
                INSERT INTO document_status_history (id, document_id, status, run_id, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (str(uuid4()), document.document_id, status.value, None, document.created_at),
            )
            conn.commit()

    def get(self, document_id: str) -> Document | None:
        with database.get_connection() as conn:
            row = conn.execute(
                """
                SELECT
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
                FROM documents
                WHERE document_id = ?
                """,
                (document_id,),
            ).fetchone()

        if row is None:
            return None

        return Document(
            document_id=row["document_id"],
            original_filename=row["original_filename"],
            content_type=row["content_type"],
            file_size=row["file_size"],
            storage_path=row["storage_path"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            review_status=ReviewStatus(row["review_status"]),
            reviewed_at=row["reviewed_at"],
            reviewed_by=row["reviewed_by"],
            reviewed_run_id=row["reviewed_run_id"],
        )

    def list_documents(self, *, limit: int, offset: int) -> list[DocumentWithLatestRun]:
        with database.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    d.document_id,
                    d.original_filename,
                    d.content_type,
                    d.file_size,
                    d.storage_path,
                    d.created_at,
                    d.updated_at,
                    d.review_status,
                    d.reviewed_at,
                    d.reviewed_by,
                    d.reviewed_run_id,
                    r.run_id AS latest_run_id,
                    r.state AS latest_run_state,
                    r.failure_type AS latest_run_failure_type
                FROM documents d
                LEFT JOIN processing_runs r
                    ON r.run_id = (
                        SELECT pr.run_id
                        FROM processing_runs pr
                        WHERE pr.document_id = d.document_id
                        ORDER BY pr.created_at DESC
                        LIMIT 1
                    )
                ORDER BY d.created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            ).fetchall()

        results: list[DocumentWithLatestRun] = []
        for row in rows:
            document = Document(
                document_id=row["document_id"],
                original_filename=row["original_filename"],
                content_type=row["content_type"],
                file_size=row["file_size"],
                storage_path=row["storage_path"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                review_status=ReviewStatus(row["review_status"]),
                reviewed_at=row["reviewed_at"],
                reviewed_by=row["reviewed_by"],
                reviewed_run_id=row["reviewed_run_id"],
            )
            latest_run = None
            if row["latest_run_id"] is not None:
                latest_run = ProcessingRunSummary(
                    run_id=row["latest_run_id"],
                    state=ProcessingRunState(row["latest_run_state"]),
                    failure_type=row["latest_run_failure_type"],
                )
            results.append(DocumentWithLatestRun(document=document, latest_run=latest_run))
        return results

    def count_documents(self) -> int:
        with database.get_connection() as conn:
            row = conn.execute("SELECT COUNT(*) AS total FROM documents").fetchone()
        return int(row["total"]) if row else 0

    def update_review_status(
        self,
        *,
        document_id: str,
        review_status: str,
        updated_at: str,
        reviewed_at: str | None,
        reviewed_by: str | None,
        reviewed_run_id: str | None,
    ) -> Document | None:
        if review_status == ReviewStatus.REVIEWED.value:
            query = """
                UPDATE documents
                SET
                    review_status = ?,
                    updated_at = CASE
                        WHEN review_status = ? THEN updated_at
                        ELSE ?
                    END,
                    reviewed_at = CASE
                        WHEN review_status = ? THEN reviewed_at
                        ELSE ?
                    END,
                    reviewed_by = CASE
                        WHEN review_status = ? THEN reviewed_by
                        ELSE ?
                    END,
                    reviewed_run_id = CASE
                        WHEN review_status = ? THEN reviewed_run_id
                        ELSE ?
                    END
                WHERE document_id = ?
            """
            params = (
                review_status,
                ReviewStatus.REVIEWED.value,
                updated_at,
                ReviewStatus.REVIEWED.value,
                reviewed_at,
                ReviewStatus.REVIEWED.value,
                reviewed_by,
                ReviewStatus.REVIEWED.value,
                reviewed_run_id,
                document_id,
            )
        elif review_status == ReviewStatus.IN_REVIEW.value:
            query = """
                UPDATE documents
                SET
                    review_status = ?,
                    updated_at = CASE
                        WHEN review_status = ? THEN updated_at
                        ELSE ?
                    END,
                    reviewed_at = NULL,
                    reviewed_by = NULL,
                    reviewed_run_id = NULL
                WHERE document_id = ?
            """
            params = (
                review_status,
                ReviewStatus.IN_REVIEW.value,
                updated_at,
                document_id,
            )
        else:
            query = """
                UPDATE documents
                SET review_status = ?,
                    updated_at = ?,
                    reviewed_at = ?,
                    reviewed_by = ?,
                    reviewed_run_id = ?
                WHERE document_id = ?
            """
            params = (
                review_status,
                updated_at,
                reviewed_at,
                reviewed_by,
                reviewed_run_id,
                document_id,
            )

        with database.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()

        if cursor.rowcount != 1:
            return None
        return self.get(document_id)
