"""Unit tests for _validate_edit_preconditions in edit_service.py (Q-10)."""

from __future__ import annotations

from unittest.mock import MagicMock

from backend.app.application.documents.edit_service import (
    InterpretationEditOutcome,
    _EditPreconditionContext,
    _validate_edit_preconditions,
)
from backend.app.domain.models import ProcessingRun, ProcessingRunState


def _make_run(
    *,
    run_id: str = "run-1",
    document_id: str = "doc-1",
    state: ProcessingRunState = ProcessingRunState.COMPLETED,
) -> ProcessingRun:
    return ProcessingRun(
        run_id=run_id,
        document_id=document_id,
        state=state,
        created_at="2026-01-01T00:00:00Z",
    )


def _make_repo(
    *,
    run: ProcessingRun | None = None,
    processing_runs: list[ProcessingRun] | None = None,
    artifact_payload: dict[str, object] | None = None,
) -> MagicMock:
    repo = MagicMock()
    repo.get_run.return_value = run
    repo.list_processing_runs.return_value = processing_runs or ([] if run is None else [run])
    repo.get_latest_artifact_payload.return_value = artifact_payload
    return repo


class TestValidateEditPreconditions:
    """Tests for _validate_edit_preconditions."""

    def test_returns_none_when_run_not_found(self) -> None:
        repo = _make_repo(run=None)
        result = _validate_edit_preconditions(
            run_id="missing", base_version_number=1, repository=repo
        )
        assert result is None

    def test_blocked_by_active_run(self) -> None:
        run = _make_run()
        active_run = _make_run(run_id="run-active", state=ProcessingRunState.RUNNING)
        repo = _make_repo(run=run, processing_runs=[run, active_run])
        result = _validate_edit_preconditions(
            run_id="run-1", base_version_number=1, repository=repo
        )
        assert isinstance(result, InterpretationEditOutcome)
        assert result.conflict_reason == "REVIEW_BLOCKED_BY_ACTIVE_RUN"

    def test_not_completed_returns_conflict(self) -> None:
        run = _make_run(state=ProcessingRunState.FAILED)
        repo = _make_repo(run=run, processing_runs=[run])
        result = _validate_edit_preconditions(
            run_id="run-1", base_version_number=1, repository=repo
        )
        assert isinstance(result, InterpretationEditOutcome)
        assert result.conflict_reason == "INTERPRETATION_NOT_AVAILABLE"

    def test_missing_artifact_returns_conflict(self) -> None:
        run = _make_run()
        repo = _make_repo(run=run, artifact_payload=None)
        result = _validate_edit_preconditions(
            run_id="run-1", base_version_number=1, repository=repo
        )
        assert isinstance(result, InterpretationEditOutcome)
        assert result.conflict_reason == "INTERPRETATION_MISSING"

    def test_version_mismatch_returns_conflict(self) -> None:
        run = _make_run()
        payload = {"version_number": 3, "data": {"fields": []}}
        repo = _make_repo(run=run, artifact_payload=payload)
        result = _validate_edit_preconditions(
            run_id="run-1", base_version_number=1, repository=repo
        )
        assert isinstance(result, InterpretationEditOutcome)
        assert result.conflict_reason == "BASE_VERSION_MISMATCH"

    def test_happy_path_returns_context(self) -> None:
        run = _make_run()
        payload = {
            "version_number": 1,
            "data": {"fields": [{"key": "pet_name", "value": "Max", "context_key": "ctx-1"}]},
        }
        repo = _make_repo(run=run, artifact_payload=payload)
        result = _validate_edit_preconditions(
            run_id="run-1", base_version_number=1, repository=repo
        )
        assert isinstance(result, _EditPreconditionContext)
        assert result.run is run
        assert result.active_version_number == 1
        assert result.context_key == "ctx-1"
        assert len(result.active_fields) == 1
