from __future__ import annotations

import asyncio
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from backend.app.application.processing import orchestrator
from backend.app.domain.models import ProcessingRun, ProcessingRunState


def _build_run() -> ProcessingRun:
    return ProcessingRun(
        run_id="run-1",
        document_id="doc-1",
        state=ProcessingRunState.RUNNING,
        created_at="2026-01-01T00:00:00+00:00",
    )


def test_execute_run_marks_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    repository = Mock()
    storage = Mock()

    async def _raise_timeout(coro, *_args, **_kwargs):
        coro.close()
        raise TimeoutError

    monkeypatch.setattr(asyncio, "wait_for", _raise_timeout)

    asyncio.run(orchestrator._execute_run(run=_build_run(), repository=repository, storage=storage))

    repository.complete_run.assert_called_once()
    kwargs = repository.complete_run.call_args.kwargs
    assert kwargs["state"] is ProcessingRunState.TIMED_OUT
    assert kwargs["failure_type"] is None


def test_execute_run_marks_failed_when_processing_error(monkeypatch: pytest.MonkeyPatch) -> None:
    repository = Mock()
    storage = Mock()

    async def _raise_processing_error(coro, *_args, **_kwargs):
        coro.close()
        raise orchestrator.ProcessingError("EXTRACTION_FAILED")

    monkeypatch.setattr(asyncio, "wait_for", _raise_processing_error)

    asyncio.run(orchestrator._execute_run(run=_build_run(), repository=repository, storage=storage))

    kwargs = repository.complete_run.call_args.kwargs
    assert kwargs["state"] is ProcessingRunState.FAILED
    assert kwargs["failure_type"] == "EXTRACTION_FAILED"


def test_execute_run_marks_failed_for_unexpected_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    repository = Mock()
    storage = Mock()

    async def _raise_unexpected(coro, *_args, **_kwargs):
        coro.close()
        raise RuntimeError("boom")

    monkeypatch.setattr(asyncio, "wait_for", _raise_unexpected)

    asyncio.run(orchestrator._execute_run(run=_build_run(), repository=repository, storage=storage))

    kwargs = repository.complete_run.call_args.kwargs
    assert kwargs["state"] is ProcessingRunState.FAILED
    assert kwargs["failure_type"] == "INTERPRETATION_FAILED"


def test_execute_run_completes_and_persists_observability(monkeypatch: pytest.MonkeyPatch) -> None:
    repository = Mock()
    storage = Mock()
    persist_spy = Mock()

    async def _wait_for_noop(coro, *_args, **_kwargs):
        coro.close()
        return None

    monkeypatch.setattr(asyncio, "wait_for", _wait_for_noop)
    monkeypatch.setattr(
        orchestrator, "_persist_observability_snapshot_for_completed_run", persist_spy
    )

    asyncio.run(orchestrator._execute_run(run=_build_run(), repository=repository, storage=storage))

    kwargs = repository.complete_run.call_args.kwargs
    assert kwargs["state"] is ProcessingRunState.COMPLETED
    assert kwargs["failure_type"] is None
    persist_spy.assert_called_once()


def test_process_document_fails_when_document_not_found() -> None:
    repository = Mock()
    storage = Mock()
    repository.get.return_value = None

    with pytest.raises(orchestrator.ProcessingError, match="EXTRACTION_FAILED"):
        asyncio.run(
            orchestrator._process_document(
                run_id="run-1",
                document_id="doc-1",
                repository=repository,
                storage=storage,
            )
        )

    step_status_calls = [
        call.kwargs["payload"]["step_status"]
        for call in repository.append_artifact.call_args_list
        if call.kwargs.get("artifact_type") == "STEP_STATUS"
    ]
    assert step_status_calls == ["RUNNING", "FAILED"]


def test_process_document_fails_when_storage_path_missing() -> None:
    repository = Mock()
    storage = Mock()
    repository.get.return_value = SimpleNamespace(storage_path="missing/path.pdf")
    storage.exists.return_value = False

    with pytest.raises(orchestrator.ProcessingError, match="EXTRACTION_FAILED"):
        asyncio.run(
            orchestrator._process_document(
                run_id="run-1",
                document_id="doc-1",
                repository=repository,
                storage=storage,
            )
        )


def test_process_document_fails_for_low_quality_extraction(monkeypatch: pytest.MonkeyPatch) -> None:
    repository = Mock()
    storage = Mock()
    sample_pdf = Path(__file__)
    repository.get.return_value = SimpleNamespace(storage_path="doc/original.pdf")
    storage.exists.return_value = True
    storage.resolve.return_value = sample_pdf

    monkeypatch.setattr(
        orchestrator.pdf_extraction,
        "_extract_pdf_text_with_extractor",
        lambda _path: ("texto ilegible", "fitz"),
    )
    monkeypatch.setattr(
        orchestrator,
        "evaluate_extracted_text_quality",
        lambda _text: (0.2, False, ["LOW_QUALITY"]),
    )

    with pytest.raises(orchestrator.ProcessingError, match="EXTRACTION_LOW_QUALITY"):
        asyncio.run(
            orchestrator._process_document(
                run_id="run-1",
                document_id="doc-1",
                repository=repository,
                storage=storage,
            )
        )


def test_process_document_marks_interpretation_failed_for_builder_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = Mock()
    storage = Mock()
    sample_pdf = Path(__file__)
    repository.get.return_value = SimpleNamespace(storage_path="doc/original.pdf")
    storage.exists.return_value = True
    storage.resolve.return_value = sample_pdf

    monkeypatch.setattr(
        orchestrator.pdf_extraction,
        "_extract_pdf_text_with_extractor",
        lambda _path: ("texto valido", "fitz"),
    )
    monkeypatch.setattr(
        orchestrator,
        "evaluate_extracted_text_quality",
        lambda _text: (0.9, True, []),
    )

    def _raise_build_error(*_args, **_kwargs):
        raise orchestrator.InterpretationBuildError(
            error_code="INTERPRETATION_SCHEMA_INVALID",
            details={"field": "visit_date"},
        )

    monkeypatch.setattr(orchestrator, "_build_interpretation_artifact", _raise_build_error)

    with pytest.raises(orchestrator.ProcessingError, match="INTERPRETATION_FAILED"):
        asyncio.run(
            orchestrator._process_document(
                run_id="run-1",
                document_id="doc-1",
                repository=repository,
                storage=storage,
            )
        )

    interpretation_fail_status = [
        call.kwargs["payload"]
        for call in repository.append_artifact.call_args_list
        if call.kwargs.get("artifact_type") == "STEP_STATUS"
        and call.kwargs["payload"]["step_name"] == "INTERPRETATION"
        and call.kwargs["payload"]["step_status"] == "FAILED"
    ]
    assert interpretation_fail_status
    assert interpretation_fail_status[0]["error_code"] == "INTERPRETATION_SCHEMA_INVALID"


def test_persist_observability_snapshot_skips_or_handles_invalid_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = Mock()
    repository.get_latest_artifact_payload.return_value = {"ok": True}

    monkeypatch.setattr(orchestrator, "extraction_observability_enabled", lambda: True)
    monkeypatch.setattr(
        orchestrator, "build_extraction_snapshot_from_interpretation", lambda **_k: None
    )
    persist_spy = Mock()
    monkeypatch.setattr(orchestrator, "persist_extraction_run_snapshot", persist_spy)

    orchestrator._persist_observability_snapshot_for_completed_run(
        repository=repository,
        document_id="doc-1",
        run_id="run-1",
        created_at="2026-01-01T00:00:00+00:00",
    )

    persist_spy.assert_not_called()
