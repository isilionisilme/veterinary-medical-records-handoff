#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path
from urllib.parse import quote

ROOT_README = Path("README.md")
DOCS_README = Path("docs/README.md")
PROJECT_ROOT = Path("docs/projects/veterinary-medical-records")
SHARED_ROOT = Path("docs/shared")
ADR_ROOT = Path("docs/projects/veterinary-medical-records/02-tech/adr")
PROJECT_INDEX_PAGE = "veterinary-medical-records"
PROJECT_INDEX_TITLE = "2026-03-02 Veterinary Medical Records"
TOP_LEVEL_CATEGORIES: tuple[str, ...] = (
    "01-product",
    "02-tech",
    "03-ops",
    "04-delivery",
    "99-archive",
)

_CATEGORY_PURPOSES: dict[str, str] = {
    "01-product": "Defines what we build, for whom, and how it looks.",
    "02-tech": "Defines how the system is built.",
    "03-ops": "Defines how we operate and validate quality.",
    "04-delivery": "Defines what was delivered and how it evolved.",
    "99-archive": "Stores historical or non-canonical material.",
    "adr": "Stores architecture decision records.",
    "plans": "Stores active implementation plans.",
    "completed": "Stores completed plan records.",
}

# Fixed page names for well-known READMEs (avoids stem collisions).
_FIXED_NAMES: dict[str, str] = {
    DOCS_README.as_posix(): "Home",
    ROOT_README.as_posix(): "README",
    f"{PROJECT_ROOT.as_posix()}/README.md": "Project-Overview",
    f"{ADR_ROOT.as_posix()}/README.md": "ADR-Index",
}


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value.strip())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def _collect_sources(repo_root: Path) -> list[Path]:
    sources: list[Path] = []
    if (repo_root / ROOT_README).exists():
        sources.append(ROOT_README)
    if (repo_root / DOCS_README).exists():
        sources.append(DOCS_README)

    for base in (PROJECT_ROOT, SHARED_ROOT):
        base_abs = repo_root / base
        if not base_abs.exists():
            continue
        for path in sorted(base_abs.rglob("*.md")):
            rel = path.relative_to(repo_root)
            if rel.parts[:2] == ("docs", "agent_router"):
                continue
            sources.append(rel)
    return sources


def _build_mapping(sources: list[Path]) -> dict[Path, str]:
    """Map each source doc to a short, unique wiki page name."""
    desired: dict[Path, str] = {}
    for source in sources:
        fixed = _FIXED_NAMES.get(source.as_posix())
        if fixed:
            desired[source] = fixed
        else:
            desired[source] = _slug(source.stem)

    # Disambiguate any remaining collisions by prefixing parent folder.
    counts = Counter(desired.values())
    collisions = {name for name, n in counts.items() if n > 1}
    if collisions:
        for source in list(desired.keys()):
            if desired[source] in collisions:
                parent = _slug(source.parent.name)
                desired[source] = f"{parent}-{_slug(source.stem)}"

    return desired


def _split_anchor(target: str) -> tuple[str, str]:
    if "#" not in target:
        return target, ""
    base, anchor = target.split("#", 1)
    return base, f"#{anchor}"


def _sidebar_link(label: str, page: str, wiki_base_url: str) -> str:
    encoded_page = quote(page, safe="-")
    return f"[{label}]({wiki_base_url}/{encoded_page})"


def _wiki_link(label: str, page: str) -> str:
    return f"[[{page}|{label}]]"


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _shorten_sentence(text: str, max_len: int = 140) -> str:
    cleaned = _normalize_whitespace(text)
    if not cleaned:
        return ""
    if len(cleaned) <= max_len:
        return cleaned
    cutoff = cleaned[:max_len].rsplit(" ", 1)[0]
    return (cutoff or cleaned[:max_len]).rstrip(".,;: ") + "..."


def _extract_page_description(content: str, label: str) -> str:
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", content, flags=re.DOTALL)
    body = content
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        body = content[frontmatter_match.end() :]
        description_match = re.search(
            r"^description\s*:\s*(.+)$", frontmatter, flags=re.MULTILINE | re.IGNORECASE
        )
        if description_match:
            raw = description_match.group(1).strip().strip("\"'")
            if raw:
                return _shorten_sentence(raw)

    paragraph_lines: list[str] = []
    in_code_block = False
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if not line:
            if paragraph_lines:
                break
            continue
        if re.match(r"^\**\s*breadcrumbs\s*:\s*", line, flags=re.IGNORECASE):
            if paragraph_lines:
                break
            continue
        if line.startswith("<!--") or line.endswith("-->"):
            if paragraph_lines:
                break
            continue
        if re.match(r"^[-*_]{3,}$", line):
            if paragraph_lines:
                break
            continue
        if re.match(r"^table of contents\b", line, flags=re.IGNORECASE):
            if paragraph_lines:
                break
            continue
        if line.startswith(("#", "- ", "* ", ">", "|", "!", "[")):
            if paragraph_lines:
                break
            continue
        paragraph_lines.append(line)

    if paragraph_lines:
        return _shorten_sentence(" ".join(paragraph_lines))

    normalized = label.replace("-", " ").strip()
    if normalized:
        return _shorten_sentence(f"Documentation page for {normalized}.")
    return "Documentation page."


def _build_page_descriptions(repo_root: Path, mapping: dict[Path, str]) -> dict[str, str]:
    descriptions: dict[str, str] = {}
    for source, page in mapping.items():
        try:
            content = (repo_root / source).read_text(encoding="utf-8")
        except Exception:
            continue
        descriptions[page] = _extract_page_description(content, source.stem)
    return descriptions


def _page_entry_description(label: str) -> str:
    normalized = label.replace("-", " ").strip()
    if not normalized:
        return "Documentation page."
    return f"Documentation page for {normalized}."


def _rewrite_links(
    content: str, source_rel: Path, mapping: dict[Path, str], repo: str, ref: str
) -> str:
    link_re = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    source_parent = source_rel.parent

    def replace(match: re.Match[str]) -> str:
        text = match.group(1)
        target = match.group(2).strip()

        if not target:
            return match.group(0)
        if target.startswith(("http://", "https://", "mailto:", "#")):
            return match.group(0)

        base_target, anchor = _split_anchor(target)
        normalized = base_target.replace("\\", "/")

        try:
            resolved = (source_parent / normalized).resolve().relative_to(Path.cwd().resolve())
        except Exception:
            return match.group(0)

        resolved = Path(resolved.as_posix())
        if resolved in mapping:
            page = mapping[resolved]
            if anchor:
                return f"[{text}]({page}{anchor})"
            return f"[[{page}|{text}]]"

        blob_target = resolved.as_posix()
        blob_url = f"https://github.com/{repo}/blob/{ref}/{blob_target}{anchor}"
        return f"[{text}]({blob_url})"

    return link_re.sub(replace, content)


def _collect_tree(
    mapping: dict[Path, str],
    root: Path,
) -> dict[str, object]:
    tree: dict[str, object] = {}
    for source, page in mapping.items():
        source_posix = source.as_posix()
        root_posix = root.as_posix().rstrip("/") + "/"
        if not source_posix.startswith(root_posix):
            continue

        rel = source.relative_to(root)
        parts = list(rel.parts)
        if not parts:
            continue

        node: dict[str, object] = tree
        for folder in parts[:-1]:
            child = node.setdefault(folder, {})
            if not isinstance(child, dict):
                child = {}
                node[folder] = child
            node = child

        files = node.setdefault("__files__", [])
        if isinstance(files, list):
            files.append((rel.stem, page))

    return tree


def _render_tree_lines(
    tree: dict[str, object],
    indent: str = "",
    depth: int = 1,
    max_depth: int = 3,
    folder_pages: dict[str, str] | None = None,
    wiki_base_url: str = "",
) -> list[str]:
    """Render a nested tree as indented Markdown list lines.

    *depth* tracks the current nesting level (1-based).  When *depth*
    exceeds *max_depth*, children are suppressed — the user navigates
    to deeper content via the folder's own index page.

    *folder_pages* maps a folder slug (e.g. ``01-product``) to its
    wiki page name so the folder label becomes a clickable link.
    """
    if folder_pages is None:
        folder_pages = {}
    lines: list[str] = []

    files = tree.get("__files__", [])
    if isinstance(files, list):
        for label, page in sorted(files, key=lambda item: item[0].lower()):
            lines.append(f"{indent}- [[{page}|{label}]]")

    folders = [key for key in tree.keys() if key != "__files__"]
    for folder in sorted(folders, key=str.lower):
        page_name = folder_pages.get(folder)
        if page_name:
            lines.append(f"{indent}- {_sidebar_link(folder, page_name, wiki_base_url)}")
        else:
            lines.append(f"{indent}- {folder}")
        child = tree.get(folder)
        if isinstance(child, dict) and depth < max_depth:
            lines.extend(
                _render_tree_lines(
                    child,
                    indent=indent + "  ",
                    depth=depth + 1,
                    max_depth=max_depth,
                    folder_pages=folder_pages,
                    wiki_base_url=wiki_base_url,
                )
            )

    return lines


def _build_sidebar(
    mapping: dict[Path, str],
    wiki_base_url: str,
    project_folder_pages: dict[str, str] | None = None,
    shared_folder_pages: dict[str, str] | None = None,
    shared_top_folders: tuple[str, ...] | None = None,
    max_depth: int = 3,
) -> str:
    project_tree = _collect_tree(mapping, PROJECT_ROOT)
    shared_tree = _collect_tree(mapping, SHARED_ROOT)
    shared_tree_sidebar = {k: v for k, v in shared_tree.items() if k != "__files__"}
    if shared_top_folders:
        for folder in shared_top_folders:
            shared_tree_sidebar.setdefault(folder, {})
    project_tree_sidebar = {k: v for k, v in project_tree.items() if k != "__files__"}

    lines = [
        "## Documentation",
        "",
        "- [[Home]]",
        f"- {_sidebar_link('Shared Documentation', 'Shared', wiki_base_url)}",
    ]
    lines.extend(
        _render_tree_lines(
            shared_tree_sidebar,
            indent="  ",
            depth=2,
            max_depth=2,
            folder_pages=shared_folder_pages or {},
            wiki_base_url=wiki_base_url,
        )
    )

    lines.append("- [[Projects]]")
    lines.append(f"  - {_sidebar_link(PROJECT_INDEX_TITLE, PROJECT_INDEX_PAGE, wiki_base_url)}")
    lines.extend(
        _render_tree_lines(
            project_tree_sidebar,
            indent="    ",
            depth=3,
            max_depth=max_depth,
            folder_pages=project_folder_pages or {},
            wiki_base_url=wiki_base_url,
        )
    )

    lines.append("")
    return "\n".join(lines)


def _build_root_index_page(
    title: str,
    intro: str,
    purpose: str,
    pages: list[tuple[str, str]],
    page_descriptions: dict[str, str] | None = None,
) -> str:
    if page_descriptions is None:
        page_descriptions = {}
    lines = [f"# {title}", "", "## Purpose", "", intro or purpose, "", "## Contents", ""]
    if pages:
        for label, page in pages:
            description = page_descriptions.get(page) or _page_entry_description(label)
            lines.append(f"- [[{page}|{label}]] — {description}")
    else:
        lines.append("- (No pages in this section)")

    lines.extend(
        [
            "",
            "## Governance",
            "",
            "- This page is generated by `scripts/sync_docs_to_wiki.py`.",
            "- Canonical source docs are in `docs/projects/*` and `docs/shared/*`.",
            "",
        ]
    )
    return "\n".join(lines)


def _build_folder_index(
    folder_name: str,
    child_pages: list[tuple[str, str]],
    child_folders: list[str],
    child_folder_contents: dict[str, list[tuple[str, str]]],
    folder_pages: dict[str, str],
    display_title: str | None = None,
    link_categories: bool = True,
    page_descriptions: dict[str, str] | None = None,
) -> str:
    """Auto-generate an index page for a category folder.

    *child_pages* is a list of ``(label, wiki_page_name)`` tuples.
    *child_folders* lists sub-folder names that also have index pages.
    """
    if display_title is not None:
        display = display_title
    elif re.match(r"^\d{2}-", folder_name):
        code, rest = folder_name.split("-", 1)
        display = f"{code} {rest.replace('-', ' ').title()}"
    elif folder_name == "adr":
        display = "ADR"
    else:
        display = folder_name.replace("-", " ").title()

    has_categories = len(child_folders) > 0
    purpose = _CATEGORY_PURPOSES.get(folder_name, "")
    if page_descriptions is None:
        page_descriptions = {}

    lines = [
        f"# {display}",
        "",
        "## Purpose",
        "",
        purpose or "Navigation index for this section.",
        "",
        "## Contents",
        "",
    ]

    if has_categories:
        for cf in sorted(child_folders, key=str.lower):
            page_name = folder_pages.get(cf, cf)
            category_purpose = _CATEGORY_PURPOSES.get(cf, "Shared category documentation.")
            if link_categories:
                lines.append(f"- {_wiki_link(cf, page_name)} — {category_purpose}")
            else:
                lines.append(f"- {cf} — {category_purpose}")

    if child_pages:
        for label, page in sorted(child_pages, key=lambda x: x[0].lower()):
            description = page_descriptions.get(page) or _page_entry_description(label)
            lines.append(f"- [[{page}|{label}]] — {description}")

    if not has_categories and not child_pages:
        lines.append("- (No pages in this section)")

    lines.extend(
        [
            "",
            "## Governance",
            "",
            "- This page is generated by `scripts/sync_docs_to_wiki.py`.",
            f"- Section id: `{folder_name}`.",
            "",
        ]
    )
    return "\n".join(lines)


def _build_project_index(
    mapping: dict[Path, str],
    folder_pages: dict[str, str],
    page_descriptions: dict[str, str] | None = None,
) -> str:
    tree = _collect_tree(mapping, PROJECT_ROOT)

    files = tree.get("__files__", [])
    child_pages = (
        [
            (label, page)
            for label, page in files
            if isinstance(files, list) and page != PROJECT_INDEX_PAGE
        ]
        if isinstance(files, list)
        else []
    )
    child_folders = [key for key in tree if key != "__files__"]
    child_folder_contents: dict[str, list[tuple[str, str]]] = {}
    for cf in child_folders:
        sub = tree.get(cf)
        if not isinstance(sub, dict):
            continue
        sub_files = sub.get("__files__", [])
        docs = list(sub_files) if isinstance(sub_files, list) else []
        if cf == "adr":
            docs = [(label, page) for label, page in docs if label.lower() != "index"]
        child_folder_contents[cf] = sorted(docs, key=lambda x: x[0].lower())

    return _build_folder_index(
        folder_name="veterinary-medical-records",
        child_pages=child_pages,
        child_folders=child_folders,
        child_folder_contents=child_folder_contents,
        folder_pages=folder_pages,
        display_title=PROJECT_INDEX_TITLE,
        page_descriptions=page_descriptions,
    )


def _auto_generate_folder_indices(
    mapping: dict[Path, str],
    root: Path,
    wiki_dir: Path,
    page_prefix: str = "",
    page_descriptions: dict[str, str] | None = None,
) -> dict[str, str]:
    """Walk the tree under *root* and generate wiki index pages for folders.

    Returns a ``{folder_name: wiki_page_name}`` dict so the sidebar can
    render folders as clickable links.

    *page_prefix* is prepended to page names to disambiguate folders that
    exist under both project and shared roots (e.g. ``shared-01-product``).
    """
    tree = _collect_tree(mapping, root)
    folder_pages: dict[str, str] = {}
    _generate_indices_recursive(
        tree,
        wiki_dir,
        folder_pages,
        page_prefix=page_prefix,
        page_descriptions=page_descriptions,
    )
    return folder_pages


def _generate_indices_recursive(
    tree: dict[str, object],
    wiki_dir: Path,
    folder_pages: dict[str, str],
    page_prefix: str = "",
    page_descriptions: dict[str, str] | None = None,
) -> None:
    folders = [k for k in tree if k != "__files__"]
    for folder in folders:
        child = tree[folder]
        if not isinstance(child, dict):
            continue

        # Use folder name with optional technical prefix as the wiki page name.
        page_name = f"{page_prefix}{folder}" if page_prefix else folder
        folder_pages[folder] = page_name

        child_pages: list[tuple[str, str]] = []
        files = child.get("__files__", [])
        if isinstance(files, list):
            child_pages = list(files)
        if folder == "adr":
            child_pages = [(label, page) for label, page in child_pages if label.lower() != "index"]

        child_folders = [k for k in child if k != "__files__"]
        child_folder_contents: dict[str, list[tuple[str, str]]] = {}
        for cf in child_folders:
            sub = child.get(cf)
            if not isinstance(sub, dict):
                continue
            sub_files = sub.get("__files__", [])
            docs = list(sub_files) if isinstance(sub_files, list) else []
            if cf == "adr":
                docs = [(label, page) for label, page in docs if label.lower() != "index"]
            child_folder_contents[cf] = sorted(docs, key=lambda x: x[0].lower())

        _generate_indices_recursive(
            child,
            wiki_dir,
            folder_pages,
            page_prefix=page_prefix,
            page_descriptions=page_descriptions,
        )

        content = _build_folder_index(
            folder,
            child_pages,
            child_folders,
            child_folder_contents,
            folder_pages,
            page_descriptions=page_descriptions,
        )
        page_path = wiki_dir / f"{page_name}.md"
        page_path.parent.mkdir(parents=True, exist_ok=True)
        page_path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync canonical repo docs to a GitHub wiki checkout"
    )
    parser.add_argument("--wiki-dir", required=True, help="Path to cloned wiki repository")
    parser.add_argument("--repo", required=True, help="owner/repo for blob links")
    parser.add_argument("--ref", default="main", help="Git ref used for blob links")
    args = parser.parse_args()

    repo_root = Path.cwd()
    wiki_dir = Path(args.wiki_dir).resolve()
    wiki_dir.mkdir(parents=True, exist_ok=True)

    sources = _collect_sources(repo_root)
    mapping = _build_mapping(sources)
    page_descriptions = _build_page_descriptions(repo_root, mapping)
    page_descriptions.setdefault(
        PROJECT_INDEX_PAGE,
        "Primary index for Veterinary Medical Records project documentation.",
    )

    for source, page in mapping.items():
        content = (repo_root / source).read_text(encoding="utf-8")
        rewritten = _rewrite_links(content, source, mapping, args.repo, args.ref)
        (wiki_dir / f"{page}.md").write_text(rewritten, encoding="utf-8")

    (wiki_dir / "Projects.md").write_text(
        _build_root_index_page(
            "Projects",
            "Human-facing, project-specific documentation hubs.",
            "Contains project root pages for active and historical projects.",
            [(PROJECT_INDEX_TITLE, PROJECT_INDEX_PAGE)],
            page_descriptions=page_descriptions,
        ),
        encoding="utf-8",
    )

    # Auto-generate project category index pages (technical prefixed slugs)
    project_folder_pages = _auto_generate_folder_indices(
        mapping,
        PROJECT_ROOT,
        wiki_dir,
        page_prefix="project-",
        page_descriptions=page_descriptions,
    )
    # Auto-generate shared category index pages (technical prefixed slugs)
    shared_folder_pages = _auto_generate_folder_indices(
        mapping,
        SHARED_ROOT,
        wiki_dir,
        page_prefix="shared-",
        page_descriptions=page_descriptions,
    )
    for folder in TOP_LEVEL_CATEGORIES:
        if folder in shared_folder_pages:
            continue

        page_name = f"shared-{folder}"
        shared_folder_pages[folder] = page_name
        page_path = wiki_dir / f"{page_name}.md"
        page_path.parent.mkdir(parents=True, exist_ok=True)
        page_path.write_text(
            _build_folder_index(
                folder_name=folder,
                child_pages=[],
                child_folders=[],
                child_folder_contents={},
                folder_pages={},
                page_descriptions=page_descriptions,
            ),
            encoding="utf-8",
        )

    # Generate project root page from project tree (canonical wiki index)
    (wiki_dir / f"{PROJECT_INDEX_PAGE}.md").write_text(
        _build_project_index(mapping, project_folder_pages, page_descriptions=page_descriptions),
        encoding="utf-8",
    )

    # Build Shared.md from tree (same category format as project page)
    shared_tree = _collect_tree(mapping, SHARED_ROOT)
    shared_root_files = shared_tree.get("__files__", [])
    shared_child_pages = list(shared_root_files) if isinstance(shared_root_files, list) else []
    shared_child_folders = [k for k in shared_tree if k != "__files__"]
    for folder in TOP_LEVEL_CATEGORIES:
        if folder not in shared_child_folders:
            shared_child_folders.append(folder)
    shared_child_folders = sorted(shared_child_folders, key=str.lower)
    shared_child_folder_contents: dict[str, list[tuple[str, str]]] = {}
    for sf in shared_child_folders:
        sub = shared_tree.get(sf)
        if not isinstance(sub, dict):
            continue
        sub_files = sub.get("__files__", [])
        docs = list(sub_files) if isinstance(sub_files, list) else []
        shared_child_folder_contents[sf] = sorted(docs, key=lambda x: x[0].lower())
    shared_index_body = _build_folder_index(
        folder_name="shared",
        child_pages=shared_child_pages,
        child_folders=shared_child_folders,
        child_folder_contents=shared_child_folder_contents,
        folder_pages=shared_folder_pages,
        display_title="Shared Documentation",
        link_categories=True,
        page_descriptions=page_descriptions,
    )
    (wiki_dir / "Shared.md").write_text(shared_index_body, encoding="utf-8")
    (wiki_dir / "_Sidebar.md").write_text(
        _build_sidebar(
            mapping,
            wiki_base_url=f"https://github.com/{args.repo}/wiki",
            project_folder_pages=project_folder_pages,
            shared_folder_pages=shared_folder_pages,
            shared_top_folders=TOP_LEVEL_CATEGORIES,
            max_depth=3,
        ),
        encoding="utf-8",
    )
    (wiki_dir / "_Footer.md").write_text(
        (
            "Synced automatically from canonical repository docs "
            "(`docs/projects/veterinary-medical-records`, `docs/shared`, and "
            "`README.md`).\n"
        ),
        encoding="utf-8",
    )

    keep = {f"{page}.md" for page in mapping.values()}
    keep.add(f"{PROJECT_INDEX_PAGE}.md")
    keep.update({"Projects.md", "Shared.md", "_Sidebar.md", "_Footer.md"})
    # Keep auto-generated index pages from project and shared categories
    keep.update(f"{page}.md" for page in project_folder_pages.values())
    keep.update(f"{page}.md" for page in shared_folder_pages.values())
    for md_file in wiki_dir.rglob("*.md"):
        rel = md_file.relative_to(wiki_dir).as_posix()
        if rel not in keep:
            md_file.unlink()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
