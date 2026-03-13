from __future__ import annotations

import re
from collections.abc import Mapping

_WHITESPACE_PATTERN = re.compile(r"\s+")

CANONICAL_SPECIES: frozenset[str] = frozenset({"canino", "felino"})

SPECIES_TOKEN_TO_CANONICAL: dict[str, str] = {
    "canina": "canino",
    "canino": "canino",
    "perro": "canino",
    "perra": "canino",
    "felina": "felino",
    "felino": "felino",
    "gato": "felino",
    "gata": "felino",
}


def _normalize_species_value(value: object) -> str | None:
    cleaned = _normalize_scalar_with_labels(value, ("especie", "species"))
    if not cleaned:
        return None

    lower_cleaned = cleaned.casefold()
    for token, canonical in SPECIES_TOKEN_TO_CANONICAL.items():
        if re.search(rf"\b{re.escape(token)}\b", lower_cleaned):
            return canonical
    return None


def _pretty_breed_case(value: str) -> str:
    words = value.split(" ")
    return " ".join(word.capitalize() if word.islower() else word for word in words)


def _remove_species_tokens(value: str) -> str:
    cleaned = value
    for token in SPECIES_TOKEN_TO_CANONICAL:
        cleaned = re.sub(rf"(?i)\b{re.escape(token)}\b", " ", cleaned)
    cleaned = re.sub(r"[\-_/|]+", " ", cleaned)
    return _normalize_whitespace(cleaned)


def _normalize_species_and_breed_pair(
    values: dict[str, object],
    evidence_map: Mapping[str, list[dict[str, object]]] | None,
) -> dict[str, object]:
    """Normalize species/breed in *values* using tokens and evidence.

    Mutates *values* in-place (sets ``species`` and ``breed`` keys) **and**
    returns it for convenience chaining.
    """
    species = values.get("species") if isinstance(values.get("species"), str) else None
    breed = values.get("breed") if isinstance(values.get("breed"), str) else None

    combined_sources = [value for value in (species, breed) if isinstance(value, str)]
    combined_sources.extend(_species_breed_sources_from_evidence(evidence_map))
    for source in combined_sources:
        lower_source = source.casefold()
        matched_token = next(
            (
                token
                for token in SPECIES_TOKEN_TO_CANONICAL
                if re.search(rf"\b{re.escape(token)}\b", lower_source)
            ),
            None,
        )
        if matched_token is None:
            continue

        canonical_species = SPECIES_TOKEN_TO_CANONICAL[matched_token]
        if not species:
            species = canonical_species

        remainder = _remove_species_tokens(source)
        if remainder and (not breed or source == species):
            breed = remainder

    if isinstance(breed, str):
        cleaned_breed = _remove_species_tokens(
            _normalize_scalar_with_labels(breed, ("raza", "breed")) or ""
        )
        breed = _pretty_breed_case(cleaned_breed) if cleaned_breed else None

    values["species"] = species
    values["breed"] = breed
    return values


def _species_breed_sources_from_evidence(
    evidence_map: Mapping[str, list[dict[str, object]]] | None,
) -> list[str]:
    if evidence_map is None:
        return []

    sources: list[str] = []
    for key in ("species", "breed"):
        for item in evidence_map.get(key, []):
            if not isinstance(item, dict):
                continue
            evidence = item.get("evidence")
            if not isinstance(evidence, dict):
                continue
            snippet = evidence.get("snippet")
            if not isinstance(snippet, str):
                continue

            compact = _normalize_whitespace(snippet)
            direct_match = re.search(
                r"(?i)(?:especie\s*/\s*raza|raza\s*/\s*especie)\s*[:\-]\s*([^\n;]{2,120})",
                compact,
            )
            if direct_match:
                sources.append(_normalize_whitespace(direct_match.group(1)))
                continue
            sources.append(compact)
    return sources


def _normalize_whitespace(value: str) -> str:
    return _WHITESPACE_PATTERN.sub(" ", value).strip()


def _normalize_scalar_with_labels(value: object, labels: tuple[str, ...]) -> str | None:
    if not isinstance(value, str):
        return None

    cleaned = _normalize_whitespace(value)
    if not cleaned:
        return None

    for label in labels:
        cleaned = re.sub(
            rf"(?i)\b{re.escape(label)}\b\s*[:\-]?\s*",
            "",
            cleaned,
        )

    cleaned = _normalize_whitespace(cleaned.strip(" -:;,."))
    return cleaned or None
