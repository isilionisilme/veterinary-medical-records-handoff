from __future__ import annotations

from backend.app.application.confidence_calibration import (
    build_context_key,
    compute_review_history_adjustment,
)


def test_compute_review_history_adjustment_returns_zero_below_min_volume() -> None:
    assert compute_review_history_adjustment(accept_count=2, edit_count=0) == 0.0
    assert compute_review_history_adjustment(accept_count=1, edit_count=1) == 0.0


def test_compute_review_history_adjustment_is_positive_for_high_acceptance() -> None:
    adjustment = compute_review_history_adjustment(accept_count=9, edit_count=1)
    assert adjustment > 0
    assert adjustment <= 15.0


def test_compute_review_history_adjustment_is_negative_for_high_edits() -> None:
    adjustment = compute_review_history_adjustment(accept_count=1, edit_count=9)
    assert adjustment < 0
    assert adjustment >= -15.0


def test_compute_review_history_adjustment_is_bounded_and_rounded() -> None:
    assert compute_review_history_adjustment(accept_count=1_000, edit_count=0) == 15.0
    assert compute_review_history_adjustment(accept_count=0, edit_count=1_000) == -15.0
    assert compute_review_history_adjustment(accept_count=4, edit_count=3) == 1.7


def test_build_context_key_is_stable_for_same_inputs() -> None:
    first = build_context_key(
        document_type="veterinary_record",
        language="es",
    )
    second = build_context_key(
        document_type="veterinary_record",
        language="es",
    )
    assert first == second
