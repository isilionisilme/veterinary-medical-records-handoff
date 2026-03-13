from __future__ import annotations

from backend.app.application import field_normalizers

SPECIES_VALID_VECTORS: tuple[tuple[str, str], ...] = (
    ("canino", "canino"),
    ("canina", "canino"),
    ("perro", "canino"),
    ("perra", "canino"),
    ("felino", "felino"),
    ("felina", "felino"),
    ("gato", "felino"),
    ("gata", "felino"),
)
SPECIES_INVALID_VECTORS: tuple[str, ...] = ("equino", "lagarto")


def test_species_normalizer_returns_canonical_values_for_known_tokens() -> None:
    for raw_value, expected in SPECIES_VALID_VECTORS:
        normalized = field_normalizers.normalize_canonical_fields({"species": raw_value})
        assert normalized["species"] == expected


def test_species_normalizer_drops_unknown_tokens_instead_of_pass_through() -> None:
    for raw_value in SPECIES_INVALID_VECTORS:
        normalized = field_normalizers.normalize_canonical_fields({"species": raw_value})
        assert normalized["species"] is None


def test_species_contract_constants_match_current_canonical_set() -> None:
    assert field_normalizers.CANONICAL_SPECIES == frozenset({"canino", "felino"})
    for value in field_normalizers.SPECIES_TOKEN_TO_CANONICAL.values():
        assert value in field_normalizers.CANONICAL_SPECIES


def test_clinic_address_normalizer_expands_abbreviations_and_compacts_whitespace() -> None:
    normalized = field_normalizers.normalize_canonical_fields(
        {"clinic_address": "Dir.:  C/  Mayor  45 ,  46001   Valencia"}
    )

    assert normalized["clinic_address"] == "Calle Mayor 45, 46001 Valencia"


def test_clinic_address_normalizer_collapses_multiline_into_single_line() -> None:
    normalized = field_normalizers.normalize_canonical_fields(
        {"clinic_address": "Dirección:\nAvda. de la Ilustración 22, 1º B\n28029 Madrid"}
    )

    assert normalized["clinic_address"] == "Avenida de la Ilustración 22, 1º B 28029 Madrid"


def test_clinic_address_normalizer_returns_none_for_non_string_value() -> None:
    normalized = field_normalizers.normalize_canonical_fields({"clinic_address": None})

    assert normalized["clinic_address"] is None
