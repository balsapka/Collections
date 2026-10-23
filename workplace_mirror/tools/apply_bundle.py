"""Apply a mirror bundle (.md) to the workplace repo — safely.

Run from the workplace repo root:

    python docs/mirror_bundles/apply_bundle.py docs/mirror_bundles/<bundle>.md --check
        -> dry run, changes nothing. Must end with "CHECK PASSED".
    python docs/mirror_bundles/apply_bundle.py docs/mirror_bundles/<bundle>.md --apply
        -> writes the files, verifies them, compiles and imports every touched module.
           Must end with "APPLY PASSED".
    python docs/mirror_bundles/apply_bundle.py docs/mirror_bundles/<bundle>.md --revert
        -> puts every touched file back the way it was before --apply (uncommitted work only).

Safety rules:
  * every file the bundle replaces or deletes must be byte-identical (line endings aside) to
    the version the bundle was built from; otherwise nothing is written and the diff is
    printed. Someone else's edits are never overwritten.
  * refuses to write on main/master, or when a touched file has uncommitted changes.
  * the bundle carries a SHA-256 for every block, so a damaged copy (rendered instead of raw
    markdown, smart quotes, lost lines) is detected before anything is written.

Options: --no-import skips the import check (e.g. outside the dev container).
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import os
import pathlib
import re
import subprocess
import sys

APPLY_VERSION = 1
PROTECTED_BRANCHES = {"main", "master"}
FENCE = re.compile(r"^(`{5,})")


def _norm(text: str) -> str:
    return text.replace("\r\n", "\n")


def _sha(text: str) -> str:
    return hashlib.sha256(_norm(text).encode("utf-8")).hexdigest()


def _read(path: pathlib.Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_bytes().decode("utf-8")


# ── Parsing ──────────────────────────────────────────────────────────────────


def parse_bundle(md: str) -> list[dict]:
    """Return one dict per file: path, action, base/new sha and text."""
    lines = _norm(md).split("\n")
    entries, i = [], 0
    while i < len(lines):
        m = re.match(r"^### FILE: `([^`]+)`\s*$", lines[i])
        if not m:
            i += 1
            continue
        meta = lines[i + 1]
        entry = {
            "path": m.group(1),
            "action": re.search(r"action: (add|replace|delete)", meta).group(1),
            "base_sha": None,
            "new_sha": None,
            "base": None,
            "new": None,
        }
        for kind in ("base", "new"):
            sm = re.search(kind + r" sha256 `([0-9a-f]{64})`", meta)
            if sm:
                entry[kind + "_sha"] = sm.group(1)
        j = i + 2
        for kind in ("base", "new"):
            if entry[kind + "_sha"] is None:
                continue
            while not FENCE.match(lines[j]):
                j += 1
            fence = FENCE.match(lines[j]).group(1)
            k = j + 1
            while lines[k] != fence:
                k += 1
            body = "\n".join(lines[j + 1 : k])
            if re.search(kind + r" trailing newline: yes", meta) and body:
                body += "\n"
            entry[kind] = body
            j = k + 1
        entries.append(entry)
        i = j
    return entries


def verify_bundle(entries: list[dict]) -> list[str]:
    errors = []
    for e in entries:
        for kind in ("base", "new"):
            if e[kind + "_sha"] and _sha(e[kind]) != e[kind + "_sha"]:
                errors.append(f"{e['path']}: {kind} block does not match its checksum")
    return errors


# ── Git guards ───────────────────────────────────────────────────────────────


def _git(*args: str) -> str | None:
    try:
        return subprocess.run(
            ["git", *args], capture_output=True, text=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def _head_version(path: str) -> str | None:
    """The committed (HEAD) content of a file, byte-exact, or None."""
    try:
        out = subprocess.run(
            ["git", "show", f"HEAD:{path}"], capture_output=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.decode("utf-8")


def git_problems(entries: list[dict]) -> list[str]:
    problems = []
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    if branch is not None:
        branch = branch.strip()
    if branch is None:
        print("note: not a git repository (or git missing) — branch checks skipped")
        return problems
    if branch in PROTECTED_BRANCHES:
        problems.append(
            f"you are on '{branch}' — create a branch first: git checkout -b <name>"
        )
    # Files already in their final state may be uncommitted (applied, not yet committed).
    pending = [e["path"] for e in entries if file_status(e) != "done"]
    dirty = _git("status", "--porcelain", "--", *pending) if pending else ""
    for line in (dirty or "").splitlines():
        if line[:2] != "??":  # untracked files are compared by content below
            problems.append(f"uncommitted change in a touched file: {line[3:]}")
    return problems


# ── Status ───────────────────────────────────────────────────────────────────


def file_status(e: dict) -> str:
    """One of: todo, done, conflict."""
    current = _read(pathlib.Path(e["path"]))
    cur_sha = None if current is None else _sha(current)
    if e["action"] == "add":
        if current is None:
            return "todo"
        return "done" if cur_sha == e["new_sha"] else "conflict"
    if e["action"] == "replace":
        if cur_sha == e["base_sha"]:
            return "todo"
        return "done" if cur_sha == e["new_sha"] else "conflict"
    # delete
    if current is None:
        return "done"
    return "todo" if cur_sha == e["base_sha"] else "conflict"


def explain_conflict(e: dict) -> None:
    current = _read(pathlib.Path(e["path"]))
    print(f"\n--- CONFLICT: {e['path']} ({e['action']})")
    if e["action"] == "add":
        print("    the file already exists with different content; the bundle would add it.")
        expected, label = e["new"], "bundle (new)"
    else:
        expected, label = e["base"], "bundle base (as photographed)"
        if current is None:
            print("    the file does not exist in this repo.")
            return
    diff = list(
        difflib.unified_diff(
            _norm(expected).splitlines(),
            _norm(current or "").splitlines(),
            fromfile=label,
            tofile="this repo",
            lineterm="",
            n=1,
        )
    )
    for line in diff[:80]:
        print("    " + line)
    if len(diff) > 80:
        print(f"    ... {len(diff) - 80} more diff lines")


def print_table(entries: list[dict], statuses: list[str]) -> None:
    word = {"todo": "will apply", "done": "already applied", "conflict": "CONFLICT"}
    width = max(len(e["path"]) for e in entries)
    for e, s in zip(entries, statuses):
        print(f"  {e['action']:<8} {e['path']:<{width}}  {word[s]}")


# ── Post-apply checks ────────────────────────────────────────────────────────


def _module_name(path: str) -> str | None:
    p = pathlib.PurePosixPath(path)
    if p.suffix != ".py" or p.parts[0] != "src":
        return None
    parts = list(p.with_suffix("").parts[1:])
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def compile_and_import(entries: list[dict], do_import: bool) -> list[str]:
    failures = []
    existing = [e for e in entries if e["action"] != "delete" and e["path"].endswith(".py")]
    for e in existing:
        try:
            compile(_read(pathlib.Path(e["path"])), e["path"], "exec")
        except SyntaxError as exc:
            failures.append(f"compile: {e['path']}: {exc}")
    if not do_import or failures:
        return failures
    modules = [m for m in (_module_name(e["path"]) for e in existing) if m]
    if pathlib.Path("src/enbd_collections/pipeline_registry.py").is_file():
        modules.append("enbd_collections.pipeline_registry")
    env = dict(os.environ)
    env["PYTHONPATH"] = "src" + os.pathsep + env.get("PYTHONPATH", "")
    for mod in dict.fromkeys(modules):
        r = subprocess.run(
            [sys.executable, "-c", f"import {mod}"],
            capture_output=True,
            text=True,
            env=env,
        )
        if r.returncode != 0:
            last = (r.stderr.strip().splitlines() or ["?"])[-1]
            failures.append(f"import: {mod}: {last}")
    return failures


# ── Commands ─────────────────────────────────────────────────────────────────


def cmd_check(entries: list[dict], quiet: bool = False) -> bool:
    statuses = [file_status(e) for e in entries]
    problems = git_problems(entries)
    if not quiet:
        print_table(entries, statuses)
    for e, s in zip(entries, statuses):
        if s == "conflict":
            explain_conflict(e)
    for p in problems:
        print("REFUSED: " + p)
    n_conflict = statuses.count("conflict")
    ok = n_conflict == 0 and not problems
    print(
        f"\n{statuses.count('todo')} to apply, {statuses.count('done')} already applied, "
        f"{n_conflict} conflicts"
    )
    print("CHECK PASSED" if ok else "CHECK FAILED — nothing was written")
    if n_conflict:
        print(
            "A conflict means this repo's file differs from the version the bundle was "
            "built from. Do NOT hand-edit to force it: send the diff above back so the "
            "bundle can be rebuilt."
        )
    return ok


def cmd_apply(entries: list[dict], do_import: bool) -> bool:
    if not cmd_check(entries, quiet=True):
        return False
    for e in entries:
        if file_status(e) != "todo":
            continue
        path = pathlib.Path(e["path"])
        if e["action"] == "delete":
            path.unlink()
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(e["new"].encode("utf-8"))
    bad = [e["path"] for e in entries if file_status(e) != "done"]
    failures = [f"not in the expected final state: {p}" for p in bad]
    failures += compile_and_import(entries, do_import)
    for f in failures:
        print("FAILED " + f)
    if failures:
        print("APPLY FAILED — undo with --revert, then send the messages above back")
        return False
    print(f"{len(entries)} files in their new state, compile OK"
          + (", imports OK" if do_import else " (imports skipped)"))
    print("APPLY PASSED — review with `git status` / `git diff`, then commit")
    return True


def cmd_revert(entries: list[dict]) -> bool:
    skipped = []
    for e in entries:
        path = pathlib.Path(e["path"])
        current = _read(path)
        cur_sha = None if current is None else _sha(current)
        if e["action"] == "add":
            if cur_sha == e["new_sha"]:
                path.unlink()
                for parent in path.parents:
                    if parent == pathlib.Path(".") or any(parent.iterdir()):
                        break
                    parent.rmdir()
            elif current is not None:
                skipped.append(e["path"])
        elif cur_sha == e["new_sha"] or (e["action"] == "delete" and current is None):
            # prefer the committed bytes (keeps the repo's own line endings)
            committed = _head_version(e["path"])
            restore = committed if committed and _sha(committed) == e["base_sha"] else e["base"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(restore.encode("utf-8"))
        elif cur_sha != e["base_sha"]:
            skipped.append(e["path"])
    for p in skipped:
        print(f"left alone (edited after apply): {p}")
    print("REVERT DONE" if not skipped else "REVERT PARTIAL — see the files above")
    return not skipped


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("bundle")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--revert", action="store_true")
    ap.add_argument("--no-import", action="store_true")
    args = ap.parse_args()

    md = pathlib.Path(args.bundle).read_text(encoding="utf-8")
    need = re.search(r"apply_bundle version: (\d+)", md)
    if need and int(need.group(1)) > APPLY_VERSION:
        print(f"This bundle needs apply_bundle.py version {need.group(1)}; you have "
              f"{APPLY_VERSION}. Recreate it from the bundle's 'Apply script' section.")
        return 1
    entries = parse_bundle(md)
    if not entries:
        print("No files found — was the raw markdown copied (not the rendered page)?")
        return 1
    errors = verify_bundle(entries)
    if errors:
        for err in errors:
            print("DAMAGED: " + err)
        print("The bundle copy is damaged — recopy the RAW file. Nothing was written.")
        return 1
    if not pathlib.Path("src").is_dir():
        print("Run this from the workplace repo root (no src/ folder here).")
        return 1
    print(f"{len(entries)} files in bundle, all checksums OK\n")
    if args.check:
        ok = cmd_check(entries)
    elif args.apply:
        ok = cmd_apply(entries, do_import=not args.no_import)
    else:
        ok = cmd_revert(entries)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
