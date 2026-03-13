from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def benchmark_client(test_client_factory):
    with test_client_factory(disable_processing=True, auth_token=None) as client:
        yield client


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    fixture_path = (
        Path(__file__).resolve().parents[1] / "fixtures" / "pdfs" / "clinical_history_1.pdf"
    )
    return fixture_path.read_bytes()


@pytest.fixture
def seeded_document_ids(benchmark_client, sample_pdf_bytes: bytes) -> list[str]:
    document_ids: list[str] = []
    for index in range(5):
        response = benchmark_client.post(
            "/documents/upload",
            files={"file": (f"seed-{index}.pdf", sample_pdf_bytes, "application/pdf")},
        )
        assert response.status_code == 201
        document_ids.append(response.json()["document_id"])
    return document_ids
