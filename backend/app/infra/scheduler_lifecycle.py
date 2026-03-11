"""Lifecycle wrapper for the background processing scheduler."""

from __future__ import annotations

import asyncio

from backend.app.ports.document_repository import DocumentRepository
from backend.app.ports.file_storage import FileStorage
from backend.app.ports.scheduler_port import SchedulerPort


class SchedulerLifecycle:
    """Manage scheduler task lifecycle independently from FastAPI wiring."""

    def __init__(self, *, scheduler_fn: SchedulerPort) -> None:
        self._scheduler_fn = scheduler_fn
        self._task: asyncio.Task[None] | None = None
        self._stop_event: asyncio.Event | None = None

    @property
    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def start(self, repository: DocumentRepository, storage: FileStorage) -> None:
        if self.is_running:
            return
        self._stop_event = asyncio.Event()
        self._task = asyncio.create_task(
            self._scheduler_fn(
                repository=repository,
                storage=storage,
                stop_event=self._stop_event,
            )
        )

    async def stop(self) -> None:
        if self._task is None or self._stop_event is None:
            self._task = None
            self._stop_event = None
            return

        self._stop_event.set()
        try:
            await self._task
        finally:
            self._task = None
            self._stop_event = None
