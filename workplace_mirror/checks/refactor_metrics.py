"""Code metrics of the crx_persona files, per file and per tier (refactor PLAN §5).

    python workplace_mirror/checks/refactor_metrics.py [OUT_DIR]

Writes ``metrics.json`` and ``metrics.md`` to OUT_DIR (default
``refactor_review/00_baseline``). Per file: lines; docstring and comment share (of the
non-blank lines); functions over 40 lines; maximum nesting (compound statements, a
function body is 1); Spark actions (``.count/.collect/.show/.toPandas/.first/.take(``
calls, not ``F.`` aggregates); the pylint score; the ruff finding count
(``--select F,E,W,I,B,SIM,UP``). Tiers are those of PLAN §2.
"""

import ast
import json
import os
import pathlib
import re
import subprocess
import sys
import tokenize
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[1]
PKG = ROOT / "src/enbd_collections/pipelines/crx_persona"
ACTIONS = {"count", "collect", "show", "toPandas", "first", "take"}
BLOCKS = (
    ast.If,
    ast.For,
    ast.While,
    ast.With,
    ast.Try,
    ast.FunctionDef,
    ast.ClassDef,
    ast.AsyncFunctionDef,
    ast.AsyncFor,
    ast.AsyncWith,
    ast.Match,
)
TIERS = [  # first match wins
    ("X", r"_dcore_codes\.py|b13_check\.py|b14_check\.py"),
    (
        "D",
        r"cc_a2_locatability/(nodes|constants)\.py|rl_a2_locatability/nodes\.py"
        r"|cc_departure_signature/|cc_payment_trajectory/|cc_utilisation/"
        r"|rl_departure_signature/",
    ),
    ("K", r"cc_spell/|rl_spell_table/|rl_a4_spine/|_spine_utils\.py|cc_raw_extract/"),
    ("A", r"cc_a3_payment_credibility/|rl_a3_payment_credibility/"),
    ("L", r".*"),
]


def tier(rel: str) -> str:
    return next(t for t, pattern in TIERS if re.search(pattern, rel))


def _docstring_lines(tree: ast.Module) -> set[int]:
    lines = set()
    for node in ast.walk(tree):
        if isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            first = node.body[0] if node.body else None
            value = getattr(first, "value", None)
            text = getattr(value, "value", None)
            if isinstance(first, ast.Expr) and isinstance(text, str):
                lines |= set(range(first.lineno, first.end_lineno + 1))
    return lines


def _comment_lines(path: pathlib.Path) -> set[int]:
    with path.open() as f:
        tokens = list(tokenize.generate_tokens(f.readline))
    code_lines = {
        t.start[0]
        for t in tokens
        if t.type
        not in (
            tokenize.COMMENT,
            tokenize.NL,
            tokenize.NEWLINE,
            tokenize.INDENT,
            tokenize.DEDENT,
        )
    }
    return {t.start[0] for t in tokens if t.type == tokenize.COMMENT} - code_lines


def _depth(node: ast.AST, level: int = 0) -> int:
    deepest = level
    for child in ast.iter_child_nodes(node):
        deepest = max(deepest, _depth(child, level + isinstance(child, BLOCKS)))
    return deepest


def _actions(tree: ast.Module) -> int:
    return sum(
        1
        for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and n.func.attr in ACTIONS
        and not (
            isinstance(n.func.value, ast.Name) and n.func.value.id in ("F", "functions")
        )
    )


def file_metrics(path: pathlib.Path) -> dict:
    text = path.read_text()
    tree = ast.parse(text)
    non_blank = {i for i, line in enumerate(text.splitlines(), 1) if line.strip()}
    doc, comments = _docstring_lines(tree) & non_blank, _comment_lines(path) & non_blank
    long_funcs = [
        f"{n.name}:{n.end_lineno - n.lineno + 1}"
        for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        and n.end_lineno - n.lineno + 1 > 40
    ]
    return {
        "lines": len(text.splitlines()),
        "doc_comment_share": round(len(doc | comments) / max(len(non_blank), 1), 3),
        "functions_over_40": long_funcs,
        "max_nesting": _depth(tree),
        "spark_actions": _actions(tree),
    }


def pylint_score(path: pathlib.Path) -> float | None:
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    out = subprocess.run(
        [
            sys.executable,
            "-m",
            "pylint",
            "--disable=relative-beyond-top-level",
            str(path),
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    ).stdout
    match = re.search(r"rated at (-?[\d.]+)/10", out)
    return float(match[1]) if match else None


def ruff_counts(paths: list[pathlib.Path]) -> dict[str, int]:
    out = subprocess.run(
        [
            "ruff",
            "check",
            "--select",
            "F,E,W,I,B,SIM,UP",
            "--output-format",
            "json",
            "--no-cache",
            *map(str, paths),
        ],
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    counts: dict[str, int] = {}
    for finding in json.loads(out or "[]"):
        counts[finding["filename"]] = counts.get(finding["filename"], 0) + 1
    return counts


def main() -> None:
    out_dir = (
        pathlib.Path(sys.argv[1])
        if len(sys.argv) > 1
        else ROOT / "refactor_review/00_baseline"
    )
    paths = sorted(PKG.rglob("*.py"))
    with ThreadPoolExecutor(8) as pool:
        scores = dict(zip(paths, pool.map(pylint_score, paths), strict=True))
    ruff = ruff_counts(paths)
    files = {}
    for p in paths:
        rel = str(p.relative_to(PKG))
        files[rel] = {
            "tier": tier(rel),
            **file_metrics(p),
            "pylint": scores[p],
            "ruff_findings": ruff.get(str(p), 0),
        }
    totals = {}
    for t in "LDKAX":
        rows = [m for m in files.values() if m["tier"] == t]
        lines = sum(m["lines"] for m in rows)
        totals[t] = {
            "files": len(rows),
            "lines": lines,
            "doc_comment_share": round(
                sum(m["doc_comment_share"] * m["lines"] for m in rows) / max(lines, 1),
                3,
            ),
            "functions_over_40": sum(len(m["functions_over_40"]) for m in rows),
            "max_nesting": max((m["max_nesting"] for m in rows), default=0),
            "spark_actions": sum(m["spark_actions"] for m in rows),
            "pylint_line_weighted": round(
                sum((m["pylint"] or 0) * m["lines"] for m in rows) / max(lines, 1), 2
            ),
            "ruff_findings": sum(m["ruff_findings"] for m in rows),
        }
    (out_dir / "metrics.json").write_text(
        json.dumps({"files": files, "tiers": totals}, indent=1) + "\n"
    )
    md = [
        "# crx_persona metrics",
        "",
        "Generated by `checks/refactor_metrics.py`. Doc share = docstring + comment",
        "lines of the non-blank lines. Nesting: compound statements, a function body",
        "is 1. Actions: `.count/.collect/.show/.toPandas/.first/.take(` calls (an",
        "action on a Python list or string counts too). Tiers: PLAN §2 (X: read only).",
        "",
        "## Totals per tier",
        "",
        "| Tier | Files | Lines | Doc share | Funcs > 40 | Max nesting"
        " | Actions | Pylint (line-weighted) | Ruff |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for t, m in totals.items():
        md.append(
            f"| {t} | {m['files']} | {m['lines']} | {m['doc_comment_share']:.0%} | "
            f"{m['functions_over_40']} | {m['max_nesting']} | {m['spark_actions']} | "
            f"{m['pylint_line_weighted']} | {m['ruff_findings']} |"
        )
    md += [
        "",
        "## Per file (tiers L, D, A)",
        "",
        "| File | Tier | Lines | Doc share | Funcs > 40 (name:lines) | Nesting"
        " | Actions | Pylint | Ruff |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for rel, m in sorted(
        files.items(), key=lambda kv: ("LDAKX".index(kv[1]["tier"]), kv[0])
    ):
        if m["tier"] in "LDA":
            md.append(
                f"| `{rel}` | {m['tier']} | {m['lines']} | "
                f"{m['doc_comment_share']:.0%} | "
                f"{', '.join(m['functions_over_40']) or '—'} | {m['max_nesting']} | "
                f"{m['spark_actions']} | {m['pylint']} | {m['ruff_findings']} |"
            )
    (out_dir / "metrics.md").write_text("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
