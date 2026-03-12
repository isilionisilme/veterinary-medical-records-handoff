"""Tests for correlation ID middleware and contextvars propagation."""

from __future__ import annotations

from unittest.mock import MagicMock

from backend.app.infra.correlation import (
    CorrelationIdFilter,
    generate_request_id,
    get_request_id,
    request_id_var,
)


class TestCorrelationModule:
    """Unit tests for correlation.py helpers."""

    def test_generate_request_id_is_16_hex_chars(self) -> None:
        rid = generate_request_id()
        assert len(rid) == 16
        assert all(c in "0123456789abcdef" for c in rid)

    def test_generate_request_id_is_unique(self) -> None:
        ids = {generate_request_id() for _ in range(100)}
        assert len(ids) == 100

    def test_get_request_id_default_empty(self) -> None:
        token = request_id_var.set("")
        try:
            assert get_request_id() == ""
        finally:
            request_id_var.reset(token)

    def test_get_request_id_returns_set_value(self) -> None:
        token = request_id_var.set("test-123")
        try:
            assert get_request_id() == "test-123"
        finally:
            request_id_var.reset(token)

    def test_correlation_id_filter_injects_request_id(self) -> None:
        token = request_id_var.set("filter-abc")
        try:
            filt = CorrelationIdFilter()
            record = MagicMock()
            result = filt.filter(record)
            assert result is True
            assert record.request_id == "filter-abc"
        finally:
            request_id_var.reset(token)


class TestCorrelationIdMiddleware:
    """Integration tests for CorrelationIdMiddleware via TestClient."""

    def test_response_includes_x_request_id_header(self, test_client_factory) -> None:
        with test_client_factory(auth_token=None) as client:
            response = client.get("/health")
        assert response.status_code == 200
        assert "x-request-id" in response.headers

    def test_generated_id_is_16_hex_chars(self, test_client_factory) -> None:
        with test_client_factory(auth_token=None) as client:
            response = client.get("/health")
        rid = response.headers["x-request-id"]
        assert len(rid) == 16
        assert all(c in "0123456789abcdef" for c in rid)

    def test_incoming_x_request_id_is_preserved(self, test_client_factory) -> None:
        with test_client_factory(auth_token=None) as client:
            response = client.get("/health", headers={"X-Request-ID": "custom-id-42"})
        assert response.headers["x-request-id"] == "custom-id-42"

    def test_missing_x_request_id_generates_new_one(self, test_client_factory) -> None:
        with test_client_factory(auth_token=None) as client:
            r1 = client.get("/health")
            r2 = client.get("/health")
        assert r1.headers["x-request-id"] != r2.headers["x-request-id"]

    def test_x_request_id_present_on_api_routes(self, test_client_factory) -> None:
        with test_client_factory(auth_token=None) as client:
            response = client.get("/api/health")
        assert "x-request-id" in response.headers

    def test_x_request_id_present_on_auth_401(self, test_client_factory) -> None:
        with test_client_factory(auth_token="secret-token") as client:
            response = client.get("/api/health")
        assert response.status_code == 401
        assert "x-request-id" in response.headers

    def test_x_request_id_present_on_unhandled_500(self, test_client_factory) -> None:
        with test_client_factory(auth_token=None) as client:

            @client.app.get("/__test/boom")
            def _boom() -> dict[str, str]:
                raise RuntimeError("boom")

            response = client.get("/__test/boom")

        assert response.status_code == 500
        assert "x-request-id" in response.headers
