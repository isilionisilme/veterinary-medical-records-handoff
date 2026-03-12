"""Typed application settings loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _getenv(name: str) -> str | None:
    return os.environ.get(name)


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = BASE_DIR / "data" / "documents.db"
DEFAULT_STORAGE_PATH = BASE_DIR / "storage"


@dataclass(frozen=True)
class Settings:
    """Runtime configuration resolved from environment variables."""

    env: str | None
    app_env: str | None
    vet_records_env: str | None
    uvicorn_reload: str | None
    vet_records_cors_origins: str | None
    vet_records_db_path: str
    vet_records_storage_path: str
    vet_records_disable_processing: str | None
    vet_records_extraction_obs: str | None
    vet_records_confidence_policy_version: str | None
    vet_records_confidence_low_max: str | None
    vet_records_confidence_mid_max: str | None
    vet_records_human_edit_neutral_candidate_confidence: str | None
    vet_records_rate_limit_upload: str | None
    vet_records_rate_limit_download: str | None
    log_level: str
    pdf_extractor_force: str
    include_interpretation_candidates: bool
    auth_token: str | None
    app_version: str
    git_commit: str
    build_date: str

    def __post_init__(self) -> None:
        if not self.vet_records_db_path.strip():
            raise ValueError("VET_RECORDS_DB_PATH cannot be empty")
        if not self.vet_records_storage_path.strip():
            raise ValueError("VET_RECORDS_STORAGE_PATH cannot be empty")
        if not self.log_level.strip():
            object.__setattr__(self, "log_level", "INFO")
        else:
            object.__setattr__(self, "log_level", self.log_level.strip().upper())
        if not self.app_version.strip():
            object.__setattr__(self, "app_version", "dev")
        if not self.git_commit.strip():
            object.__setattr__(self, "git_commit", "unknown")
        if not self.build_date.strip():
            object.__setattr__(self, "build_date", "unknown")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached process-wide runtime settings."""

    return Settings(
        env=_getenv("ENV"),
        app_env=_getenv("APP_ENV"),
        vet_records_env=_getenv("VET_RECORDS_ENV"),
        uvicorn_reload=_getenv("UVICORN_RELOAD"),
        vet_records_cors_origins=_getenv("VET_RECORDS_CORS_ORIGINS"),
        vet_records_db_path=_getenv("VET_RECORDS_DB_PATH") or str(DEFAULT_DB_PATH),
        vet_records_storage_path=_getenv("VET_RECORDS_STORAGE_PATH") or str(DEFAULT_STORAGE_PATH),
        vet_records_disable_processing=_getenv("VET_RECORDS_DISABLE_PROCESSING"),
        vet_records_extraction_obs=_getenv("VET_RECORDS_EXTRACTION_OBS"),
        vet_records_confidence_policy_version=_getenv("VET_RECORDS_CONFIDENCE_POLICY_VERSION"),
        vet_records_confidence_low_max=_getenv("VET_RECORDS_CONFIDENCE_LOW_MAX"),
        vet_records_confidence_mid_max=_getenv("VET_RECORDS_CONFIDENCE_MID_MAX"),
        vet_records_human_edit_neutral_candidate_confidence=_getenv(
            "VET_RECORDS_HUMAN_EDIT_NEUTRAL_CANDIDATE_CONFIDENCE"
        ),
        vet_records_rate_limit_upload=_getenv("VET_RECORDS_RATE_LIMIT_UPLOAD"),
        vet_records_rate_limit_download=_getenv("VET_RECORDS_RATE_LIMIT_DOWNLOAD"),
        log_level=_getenv("LOG_LEVEL") or "INFO",
        pdf_extractor_force=(_getenv("PDF_EXTRACTOR_FORCE") or ""),
        include_interpretation_candidates=(
            (_getenv("VET_RECORDS_INCLUDE_INTERPRETATION_CANDIDATES") or "") != ""
        ),
        auth_token=_getenv("AUTH_TOKEN"),
        app_version=_getenv("APP_VERSION") or "dev",
        git_commit=_getenv("GIT_COMMIT") or "unknown",
        build_date=_getenv("BUILD_DATE") or "unknown",
    )


def clear_settings_cache() -> None:
    """Reset cached settings to re-read environment values."""

    get_settings.cache_clear()


def get_pdf_extractor_force() -> str:
    """Return runtime override for PDF extractor selection."""

    return (_getenv("PDF_EXTRACTOR_FORCE") or get_settings().pdf_extractor_force).strip()


def should_include_interpretation_candidates() -> bool:
    """Return runtime flag for including interpretation candidate debug payloads."""

    raw = _getenv("VET_RECORDS_INCLUDE_INTERPRETATION_CANDIDATES")
    if raw is None:
        return get_settings().include_interpretation_candidates
    return raw.strip().lower() in {"1", "true", "yes", "on"}
