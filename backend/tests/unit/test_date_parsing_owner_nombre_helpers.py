"""Unit tests for extracted helpers in date_parsing.py (Q-9)."""

from __future__ import annotations

import re

from backend.app.application.processing.date_parsing import (
    _extract_owner_nombre_from_match,
    _has_owner_nombre_context,
)

# Reuse the line pattern to build match objects for testing.
_OWNER_NOMBRE_LINE_PATTERN = re.compile(r"(?i)^\s*nombre\s*(?::|-)?\s*(.*)$")


def _match_for(line: str) -> re.Match[str]:
    m = _OWNER_NOMBRE_LINE_PATTERN.match(line)
    assert m is not None, f"Line did not match nombre pattern: {line!r}"
    return m


class TestHasOwnerNombreContext:
    """Tests for _has_owner_nombre_context."""

    def test_owner_context_present(self) -> None:
        raw_lines = ["Propietario:", "Nombre: Juan Garcia"]
        assert _has_owner_nombre_context(raw_lines, 1) is True

    def test_client_header_only(self) -> None:
        raw_lines = ["Datos del cliente", "Nombre: Maria Lopez"]
        assert _has_owner_nombre_context(raw_lines, 1) is True

    def test_vet_clinic_exclusion(self) -> None:
        raw_lines = ["Veterinario:", "Nombre: Dr. Perez"]
        assert _has_owner_nombre_context(raw_lines, 1) is False

    def test_patient_label_exclusion(self) -> None:
        raw_lines = ["Paciente:", "Nombre: Firulais"]
        assert _has_owner_nombre_context(raw_lines, 1) is False

    def test_no_context_returns_false(self) -> None:
        raw_lines = ["Algo irrelevante", "Nombre: Random"]
        assert _has_owner_nombre_context(raw_lines, 1) is False


class TestExtractOwnerNombreFromMatch:
    """Tests for _extract_owner_nombre_from_match."""

    def test_inline_candidate(self) -> None:
        line = "Nombre: Juan Carlos Garcia"
        result = _extract_owner_nombre_from_match(_match_for(line), [line], 0)
        assert result is not None
        assert "Juan" in result

    def test_forward_scan_tabular_candidate(self) -> None:
        lines = ["Nombre:", "Especie", "Maria Lopez Garcia"]
        result = _extract_owner_nombre_from_match(_match_for(lines[0]), lines, 0)
        assert result is not None
        assert "Maria" in result

    def test_address_splitting(self) -> None:
        line = "Nombre: Ana Torres Calle Mayor 5"
        result = _extract_owner_nombre_from_match(_match_for(line), [line], 0)
        assert result is not None
        assert "Calle" not in result

    def test_normalization_failure_returns_none(self) -> None:
        line = "Nombre: 12345"
        result = _extract_owner_nombre_from_match(_match_for(line), [line], 0)
        assert result is None
