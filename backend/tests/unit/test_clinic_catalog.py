from __future__ import annotations

from backend.app.application import clinic_catalog

KNOWN_NAME = "CENTRO COSTA AZAHAR"
ONLINE_ADDRESS = "Avinguda del Mar, 12, 12003 Castelló, España"


def test_lookup_address_uses_online_source(monkeypatch) -> None:
    class _FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> list[dict[str, str]]:
            return [{"display_name": ONLINE_ADDRESS}]

    def _fake_get(*_args, **_kwargs):
        return _FakeResponse()

    monkeypatch.setattr(clinic_catalog.httpx, "get", _fake_get)

    result = clinic_catalog.lookup_address_by_name(KNOWN_NAME)
    assert result["found"] is True
    assert result["address"] == ONLINE_ADDRESS
    assert result["source"] == "nominatim"


def test_lookup_address_case_insensitive(monkeypatch) -> None:
    class _FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> list[dict[str, str]]:
            return [{"display_name": ONLINE_ADDRESS}]

    def _fake_get(*_args, **_kwargs):
        return _FakeResponse()

    monkeypatch.setattr(clinic_catalog.httpx, "get", _fake_get)

    result = clinic_catalog.lookup_address_by_name("centro costa azahar")
    assert result["found"] is True
    assert result["address"] == ONLINE_ADDRESS


def test_lookup_name_exact_match() -> None:
    assert clinic_catalog.lookup_name_by_address(ONLINE_ADDRESS) is None


def test_lookup_name_case_insensitive() -> None:
    assert (
        clinic_catalog.lookup_name_by_address("avinguda del mar, 12, 12003 castelló, españa")
        is None
    )


def test_lookup_address_no_match(monkeypatch) -> None:
    class _FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> list[dict[str, str]]:
            return []

    def _fake_get(*_args, **_kwargs):
        return _FakeResponse()

    monkeypatch.setattr(clinic_catalog.httpx, "get", _fake_get)

    result = clinic_catalog.lookup_address_by_name("CLINICA DESCONOCIDA")
    assert result["found"] is False
    assert result["address"] is None
    assert result["source"] == "none"


def test_lookup_name_no_match() -> None:
    assert clinic_catalog.lookup_name_by_address("Avenida Inexistente 999, 99999 Ciudad") is None


def test_lookup_address_ambiguous(monkeypatch) -> None:
    monkeypatch.setattr(
        clinic_catalog,
        "_CLINIC_CATALOG",
        [
            {"names": ["CLINICA DUPLICADA"], "address": "Dir 1"},
            {"names": ["CLINICA DUPLICADA", "CLINICA DUP"], "address": "Dir 2"},
        ],
    )

    result = clinic_catalog.lookup_address_by_name("CLINICA DUPLICADA")
    assert result["found"] is False
    assert result["address"] is None


def test_lookup_name_ambiguous(monkeypatch) -> None:
    monkeypatch.setattr(
        clinic_catalog,
        "_CLINIC_CATALOG",
        [
            {"names": ["CLINICA A"], "address": "Calle Repetida 1"},
            {"names": ["CLINICA B"], "address": "Calle Repetida 1"},
        ],
    )

    assert clinic_catalog.lookup_name_by_address("Calle Repetida 1") is None


def test_lookup_address_uses_nominatim_after_catalog_miss(monkeypatch) -> None:
    expected_address = ONLINE_ADDRESS

    class _FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> list[dict[str, str]]:
            return [{"display_name": expected_address}]

    def _fake_get(*_args, **_kwargs):
        return _FakeResponse()

    monkeypatch.setattr(clinic_catalog.httpx, "get", _fake_get)

    result = clinic_catalog.lookup_address_by_name("CLINICA NUEVA")
    assert result["found"] is True
    assert result["address"] == expected_address
    assert result["source"] == "nominatim"


def test_lookup_address_catalog_hit_skips_nominatim(monkeypatch) -> None:
    def _fail_if_called(*_args, **_kwargs):
        raise AssertionError("Nominatim must not be called on catalog hit")

    monkeypatch.setattr(
        clinic_catalog,
        "_CLINIC_CATALOG",
        [{"names": [KNOWN_NAME], "address": "Rosa Molas 6, Bajo, 12003 Castelló"}],
    )
    monkeypatch.setattr(clinic_catalog.httpx, "get", _fail_if_called)

    result = clinic_catalog.lookup_address_by_name(KNOWN_NAME)
    assert result["found"] is True
    assert result["address"] == "Rosa Molas 6, Bajo, 12003 Castelló"
    assert result["source"] == "clinic_catalog"


def test_lookup_address_nominatim_timeout_returns_not_found(monkeypatch) -> None:
    def _timeout(*_args, **_kwargs):
        raise clinic_catalog.httpx.TimeoutException("timeout")

    monkeypatch.setattr(clinic_catalog.httpx, "get", _timeout)

    result = clinic_catalog.lookup_address_by_name("CLINICA TIMEOUT")
    assert result["found"] is False
    assert result["address"] is None


def test_lookup_address_nominatim_http_error_returns_not_found(monkeypatch) -> None:
    def _http_error(*_args, **_kwargs):
        raise clinic_catalog.httpx.HTTPError("http error")

    monkeypatch.setattr(clinic_catalog.httpx, "get", _http_error)

    result = clinic_catalog.lookup_address_by_name("CLINICA ERROR")
    assert result["found"] is False
    assert result["address"] is None


def test_lookup_address_nominatim_empty_result_returns_not_found(monkeypatch) -> None:
    class _FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> list[dict[str, str]]:
            return []

    def _fake_get(*_args, **_kwargs):
        return _FakeResponse()

    monkeypatch.setattr(clinic_catalog.httpx, "get", _fake_get)

    result = clinic_catalog.lookup_address_by_name("CLINICA SIN RESULTADOS")
    assert result["found"] is False
    assert result["address"] is None


def test_lookup_address_web_search_fallback_after_nominatim_miss(monkeypatch) -> None:
    class _NominatimEmptyResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> list[dict[str, str]]:
            return []

    class _WebSearchResponse:
        def raise_for_status(self) -> None:
            return None

        @property
        def text(self) -> str:
            return (
                '<a class="result__snippet" href="#">'
                "Veterinario en Castellón que encontrarás en Carrer Santa Maria "
                "Rosa Molas, 6, Bajos, 12004 Castelló de la Plana, Castelló."
                "</a>"
            )

    def _fake_get(url: str, *_args, **_kwargs):
        if "nominatim" in url:
            return _NominatimEmptyResponse()
        return _WebSearchResponse()

    monkeypatch.setattr(clinic_catalog.httpx, "get", _fake_get)

    result = clinic_catalog.lookup_address_by_name("CENTRO COSTA AZAHAR")
    assert result["found"] is True
    assert "Santa Maria Rosa Molas" in str(result["address"])
    assert result["source"] == "web_search"


def test_extract_address_from_web_snippet_returns_none_without_postal_code() -> None:
    snippet = (
        '<a class="result__snippet" href="#">'
        "Hospital Veterinario Costa Azahar en Castellón. "
        "Teléfono 964 72 36 97."
        "</a>"
    )

    assert clinic_catalog._extract_address_from_web_snippet(snippet) is None


def test_lookup_address_web_search_uses_proxy_when_direct_search_has_no_snippets(
    monkeypatch,
) -> None:
    class _DirectSearchResponse:
        def raise_for_status(self) -> None:
            return None

        @property
        def text(self) -> str:
            return "<html><body>No snippet available</body></html>"

    class _NominatimEmptyResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> list[dict[str, str]]:
            return []

    class _ProxyResponse:
        def raise_for_status(self) -> None:
            return None

        @property
        def text(self) -> str:
            return "Carrer de Santa María Rosa Molas, 6, 12004 Castelló de la Plana"

    def _fake_get(url: str, *_args, **_kwargs):
        if "nominatim" in url:
            return _NominatimEmptyResponse()
        if url.startswith(clinic_catalog._WEB_SEARCH_PROXY_PREFIX):
            return _ProxyResponse()
        return _DirectSearchResponse()

    monkeypatch.setattr(clinic_catalog.httpx, "get", _fake_get)

    result = clinic_catalog.lookup_address_by_name("CENTRO COSTA AZAHAR")
    assert result["found"] is True
    assert "Rosa Molas" in str(result["address"])
    assert result["source"] == "web_search"
