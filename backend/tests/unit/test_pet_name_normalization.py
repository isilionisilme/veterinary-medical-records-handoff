"""Unit tests for pet_name normalization and candidate extraction guards."""

from __future__ import annotations

import pytest

from backend.app.application.field_normalizers import (
    _normalize_pet_name_value,
)

# ---------------------------------------------------------------------------
# _normalize_pet_name_value
# ---------------------------------------------------------------------------


class TestNormalizePetNameValue:
    """Normalization: strip noise, reject invalid, title-case."""

    def test_simple_name(self) -> None:
        assert _normalize_pet_name_value("Luna") == "Luna"

    def test_uppercase_name(self) -> None:
        assert _normalize_pet_name_value("LUNA") == "Luna"

    def test_lowercase_name(self) -> None:
        assert _normalize_pet_name_value("luna") == "Luna"

    def test_multi_word_name(self) -> None:
        assert _normalize_pet_name_value("Luna Bella") == "Luna Bella"

    def test_diacritics_preserved(self) -> None:
        assert _normalize_pet_name_value("Ñoño") == "Ñoño"

    def test_strips_trailing_birth_date(self) -> None:
        assert _normalize_pet_name_value("ALYA - Nacimiento: 05/07/2018") == "Alya"

    def test_strips_trailing_nac_variant(self) -> None:
        assert _normalize_pet_name_value("Rex - Nac. 2019") == "Rex"

    def test_strips_trailing_dob(self) -> None:
        assert _normalize_pet_name_value("Max - DOB 01/01/2020") == "Max"

    def test_rejects_numeric_only(self) -> None:
        assert _normalize_pet_name_value("12345") is None

    def test_rejects_empty_string(self) -> None:
        assert _normalize_pet_name_value("") is None

    def test_rejects_whitespace_only(self) -> None:
        assert _normalize_pet_name_value("   ") is None

    def test_rejects_none(self) -> None:
        assert _normalize_pet_name_value(None) is None

    def test_rejects_label_like_value(self) -> None:
        assert _normalize_pet_name_value("Especie: Canina") is None

    def test_rejects_raza_label(self) -> None:
        assert _normalize_pet_name_value("Raza: Mestiza") is None

    def test_rejects_chip_label(self) -> None:
        assert _normalize_pet_name_value("Chip: 941000024967769") is None

    def test_strips_label_echo(self) -> None:
        # If the regex captured "Paciente: Rex" as the full value
        assert _normalize_pet_name_value("Paciente: Rex") == "Rex"

    def test_strips_animal_label_echo(self) -> None:
        assert _normalize_pet_name_value("Animal: Kira") == "Kira"

    def test_strips_mascota_label_echo(self) -> None:
        assert _normalize_pet_name_value("Mascota: Nilo") == "Nilo"

    def test_roman_suffix_preserved(self) -> None:
        assert _normalize_pet_name_value("Rex III") == "Rex Iii"

    def test_extra_whitespace_collapsed(self) -> None:
        assert _normalize_pet_name_value("  Luna   Bella  ") == "Luna Bella"

    def test_non_string_input(self) -> None:
        assert _normalize_pet_name_value(42) is None


# ---------------------------------------------------------------------------
# Suspicious flag tests (triage)
# ---------------------------------------------------------------------------


class TestPetNameSuspiciousFlags:
    """triage._suspicious_accepted_flags for pet_name field."""

    @pytest.fixture(autouse=True)
    def _import_flags(self) -> None:
        from backend.app.application.extraction_observability.triage import (
            _suspicious_accepted_flags,
        )

        self._flags = _suspicious_accepted_flags

    def test_no_flags_for_clean_name(self) -> None:
        assert self._flags("pet_name", "Luna") == []

    def test_numeric_only(self) -> None:
        flags = self._flags("pet_name", "12345")
        assert "pet_name_numeric_only" in flags

    def test_too_short(self) -> None:
        flags = self._flags("pet_name", "A")
        assert "pet_name_too_short" in flags

    def test_contains_field_label(self) -> None:
        flags = self._flags("pet_name", "Especie Canina")
        assert "pet_name_contains_field_label" in flags

    def test_contains_embedded_date(self) -> None:
        flags = self._flags("pet_name", "Rex 05/07/2018")
        assert "pet_name_contains_embedded_date" in flags

    def test_is_stopword(self) -> None:
        flags = self._flags("pet_name", "Nombre")
        assert "pet_name_is_stopword" in flags

    def test_none_value_no_crash(self) -> None:
        assert self._flags("pet_name", None) == []

    def test_empty_value_no_crash(self) -> None:
        assert self._flags("pet_name", "") == []
