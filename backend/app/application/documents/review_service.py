"""Review lifecycle API: document review retrieval, mark/reopen.

Visit scoping and segment parsing responsibilities have been extracted to
``visit_scoping`` and ``segment_parser`` respectively (ARCH-01).
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from backend.app.application.documents import review_payload_projector
from backend.app.application.documents.calibration import (
    _apply_reviewed_document_calibration,
    _revert_reviewed_document_calibration,
)
from backend.app.application.documents.upload_service import _default_now_iso
from backend.app.domain.models import ReviewStatus
from backend.app.ports.document_repository import DocumentRepository
from backend.app.ports.file_storage import FileStorage

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class LatestCompletedRunReview:
    run_id: str
    state: str
    completed_at: str | None
    failure_type: str | None


@dataclass(frozen=True, slots=True)
class ActiveInterpretationReview:
    interpretation_id: str
    version_number: int
    data: dict[str, object]


@dataclass(frozen=True, slots=True)
class RawTextArtifactAvailability:
    run_id: str
    available: bool


@dataclass(frozen=True, slots=True)
class DocumentReview:
    document_id: str
    latest_completed_run: LatestCompletedRunReview
    active_interpretation: ActiveInterpretationReview
    raw_text_artifact: RawTextArtifactAvailability
    review_status: str
    reviewed_at: str | None
    reviewed_by: str | None


@dataclass(frozen=True, slots=True)
class DocumentReviewLookupResult:
    review: DocumentReview | None
    unavailable_reason: str | None


def get_document_review(
    *,
    document_id: str,
    repository: DocumentRepository,
    storage: FileStorage,
) -> DocumentReviewLookupResult | None:
    logger.info("get_document_review called document_id=%s", document_id)
    document = repository.get(document_id)
    if document is None:
        return None

    latest_completed_run = repository.get_latest_completed_run(document_id)
    if latest_completed_run is None:
        return DocumentReviewLookupResult(
            review=None,
            unavailable_reason="NO_COMPLETED_RUN",
        )

    interpretation_payload = repository.get_latest_artifact_payload(
        run_id=latest_completed_run.run_id,
        artifact_type="STRUCTURED_INTERPRETATION",
    )
    if interpretation_payload is None:
        return DocumentReviewLookupResult(
            review=None,
            unavailable_reason="INTERPRETATION_MISSING",
        )

    interpretation_id = str(interpretation_payload.get("interpretation_id", ""))
    version_number_raw = interpretation_payload.get("version_number", 1)
    version_number = version_number_raw if isinstance(version_number_raw, int) else 1

    structured_data = interpretation_payload.get("data")
    if not isinstance(structured_data, dict):
        structured_data = {}

    raw_text: str | None = None
    raw_text_path = storage.resolve_raw_text(
        document_id=latest_completed_run.document_id,
        run_id=latest_completed_run.run_id,
    )
    if raw_text_path.exists():
        try:
            raw_text = raw_text_path.read_text(encoding="utf-8")
        except OSError:
            logger.warning("Failed to read raw_text file path=%s", raw_text_path)
            raw_text = None

    structured_data = review_payload_projector._normalize_review_interpretation_data(
        structured_data,
        raw_text=raw_text,
    )

    return DocumentReviewLookupResult(
        review=DocumentReview(
            document_id=document_id,
            latest_completed_run=LatestCompletedRunReview(
                run_id=latest_completed_run.run_id,
                state=latest_completed_run.state.value,
                completed_at=latest_completed_run.completed_at,
                failure_type=latest_completed_run.failure_type,
            ),
            active_interpretation=ActiveInterpretationReview(
                interpretation_id=interpretation_id,
                version_number=version_number,
                data=structured_data,
            ),
            raw_text_artifact=RawTextArtifactAvailability(
                run_id=latest_completed_run.run_id,
                available=storage.exists_raw_text(
                    document_id=latest_completed_run.document_id,
                    run_id=latest_completed_run.run_id,
                ),
            ),
            review_status=document.review_status.value,
            reviewed_at=document.reviewed_at,
            reviewed_by=document.reviewed_by,
        ),
        unavailable_reason=None,
    )


@dataclass(frozen=True, slots=True)
class ReviewToggleResult:
    document_id: str
    review_status: str
    reviewed_at: str | None
    reviewed_by: str | None


def mark_document_reviewed(
    *,
    document_id: str,
    repository: DocumentRepository,
    now_provider: Callable[[], str] = _default_now_iso,
    reviewed_by: str | None = None,
) -> ReviewToggleResult | None:
    logger.info("mark_document_reviewed called document_id=%s", document_id)
    document = repository.get(document_id)
    if document is None:
        return None

    if document.review_status == ReviewStatus.REVIEWED:
        return ReviewToggleResult(
            document_id=document.document_id,
            review_status=document.review_status.value,
            reviewed_at=document.reviewed_at,
            reviewed_by=document.reviewed_by,
        )

    reviewed_at = now_provider()
    latest_completed_run = repository.get_latest_completed_run(document_id)
    reviewed_run_id = latest_completed_run.run_id if latest_completed_run is not None else None
    updated = repository.update_review_status(
        document_id=document_id,
        review_status=ReviewStatus.REVIEWED.value,
        updated_at=reviewed_at,
        reviewed_at=reviewed_at,
        reviewed_by=reviewed_by,
        reviewed_run_id=reviewed_run_id,
    )
    if updated is None:
        return None

    _apply_reviewed_document_calibration(
        document_id=document_id,
        reviewed_run_id=reviewed_run_id,
        repository=repository,
        created_at=reviewed_at,
    )

    return ReviewToggleResult(
        document_id=updated.document_id,
        review_status=updated.review_status.value,
        reviewed_at=updated.reviewed_at,
        reviewed_by=updated.reviewed_by,
    )


def reopen_document_review(
    *,
    document_id: str,
    repository: DocumentRepository,
    now_provider: Callable[[], str] = _default_now_iso,
) -> ReviewToggleResult | None:
    logger.info("reopen_document_review called document_id=%s", document_id)
    document = repository.get(document_id)
    if document is None:
        return None

    if document.review_status == ReviewStatus.IN_REVIEW:
        return ReviewToggleResult(
            document_id=document.document_id,
            review_status=document.review_status.value,
            reviewed_at=document.reviewed_at,
            reviewed_by=document.reviewed_by,
        )

    reopened_at = now_provider()
    updated = repository.update_review_status(
        document_id=document_id,
        review_status=ReviewStatus.IN_REVIEW.value,
        updated_at=reopened_at,
        reviewed_at=None,
        reviewed_by=None,
        reviewed_run_id=None,
    )
    if updated is None:
        return None

    _revert_reviewed_document_calibration(
        document_id=document_id,
        reviewed_run_id=document.reviewed_run_id,
        repository=repository,
        created_at=reopened_at,
    )

    return ReviewToggleResult(
        document_id=updated.document_id,
        review_status=updated.review_status.value,
        reviewed_at=updated.reviewed_at,
        reviewed_by=updated.reviewed_by,
    )
