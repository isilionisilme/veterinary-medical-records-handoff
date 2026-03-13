from __future__ import annotations

API_HEALTH_PATHS = [
    "/api/health",
    "/api/health/live",
    "/api/health/ready",
]

PUBLIC_HEALTH_PATHS = [
    "/health",
    "/health/live",
    "/health/ready",
]


def test_api_routes_are_open_when_auth_token_is_unset(test_client_factory) -> None:
    with test_client_factory(auth_token=None) as client:
        for path in API_HEALTH_PATHS:
            response = client.get(path)

            assert response.status_code == 200
            if path.endswith("/live"):
                assert response.json() == {"status": "alive"}
            else:
                assert response.json()["status"] == "healthy"


def test_api_routes_require_bearer_token_when_auth_token_is_set(test_client_factory) -> None:
    with test_client_factory(auth_token="secret-token") as client:
        for path in API_HEALTH_PATHS:
            response = client.get(path)

            assert response.status_code == 401
            payload = response.json()
            assert payload["error_code"] == "UNAUTHORIZED"


def test_api_routes_reject_invalid_bearer_token(test_client_factory) -> None:
    with test_client_factory(auth_token="secret-token") as client:
        for path in API_HEALTH_PATHS:
            response = client.get(
                path,
                headers={"Authorization": "Bearer wrong-token"},
            )

            assert response.status_code == 401
            payload = response.json()
            assert payload["error_code"] == "UNAUTHORIZED"


def test_api_routes_allow_valid_bearer_token(test_client_factory) -> None:
    with test_client_factory(auth_token="secret-token") as client:
        for path in API_HEALTH_PATHS:
            response = client.get(
                path,
                headers={"Authorization": "Bearer secret-token"},
            )

            assert response.status_code == 200
            if path.endswith("/live"):
                assert response.json() == {"status": "alive"}
            else:
                assert response.json()["status"] == "healthy"


def test_non_api_routes_remain_unauthenticated_even_when_auth_enabled(
    test_client_factory,
) -> None:
    with test_client_factory(auth_token="secret-token") as client:
        for path in PUBLIC_HEALTH_PATHS:
            response = client.get(path)

            assert response.status_code == 200
            if path.endswith("/live"):
                assert response.json() == {"status": "alive"}
            else:
                assert response.json()["status"] == "healthy"
