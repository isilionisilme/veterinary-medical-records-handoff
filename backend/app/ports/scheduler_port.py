"""Port for background processing scheduler execution."""

from __future__ import annotations

import asyncio
from typing import Protocol

from backend.app.ports.document_repository import DocumentRepository
from backend.app.ports.file_storage import FileStorage


class SchedulerPort(Protocol):
    """Callable contract for running the processing scheduler loop."""

    async def __call__(
        self,
        *,
        repository: DocumentRepository,
        storage: FileStorage,
        stop_event: asyncio.Event,
    ) -> None:
        """Run the scheduler loop until the stop event is set."""
