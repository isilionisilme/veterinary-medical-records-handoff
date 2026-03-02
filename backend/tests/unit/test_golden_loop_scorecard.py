from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    module_path = Path(__file__).resolve().parents[3] / "scripts" / "golden_loop_scorecard.py"
    spec = importlib.util.spec_from_file_location("golden_loop_scorecard", module_path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_evaluate_cases_computes_expected_metrics() -> None:
    module = _load_module()

    cases = [
        {"id": "a", "text": "x", "expected": "Luna"},
        {"id": "b", "text": "y", "expected": "Nala"},
        {"id": "c", "text": "z", "expected": None},
    ]
    extracted_by_case = {"a": "Luna", "b": None, "c": "Noise"}

    def _fake_extract(field_key: str, raw_text: str, case_id: str):
        assert field_key == "pet_name"
        assert isinstance(raw_text, str)
        return extracted_by_case[case_id]

    metrics = module.evaluate_cases(
        cases=cases,
        field_key="pet_name",
        extractor=_fake_extract,
    )

    assert metrics["total_cases"] == 3
    assert metrics["exact_matches"] == 1
    assert metrics["null_misses"] == 1
    assert metrics["false_positives"] == 1
    assert metrics["exact_match_rate"] == 1 / 3
    assert metrics["null_miss_rate"] == 1 / 3
    assert metrics["false_positive_rate"] == 1 / 3
    assert len(metrics["mismatches"]) == 2


def test_evaluate_gates_fails_on_threshold_and_regression() -> None:
    module = _load_module()

    metrics = {
        "exact_match_rate": 0.75,
        "null_miss_rate": 0.25,
        "false_positive_rate": 0.10,
    }
    baseline = {
        "exact_match_rate": 0.80,
        "null_miss_rate": 0.20,
        "false_positive_rate": 0.05,
    }

    failures = module.evaluate_gates(
        metrics=metrics,
        baseline_metrics=baseline,
        min_exact_match_rate=0.78,
        max_null_miss_rate=0.22,
        max_false_positive_rate=0.08,
        allow_regression=False,
    )

    assert any("exact_match_rate" in failure for failure in failures)
    assert any("null_miss_rate" in failure for failure in failures)
    assert any("false_positive_rate" in failure for failure in failures)
    assert any("regression: exact_match_rate" in failure for failure in failures)
    assert any("regression: null_miss_rate" in failure for failure in failures)
    assert any("regression: false_positive_rate" in failure for failure in failures)


def test_evaluate_gates_allows_regression_when_opted_in() -> None:
    module = _load_module()

    metrics = {
        "exact_match_rate": 0.75,
        "null_miss_rate": 0.25,
        "false_positive_rate": 0.10,
    }
    baseline = {
        "exact_match_rate": 0.80,
        "null_miss_rate": 0.20,
        "false_positive_rate": 0.05,
    }

    failures = module.evaluate_gates(
        metrics=metrics,
        baseline_metrics=baseline,
        min_exact_match_rate=0.70,
        max_null_miss_rate=0.30,
        max_false_positive_rate=0.20,
        allow_regression=True,
    )

    assert failures == []


def test_resolve_config_float_prefers_cli_then_gates_then_top_level() -> None:
    module = _load_module()

    payload = {
        "min_exact_match_rate": 0.6,
        "gates": {
            "min_exact_match_rate": 0.7,
        },
    }

    assert (
        module._resolve_config_float(
            cli_value=0.8,
            cases_payload=payload,
            key="min_exact_match_rate",
            default_value=0.0,
        )
        == 0.8
    )
    assert (
        module._resolve_config_float(
            cli_value=None,
            cases_payload=payload,
            key="min_exact_match_rate",
            default_value=0.0,
        )
        == 0.7
    )
    assert (
        module._resolve_config_float(
            cli_value=None,
            cases_payload={"max_null_miss_rate": 0.2},
            key="max_null_miss_rate",
            default_value=1.0,
        )
        == 0.2
    )


def test_resolve_optional_path_handles_relative_paths_from_cases_dir() -> None:
    module = _load_module()

    cases_path = Path("D:/repo/backend/tests/fixtures/field/cases.golden-loop.json")

    resolved = module._resolve_optional_path(
        cli_value=None,
        cases_payload={"baseline": "./baselines/pet_name.baseline.json"},
        payload_key="baseline",
        cases_path=cases_path,
    )

    assert resolved is not None
    assert (
        str(resolved)
        .replace("\\", "/")
        .endswith("/backend/tests/fixtures/field/baselines/pet_name.baseline.json")
    )
