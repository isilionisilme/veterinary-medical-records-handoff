"""Port for calibration signals and snapshots persistence."""

from __future__ import annotations

from typing import Literal, Protocol


class CalibrationRepository(Protocol):
    """Persistence contract for deterministic calibration counters and snapshots."""

    def get_latest_applied_calibration_snapshot(
        self, *, document_id: str
    ) -> tuple[str, dict[str, object]] | None:
        """Return (run_id, snapshot_payload) for the latest applied calibration snapshot."""

    def increment_calibration_signal(
        self,
        *,
        context_key: str,
        field_key: str,
        mapping_id: str | None,
        policy_version: str,
        signal_type: Literal["edited", "accepted_unchanged"],
        updated_at: str,
    ) -> None:
        """Increment deterministic calibration counters for a scoped signal."""

    def apply_calibration_deltas(
        self,
        *,
        context_key: str,
        field_key: str,
        mapping_id: str | None,
        policy_version: str,
        accept_delta: int,
        edit_delta: int,
        updated_at: str,
    ) -> None:
        """Apply deterministic signed deltas to calibration counters for a scope."""

    def get_calibration_counts(
        self,
        *,
        context_key: str,
        field_key: str,
        mapping_id: str | None,
        policy_version: str,
    ) -> tuple[int, int] | None:
        """Return (accept_count, edit_count) for a calibration scope."""
