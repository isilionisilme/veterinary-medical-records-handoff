from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_backend_image_copies_shared_contract_directory() -> None:
    dockerfile = (REPO_ROOT / "Dockerfile.backend").read_text(encoding="utf-8")
    assert "COPY shared /app/shared" in dockerfile


def test_frontend_image_copies_shared_contract_directory() -> None:
    dockerfile = (REPO_ROOT / "Dockerfile.frontend").read_text(encoding="utf-8")
    assert "COPY shared /app/shared" in dockerfile


def test_frontend_contract_import_path_stays_repo_relative() -> None:
    source = (REPO_ROOT / "frontend" / "src" / "lib" / "globalSchema.ts").read_text(
        encoding="utf-8"
    )
    assert "../../../shared/global_schema_contract.json" in source
