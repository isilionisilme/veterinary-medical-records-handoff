from __future__ import annotations

import signal


def test_create_app_applies_security_headers_to_version_route(test_client_factory) -> None:
    client = test_client_factory()

    with client:
        response = client.get("/version")

    assert response.status_code == 200
    assert response.headers["Strict-Transport-Security"] == "max-age=63072000; includeSubDomains"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Content-Security-Policy"] == "default-src 'self'"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_create_app_registers_and_restores_sigterm_handler_on_non_windows(
    monkeypatch, test_client_factory
) -> None:
    registrations: list[tuple[signal.Signals, object]] = []
    previous_handler = object()

    monkeypatch.setattr("backend.app.main.sys.platform", "linux")
    monkeypatch.setattr("backend.app.main.signal.getsignal", lambda _sig: previous_handler)
    monkeypatch.setattr("backend.app.main._in_main_thread", lambda: True)

    def _fake_signal(sig: signal.Signals, handler: object) -> None:
        registrations.append((sig, handler))

    monkeypatch.setattr("backend.app.main.signal.signal", _fake_signal)

    client = test_client_factory()
    with client:
        pass

    assert len(registrations) == 2
    assert registrations[0][0] == signal.SIGTERM
    assert callable(registrations[0][1])
    assert registrations[1] == (signal.SIGTERM, previous_handler)
