"""Compatibility guard for the split review-flow suites.

Scenario focus: keep discoverability and ensure split modules remain importable.
"""

from __future__ import annotations

import importlib


def test_review_flow_split_modules_are_importable() -> None:
    modules = (
        "backend.tests.integration.test_document_review_confidence_learning",
        "backend.tests.integration.test_document_review_review_status",
        "backend.tests.integration.test_document_review_edit_flow",
        "backend.tests.integration.test_document_review_edit_guards",
    )

    for module_name in modules:
        assert importlib.import_module(module_name) is not None
