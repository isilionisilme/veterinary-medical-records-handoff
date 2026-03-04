"""On-demand clinic address lookup with online geocoder.

This module resolves addresses via Nominatim (OpenStreetMap) on-demand.
It is called via API (user-initiated), never auto-enriched.
It is a production component and emits fallback events for operational monitoring.
"""

from __future__ import annotations

import html
import logging
import re
from urllib.parse import quote_plus

import httpx

CATALOG_VERSION = "1.0.0"
_NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
_NOMINATIM_TIMEOUT_SECONDS = 5.0
_NOMINATIM_HEADERS = {"User-Agent": "veterinary-medical-records/1.0"}
_WEB_SEARCH_URL = "https://duckduckgo.com/html/"
_WEB_SEARCH_HEADERS = {"User-Agent": "Mozilla/5.0"}
_WEB_SEARCH_PROXY_PREFIX = "https://r.jina.ai/http://duckduckgo.com/?q="

_CLINIC_CATALOG: list[dict[str, object]] = []
logger = logging.getLogger(__name__)


def _normalize_text(value: str) -> str:
    return value.strip().casefold()


def _lookup_address_via_nominatim(name: str) -> str | None:
    params = {
        "q": name,
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": 1,
        "countrycodes": "es",
    }

    try:
        response = httpx.get(
            _NOMINATIM_URL,
            params=params,
            headers=_NOMINATIM_HEADERS,
            timeout=_NOMINATIM_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError):
        return None

    if not isinstance(payload, list) or not payload:
        return None

    first_result = payload[0]
    if not isinstance(first_result, dict):
        return None

    display_name = first_result.get("display_name")
    if not isinstance(display_name, str) or not display_name.strip():
        return None

    return display_name.strip()


def _extract_address_from_web_snippet(snippet: str) -> str | None:
    cleaned = html.unescape(re.sub(r"<[^>]+>", " ", snippet))
    cleaned = " ".join(cleaned.split())

    pattern = re.compile(
        r"(?:Carrer|Calle|Avenida|Av\.?|Plaza|Paseo|Camino|Ronda|Rua|C/|C\.)"
        r"[^.;]{0,120}?\b\d{1,4}\b[^.;]{0,120}?\b\d{5}\b[^.;]{0,120}",
        flags=re.IGNORECASE,
    )
    direct_match = pattern.search(cleaned)
    if direct_match:
        return _sanitize_address_candidate(direct_match.group(0))

    direccion_pattern = re.compile(
        r"Direcci[oó]n\s*:?\s*([^.;]{10,220})",
        flags=re.IGNORECASE,
    )
    direccion_match = direccion_pattern.search(cleaned)
    if direccion_match:
        candidate = _sanitize_address_candidate(direccion_match.group(1))
        if re.search(r"\b\d{5}\b", candidate):
            return candidate

    return None


def _extract_address_from_text_block(text_block: str) -> str | None:
    cleaned = " ".join(text_block.split())
    pattern = re.compile(
        r"(?:Carrer|Calle|Avenida|Av\.?|Plaza|Paseo|Camino|Ronda|Rua|C/|C\.)"
        r"[^.;\n]{0,120}?\b\d{1,4}\b[^.;\n]{0,120}?\b\d{5}\b[^.;\n]{0,120}",
        flags=re.IGNORECASE,
    )
    match = pattern.search(cleaned)
    return _sanitize_address_candidate(match.group(0)) if match else None


def _sanitize_address_candidate(candidate: str) -> str:
    sanitized = re.sub(r"\[[^\]]+\]\([^\)]+\)", "", candidate)
    sanitized = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", sanitized)
    sanitized = sanitized.split("![", 1)[0]
    sanitized = re.split(
        r"(?:\bTel[eé]fono\b|tel:|\bHorario\b|\bCódigo Postal\b)",
        sanitized,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    sanitized = re.sub(r"\s{2,}", " ", sanitized)
    sanitized = re.sub(r"\s+\d(?:[\.,]\d)?$", "", sanitized)
    return sanitized.strip(" ,;.-")


def _lookup_address_via_web_search(name: str) -> str | None:
    query = f"hospital veterinario {name} direccion"

    try:
        response = httpx.get(
            _WEB_SEARCH_URL,
            params={"q": query},
            headers=_WEB_SEARCH_HEADERS,
            timeout=_NOMINATIM_TIMEOUT_SECONDS,
            follow_redirects=True,
        )
        response.raise_for_status()
        content = response.text
    except (httpx.HTTPError, AttributeError):
        return None

    snippets = re.findall(
        r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
        content,
        flags=re.IGNORECASE | re.DOTALL,
    )

    for snippet in snippets[:10]:
        address = _extract_address_from_web_snippet(snippet)
        if address:
            return address

    proxy_url = _WEB_SEARCH_PROXY_PREFIX + quote_plus(query)
    try:
        logger.info("clinic_lookup_web_proxy_fallback_attempted")
        proxy_response = httpx.get(
            proxy_url,
            headers=_WEB_SEARCH_HEADERS,
            timeout=_NOMINATIM_TIMEOUT_SECONDS,
            follow_redirects=True,
        )
        proxy_response.raise_for_status()
        proxy_content = proxy_response.text
    except (httpx.HTTPError, AttributeError):
        return None

    proxy_address = _extract_address_from_text_block(proxy_content)
    if proxy_address:
        logger.info("clinic_lookup_web_proxy_fallback_succeeded")
        return proxy_address

    return None


def lookup_address_by_name(name: str) -> dict[str, object]:
    """Look up a clinic address by name.

    Returns a dict with keys:
      - found (bool): whether a unique match was found
      - address (str | None): the matched address, or None
            - source (str): "nominatim" | "web_search" | "clinic_catalog" | "none"
      - catalog_version (str): version of the catalog used
    """
    result: dict[str, object] = {
        "found": False,
        "address": None,
        "source": "none",
        "catalog_version": CATALOG_VERSION,
    }

    if not isinstance(name, str) or not name.strip():
        return result

    normalized_name = _normalize_text(name)

    matches: list[dict[str, object]] = []
    for entry in _CLINIC_CATALOG:
        raw_names = entry.get("names")
        if not isinstance(raw_names, list):
            continue
        normalized_aliases = [
            _normalize_text(alias)
            for alias in raw_names
            if isinstance(alias, str) and alias.strip()
        ]
        if normalized_name in normalized_aliases:
            matches.append(entry)

    if len(matches) == 1:
        address = matches[0].get("address")
        if isinstance(address, str) and address.strip():
            result["found"] = True
            result["address"] = address
            result["source"] = "clinic_catalog"
            return result

    if len(matches) > 1:
        return result

    nominatim_address = _lookup_address_via_nominatim(name)
    if nominatim_address:
        result["found"] = True
        result["address"] = nominatim_address
        result["source"] = "nominatim"
        return result

    web_address = _lookup_address_via_web_search(name)
    if web_address:
        result["found"] = True
        result["address"] = web_address
        result["source"] = "web_search"

    return result


def lookup_name_by_address(address: str) -> str | None:
    """Look up a canonical clinic name by address (exact match).

    Returns the canonical name if exactly 1 match, None otherwise.
    """
    if not isinstance(address, str):
        return None

    normalized_address = _normalize_text(address)
    if not normalized_address:
        return None

    matches: list[dict[str, object]] = []
    for entry in _CLINIC_CATALOG:
        entry_address = entry.get("address")
        if not isinstance(entry_address, str):
            continue
        if _normalize_text(entry_address) == normalized_address:
            matches.append(entry)

    if len(matches) != 1:
        return None

    raw_names = matches[0].get("names")
    if not isinstance(raw_names, list) or not raw_names:
        return None

    canonical_name = raw_names[0]
    return canonical_name if isinstance(canonical_name, str) and canonical_name.strip() else None
