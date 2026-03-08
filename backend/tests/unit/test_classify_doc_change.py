from __future__ import annotations

import importlib.util
import json
import runpy
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
CLASSIFIER_PATH = REPO_ROOT / "scripts" / "docs" / "classify_doc_change.py"
DOC_SYNC_GUARD_PATH = REPO_ROOT / "scripts" / "docs" / "check_doc_test_sync.py"


def _load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_classifier_main(
    module: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> dict[str, Any]:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        module,
        "_git_single_line",
        lambda cmd, _error: "HEADSHA" if cmd[-1] == "HEAD" else "MERGEBASE",
    )
    monkeypatch.setattr(sys, "argv", ["classify_doc_change.py", "--base-ref", "BASE"])
    assert module.main() == 0
    output_path = tmp_path / "doc_change_classification.json"
    return json.loads(output_path.read_text(encoding="utf-8"))


def _run_doc_sync_main(
    module: Any,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    changed_files: list[str],
    rules: list[dict[str, Any]],
    classification: str | None,
) -> int:
    map_path = tmp_path / "map.json"
    map_path.write_text(
        json.dumps(
            {
                "fail_on_unmapped_docs": True,
                "rules": rules,
            }
        ),
        encoding="utf-8",
    )
    if classification is not None:
        (tmp_path / "doc_change_classification.json").write_text(
            json.dumps(
                {
                    "files": {},
                    "overall": classification,
                    "meta": {
                        "base_ref": "BASE",
                        "head_sha": "HEADSHA",
                    },
                }
            ),
            encoding="utf-8",
        )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(module, "_run_changed_files", lambda _base: changed_files)
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=0, stdout="HEADSHA\n", stderr=""),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "check_doc_test_sync.py",
            "--base-ref",
            "BASE",
            "--map-file",
            str(map_path),
        ],
    )
    monkeypatch.delenv("DOC_SYNC_RELAXED", raising=False)
    return module.main()


def test_rule_signal_must(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module(CLASSIFIER_PATH, "scripts.classify_doc_change")
    monkeypatch.setattr(
        module, "_changed_added_lines", lambda _base, _path: ["This MUST be enforced"]
    )
    assert module._classify_file("BASE", "docs/path.md") == "Rule"


def test_rule_signal_threshold(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module(CLASSIFIER_PATH, "scripts.classify_doc_change")
    monkeypatch.setattr(
        module, "_changed_added_lines", lambda _base, _path: ["minimum threshold is 0.8"]
    )
    assert module._classify_file("BASE", "docs/path.md") == "Rule"


def test_navigation_links_only(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module(CLASSIFIER_PATH, "scripts.classify_doc_change")
    monkeypatch.setattr(
        module,
        "_changed_added_lines",
        lambda _base, _path: ["[Guide](docs/guide.md)", "[FAQ](docs/faq.md)"],
    )
    assert module._classify_file("BASE", "docs/path.md") == "Navigation"


def test_navigation_heading_change(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module(CLASSIFIER_PATH, "scripts.classify_doc_change")
    monkeypatch.setattr(module, "_changed_added_lines", lambda _base, _path: ["## Updated heading"])
    assert module._classify_file("BASE", "docs/path.md") == "Navigation"


def test_clarification_rewording(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module(CLASSIFIER_PATH, "scripts.classify_doc_change")
    monkeypatch.setattr(
        module,
        "_changed_added_lines",
        lambda _base, _path: ["This text clarifies expected behavior for contributors."],
    )
    assert module._classify_file("BASE", "docs/path.md") == "Clarification"


def test_fallback_on_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module(CLASSIFIER_PATH, "scripts.classify_doc_change")
    monkeypatch.setattr(
        module, "_changed_markdown_files", lambda _base: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    payload = _run_classifier_main(module, tmp_path, monkeypatch)
    assert payload["overall"] == "Rule"
    assert payload["files"] == {}


def test_commit_tag_override_nav(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module(CLASSIFIER_PATH, "scripts.classify_doc_change")
    monkeypatch.setattr(
        module,
        "_changed_markdown_files",
        lambda _base: ["docs/projects/veterinary-medical-records/A.md"],
    )
    monkeypatch.setattr(module, "_commit_tag_override", lambda _base: "Navigation")
    monkeypatch.setattr(module, "_classify_file", lambda _base, _path: "Rule")
    payload = _run_classifier_main(module, tmp_path, monkeypatch)
    assert payload["overall"] == "Navigation"
    assert payload["files"]["docs/projects/veterinary-medical-records/A.md"] == "Navigation"


def test_commit_tag_override_rule(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module(CLASSIFIER_PATH, "scripts.classify_doc_change")
    monkeypatch.setattr(
        module,
        "_changed_markdown_files",
        lambda _base: ["docs/projects/veterinary-medical-records/A.md"],
    )
    monkeypatch.setattr(module, "_commit_tag_override", lambda _base: "Rule")
    monkeypatch.setattr(module, "_classify_file", lambda _base, _path: "Navigation")
    payload = _run_classifier_main(module, tmp_path, monkeypatch)
    assert payload["overall"] == "Rule"
    assert payload["files"]["docs/projects/veterinary-medical-records/A.md"] == "Rule"


def test_overall_most_restrictive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module(CLASSIFIER_PATH, "scripts.classify_doc_change")
    paths = ["docs/a.md", "docs/b.md", "docs/c.md"]
    by_path = {
        "docs/a.md": "Navigation",
        "docs/b.md": "Clarification",
        "docs/c.md": "Rule",
    }
    monkeypatch.setattr(module, "_changed_markdown_files", lambda _base: paths)
    monkeypatch.setattr(module, "_commit_tag_override", lambda _base: None)
    monkeypatch.setattr(module, "_classify_file", lambda _base, path: by_path[path])
    payload = _run_classifier_main(module, tmp_path, monkeypatch)
    assert payload["overall"] == "Rule"


def test_run_git_uses_utf8_decoding(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module(CLASSIFIER_PATH, "scripts.classify_doc_change")
    calls: list[dict[str, Any]] = []

    def _fake_run(cmd: list[str], **kwargs: Any) -> SimpleNamespace:
        calls.append(kwargs)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(module.subprocess, "run", _fake_run)
    assert module._run_git(["git", "status"], "x") == ""
    assert calls
    assert calls[0]["encoding"] == "utf-8"
    assert calls[0]["errors"] == "replace"
    assert calls[0]["cwd"] == module.REPO_ROOT


def test_run_git_raises_on_non_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module(CLASSIFIER_PATH, "scripts.classify_doc_change")
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=2, stdout="", stderr="boom"),
    )
    with pytest.raises(RuntimeError, match="boom"):
        module._run_git(["git", "status"], "x")


def test_changed_markdown_files_filters_and_deduplicates(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module(CLASSIFIER_PATH, "scripts.classify_doc_change")
    outputs = iter(
        [
            "docs/a.md\nfrontend/src/App.tsx\ndocs\\nested\\b.md\n",
            "docs/a.md\n",
            "README.md\n",
        ]
    )
    monkeypatch.setattr(module, "_run_git", lambda *_args, **_kwargs: next(outputs))
    assert module._changed_markdown_files("BASE") == ["docs/a.md", "docs/nested/b.md"]


def test_commit_tag_override_priority(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module(CLASSIFIER_PATH, "scripts.classify_doc_change")
    monkeypatch.setattr(
        module,
        "_run_git",
        lambda *_args, **_kwargs: "feat: x [doc:clar]\nchore: y [doc:rule]\n",
    )
    assert module._commit_tag_override("BASE") == "Rule"


def test_commit_tag_override_none(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module(CLASSIFIER_PATH, "scripts.classify_doc_change")
    monkeypatch.setattr(module, "_run_git", lambda *_args, **_kwargs: "regular commit")
    assert module._commit_tag_override("BASE") is None


def test_changed_added_lines_ignores_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module(CLASSIFIER_PATH, "scripts.classify_doc_change")
    monkeypatch.setattr(
        module,
        "_run_git",
        lambda *_args, **_kwargs: "--- a/docs/a.md\n+++ b/docs/a.md\n+line1\n context\n+line2\n",
    )
    assert module._changed_added_lines("BASE", "docs/a.md") == ["line1", "line2"]


def test_overall_classification_prefers_clarification() -> None:
    module = _load_module(CLASSIFIER_PATH, "scripts.classify_doc_change")
    assert module._overall_classification(["Navigation", "Clarification"]) == "Clarification"


def test_main_fail_closed_on_no_changed_docs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load_module(CLASSIFIER_PATH, "scripts.classify_doc_change")
    monkeypatch.setattr(module, "_changed_markdown_files", lambda _base: [])
    payload = _run_classifier_main(module, tmp_path, monkeypatch)
    assert payload["overall"] == "Rule"
    assert payload["files"] == {}


def test_script_entrypoint_executes_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["classify_doc_change.py", "--base-ref", "BASE"])

    def _fake_run(cmd: list[str], **_kwargs: Any) -> SimpleNamespace:
        # branch/local/staged diffs + commit log + per-file diff
        if cmd[:3] == ["git", "diff", "--name-only"]:
            return SimpleNamespace(returncode=0, stdout="docs/a.md\n", stderr="")
        if cmd[:3] == ["git", "log", "--format=%B"]:
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        return SimpleNamespace(returncode=0, stdout="+just text\n", stderr="")

    monkeypatch.setattr(subprocess, "run", _fake_run)
    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path(str(CLASSIFIER_PATH), run_name="__main__")
    assert exc_info.value.code == 0
    payload = json.loads((tmp_path / "doc_change_classification.json").read_text(encoding="utf-8"))
    assert payload["overall"] == "Clarification"


def test_navigation_skips_guard(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module(DOC_SYNC_GUARD_PATH, "doc_sync_guard_nav")
    result = _run_doc_sync_main(
        module,
        tmp_path,
        monkeypatch,
        changed_files=["docs/projects/veterinary-medical-records/A.md"],
        rules=[
            {
                "doc_glob": "docs/projects/veterinary-medical-records/*.md",
                "required_any": ["backend/tests/unit/test_doc_updates_contract.py"],
            }
        ],
        classification="Navigation",
    )
    assert result == 0


def test_clarification_relaxes_required(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module(DOC_SYNC_GUARD_PATH, "doc_sync_guard_clarification")
    result = _run_doc_sync_main(
        module,
        tmp_path,
        monkeypatch,
        changed_files=[
            "docs/projects/veterinary-medical-records/A.md",
            "docs/agent_router/04_PROJECT/A/00_entry.md",
        ],
        rules=[
            {
                "doc_glob": "docs/projects/veterinary-medical-records/*.md",
                "required_any": ["backend/tests/unit/test_doc_updates_contract.py"],
                "owner_any": ["docs/agent_router/04_PROJECT/**/*.md"],
            },
            {"doc_glob": "docs/agent_router/**/*.md"},
        ],
        classification="Clarification",
    )
    assert result == 0


def test_rule_full_enforcement(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module(DOC_SYNC_GUARD_PATH, "doc_sync_guard_rule")
    result = _run_doc_sync_main(
        module,
        tmp_path,
        monkeypatch,
        changed_files=[
            "docs/projects/veterinary-medical-records/A.md",
            "docs/agent_router/04_PROJECT/A/00_entry.md",
        ],
        rules=[
            {
                "doc_glob": "docs/projects/veterinary-medical-records/*.md",
                "required_any": ["backend/tests/unit/test_doc_updates_contract.py"],
                "owner_any": ["docs/agent_router/04_PROJECT/**/*.md"],
            }
        ],
        classification="Rule",
    )
    assert result == 1


def test_missing_classification_full_check(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module(DOC_SYNC_GUARD_PATH, "doc_sync_guard_missing_classification")
    result = _run_doc_sync_main(
        module,
        tmp_path,
        monkeypatch,
        changed_files=[
            "docs/projects/veterinary-medical-records/A.md",
            "docs/agent_router/04_PROJECT/A/00_entry.md",
        ],
        rules=[
            {
                "doc_glob": "docs/projects/veterinary-medical-records/*.md",
                "required_any": ["backend/tests/unit/test_doc_updates_contract.py"],
                "owner_any": ["docs/agent_router/04_PROJECT/**/*.md"],
            }
        ],
        classification=None,
    )
    assert result == 1
