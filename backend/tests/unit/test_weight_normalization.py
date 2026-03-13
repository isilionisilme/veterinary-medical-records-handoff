"""Unit tests for weight normalization helpers."""

from __future__ import annotations

from backend.app.application.field_normalizers import _normalize_weight


def test_normalize_weight_with_comma_decimal() -> None:
    assert _normalize_weight("3,5 kg") == "3.5 kg"


def test_normalize_weight_with_dot_decimal() -> None:
    assert _normalize_weight("12.8 kg") == "12.8 kg"


def test_normalize_weight_with_kgs_suffix() -> None:
    assert _normalize_weight("25 kgs") == "25 kg"


def test_normalize_weight_without_unit_defaults_to_kg() -> None:
    assert _normalize_weight("7") == "7 kg"


def test_normalize_weight_converts_grams() -> None:
    assert _normalize_weight("500 g") == "0.5 kg"


def test_normalize_weight_keeps_small_valid_value() -> None:
    assert _normalize_weight("0.8 kg") == "0.8 kg"


def test_normalize_weight_trims_whitespace() -> None:
    assert _normalize_weight("  4.2  kg  ") == "4.2 kg"


def test_normalize_weight_converts_large_grams() -> None:
    assert _normalize_weight("3500 g") == "3.5 kg"


def test_normalize_weight_rejects_empty() -> None:
    assert _normalize_weight("") == ""


def test_normalize_weight_rejects_none() -> None:
    assert _normalize_weight(None) == ""


def test_normalize_weight_rejects_zero_kg() -> None:
    assert _normalize_weight("0 kg") == ""


def test_normalize_weight_rejects_zero_scalar() -> None:
    assert _normalize_weight("0.0") == ""


def test_normalize_weight_rejects_above_max_range() -> None:
    assert _normalize_weight("150 kg") == ""


def test_normalize_weight_rejects_below_min_range() -> None:
    assert _normalize_weight("0.1 kg") == ""


def test_normalize_weight_rejects_non_numeric() -> None:
    assert _normalize_weight("abc") == ""
