"""Build a mirror bundle: the workplace_mirror changes between two commits, as one .md file.

    python workplace_mirror/tools/make_bundle.py --base <baseline-commit> --slug a1_engine \\
        --title "Extract the shared A1 engine" [--head HEAD] [--branch crx/a1-engine] \\
        [--summary-file notes.md]

Writes workplace_mirror/bundles/NN_<slug>.md. Only files under workplace_mirror/src/,
conf/ and docs/ are bundled; their path inside the bundle is the workplace repo path
(src/..., conf/...). Every replaced or deleted file carries its base version, so the
workplace side can refuse to touch a file that differs from what was photographed.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import pathlib
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[2]
MIRROR = "workplace_mirror/"
BUNDLED_ROOTS = ("src/", "conf/", "docs/")
OUT_DIR = REPO / "workplace_mirror" / "bundles"
APPLY = pathlib.Path(__file__).with_name("apply_bundle.py")
LANG = {".py": "python", ".yml": "yaml", ".yaml": "yaml", ".md": "markdown"}
WORKPLACE_DIR = "docs/mirror_bundles"


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), *args], capture_output=True, text=True, check=True
    ).stdout


def _show(ref: str, path: str) -> str:
    return _git("show", f"{ref}:{path}")


def _sha(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def _fence(text: str) -> str:
    fence = "`````"
    while any(line.startswith(fence) for line in text.split("\n")):
        fence += "`"
    return fence


def _block(text: str, lang: str) -> list[str]:
    fence = _fence(text)
    body = text[:-1] if text.endswith("\n") else text
    return [f"{fence}{lang}", body, fence]


def changed_files(base: str, head: str) -> list[tuple[str, str]]:
    """[(action, workplace_path)] for bundled files changed between base and head."""
    out = _git("diff", "--no-renames", "--name-status", base, head, "--", MIRROR)
    result = []
    for line in out.splitlines():
        status, path = line.split("\t", 1)
        rel = path[len(MIRROR):]
        if not rel.startswith(BUNDLED_ROOTS):
            continue
        action = {"A": "add", "M": "replace", "D": "delete"}[status[0]]
        result.append((action, rel))
    return sorted(result, key=lambda x: ({"delete": 2}.get(x[0], 1), x[1]))


def build(base: str, head: str, slug: str, title: str, branch: str, summary: str) -> pathlib.Path:
    files = changed_files(base, head)
    if not files:
        raise SystemExit(f"No changes under {MIRROR}src|conf between {base} and {head}.")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    number = len(list(OUT_DIR.glob("[0-9][0-9]_*.md"))) + 1
    name = f"{number:02d}_{slug}.md"
    base_sha = _git("rev-parse", "--short", base).strip()
    head_sha = _git("rev-parse", "--short", head).strip()
    apply_src = APPLY.read_text(encoding="utf-8")
    apply_version = next(
        line.split("=")[1].strip()
        for line in apply_src.splitlines()
        if line.startswith("APPLY_VERSION")
    )
    bundle_path = f"{WORKPLACE_DIR}/{name}"
    run = f"python {WORKPLACE_DIR}/apply_bundle.py {bundle_path}"

    counts = {a: sum(1 for x, _ in files if x == a) for a in ("add", "replace", "delete")}
    md: list[str] = [
        f"# Mirror bundle {number:02d} — {title}",
        "",
        f"apply_bundle version: {apply_version} · built {datetime.date.today()} from "
        f"`{base_sha}..{head_sha}` · {counts['add']} added, {counts['replace']} replaced, "
        f"{counts['delete']} deleted",
        "",
        summary.strip() or "_No summary given._",
        "",
        "## Run this (from the workplace repo root)",
        "",
        "```bash",
        f"git checkout -b {branch}            # never apply on main",
        f"# save this file RAW as {bundle_path}",
        f"# first time / version bump only: create {WORKPLACE_DIR}/apply_bundle.py "
        "from the 'Apply script' section",
        f"{run} --check     # dry run -> CHECK PASSED",
        f"{run} --apply     # writes + compile + imports -> APPLY PASSED",
        "git status && git diff --stat",
        f'git add -A src conf docs && git commit -m "Mirror bundle {number:02d}: {title}"',
        "```",
        "",
        f"Undo before committing: `{run} --revert`. After committing: `git revert <commit>`.",
        "",
        "## Instructions for the workplace assistant",
        "",
        "1. **Do not retype or hand-edit code from this file.** Save it raw (GitHub \"Copy raw "
        "file\", not the rendered page) and let `apply_bundle.py` write the files.",
        "2. `--check` must print **CHECK PASSED**. If it prints CONFLICT, the workplace file "
        "differs from the version this bundle was built from: stop, and give the printed diff "
        "to the user. Do not edit files to make the check pass.",
        "3. `DAMAGED` means the markdown copy was altered — recopy the raw file.",
        "4. `--apply` must print **APPLY PASSED**. If an import fails, run `--revert` and report "
        "the message.",
        "5. Touch nothing outside the files listed in the manifest.",
        "",
        "## Manifest",
        "",
        "| Action | Path |",
        "|---|---|",
        *[f"| {a} | `{p}` |" for a, p in files],
        "",
        "## Files",
        "",
    ]
    for action, rel in files:
        lang = LANG.get(pathlib.PurePosixPath(rel).suffix, "")
        base_txt = _show(base, MIRROR + rel) if action != "add" else None
        new_txt = _show(head, MIRROR + rel) if action != "delete" else None
        meta = [f"action: {action}"]
        for kind, txt in (("base", base_txt), ("new", new_txt)):
            if txt is not None:
                meta.append(f"{kind} sha256 `{_sha(txt)}`")
                meta.append(f"{kind} trailing newline: {'yes' if txt.endswith(chr(10)) else 'no'}")
        md += [f"### FILE: `{rel}`", " · ".join(meta), ""]
        if base_txt is not None:
            md += ["Base (as photographed — used only for the safety check and --revert):", ""]
            md += _block(base_txt, lang) + [""]
        if new_txt is not None:
            md += ["New:", ""]
            md += _block(new_txt, lang) + [""]

    md += [
        "## Apply script",
        "",
        f"Save as `{WORKPLACE_DIR}/apply_bundle.py` (only when missing or older than version "
        f"{apply_version}).",
        "",
        *_block(apply_src, "python"),
        "",
    ]
    out = OUT_DIR / name
    out.write_text("\n".join(md), encoding="utf-8")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", required=True, help="commit the workplace files match today")
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--branch", default=None, help="suggested workplace branch name")
    ap.add_argument("--summary-file", default=None)
    args = ap.parse_args()
    summary = (
        pathlib.Path(args.summary_file).read_text(encoding="utf-8") if args.summary_file else ""
    )
    out = build(
        args.base,
        args.head,
        args.slug,
        args.title,
        args.branch or f"crx/{args.slug.replace('_', '-')}",
        summary,
    )
    print(f"wrote {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
