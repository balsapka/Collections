"""Build a mirror bundle: the workplace_mirror changes between two commits, as one .md file.

    python workplace_mirror/tools/make_bundle.py --base <commit> --slug a1_engine \\
        --title "..." [--head HEAD] [--branch feature/x] [--summary-file f.md] \\
        [--uat-file f.md] [--run-file f.md] [--cleanup-file f.md] [--helper path ...] \\
        [--message "workplace commit message"] [--existing-branch] [--exclude src/path/ ...]

Writes workplace_mirror/bundles/NN_<slug>.md:

* source changes: files under workplace_mirror/src/ and conf/ changed between the two
  commits, at their workplace path; replaced / deleted files carry their base version so
  the workplace side can three-way merge a file that has changed there since;
* helpers (``--helper``, e.g. a PROD check snippet): shipped to the workplace's gitignored
  ``data/input/mirror_bundles/`` — never part of the source, never committed;
* the exact steps on top (UAT: apply, commit src/ + conf/, push; PROD: pull, run the
  bundle's check pipeline), the apply script and a cleanup prompt at the bottom.
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


def changed_files(
    base: str, head: str, exclude: tuple[str, ...] = ()
) -> list[tuple[str, str]]:
    """[(action, workplace_path)] for source files changed between base and head, minus
    the ``exclude`` path prefixes (e.g. transcriptions of files the workplace already has,
    committed meanwhile by another session)."""
    out = _git("diff", "--no-renames", "--name-status", base, head, "--", MIRROR)
    result = []
    for line in out.splitlines():
        status, path = line.split("\t", 1)
        rel = path[len(MIRROR) :]
        if rel.startswith(SOURCE_ROOTS) and not rel.startswith(exclude):
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


def _steps(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    name: str,
    branch: str,
    existing: bool,
    uat_md: str,
    run_md: str,
    message: str,
) -> list[str]:
    """The UAT and PROD steps on top of the bundle.

    ``uat_md`` / ``run_md`` number their own steps: UAT steps from 4, PROD steps from
    6 + the number of UAT steps.
    """
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
    n_uat = uat_md.count("**Step ")
    commit = 4 + n_uat

    def step(n: int, text: str, cmd: str) -> list[str]:
        return [f"**Step {n}.** {text}", "", "```bash", cmd, "```", ""]

    return [
        "## Steps — do these in order, from the workplace repo root",
        "",
        f"The bundle file and the apply script live in `{WORK_DIR}/` (gitignored) and are",
        f"never committed; only `src/` and `conf/` are (step {commit}). Copy each command",
        "block exactly as it is.",
        "",
        "### In UAT",
        "",
        *(
            step(
                1,
                "Continue on the branch of the earlier bundle (nothing uncommitted on it):",
                f"git checkout {branch} && git pull && git status --short",
            )
            if existing
            else step(
                1,
                "Work on a branch (the apply script refuses to run on main):",
                f"git checkout -b {branch}",
            )
        ),
        *step(
            2,
            f"Create the folder, then save this file **raw** (GitHub → Raw → copy all) "
            f"as `{md_path}`:",
            f"mkdir -p {WORK_DIR}",
        ),
        *step(
            3,
            "Write the apply script, apply, and list what changed — must end with "
            "`APPLY PASSED`:",
            f"{extract} && {apply} --apply && git status --short",
        ),
        "A file this repo changed since the bundle's copy (an edit at work, a lint fix) is",
        "merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before",
        "committing.",
        "",
        *([uat_md.strip(), ""] if uat_md.strip() else []),
        *step(
            commit,
            "Commit the source only, and push:",
            f'git add src conf && git commit -m "{message}" && git push'
            + ("" if existing else f" -u origin {branch}"),
        ),
        f"**Undo** (before step {commit}) — puts every touched file back to the last commit:",
        "",
        "```bash",
        f"{apply} --revert",
        "```",
        "",
        "### In PROD",
        "",
        *step(
            commit + 1,
            "Get the branch:",
            f"git fetch origin && git checkout {branch} && git pull",
        ),
        run_md.strip(),
        "",
        "**When you are done**, give the *Cleanup prompt* at the bottom to the workplace",
        "assistant in UAT.",
        "",
    ]


def _cleanup(name: str, extra_md: str) -> list[str]:
    return [
        "## Cleanup prompt",
        "",
        "Copy this to the workplace assistant in UAT once the bundle's PROD checks are done:",
        "",
        "````text",
        f"Clean up after mirror bundle {name}, on the bundle's branch.",
        *([extra_md.strip()] if extra_md.strip() else []),
        f"- Delete the folder {WORK_DIR}/ (bundle file, apply script):",
        f"  rm -rf {WORK_DIR}",
        "- Run `git status`: only the files named above may have changed, nothing under",
        "  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what",
        "  you removed and the hdfs commands the user still has to run in PROD.",
        "````",
        "",
    ]


def _read_optional(path: str | None) -> str:
    return pathlib.Path(path).read_text(encoding="utf-8") if path else ""


def build(args: argparse.Namespace) -> pathlib.Path:  # pylint: disable=too-many-locals
    """Write the bundle .md for ``args`` and return its path."""
    base, head = args.base, args.head
    files = changed_files(base, head, tuple(args.exclude or ()))
    if not files:
        raise SystemExit(f"No src/ or conf/ changes between {base} and {head}.")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    number = len(list(OUT_DIR.glob("[0-9][0-9]_*.md"))) + 1
    name = f"{number:02d}_{args.slug}.md"
    read = _read_optional
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
        f"`{_short(base)}..{_short(head)}`"
        f" · source: {counts['add']} added, {counts['replace']} replaced, "
        f"{counts['delete']} deleted · helpers: {len(helpers)}",
        "",
        *_steps(
            name,
            branch,
            args.existing_branch,
            read(args.uat_file),
            read(args.run_file),
            args.message or f"Mirror bundle {number:02d}: {args.title}",
        ),
        "## What this bundle does",
        "",
        read(args.summary_file).strip() or "_No summary given._",
        "",
        "## Instructions for the workplace assistant",
        "",
        "1. Do not retype or hand-edit code from this file; `apply_bundle.py` writes it.",
        "2. `--apply` must print **APPLY PASSED**. A `MERGED` file differed from the copy",
        "   this bundle was built from; show the user its `git diff` before committing.",
        "3. `DAMAGED` means the markdown copy was altered — recopy the raw file.",
        "4. If an import fails, run `--revert` and report.",
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


def _short(commit: str) -> str:
    return _git("rev-parse", "--short", commit).strip()


def main() -> None:
    """Parse the arguments and build the bundle."""
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
        "--uat-file", default=None, help="UAT steps before the commit (markdown)"
    )
    ap.add_argument(
        "--run-file", default=None, help="PROD run / check steps (markdown)"
    )
    ap.add_argument(
        "--cleanup-file", default=None, help="extra cleanup lines (markdown)"
    )
    ap.add_argument(
        "--helper", action="append", help="file shipped to data/input/mirror_bundles"
    )
    ap.add_argument("--message", default=None, help="workplace commit message")
    ap.add_argument(
        "--exclude",
        action="append",
        help="workplace path prefix to leave out (e.g. another session's transcriptions)",
    )
    ap.add_argument(
        "--existing-branch",
        action="store_true",
        help="continue on --branch (already pushed by an earlier bundle)",
    )
    out = build(ap.parse_args())
    print(f"wrote {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
