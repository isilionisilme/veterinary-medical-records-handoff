"""Document-related API routes."""

from pathlib import Path
from typing import Annotated, Any, cast
from urllib.parse import quote

from fastapi import APIRouter, File, Query, Request, UploadFile, status
from fastapi import Path as ParamPath
from fastapi.responses import FileResponse, JSONResponse, Response

from backend.app.api.schemas import (
    DocumentListItemResponse,
    DocumentListResponse,
    DocumentResponse,
    DocumentUploadResponse,
    ErrorResponse,
    LatestRunResponse,
    ProcessingHistoryResponse,
    ProcessingHistoryRunResponse,
    ProcessingStepResponse,
)
from backend.app.application.document_service import (
    get_document_original_location,
    get_document_status_details,
    get_processing_history,
    list_documents,
    register_document_upload,
)
from backend.app.application.processing import enqueue_processing_run
from backend.app.config import processing_enabled, rate_limit_download, rate_limit_upload
from backend.app.domain.models import ProcessingStatus
from backend.app.infra.rate_limiter import limiter
from backend.app.ports.document_repository import DocumentRepository
from backend.app.ports.file_storage import FileStorage

from .routes_common import _request_content_length, error_response, log_event

router = APIRouter(tags=["Documents"])

# Normative default: 20 MB (see
# docs/projects/veterinary-medical-records/02-tech/technical-design.md Appendix B3.2).
MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20 MB
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
}
ALLOWED_EXTENSIONS = {".pdf"}
DEFAULT_LIST_LIMIT = 50
UUID_PATH_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
DocumentIdPath = Annotated[str, ParamPath(..., pattern=UUID_PATH_PATTERN)]


def _safe_content_disposition(disposition_type: str, filename: str) -> str:
    """Build a safe Content-Disposition value with RFC 5987 encoding."""

    normalized = filename.replace("\r", "").replace("\n", "")
    ascii_filename = normalized.encode("ascii", "replace").decode("ascii")
    ascii_filename = ascii_filename.replace('"', "'")
    encoded_filename = quote(normalized, safe="")
    return f"{disposition_type}; filename=\"{ascii_filename}\"; filename*=UTF-8''{encoded_filename}"


def _upload_rate_limit() -> str:
    return rate_limit_upload()


def _download_rate_limit() -> str:
    return rate_limit_download()


@router.get(
    "/documents",
    response_model=DocumentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List uploaded documents and their status",
    description="Return paginated documents with derived processing status.",
    responses={500: {"description": "Unexpected system failure."}},
)
def list_documents_route(
    request: Request,
    limit: int = Query(
        DEFAULT_LIST_LIMIT,
        ge=1,
        description="Maximum number of documents to return.",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Pagination offset.",
    ),
) -> DocumentListResponse | JSONResponse:
    """Return a paginated list of documents with derived status labels."""

    repository = cast(DocumentRepository, request.app.state.document_repository)
    try:
        result = list_documents(
            repository=repository,
            limit=limit,
            offset=offset,
        )
    except Exception as exc:  # pragma: no cover - defensive
        log_event(
            event_type="DOCUMENT_LIST_VIEW_FAILED",
            document_id=None,
            failure_reason=str(exc),
        )
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
            message="Unexpected error while listing documents.",
        )

    log_event(
        event_type="DOCUMENT_LIST_VIEWED",
        document_id=None,
        count_returned=len(result.items),
    )

    items = [
        DocumentListItemResponse(
            document_id=item.document_id,
            original_filename=item.original_filename,
            created_at=item.created_at,
            status=item.status,
            status_label=item.status_label,
            failure_type=item.failure_type,
            review_status=item.review_status,
            reviewed_at=item.reviewed_at,
            reviewed_by=item.reviewed_by,
        )
        for item in result.items
    ]
    return DocumentListResponse(
        items=items,
        limit=result.limit,
        offset=result.offset,
        total=result.total,
    )


@router.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document processing status",
    description="Return document metadata and its current processing state.",
    responses={404: {"description": "Document not found (NOT_FOUND)."}},
)
def get_document_status(
    request: Request, document_id: DocumentIdPath
) -> DocumentResponse | JSONResponse:
    """Return the document processing status for a given document id."""

    repository = cast(DocumentRepository, request.app.state.document_repository)
    details = get_document_status_details(
        document_id=document_id,
        repository=repository,
    )
    if details is None:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message="Document not found.",
        )

    latest_run = None
    if details.latest_run is not None:
        latest_run = LatestRunResponse(
            run_id=details.latest_run.run_id,
            state=details.latest_run.state.value,
            failure_type=details.latest_run.failure_type,
        )

    log_event(
        event_type="DOCUMENT_METADATA_VIEWED",
        document_id=details.document.document_id,
        run_id=details.latest_run.run_id if details.latest_run else None,
    )

    return DocumentResponse(
        document_id=details.document.document_id,
        original_filename=details.document.original_filename,
        content_type=details.document.content_type,
        file_size=details.document.file_size,
        created_at=details.document.created_at,
        updated_at=details.document.updated_at,
        status=details.status_view.status.value,
        status_message=details.status_view.status_message,
        failure_type=details.status_view.failure_type,
        review_status=details.document.review_status.value,
        reviewed_at=details.document.reviewed_at,
        reviewed_by=details.document.reviewed_by,
        latest_run=latest_run,
    )


@router.get(
    "/documents/{document_id}/processing-history",
    response_model=ProcessingHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get processing history for a document",
    description="Return chronological processing runs with step status artifacts.",
    responses={404: {"description": "Document not found (NOT_FOUND)."}},
)
def get_document_processing_history(
    request: Request, document_id: DocumentIdPath
) -> ProcessingHistoryResponse | JSONResponse:
    """Return read-only processing history for a document."""

    repository = cast(DocumentRepository, request.app.state.document_repository)
    result = get_processing_history(document_id=document_id, repository=repository)
    if result is None:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message="Document not found.",
        )

    log_event(
        event_type="DOCUMENT_PROCESSING_HISTORY_VIEWED",
        document_id=document_id,
    )
    return ProcessingHistoryResponse(
        document_id=result.document_id,
        runs=[
            ProcessingHistoryRunResponse(
                run_id=run.run_id,
                state=run.state,
                failure_type=run.failure_type,
                started_at=run.started_at,
                completed_at=run.completed_at,
                steps=[
                    ProcessingStepResponse(
                        step_name=step.step_name,
                        step_status=step.step_status,
                        attempt=step.attempt,
                        started_at=step.started_at,
                        ended_at=step.ended_at,
                        error_code=step.error_code,
                    )
                    for step in run.steps
                ],
            )
            for run in result.runs
        ],
    )


@router.get(
    "/documents/{document_id}/download",
    status_code=status.HTTP_200_OK,
    response_class=FileResponse,
    response_model=None,
    summary="Download or preview an original document",
    description="Return the original uploaded PDF for preview or download.",
    responses={
        404: {"description": "Document not found (NOT_FOUND)."},
        410: {"description": "Original file missing (ARTIFACT_MISSING)."},
        500: {"description": "Unexpected filesystem or I/O failure (INTERNAL_ERROR)."},
    },
)
@limiter.limit(_download_rate_limit)
def get_document_original(
    request: Request,
    document_id: DocumentIdPath,
    download: bool = Query(
        False,
        description="Return the document as an attachment when true; inline preview otherwise.",
    ),
) -> Response:
    """Return the original uploaded document file."""

    repository = cast(DocumentRepository, request.app.state.document_repository)
    storage = cast(FileStorage, request.app.state.file_storage)
    location = get_document_original_location(
        document_id=document_id,
        repository=repository,
        storage=storage,
    )
    if location is None:
        log_event(
            event_type="DOCUMENT_ORIGINAL_ACCESS_FAILED",
            document_id=document_id,
            failure_reason="Document metadata not found.",
        )
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message="Document not found.",
        )
    if not location.exists:
        log_event(
            event_type="DOCUMENT_ORIGINAL_ACCESS_FAILED",
            document_id=document_id,
            failure_reason="Original document file is missing.",
        )
        return error_response(
            status_code=status.HTTP_410_GONE,
            error_code="ARTIFACT_MISSING",
            message="Original document file is missing.",
        )

    disposition_type = "attachment" if download else "inline"
    log_event(
        event_type="DOCUMENT_ORIGINAL_ACCESSED",
        document_id=document_id,
        access_type="download" if download else "preview",
    )

    headers = {
        "Content-Disposition": _safe_content_disposition(
            disposition_type, location.document.original_filename
        )
    }
    try:
        return FileResponse(
            path=location.file_path,
            media_type="application/pdf",
            headers=headers,
        )
    except Exception as exc:  # pragma: no cover - defensive
        log_event(
            event_type="DOCUMENT_ORIGINAL_ACCESS_FAILED",
            document_id=document_id,
            failure_reason=str(exc),
        )
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
            message="Unexpected error while accessing the original document.",
        )


@router.post(
    "/documents/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a document upload",
    description=(
        "Validate an uploaded file and register its metadata. "
        "Release 1 stores the original PDF in filesystem storage."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request (INVALID_REQUEST)."},
        422: {"model": ErrorResponse, "description": "Validation error (UNPROCESSABLE_ENTITY)."},
        413: {"description": "Uploaded file exceeds the maximum allowed size (FILE_TOO_LARGE)."},
        415: {"description": "Unsupported upload type (UNSUPPORTED_MEDIA_TYPE)."},
        500: {"description": "Unexpected storage or database failure (INTERNAL_ERROR)."},
    },
)
@limiter.limit(_upload_rate_limit)
async def upload_document(
    request: Request,
    file: UploadFile = File(  # noqa: B008
        ...,
        description="Document file to register (validated for type/extension and size).",
    ),
) -> DocumentUploadResponse:
    """Register a document upload (Release 1: store original PDF + persist metadata)."""

    validation_error = _validate_upload(file)
    if validation_error is not None:
        log_event(
            event_type="DOCUMENT_UPLOADED",
            document_id=None,
            error_code=validation_error["error_code"],
            failure_reason=validation_error["message"],
        )
        return error_response(**validation_error)

    request_content_length = _request_content_length(request)
    if request_content_length is not None and request_content_length > MAX_UPLOAD_SIZE:
        log_event(
            event_type="DOCUMENT_UPLOADED",
            document_id=None,
            error_code="FILE_TOO_LARGE",
            failure_reason="Document exceeds the maximum allowed size.",
        )
        return error_response(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            error_code="FILE_TOO_LARGE",
            message="Document exceeds the maximum allowed size of 20 MB.",
        )

    max_chunk_size = 64 * 1024
    total_size = 0
    content_chunks: list[bytes] = []
    while True:
        chunk = await file.read(max_chunk_size)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > MAX_UPLOAD_SIZE:
            log_event(
                event_type="DOCUMENT_UPLOADED",
                document_id=None,
                error_code="FILE_TOO_LARGE",
                failure_reason="Document exceeds the maximum allowed size.",
            )
            return error_response(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                error_code="FILE_TOO_LARGE",
                message="Document exceeds the maximum allowed size of 20 MB.",
            )
        content_chunks.append(chunk)

    contents = b"".join(content_chunks)
    if len(contents) == 0:
        log_event(
            event_type="DOCUMENT_UPLOADED",
            document_id=None,
            error_code="INVALID_REQUEST",
            failure_reason="The uploaded file is empty.",
        )
        return error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_REQUEST",
            message="The uploaded file is empty.",
        )

    repository = cast(DocumentRepository, request.app.state.document_repository)
    storage = cast(FileStorage, request.app.state.file_storage)
    try:
        result = register_document_upload(
            filename=Path(file.filename).name,
            content_type=file.content_type or "",
            content=contents,
            repository=repository,
            storage=storage,
        )
        if processing_enabled():
            enqueue_processing_run(
                document_id=result.document_id,
                repository=repository,
            )
    except Exception as exc:  # pragma: no cover - defensive
        log_event(
            event_type="DOCUMENT_UPLOADED",
            document_id=None,
            error_code="INTERNAL_ERROR",
            failure_reason=str(exc),
        )
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
            message="Unexpected error while storing the document.",
        )

    log_event(
        event_type="DOCUMENT_UPLOADED",
        document_id=result.document_id,
    )
    status_value = (
        ProcessingStatus.PROCESSING.value
        if processing_enabled()
        else ProcessingStatus.UPLOADED.value
    )
    return DocumentUploadResponse(
        document_id=result.document_id,
        status=status_value,
        created_at=result.created_at,
    )


def _validate_upload(file: UploadFile) -> dict[str, Any] | None:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        return {
            "status_code": status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "error_code": "UNSUPPORTED_MEDIA_TYPE",
            "message": "Unsupported file type.",
        }

    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        return {
            "status_code": status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "error_code": "UNSUPPORTED_MEDIA_TYPE",
            "message": "Unsupported file extension.",
        }

    return None
