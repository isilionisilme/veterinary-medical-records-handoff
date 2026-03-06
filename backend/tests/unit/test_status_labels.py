from typing import cast

from backend.app.domain.models import ProcessingStatus
from backend.app.domain.status import map_status_label


def test_map_status_label_returns_expected_labels() -> None:
    assert map_status_label(ProcessingStatus.UPLOADED) == "Uploaded"
    assert map_status_label(ProcessingStatus.PROCESSING) == "Processing"
    assert map_status_label(ProcessingStatus.COMPLETED) == "Ready for review"
    assert map_status_label(ProcessingStatus.FAILED) == "Failed"
    assert map_status_label(ProcessingStatus.TIMED_OUT) == "Processing timed out"


def test_map_status_label_returns_unknown_for_unmapped_status() -> None:
    assert map_status_label(cast(ProcessingStatus, "UNMAPPED_STATUS")) == "Unknown"
