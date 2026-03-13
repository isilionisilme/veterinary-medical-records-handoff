"""Administrative one-off CLI commands for backend operations."""

from __future__ import annotations

import argparse
import json

from backend.app.infra import database
from backend.app.settings import get_settings


def _mask_config(key: str, value: object) -> object:
    sensitive_tokens = ("secret", "token", "password", "key")
    key_lower = key.lower()
    if isinstance(value, str) and any(token in key_lower for token in sensitive_tokens):
        if len(value) <= 4:
            return "****"
        return f"{value[:2]}***{value[-2:]}"
    return value


def command_db_schema() -> int:
    database.ensure_schema()
    print("Schema ensured successfully.")
    return 0


def command_db_check() -> int:
    path = database.get_database_path()
    exists = path.exists()
    with database.get_connection() as conn:
        table_count = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
        ).fetchone()[0]
    print(f"DB path: {path}")
    print(f"Exists: {exists}")
    print(f"Table count: {table_count}")
    return 0


def command_config_check() -> int:
    settings = get_settings()
    payload = {key: _mask_config(key, value) for key, value in settings.__dict__.items()}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Backend administrative commands")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("db-schema", help="Ensure SQLite schema exists")
    subparsers.add_parser("db-check", help="Check database readability and table count")
    subparsers.add_parser("config-check", help="Print resolved runtime configuration")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "db-schema":
        return command_db_schema()
    if args.command == "db-check":
        return command_db_check()
    if args.command == "config-check":
        return command_config_check()

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
