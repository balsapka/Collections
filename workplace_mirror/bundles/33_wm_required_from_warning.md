# Mirror bundle 33 — WM snapshots: required_from warns instead of refusing

apply_bundle version: 7 · built 2026-11-26 from `85b6fc2..bf1684b` · source: 0 added, 1 replaced, 0 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 4). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Work on a branch (the apply script refuses to run on main):

```bash
git checkout -b feature/wm_required_from_warning
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/33_wm_required_from_warning.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '33_wm_required_from_warning.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/33_wm_required_from_warning.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Commit the source only, and push:

```bash
git add src conf && git commit -m "Mirror bundle 33: WM snapshots: required_from warns instead of refusing" && git push -u origin feature/wm_required_from_warning
```

**Undo** (before step 4) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/33_wm_required_from_warning.md --revert
```

### In PROD

**Step 5.** Get the branch:

```bash
git fetch origin && git checkout feature/wm_required_from_warning && git pull
```

**Step 7.** In PROD, after the pull, carry on with bundle 32's step 7 for each model_id (switch `model_id` in `globals_dev.yml` to the pipeline prefix): `casa_b32_snapshot` → `<model_id>.persona_e2e` → `casa_b32_compare`. If `casa_b32_snapshot` already ran for a model_id and `casa_features` did not finish since, don't rerun it.

```bash
kedro run --pipeline=casa_b32_snapshot
```

```bash
kedro run --env=dev --pipeline=<model_id>.persona_e2e
```

```bash
kedro run --pipeline=casa_b32_compare
```

Paste back the `=== B32 CASA OLD NEW START/END ===` block per model_id, and from the `persona_e2e` log each WM table's `weeks <first> to <last>` line, the `weeks start at ... later than the requested month` warnings and any `using adv_load_date=... instead of ...` warning.

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

`WMSnapshotDataset`: `required_from` warns instead of refusing.

WM keeps a rolling history (about two years): the 2026-10-02 partition of `fea_casa_cc_inflow_outflow_by_cif` starts at week 20241001, so with `wm_snapshot_required_from` = 2024-02-01 every partition was refused and `casa_features` stopped. Now a partition whose weeks start after the `required_from` month is used, with a warning (`weeks start at <first>, later than the requested month <yyyyMM>; the months before are empty`). `required_through` still refuses an older snapshot that stops before the run's last month.

One file changes: `src/enbd_collections/datasets/wm_snapshot_dataset.py`. No catalog, globals or registry change. Bundle 32's check pipelines and cleanup stay as they are.

## Instructions for the workplace assistant

1. Do not retype or hand-edit code from this file; `apply_bundle.py` writes it.
2. `--apply` must print **APPLY PASSED**. A `MERGED` file differed from the copy
   this bundle was built from; show the user its `git diff` before committing.
3. `DAMAGED` means the markdown copy was altered — recopy the raw file.
4. If an import fails, run `--revert` and report.
5. Touch nothing outside the manifest. Never commit `data/input/mirror_bundles/`.

## Manifest

| Action | Path |
|---|---|
| replace | `src/enbd_collections/datasets/wm_snapshot_dataset.py` |

## Files

### FILE: `src/enbd_collections/datasets/wm_snapshot_dataset.py`
action: replace · base sha256 `d1ddf86a1a91fd09f7585d338dcc6fdd230244df1bff753d37a3b23e6ca30b95` · base trailing newline: yes · new sha256 `c849a9e274ce508574034145d6ab73a1d8e664d1835533656bb693e225d17145` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Read-only Kedro dataset: one ``adv_load_date`` snapshot of a WM feature table.

WM ``04_feature`` tables are written as ``<root>/adv_load_date=YYYY-MM-DD/``; each
partition is a full-history snapshot (weekly rows in ``week_number``, ``yyyyMM0W``).
The dataset reads one partition, the ``snapshot`` date from globals, and falls back to
another partition when that one is missing or cannot be read. The tables belong to WM,
so a damaged partition cannot be fixed or rebuilt from this repo.

Readable means every byte of the partition comes back: the dataset scans the whole
partition once (Spark's ``noop`` sink) before returning it. HDFS can list a file whose
block no DataNode can serve (``BlockMissingException``), so the listing alone proves
nothing.

Fallback order: newer partitions first (nearest first), then older ones (nearest
first), at most ``max_fallback`` of them. A partition is only used when its
``week_number`` range covers the ``required_from`` and ``required_through`` months (each
optional): an older snapshot that would leave the last months empty, or a partition
without the full history, is refused. When no partition qualifies, the load
fails with the reason for each one tried. A fallback is logged as a warning.

Catalog example::

    wm_fea_casa_eod_avg_balance:
      type: enbd_collections.datasets.wm_snapshot_dataset.WMSnapshotDataset
      filepath: ".../04_feature/fea_casa_eod_avg_bal_by_cif"
      snapshot: "${globals:snapshot_adv_load_date}"
      required_from: "2025-02-01"
      required_through: "${globals:crx_persona.persona_end_date}"
"""

from __future__ import annotations

import logging
import re
from datetime import date
from typing import Any

from kedro.io.core import AbstractDataset, DatasetError
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

logger = logging.getLogger(__name__)


def _date(value: str | None) -> date | None:
    return date.fromisoformat(str(value)) if value else None


def _month(day: date) -> int:
    """``day``'s month as ``yyyyMM``, the leading part of a WM ``week_number``."""
    return day.year * 100 + day.month


# Kedro aliases load / save to _load / _save; there is no base __init__ to call.
# pylint: disable=abstract-method,super-init-not-called,too-many-instance-attributes
# pylint: disable=broad-exception-caught
class WMSnapshotDataset(AbstractDataset[None, DataFrame]):
    """One snapshot partition of a WM table, with fallback to its neighbours."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *,
        filepath: str,
        snapshot: str,
        partition_column: str = "adv_load_date",
        required_from: str | None = None,
        required_through: str | None = None,
        week_column: str = "week_number",
        max_fallback: int = 3,
        file_format: str = "parquet",
        load_args: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._root = filepath.rstrip("/")
        self._snapshot = date.fromisoformat(str(snapshot))
        self._column = partition_column
        self._required_from = _date(required_from)
        self._required = _date(required_through)
        self._week = week_column
        self._max_fallback = max_fallback
        self._format = file_format
        self._load_args = load_args or {}
        self.metadata = metadata

    def _describe(self) -> dict[str, Any]:
        return {
            "filepath": self._root,
            "snapshot": str(self._snapshot),
            "partition_column": self._column,
            "required_from": self._required_from,
            "required_through": self._required,
            "max_fallback": self._max_fallback,
        }

    def _save(self, data: None) -> None:
        raise DatasetError(f"{self._root} belongs to WM; this dataset is read-only.")

    def _exists(self) -> bool:
        return bool(self.partitions())

    def _load(self) -> DataFrame:
        available = self.partitions()
        refused = []
        for day in self.candidates(self._snapshot, available, self._max_fallback):
            problem = "no partition"
            if day in available:
                df, problem = self._read(day)
                problem = problem or self.coverage_problem(df)
            if problem:
                refused.append(f"{day}: {problem}")
                continue
            if day != self._snapshot:
                logger.warning(
                    "%s: using %s=%s instead of %s (%s)",
                    self._root,
                    self._column,
                    day,
                    self._snapshot,
                    "; ".join(refused),
                )
            return df
        raise DatasetError(
            f"{self._root}: no usable {self._column} partition. " + "; ".join(refused)
        )

    @staticmethod
    def candidates(
        target: date, available: list[date], max_fallback: int
    ) -> list[date]:
        """``target``, then up to ``max_fallback`` other partitions: newer ones from the
        nearest on, then older ones from the nearest back."""
        newer = sorted(d for d in available if d > target)
        older = sorted((d for d in available if d < target), reverse=True)
        return [target] + (newer + older)[:max_fallback]

    @staticmethod
    def problem(err: Exception) -> str:
        """A one-line reason from a read error: the deepest Java cause (e.g.
        ``BlockMissingException: ...``) when there is one, else the first line."""
        cause = getattr(err, "java_exception", None)
        while cause is not None and cause.getCause() is not None:
            cause = cause.getCause()
        text = str(cause.toString()) if cause is not None else str(err).strip()
        return (text.splitlines() or [type(err).__name__])[0][:300]

    def coverage_problem(self, df: DataFrame) -> str | None:
        """Why ``df``'s weeks miss the ``required_from`` or ``required_through`` month,
        or None (also when neither is set). Logs the partition's week range."""
        if not (self._required_from or self._required):
            return None
        week = F.col(self._week).cast("long")
        first, last = df.agg(F.min(week), F.max(week)).first()
        logger.info("%s: weeks %s to %s", self._root, first, last)
        if last is None:
            return "no rows"
        if self._required_from and first // 100 > _month(self._required_from):
            return f"weeks start at {first}, run needs {_month(self._required_from)}"
        if self._required and last // 100 < _month(self._required):
            return f"weeks end at {last}, run needs month {_month(self._required)}"
        return None

    def partitions(self) -> list[date]:
        """The dates of the ``<partition_column>=YYYY-MM-DD`` folders under the root."""
        spark = SparkSession.builder.getOrCreate()
        jvm, jsc = spark._jvm, spark._jsc  # pylint: disable=protected-access
        root = jvm.org.apache.hadoop.fs.Path(self._root)
        fs = root.getFileSystem(jsc.hadoopConfiguration())
        if not fs.exists(root):
            return []
        pattern = re.compile(rf"{re.escape(self._column)}=(\d{{4}}-\d{{2}}-\d{{2}})$")
        found = []
        for status in fs.listStatus(root):
            match = pattern.match(status.getPath().getName())
            if status.isDirectory() and match:
                found.append(date.fromisoformat(match.group(1)))
        return found

    def _read(self, day: date) -> tuple[DataFrame | None, str | None]:
        """The partition and None, or None and why it cannot be read in full (the
        footers are read on load, the rest by the ``noop`` scan)."""
        spark = SparkSession.builder.getOrCreate()
        reader = spark.read.format(self._format).options(**self._load_args)
        try:
            df = reader.load(f"{self._root}/{self._column}={day}")
            df.write.format("noop").mode("overwrite").save()
        except Exception as err:  # noqa: BLE001 - any read failure means fall back
            return None, self.problem(err)
        return df, None
`````

New:

`````python
"""Read-only Kedro dataset: one ``adv_load_date`` snapshot of a WM feature table.

WM ``04_feature`` tables are written as ``<root>/adv_load_date=YYYY-MM-DD/``; each
partition is a full-history snapshot (weekly rows in ``week_number``, ``yyyyMM0W``).
The dataset reads one partition, the ``snapshot`` date from globals, and falls back to
another partition when that one is missing or cannot be read. The tables belong to WM,
so a damaged partition cannot be fixed or rebuilt from this repo.

Readable means every byte of the partition comes back: the dataset scans the whole
partition once (Spark's ``noop`` sink) before returning it. HDFS can list a file whose
block no DataNode can serve (``BlockMissingException``), so the listing alone proves
nothing.

Fallback order: newer partitions first (nearest first), then older ones (nearest
first), at most ``max_fallback`` of them. A partition is only used when its
``week_number`` range reaches the ``required_through`` month (optional): an older
snapshot that would leave the last months empty is refused. When no partition
qualifies, the load fails with the reason for each one tried. A partition whose weeks
start after the ``required_from`` month (optional) is still used, with a warning: WM
keeps a rolling history, so the earliest months are empty. A fallback is logged as a
warning.

Catalog example::

    wm_fea_casa_eod_avg_balance:
      type: enbd_collections.datasets.wm_snapshot_dataset.WMSnapshotDataset
      filepath: ".../04_feature/fea_casa_eod_avg_bal_by_cif"
      snapshot: "${globals:snapshot_adv_load_date}"
      required_from: "2025-02-01"
      required_through: "${globals:crx_persona.persona_end_date}"
"""

from __future__ import annotations

import logging
import re
from datetime import date
from typing import Any

from kedro.io.core import AbstractDataset, DatasetError
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

logger = logging.getLogger(__name__)


def _date(value: str | None) -> date | None:
    return date.fromisoformat(str(value)) if value else None


def _month(day: date) -> int:
    """``day``'s month as ``yyyyMM``, the leading part of a WM ``week_number``."""
    return day.year * 100 + day.month


# Kedro aliases load / save to _load / _save; there is no base __init__ to call.
# pylint: disable=abstract-method,super-init-not-called,too-many-instance-attributes
# pylint: disable=broad-exception-caught
class WMSnapshotDataset(AbstractDataset[None, DataFrame]):
    """One snapshot partition of a WM table, with fallback to its neighbours."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *,
        filepath: str,
        snapshot: str,
        partition_column: str = "adv_load_date",
        required_from: str | None = None,
        required_through: str | None = None,
        week_column: str = "week_number",
        max_fallback: int = 3,
        file_format: str = "parquet",
        load_args: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._root = filepath.rstrip("/")
        self._snapshot = date.fromisoformat(str(snapshot))
        self._column = partition_column
        self._required_from = _date(required_from)
        self._required = _date(required_through)
        self._week = week_column
        self._max_fallback = max_fallback
        self._format = file_format
        self._load_args = load_args or {}
        self.metadata = metadata

    def _describe(self) -> dict[str, Any]:
        return {
            "filepath": self._root,
            "snapshot": str(self._snapshot),
            "partition_column": self._column,
            "required_from": self._required_from,
            "required_through": self._required,
            "max_fallback": self._max_fallback,
        }

    def _save(self, data: None) -> None:
        raise DatasetError(f"{self._root} belongs to WM; this dataset is read-only.")

    def _exists(self) -> bool:
        return bool(self.partitions())

    def _load(self) -> DataFrame:
        available = self.partitions()
        refused = []
        for day in self.candidates(self._snapshot, available, self._max_fallback):
            problem = "no partition"
            if day in available:
                df, problem = self._read(day)
                problem = problem or self.coverage_problem(df)
            if problem:
                refused.append(f"{day}: {problem}")
                continue
            if day != self._snapshot:
                logger.warning(
                    "%s: using %s=%s instead of %s (%s)",
                    self._root,
                    self._column,
                    day,
                    self._snapshot,
                    "; ".join(refused),
                )
            return df
        raise DatasetError(
            f"{self._root}: no usable {self._column} partition. " + "; ".join(refused)
        )

    @staticmethod
    def candidates(
        target: date, available: list[date], max_fallback: int
    ) -> list[date]:
        """``target``, then up to ``max_fallback`` other partitions: newer ones from the
        nearest on, then older ones from the nearest back."""
        newer = sorted(d for d in available if d > target)
        older = sorted((d for d in available if d < target), reverse=True)
        return [target] + (newer + older)[:max_fallback]

    @staticmethod
    def problem(err: Exception) -> str:
        """A one-line reason from a read error: the deepest Java cause (e.g.
        ``BlockMissingException: ...``) when there is one, else the first line."""
        cause = getattr(err, "java_exception", None)
        while cause is not None and cause.getCause() is not None:
            cause = cause.getCause()
        text = str(cause.toString()) if cause is not None else str(err).strip()
        return (text.splitlines() or [type(err).__name__])[0][:300]

    def coverage_problem(self, df: DataFrame) -> str | None:
        """Why ``df``'s weeks miss the ``required_through`` month, or None (also when
        neither date is set). Logs the partition's week range, and a warning when the
        weeks start after the ``required_from`` month."""
        if not (self._required_from or self._required):
            return None
        week = F.col(self._week).cast("long")
        first, last = df.agg(F.min(week), F.max(week)).first()
        logger.info("%s: weeks %s to %s", self._root, first, last)
        if last is None:
            return "no rows"
        if self._required and last // 100 < _month(self._required):
            return f"weeks end at {last}, run needs month {_month(self._required)}"
        if self._required_from and first // 100 > _month(self._required_from):
            logger.warning(
                "%s: weeks start at %s, later than the requested month %s; the months"
                " before are empty",
                self._root,
                first,
                _month(self._required_from),
            )
        return None

    def partitions(self) -> list[date]:
        """The dates of the ``<partition_column>=YYYY-MM-DD`` folders under the root."""
        spark = SparkSession.builder.getOrCreate()
        jvm, jsc = spark._jvm, spark._jsc  # pylint: disable=protected-access
        root = jvm.org.apache.hadoop.fs.Path(self._root)
        fs = root.getFileSystem(jsc.hadoopConfiguration())
        if not fs.exists(root):
            return []
        pattern = re.compile(rf"{re.escape(self._column)}=(\d{{4}}-\d{{2}}-\d{{2}})$")
        found = []
        for status in fs.listStatus(root):
            match = pattern.match(status.getPath().getName())
            if status.isDirectory() and match:
                found.append(date.fromisoformat(match.group(1)))
        return found

    def _read(self, day: date) -> tuple[DataFrame | None, str | None]:
        """The partition and None, or None and why it cannot be read in full (the
        footers are read on load, the rest by the ``noop`` scan)."""
        spark = SparkSession.builder.getOrCreate()
        reader = spark.read.format(self._format).options(**self._load_args)
        try:
            df = reader.load(f"{self._root}/{self._column}={day}")
            df.write.format("noop").mode("overwrite").save()
        except Exception as err:  # noqa: BLE001 - any read failure means fall back
            return None, self.problem(err)
        return df, None
`````

## Apply script

Written to `data/input/mirror_bundles/apply_bundle.py` by step 3.

`````python
"""Apply a mirror bundle (.md) to the workplace repo — safely.

Run from the workplace repo root:

    python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/<bundle>.md --check
        -> dry run, changes nothing. Must end with "CHECK PASSED".
    python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/<bundle>.md --apply
        -> writes the files, verifies them, compiles and imports every touched module.
           Must end with "APPLY PASSED".
    python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/<bundle>.md --revert
        -> puts every touched file back the way it was before --apply (uncommitted work only).

When a repo file differs from the copy the bundle was built from (an edit made at work, a
lint fix, a photo slip), the bundle still applies — it never stops on a difference:
  * replace: three-way merge (git merge-file) of this repo's file, the bundle's base copy and
    the bundle's new version. Edits made here survive wherever the bundle did not change the
    same lines; where both changed the same lines, the bundle's version wins.
  * delete: the file is deleted (git history keeps it).
  * add over an existing file: the bundle's version is written.
Each such file is listed as MERGED; review it with `git diff <path>` before committing.

Safety rules:
  * refuses to write on main/master, or when a touched file has uncommitted changes, so
    `git diff` shows exactly what the bundle did and --revert restores HEAD.
  * the bundle carries a SHA-256 for every block, so a damaged copy (rendered instead of raw
    markdown, smart quotes, lost lines) is detected before anything is written.

Options: --no-import skips the import check (e.g. outside the dev container).
"""

from __future__ import annotations

import argparse
import ast
import difflib
import hashlib
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

APPLY_VERSION = 7
PROTECTED_BRANCHES = {"main", "master"}
FENCE = re.compile(r"^(`{5,})")


def _norm(text: str) -> str:
    return text.replace("\r\n", "\n")


# Separator lines in comments (``# ── Node 1 ─────``, ``#######``) are transcribed from
# photos, where their exact length cannot be read. Runs of 4+ identical separator
# characters therefore compare equal whatever their length; so do trailing spaces.
_RULE_RUN = re.compile(r"([─━═=\-#*~_])\1{3,}")


def _loose(text: str) -> str:
    return "\n".join(
        _RULE_RUN.sub(r"\1\1\1\1", line.rstrip()) for line in _norm(text).split("\n")
    )


def _strip_docstrings(tree):
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if (
            isinstance(body, list)
            and body
            and isinstance(body[0], ast.Expr)
            and isinstance(getattr(body[0], "value", None), ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            node.body = body[1:] or [ast.Pass()]
    return tree


def _same_code(path: str, a: str, b: str) -> bool:
    """Same Python code (comments and docstrings aside) or the same YAML content."""
    try:
        if path.endswith(".py"):
            return ast.dump(_strip_docstrings(ast.parse(a))) == ast.dump(
                _strip_docstrings(ast.parse(b))
            )
        if path.endswith((".yml", ".yaml")):
            import yaml  # pylint: disable=import-outside-toplevel  # optional

            return yaml.safe_load(a) == yaml.safe_load(b)
    except Exception:  # pylint: disable=broad-except
        return False
    return False


def _is_new(current: str, e: dict) -> bool:
    """The repo file already holds the bundle's new version (comment noise aside)."""
    return _loose(current) == _loose(e["new"]) or _same_code(
        e["path"], current, e["new"]
    )


def _code_text(path: str, text: str) -> str:
    """The text with comments and docstrings removed (Python) or normalised (YAML)."""
    try:
        if path.endswith(".py"):
            return ast.unparse(_strip_docstrings(ast.parse(text)))
        if path.endswith((".yml", ".yaml")):
            import yaml  # pylint: disable=import-outside-toplevel  # optional

            return yaml.safe_dump(yaml.safe_load(text), sort_keys=True)
    except Exception:  # pylint: disable=broad-except
        pass
    return _loose(text)


def _matches_base(current: str | None, e: dict) -> bool:
    """The repo file is the version the bundle was built from: identical up to
    separator lengths and trailing spaces, or — since comments and docstrings are
    transcribed from photos — the same code / YAML content."""
    if current is None:
        return False
    if _loose(current) == _loose(e["base"]):
        return True
    return _same_code(e["path"], current, e["base"])


def _rebase(new: str, base: str, current: str) -> str:
    """``new`` with every line the bundle did not change taken from ``current``.

    ``current`` matches ``base`` line by line up to separator lengths (``_matches_base``),
    so the repo's own separators survive and ``git diff`` shows only real changes.
    """
    base_l, new_l, cur_l = (_norm(t).split("\n") for t in (base, new, current))
    if len(cur_l) != len(base_l):  # comments wrapped differently: no line alignment
        return new
    out: list[str] = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
        None, base_l, new_l, autojunk=False
    ).get_opcodes():
        out += cur_l[i1:i2] if tag == "equal" else new_l[j1:j2]
    return "\n".join(out)


def _merge3(current: str, base: str, new: str) -> str:
    """Three-way merge: this repo's edits on top of the bundle's change (git merge-file;
    on overlapping lines the bundle's version wins). Without git: the bundle's version.
    """
    with tempfile.TemporaryDirectory() as tmp:
        paths = []
        for name, text in (("current", current), ("base", base), ("new", new)):
            f = pathlib.Path(tmp) / name
            f.write_text(_norm(text), encoding="utf-8")
            paths.append(str(f))
        try:
            out = subprocess.run(
                ["git", "merge-file", "-p", "--theirs", *paths],
                capture_output=True,
                check=False,
            )
        except OSError:
            return new
    return out.stdout.decode("utf-8") if out.returncode >= 0 else new


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
    """Blocks whose content no longer matches the checksum (a damaged copy)."""
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
    """Reasons to refuse: a protected branch, or uncommitted edits in a touched file."""
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


def file_status(e: dict) -> str:  # pylint: disable=too-many-return-statements
    """One of: todo, done, merge (the repo file differs from the bundle's base copy)."""
    current = _read(pathlib.Path(e["path"]))
    cur_sha = None if current is None else _sha(current)
    if e["action"] == "add":
        if current is None:
            return "todo"
        return "done" if cur_sha == e["new_sha"] else "merge"
    if e["action"] == "replace":
        if current is not None and _loose(current) == _loose(e["new"]):
            return "done"
        if current is not None and _loose(current) == _loose(e["base"]):
            return "todo"
        if current is not None and _same_code(e["path"], current, e["new"]):
            return "done"
        if _matches_base(current, e):
            return "todo"
        return "merge"
    # delete
    if current is None:
        return "done"
    return "todo" if _matches_base(current, e) else "merge"


def explain_merge(e: dict) -> None:
    """One line on what happened to a file that differed from the bundle's copy."""
    what = {
        "replace": "merged with this repo's own edits",
        "delete": "deleted, although it had edits the bundle's copy lacks (git keeps them)",
        "add": "already existed with other content; replaced by the bundle's version",
    }[e["action"]]
    print(f"MERGED {e['path']}: {what} — review: git diff -- {e['path']}")


def _comment_only(e: dict) -> bool:
    current = _read(pathlib.Path(e["path"]))
    return (
        e["action"] in ("replace", "delete")
        and current is not None
        and _loose(current) != _loose(e["base"])
        and _matches_base(current, e)
    )


def print_table(entries: list[dict], statuses: list[str]) -> None:
    """One line per bundle file: its action and status."""
    word = {
        "todo": "will apply",
        "done": "already applied",
        "merge": "will apply — MERGED (differs from the bundle's copy)",
    }
    width = max(len(e["path"]) for e in entries)
    for e, s in zip(entries, statuses):
        note = ""
        if s == "todo" and _comment_only(e):
            note = "  (comments differ from the bundle's copy — fine)"
        print(f"  {e['action']:<8} {e['path']:<{width}}  {word[s]}{note}")


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
    """Compile every touched .py file and import its module (plus the registry)."""
    failures = []
    existing = [
        e for e in entries if e["action"] != "delete" and e["path"].endswith(".py")
    ]
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
            check=False,
        )
        if r.returncode != 0:
            last = (r.stderr.strip().splitlines() or ["?"])[-1]
            failures.append(f"import: {mod}: {last}")
    return failures


def _prune_empty_dirs(folder: pathlib.Path) -> None:
    """Remove folders left with nothing but bytecode caches after a delete."""
    while folder != pathlib.Path(".") and folder.is_dir():
        rest = [p for p in folder.iterdir() if p.name != "__pycache__"]
        if rest:
            return
        shutil.rmtree(folder)
        folder = folder.parent


# ── Commands ─────────────────────────────────────────────────────────────────


def cmd_check(entries: list[dict], quiet: bool = False) -> bool:
    """Dry run: what --apply would do; False only when git refuses."""
    statuses = [file_status(e) for e in entries]
    problems = git_problems(entries)
    if not quiet:
        print_table(entries, statuses)
    for p in problems:
        print("REFUSED: " + p)
    print(
        f"\n{statuses.count('todo') + statuses.count('merge')} to apply "
        f"({statuses.count('merge')} merged), {statuses.count('done')} already applied"
    )
    print("CHECK FAILED — nothing was written" if problems else "CHECK PASSED")
    return not problems


def cmd_apply(entries: list[dict], do_import: bool) -> bool:
    """Write every file (merging where this repo differs), then verify and import."""
    if not cmd_check(entries):
        return False
    merged = []
    for e in entries:
        status = file_status(e)
        if status == "done":
            continue
        path = pathlib.Path(e["path"])
        if status == "merge":
            merged.append(e)
        if e["action"] == "delete":
            path.unlink()
            _prune_empty_dirs(path.parent)
            continue
        new = e["new"]
        if e["action"] == "replace":
            current = _read(path)
            if status == "todo":
                new = _rebase(new, e["base"], current)
            elif current is not None:  # a file missing here gets the bundle's version
                new = _merge3(current, e["base"], new)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(new.encode("utf-8"))
    print()
    for e in merged:
        explain_merge(e)
    # a merged file keeps this repo's own edits, so it need not equal the bundle's version
    merged_paths = {e["path"] for e in merged if e["action"] == "replace"}
    bad = [
        e["path"]
        for e in entries
        if e["path"] not in merged_paths and file_status(e) != "done"
    ]
    failures = [f"not in the expected final state: {p}" for p in bad]
    failures += compile_and_import(entries, do_import)
    for f in failures:
        print("FAILED " + f)
    if failures:
        print("APPLY FAILED — undo with --revert, then send the messages above back")
        return False
    print(
        f"{len(entries)} files in their new state, compile OK"
        + (", imports OK" if do_import else " (imports skipped)")
    )
    print(
        "APPLY PASSED — review with `git status` / `git diff`"
        + (f" (look closely at the {len(merged)} MERGED files)" if merged else "")
    )
    return True


def cmd_revert(entries: list[dict]) -> bool:
    """Put every touched file back to HEAD (apply refuses to run over uncommitted changes,
    so HEAD is the state before --apply); files the bundle added are removed."""
    for e in entries:
        path = pathlib.Path(e["path"])
        committed = _head_version(e["path"])
        if committed is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(committed.encode("utf-8"))
        elif path.exists():
            path.unlink()
            _prune_empty_dirs(path.parent)
    print("REVERT DONE — `git status` should show none of the bundle's files")
    return True


def main() -> int:
    """Parse the arguments, verify the bundle's checksums and run the chosen mode."""
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
        print(
            f"This bundle needs apply_bundle.py version {need.group(1)}; you have "
            f"{APPLY_VERSION}. Redo step 3 of the bundle."
        )
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
`````

## Cleanup prompt

Copy this to the workplace assistant in UAT once the bundle's PROD checks are done:

````text
Clean up after mirror bundle 33_wm_required_from_warning.md, on the bundle's branch.
Nothing to clean up for bundle 33: it adds no temporary files. Bundle 32's cleanup covers the check pipelines.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
