from __future__ import annotations

import argparse
import difflib
import os
import sys
from pathlib import Path


def _extract_with_mode(pdf_path: Path, mode: str) -> tuple[str | None, str | None]:
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from backend.app.application.processing_runner import (
        PDF_EXTRACTOR_FORCE_ENV,
        _extract_pdf_text,
    )

    previous = os.environ.get(PDF_EXTRACTOR_FORCE_ENV)
    os.environ[PDF_EXTRACTOR_FORCE_ENV] = mode
    try:
        return _extract_pdf_text(pdf_path), None
    except Exception as exc:  # pragma: no cover - diagnostic script
        return None, f"{type(exc).__name__}: {exc}"
    finally:
        if previous is None:
            os.environ.pop(PDF_EXTRACTOR_FORCE_ENV, None)
        else:
            os.environ[PDF_EXTRACTOR_FORCE_ENV] = previous


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run A/B PDF text extraction with fitz vs fallback and write outputs + diff."
    )
    parser.add_argument("pdf", type=Path, help="PDF file path")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("backend/tests/fixtures/pdfs"),
        help="Directory for output snapshots",
    )
    args = parser.parse_args()

    pdf_path = args.pdf.resolve()
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        return 2

    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    fallback_text, fallback_error = _extract_with_mode(pdf_path, "fallback")
    fitz_text, fitz_error = _extract_with_mode(pdf_path, "fitz")

    stem = pdf_path.stem
    fallback_path = out_dir / f"{stem}.fallback.txt"
    fitz_path = out_dir / f"{stem}.fitz.txt"
    diff_path = out_dir / f"{stem}.fitz-vs-fallback.diff.txt"

    if fallback_text is not None:
        fallback_path.write_text(fallback_text, encoding="utf-8")
        print(f"fallback: ok ({len(fallback_text)} chars) -> {fallback_path}")
    else:
        print(f"fallback: error -> {fallback_error}")

    if fitz_text is not None:
        fitz_path.write_text(fitz_text, encoding="utf-8")
        print(f"fitz: ok ({len(fitz_text)} chars) -> {fitz_path}")
    else:
        print(f"fitz: error -> {fitz_error}")

    if fallback_text is not None and fitz_text is not None:
        diff = difflib.unified_diff(
            fitz_text.splitlines(keepends=True),
            fallback_text.splitlines(keepends=True),
            fromfile=f"{stem}.fitz.txt",
            tofile=f"{stem}.fallback.txt",
        )
        diff_content = "".join(diff)
        diff_path.write_text(diff_content, encoding="utf-8")
        print(f"diff: written -> {diff_path}")
        return 0

    print("diff: skipped (both extractions must succeed)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
