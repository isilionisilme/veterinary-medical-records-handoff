from __future__ import annotations

from pathlib import Path

from backend.app.application import document_service, documents
from backend.app.application.document_service import (
    _normalize_visit_date_candidate,
    _project_review_payload_to_canonical,
    get_document_original_location,
    get_document_status_details,
    mark_document_reviewed,
    register_document_upload,
    reopen_document_review,
)
from backend.app.domain.models import (
    Document,
    ProcessingRunDetails,
    ProcessingRunState,
    ProcessingRunSummary,
    ProcessingStatus,
    ReviewStatus,
)
from backend.app.ports.file_storage import StoredFile


def test_document_service_re_exports_stay_in_sync_with_documents_package() -> None:
    assert document_service.__all__ == documents.__all__
    for symbol in documents.__all__:
        assert getattr(document_service, symbol) is getattr(documents, symbol)


class FakeDocumentRepository:
    def __init__(self) -> None:
        self.created: list[tuple[Document, ProcessingStatus]] = []

    def create(self, document: Document, status: ProcessingStatus) -> None:
        self.created.append((document, status))

    def get(self, document_id: str) -> Document | None:
        return None

    def get_latest_run(self, document_id: str) -> ProcessingRunSummary | None:
        return None

    def get_latest_completed_run(self, document_id: str) -> ProcessingRunDetails | None:
        return None

    def get_latest_artifact_payload(
        self, *, run_id: str, artifact_type: str
    ) -> dict[str, object] | None:
        return None

    def append_artifact(
        self,
        *,
        run_id: str,
        artifact_type: str,
        payload: dict[str, object],
        created_at: str,
    ) -> None:
        return None

    def increment_calibration_signal(
        self,
        *,
        context_key: str,
        field_key: str,
        mapping_id: str | None,
        policy_version: str,
        signal_type: str,
        updated_at: str,
    ) -> None:
        return None

    def apply_calibration_deltas(
        self,
        *,
        context_key: str,
        field_key: str,
        mapping_id: str | None,
        policy_version: str,
        accept_delta: int,
        edit_delta: int,
        updated_at: str,
    ) -> None:
        return None

    def get_latest_applied_calibration_snapshot(
        self, *, document_id: str
    ) -> tuple[str, dict[str, object]] | None:
        return None


class FakeFileStorage:
    def save(self, *, document_id: str, content: bytes) -> StoredFile:
        return StoredFile(storage_path=f"{document_id}/original.pdf", file_size=len(content))

    def delete(self, *, storage_path: str) -> None:
        return None

    def resolve(self, *, storage_path: str) -> Path:
        return Path("/tmp") / storage_path

    def exists(self, *, storage_path: str) -> bool:
        return True

    def save_raw_text(self, *, document_id: str, run_id: str, text: str) -> StoredFile:
        return StoredFile(
            storage_path=f"{document_id}/runs/{run_id}/raw-text.txt",
            file_size=len(text),
        )

    def resolve_raw_text(self, *, document_id: str, run_id: str) -> Path:
        return Path("/tmp") / document_id / "runs" / run_id / "raw-text.txt"

    def exists_raw_text(self, *, document_id: str, run_id: str) -> bool:
        return False


def test_register_document_upload_persists_document_and_returns_response_fields() -> None:
    repository = FakeDocumentRepository()
    storage = FakeFileStorage()

    result = register_document_upload(
        filename="record.pdf",
        content_type="application/pdf",
        content=b"%PDF-1.5 sample",
        repository=repository,
        storage=storage,
        id_provider=lambda: "doc-123",
        now_provider=lambda: "2026-02-02T09:00:00+00:00",
    )

    assert result.document_id == "doc-123"
    assert result.status == ProcessingStatus.UPLOADED.value
    assert result.created_at == "2026-02-02T09:00:00+00:00"

    assert len(repository.created) == 1
    created, status = repository.created[0]
    assert created.document_id == "doc-123"
    assert created.original_filename == "record.pdf"
    assert created.content_type == "application/pdf"
    assert created.file_size == len(b"%PDF-1.5 sample")
    assert created.storage_path == "doc-123/original.pdf"
    assert created.created_at == "2026-02-02T09:00:00+00:00"
    assert created.updated_at == "2026-02-02T09:00:00+00:00"
    assert created.review_status == ReviewStatus.IN_REVIEW
    assert status == ProcessingStatus.UPLOADED


def test_register_document_upload_uses_provided_id_and_time_sources() -> None:
    repository = FakeDocumentRepository()
    storage = FakeFileStorage()

    result = register_document_upload(
        filename="x.pdf",
        content_type="application/pdf",
        content=b"data",
        repository=repository,
        storage=storage,
        id_provider=lambda: "fixed-id",
        now_provider=lambda: "fixed-time",
    )

    assert result.document_id == "fixed-id"
    created, _ = repository.created[0]
    assert created.created_at == "fixed-time"


def test_get_document_original_location_returns_none_when_missing() -> None:
    repository = FakeDocumentRepository()
    storage = FakeFileStorage()

    result = get_document_original_location(
        document_id="missing",
        repository=repository,
        storage=storage,
    )

    assert result is None


def test_get_document_original_location_resolves_path_and_existence() -> None:
    document = Document(
        document_id="doc-123",
        original_filename="record.pdf",
        content_type="application/pdf",
        file_size=10,
        storage_path="doc-123/original.pdf",
        created_at="2026-02-02T09:00:00+00:00",
        updated_at="2026-02-02T09:00:00+00:00",
        review_status=ReviewStatus.IN_REVIEW,
    )

    class StubRepository(FakeDocumentRepository):
        def get(self, document_id: str) -> Document | None:
            return document

    class StubStorage(FakeFileStorage):
        def exists(self, *, storage_path: str) -> bool:
            return False

    result = get_document_original_location(
        document_id="doc-123",
        repository=StubRepository(),
        storage=StubStorage(),
    )

    assert result is not None
    assert result.document.document_id == "doc-123"
    assert result.file_path == Path("/tmp/doc-123/original.pdf")
    assert result.exists is False


def test_get_document_status_details_does_not_re_evaluate_raw_text_quality() -> None:
    document = Document(
        document_id="doc-raw-text",
        original_filename="record.pdf",
        content_type="application/pdf",
        file_size=10,
        storage_path="doc-raw-text/original.pdf",
        created_at="2026-02-02T09:00:00+00:00",
        updated_at="2026-02-02T09:00:00+00:00",
        review_status=ReviewStatus.IN_REVIEW,
    )
    latest_run = ProcessingRunSummary(
        run_id="run-123",
        state=ProcessingRunState.COMPLETED,
        failure_type=None,
    )

    class StubRepository(FakeDocumentRepository):
        def get(self, document_id: str) -> Document | None:
            return document

        def get_latest_run(self, document_id: str) -> ProcessingRunSummary | None:
            return latest_run

    result = get_document_status_details(
        document_id="doc-raw-text",
        repository=StubRepository(),
    )

    assert result is not None
    assert result.status_view.status == ProcessingStatus.COMPLETED
    assert result.status_view.failure_type is None


def test_get_document_status_details_keeps_completed_when_raw_text_is_usable() -> None:
    document = Document(
        document_id="doc-usable-text",
        original_filename="record.pdf",
        content_type="application/pdf",
        file_size=10,
        storage_path="doc-usable-text/original.pdf",
        created_at="2026-02-02T09:00:00+00:00",
        updated_at="2026-02-02T09:00:00+00:00",
        review_status=ReviewStatus.IN_REVIEW,
    )
    latest_run = ProcessingRunSummary(
        run_id="run-usable",
        state=ProcessingRunState.COMPLETED,
        failure_type=None,
    )

    class StubRepository(FakeDocumentRepository):
        def get(self, document_id: str) -> Document | None:
            return document

        def get_latest_run(self, document_id: str) -> ProcessingRunSummary | None:
            return latest_run

    result = get_document_status_details(
        document_id="doc-usable-text",
        repository=StubRepository(),
    )

    assert result is not None
    assert result.status_view.status == ProcessingStatus.COMPLETED
    assert result.status_view.failure_type is None


def test_mark_document_reviewed_updates_review_metadata() -> None:
    document = Document(
        document_id="doc-review",
        original_filename="record.pdf",
        content_type="application/pdf",
        file_size=10,
        storage_path="doc-review/original.pdf",
        created_at="2026-02-02T09:00:00+00:00",
        updated_at="2026-02-02T09:00:00+00:00",
        review_status=ReviewStatus.IN_REVIEW,
    )

    class StubRepository(FakeDocumentRepository):
        def __init__(self) -> None:
            super().__init__()
            self.document = document

        def get(self, document_id: str) -> Document | None:
            return self.document if document_id == self.document.document_id else None

        def update_review_status(
            self,
            *,
            document_id: str,
            review_status: str,
            updated_at: str,
            reviewed_at: str | None,
            reviewed_by: str | None,
            reviewed_run_id: str | None,
        ) -> Document | None:
            if document_id != self.document.document_id:
                return None
            self.document = Document(
                document_id=self.document.document_id,
                original_filename=self.document.original_filename,
                content_type=self.document.content_type,
                file_size=self.document.file_size,
                storage_path=self.document.storage_path,
                created_at=self.document.created_at,
                updated_at=updated_at,
                review_status=ReviewStatus(review_status),
                reviewed_at=reviewed_at,
                reviewed_by=reviewed_by,
                reviewed_run_id=reviewed_run_id,
            )
            return self.document

    repository = StubRepository()
    result = mark_document_reviewed(
        document_id="doc-review",
        repository=repository,
        now_provider=lambda: "2026-02-03T10:00:00+00:00",
        reviewed_by="vet-1",
    )

    assert result is not None
    assert result.review_status == "REVIEWED"
    assert result.reviewed_at == "2026-02-03T10:00:00+00:00"
    assert result.reviewed_by == "vet-1"


def test_reopen_document_review_clears_review_metadata() -> None:
    document = Document(
        document_id="doc-review",
        original_filename="record.pdf",
        content_type="application/pdf",
        file_size=10,
        storage_path="doc-review/original.pdf",
        created_at="2026-02-02T09:00:00+00:00",
        updated_at="2026-02-02T09:00:00+00:00",
        review_status=ReviewStatus.REVIEWED,
        reviewed_at="2026-02-03T10:00:00+00:00",
        reviewed_by="vet-1",
    )

    class StubRepository(FakeDocumentRepository):
        def __init__(self) -> None:
            super().__init__()
            self.document = document

        def get(self, document_id: str) -> Document | None:
            return self.document if document_id == self.document.document_id else None

        def update_review_status(
            self,
            *,
            document_id: str,
            review_status: str,
            updated_at: str,
            reviewed_at: str | None,
            reviewed_by: str | None,
            reviewed_run_id: str | None,
        ) -> Document | None:
            if document_id != self.document.document_id:
                return None
            self.document = Document(
                document_id=self.document.document_id,
                original_filename=self.document.original_filename,
                content_type=self.document.content_type,
                file_size=self.document.file_size,
                storage_path=self.document.storage_path,
                created_at=self.document.created_at,
                updated_at=updated_at,
                review_status=ReviewStatus(review_status),
                reviewed_at=reviewed_at,
                reviewed_by=reviewed_by,
                reviewed_run_id=reviewed_run_id,
            )
            return self.document

    repository = StubRepository()
    result = reopen_document_review(
        document_id="doc-review",
        repository=repository,
        now_provider=lambda: "2026-02-04T10:00:00+00:00",
    )

    assert result is not None
    assert result.review_status == "IN_REVIEW"
    assert result.reviewed_at is None
    assert result.reviewed_by is None


def test_normalize_visit_date_candidate_is_type_safe() -> None:
    assert _normalize_visit_date_candidate(None) is None
    assert _normalize_visit_date_candidate(123) is None
    assert _normalize_visit_date_candidate({"value": "11/02/2026"}) is None


def test_normalize_visit_date_candidate_normalizes_ddmmyy_and_ddmmyyyy() -> None:
    assert _normalize_visit_date_candidate("11/02/2026") == "2026-02-11"
    assert _normalize_visit_date_candidate("11/02/26") == "2026-02-11"


def test_normalize_visit_date_candidate_rejects_two_digit_years_1969() -> None:
    assert _normalize_visit_date_candidate("11/02/69") is None


def test_normalize_visit_date_candidate_is_deterministic() -> None:
    raw = "Consulta realizada el 11/02/2026"
    first = _normalize_visit_date_candidate(raw)
    second = _normalize_visit_date_candidate(raw)
    assert first == "2026-02-11"
    assert second == first


def test_project_review_payload_projects_to_canonical_schema_contract() -> None:
    payload = {
        "schema_contract": "visit-grouped-canonical",
        "global_schema": {"pet_name": "Luna"},
        "fields": [],
    }

    projected = _project_review_payload_to_canonical(payload)

    assert projected["schema_contract"] == "visit-grouped-canonical"
    assert "schema_version" not in projected


def test_project_review_payload_merges_prepopulated_and_inferred_visits_deterministically() -> None:
    payload = {
        "fields": [
            {
                "field_id": "f-symptoms-canonical",
                "key": "symptoms",
                "value": "Otalgia",
                "value_type": "string",
                "scope": "document",
                "section": "visits",
                "classification": "medical_record",
                "origin": "machine",
                "evidence": {"page": 1, "snippet": "Consulta 11/02/2026: dolor de oido"},
            },
            {
                "field_id": "f-medication-v2",
                "key": "medication",
                "value": "Gotas oticas",
                "value_type": "string",
                "scope": "document",
                "section": "visits",
                "classification": "medical_record",
                "origin": "machine",
                "evidence": {"page": 1, "snippet": "Consulta 18/02/2026: indicar gotas"},
            },
        ],
        "visits": [
            {
                "visit_id": "visit-existing",
                "visit_date": "2026-02-18",
                "admission_date": None,
                "discharge_date": None,
                "reason_for_visit": "Control",
                "fields": [
                    {
                        "field_id": "vf-existing-lab",
                        "key": "lab_result",
                        "value": "Cultivo negativo",
                        "value_type": "string",
                        "scope": "visit",
                        "section": "visits",
                        "classification": "medical_record",
                        "origin": "machine",
                    }
                ],
            }
        ],
        "other_fields": [],
    }

    first = _project_review_payload_to_canonical(payload)
    second = _project_review_payload_to_canonical(payload)

    first_visits = [
        visit
        for visit in first["visits"]
        if isinstance(visit, dict) and visit.get("visit_id") != "unassigned"
    ]
    second_visits = [
        visit
        for visit in second["visits"]
        if isinstance(visit, dict) and visit.get("visit_id") != "unassigned"
    ]

    assert [visit.get("visit_date") for visit in first_visits] == ["2026-02-11", "2026-02-18"]
    assert first_visits == second_visits

    first_visit_keys = {
        field.get("key") for field in first_visits[0].get("fields", []) if isinstance(field, dict)
    }
    second_visit_keys = {
        field.get("key") for field in first_visits[1].get("fields", []) if isinstance(field, dict)
    }
    assert "symptoms" in first_visit_keys
    assert "medication" not in first_visit_keys
    assert "medication" in second_visit_keys
    assert "lab_result" in second_visit_keys


def test_project_review_payload_keeps_ambiguous_raw_text_field_unassigned() -> None:
    projected = _project_review_payload_to_canonical(
        {
            "fields": [
                {
                    "field_id": "f-symptoms-canonical",
                    "key": "symptoms",
                    "value": "Dolor",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {"page": 1, "snippet": "Consulta 11/02/2026: dolor de oido"},
                },
                {
                    "field_id": "f-medication-ambiguous-raw-text",
                    "key": "medication",
                    "value": "Gotas",
                    "value_type": "string",
                    "scope": "document",
                    "section": "visits",
                    "classification": "medical_record",
                    "origin": "machine",
                    "evidence": {
                        "page": 1,
                        "snippet": "Informe emitido 18/02/2026: medicacion indicada",
                    },
                },
            ],
            "visits": [],
            "other_fields": [],
        },
        raw_text=(
            "Consulta 11/02/2026: dolor de oido.\n"
            "Control 18/02/2026: ajustar medicacion.\n"
            "Informe emitido 18/02/2026: medicacion indicada.\n"
        ),
    )

    assigned = [
        visit
        for visit in projected["visits"]
        if isinstance(visit, dict) and visit.get("visit_id") != "unassigned"
    ]
    assert len(assigned) >= 2
    for visit in assigned:
        fields = visit.get("fields")
        if not isinstance(fields, list):
            continue
        assert all(
            not (
                isinstance(field, dict)
                and field.get("field_id") == "f-medication-ambiguous-raw-text"
            )
            for field in fields
        )

    unassigned = next(
        (
            visit
            for visit in projected["visits"]
            if isinstance(visit, dict) and visit.get("visit_id") == "unassigned"
        ),
        None,
    )
    assert isinstance(unassigned, dict)
    assert any(
        isinstance(field, dict) and field.get("field_id") == "f-medication-ambiguous-raw-text"
        for field in unassigned.get("fields", [])
    )


def test_project_review_payload_derives_latest_weight_from_raw_text() -> None:
    projected = _project_review_payload_to_canonical(
        {
            "fields": [],
            "visits": [],
            "other_fields": [],
        },
        raw_text=(
            "Consulta 11/02/2026 - 10:00\nPeso 7.0 kg\nConsulta 25/02/2026 - 12:00\nPeso 7.8 kg\n"
        ),
    )

    top_level_weight_fields = [
        field
        for field in projected["fields"]
        if isinstance(field, dict) and field.get("key") == "weight"
    ]
    assert len(top_level_weight_fields) == 1
    derived = top_level_weight_fields[0]
    assert derived["field_id"] == "derived-weight-current"
    assert derived["value"] == "7.8 kg"
    assert derived["origin"] == "derived"
