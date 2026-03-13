"""Application configuration helpers."""

from __future__ import annotations

import os
import sys

from backend.app.settings import clear_settings_cache, get_settings

DEFAULT_CONFIDENCE_POLICY_VERSION = "v1"
DEFAULT_CONFIDENCE_LOW_MAX = 0.50
DEFAULT_CONFIDENCE_MID_MAX = 0.75
DEFAULT_HUMAN_EDIT_NEUTRAL_CANDIDATE_CONFIDENCE = 0.50
CONFIDENCE_POLICY_VERSION_ENV = "VET_RECORDS_CONFIDENCE_POLICY_VERSION"
CONFIDENCE_LOW_MAX_ENV = "VET_RECORDS_CONFIDENCE_LOW_MAX"
CONFIDENCE_MID_MAX_ENV = "VET_RECORDS_CONFIDENCE_MID_MAX"
HUMAN_EDIT_NEUTRAL_CANDIDATE_CONFIDENCE_ENV = "VET_RECORDS_HUMAN_EDIT_NEUTRAL_CANDIDATE_CONFIDENCE"
RATE_LIMIT_UPLOAD_ENV = "VET_RECORDS_RATE_LIMIT_UPLOAD"
RATE_LIMIT_DOWNLOAD_ENV = "VET_RECORDS_RATE_LIMIT_DOWNLOAD"
DEFAULT_RATE_LIMIT_UPLOAD = "10/minute"
DEFAULT_RATE_LIMIT_DOWNLOAD = "30/minute"


def _current_settings():
    clear_settings_cache()
    return get_settings()


def _strip_or_none(raw: str | None) -> str | None:
    if raw is None:
        return None
    value = raw.strip()
    return value or None


def _parse_bounded_float(
    raw: str | None,
    *,
    default: float | None,
    min_value: float = 0.0,
    max_value: float = 1.0,
) -> float | None:
    normalized = _strip_or_none(raw)
    if normalized is None:
        return default
    try:
        value = float(normalized)
    except ValueError:
        return default
    if not (min_value <= value <= max_value):
        return default
    return value


def _parse_bounded_float_strict(
    raw: str | None,
    *,
    min_value: float = 0.0,
    max_value: float = 1.0,
) -> float | None:
    return _parse_bounded_float(
        raw,
        default=None,
        min_value=min_value,
        max_value=max_value,
    )


def _parse_band_cutoffs(
    *,
    low_raw: str | None,
    mid_raw: str | None,
    default_low: float | None,
    default_mid: float | None,
) -> tuple[float, float] | None:
    normalized_low = _strip_or_none(low_raw)
    normalized_mid = _strip_or_none(mid_raw)

    if normalized_low is None:
        low_max = default_low
    else:
        low_max = _parse_bounded_float_strict(normalized_low)

    if normalized_mid is None:
        mid_max = default_mid
    else:
        mid_max = _parse_bounded_float_strict(normalized_mid)

    if low_max is None or mid_max is None:
        if default_low is None or default_mid is None:
            return None
        return default_low, default_mid
    if low_max >= mid_max:
        if default_low is None or default_mid is None:
            return None
        return default_low, default_mid
    return low_max, mid_max


def _resolve_rate_limit(raw: str | None, *, default: str) -> str:
    configured = _strip_or_none(raw)
    if configured is not None:
        return configured
    if _is_pytest_runtime():
        return "10000/minute"
    return default


def processing_enabled() -> bool:
    """Return whether background processing is enabled."""

    raw = _current_settings().vet_records_disable_processing
    if raw is None:
        return True
    return raw.strip().lower() not in {"1", "true", "yes", "on"}


def extraction_observability_enabled() -> bool:
    """Return whether extraction observability debug endpoints are enabled."""

    raw = _current_settings().vet_records_extraction_obs
    if raw is None:
        return False
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def auth_token() -> str | None:
    """Return optional API bearer token; empty values disable auth boundary."""

    raw = _current_settings().auth_token
    if raw is None:
        return None
    token = raw.strip()
    return token or None


def _is_pytest_runtime() -> bool:
    return bool(os.environ.get("PYTEST_CURRENT_TEST")) or "pytest" in sys.modules


def rate_limit_upload() -> str:
    """Return upload endpoint rate limit string."""

    return _resolve_rate_limit(
        _current_settings().vet_records_rate_limit_upload,
        default=DEFAULT_RATE_LIMIT_UPLOAD,
    )


def rate_limit_download() -> str:
    """Return download endpoint rate limit string."""

    return _resolve_rate_limit(
        _current_settings().vet_records_rate_limit_download,
        default=DEFAULT_RATE_LIMIT_DOWNLOAD,
    )


def confidence_policy_version() -> str:
    """Return the active confidence policy version for review payloads."""

    settings = _current_settings()
    return confidence_policy_version_or_default(settings.vet_records_confidence_policy_version)


def confidence_policy_version_or_default(version_raw: str | None) -> str:
    return _strip_or_none(version_raw) or DEFAULT_CONFIDENCE_POLICY_VERSION


def confidence_band_cutoffs() -> tuple[float, float]:
    """Return (low_max, mid_max) confidence band cutoffs for veterinarian UI."""

    settings = get_settings()
    return confidence_band_cutoffs_from_values(
        low_raw=settings.vet_records_confidence_low_max,
        mid_raw=settings.vet_records_confidence_mid_max,
    )


def confidence_band_cutoffs_from_values(
    *, low_raw: str | None, mid_raw: str | None
) -> tuple[float, float]:
    """Return cutoffs from raw environment-like values."""

    parsed = _parse_band_cutoffs(
        low_raw=low_raw,
        mid_raw=mid_raw,
        default_low=DEFAULT_CONFIDENCE_LOW_MAX,
        default_mid=DEFAULT_CONFIDENCE_MID_MAX,
    )
    assert parsed is not None
    return parsed


def confidence_policy_version_or_none() -> str | None:
    """Return policy version when explicitly configured, else None."""

    return _strip_or_none(_current_settings().vet_records_confidence_policy_version)


def human_edit_neutral_candidate_confidence() -> float:
    """Return neutral candidate confidence baseline for human edits (0..1)."""

    return _parse_bounded_float(
        _current_settings().vet_records_human_edit_neutral_candidate_confidence,
        default=DEFAULT_HUMAN_EDIT_NEUTRAL_CANDIDATE_CONFIDENCE,
    )


def confidence_band_cutoffs_or_none() -> tuple[float, float] | None:
    """Return (low_max, mid_max) only when both values are configured and valid."""

    settings = _current_settings()
    return confidence_band_cutoffs_or_none_from_values(
        low_raw=settings.vet_records_confidence_low_max,
        mid_raw=settings.vet_records_confidence_mid_max,
    )


def confidence_band_cutoffs_or_none_from_values(
    *, low_raw: str | None, mid_raw: str | None
) -> tuple[float, float] | None:
    """Return cutoffs only when both values are provided and valid."""

    if _strip_or_none(low_raw) is None or _strip_or_none(mid_raw) is None:
        return None
    return _parse_band_cutoffs(
        low_raw=low_raw,
        mid_raw=mid_raw,
        default_low=None,
        default_mid=None,
    )


def confidence_policy_explicit_config_diagnostics() -> tuple[bool, str, list[str], list[str]]:
    """Return explicit confidence-policy config status for diagnostics and logs."""

    settings = _current_settings()
    return confidence_policy_explicit_config_diagnostics_from_values(
        version_raw=settings.vet_records_confidence_policy_version,
        low_raw=settings.vet_records_confidence_low_max,
        mid_raw=settings.vet_records_confidence_mid_max,
    )


def confidence_policy_explicit_config_diagnostics_from_values(
    *,
    version_raw: str | None,
    low_raw: str | None,
    mid_raw: str | None,
) -> tuple[bool, str, list[str], list[str]]:
    """Return confidence policy diagnostics from explicit values."""

    missing_keys: list[str] = []
    invalid_keys: list[str] = []

    if version_raw is None or not version_raw.strip():
        missing_keys.append(CONFIDENCE_POLICY_VERSION_ENV)
    if low_raw is None:
        missing_keys.append(CONFIDENCE_LOW_MAX_ENV)
    if mid_raw is None:
        missing_keys.append(CONFIDENCE_MID_MAX_ENV)

    low_value: float | None = None
    mid_value: float | None = None
    if low_raw is not None:
        try:
            low_value = float(low_raw)
        except ValueError:
            invalid_keys.append(CONFIDENCE_LOW_MAX_ENV)
    if mid_raw is not None:
        try:
            mid_value = float(mid_raw)
        except ValueError:
            invalid_keys.append(CONFIDENCE_MID_MAX_ENV)

    if low_value is not None and not (0 <= low_value <= 1):
        invalid_keys.append(CONFIDENCE_LOW_MAX_ENV)
    if mid_value is not None and not (0 <= mid_value <= 1):
        invalid_keys.append(CONFIDENCE_MID_MAX_ENV)
    if low_value is not None and mid_value is not None and low_value >= mid_value:
        invalid_keys.extend([CONFIDENCE_LOW_MAX_ENV, CONFIDENCE_MID_MAX_ENV])

    missing_keys = sorted(missing_keys)
    invalid_keys = sorted(set(invalid_keys))
    if missing_keys or invalid_keys:
        reason = "policy_invalid" if invalid_keys else "policy_not_configured"
        return False, reason, missing_keys, invalid_keys
    return True, "policy_configured", [], []
