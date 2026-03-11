#!/usr/bin/env python3
"""Architecture metrics collector for audit automation.

Collects deterministic code metrics and generates:
- tmp/audit/metrics.json  — raw data for AI-assisted analysis
- tmp/audit/metrics-report.md — pre-filled Markdown tables

Usage:
    python scripts/quality/architecture_metrics.py
    python scripts/quality/architecture_metrics.py --baseline 2026-02-23
    python scripts/quality/architecture_metrics.py --check --warn-cc 11 --max-cc 30 --max-loc 500
    python scripts/quality/architecture_metrics.py --check --base-ref main --warn-cc 11
        --max-cc 30 --max-loc 500 --max-loc-growth 50
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_APP = REPO_ROOT / "backend" / "app"
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"
TMP_AUDIT = REPO_ROOT / "tmp" / "audit"

# ── Hexagonal layer config ──────────────────────────────────────────

LAYERS = ("domain", "ports", "application", "infra", "api")
SHARED_MODULES = {"config", "settings"}

# Allowed import directions: source_layer → set of allowed target layers.
ALLOWED_IMPORTS: dict[str, set[str]] = {
    "domain": set(),
    "ports": set(),
    "application": {"domain", "ports"} | SHARED_MODULES,
    "infra": {"domain", "ports"} | SHARED_MODULES,
    "api": {"application", "domain", "ports"} | SHARED_MODULES,
}

# ── Scan patterns ───────────────────────────────────────────────────

SECRET_RE = re.compile(
    r"""(password|secret|api_key|token)\s*=\s*['"][^'"]+['"]""",
    re.IGNORECASE,
)
TODO_RE = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b", re.IGNORECASE)
NOQA_RE = re.compile(r"#\s*noqa", re.IGNORECASE)
LOG_RE = re.compile(r"\blogger\.\w+\(|logging\.\w+\(")
IMPORT_RE = re.compile(r"^from\s+backend\.app\.(\w+)")


# ── Helpers ─────────────────────────────────────────────────────────


def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=REPO_ROOT,
        check=False,
        **kwargs,
    )


def _python_files(root: Path) -> list[Path]:
    return sorted(
        p for p in root.rglob("*.py") if "__pycache__" not in p.parts and ".venv" not in p.parts
    )


def _ts_files(root: Path) -> list[Path]:
    return sorted(
        p for p in root.rglob("*.ts*") if "node_modules" not in p.parts and "dist" not in p.parts
    )


def _rel(p: Path) -> str:
    return str(p.relative_to(REPO_ROOT)).replace("\\", "/")


def _is_backend_app_path(path: str) -> bool:
    return path.startswith("backend/app/")


def _git_output(args: list[str]) -> list[str]:
    result = _run(["git", *args])
    if result.returncode != 0 or not result.stdout:
        return []
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def _changed_backend_python_paths(base_ref: str | None) -> set[str]:
    sources: list[list[str]] = []
    if base_ref:
        sources.append(["diff", "--name-only", f"{base_ref}...HEAD"])
    sources.extend(
        [
            ["diff", "--name-only"],
            ["diff", "--name-only", "--cached"],
        ]
    )

    changed: set[str] = set()
    for args in sources:
        for path in _git_output(args):
            if _is_backend_app_path(path) and path.endswith(".py"):
                changed.add(path)
    return changed


def _base_ref_loc(base_ref: str, rel_path: str) -> int:
    """Count LOC of a file at the given git ref. Returns 0 if not found (new file)."""
    result = _run(["git", "show", f"{base_ref}:{rel_path}"])
    if result.returncode != 0:
        return 0
    return sum(1 for _ in result.stdout.splitlines())


def _layer_of(path: Path) -> str | None:
    """Return the hexagonal layer name for a backend/app file."""
    rel = path.relative_to(BACKEND_APP)
    top = rel.parts[0] if rel.parts else None
    if top in LAYERS:
        return top
    if top in SHARED_MODULES:
        return top
    return None


# ── Collectors ──────────────────────────────────────────────────────


def collect_loc(py_files: list[Path], ts_files: list[Path]) -> dict:
    """Lines of code per file."""
    result: dict[str, int] = {}
    for p in py_files + ts_files:
        try:
            result[_rel(p)] = sum(1 for _ in p.open(encoding="utf-8", errors="replace"))
        except OSError:
            continue

    above_500 = {k: v for k, v in result.items() if v > 500}
    return {
        "files": result,
        "total_files": len(result),
        "above_500_loc": above_500,
        "count_above_500": len(above_500),
    }


def collect_radon_cc(py_files: list[Path]) -> dict:
    """Cyclomatic complexity via radon CLI."""
    cmd = [sys.executable, "-m", "radon", "cc", "-s", "-j", "--"] + [str(p) for p in py_files]
    r = _run(cmd)
    if r.returncode != 0:
        return {"error": f"radon failed: {r.stderr.strip()}", "functions": []}

    try:
        raw: dict = json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"error": "radon output not valid JSON", "functions": []}

    functions: list[dict] = []
    grade_dist: dict[str, int] = defaultdict(int)
    for filepath, blocks in raw.items():
        for b in blocks:
            cc = b.get("complexity", 0)
            grade = _cc_grade(cc)
            grade_dist[grade] += 1
            functions.append(
                {
                    "file": _rel(Path(filepath)),
                    "name": b.get("name", "?"),
                    "lineno": b.get("lineno", 0),
                    "complexity": cc,
                    "grade": grade,
                }
            )

    cc_values = [f["complexity"] for f in functions]
    above_c = [f for f in functions if f["complexity"] >= 11]
    above_e = [f for f in functions if f["complexity"] >= 31]
    above_f = [f for f in functions if f["complexity"] >= 41]

    return {
        "functions": sorted(functions, key=lambda f: -f["complexity"]),
        "total_functions": len(functions),
        "average_cc": round(sum(cc_values) / len(cc_values), 2) if cc_values else 0,
        "max_cc": max(cc_values) if cc_values else 0,
        "grade_distribution": dict(grade_dist),
        "count_above_c": len(above_c),
        "count_above_e": len(above_e),
        "count_above_f": len(above_f),
        "top_10": sorted(functions, key=lambda f: -f["complexity"])[:10],
    }


def _cc_grade(cc: int) -> str:
    if cc <= 5:
        return "A"
    if cc <= 10:
        return "B"
    if cc <= 20:
        return "C"
    if cc <= 30:
        return "D"
    if cc <= 40:
        return "E"
    return "F"


def collect_git_churn(baseline: str | None) -> dict:
    """Commits per file since baseline date."""
    cmd = ["git", "log", "--name-only", "--pretty=format:"]
    if baseline:
        cmd += [f"--since={baseline}"]
    cmd += ["--", "backend/app", "frontend/src"]
    r = _run(cmd)
    if r.returncode != 0:
        return {"error": r.stderr.strip(), "files": {}}

    counts: dict[str, int] = defaultdict(int)
    for line in r.stdout.splitlines():
        line = line.strip()
        if line:
            counts[line.replace("\\", "/")] += 1

    above_8 = {k: v for k, v in counts.items() if v > 8}
    return {
        "files": dict(sorted(counts.items(), key=lambda kv: -kv[1])),
        "count_above_8": len(above_8),
        "above_8": above_8,
    }


def collect_imports(py_files: list[Path]) -> dict:
    """Cross-layer import map and hexagonal violations."""
    import_map: dict[str, list[str]] = defaultdict(list)
    violations: list[dict] = []

    for p in py_files:
        src_layer = _layer_of(p)
        if src_layer is None or src_layer in SHARED_MODULES:
            continue

        try:
            source = p.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(p))
        except (SyntaxError, OSError):
            continue

        for node in ast.walk(tree):
            target_layer = _extract_layer(node)
            if target_layer is None or target_layer == src_layer:
                continue

            edge = f"{src_layer} -> {target_layer}"
            if edge not in import_map[_rel(p)]:
                import_map[_rel(p)].append(edge)

            allowed = ALLOWED_IMPORTS.get(src_layer, set())
            if target_layer not in allowed:
                violations.append(
                    {
                        "file": _rel(p),
                        "line": getattr(node, "lineno", 0),
                        "source_layer": src_layer,
                        "target_layer": target_layer,
                        "edge": edge,
                    }
                )

    return {
        "import_edges": dict(import_map),
        "violations": violations,
        "violation_count": len(violations),
    }


def _extract_layer(node: ast.AST) -> str | None:
    """Extract target layer from an import node like `from backend.app.X...`."""
    if isinstance(node, ast.ImportFrom) and node.module:
        m = IMPORT_RE.match(f"from {node.module}")
        if m:
            target = m.group(1)
            if target in LAYERS or target in SHARED_MODULES:
                return target
    return None


def collect_hotspots(
    loc_data: dict, cc_data: dict, churn_data: dict, import_data: dict
) -> list[dict]:
    """Score files against 4-signal hotspot criteria."""
    all_files: set[str] = set()
    all_files.update(loc_data.get("files", {}).keys())
    all_files.update(churn_data.get("files", {}).keys())

    cc_by_file: dict[str, int] = {}
    for f in cc_data.get("functions", []):
        fp = f["file"]
        cc_by_file[fp] = max(cc_by_file.get(fp, 0), f["complexity"])

    import_count_by_file: dict[str, int] = {}
    for fp, edges in import_data.get("import_edges", {}).items():
        import_count_by_file[fp] = len(edges)

    hotspots: list[dict] = []
    for fp in sorted(all_files):
        loc = loc_data["files"].get(fp, 0)
        cc = cc_by_file.get(fp, 0)
        churn = churn_data["files"].get(fp, 0)
        imports = import_count_by_file.get(fp, 0)

        flags = 0
        signals = []
        if loc > 500:
            flags += 1
            signals.append(f"LOC={loc}")
        if cc > 10:
            flags += 1
            signals.append(f"CC={cc}")
        if imports > 8:
            flags += 1
            signals.append(f"imports={imports}")
        if churn > 8:
            flags += 1
            signals.append(f"churn={churn}")

        if flags >= 2:
            hotspots.append(
                {
                    "file": fp,
                    "loc": loc,
                    "max_cc": cc,
                    "churn": churn,
                    "imports": imports,
                    "flags": flags,
                    "signals": signals,
                    "verdict": "CRITICAL" if flags >= 3 else "HIGH",
                }
            )

    return sorted(hotspots, key=lambda h: -h["flags"])


def collect_pattern_scan(py_files: list[Path], ts_files: list[Path]) -> dict:
    """Scan for secrets, TODOs, NOQAs, and log statements."""
    secrets: list[dict] = []
    todos: list[dict] = []
    noqas: list[dict] = []
    log_count = 0
    log_files: dict[str, int] = defaultdict(int)

    for p in py_files + ts_files:
        try:
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue

        for i, line in enumerate(lines, 1):
            if SECRET_RE.search(line):
                secrets.append({"file": _rel(p), "line": i, "text": line.strip()})
            if TODO_RE.search(line):
                todos.append({"file": _rel(p), "line": i, "text": line.strip()})
            if NOQA_RE.search(line):
                noqas.append({"file": _rel(p), "line": i, "text": line.strip()})
            if p.suffix == ".py" and LOG_RE.search(line):
                log_count += 1
                log_files[_rel(p)] += 1

    return {
        "secrets": secrets,
        "secret_count": len(secrets),
        "todos": todos,
        "todo_count": len(todos),
        "noqas": noqas,
        "noqa_count": len(noqas),
        "log_statements": log_count,
        "log_files": dict(log_files),
        "logger_file_count": len(log_files),
    }


def collect_dependency_check() -> dict:
    """Verify backend imports match declared dependencies."""
    req_path = REPO_ROOT / "backend" / "requirements.txt"
    declared: set[str] = set()
    if req_path.exists():
        for line in req_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-"):
                pkg = re.split(r"[=<>!~]", line)[0].strip().lower().replace("-", "_")
                declared.add(pkg)

    # Scan all top-level imports in backend
    third_party: set[str] = set()
    stdlib = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else set()

    for p in _python_files(BACKEND_APP):
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"), str(p))
        except (SyntaxError, OSError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    if top not in stdlib and not top.startswith("backend"):
                        third_party.add(top.lower().replace("-", "_"))
            elif isinstance(node, ast.ImportFrom) and node.module:
                top = node.module.split(".")[0]
                if top not in stdlib and not top.startswith("backend"):
                    third_party.add(top.lower().replace("-", "_"))

    # Normalize known aliases: pymupdf → fitz
    ALIASES = {"fitz": "pymupdf"}
    normalized = {ALIASES.get(p, p) for p in third_party}
    undeclared = normalized - declared

    return {
        "declared": sorted(declared),
        "imported": sorted(normalized),
        "undeclared": sorted(undeclared),
        "undeclared_count": len(undeclared),
    }


# ── Report generation ───────────────────────────────────────────────


def generate_markdown(data: dict) -> str:
    """Generate pre-filled Markdown report from metrics."""
    lines: list[str] = []
    w = lines.append

    w("# Architecture Metrics Report")
    w("")
    w(f"**Date:** {date.today().isoformat()}")
    if data.get("baseline"):
        w(f"**Baseline:** {data['baseline']}")
    w("**Generated by:** `scripts/quality/architecture_metrics.py`")
    w("")

    # ── Summary
    cc = data.get("radon_cc", {})
    loc = data.get("loc", {})
    imp = data.get("imports", {})
    sc = data.get("pattern_scan", {})
    hs = data.get("hotspots", [])

    w("## Summary")
    w("")
    w("| Metric | Value |")
    w("|--------|-------|")
    w(f"| Total Python files | {loc.get('total_files', '?')} |")
    w(f"| Files > 500 LOC | {loc.get('count_above_500', '?')} |")
    w(f"| Total functions analyzed | {cc.get('total_functions', '?')} |")
    w(f"| Average CC | {cc.get('average_cc', '?')} |")
    w(f"| Max CC | {cc.get('max_cc', '?')} |")
    w(f"| Functions CC ≥ 11 (C+) | {cc.get('count_above_c', '?')} |")
    w(f"| Functions CC ≥ 31 (E+) | {cc.get('count_above_e', '?')} |")
    w(f"| Functions CC ≥ 41 (F) | {cc.get('count_above_f', '?')} |")
    w(f"| Hex violations | {imp.get('violation_count', '?')} |")
    w(f"| Hotspots (≥2 flags) | {len(hs)} |")
    w(f"| Secrets found | {sc.get('secret_count', '?')} |")
    w(f"| TODO/FIXME markers | {sc.get('todo_count', '?')} |")
    w(f"| NOQA suppressions | {sc.get('noqa_count', '?')} |")
    w(f"| Log statements | {sc.get('log_statements', '?')} |")
    w(f"| Logger files | {sc.get('logger_file_count', '?')} |")
    w("")

    # ── Hotspots
    w("## Hotspot Table")
    w("")
    w("| File | LOC | Max CC | Churn | Imports | Flags | Verdict |")
    w("|------|-----|--------|-------|---------|-------|---------|")
    for h in hs:
        w(
            f"| `{h['file']}` | {h['loc']} | {h['max_cc']} "
            f"| {h['churn']} | {h['imports']} | {h['flags']}/4 "
            f"| {'🔴' if h['verdict'] == 'CRITICAL' else '🟠'} {h['verdict']} |"
        )
    w("")

    # ── CC Top 10
    w("## Top 10 Most Complex Functions")
    w("")
    w("| Rank | Function | File | CC | Grade |")
    w("|------|----------|------|----|-------|")
    for i, f in enumerate(cc.get("top_10", []), 1):
        w(f"| {i} | `{f['name']}` | `{f['file']}` | {f['complexity']} | {f['grade']} |")
    w("")

    # ── CC Grade Distribution
    w("## Complexity Grade Distribution")
    w("")
    w("| Grade | CC Range | Count |")
    w("|-------|----------|-------|")
    dist = cc.get("grade_distribution", {})
    for grade, label in [
        ("A", "1-5"),
        ("B", "6-10"),
        ("C", "11-20"),
        ("D", "21-30"),
        ("E", "31-40"),
        ("F", "41+"),
    ]:
        w(f"| {grade} | {label} | {dist.get(grade, 0)} |")
    w("")

    # ── Files > 500 LOC
    w("## Files > 500 LOC")
    w("")
    w("| File | LOC |")
    w("|------|-----|")
    for fp, count in sorted(loc.get("above_500_loc", {}).items(), key=lambda kv: -kv[1]):
        w(f"| `{fp}` | {count} |")
    w("")

    # ── Hex violations
    violations = imp.get("violations", [])
    w("## Hexagonal Violations")
    w("")
    if violations:
        w("| File | Line | Direction | Edge |")
        w("|------|------|-----------|------|")
        for v in violations:
            w(
                f"| `{v['file']}` | {v['line']} "
                f"| {v['source_layer']} → {v['target_layer']} | {v['edge']} |"
            )
    else:
        w("None detected.")
    w("")

    # ── Pattern scan
    w("## Pattern Scan")
    w("")
    w(f"- **Secrets:** {sc.get('secret_count', 0)}")
    for s in sc.get("secrets", []):
        w(f"  - `{s['file']}:{s['line']}`")
    w(f"- **TODO/FIXME:** {sc.get('todo_count', 0)}")
    for t in sc.get("todos", []):
        w(f"  - `{t['file']}:{t['line']}`: {t['text'][:80]}")
    w(f"- **NOQA suppressions:** {sc.get('noqa_count', 0)}")
    for n in sc.get("noqas", []):
        w(f"  - `{n['file']}:{n['line']}`: {n['text'][:80]}")
    w("")

    # ── Dependencies
    deps = data.get("dependencies", {})
    undeclared = deps.get("undeclared", [])
    w("## Dependency Verification")
    w("")
    w(f"- **Declared in requirements.txt:** {len(deps.get('declared', []))}")
    w(f"- **Imported third-party:** {len(deps.get('imported', []))}")
    if undeclared:
        w(f"- **Undeclared:** {', '.join(undeclared)}")
    else:
        w("- **Undeclared:** none")
    w("")

    # ── Churn
    churn = data.get("git_churn", {})
    w("## High-Churn Files (> 8 commits)")
    w("")
    above_8 = churn.get("above_8", {})
    if above_8:
        w("| File | Commits |")
        w("|------|---------|")
        for fp, count in sorted(above_8.items(), key=lambda kv: -kv[1]):
            w(f"| `{fp}` | {count} |")
    else:
        w("None.")
    w("")

    w("---")
    w("")
    w("<!-- AI ASSESSMENT NEEDED: Severity classification, responsibility ")
    w("     analysis, decomposition strategies, narrative, recommendations -->")
    w("")

    return "\n".join(lines)


# ── CI check mode ───────────────────────────────────────────────────


def check_thresholds(
    data: dict,
    max_cc: int,
    max_loc: int,
    warn_cc: int,
    changed_backend_paths: set[str] | None = None,
    base_ref: str | None = None,
    max_loc_growth: int = 50,
) -> tuple[list[str], list[str]]:
    """Return warning and failure lists for backend CI complexity checks."""
    warnings: list[str] = []
    failures: list[str] = []

    cc_data = data.get("radon_cc", {})
    loc_data = data.get("loc", {})

    for f in cc_data.get("functions", []):
        if not _is_backend_app_path(f["file"]):
            continue
        if changed_backend_paths is not None and f["file"] not in changed_backend_paths:
            continue
        complexity = f["complexity"]
        if complexity > max_cc:
            failures.append(
                f"FAIL: CC {complexity} > {max_cc}: {f['name']} in {f['file']}:{f['lineno']}"
            )
        elif complexity >= warn_cc:
            warnings.append(
                f"WARNING: CC {complexity} >= {warn_cc}: {f['name']} in {f['file']}:{f['lineno']}"
            )

    for fp, count in loc_data.get("files", {}).items():
        if not _is_backend_app_path(fp):
            continue
        if changed_backend_paths is not None and fp not in changed_backend_paths:
            continue
        if count > max_loc:
            base_loc = _base_ref_loc(base_ref, fp) if base_ref else 0
            delta = count - base_loc
            if base_loc > max_loc:
                # Pre-existing violation
                if delta > max_loc_growth:
                    failures.append(
                        f"FAIL: LOC {count} (delta +{delta}) > growth cap {max_loc_growth}: {fp}"
                    )
                else:
                    warnings.append(
                        f"WARNING: LOC {count} > {max_loc} (pre-existing, delta +{delta}): {fp}"
                    )
            else:
                # This PR crossed the threshold
                failures.append(f"FAIL: LOC {count} > {max_loc}: {fp}")

    return warnings, failures


# ── Main ────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description="Architecture metrics collector")
    parser.add_argument(
        "--baseline",
        help="Git date (YYYY-MM-DD) for churn analysis (e.g. 2026-02-23)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="CI mode: exit 1 if thresholds exceeded",
    )
    parser.add_argument(
        "--base-ref",
        help="Git base ref or commit used to scope --check to changed backend Python files",
    )
    parser.add_argument(
        "--warn-cc", type=int, default=11, help="Warn CC threshold for --check (default: 11)"
    )
    parser.add_argument("--max-cc", type=int, default=30, help="Max CC for --check (default: 30)")
    parser.add_argument(
        "--max-loc", type=int, default=500, help="Max LOC for --check (default: 500)"
    )
    parser.add_argument(
        "--max-loc-growth",
        type=int,
        default=50,
        help="Max LOC growth allowed in files already above --max-loc (default: 50)",
    )
    parser.add_argument("--json-only", action="store_true", help="Output only JSON, no Markdown")
    args = parser.parse_args()

    print("Collecting architecture metrics...", file=sys.stderr)

    py_files = _python_files(BACKEND_APP)
    ts_files = _ts_files(FRONTEND_SRC)
    print(f"  Found {len(py_files)} Python files, {len(ts_files)} TS/TSX files", file=sys.stderr)

    print("  LOC analysis...", file=sys.stderr)
    loc_data = collect_loc(py_files, ts_files)

    print("  Radon CC analysis...", file=sys.stderr)
    cc_data = collect_radon_cc(py_files)

    print("  Git churn analysis...", file=sys.stderr)
    churn_data = collect_git_churn(args.baseline)

    print("  Import map + hex violations...", file=sys.stderr)
    import_data = collect_imports(py_files)

    print("  Pattern scan (secrets, TODOs, logging)...", file=sys.stderr)
    scan_data = collect_pattern_scan(py_files, ts_files)

    print("  Dependency verification...", file=sys.stderr)
    dep_data = collect_dependency_check()

    print("  Hotspot scoring...", file=sys.stderr)
    hotspots = collect_hotspots(loc_data, cc_data, churn_data, import_data)

    data = {
        "date": date.today().isoformat(),
        "baseline": args.baseline,
        "loc": loc_data,
        "radon_cc": cc_data,
        "git_churn": churn_data,
        "imports": import_data,
        "pattern_scan": scan_data,
        "dependencies": dep_data,
        "hotspots": hotspots,
    }

    # ── CI check mode
    if args.check:
        changed_backend_paths = (
            _changed_backend_python_paths(args.base_ref) if args.base_ref else None
        )
        if changed_backend_paths is not None:
            print(
                f"  Scoped backend Python files: {len(changed_backend_paths)}",
                file=sys.stderr,
            )
            if not changed_backend_paths:
                print("\nSummary: 0 warning(s), 0 failure(s)", file=sys.stderr)
                print("\n✅ No changed backend Python files to evaluate.", file=sys.stderr)
                return 0
        warnings, failures = check_thresholds(
            data,
            args.max_cc,
            args.max_loc,
            args.warn_cc,
            changed_backend_paths,
            base_ref=args.base_ref,
            max_loc_growth=args.max_loc_growth,
        )
        if warnings:
            print(f"\n⚠️  {len(warnings)} warning(s):", file=sys.stderr)
            for warning in warnings:
                print(f"   • {warning}", file=sys.stderr)
        if failures:
            print(f"\n❌ {len(failures)} failure(s):", file=sys.stderr)
            for failure in failures:
                print(f"   • {failure}", file=sys.stderr)
            print(
                f"\nSummary: {len(warnings)} warning(s), {len(failures)} failure(s)",
                file=sys.stderr,
            )
            return 1
        print(f"\nSummary: {len(warnings)} warning(s), {len(failures)} failure(s)", file=sys.stderr)
        print("\n✅ All thresholds passed.", file=sys.stderr)
        return 0

    # ── Output
    TMP_AUDIT.mkdir(parents=True, exist_ok=True)

    json_path = TMP_AUDIT / "metrics.json"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  → {json_path.relative_to(REPO_ROOT)}", file=sys.stderr)

    if not args.json_only:
        md_path = TMP_AUDIT / "metrics-report.md"
        md_path.write_text(generate_markdown(data), encoding="utf-8")
        print(f"  → {md_path.relative_to(REPO_ROOT)}", file=sys.stderr)

    print("\nDone.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
