from __future__ import annotations

from time import perf_counter

import pytest


def _measure_p95_ms(callable_request, rounds: int = 10) -> float:
    samples_ms: list[float] = []
    for _ in range(rounds):
        started = perf_counter()
        callable_request()
        samples_ms.append((perf_counter() - started) * 1000)
    samples_ms.sort()
    if not samples_ms:
        return 0.0
    index = max(0, min(len(samples_ms) - 1, int(0.95 * (len(samples_ms) - 1))))
    return samples_ms[index]


@pytest.mark.benchmark
def test_list_documents_latency_empty_db(benchmark, benchmark_client):
    def request():
        response = benchmark_client.get("/documents")
        assert response.status_code == 200
        return response

    benchmark.pedantic(request, rounds=10, iterations=1)
    p95_ms = _measure_p95_ms(request, rounds=10)
    assert p95_ms < 500


@pytest.mark.benchmark
def test_list_documents_latency_seeded_db(benchmark, benchmark_client, seeded_document_ids):
    assert len(seeded_document_ids) == 5

    def request():
        response = benchmark_client.get("/documents")
        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] >= 5
        return response

    benchmark.pedantic(request, rounds=10, iterations=1)
    p95_ms = _measure_p95_ms(request, rounds=10)
    assert p95_ms < 500


@pytest.mark.benchmark
def test_get_document_latency(benchmark, benchmark_client, seeded_document_ids):
    target_document_id = seeded_document_ids[0]

    def request():
        response = benchmark_client.get(f"/documents/{target_document_id}")
        assert response.status_code == 200
        return response

    benchmark.pedantic(request, rounds=10, iterations=1)
    p95_ms = _measure_p95_ms(request, rounds=10)
    assert p95_ms < 500


@pytest.mark.benchmark
def test_upload_latency(benchmark, benchmark_client, sample_pdf_bytes: bytes):
    upload_counter = 0

    def request():
        nonlocal upload_counter
        upload_counter += 1
        response = benchmark_client.post(
            "/documents/upload",
            files={
                "file": (
                    f"benchmark-upload-{upload_counter}.pdf",
                    sample_pdf_bytes,
                    "application/pdf",
                )
            },
        )
        assert response.status_code == 201
        return response

    benchmark.pedantic(request, rounds=10, iterations=1)
    p95_ms = _measure_p95_ms(request, rounds=10)
    assert p95_ms < 2000


@pytest.mark.benchmark
def test_health_latency(benchmark, benchmark_client):
    def request():
        response = benchmark_client.get("/health")
        assert response.status_code == 200
        return response

    benchmark.pedantic(request, rounds=10, iterations=1)
    p95_ms = _measure_p95_ms(request, rounds=10)
    assert p95_ms < 500
