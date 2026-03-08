#!/usr/bin/env python3
"""Generate router mini-files from canonical documentation sources.

Reads docs/agent_router/MANIFEST.yaml and generates token-optimized
router files from canonical documentation.

Usage:
    python scripts/docs/generate-router-files.py          # generate all
    python scripts/docs/generate-router-files.py --check   # CI drift check

Synced in PR-231 merge-conflict follow-up for doc-update guard compliance.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit(
        "PyYAML is required. Install with: pip install pyyaml>=6.0\n"
        "Or: pip install -r requirements-dev.txt"
    )

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "docs" / "agent_router" / "MANIFEST.yaml"

AUTO_HEADER = (
    "<!-- AUTO-GENERATED from canonical source: {source} — DO NOT EDIT -->\n"
    "<!-- To update, edit the canonical source and run: "
    "python scripts/docs/generate-router-files.py -->\n\n"
)


def _format_source_label(source: str) -> str:
    """Return a compact, non-path label for source display in headers.

    Using plain labels avoids leaking direct `docs/...` references into
    operational router modules that must route through `docs/agent_router/*`.
    """
    return Path(source).name


# ── Markdown section parser ──────────────────────────────────────


def _parse_sections(text: str) -> list[dict]:
    """Parse markdown into heading-delimited sections.

    Returns a list of dicts with keys: level, title, content.
    Content includes the heading line itself and all text until the
    next heading at the same or higher level.
    """
    lines = text.split("\n")
    sections: list[dict] = []
    current: dict | None = None

    for line in lines:
        m = re.match(r"^(#{2,4})\s+(.+)$", line)
        if m:
            if current is not None:
                sections.append(current)
            current = {
                "level": len(m.group(1)),
                "title": m.group(2).strip(),
                "content": line + "\n",
            }
        elif current is not None:
            current["content"] += line + "\n"

    if current is not None:
        sections.append(current)

    return sections


def _extract_sections(text: str, titles: list[str] | str) -> str:
    """Extract sections matching the given titles (with nested subsections).

    If titles is "all", returns all sections (stripping preamble/governance).
    """
    sections = _parse_sections(text)

    if titles == "all":
        return "".join(s["content"] for s in sections).rstrip() + "\n"

    result_parts: list[str] = []
    i = 0
    while i < len(sections):
        if sections[i]["title"] in titles:
            parent_level = sections[i]["level"]
            result_parts.append(sections[i]["content"])
            j = i + 1
            while j < len(sections) and sections[j]["level"] > parent_level:
                result_parts.append(sections[j]["content"])
                j += 1
            i = j
        else:
            i += 1

    return "".join(result_parts).rstrip() + "\n"


# ── Generators by entry type ─────────────────────────────────────


def _sort_key(path: str) -> tuple[int, str]:
    """Sort key that handles numeric prefixes (10_ before 100_)."""
    name = Path(path).stem
    m = re.match(r"^(\d+)", name)
    if m:
        return (int(m.group(1)), name)
    return (0, name)


def _generate_content(entry: dict) -> str:
    """Generate a content file by extracting sections from a canonical."""
    source = entry["source"]
    source_path = REPO_ROOT / source
    text = source_path.read_text(encoding="utf-8")

    titles = entry.get("sections", "all")
    content = _extract_sections(text, titles)

    header = AUTO_HEADER.format(source=_format_source_label(source))
    return header + content


def _generate_index(entry: dict, all_outputs: list[dict]) -> str:
    """Generate a 00_entry.md index listing sibling modules."""
    title = entry["title"]
    sources = entry.get("sources", [])
    description = entry.get("description", "")
    subdirectories = entry.get("subdirectories")

    target_dir = str(Path(entry["target"]).parent)
    source_label = (
        ", ".join(_format_source_label(s) for s in sources) if sources else "canonical docs"
    )
    header = AUTO_HEADER.format(source=source_label)

    lines = [header, f"# {title}\n\n"]

    if description:
        lines.append(f"{description}\n\n")

    lines.append(
        "Start with `AGENTS.md` (repo root) and "
        "`docs/agent_router/00_AUTHORITY.md` for intent routing.\n\n"
    )

    if subdirectories:
        lines.append("## Index\n\n")
        for sd in subdirectories:
            lines.append(f"- `docs/agent_router/03_SHARED/{sd['name']}/00_entry.md`\n")
        return "".join(lines)

    # List sibling files in same directory
    siblings = [
        o
        for o in all_outputs
        if str(Path(o["target"]).parent) == target_dir and o["target"] != entry["target"]
    ]
    siblings.sort(key=lambda o: _sort_key(o["target"]))

    if siblings:
        lines.append("## Modules\n\n")
        for s in siblings:
            filename = Path(s["target"]).name
            # Use first section title or filename as label
            sections = s.get("sections", [])
            if isinstance(sections, list) and sections:
                label = sections[0]
            elif s.get("title"):
                label = s["title"]
            elif s.get("sections") == "all":
                # Full-doc extraction — derive label from source filename
                src = s.get("source", "")
                label = Path(src).stem.replace("-", " ").title() if src else filename
            else:
                label = filename
            lines.append(f"- `{filename}` — {label}\n")

    if sources:
        lines.append("\n## Canonical sources\n\n")
        for src in sources:
            lines.append(f"- `{src}`\n")

    return "".join(lines)


def _generate_reference(entry: dict) -> str:
    """Generate a reference/pointer file."""
    title = entry["title"]
    source = entry["source"]
    description = entry.get("description", f"See `{source}`.")

    header = AUTO_HEADER.format(source=_format_source_label(source))
    return f"{header}# {title}\n\n{description}\n\nCanonical source:\n- `{source}`\n"


# ── Main ─────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate router mini-files from canonical docs.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for drift (CI mode): exit 1 if files differ.",
    )
    args = parser.parse_args()

    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    outputs = manifest["outputs"]

    drift_files: list[str] = []
    generated_count = 0

    for entry in outputs:
        target_path = REPO_ROOT / entry["target"]
        entry_type = entry.get("type", "content")

        if entry_type == "index":
            content = _generate_index(entry, outputs)
        elif entry_type == "reference":
            content = _generate_reference(entry)
        else:
            content = _generate_content(entry)

        if args.check:
            if target_path.exists():
                current = target_path.read_text(encoding="utf-8")
                if current != content:
                    drift_files.append(entry["target"])
            else:
                drift_files.append(f"{entry['target']} (missing)")
        else:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content, encoding="utf-8")
            generated_count += 1

    if args.check:
        if drift_files:
            print("Router drift detected in:")
            for f in drift_files:
                print(f"  {f}")
            print("\nRun: python scripts/docs/generate-router-files.py")
            return 1
        print("Router files are in sync with canonical sources.")
        return 0

    print(f"Generated {generated_count} router files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
