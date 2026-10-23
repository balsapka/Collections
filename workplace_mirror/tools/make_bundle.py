"""Build a mirror bundle: the workplace_mirror changes between two commits, as one .md file.

    python workplace_mirror/tools/make_bundle.py --base <commit> --slug a1_engine \\
        --title "..." [--head HEAD] [--branch feature/x] [--summary-file f.md] \\
        [--run-file f.md] [--cleanup-file f.md] [--helper path ...]

Writes workplace_mirror/bundles/NN_<slug>.md:

* source changes: files under workplace_mirror/src/ and conf/ changed between the two
  commits, at their workplace path; replaced / deleted files carry their base version so
  the workplace side refuses to touch a file that differs from what was photographed;
* helpers (``--helper``, e.g. a PROD check snippet): shipped to the workplace's gitignored
  ``data/input/mirror_bundles/`` — never part of the source, never committed;
* the exact steps on top, the apply script and a cleanup prompt at the bottom.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import pathlib
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[2]
MIRROR = "workplace_mirror/"
SOURCE_ROOTS = ("src/", "conf/")
OUT_DIR = REPO / "workplace_mirror" / "bundles"
APPLY = pathlib.Path(__file__).with_name("apply_bundle.py")
LANG = {".py": "python", ".yml": "yaml", ".yaml": "yaml", ".md": "markdown"}
WORK_DIR = "data/input/mirror_bundles"  # gitignored in the workplace repo


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), *args], capture_output=True, text=True, check=True
    ).stdout


def _show(ref: str, path: str) -> str:
    return _git("show", f"{ref}:{path}")


def _sha(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def _block(text: str, lang: str) -> list[str]:
    fence = "`````"
    while any(line.startswith(fence) for line in text.split("\n")):
        fence += "`"
    return [f"{fence}{lang}", text[:-1] if text.endswith("\n") else text, fence]


def changed_files(base: str, head: str) -> list[tuple[str, str]]:
    """[(action, workplace_path)] for source files changed between base and head."""
    out = _git("diff", "--no-renames", "--name-status", base, head, "--", MIRROR)
    result = []
    for line in out.splitlines():
        status, path = line.split("\t", 1)
        rel = path[len(MIRROR) :]
        if rel.startswith(SOURCE_ROOTS):
            result.append(({"A": "add", "M": "replace", "D": "delete"}[status[0]], rel))
    return sorted(result, key=lambda x: (x[0] == "delete", x[1]))


def _file_entry(
    rel: str, action: str, base_txt: str | None, new_txt: str | None
) -> list[str]:
    lang = LANG.get(pathlib.PurePosixPath(rel).suffix, "")
    meta = [f"action: {action}"]
    for kind, txt in (("base", base_txt), ("new", new_txt)):
        if txt is not None:
            meta.append(f"{kind} sha256 `{_sha(txt)}`")
            meta.append(
                f"{kind} trailing newline: {'yes' if txt.endswith(chr(10)) else 'no'}"
            )
    md = [f"### FILE: `{rel}`", " · ".join(meta), ""]
    if base_txt is not None:
        md += [
            "Base (as photographed — used only for the safety check and --revert):",
            "",
        ]
        md += _block(base_txt, lang) + [""]
    if new_txt is not None:
        md += ["New:", ""] + _block(new_txt, lang) + [""]
    return md


def _steps(name: str, branch: str, run_md: str) -> list[str]:
    md_path = f"{WORK_DIR}/{name}"
    apply = f"python {WORK_DIR}/apply_bundle.py {md_path}"
    # One line, no heredoc, no backticks: survives copy-paste into bash or zsh.
    extract = (
        'python -c "import pathlib, re; '
        f"d = pathlib.Path('{WORK_DIR}'); "
        f"md = (d / '{name}').read_text(encoding='utf-8'); "
        "sec = md.split('\\n## Apply script\\n', 1)[1]; "
        "m = re.search(r'^(\\x60{5,})python\\n(.*?)\\n\\1$', sec, re.S | re.M); "
        "(d / 'apply_bundle.py').write_text(m.group(2) + '\\n', encoding='utf-8'); "
        "print('apply_bundle.py written')\""
    )

    def step(n: int, text: str, cmd: str) -> list[str]:
        return [f"**Step {n}.** {text}", "", "```bash", cmd, "```", ""]

    return [
        "## Steps — do these in order, from the workplace repo root",
        "",
        f"Everything this bundle adds outside `src/` and `conf/` lives in `{WORK_DIR}/`",
        "(gitignored). Nothing here is committed; commit `src/` and `conf/` only if you",
        "decide to keep the change. Copy each command block exactly as it is.",
        "",
        *step(
            1,
            "Work on a branch (the apply script refuses to run on main):",
            f"git checkout -b {branch}",
        ),
        *step(
            2,
            f"Create the folder, then save this file **raw** (GitHub → Raw → copy all) "
            f"as `{md_path}`:",
            f"mkdir -p {WORK_DIR}",
        ),
        *step(
            3,
            "Write the apply script from the *Apply script* section at the bottom "
            "(prints `apply_bundle.py written`):",
            extract,
        ),
        *step(
            4,
            "Dry run — must end with `CHECK PASSED` (nothing is written):",
            f"{apply} --check",
        ),
        "If step 4 reports a **CONFLICT** for a file nobody edited by hand, the code-only",
        "diff it prints is a transcription slip in the bundle's copy. Re-run step 4, then",
        "step 5, with `--accept <path>` added for that file, e.g.:",
        "",
        "```bash",
        f"{apply} --check --accept src/path/of/the/file.py",
        "```",
        "",
        *step(
            5,
            "Apply — must end with `APPLY PASSED` (add the same `--accept` if you "
            "used one in step 4):",
            f"{apply} --apply",
        ),
        *step(6, "Look at what changed:", "git status && git diff --stat"),
        run_md.strip(),
        "",
        "**Undo** (before any commit) — restores every touched file exactly:",
        "",
        "```bash",
        f"{apply} --revert",
        "```",
        "",
        "**When you are done**, give the *Cleanup prompt* at the bottom to the workplace",
        "assistant (or run its steps yourself).",
        "",
    ]


def _cleanup(name: str, extra_md: str) -> list[str]:
    return [
        "## Cleanup prompt",
        "",
        "Copy this to the workplace assistant once the bundle's checks are done:",
        "",
        "````text",
        f"Clean up after mirror bundle {name}. Leave src/ and conf/ as they are, apart from",
        "any temporary switch a step below asks you to make and undo.",
        *([extra_md.strip()] if extra_md.strip() else []),
        f"- Delete the folder {WORK_DIR}/ (bundle file, apply script, helpers, results):",
        f"  rm -rf {WORK_DIR}",
        "- Run `git status` and confirm nothing under data/input/ is tracked or staged and",
        "  that no other file changed. Report what you deleted.",
        "````",
        "",
    ]


def build(args: argparse.Namespace) -> pathlib.Path:
    base, head = args.base, args.head
    files = changed_files(base, head)
    if not files:
        raise SystemExit(f"No src/ or conf/ changes between {base} and {head}.")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    number = len(list(OUT_DIR.glob("[0-9][0-9]_*.md"))) + 1
    name = f"{number:02d}_{args.slug}.md"
    read = lambda p: pathlib.Path(p).read_text(encoding="utf-8") if p else ""  # noqa: E731
    apply_src = APPLY.read_text(encoding="utf-8")
    version = next(
        ln.split("=")[1].strip()
        for ln in apply_src.splitlines()
        if ln.startswith("APPLY_VERSION")
    )
    helpers = [pathlib.Path(h) for h in args.helper or []]
    counts = {
        a: sum(1 for x, _ in files if x == a) for a in ("add", "replace", "delete")
    }
    branch = args.branch or f"feature/{args.slug}"
    md = [
        f"# Mirror bundle {number:02d} — {args.title}",
        "",
        f"apply_bundle version: {version} · built {datetime.date.today()} from "
        f"`{_git('rev-parse', '--short', base).strip()}..{_git('rev-parse', '--short', head).strip()}`"
        f" · source: {counts['add']} added, {counts['replace']} replaced, "
        f"{counts['delete']} deleted · helpers: {len(helpers)}",
        "",
        *_steps(name, branch, read(args.run_file)),
        "## What this bundle does",
        "",
        read(args.summary_file).strip() or "_No summary given._",
        "",
        "## Instructions for the workplace assistant",
        "",
        "1. Do not retype or hand-edit code from this file; `apply_bundle.py` writes it.",
        "2. `--check` must print **CHECK PASSED**. On CONFLICT the workplace file differs from",
        "   the version this bundle was built from: stop and show the printed diff to the user.",
        "3. `DAMAGED` means the markdown copy was altered — recopy the raw file.",
        "4. `--apply` must print **APPLY PASSED**; if an import fails, run `--revert` and report.",
        f"5. Touch nothing outside the manifest. Never commit `{WORK_DIR}/`.",
        "",
        "## Manifest",
        "",
        "| Action | Path |",
        "|---|---|",
        *[f"| {a} | `{p}` |" for a, p in files],
        *[f"| add (helper) | `{WORK_DIR}/{h.name}` |" for h in helpers],
        "",
        "## Files",
        "",
    ]
    for action, rel in files:
        md += _file_entry(
            rel,
            action,
            _show(base, MIRROR + rel) if action != "add" else None,
            _show(head, MIRROR + rel) if action != "delete" else None,
        )
    for h in helpers:
        md += _file_entry(
            f"{WORK_DIR}/{h.name}", "add", None, h.read_text(encoding="utf-8")
        )
    md += [
        "## Apply script",
        "",
        f"Written to `{WORK_DIR}/apply_bundle.py` by step 3.",
        "",
        *_block(apply_src, "python"),
        "",
        *_cleanup(name, read(args.cleanup_file)),
    ]
    out = OUT_DIR / name
    out.write_text("\n".join(md), encoding="utf-8")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--base", required=True, help="commit the workplace files match today"
    )
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--branch", default=None, help="workplace branch name")
    ap.add_argument("--summary-file", default=None)
    ap.add_argument(
        "--run-file", default=None, help="PROD run / check steps (markdown)"
    )
    ap.add_argument(
        "--cleanup-file", default=None, help="extra cleanup lines (markdown)"
    )
    ap.add_argument(
        "--helper", action="append", help="file shipped to data/input/mirror_bundles"
    )
    out = build(ap.parse_args())
    print(f"wrote {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
