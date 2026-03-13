from __future__ import annotations

from backend.app.application import processing_runner


class _RepositoryStub:
    def __init__(self, interpretation_payload: dict[str, object] | None) -> None:
        self.interpretation_payload = interpretation_payload

    def get_latest_artifact_payload(
        self, *, run_id: str, artifact_type: str
    ) -> dict[str, object] | None:
        assert run_id == "run-123"
        assert artifact_type == "STRUCTURED_INTERPRETATION"
        return self.interpretation_payload


def test_persist_observability_snapshot_for_completed_run_persists_when_enabled(
    monkeypatch,
) -> None:
    repository = _RepositoryStub(
        {
            "data": {
                "global_schema": {"pet_name": "Luna"},
                "fields": [{"key": "pet_name", "value": "Luna", "confidence": 0.72}],
            }
        }
    )

    captured_snapshots: list[dict[str, object]] = []

    monkeypatch.setattr(
        "backend.app.application.processing.orchestrator.extraction_observability_enabled",
        lambda: True,
    )
    monkeypatch.setattr(
        "backend.app.application.processing.orchestrator.persist_extraction_run_snapshot",
        lambda snapshot: captured_snapshots.append(snapshot),
    )

    processing_runner._persist_observability_snapshot_for_completed_run(
        repository=repository,
        document_id="doc-123",
        run_id="run-123",
        created_at="2026-02-14T08:10:00Z",
    )

    assert len(captured_snapshots) == 1
    assert captured_snapshots[0]["documentId"] == "doc-123"
    assert captured_snapshots[0]["runId"] == "run-123"


def test_persist_observability_snapshot_for_completed_run_skips_when_disabled(
    monkeypatch,
) -> None:
    repository = _RepositoryStub(
        {
            "data": {
                "global_schema": {"pet_name": "Luna"},
                "fields": [{"key": "pet_name", "value": "Luna", "confidence": 0.72}],
            }
        }
    )

    captured_snapshots: list[dict[str, object]] = []

    monkeypatch.setattr(
        "backend.app.application.processing.orchestrator.extraction_observability_enabled",
        lambda: False,
    )
    monkeypatch.setattr(
        "backend.app.application.processing.orchestrator.persist_extraction_run_snapshot",
        lambda snapshot: captured_snapshots.append(snapshot),
    )

    processing_runner._persist_observability_snapshot_for_completed_run(
        repository=repository,
        document_id="doc-123",
        run_id="run-123",
        created_at="2026-02-14T08:10:00Z",
    )

    assert captured_snapshots == []
