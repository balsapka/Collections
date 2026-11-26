# Mirror bundle 32 — WM snapshot tables: one adv_load_date partition, with fallback

apply_bundle version: 7 · built 2026-11-26 from `43489e1..ae4eab7` · source: 3 added, 1 replaced, 0 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 5). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Work on a branch (the apply script refuses to run on main):

```bash
git checkout -b feature/wm_snapshot_fallback
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/32_wm_snapshot_fallback.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '32_wm_snapshot_fallback.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/32_wm_snapshot_fallback.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Ask Sonnet the following, in one go, and fix what it finds before committing:

> **Goal.** The WM `04_feature` snapshot tables we read load one `adv_load_date` partition through the bundle's new dataset `enbd_collections.datasets.wm_snapshot_dataset.WMSnapshotDataset`. If that partition can't be read, they fall back to a neighbouring one. Read the module docstring first.
>
> **Decisions already made (don't revisit):**
> - Switch these four entries in `conf/base/catalog/catalog_casa_plus_ftr.yml`: `wm_fea_casa_eod_avg_balance`, `wm_fea_casa_cc_inflow_outflow`, `wm_fea_salary_days_since_increment`, `wm_fea_wealth_holdings_by_cif` (if that one lives in another catalog file, switch it there). Each becomes:
>   ```yaml
>   type: enbd_collections.datasets.wm_snapshot_dataset.WMSnapshotDataset
>   filepath: <the table's folder root, without any /adv_load_date=... suffix>
>   snapshot: "${globals:snapshot_adv_load_date}"
>   required_from: "${globals:wm_snapshot_required_from}"
>   required_through: "${globals:crx_persona.persona_end_date}"
>   ```
>   Keep any existing `load_args` and `metadata`. Drop `file_format: parquet` and `save_args`: parquet is the default and the dataset is read-only.
> - `wm_fea_casa_eod_avg_balance` today points at the folder root, so it reads every partition. That is how the damaged `adv_load_date=2026-06-02` partition (`BlockMissingException` on `part-00007`) broke the run. Pinning it to one snapshot is intended.
> - In `conf/dev/globals_dev.yml`, add right under `snapshot_adv_load_date` (keep every other value exactly as it is now, including the dates the user set):
>   ```yaml
>   # Earliest month any WM snapshot consumer reads: persona_start_date minus 11 months
>   # (products history_months 12). Update with persona_start_date.
>   wm_snapshot_required_from: "<persona_start_date minus 11 months, first of month>"
>   ```
>   Work the value out from the current `crx_persona.persona_start_date` and say what you used.
>
> **Hard rules:** change nothing else in the catalogs or globals. Never run `hdfs fsck -delete` / `-move` or anything else that writes to WM paths. Node code keeps reading through node inputs.
>
> **Deliverables in your reply:**
> 1. Each switched entry, before → after. Also list (don't switch) any other catalog entry under `wealth_management/04_feature/` or with `adv_load_date` in its path.
> 2. Every top-level key the apply added or removed in `src/enbd_collections/pipeline_registry.py` and `conf/base/catalog/*.yml`, compared with the last commit. Expected: the registry adds the `b32_check` import plus `casa_b32_snapshot` and `casa_b32_compare`; the catalog adds `catalog_tmp_b32_check.yml` (`casa_b32_old_balance`); nothing removed. Put back anything else that went missing, and make sure no key appears twice across `conf/base/catalog/*.yml`.
> 3. `src/enbd_collections/datasets/__init__.py` exists. `python -c "import enbd_collections.datasets.wm_snapshot_dataset, enbd_collections.pipeline_registry"` imports. `kedro registry list` shows `casa_b32_snapshot` and `casa_b32_compare`. `kedro catalog list` (or a `DataCatalog.from_config` of the four entries) builds the datasets without error.
> 4. Unit tests for `WMSnapshotDataset.candidates` (order and cap) and the coverage rule (`coverage_problem` on a small DataFrame), in the existing test style; they pass. black, ruff and pylint clean on the touched files.

**Step 5.** Commit the source only, and push:

```bash
git add src conf && git commit -m "WM snapshot tables read one adv_load_date partition with fallback (bundle 32)" && git push -u origin feature/wm_snapshot_fallback
```

**Undo** (before step 5) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/32_wm_snapshot_fallback.md --revert
```

### In PROD

**Step 6.** Get the branch:

```bash
git fetch origin && git checkout feature/wm_snapshot_fallback && git pull
```

**Step 7.** In PROD, after the pull, for each model_id you rerun (switch `model_id` in `globals_dev.yml`). Run them in this order, because the snapshot has to come before `casa_features` overwrites the table:

```bash
kedro run --pipeline=casa_b32_snapshot
```

```bash
kedro run --pipeline=casa_features
```

```bash
kedro run --pipeline=casa_b32_compare
```

Paste back the `=== B32 CASA OLD NEW START/END ===` block per model_id. Also paste the dataset's log lines from `casa_features`: `... weeks <first> to <last>` for each WM table, and any `using adv_load_date=... instead of ...` warning. Then carry on with the rest of the rerun (product features, persona pipelines) as planned. If a load fails with `no usable adv_load_date partition`, paste the message: it gives the reason for each partition tried.

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** WM `04_feature` tables are read from one `adv_load_date` partition (the `snapshot_adv_load_date` global). If that partition can't be read, the load falls back to a neighbouring one. **Apply on top of bundles 25–31 and their cleanups.** No persona logic changes.

- **Why.** `wm_fea_casa_eod_avg_balance` points at the folder root in `catalog_casa_plus_ftr.yml`. Spark therefore read **every** partition, whatever the global said. One block of `part-00007` in `adv_load_date=2026-06-02` has no reachable replica (`BlockMissingException`; NameNode still lists replicas on `10.229.163.35` / `.87`). Every scan that touches it fails. The table belongs to WM, so we can't repair it. Its sibling entries are already pinned to one partition.
- **New dataset** `enbd_collections.datasets.wm_snapshot_dataset.WMSnapshotDataset` (read-only):
  - Reads `<root>/adv_load_date=<snapshot>`.
  - First it scans the whole partition once (Spark `noop` sink). HDFS can list a file it cannot serve, so the listing alone proves nothing.
  - If the partition is missing, unreadable, or its `week_number` range misses the `required_from` / `required_through` months, it tries newer partitions (nearest first), then older ones. At most `max_fallback` (3) are tried.
  - A fallback is logged as a warning naming the partition used and why the others were refused. When nothing qualifies, the load fails with each reason.
  - Every load logs the week range it got.
- **Catalog (UAT step 4, Sonnet).** `catalog_casa_plus_ftr.yml` is not in the mirror, so Sonnet switches the four WM entries we read: `wm_fea_casa_eod_avg_balance`, `wm_fea_casa_cc_inflow_outflow`, `wm_fea_salary_days_since_increment`, `wm_fea_wealth_holdings_by_cif`. It also adds the global `wm_snapshot_required_from`.
- **Temporary check:** `pipelines/casa/b32_check.py`, `catalog_tmp_b32_check.yml` and 3 registry lines. It snapshots the persisted `feat_cif_casa_balance_monthly` (built from all partitions), then compares it with the one rebuilt from the single snapshot, per month: rows only old / only new / both, share of equal balances, size of the differences, `casa_flow` disagreements.

Tested in the mirror:
- Spec test `checks/wm_snapshot_spec.py` (local Spark, 11 cases): healthy snapshot, missing snapshot, damaged part files (they open, but the scan fails), fallback order, coverage refusals, failure message, read-only.
- Check module run on toy data.
- Smoke check at baseline (the 6 known `cc_raw_extract` lines).
- black, ruff and pylint clean on the touched files.

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
| add | `conf/base/catalog/catalog_tmp_b32_check.yml` |
| add | `src/enbd_collections/datasets/wm_snapshot_dataset.py` |
| replace | `src/enbd_collections/pipeline_registry.py` |
| add | `src/enbd_collections/pipelines/casa/b32_check.py` |

## Files

### FILE: `conf/base/catalog/catalog_tmp_b32_check.yml`
action: add · new sha256 `ee613a118bb38dbf06719323167b5a0b9b0619d4be8f5b875f6e5529b79e4cc8` · new trailing newline: yes

New:

`````yaml
# TEMPORARY (bundle 32): feat_cif_casa_balance_monthly before the WM snapshot switch;
# removed by the bundle's cleanup.
casa_b32_old_balance:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/b32_check/casa_b32_old_balance"
  save_args:
    mode: overwrite
`````

### FILE: `src/enbd_collections/datasets/wm_snapshot_dataset.py`
action: add · new sha256 `d1ddf86a1a91fd09f7585d338dcc6fdd230244df1bff753d37a3b23e6ca30b95` · new trailing newline: yes

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

### FILE: `src/enbd_collections/pipeline_registry.py`
action: replace · base sha256 `581be2c57723cc6c8bfe7fda5840dcb2f2215c50a510d4d85a5d4bae8c02efa4` · base trailing newline: yes · new sha256 `909cf0fe1dbfbb3e8237f3a5029de44315d177b9e746f849f02d77908efad31f` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Project pipeline registry."""

from kedro.pipeline import Pipeline

from enbd_collections.pipelines import schema_intelligence as si
from enbd_collections.pipelines import credit_card as cc_dpl
from enbd_collections.pipelines import credit_card_way4 as cc_way4
from enbd_collections.pipelines import demographics as demo
from enbd_collections.pipelines import bureau
from enbd_collections.pipelines import retail_loans

from enbd_collections.pipelines.credit_card import staging as cc_dpl_stg
from enbd_collections.pipelines.credit_card import primary as cc_dpl_prm
from enbd_collections.pipelines.credit_card import features as cc_dpl_feat
from enbd_collections.pipelines.credit_card import spine as cc_dpl_spine
from enbd_collections.pipelines.credit_card import model_input as cc_dpl_mi

from enbd_collections.pipelines.credit_card_way4 import staging as cc_way4_stg
from enbd_collections.pipelines.credit_card_way4 import primary as cc_way4_prm
from enbd_collections.pipelines.credit_card_way4 import features as cc_way4_feat
from enbd_collections.pipelines.credit_card_way4 import spine as cc_way4_spine
from enbd_collections.pipelines.credit_card_way4 import target as cc_way4_target
from enbd_collections.pipelines.demographics import staging as demo_stg
from enbd_collections.pipelines.demographics import intermediate as demo_int
from enbd_collections.pipelines.demographics import primary as demo_prm
from enbd_collections.pipelines.demographics import features as demo_feat

from enbd_collections.pipelines.bureau import staging as bureau_stg
from enbd_collections.pipelines.bureau import primary as bureau_prm
from enbd_collections.pipelines.bureau import intermediate as bureau_int
from enbd_collections.pipelines.bureau import features as bureau_feat
from enbd_collections.pipelines.bureau import salary_bounces as bureau_salary_bounces

from enbd_collections.pipelines.casa import primary as casa_prm
from enbd_collections.pipelines.casa import features as casa_feat
from enbd_collections.pipelines.casa import windows as casa_win
from enbd_collections.pipelines.casa import windows_all_models as casa_win_all
from enbd_collections.pipelines.casa import windows_casa as casa_win_casa
from enbd_collections.pipelines.casa import windows_casa_all_models as casa_win_casa_all
from enbd_collections.pipelines.products import features as products_feat
from enbd_collections.pipelines.products import primary as products_prm

from enbd_collections.pipelines.retail_loans import staging as retail_loans_stg
from enbd_collections.pipelines.retail_loans import primary as retail_loans_prm
from enbd_collections.pipelines.retail_loans import intermediate as retail_loans_int
from enbd_collections.pipelines.retail_loans import features as retail_loans_feat
from enbd_collections.pipelines.retail_loans import spine as retail_loans_spine
from enbd_collections.pipelines.retail_loans import target as retail_loans_target

from enbd_collections.pipelines import dcore
from enbd_collections.pipelines.dcore import staging as dcore_stg
from enbd_collections.pipelines.dcore import primary as dcore_prm
from enbd_collections.pipelines.dcore import intermediate as dcore_int
from enbd_collections.pipelines.dcore import features as dcore_feat

from enbd_collections.pipelines.sampling import dpl as sampling_dpl
from enbd_collections.pipelines.sampling import overdue as sampling_overdue
from enbd_collections.pipelines.sampling import aecb as sampling_aecb
from enbd_collections.pipelines.sampling import demographics as sampling_demo
from enbd_collections.pipelines.sampling import ddi as sampling_ddi
from enbd_collections.pipelines.sampling import way4 as sampling_way4
from enbd_collections.pipelines.sampling import retail_loans as sampling_retail
from enbd_collections.pipelines.sampling import dcore as sampling_dcore
from enbd_collections.pipelines.validation import mpdpd as validation_mpdpd
from enbd_collections.pipelines.validation import (
    demographics as validation_demographics,
)
from enbd_collections.pipelines.validation import (
    validate_dcore_cc_180_plus as validation_dcore_cc_180_plus,
)
from enbd_collections.pipelines.bureau import validation as validation_bureau
from enbd_collections.pipelines import model_input
from enbd_collections.pipelines import model_training
from enbd_collections.pipelines import model_reporting
from enbd_collections.pipelines.crx_persona import (
    cc_full_history as crx_cc_full_history,
)
from enbd_collections.pipelines.crx_persona import (
    cc_raw_extract as crx_cc_raw_extract,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a4_deterioration as crx_cc_a4_deterioration,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a2_locatability as crx_cc_a2_locatability,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a1_ability as crx_cc_a1_ability,
)
from enbd_collections.pipelines.crx_persona import obs_base as crx_obs_base

from enbd_collections.pipelines.crx_persona import (
    cc_a3_payment_credibility as crx_cc_a3_payment_credibility,
)
from enbd_collections.pipelines.crx_persona import (
    rl_full_history as crx_rl_full_history,
)
from enbd_collections.pipelines.crx_persona import (
    rl_a4_deterioration as crx_rl_a4_deterioration,
)
from enbd_collections.pipelines.crx_persona import rl_a1_ability as crx_rl_a1_ability
from enbd_collections.pipelines.crx_persona import (
    rl_a2_locatability as crx_rl_a2_locatability,
)
from enbd_collections.pipelines.crx_persona import (
    rl_a3_payment_credibility as crx_rl_a3_payment_credibility,
)
from enbd_collections.pipelines.crx_persona import cc_uc1_stated as crx_cc_uc1_stated
from enbd_collections.pipelines.crx_persona import rl_uc1_stated as crx_rl_uc1_stated
from enbd_collections.pipelines import digital_login as dl
from enbd_collections.pipelines.location import pipeline as location_features
from enbd_collections.pipelines import genesys


def register_pipelines() -> dict[str, Pipeline]:
    """Pipeline registry."""

    return {
        # -- Model input (cross-domain) ------------------------------------
        "model_input": model_input.create_pipeline(),
        "model_input_base": model_input.create_base_pipeline(),
        "model_input_features": model_input.create_features_pipeline(),
        # -- Model training & reporting ------------------------------------
        "model_training": model_training.create_pipeline(),
        "model_reporting": model_reporting.create_pipeline(),
        # -- Credit card DPL (domain) --------------------------------------
        "cc_dpl": cc_dpl.create_pipeline(),
        "cc_dpl_data_spine": cc_dpl_spine.create_data_spine_pipeline(),
        "cc_dpl_staging": cc_dpl_stg.create_pipeline(),
        "cc_dpl_primary": cc_dpl_prm.create_pipeline(),
        "cc_dpl_spine_target": cc_dpl_spine.create_pipeline(),
        "cc_dpl_spine_recovery_target": cc_dpl_spine.create_recovery_pipeline(),
        "cc_dpl_features": cc_dpl_feat.create_pipeline(),
        "cc_dpl_model_input": cc_dpl_mi.create_pipeline(),
        # -- Credit card Way4 (domain) -------------------------------------
        "cc_way4_spine": cc_way4_spine.create_pipeline(),
        "cc_way4_staging": cc_way4_stg.create_pipeline(),
        "cc_way4_primary": cc_way4_prm.create_pipeline(),
        "cc_way4_target": cc_way4_target.create_pipeline(),
        "cc_way4_features": cc_way4_feat.create_pipeline(),
        # -- Demographics (domain) -----------------------------------------
        "demographics": demo.create_pipeline(cif_obs_spine="rl_cif_obs_spine"),
        "demographics_cc": demo.create_pipeline(cif_obs_spine="cc_cif_obs_spine"),
        "demographics_staging": demo_stg.create_pipeline(),
        "demographics_primary": demo_prm.create_pipeline(),
        "demographics_intermediate": demo_int.create_pipeline(),
        "demographics_features": demo_feat.create_pipeline(
            cif_obs_spine="rl_cif_obs_spine"
        ),
        "demographics_features_cc": demo_feat.create_pipeline(
            cif_obs_spine="cc_cif_obs_spine"
        ),
        # -- Bureau / AECB (domain) ----------------------------------------
        "bureau": bureau.create_pipeline(),
        "bureau_staging": bureau_stg.create_pipeline(),
        "bureau_primary": bureau_prm.create_pipeline(),
        "bureau_intermediate": bureau_int.create_pipeline(),
        "bureau_features": bureau_feat.create_pipeline(),
        "bureau_salary_bounces": bureau_salary_bounces.create_pipeline(),
        # -- CASA (domain) ---------------------------------------------------
        "casa_primary": casa_prm.create_pipeline(),
        "casa_features": casa_feat.create_pipeline(),
        "casa_windows": casa_win.create_pipeline(),
        "casa_windows_all_models": casa_win_all.create_pipeline(),
        "casa_windows_casa": casa_win_casa.create_pipeline(),
        "casa_windows_casa_all_models": casa_win_casa_all.create_pipeline(),
        "product_primary": products_prm.create_pipeline(),
        "product_features": products_feat.create_pipeline(),
        # -- Retail Loans (domain) -----------------------------------------
        "retail_loans": retail_loans.create_pipeline(),
        "retail_loans_staging": retail_loans_stg.create_pipeline(),
        "retail_loans_primary": retail_loans_prm.create_pipeline(),
        "retail_loans_intermediate": retail_loans_int.create_pipeline(),
        "retail_loans_features": retail_loans_feat.create_pipeline(),
        # -- Schema intelligence -------------------------------------------
        "schema_intelligence": si.create_pipeline(),
        # -- Sampling ------------------------------------------------------
        "dpl_sampling": sampling_dpl.create_pipeline(),
        "overdue_sampling": sampling_overdue.create_pipeline(),
        "aecb_sampling": sampling_aecb.create_pipeline(),
        "demographics_sampling": sampling_demo.create_pipeline(),
        "ddi_sampling": sampling_ddi.create_pipeline(),
        "way4_sampling": sampling_way4.create_pipeline(),
        "retail_loans_sampling": sampling_retail.create_pipeline(),
        "dcore_sampling": sampling_dcore.create_pipeline(),
        # -- Validation ----------------------------------------------------
        "validate_mpdpd": validation_mpdpd.create_pipeline(),
        "validate_bureau_alerts": validation_bureau.create_pipeline(),
        "validate_demographics": validation_demographics.create_pipeline(),
        "validate_dcore_cc_180_plus": validation_dcore_cc_180_plus.create_pipeline(),
        # -- DCORE (Collections Management System) -------------------------
        "dcore": dcore.create_pipeline(),
        "dcore_staging": dcore_stg.create_pipeline(),
        "dcore_primary": dcore_prm.create_pipeline(),
        "dcore_intermediate": dcore_int.create_pipeline(),
        "dcore_features": dcore_feat.create_pipeline(),
        # -- Model variant pipelines (namespaced by model_id) --------------
        # Full pipelines — run with: kedro run --env=dev --pipeline=<model_id>
        "cc_60_180": cc_way4.create_pipeline(),
        "cc_180_plus": cc_way4.create_180_plus_pipeline(),
        "rl_60_180": retail_loans.create_rl_60_180_pipeline(),
        "rl_180_plus": retail_loans.create_rl_180_plus_pipeline(),
        # Sub-pipelines for incremental cc_60_180 runs
        "cc_60_180.spine": cc_way4_spine.create_pipeline(),
        "cc_60_180.staging": cc_way4_stg.create_pipeline(),
        "cc_60_180.target": cc_way4_target.create_pipeline(),
        "cc_60_180.features": cc_way4_feat.create_pipeline(),
        "cc_60_180.rl_scope": retail_loans.create_cc_scoped_pipeline(),
        # Bureau scoped to this model's spine CIFs (model_id set by ModelConfigHook)
        "cc_60_180.bureau": bureau.create_pipeline(),
        # Sub-pipelines for incremental cc_180_plus runs
        "cc_180_plus.spine": cc_way4_spine.create_180_plus_pipeline(),
        "cc_180_plus.staging": cc_way4_stg.create_pipeline(),
        "cc_180_plus.target": cc_way4_target.create_recovery_pipeline(),
        "cc_180_plus.features": cc_way4_feat.create_pipeline(),
        "cc_180_plus.rl_scope": retail_loans.create_cc_scoped_pipeline(),
        "cc_180_plus.bureau": bureau.create_pipeline(),
        # Sub-pipelines for incremental rl_60_180 / rl_180_plus runs
        "rl_60_180.spine": retail_loans_spine.create_pipeline(),
        "rl_60_180.staging": retail_loans_stg.create_pipeline(),
        "rl_60_180.target": retail_loans_target.create_pipeline(),
        "rl_60_180.features": retail_loans_feat.create_pipeline(),
        "rl_60_180.primary": retail_loans_prm.create_pipeline(),
        "rl_60_180.intermediate": retail_loans_int.create_pipeline(),
        "rl_60_180.cc_scope": cc_way4.create_rl_scoped_pipeline(),
        "rl_60_180.bureau": bureau.create_pipeline(),
        "rl_180_plus.spine": retail_loans_spine.create_180_plus_pipeline(),
        "rl_180_plus.staging": retail_loans_stg.create_pipeline(),
        "rl_180_plus.target": retail_loans_target.create_recovery_pipeline(),
        "rl_180_plus.features": retail_loans_feat.create_rl_180_plus_pipeline(),
        "rl_180_plus.primary": retail_loans_prm.create_pipeline(),
        "rl_180_plus.intermediate": retail_loans_int.create_pipeline(),
        "rl_180_plus.cc_scope": cc_way4.create_rl_scoped_pipeline(),
        "rl_180_plus.bureau": bureau.create_pipeline(),
        # -- CRX Persona (experimental, additive) ---------------------------
        # Revert: remove this entry + the import above + rm -r crx_persona/
        "crx_cc_full_history": crx_cc_full_history.create_pipeline(),
        "crx_cc_raw_extract": crx_cc_raw_extract.create_pipeline(),
        "crx_cc_a4_deterioration": crx_cc_a4_deterioration.create_pipeline(),
        "crx_cc_a2_locatability": crx_cc_a2_locatability.create_pipeline(),
        "crx_cc_a1_ability": crx_cc_a1_ability.create_pipeline(),
        "crx_cc_obs_base": crx_obs_base.create_cc_pipeline(),
        "crx_rl_obs_base": crx_obs_base.create_rl_pipeline(),
        "crx_cc_uc1_stated": crx_cc_uc1_stated.create_pipeline(),
        "crx_rl_uc1_stated": crx_rl_uc1_stated.create_pipeline(),
        "crx_cc_a3_payment_credibility": (
            crx_cc_a3_payment_credibility.create_pipeline()
        ),
        "crx_rl_full_history": crx_rl_full_history.create_pipeline(),
        "crx_rl_a4_deterioration": crx_rl_a4_deterioration.create_pipeline(),
        "crx_rl_a1_ability": crx_rl_a1_ability.create_pipeline(),
        "crx_rl_a2_locatability": crx_rl_a2_locatability.create_pipeline(),
        "crx_rl_a3_payment_credibility": (
            crx_rl_a3_payment_credibility.create_pipeline()
        ),
        # TEMPORARY (bundle 28): removed by the cleanup
        # -- Digital login (OMB) --------------------------------------------
        "digital_login": dl.create_pipeline(),
        "location_features": location_features.create_pipeline(),
        # -- Genesys / PCA interactions ----------------------------------------
        "genesys": genesys.create_pipeline(),
        # -- Default ---------------------------------------------------------
        "__default__": cc_way4.create_pipeline(),
        "rerun": model_input.create_features_pipeline()
        + model_training.create_pipeline()
        + model_reporting.create_pipeline(),
        "rerun_full": model_input.create_base_pipeline()
        + model_input.create_features_pipeline()
        + model_training.create_pipeline()
        + model_reporting.create_pipeline(),
    }
`````

New:

`````python
"""Project pipeline registry."""

from kedro.pipeline import Pipeline

from enbd_collections.pipelines import schema_intelligence as si
from enbd_collections.pipelines import credit_card as cc_dpl
from enbd_collections.pipelines import credit_card_way4 as cc_way4
from enbd_collections.pipelines import demographics as demo
from enbd_collections.pipelines import bureau
from enbd_collections.pipelines import retail_loans

from enbd_collections.pipelines.credit_card import staging as cc_dpl_stg
from enbd_collections.pipelines.credit_card import primary as cc_dpl_prm
from enbd_collections.pipelines.credit_card import features as cc_dpl_feat
from enbd_collections.pipelines.credit_card import spine as cc_dpl_spine
from enbd_collections.pipelines.credit_card import model_input as cc_dpl_mi

from enbd_collections.pipelines.credit_card_way4 import staging as cc_way4_stg
from enbd_collections.pipelines.credit_card_way4 import primary as cc_way4_prm
from enbd_collections.pipelines.credit_card_way4 import features as cc_way4_feat
from enbd_collections.pipelines.credit_card_way4 import spine as cc_way4_spine
from enbd_collections.pipelines.credit_card_way4 import target as cc_way4_target
from enbd_collections.pipelines.demographics import staging as demo_stg
from enbd_collections.pipelines.demographics import intermediate as demo_int
from enbd_collections.pipelines.demographics import primary as demo_prm
from enbd_collections.pipelines.demographics import features as demo_feat

from enbd_collections.pipelines.bureau import staging as bureau_stg
from enbd_collections.pipelines.bureau import primary as bureau_prm
from enbd_collections.pipelines.bureau import intermediate as bureau_int
from enbd_collections.pipelines.bureau import features as bureau_feat
from enbd_collections.pipelines.bureau import salary_bounces as bureau_salary_bounces

from enbd_collections.pipelines.casa import primary as casa_prm
from enbd_collections.pipelines.casa import features as casa_feat
from enbd_collections.pipelines.casa import b32_check  # TEMPORARY
from enbd_collections.pipelines.casa import windows as casa_win
from enbd_collections.pipelines.casa import windows_all_models as casa_win_all
from enbd_collections.pipelines.casa import windows_casa as casa_win_casa
from enbd_collections.pipelines.casa import windows_casa_all_models as casa_win_casa_all
from enbd_collections.pipelines.products import features as products_feat
from enbd_collections.pipelines.products import primary as products_prm

from enbd_collections.pipelines.retail_loans import staging as retail_loans_stg
from enbd_collections.pipelines.retail_loans import primary as retail_loans_prm
from enbd_collections.pipelines.retail_loans import intermediate as retail_loans_int
from enbd_collections.pipelines.retail_loans import features as retail_loans_feat
from enbd_collections.pipelines.retail_loans import spine as retail_loans_spine
from enbd_collections.pipelines.retail_loans import target as retail_loans_target

from enbd_collections.pipelines import dcore
from enbd_collections.pipelines.dcore import staging as dcore_stg
from enbd_collections.pipelines.dcore import primary as dcore_prm
from enbd_collections.pipelines.dcore import intermediate as dcore_int
from enbd_collections.pipelines.dcore import features as dcore_feat

from enbd_collections.pipelines.sampling import dpl as sampling_dpl
from enbd_collections.pipelines.sampling import overdue as sampling_overdue
from enbd_collections.pipelines.sampling import aecb as sampling_aecb
from enbd_collections.pipelines.sampling import demographics as sampling_demo
from enbd_collections.pipelines.sampling import ddi as sampling_ddi
from enbd_collections.pipelines.sampling import way4 as sampling_way4
from enbd_collections.pipelines.sampling import retail_loans as sampling_retail
from enbd_collections.pipelines.sampling import dcore as sampling_dcore
from enbd_collections.pipelines.validation import mpdpd as validation_mpdpd
from enbd_collections.pipelines.validation import (
    demographics as validation_demographics,
)
from enbd_collections.pipelines.validation import (
    validate_dcore_cc_180_plus as validation_dcore_cc_180_plus,
)
from enbd_collections.pipelines.bureau import validation as validation_bureau
from enbd_collections.pipelines import model_input
from enbd_collections.pipelines import model_training
from enbd_collections.pipelines import model_reporting
from enbd_collections.pipelines.crx_persona import (
    cc_full_history as crx_cc_full_history,
)
from enbd_collections.pipelines.crx_persona import (
    cc_raw_extract as crx_cc_raw_extract,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a4_deterioration as crx_cc_a4_deterioration,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a2_locatability as crx_cc_a2_locatability,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a1_ability as crx_cc_a1_ability,
)
from enbd_collections.pipelines.crx_persona import obs_base as crx_obs_base

from enbd_collections.pipelines.crx_persona import (
    cc_a3_payment_credibility as crx_cc_a3_payment_credibility,
)
from enbd_collections.pipelines.crx_persona import (
    rl_full_history as crx_rl_full_history,
)
from enbd_collections.pipelines.crx_persona import (
    rl_a4_deterioration as crx_rl_a4_deterioration,
)
from enbd_collections.pipelines.crx_persona import rl_a1_ability as crx_rl_a1_ability
from enbd_collections.pipelines.crx_persona import (
    rl_a2_locatability as crx_rl_a2_locatability,
)
from enbd_collections.pipelines.crx_persona import (
    rl_a3_payment_credibility as crx_rl_a3_payment_credibility,
)
from enbd_collections.pipelines.crx_persona import cc_uc1_stated as crx_cc_uc1_stated
from enbd_collections.pipelines.crx_persona import rl_uc1_stated as crx_rl_uc1_stated
from enbd_collections.pipelines import digital_login as dl
from enbd_collections.pipelines.location import pipeline as location_features
from enbd_collections.pipelines import genesys


def register_pipelines() -> dict[str, Pipeline]:
    """Pipeline registry."""

    return {
        # -- Model input (cross-domain) ------------------------------------
        "model_input": model_input.create_pipeline(),
        "model_input_base": model_input.create_base_pipeline(),
        "model_input_features": model_input.create_features_pipeline(),
        # -- Model training & reporting ------------------------------------
        "model_training": model_training.create_pipeline(),
        "model_reporting": model_reporting.create_pipeline(),
        # -- Credit card DPL (domain) --------------------------------------
        "cc_dpl": cc_dpl.create_pipeline(),
        "cc_dpl_data_spine": cc_dpl_spine.create_data_spine_pipeline(),
        "cc_dpl_staging": cc_dpl_stg.create_pipeline(),
        "cc_dpl_primary": cc_dpl_prm.create_pipeline(),
        "cc_dpl_spine_target": cc_dpl_spine.create_pipeline(),
        "cc_dpl_spine_recovery_target": cc_dpl_spine.create_recovery_pipeline(),
        "cc_dpl_features": cc_dpl_feat.create_pipeline(),
        "cc_dpl_model_input": cc_dpl_mi.create_pipeline(),
        # -- Credit card Way4 (domain) -------------------------------------
        "cc_way4_spine": cc_way4_spine.create_pipeline(),
        "cc_way4_staging": cc_way4_stg.create_pipeline(),
        "cc_way4_primary": cc_way4_prm.create_pipeline(),
        "cc_way4_target": cc_way4_target.create_pipeline(),
        "cc_way4_features": cc_way4_feat.create_pipeline(),
        # -- Demographics (domain) -----------------------------------------
        "demographics": demo.create_pipeline(cif_obs_spine="rl_cif_obs_spine"),
        "demographics_cc": demo.create_pipeline(cif_obs_spine="cc_cif_obs_spine"),
        "demographics_staging": demo_stg.create_pipeline(),
        "demographics_primary": demo_prm.create_pipeline(),
        "demographics_intermediate": demo_int.create_pipeline(),
        "demographics_features": demo_feat.create_pipeline(
            cif_obs_spine="rl_cif_obs_spine"
        ),
        "demographics_features_cc": demo_feat.create_pipeline(
            cif_obs_spine="cc_cif_obs_spine"
        ),
        # -- Bureau / AECB (domain) ----------------------------------------
        "bureau": bureau.create_pipeline(),
        "bureau_staging": bureau_stg.create_pipeline(),
        "bureau_primary": bureau_prm.create_pipeline(),
        "bureau_intermediate": bureau_int.create_pipeline(),
        "bureau_features": bureau_feat.create_pipeline(),
        "bureau_salary_bounces": bureau_salary_bounces.create_pipeline(),
        # -- CASA (domain) ---------------------------------------------------
        "casa_primary": casa_prm.create_pipeline(),
        "casa_features": casa_feat.create_pipeline(),
        "casa_b32_snapshot": b32_check.create_snapshot_pipeline(),
        "casa_b32_compare": b32_check.create_compare_pipeline(),
        "casa_windows": casa_win.create_pipeline(),
        "casa_windows_all_models": casa_win_all.create_pipeline(),
        "casa_windows_casa": casa_win_casa.create_pipeline(),
        "casa_windows_casa_all_models": casa_win_casa_all.create_pipeline(),
        "product_primary": products_prm.create_pipeline(),
        "product_features": products_feat.create_pipeline(),
        # -- Retail Loans (domain) -----------------------------------------
        "retail_loans": retail_loans.create_pipeline(),
        "retail_loans_staging": retail_loans_stg.create_pipeline(),
        "retail_loans_primary": retail_loans_prm.create_pipeline(),
        "retail_loans_intermediate": retail_loans_int.create_pipeline(),
        "retail_loans_features": retail_loans_feat.create_pipeline(),
        # -- Schema intelligence -------------------------------------------
        "schema_intelligence": si.create_pipeline(),
        # -- Sampling ------------------------------------------------------
        "dpl_sampling": sampling_dpl.create_pipeline(),
        "overdue_sampling": sampling_overdue.create_pipeline(),
        "aecb_sampling": sampling_aecb.create_pipeline(),
        "demographics_sampling": sampling_demo.create_pipeline(),
        "ddi_sampling": sampling_ddi.create_pipeline(),
        "way4_sampling": sampling_way4.create_pipeline(),
        "retail_loans_sampling": sampling_retail.create_pipeline(),
        "dcore_sampling": sampling_dcore.create_pipeline(),
        # -- Validation ----------------------------------------------------
        "validate_mpdpd": validation_mpdpd.create_pipeline(),
        "validate_bureau_alerts": validation_bureau.create_pipeline(),
        "validate_demographics": validation_demographics.create_pipeline(),
        "validate_dcore_cc_180_plus": validation_dcore_cc_180_plus.create_pipeline(),
        # -- DCORE (Collections Management System) -------------------------
        "dcore": dcore.create_pipeline(),
        "dcore_staging": dcore_stg.create_pipeline(),
        "dcore_primary": dcore_prm.create_pipeline(),
        "dcore_intermediate": dcore_int.create_pipeline(),
        "dcore_features": dcore_feat.create_pipeline(),
        # -- Model variant pipelines (namespaced by model_id) --------------
        # Full pipelines — run with: kedro run --env=dev --pipeline=<model_id>
        "cc_60_180": cc_way4.create_pipeline(),
        "cc_180_plus": cc_way4.create_180_plus_pipeline(),
        "rl_60_180": retail_loans.create_rl_60_180_pipeline(),
        "rl_180_plus": retail_loans.create_rl_180_plus_pipeline(),
        # Sub-pipelines for incremental cc_60_180 runs
        "cc_60_180.spine": cc_way4_spine.create_pipeline(),
        "cc_60_180.staging": cc_way4_stg.create_pipeline(),
        "cc_60_180.target": cc_way4_target.create_pipeline(),
        "cc_60_180.features": cc_way4_feat.create_pipeline(),
        "cc_60_180.rl_scope": retail_loans.create_cc_scoped_pipeline(),
        # Bureau scoped to this model's spine CIFs (model_id set by ModelConfigHook)
        "cc_60_180.bureau": bureau.create_pipeline(),
        # Sub-pipelines for incremental cc_180_plus runs
        "cc_180_plus.spine": cc_way4_spine.create_180_plus_pipeline(),
        "cc_180_plus.staging": cc_way4_stg.create_pipeline(),
        "cc_180_plus.target": cc_way4_target.create_recovery_pipeline(),
        "cc_180_plus.features": cc_way4_feat.create_pipeline(),
        "cc_180_plus.rl_scope": retail_loans.create_cc_scoped_pipeline(),
        "cc_180_plus.bureau": bureau.create_pipeline(),
        # Sub-pipelines for incremental rl_60_180 / rl_180_plus runs
        "rl_60_180.spine": retail_loans_spine.create_pipeline(),
        "rl_60_180.staging": retail_loans_stg.create_pipeline(),
        "rl_60_180.target": retail_loans_target.create_pipeline(),
        "rl_60_180.features": retail_loans_feat.create_pipeline(),
        "rl_60_180.primary": retail_loans_prm.create_pipeline(),
        "rl_60_180.intermediate": retail_loans_int.create_pipeline(),
        "rl_60_180.cc_scope": cc_way4.create_rl_scoped_pipeline(),
        "rl_60_180.bureau": bureau.create_pipeline(),
        "rl_180_plus.spine": retail_loans_spine.create_180_plus_pipeline(),
        "rl_180_plus.staging": retail_loans_stg.create_pipeline(),
        "rl_180_plus.target": retail_loans_target.create_recovery_pipeline(),
        "rl_180_plus.features": retail_loans_feat.create_rl_180_plus_pipeline(),
        "rl_180_plus.primary": retail_loans_prm.create_pipeline(),
        "rl_180_plus.intermediate": retail_loans_int.create_pipeline(),
        "rl_180_plus.cc_scope": cc_way4.create_rl_scoped_pipeline(),
        "rl_180_plus.bureau": bureau.create_pipeline(),
        # -- CRX Persona (experimental, additive) ---------------------------
        # Revert: remove this entry + the import above + rm -r crx_persona/
        "crx_cc_full_history": crx_cc_full_history.create_pipeline(),
        "crx_cc_raw_extract": crx_cc_raw_extract.create_pipeline(),
        "crx_cc_a4_deterioration": crx_cc_a4_deterioration.create_pipeline(),
        "crx_cc_a2_locatability": crx_cc_a2_locatability.create_pipeline(),
        "crx_cc_a1_ability": crx_cc_a1_ability.create_pipeline(),
        "crx_cc_obs_base": crx_obs_base.create_cc_pipeline(),
        "crx_rl_obs_base": crx_obs_base.create_rl_pipeline(),
        "crx_cc_uc1_stated": crx_cc_uc1_stated.create_pipeline(),
        "crx_rl_uc1_stated": crx_rl_uc1_stated.create_pipeline(),
        "crx_cc_a3_payment_credibility": (
            crx_cc_a3_payment_credibility.create_pipeline()
        ),
        "crx_rl_full_history": crx_rl_full_history.create_pipeline(),
        "crx_rl_a4_deterioration": crx_rl_a4_deterioration.create_pipeline(),
        "crx_rl_a1_ability": crx_rl_a1_ability.create_pipeline(),
        "crx_rl_a2_locatability": crx_rl_a2_locatability.create_pipeline(),
        "crx_rl_a3_payment_credibility": (
            crx_rl_a3_payment_credibility.create_pipeline()
        ),
        # TEMPORARY (bundle 28): removed by the cleanup
        # -- Digital login (OMB) --------------------------------------------
        "digital_login": dl.create_pipeline(),
        "location_features": location_features.create_pipeline(),
        # -- Genesys / PCA interactions ----------------------------------------
        "genesys": genesys.create_pipeline(),
        # -- Default ---------------------------------------------------------
        "__default__": cc_way4.create_pipeline(),
        "rerun": model_input.create_features_pipeline()
        + model_training.create_pipeline()
        + model_reporting.create_pipeline(),
        "rerun_full": model_input.create_base_pipeline()
        + model_input.create_features_pipeline()
        + model_training.create_pipeline()
        + model_reporting.create_pipeline(),
    }
`````

### FILE: `src/enbd_collections/pipelines/casa/b32_check.py`
action: add · new sha256 `64902794d812b602ea2324b071b836a6a513a962f60f6446e474dc93119367cb` · new trailing newline: yes

New:

`````python
"""TEMPORARY (bundle 32): ``feat_cif_casa_balance_monthly`` before and after the switch
of ``wm_fea_casa_eod_avg_balance`` from every ``adv_load_date`` partition to one.

``casa_b32_snapshot`` (run before ``casa_features``) copies the persisted table into
``casa_b32_old_balance`` (explicit entry in ``catalog_tmp_b32_check.yml``).
``casa_b32_compare`` (run after ``casa_features``) logs, for ``model_id``, per month the
two tables share:

- rows only in the old table, only in the new one, in both;
- of the rows in both with a balance on both sides: the share equal (within 0.01 AED),
  the median and p99 absolute difference of the unequal ones, and the share where the
  new balance is lower;
- balance NULL on one side only, and ``casa_flow`` disagreements.

Months after the old table's last month are new and left out. Removed by the bundle's
cleanup.

    kedro run --pipeline=casa_b32_snapshot      (before casa_features)
    kedro run --pipeline=casa_b32_compare       (after casa_features)
"""

import logging

from kedro.pipeline import Pipeline, node
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

logger = logging.getLogger(__name__)
TAGS = ["casa", "b32_check"]
KEY = ["cif_id", "month_end"]


def snapshot(balance: DataFrame) -> DataFrame:
    """The persisted table as it is."""
    return balance


def _side(df: DataFrame, tag: str) -> DataFrame:
    return df.select(
        *KEY,
        F.col("casa_balance").alias(f"{tag}_bal"),
        F.col("casa_flow").alias(f"{tag}_flow"),
        F.lit(1).alias(f"in_{tag}"),
    )


def compare(old: DataFrame, new: DataFrame, model_id: str) -> None:
    """Log the ``B32 CASA OLD NEW`` block (see the module docstring)."""
    last_old = old.agg(F.max("month_end")).first()[0]
    new = new.filter(F.col("month_end") <= last_old)
    joined = (
        _side(old, "o")
        .join(_side(new, "n"), KEY, "full")
        .withColumn("d", F.abs(F.col("o_bal") - F.col("n_bal")))
        .withColumn("ud", F.when(F.col("d") > 0.01, F.col("d")))
    )
    in_o, in_n = F.col("in_o").isNotNull(), F.col("in_n").isNotNull()
    rows = (
        joined.groupBy("month_end")
        .agg(
            F.sum((in_o & ~in_n).cast("int")).alias("only_old"),
            F.sum((in_n & ~in_o).cast("int")).alias("only_new"),
            F.sum((in_o & in_n).cast("int")).alias("both"),
            F.count("d").alias("n_bal"),
            F.count("ud").alias("n_diff"),
            F.expr("percentile_approx(ud, 0.5)").alias("p50"),
            F.expr("percentile_approx(ud, 0.99)").alias("p99"),
            F.count(F.when(F.col("n_bal") < F.col("o_bal"), F.col("ud"))).alias(
                "n_lower"
            ),
            F.count(
                F.when(
                    in_o & in_n & (F.col("o_bal").isNull() != F.col("n_bal").isNull()),
                    1,
                )
            ).alias("null_one_side"),
            F.count(F.when(F.col("o_flow") != F.col("n_flow"), 1)).alias("flow_diff"),
        )
        .orderBy("month_end")
        .collect()
    )
    lines = [
        f"  model_id {model_id}",
        (
            "  month_end: only_old / only_new / both | equal % of n_bal (n_bal) |"
            " unequal p50 / p99 abs diff, new lower % | balance NULL one side |"
            " flow diff"
        ),
    ]
    for r in rows:
        equal = 100 * (r["n_bal"] - r["n_diff"]) / r["n_bal"] if r["n_bal"] else 0.0
        lower = 100 * r["n_lower"] / r["n_diff"] if r["n_diff"] else 0.0
        lines.append(
            f"  {r['month_end']}: {r['only_old']} / {r['only_new']} / {r['both']}"
            f" | {equal:.2f}% ({r['n_bal']}) | {r['p50']} / {r['p99']}, {lower:.1f}%"
            f" | {r['null_one_side']} | {r['flow_diff']}"
        )
    name = "B32 CASA OLD NEW"
    logger.info("\n=== %s START ===\n%s\n=== %s END ===", name, "\n".join(lines), name)


def create_snapshot_pipeline() -> Pipeline:
    """Copy the persisted ``feat_cif_casa_balance_monthly`` aside."""
    return Pipeline(
        [
            node(
                func=snapshot,
                inputs="feat_cif_casa_balance_monthly",
                outputs="casa_b32_old_balance",
                name="casa_b32_snapshot",
                tags=TAGS,
            )
        ]
    )


def create_compare_pipeline() -> Pipeline:
    """Log the old x new comparison."""
    return Pipeline(
        [
            node(
                func=compare,
                inputs={
                    "old": "casa_b32_old_balance",
                    "new": "feat_cif_casa_balance_monthly",
                    "model_id": "params:model_id",
                },
                outputs=None,
                name="casa_b32_compare",
                tags=TAGS,
            )
        ]
    )
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
Clean up after mirror bundle 32_wm_snapshot_fallback.md, on the bundle's branch.
- Remove `src/enbd_collections/pipelines/casa/b32_check.py`, `conf/base/catalog/catalog_tmp_b32_check.yml`, and from `pipeline_registry.py` the `b32_check` import and the `casa_b32_snapshot` / `casa_b32_compare` entries.
- HDFS, for each model_id that ran the check: `hdfs dfs -rm -r <hdfs_path>/<model_id>/<feat folder>/b32_check` (path from `catalog_tmp_b32_check.yml`).
- Remove `data/input/mirror_bundles/`.
- Keep `WMSnapshotDataset`, the switched catalog entries and `wm_snapshot_required_from`.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
