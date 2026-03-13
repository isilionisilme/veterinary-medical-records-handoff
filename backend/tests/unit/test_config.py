from __future__ import annotations

import pytest

from backend.app import config as app_config
from backend.app.settings import clear_settings_cache


@pytest.fixture(autouse=True)
def reset_settings_cache() -> None:
    clear_settings_cache()
    yield
    clear_settings_cache()


@pytest.mark.parametrize("raw", [None, "0", "false", "no", "off", ""])
def test_processing_enabled_true_by_default_or_falsey_env(monkeypatch, raw: str | None) -> None:
    if raw is None:
        monkeypatch.delenv("VET_RECORDS_DISABLE_PROCESSING", raising=False)
    else:
        monkeypatch.setenv("VET_RECORDS_DISABLE_PROCESSING", raw)
    assert app_config.processing_enabled() is True


@pytest.mark.parametrize("raw", ["1", "true", "yes", "on", " TRUE "])
def test_processing_enabled_false_when_disabled(monkeypatch, raw: str) -> None:
    monkeypatch.setenv("VET_RECORDS_DISABLE_PROCESSING", raw)
    assert app_config.processing_enabled() is False


@pytest.mark.parametrize("raw", [None, "0", "false", "no", "off", ""])
def test_extraction_observability_disabled_by_default(monkeypatch, raw: str | None) -> None:
    if raw is None:
        monkeypatch.delenv("VET_RECORDS_EXTRACTION_OBS", raising=False)
    else:
        monkeypatch.setenv("VET_RECORDS_EXTRACTION_OBS", raw)
    assert app_config.extraction_observability_enabled() is False


@pytest.mark.parametrize("raw", ["1", "true", "yes", "on", " TRUE "])
def test_extraction_observability_enabled(monkeypatch, raw: str) -> None:
    monkeypatch.setenv("VET_RECORDS_EXTRACTION_OBS", raw)
    assert app_config.extraction_observability_enabled() is True


def test_auth_token_trims_and_handles_empty(monkeypatch) -> None:
    monkeypatch.setenv("AUTH_TOKEN", "  token-123  ")
    assert app_config.auth_token() == "token-123"

    monkeypatch.setenv("AUTH_TOKEN", "   ")
    assert app_config.auth_token() is None

    monkeypatch.delenv("AUTH_TOKEN", raising=False)
    assert app_config.auth_token() is None


def test_confidence_policy_version_helpers() -> None:
    assert app_config.confidence_policy_version_or_default(None) == "v1"
    assert app_config.confidence_policy_version_or_default("  ") == "v1"
    assert app_config.confidence_policy_version_or_default("v2") == "v2"


def test_confidence_band_cutoffs_from_values() -> None:
    assert app_config.confidence_band_cutoffs_from_values(low_raw=None, mid_raw=None) == (0.5, 0.75)
    assert app_config.confidence_band_cutoffs_from_values(low_raw="0.2", mid_raw="0.9") == (
        0.2,
        0.9,
    )
    assert app_config.confidence_band_cutoffs_from_values(low_raw="bad", mid_raw="0.9") == (
        0.5,
        0.75,
    )
    assert app_config.confidence_band_cutoffs_from_values(low_raw="-1", mid_raw="0.9") == (
        0.5,
        0.75,
    )
    assert app_config.confidence_band_cutoffs_from_values(low_raw="0.8", mid_raw="0.8") == (
        0.5,
        0.75,
    )


def test_confidence_band_cutoffs_reads_env(monkeypatch) -> None:
    monkeypatch.setenv("VET_RECORDS_CONFIDENCE_LOW_MAX", "0.25")
    monkeypatch.setenv("VET_RECORDS_CONFIDENCE_MID_MAX", "0.85")
    assert app_config.confidence_band_cutoffs() == (0.25, 0.85)


def test_confidence_policy_version_or_none(monkeypatch) -> None:
    monkeypatch.setenv("VET_RECORDS_CONFIDENCE_POLICY_VERSION", "  v9  ")
    assert app_config.confidence_policy_version_or_none() == "v9"

    monkeypatch.setenv("VET_RECORDS_CONFIDENCE_POLICY_VERSION", "   ")
    assert app_config.confidence_policy_version_or_none() is None


def test_human_edit_neutral_candidate_confidence_branches(monkeypatch) -> None:
    monkeypatch.delenv("VET_RECORDS_HUMAN_EDIT_NEUTRAL_CANDIDATE_CONFIDENCE", raising=False)
    assert app_config.human_edit_neutral_candidate_confidence() == 0.5

    monkeypatch.setenv("VET_RECORDS_HUMAN_EDIT_NEUTRAL_CANDIDATE_CONFIDENCE", "0.35")
    assert app_config.human_edit_neutral_candidate_confidence() == 0.35

    monkeypatch.setenv("VET_RECORDS_HUMAN_EDIT_NEUTRAL_CANDIDATE_CONFIDENCE", "abc")
    assert app_config.human_edit_neutral_candidate_confidence() == 0.5

    monkeypatch.setenv("VET_RECORDS_HUMAN_EDIT_NEUTRAL_CANDIDATE_CONFIDENCE", "2")
    assert app_config.human_edit_neutral_candidate_confidence() == 0.5


def test_confidence_band_cutoffs_or_none_from_values() -> None:
    assert (
        app_config.confidence_band_cutoffs_or_none_from_values(low_raw=None, mid_raw="0.9") is None
    )
    assert (
        app_config.confidence_band_cutoffs_or_none_from_values(low_raw="0.2", mid_raw=None) is None
    )
    assert (
        app_config.confidence_band_cutoffs_or_none_from_values(low_raw="x", mid_raw="0.9") is None
    )
    assert (
        app_config.confidence_band_cutoffs_or_none_from_values(low_raw="0.2", mid_raw="2.0") is None
    )
    assert (
        app_config.confidence_band_cutoffs_or_none_from_values(low_raw="0.7", mid_raw="0.7") is None
    )
    assert app_config.confidence_band_cutoffs_or_none_from_values(low_raw="0.2", mid_raw="0.9") == (
        0.2,
        0.9,
    )


def test_confidence_band_cutoffs_or_none_reads_env(monkeypatch) -> None:
    monkeypatch.setenv("VET_RECORDS_CONFIDENCE_LOW_MAX", "0.21")
    monkeypatch.setenv("VET_RECORDS_CONFIDENCE_MID_MAX", "0.81")
    assert app_config.confidence_band_cutoffs_or_none() == (0.21, 0.81)


def test_confidence_policy_explicit_config_diagnostics_from_values() -> None:
    configured, reason, missing_keys, invalid_keys = (
        app_config.confidence_policy_explicit_config_diagnostics_from_values(
            version_raw=None,
            low_raw=None,
            mid_raw=None,
        )
    )
    assert configured is False
    assert reason == "policy_not_configured"
    assert app_config.CONFIDENCE_POLICY_VERSION_ENV in missing_keys
    assert app_config.CONFIDENCE_LOW_MAX_ENV in missing_keys
    assert app_config.CONFIDENCE_MID_MAX_ENV in missing_keys
    assert invalid_keys == []

    configured, reason, missing_keys, invalid_keys = (
        app_config.confidence_policy_explicit_config_diagnostics_from_values(
            version_raw="v2",
            low_raw="0.9",
            mid_raw="0.2",
        )
    )
    assert configured is False
    assert reason == "policy_invalid"
    assert missing_keys == []
    assert app_config.CONFIDENCE_LOW_MAX_ENV in invalid_keys
    assert app_config.CONFIDENCE_MID_MAX_ENV in invalid_keys

    configured, reason, missing_keys, invalid_keys = (
        app_config.confidence_policy_explicit_config_diagnostics_from_values(
            version_raw="v2",
            low_raw="0.2",
            mid_raw="0.8",
        )
    )
    assert configured is True
    assert reason == "policy_configured"
    assert missing_keys == []
    assert invalid_keys == []


def test_confidence_policy_explicit_config_diagnostics_reads_env(monkeypatch) -> None:
    monkeypatch.setenv("VET_RECORDS_CONFIDENCE_POLICY_VERSION", "v1")
    monkeypatch.setenv("VET_RECORDS_CONFIDENCE_LOW_MAX", "0.4")
    monkeypatch.setenv("VET_RECORDS_CONFIDENCE_MID_MAX", "0.7")
    assert app_config.confidence_policy_explicit_config_diagnostics() == (
        True,
        "policy_configured",
        [],
        [],
    )
