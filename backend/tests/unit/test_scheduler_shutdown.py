from __future__ import annotations

import asyncio
from unittest.mock import Mock

import pytest

from backend.app.infra.scheduler_lifecycle import SchedulerLifecycle


def test_scheduler_stop_uses_timeout_and_cancels_task(monkeypatch) -> None:
    started = asyncio.Event()
    cancelled = asyncio.Event()

    async def _stuck_scheduler(*, repository, storage, stop_event) -> None:
        _ = repository
        _ = storage
        _ = stop_event
        started.set()
        while True:
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                cancelled.set()
                raise

    lifecycle = SchedulerLifecycle(scheduler_fn=_stuck_scheduler)

    async def _exercise() -> None:
        await lifecycle.start(repository=Mock(), storage=Mock())
        await asyncio.wait_for(started.wait(), timeout=1.0)
        await lifecycle.stop()

    monkeypatch.setattr(
        "backend.app.infra.scheduler_lifecycle.SCHEDULER_STOP_TIMEOUT_SECONDS",
        0.01,
    )

    asyncio.run(_exercise())

    assert cancelled.is_set()
    assert not lifecycle.is_running


def test_scheduler_stop_logs_and_continues_when_task_ignores_cancellation(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    class NonCooperativeTask:
        def __init__(self) -> None:
            self.cancel_calls = 0

        def cancel(self) -> None:
            self.cancel_calls += 1

        def done(self) -> bool:
            return False

        def __await__(self):
            async def _never_finishes() -> None:
                await asyncio.sleep(3600)

            return _never_finishes().__await__()

    task = NonCooperativeTask()
    lifecycle = SchedulerLifecycle(scheduler_fn=Mock())
    lifecycle._task = task  # type: ignore[assignment]
    lifecycle._stop_event = asyncio.Event()
    wait_for_calls: list[float] = []

    async def _fake_wait_for(awaitable, timeout: float):
        _ = awaitable
        wait_for_calls.append(timeout)
        raise TimeoutError()

    monkeypatch.setattr("backend.app.infra.scheduler_lifecycle.asyncio.wait_for", _fake_wait_for)

    with caplog.at_level("ERROR"):
        asyncio.run(lifecycle.stop())

    assert task.cancel_calls == 1
    assert wait_for_calls == [15.0, 5.0]
    assert "did not cancel within 5.0s" in caplog.text
    assert not lifecycle.is_running
