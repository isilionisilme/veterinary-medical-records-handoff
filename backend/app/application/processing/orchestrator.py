"""Processing subsystem modules extracted from processing_runner."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime

from backend.app.application.extraction_observability import (
    build_extraction_snapshot_from_interpretation,
    persist_extraction_run_snapshot,
)
from backend.app.application.extraction_quality import evaluate_extracted_text_quality
from backend.app.config import (
    extraction_observability_enabled,
)
from backend.app.domain.models import (
    ProcessingRun,
    ProcessingRunState,
    StepName,
    StepStatus,
)
from backend.app.ports.document_repository import DocumentRepository
from backend.app.ports.file_storage import FileStorage

from . import pdf_extraction
from .constants import PROCESSING_TIMEOUT_SECONDS
from .interpretation import _build_interpretation_artifact

logger = logging.getLogger(__name__)


def _default_now_iso() -> str:
    return datetime.now(UTC).isoformat()


class ProcessingError(Exception):
    """Processing failure with a failure_type mapping."""

    def __init__(self, failure_type: str) -> None:
        super().__init__(failure_type)
        self.failure_type = failure_type


class InterpretationBuildError(Exception):
    """Raised when interpretation cannot be built into the canonical schema shape."""

    def __init__(self, *, error_code: str, details: dict[str, object] | None = None) -> None:
        super().__init__(error_code)
        self.error_code = error_code
        self.details = details


async def _execute_run(
    *, run: ProcessingRun, repository: DocumentRepository, storage: FileStorage
) -> None:
    try:
        await asyncio.wait_for(
            _process_document(
                run_id=run.run_id,
                document_id=run.document_id,
                repository=repository,
                storage=storage,
            ),
            timeout=PROCESSING_TIMEOUT_SECONDS,
        )
    except TimeoutError:
        repository.complete_run(
            run_id=run.run_id,
            state=ProcessingRunState.TIMED_OUT,
            completed_at=_default_now_iso(),
            failure_type=None,
        )
        return
    except ProcessingError as exc:
        repository.complete_run(
            run_id=run.run_id,
            state=ProcessingRunState.FAILED,
            completed_at=_default_now_iso(),
            failure_type=exc.failure_type,
        )
        return
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Processing run failed: %s", exc)
        repository.complete_run(
            run_id=run.run_id,
            state=ProcessingRunState.FAILED,
            completed_at=_default_now_iso(),
            failure_type="INTERPRETATION_FAILED",
        )
        return

    completed_at = _default_now_iso()
    repository.complete_run(
        run_id=run.run_id,
        state=ProcessingRunState.COMPLETED,
        completed_at=completed_at,
        failure_type=None,
    )
    _persist_observability_snapshot_for_completed_run(
        repository=repository,
        document_id=run.document_id,
        run_id=run.run_id,
        created_at=completed_at,
    )


def _persist_observability_snapshot_for_completed_run(
    *,
    repository: DocumentRepository,
    document_id: str,
    run_id: str,
    created_at: str,
) -> None:
    if not extraction_observability_enabled():
        return

    interpretation_payload = repository.get_latest_artifact_payload(
        run_id=run_id,
        artifact_type="STRUCTURED_INTERPRETATION",
    )
    if not isinstance(interpretation_payload, dict):
        return

    snapshot = build_extraction_snapshot_from_interpretation(
        document_id=document_id,
        run_id=run_id,
        created_at=created_at,
        interpretation_payload=interpretation_payload,
    )
    if not isinstance(snapshot, dict):
        return

    try:
        persist_extraction_run_snapshot(snapshot)
    except Exception:  # pragma: no cover - defensive
        logger.exception(
            "Failed to persist extraction observability snapshot for completed run",
            extra={"document_id": document_id, "run_id": run_id},
        )


async def _process_document(
    *,
    run_id: str,
    document_id: str,
    repository: DocumentRepository,
    storage: FileStorage,
) -> None:
    extraction_started_at = _default_now_iso()
    _append_step_status(
        repository=repository,
        run_id=run_id,
        step_name=StepName.EXTRACTION,
        step_status=StepStatus.RUNNING,
        attempt=1,
        started_at=extraction_started_at,
        ended_at=None,
        error_code=None,
    )

    document = repository.get(document_id)
    if document is None:
        _append_step_status(
            repository=repository,
            run_id=run_id,
            step_name=StepName.EXTRACTION,
            step_status=StepStatus.FAILED,
            attempt=1,
            started_at=extraction_started_at,
            ended_at=_default_now_iso(),
            error_code="EXTRACTION_FAILED",
        )
        raise ProcessingError("EXTRACTION_FAILED")
    if not storage.exists(storage_path=document.storage_path):
        _append_step_status(
            repository=repository,
            run_id=run_id,
            step_name=StepName.EXTRACTION,
            step_status=StepStatus.FAILED,
            attempt=1,
            started_at=extraction_started_at,
            ended_at=_default_now_iso(),
            error_code="EXTRACTION_FAILED",
        )
        raise ProcessingError("EXTRACTION_FAILED")

    file_path = storage.resolve(storage_path=document.storage_path)
    file_size = await asyncio.to_thread(lambda: file_path.stat().st_size)
    if file_size == 0:
        _append_step_status(
            repository=repository,
            run_id=run_id,
            step_name=StepName.EXTRACTION,
            step_status=StepStatus.FAILED,
            attempt=1,
            started_at=extraction_started_at,
            ended_at=_default_now_iso(),
            error_code="EXTRACTION_FAILED",
        )
        raise ProcessingError("EXTRACTION_FAILED")

    raw_text, extractor_used = await asyncio.to_thread(
        pdf_extraction._extract_pdf_text_with_extractor, file_path
    )
    quality_score, quality_pass, quality_reasons = evaluate_extracted_text_quality(raw_text)
    logger.info(
        (
            "PDF extraction finished run_id=%s document_id=%s extractor=%s chars=%d "
            "quality_score=%.3f quality_pass=%s quality_reasons=%s"
        ),
        run_id,
        document_id,
        extractor_used,
        len(raw_text),
        quality_score,
        quality_pass,
        quality_reasons,
    )
    if not quality_pass:
        _append_step_status(
            repository=repository,
            run_id=run_id,
            step_name=StepName.EXTRACTION,
            step_status=StepStatus.FAILED,
            attempt=1,
            started_at=extraction_started_at,
            ended_at=_default_now_iso(),
            error_code="EXTRACTION_LOW_QUALITY",
        )
        raise ProcessingError("EXTRACTION_LOW_QUALITY")

    try:
        storage.save_raw_text(document_id=document_id, run_id=run_id, text=raw_text)
    except Exception as exc:
        _append_step_status(
            repository=repository,
            run_id=run_id,
            step_name=StepName.EXTRACTION,
            step_status=StepStatus.FAILED,
            attempt=1,
            started_at=extraction_started_at,
            ended_at=_default_now_iso(),
            error_code="EXTRACTION_FAILED",
        )
        raise ProcessingError("EXTRACTION_FAILED") from exc

    _append_step_status(
        repository=repository,
        run_id=run_id,
        step_name=StepName.EXTRACTION,
        step_status=StepStatus.SUCCEEDED,
        attempt=1,
        started_at=extraction_started_at,
        ended_at=_default_now_iso(),
        error_code=None,
    )

    interpretation_started_at = _default_now_iso()
    _append_step_status(
        repository=repository,
        run_id=run_id,
        step_name=StepName.INTERPRETATION,
        step_status=StepStatus.RUNNING,
        attempt=1,
        started_at=interpretation_started_at,
        ended_at=None,
        error_code=None,
    )
    try:
        interpretation_payload = _build_interpretation_artifact(
            document_id=document_id,
            run_id=run_id,
            raw_text=raw_text,
            repository=repository,
        )
        repository.append_artifact(
            run_id=run_id,
            artifact_type="STRUCTURED_INTERPRETATION",
            payload=interpretation_payload,
            created_at=_default_now_iso(),
        )
    except InterpretationBuildError as exc:
        _append_step_status(
            repository=repository,
            run_id=run_id,
            step_name=StepName.INTERPRETATION,
            step_status=StepStatus.FAILED,
            attempt=1,
            started_at=interpretation_started_at,
            ended_at=_default_now_iso(),
            error_code=exc.error_code,
            details=exc.details,
        )
        raise ProcessingError("INTERPRETATION_FAILED") from exc
    except Exception as exc:
        _append_step_status(
            repository=repository,
            run_id=run_id,
            step_name=StepName.INTERPRETATION,
            step_status=StepStatus.FAILED,
            attempt=1,
            started_at=interpretation_started_at,
            ended_at=_default_now_iso(),
            error_code="INTERPRETATION_FAILED",
            details=None,
        )
        raise ProcessingError("INTERPRETATION_FAILED") from exc

    await asyncio.sleep(0.05)
    _append_step_status(
        repository=repository,
        run_id=run_id,
        step_name=StepName.INTERPRETATION,
        step_status=StepStatus.SUCCEEDED,
        attempt=1,
        started_at=interpretation_started_at,
        ended_at=_default_now_iso(),
        error_code=None,
    )


def _append_step_status(
    *,
    repository: DocumentRepository,
    run_id: str,
    step_name: StepName,
    step_status: StepStatus,
    attempt: int,
    started_at: str | None,
    ended_at: str | None,
    error_code: str | None,
    details: dict[str, object] | None = None,
) -> None:
    """Persist an append-only STEP_STATUS artifact for a run."""

    repository.append_artifact(
        run_id=run_id,
        artifact_type="STEP_STATUS",
        payload={
            "step_name": step_name.value,
            "step_status": step_status.value,
            "attempt": attempt,
            "started_at": started_at,
            "ended_at": ended_at,
            "error_code": error_code,
            "details": details,
        },
        created_at=_default_now_iso(),
    )
