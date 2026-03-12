from __future__ import annotations


def test_starlette_http_exception_returns_json_only(test_client_factory) -> None:
    with test_client_factory() as client:
        response = client.get(
            "/this-route-does-not-exist?detail=<script>alert(1)</script>",
            headers={"accept": "text/html"},
        )

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")
    payload = response.json()
    assert payload["error_code"] == "NOT_FOUND"
    assert payload["message"] == "Not Found"
    assert payload["request_id"] == response.headers["x-request-id"]
    assert "<html" not in response.text.lower()
    assert "<script" not in response.text.lower()
