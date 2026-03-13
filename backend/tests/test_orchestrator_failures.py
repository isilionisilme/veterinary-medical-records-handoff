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
        run_id="run-failure-1",
        document_id="doc-failure-1",
        state=ProcessingRunState.RUNNING,
        created_at="2026-01-01T00:00:00+00:00",
    )


def test_execute_run_handles_timeout_without_observability_persist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = Mock()
    storage = Mock()
    persist_spy = Mock()

    async def _raise_timeout(coro, *_args, **_kwargs):
        coro.close()
        raise TimeoutError

    monkeypatch.setattr(asyncio, "wait_for", _raise_timeout)
    monkeypatch.setattr(
        orchestrator, "_persist_observability_snapshot_for_completed_run", persist_spy
    )

    asyncio.run(orchestrator._execute_run(run=_build_run(), repository=repository, storage=storage))

    kwargs = repository.complete_run.call_args.kwargs
    assert kwargs["state"] is ProcessingRunState.TIMED_OUT
    assert kwargs["failure_type"] is None
    persist_spy.assert_not_called()


def test_execute_run_converts_unexpected_keyerror_to_failed_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = Mock()
    storage = Mock()

    async def _raise_keyerror(coro, *_args, **_kwargs):
        coro.close()
        raise KeyError("field_mapping")

    monkeypatch.setattr(asyncio, "wait_for", _raise_keyerror)

    asyncio.run(orchestrator._execute_run(run=_build_run(), repository=repository, storage=storage))

    kwargs = repository.complete_run.call_args.kwargs
    assert kwargs["state"] is ProcessingRunState.FAILED
    assert kwargs["failure_type"] == "INTERPRETATION_FAILED"


def test_process_document_preserves_extraction_artifact_when_interpretation_fails(
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
        lambda _path: ("texto clinico suficiente para pasar calidad", "fitz"),
    )
    monkeypatch.setattr(
        orchestrator,
        "evaluate_extracted_text_quality",
        lambda _text: (0.9, True, []),
    )
    monkeypatch.setattr(
        orchestrator,
        "_build_interpretation_artifact",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("mapping crashed")),
    )

    with pytest.raises(orchestrator.ProcessingError, match="INTERPRETATION_FAILED"):
        asyncio.run(
            orchestrator._process_document(
                run_id="run-failure-2",
                document_id="doc-failure-2",
                repository=repository,
                storage=storage,
            )
        )

    step_payloads = [
        call.kwargs["payload"]
        for call in repository.append_artifact.call_args_list
        if call.kwargs.get("artifact_type") == "STEP_STATUS"
    ]
    extraction_succeeded = [
        payload
        for payload in step_payloads
        if payload["step_name"] == "EXTRACTION" and payload["step_status"] == "SUCCEEDED"
    ]
    interpretation_failed = [
        payload
        for payload in step_payloads
        if payload["step_name"] == "INTERPRETATION" and payload["step_status"] == "FAILED"
    ]
    assert extraction_succeeded
    assert interpretation_failed
    assert interpretation_failed[0]["error_code"] == "INTERPRETATION_FAILED"


def test_process_document_empty_extraction_records_low_quality_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = Mock()
    storage = Mock()
    sample_pdf = Path(__file__)
    repository.get.return_value = SimpleNamespace(storage_path="doc/original.pdf")
    storage.exists.return_value = True
    storage.resolve.return_value = sample_pdf

    monkeypatch.setattr(
        orchestrator.pdf_extraction, "_extract_pdf_text_with_extractor", lambda _path: ("", "fitz")
    )

    with pytest.raises(orchestrator.ProcessingError, match="EXTRACTION_LOW_QUALITY"):
        asyncio.run(
            orchestrator._process_document(
                run_id="run-failure-3",
                document_id="doc-failure-3",
                repository=repository,
                storage=storage,
            )
        )

    failed_extraction = [
        call.kwargs["payload"]
        for call in repository.append_artifact.call_args_list
        if call.kwargs.get("artifact_type") == "STEP_STATUS"
        and call.kwargs["payload"]["step_name"] == "EXTRACTION"
        and call.kwargs["payload"]["step_status"] == "FAILED"
    ]
    assert failed_extraction
    assert failed_extraction[0]["error_code"] == "EXTRACTION_LOW_QUALITY"
