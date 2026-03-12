from __future__ import annotations

import json
import logging

import backend.app.main as app_main
from backend.app.infra.correlation import request_id_var
from backend.app.logging_config import configure_logging
from backend.app.settings import clear_settings_cache, get_settings


class TestLogLevelSettings:
    def test_default_log_level_is_info(self, monkeypatch) -> None:
        monkeypatch.delenv("LOG_LEVEL", raising=False)
        clear_settings_cache()

        assert get_settings().log_level == "INFO"

    def test_log_level_env_override_is_normalized(self, monkeypatch) -> None:
        monkeypatch.setenv("LOG_LEVEL", " debug ")
        clear_settings_cache()

        assert get_settings().log_level == "DEBUG"


class TestLoggingConfiguration:
    def setup_method(self) -> None:
        self.root_logger = logging.getLogger()
        self.original_handlers = self.root_logger.handlers.copy()
        self.original_level = self.root_logger.level

    def teardown_method(self) -> None:
        for handler in self.root_logger.handlers[:]:
            self.root_logger.removeHandler(handler)
            handler.close()
        for handler in self.original_handlers:
            self.root_logger.addHandler(handler)
        self.root_logger.setLevel(self.original_level)
        clear_settings_cache()

    def test_configure_logging_sets_root_level_from_settings(self, monkeypatch) -> None:
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        clear_settings_cache()

        configure_logging(get_settings().log_level)

        assert logging.getLogger().getEffectiveLevel() == logging.DEBUG

    def test_configure_logging_emits_json_with_request_id(self, capsys) -> None:
        configure_logging("INFO")

        token = request_id_var.set("req-123")
        try:
            logging.getLogger("backend.tests.logging").info("structured message")
        finally:
            request_id_var.reset(token)

        payload = json.loads(capsys.readouterr().out.strip())

        assert payload["request_id"] == "req-123"
        assert payload["message"] == "structured message"
        assert payload["levelname"] == "INFO"
        assert payload["name"] == "backend.tests.logging"

    def test_lifespan_configures_logging_with_settings_level(
        self, monkeypatch, test_client_factory
    ) -> None:
        calls: list[str] = []
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        monkeypatch.setattr(app_main, "configure_logging", calls.append)

        with test_client_factory(auth_token=None) as client:
            response = client.get("/health")

        assert response.status_code == 200
        assert calls == ["WARNING"]
