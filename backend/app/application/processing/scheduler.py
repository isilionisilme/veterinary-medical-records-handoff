"""Processing subsystem modules extracted from processing_runner."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from backend.app.domain.models import (
    ProcessingRunState,
)
from backend.app.ports.document_repository import DocumentRepository
from backend.app.ports.file_storage import FileStorage

from .constants import MAX_RUNS_PER_TICK, PROCESSING_TICK_SECONDS
from .orchestrator import _execute_run

logger = logging.getLogger(__name__)


def _default_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _default_id() -> str:
    return str(uuid4())


@dataclass(frozen=True, slots=True)
class EnqueuedRun:
    run_id: str
    created_at: str
    state: ProcessingRunState


def enqueue_processing_run(
    *,
    document_id: str,
    repository: DocumentRepository,
    id_provider: callable = _default_id,
    now_provider: callable = _default_now_iso,
) -> EnqueuedRun:
    """Create a new queued processing run (append-only)."""

    run_id = id_provider()
    created_at = now_provider()
    repository.create_processing_run(
        run_id=run_id,
        document_id=document_id,
        state=ProcessingRunState.QUEUED,
        created_at=created_at,
    )
    return EnqueuedRun(run_id=run_id, created_at=created_at, state=ProcessingRunState.QUEUED)


async def processing_scheduler(
    *,
    repository: DocumentRepository,
    storage: FileStorage,
    stop_event: asyncio.Event,
    tick_seconds: float = PROCESSING_TICK_SECONDS,
) -> None:
    """Continuously start eligible queued runs and execute them."""

    while not stop_event.is_set():
        await _process_queued_runs(repository=repository, storage=storage)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=tick_seconds)
        except TimeoutError:
            continue


async def _process_queued_runs(*, repository: DocumentRepository, storage: FileStorage) -> None:
    queued_runs = repository.list_queued_runs(limit=MAX_RUNS_PER_TICK)
    for run in queued_runs:
        started = repository.try_start_run(
            run_id=run.run_id,
            document_id=run.document_id,
            started_at=_default_now_iso(),
        )
        if not started:
            continue
        await _execute_run(run=run, repository=repository, storage=storage)
