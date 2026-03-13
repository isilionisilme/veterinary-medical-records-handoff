from __future__ import annotations

from pathlib import Path

from backend.app import cli


def test_db_schema_command_ensures_schema_and_prints_status(monkeypatch, capsys) -> None:
    called = {"ensure": 0}

    def fake_ensure_schema() -> None:
        called["ensure"] += 1

    monkeypatch.setattr(cli.database, "ensure_schema", fake_ensure_schema)
    monkeypatch.setattr("sys.argv", ["cli", "db-schema"])

    result = cli.main()
    output = capsys.readouterr().out

    assert result == 0
    assert called["ensure"] == 1
    assert "Schema ensured successfully." in output


def test_db_check_command_returns_zero_for_healthy_db(monkeypatch, capsys) -> None:
    class FakeCursor:
        def fetchone(self):
            return (7,)

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def execute(self, _query: str) -> FakeCursor:
            return FakeCursor()

    monkeypatch.setattr(cli.database, "get_database_path", lambda: Path("/tmp/test.db"))
    monkeypatch.setattr(cli.database, "get_connection", lambda: FakeConnection())
    monkeypatch.setattr("sys.argv", ["cli", "db-check"])

    result = cli.main()
    output = capsys.readouterr().out

    assert result == 0
    assert "DB path:" in output
    assert "Table count: 7" in output


def test_config_check_command_prints_resolved_config(monkeypatch, capsys) -> None:
    class FakeSettings:
        def __init__(self) -> None:
            self.ENV = "test"
            self.API_TOKEN = "abcde12345"

    monkeypatch.setattr(cli, "get_settings", lambda: FakeSettings())
    monkeypatch.setattr("sys.argv", ["cli", "config-check"])

    result = cli.main()
    output = capsys.readouterr().out

    assert result == 0
    assert '"ENV": "test"' in output
    assert '"API_TOKEN": "ab***45"' in output
