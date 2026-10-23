# Mirror bundle 02 — A1 internal returns in the engine, more B01 diagnostics, cif_id from cc_spine

apply_bundle version: 5 · built 2026-10-23 from `dcf7cf1..6b30cb2` · source: 0 added, 7 replaced, 0 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 6). Copy each command block
exactly as it is.

### In UAT

**Step 1.** Continue on the branch of the earlier bundle (nothing uncommitted on it):

```bash
git checkout feature/persona_redesign_b01 && git pull && git status --short
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/02_a1_engine_checks.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script from the *Apply script* section at the bottom (prints `apply_bundle.py written`):

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '02_a1_engine_checks.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')"
```

**Step 4.** Apply — checks every file first, writes, compiles and imports; must end with `APPLY PASSED`:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/02_a1_engine_checks.md --apply --accept src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py --accept src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/nodes.py --accept src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/pipeline.py
```

The `--accept` files are known to differ from the bundle's base copy (a
transcription slip, or an edit made at work that this bundle already contains);
they are replaced as a whole. Any other **CONFLICT**: stop and send the diff back.

**Step 5.** Look at what changed (nothing under `data/input/` shows up):

```bash
git status && git diff --stat
```

**Step 6.** Commit the source only, and push:

```bash
git add src conf && git commit -m "crx_persona A1: internal returns in the engine, B01 diagnostics, cif_id from cc_spine (mirror bundle 02)" && git push
```

**Undo** (before step 6) — restores every touched file exactly:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/02_a1_engine_checks.md --revert
```

### In PROD

**Step 7.** Get the branch:

```bash
git fetch origin && git checkout feature/persona_redesign_b01 && git pull
```

**Step 8.** Run the check pipeline (terminal), first for `cc_60_180` (the `model_id` in
`conf/dev/globals_dev.yml`):

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability_b01_check
```

Paste back the three blocks, each from `=== B01 … START ===` to `=== B01 … END ===`:
`B01 DISTRESS`, `B01 SALARY` and `B01 OUTPUT` (aggregates only, no customer rows). Text is
best, if you can copy it out; otherwise one photo per block.

**Step 9.** Same for `cc_180_plus`: in `conf/dev/globals_dev.yml` switch `model_id` from
`cc_60_180` to `cc_180_plus`, run step 8 again, paste the three blocks, then switch
`model_id` back (do not commit this switch). This must print nothing afterwards:

```bash
git diff --stat conf/dev/globals_dev.yml
```

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** A follow-up to bundle 01 on the same branch, before its cleanup:

- **Internal returns move into the shared engine.** The workplace assistant's
  `build_cc_internal_returns` (`cc_a1_ability_v2/nodes.py`) becomes
  `a1_ability.build_internal_returns`, so RL A1 can reuse it. Same source and filter
  (`comp_financial_tran_repos_dly`, scoped by CIF, 100-day floor, `reason_for_excluding` in
  `CHEQUE RETURNS` / `DDS Rejects/Reversal` / `RETURNS`). Two changes: it now also prunes
  partitions on `edp_load_date`, and it keeps the reason as a column for the check.
  Catalog entry `crx_cc_a1_internal_returns` is unchanged.
- **The observation base takes `cif_id` from `cc_spine`** (no more `prm_contract` →
  `prm_client` bridge; O44).
- **More diagnostics in the temporary check** (`b01_check.py`):
  - `B01 OUTPUT` adds the income level × liquidity level crosstab and the distress-flag
    count;
  - `B01 SALARY` compares recovered salary months with `payroll_flag` in the same month, the
    month before and the month after, plus credit amounts by payroll flag;
  - `B01 DISTRESS` (new) shows rows flagged by bureau bounces vs internal returns, and
    events / rows flagged per internal reason.

The files the workplace assistant edited (`a1_ability/signals.py`,
`cc_a1_ability_v2/nodes.py`, `cc_a1_ability_v2/pipeline.py`) are replaced as a whole via
`--accept`; this bundle already contains that change.

## Instructions for the workplace assistant

1. Do not retype or hand-edit code from this file; `apply_bundle.py` writes it.
2. `--apply` must print **APPLY PASSED**. On CONFLICT (other than an `--accept`ed
   file) the workplace file differs from the version this bundle was built from:
   stop and show the printed diff to the user.
3. `DAMAGED` means the markdown copy was altered — recopy the raw file.
4. If an import fails, run `--revert` and report.
5. Touch nothing outside the manifest. Never commit `data/input/mirror_bundles/`.

## Manifest

| Action | Path |
|---|---|
| replace | `src/enbd_collections/pipelines/crx_persona/_common.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/b01_check.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/obs_base/pipeline.py` |

## Files

### FILE: `src/enbd_collections/pipelines/crx_persona/_common.py`
action: replace · base sha256 `69266100d0a55b19bcd5cacce6e406bd06e056c3db65e40b54c5aec9759813a1` · base trailing newline: yes · new sha256 `c9b8cfc76650dba8cafa36b70691c924c3af5783ce4efa3b11628f3020656e91` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Shared building blocks for the crx_persona axes.

Every axis works at the observation grain ``(account_id, observation_date)`` and looks
up customer-level sources by ``cif_id``. The helpers here encode the conventions once:

* missing source columns stop the run (``require_columns``);
* point-in-time lookups read strictly before the observation date and can be bounded in
  age (``pit_latest``), window aggregates read ``[start, observation_date)``
  (``window_agg``);
* source partition floors follow from the earliest observation date
  (``lookback_floor``);
* logging is opt-in and costs one job (``log_distribution``).
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Sequence

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.pipelines.crx_persona._spine_utils import _build_cif_bridge

LOG = logging.getLogger(__name__)

GRAIN = ("account_id", "observation_date")


def require_columns(df: DataFrame, columns: Sequence[str], source: str) -> None:
    """Raise if ``df`` lacks any of ``columns`` — a renamed source must fail the run."""
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns {missing}")


def parse_yyyymmdd(col: str) -> Column:
    """``20260531`` (int or string) -> date."""
    return F.to_date(F.col(col).cast("string"), "yyyyMMdd")


def _days_before(anchor: Column, days: int) -> Column:
    return F.date_sub(anchor, days)


def pit_latest(  # pylint: disable=too-many-arguments
    base: DataFrame,
    src: DataFrame,
    *,
    date_col: str,
    value_cols: Sequence[str],
    key: str = "cif_id",
    anchor: Column | None = None,
    max_age_days: int | None = None,
    inclusive: bool = False,
) -> DataFrame:
    """Latest ``src`` row dated before each base row's anchor, per ``GRAIN``.

    ``src`` must carry ``key``, ``date_col`` (a date) and ``value_cols``. The anchor
    defaults to ``observation_date``; ``inclusive`` also accepts rows dated on it (same-
    day snapshots). ``max_age_days`` drops rows older than that, so a stale record never
    stands in for a current one. Ties on the date are broken by the values (descending),
    so reruns agree. Returns ``GRAIN + value_cols`` for base rows with a match only.
    """
    anchor = F.col("observation_date") if anchor is None else anchor
    before = (
        F.col("_d") <= F.col("_anchor") if inclusive else F.col("_d") < F.col("_anchor")
    )
    cond = before
    if max_age_days is not None:
        cond = cond & (F.col("_d") >= _days_before(F.col("_anchor"), max_age_days))
    order = [F.col("_d").desc(), *[F.col(c).desc_nulls_last() for c in value_cols]]
    return (
        base.select(*GRAIN, key, anchor.alias("_anchor"))
        .join(src.select(key, F.col(date_col).alias("_d"), *value_cols), on=key)
        .filter(cond)
        .withColumn(
            "_rn", F.row_number().over(Window.partitionBy(*GRAIN).orderBy(*order))
        )
        .filter(F.col("_rn") == 1)
        .select(*GRAIN, *value_cols)
    )


def window_agg(  # pylint: disable=too-many-arguments
    base: DataFrame,
    src: DataFrame,
    *,
    date_col: str,
    aggs: Sequence[Column],
    days: int | None = None,
    months: int | None = None,
    key: str = "cif_id",
) -> DataFrame:
    """Aggregate ``src`` rows dated in a window ending before each observation date.

    ``days``: ``[obs - days, obs)``. ``months``: whole calendar months
    ``[trunc(obs) - months, trunc(obs))`` — for month-stamped series.
    ``src`` holds ``key``, ``date_col`` and the columns ``aggs`` read.
    Returns ``GRAIN + aggs`` for base rows with at least one row in the window.
    """
    if (days is None) == (months is None):
        raise ValueError("give exactly one of days / months")
    obs = F.col("observation_date")
    if days is not None:
        start, end = _days_before(obs, days), obs
    else:
        end = F.trunc(obs, "month")
        start = F.add_months(end, -months)
    return (
        base.select(*GRAIN, key)
        .join(src, on=key)
        .filter((F.col(date_col) >= start) & (F.col(date_col) < end))
        .groupBy(*GRAIN)
        .agg(*aggs)
    )


def lookback_floor(base: DataFrame, days: int) -> str:
    """ISO date ``days`` before the earliest observation date (partition floor)."""
    first: date = base.agg(F.min("observation_date")).first()[0]
    return (first - timedelta(days=days)).isoformat()


def left_join_all(base: DataFrame, parts: Sequence[DataFrame]) -> DataFrame:
    """Left-join every part onto ``base.select(*GRAIN)`` on ``GRAIN``."""
    result = base.select(*GRAIN)
    for part in parts:
        result = result.join(part, on=list(GRAIN), how="left")
    return result


def log_distribution(df: DataFrame, col: str, name: str, enabled: bool) -> None:
    """Log the value distribution of ``col`` (one job) when ``enabled``."""
    if not enabled:
        return
    rows = df.groupBy(col).count().orderBy(col).collect()
    total = sum(r["count"] for r in rows)
    LOG.info("%s — %s distribution (n=%d)", name, col, total)
    for r in rows:
        LOG.info(
            "  %-28s %9d  (%5.1f%%)",
            r[col],
            r["count"],
            100.0 * r["count"] / max(total, 1),
        )


# ── Observation base ──────────────────────────────────────────────────────────


def build_cc_obs_base(
    cc_spine: DataFrame, contract: DataFrame, client: DataFrame
) -> DataFrame:
    """Every CC spine row with its ``cif_id`` (NULL if the contract has no client).

    Rows without a CIF are kept: customer-level signals are simply absent for them.
    """
    spine = cc_spine.select(
        F.col("contract_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date"),
    ).dropDuplicates(list(GRAIN))
    bridge = _build_cif_bridge(contract, client).select(
        F.col("contract_id").cast("string").alias("account_id"), "cif_id"
    )
    return spine.join(bridge, on="account_id", how="left")


def build_rl_obs_base(rl_spine: DataFrame) -> DataFrame:
    """Every RL spine row with the ``cif_id`` the spine already carries."""
    return rl_spine.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        "cif_id",
    ).dropDuplicates(list(GRAIN))
`````

New:

`````python
"""Shared building blocks for the crx_persona axes.

Every axis works at the observation grain ``(account_id, observation_date)`` and looks
up customer-level sources by ``cif_id``. The helpers here encode the conventions once:

* missing source columns stop the run (``require_columns``);
* point-in-time lookups read strictly before the observation date and can be bounded in
  age (``pit_latest``), window aggregates read ``[start, observation_date)``
  (``window_agg``);
* source partition floors follow from the earliest observation date
  (``lookback_floor``);
* logging is opt-in and costs one job (``log_distribution``).
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Sequence

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F


LOG = logging.getLogger(__name__)

GRAIN = ("account_id", "observation_date")


def require_columns(df: DataFrame, columns: Sequence[str], source: str) -> None:
    """Raise if ``df`` lacks any of ``columns`` — a renamed source must fail the run."""
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns {missing}")


def parse_yyyymmdd(col: str) -> Column:
    """``20260531`` (int or string) -> date."""
    return F.to_date(F.col(col).cast("string"), "yyyyMMdd")


def _days_before(anchor: Column, days: int) -> Column:
    return F.date_sub(anchor, days)


def pit_latest(  # pylint: disable=too-many-arguments
    base: DataFrame,
    src: DataFrame,
    *,
    date_col: str,
    value_cols: Sequence[str],
    key: str = "cif_id",
    anchor: Column | None = None,
    max_age_days: int | None = None,
    inclusive: bool = False,
) -> DataFrame:
    """Latest ``src`` row dated before each base row's anchor, per ``GRAIN``.

    ``src`` must carry ``key``, ``date_col`` (a date) and ``value_cols``. The anchor
    defaults to ``observation_date``; ``inclusive`` also accepts rows dated on it (same-
    day snapshots). ``max_age_days`` drops rows older than that, so a stale record never
    stands in for a current one. Ties on the date are broken by the values (descending),
    so reruns agree. Returns ``GRAIN + value_cols`` for base rows with a match only.
    """
    anchor = F.col("observation_date") if anchor is None else anchor
    before = (
        F.col("_d") <= F.col("_anchor") if inclusive else F.col("_d") < F.col("_anchor")
    )
    cond = before
    if max_age_days is not None:
        cond = cond & (F.col("_d") >= _days_before(F.col("_anchor"), max_age_days))
    order = [F.col("_d").desc(), *[F.col(c).desc_nulls_last() for c in value_cols]]
    return (
        base.select(*GRAIN, key, anchor.alias("_anchor"))
        .join(src.select(key, F.col(date_col).alias("_d"), *value_cols), on=key)
        .filter(cond)
        .withColumn(
            "_rn", F.row_number().over(Window.partitionBy(*GRAIN).orderBy(*order))
        )
        .filter(F.col("_rn") == 1)
        .select(*GRAIN, *value_cols)
    )


def window_agg(  # pylint: disable=too-many-arguments
    base: DataFrame,
    src: DataFrame,
    *,
    date_col: str,
    aggs: Sequence[Column],
    days: int | None = None,
    months: int | None = None,
    key: str = "cif_id",
) -> DataFrame:
    """Aggregate ``src`` rows dated in a window ending before each observation date.

    ``days``: ``[obs - days, obs)``. ``months``: whole calendar months
    ``[trunc(obs) - months, trunc(obs))`` — for month-stamped series.
    ``src`` holds ``key``, ``date_col`` and the columns ``aggs`` read.
    Returns ``GRAIN + aggs`` for base rows with at least one row in the window.
    """
    if (days is None) == (months is None):
        raise ValueError("give exactly one of days / months")
    obs = F.col("observation_date")
    if days is not None:
        start, end = _days_before(obs, days), obs
    else:
        end = F.trunc(obs, "month")
        start = F.add_months(end, -months)
    return (
        base.select(*GRAIN, key)
        .join(src, on=key)
        .filter((F.col(date_col) >= start) & (F.col(date_col) < end))
        .groupBy(*GRAIN)
        .agg(*aggs)
    )


def lookback_floor(base: DataFrame, days: int) -> str:
    """ISO date ``days`` before the earliest observation date (partition floor)."""
    first: date = base.agg(F.min("observation_date")).first()[0]
    return (first - timedelta(days=days)).isoformat()


def left_join_all(base: DataFrame, parts: Sequence[DataFrame]) -> DataFrame:
    """Left-join every part onto ``base.select(*GRAIN)`` on ``GRAIN``."""
    result = base.select(*GRAIN)
    for part in parts:
        result = result.join(part, on=list(GRAIN), how="left")
    return result


def log_distribution(df: DataFrame, col: str, name: str, enabled: bool) -> None:
    """Log the value distribution of ``col`` (one job) when ``enabled``."""
    if not enabled:
        return
    rows = df.groupBy(col).count().orderBy(col).collect()
    total = sum(r["count"] for r in rows)
    LOG.info("%s — %s distribution (n=%d)", name, col, total)
    for r in rows:
        LOG.info(
            "  %-28s %9d  (%5.1f%%)",
            r[col],
            r["count"],
            100.0 * r["count"] / max(total, 1),
        )


# ── Observation base ──────────────────────────────────────────────────────────


def _obs_base(spine: DataFrame, id_col: str) -> DataFrame:
    """Every spine row with the ``cif_id`` the spine already carries.

    Rows without a CIF are kept: customer-level signals are simply absent for them.
    """
    return spine.select(
        F.col(id_col).cast("string").alias("account_id"),
        F.col("observation_date").cast("date"),
        "cif_id",
    ).dropDuplicates(list(GRAIN))


def build_cc_obs_base(cc_spine: DataFrame) -> DataFrame:
    return _obs_base(cc_spine, "contract_id")


def build_rl_obs_base(rl_spine: DataFrame) -> DataFrame:
    return _obs_base(rl_spine, "account_id")
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/__init__.py`
action: replace · base sha256 `de7eff27ace0fdcdc5690de1b1cd9c56a44085dae4e10e8c75e0a33ae1cecf4e` · base trailing newline: yes · new sha256 `0b214911e28bfaa58483e97adf6166704e7c38e15fa4b4420f25a0c4f31edfa2` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A1 ability engine shared by the CC and RL ability pipelines."""

from .classify import build_a1_ability
from .signals import (
    build_distress_signals,
    build_income_signals,
    build_liquidity_signals,
)

__all__ = [
    "build_a1_ability",
    "build_distress_signals",
    "build_income_signals",
    "build_liquidity_signals",
]
`````

New:

`````python
"""A1 ability engine shared by the CC and RL ability pipelines."""

from .classify import build_a1_ability
from .signals import (
    build_distress_signals,
    build_income_signals,
    build_internal_returns,
    build_liquidity_signals,
)

__all__ = [
    "build_a1_ability",
    "build_distress_signals",
    "build_income_signals",
    "build_internal_returns",
    "build_liquidity_signals",
]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py`
action: replace · base sha256 `179261c999a45c68948c2aeffd289156b2e06b61c6def24ce53f0779688c2f71` · base trailing newline: yes · new sha256 `971c756da1d085bda9efe3843620d86005d2beb9af2c403e5c66ae1947838880` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A1_ability_spec.md`` (GRR workbook A1_ability_20261022).

"The last 3 months" are the three complete calendar months before the observation month
(m1 = the month before, m2, m3); "the prior 3 months" are m4–m6. The builders return the
amounts the classifier compares with its thresholds:

* income    — salary received in each month (internal credit or bureau salary,
              the larger);
* liquidity — CASA average balance in each month, largest single external card payment;
* activity  — any CASA transaction in the last 3 months (the Unknown gate);
* distress  — a cheque bounce or direct-debit return in the last 3 months.

Customer-level sources are always read for the whole CIF — all the customer's accounts —
never for the scored account_id alone (an RL account_id is not a CASA account).
"""

from __future__ import annotations

from typing import Sequence

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import (
    GRAIN,
    left_join_all,
    lookback_floor,
    parse_yyyymmdd,
    require_columns,
)

_CASA_MONTH_COL = "ft_avg_casa_eod_balance_in_last_0_3_weeks_avg"  # CA+SA, ~1 month
_CASA_IN_COL = "ft_inflow_casa_amt_in_last_0_0_weeks_sum"
_CASA_OUT_COL = "ft_outflow_casa_amt_in_last_0_0_weeks_sum"


def _month_index(date: Column) -> Column:
    """1 for the month before the observation month, 2 for the one before, …"""
    obs_month = F.trunc(F.col("observation_date"), "month")
    return F.months_between(obs_month, F.trunc(date, "month")).cast("int")


def _by_month(obs: DataFrame, series: DataFrame, value: str, prefix: str) -> DataFrame:
    """Spread a ``(cif_id, month, value)`` series over ``{prefix}_m1 … _m6`` per
    observation (NULL where the month has no value)."""
    return (
        obs.select(*GRAIN, "cif_id")
        .join(series, on="cif_id")
        .withColumn("_k", _month_index(F.col("month")))
        .filter(F.col("_k").between(1, 6))
        .groupBy(*GRAIN)
        .agg(
            *[
                F.max(F.when(F.col("_k") == i, F.col(value))).alias(f"{prefix}_m{i}")
                for i in range(1, 7)
            ]
        )
    )


def _last_3_months(
    obs: DataFrame, src: DataFrame, date_col: str, aggs: Sequence[Column]
) -> DataFrame:
    """Aggregate ``src`` rows dated in the last 3 complete months, per observation."""
    return (
        obs.select(*GRAIN, "cif_id")
        .join(src, on="cif_id")
        .filter(_month_index(F.col(date_col)).between(1, 3))
        .groupBy(*GRAIN)
        .agg(*aggs)
    )


# ── Income ────────────────────────────────────────────────────────────────────


def _internal_salary(wm_salary: DataFrame) -> DataFrame:
    """Salary credits by month, recovered from the weekly WM snapshots.

    Each snapshot carries the last salary credited and how many days before the snapshot
    it was, so snapshot date minus that gap is the credit date. Several snapshots see
    the same credit; they collapse to one value per month.

    TODO(sonnet): validate against ``feat_payroll_indicator`` (payroll months without a
    recovered credit and vice versa), and switch to an internal table with salary credit
    amounts per month if one exists.
    """
    require_columns(
        wm_salary,
        [
            "cif_id",
            "week_number",
            "ft_last_salary_amount",
            "ft_days_since_salary_transaction",
        ],
        "wm_fea_salary_days_since_increment",
    )
    credit_date = F.date_sub(
        parse_yyyymmdd("week_number"),
        F.col("ft_days_since_salary_transaction").cast("int"),
    )
    return wm_salary.select(
        "cif_id",
        F.trunc(credit_date, "month").alias("month"),
        F.col("ft_last_salary_amount").cast("double").alias("amount"),
    )


def _bureau_salary(salary_hist: DataFrame, cif_bridge: DataFrame) -> DataFrame:
    """Bureau-reported salary by month."""
    require_columns(
        salary_hist,
        [
            "subj_salcr_hist_hdr_file_id",
            "subj_salcr_hist_ref_mnth",
            "subj_salcr_hist_tot_sal_amt",
        ],
        "stg_aecb_salary_history",
    )
    require_columns(cif_bridge, ["bureau_file_id", "cif_id"], "prm_bureau_cif_bridge")
    bridge = cif_bridge.select(
        F.col("bureau_file_id").alias("subj_salcr_hist_hdr_file_id"), "cif_id"
    ).distinct()
    return salary_hist.join(bridge, on="subj_salcr_hist_hdr_file_id").select(
        "cif_id",
        F.to_date("subj_salcr_hist_ref_mnth", "MMyyyy").alias("month"),
        F.col("subj_salcr_hist_tot_sal_amt").cast("double").alias("amount"),
    )


def build_income_signals(
    obs_base: DataFrame,
    wm_salary: DataFrame,
    salary_hist: DataFrame,
    bureau_cif_bridge: DataFrame,
) -> DataFrame:
    """``income_m1 … income_m6``: salary received per month — the larger of the internal
    credit and the bureau salary (NULL: no salary that month)."""
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    monthly = (
        _internal_salary(wm_salary)
        .unionByName(_bureau_salary(salary_hist, bureau_cif_bridge))
        .groupBy("cif_id", "month")
        .agg(F.max("amount").alias("amount"))
    )
    return left_join_all(obs_base, [_by_month(obs, monthly, "amount", "income")])


# ── Liquidity and activity ────────────────────────────────────────────────────


def _casa_by_month(wm_casa_bal: DataFrame) -> DataFrame:
    """CASA (current + savings) average balance per month: the 4-week average at the
    month's last weekly snapshot."""
    require_columns(
        wm_casa_bal,
        ["cif_id", "week_number", _CASA_MONTH_COL],
        "wm_fea_casa_eod_avg_balance",
    )
    week = parse_yyyymmdd("week_number")
    last_in_month = F.max(
        F.struct(week.alias("w"), F.col(_CASA_MONTH_COL).cast("double").alias("v"))
    )
    return (
        wm_casa_bal.groupBy("cif_id", F.trunc(week, "month").alias("month"))
        .agg(last_in_month.alias("_last"))
        .select("cif_id", "month", F.col("_last.v").alias("balance"))
    )


def _ext_card_payments(
    obs: DataFrame, labelled_txn: DataFrame, beneficiary_cards: DataFrame
) -> DataFrame:
    """Largest single CASA payment to one of the customer's registered external credit
    cards in the last 3 months.

    ``raw_beneficiary_cards`` is a live snapshot: a card registered after the
    observation date still counts (mild look-ahead, accepted).
    """
    require_columns(
        labelled_txn,
        [
            "cif_id",
            "in_out_flow",
            "product_category",
            "tran_date",
            "tran_amt",
            "transaction_acid",
        ],
        "wm_pri_labelled_transactions",
    )
    require_columns(
        beneficiary_cards,
        ["instrument_number", "instrument_type"],
        "raw_beneficiary_cards",
    )
    cards = (
        beneficiary_cards.filter(F.col("instrument_type") == "CARD_NUMBER")
        .select(F.col("instrument_number").alias("transaction_acid"))
        .distinct()
    )
    src = (
        labelled_txn.filter(
            (F.col("tran_date") >= F.lit(lookback_floor(obs, 100)))
            & (F.col("in_out_flow") == "outflow")
            & (F.col("product_category") == "CASA")
        )
        .join(F.broadcast(cards), on="transaction_acid", how="leftsemi")
        .select(
            "cif_id", F.col("tran_date").cast("date"), F.col("tran_amt").cast("double")
        )
    )
    return _last_3_months(
        obs, src, "tran_date", [F.max("tran_amt").alias("ext_card_payment_max_3m")]
    )


def _casa_activity(obs: DataFrame, wm_casa_flow: DataFrame) -> DataFrame:
    """Any CASA credit or debit in the last 3 months."""
    require_columns(
        wm_casa_flow,
        ["cif_id", "week_number", _CASA_IN_COL, _CASA_OUT_COL],
        "wm_fea_casa_cc_inflow_outflow",
    )
    src = wm_casa_flow.select(
        "cif_id",
        parse_yyyymmdd("week_number").alias("week"),
        ((F.col(_CASA_IN_COL) > 0) | (F.col(_CASA_OUT_COL) > 0))
        .cast("int")
        .alias("_active"),
    )
    return _last_3_months(obs, src, "week", [F.max("_active").alias("casa_active_3m")])


def build_liquidity_signals(
    obs_base: DataFrame,
    wm_casa_bal: DataFrame,
    wm_casa_flow: DataFrame,
    labelled_txn: DataFrame,
    beneficiary_cards: DataFrame,
) -> DataFrame:
    """``casa_m1 … casa_m6``, ``ext_card_payment_max_3m``, ``casa_active_3m``."""
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    return left_join_all(
        obs_base,
        [
            _by_month(obs, _casa_by_month(wm_casa_bal), "balance", "casa"),
            _ext_card_payments(obs, labelled_txn, beneficiary_cards),
            _casa_activity(obs, wm_casa_flow),
        ],
    )


# ── Distress ──────────────────────────────────────────────────────────────────


def build_distress_signals(
    obs_base: DataFrame,
    bureau_alert: DataFrame,
    payment_order: DataFrame | None = None,
    internal_returns: DataFrame | None = None,
) -> DataFrame:
    """distress_flag: a cheque bounce or direct-debit (DDS) return in the last 3 months,
    from the bureau and from the bank's own records.

    * ``bureau_alert`` — bureau-reported bounced cheques (always wired);
    * ``payment_order`` — prm_bureau_payment_order returns; not in PROD yet;
    * ``internal_returns`` — the bank's own returned cheques / DDS returns as
      ``(cif_id, event_date)``; CC: ``cc_a1_ability_v2.nodes.build_cc_internal_returns``.
    """
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    require_columns(
        bureau_alert,
        ["cif_id", "extract_date", "bounced_cheque_amount"],
        "prm_bureau_alert_enriched",
    )
    events = bureau_alert.filter(F.col("bounced_cheque_amount") > 0).select(
        "cif_id", F.to_date("extract_date").alias("event_date")
    )
    if payment_order is not None:
        require_columns(
            payment_order,
            ["cif_id", "return_date", "reason_code"],
            "prm_bureau_payment_order",
        )
        events = events.unionByName(
            payment_order.filter(F.col("reason_code").isNotNull()).select(
                "cif_id", F.to_date("return_date").alias("event_date")
            )
        )
    if internal_returns is not None:
        require_columns(internal_returns, ["cif_id", "event_date"], "internal_returns")
        events = events.unionByName(
            internal_returns.select(
                "cif_id", F.to_date("event_date").alias("event_date")
            )
        )
    hits = _last_3_months(
        obs, events, "event_date", [F.max(F.lit(1)).alias("distress_flag")]
    )
    return left_join_all(obs_base, [hits]).fillna(0, subset=["distress_flag"])
`````

New:

`````python
"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A1_ability_spec.md`` (GRR workbook A1_ability_20261022).

"The last 3 months" are the three complete calendar months before the observation month
(m1 = the month before, m2, m3); "the prior 3 months" are m4–m6. The builders return the
amounts the classifier compares with its thresholds:

* income    — salary received in each month (internal credit or bureau salary,
              the larger);
* liquidity — CASA average balance in each month, largest single external card payment;
* activity  — any CASA transaction in the last 3 months (the Unknown gate);
* distress  — a cheque bounce or direct-debit return in the last 3 months.

Customer-level sources are always read for the whole CIF — all the customer's accounts —
never for the scored account_id alone (an RL account_id is not a CASA account).
"""

from __future__ import annotations

from typing import Sequence

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import (
    GRAIN,
    left_join_all,
    lookback_floor,
    parse_yyyymmdd,
    require_columns,
)

# reason_for_excluding values marking a returned cheque or DDS return (from a profiled
# sample of comp_financial_tran_repos_dly, not a code dictionary; checked in PROD).
RETURN_REASONS = ("CHEQUE RETURNS", "DDS Rejects/Reversal", "RETURNS")
_CASA_MONTH_COL = "ft_avg_casa_eod_balance_in_last_0_3_weeks_avg"  # CA+SA, ~1 month
_CASA_IN_COL = "ft_inflow_casa_amt_in_last_0_0_weeks_sum"
_CASA_OUT_COL = "ft_outflow_casa_amt_in_last_0_0_weeks_sum"


def _month_index(date: Column) -> Column:
    """1 for the month before the observation month, 2 for the one before, …"""
    obs_month = F.trunc(F.col("observation_date"), "month")
    return F.months_between(obs_month, F.trunc(date, "month")).cast("int")


def _by_month(obs: DataFrame, series: DataFrame, value: str, prefix: str) -> DataFrame:
    """Spread a ``(cif_id, month, value)`` series over ``{prefix}_m1 … _m6`` per
    observation (NULL where the month has no value)."""
    return (
        obs.select(*GRAIN, "cif_id")
        .join(series, on="cif_id")
        .withColumn("_k", _month_index(F.col("month")))
        .filter(F.col("_k").between(1, 6))
        .groupBy(*GRAIN)
        .agg(
            *[
                F.max(F.when(F.col("_k") == i, F.col(value))).alias(f"{prefix}_m{i}")
                for i in range(1, 7)
            ]
        )
    )


def _last_3_months(
    obs: DataFrame, src: DataFrame, date_col: str, aggs: Sequence[Column]
) -> DataFrame:
    """Aggregate ``src`` rows dated in the last 3 complete months, per observation."""
    return (
        obs.select(*GRAIN, "cif_id")
        .join(src, on="cif_id")
        .filter(_month_index(F.col(date_col)).between(1, 3))
        .groupBy(*GRAIN)
        .agg(*aggs)
    )


# ── Income ────────────────────────────────────────────────────────────────────


def _internal_salary(wm_salary: DataFrame) -> DataFrame:
    """Salary credits by month, recovered from the weekly WM snapshots.

    Each snapshot carries the last salary credited and how many days before the snapshot
    it was, so snapshot date minus that gap is the credit date. Several snapshots see
    the same credit; they collapse to one value per month.

    TODO(sonnet): validate against ``feat_payroll_indicator`` (payroll months without a
    recovered credit and vice versa), and switch to an internal table with salary credit
    amounts per month if one exists.
    """
    require_columns(
        wm_salary,
        [
            "cif_id",
            "week_number",
            "ft_last_salary_amount",
            "ft_days_since_salary_transaction",
        ],
        "wm_fea_salary_days_since_increment",
    )
    credit_date = F.date_sub(
        parse_yyyymmdd("week_number"),
        F.col("ft_days_since_salary_transaction").cast("int"),
    )
    return wm_salary.select(
        "cif_id",
        F.trunc(credit_date, "month").alias("month"),
        F.col("ft_last_salary_amount").cast("double").alias("amount"),
    )


def _bureau_salary(salary_hist: DataFrame, cif_bridge: DataFrame) -> DataFrame:
    """Bureau-reported salary by month."""
    require_columns(
        salary_hist,
        [
            "subj_salcr_hist_hdr_file_id",
            "subj_salcr_hist_ref_mnth",
            "subj_salcr_hist_tot_sal_amt",
        ],
        "stg_aecb_salary_history",
    )
    require_columns(cif_bridge, ["bureau_file_id", "cif_id"], "prm_bureau_cif_bridge")
    bridge = cif_bridge.select(
        F.col("bureau_file_id").alias("subj_salcr_hist_hdr_file_id"), "cif_id"
    ).distinct()
    return salary_hist.join(bridge, on="subj_salcr_hist_hdr_file_id").select(
        "cif_id",
        F.to_date("subj_salcr_hist_ref_mnth", "MMyyyy").alias("month"),
        F.col("subj_salcr_hist_tot_sal_amt").cast("double").alias("amount"),
    )


def build_income_signals(
    obs_base: DataFrame,
    wm_salary: DataFrame,
    salary_hist: DataFrame,
    bureau_cif_bridge: DataFrame,
) -> DataFrame:
    """``income_m1 … income_m6``: salary received per month — the larger of the internal
    credit and the bureau salary (NULL: no salary that month)."""
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    monthly = (
        _internal_salary(wm_salary)
        .unionByName(_bureau_salary(salary_hist, bureau_cif_bridge))
        .groupBy("cif_id", "month")
        .agg(F.max("amount").alias("amount"))
    )
    return left_join_all(obs_base, [_by_month(obs, monthly, "amount", "income")])


# ── Liquidity and activity ────────────────────────────────────────────────────


def _casa_by_month(wm_casa_bal: DataFrame) -> DataFrame:
    """CASA (current + savings) average balance per month: the 4-week average at the
    month's last weekly snapshot."""
    require_columns(
        wm_casa_bal,
        ["cif_id", "week_number", _CASA_MONTH_COL],
        "wm_fea_casa_eod_avg_balance",
    )
    week = parse_yyyymmdd("week_number")
    last_in_month = F.max(
        F.struct(week.alias("w"), F.col(_CASA_MONTH_COL).cast("double").alias("v"))
    )
    return (
        wm_casa_bal.groupBy("cif_id", F.trunc(week, "month").alias("month"))
        .agg(last_in_month.alias("_last"))
        .select("cif_id", "month", F.col("_last.v").alias("balance"))
    )


def _ext_card_payments(
    obs: DataFrame, labelled_txn: DataFrame, beneficiary_cards: DataFrame
) -> DataFrame:
    """Largest single CASA payment to one of the customer's registered external credit
    cards in the last 3 months.

    ``raw_beneficiary_cards`` is a live snapshot: a card registered after the
    observation date still counts (mild look-ahead, accepted).
    """
    require_columns(
        labelled_txn,
        [
            "cif_id",
            "in_out_flow",
            "product_category",
            "tran_date",
            "tran_amt",
            "transaction_acid",
        ],
        "wm_pri_labelled_transactions",
    )
    require_columns(
        beneficiary_cards,
        ["instrument_number", "instrument_type"],
        "raw_beneficiary_cards",
    )
    cards = (
        beneficiary_cards.filter(F.col("instrument_type") == "CARD_NUMBER")
        .select(F.col("instrument_number").alias("transaction_acid"))
        .distinct()
    )
    src = (
        labelled_txn.filter(
            (F.col("tran_date") >= F.lit(lookback_floor(obs, 100)))
            & (F.col("in_out_flow") == "outflow")
            & (F.col("product_category") == "CASA")
        )
        .join(F.broadcast(cards), on="transaction_acid", how="leftsemi")
        .select(
            "cif_id", F.col("tran_date").cast("date"), F.col("tran_amt").cast("double")
        )
    )
    return _last_3_months(
        obs, src, "tran_date", [F.max("tran_amt").alias("ext_card_payment_max_3m")]
    )


def _casa_activity(obs: DataFrame, wm_casa_flow: DataFrame) -> DataFrame:
    """Any CASA credit or debit in the last 3 months."""
    require_columns(
        wm_casa_flow,
        ["cif_id", "week_number", _CASA_IN_COL, _CASA_OUT_COL],
        "wm_fea_casa_cc_inflow_outflow",
    )
    src = wm_casa_flow.select(
        "cif_id",
        parse_yyyymmdd("week_number").alias("week"),
        ((F.col(_CASA_IN_COL) > 0) | (F.col(_CASA_OUT_COL) > 0))
        .cast("int")
        .alias("_active"),
    )
    return _last_3_months(obs, src, "week", [F.max("_active").alias("casa_active_3m")])


def build_liquidity_signals(
    obs_base: DataFrame,
    wm_casa_bal: DataFrame,
    wm_casa_flow: DataFrame,
    labelled_txn: DataFrame,
    beneficiary_cards: DataFrame,
) -> DataFrame:
    """``casa_m1 … casa_m6``, ``ext_card_payment_max_3m``, ``casa_active_3m``."""
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    return left_join_all(
        obs_base,
        [
            _by_month(obs, _casa_by_month(wm_casa_bal), "balance", "casa"),
            _ext_card_payments(obs, labelled_txn, beneficiary_cards),
            _casa_activity(obs, wm_casa_flow),
        ],
    )


# ── Distress ──────────────────────────────────────────────────────────────────


def build_distress_signals(
    obs_base: DataFrame,
    bureau_alert: DataFrame,
    payment_order: DataFrame | None = None,
    internal_returns: DataFrame | None = None,
) -> DataFrame:
    """distress_flag: a cheque bounce or direct-debit (DDS) return in the last 3 months,
    from the bureau and from the bank's own records.

    * ``bureau_alert`` — bureau-reported bounced cheques (always wired);
    * ``payment_order`` — prm_bureau_payment_order returns; not in PROD yet;
    * ``internal_returns`` — the bank's own returned cheques / DDS returns as
      ``(cif_id, event_date)`` from ``build_internal_returns``.
    """
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    require_columns(
        bureau_alert,
        ["cif_id", "extract_date", "bounced_cheque_amount"],
        "prm_bureau_alert_enriched",
    )
    events = bureau_alert.filter(F.col("bounced_cheque_amount") > 0).select(
        "cif_id", F.to_date("extract_date").alias("event_date")
    )
    if payment_order is not None:
        require_columns(
            payment_order,
            ["cif_id", "return_date", "reason_code"],
            "prm_bureau_payment_order",
        )
        events = events.unionByName(
            payment_order.filter(F.col("reason_code").isNotNull()).select(
                "cif_id", F.to_date("return_date").alias("event_date")
            )
        )
    if internal_returns is not None:
        require_columns(internal_returns, ["cif_id", "event_date"], "internal_returns")
        events = events.unionByName(
            internal_returns.select(
                "cif_id", F.to_date("event_date").alias("event_date")
            )
        )
    hits = _last_3_months(
        obs, events, "event_date", [F.max(F.lit(1)).alias("distress_flag")]
    )
    return left_join_all(obs_base, [hits]).fillna(0, subset=["distress_flag"])


def build_internal_returns(obs_base: DataFrame, casa_txn: DataFrame) -> DataFrame:
    """The bank's own returned cheques / DDS returns as ``(cif_id, event_date, reason)``,
    across all of the customer's CASA accounts.

    ``casa_txn`` is ``comp_financial_tran_repos_dly`` (2.4B rows): scoped to the
    observation base's CIFs before any other filter (R20), partitions pruned on
    ``edp_load_date``.
    """
    require_columns(
        casa_txn,
        ["cif_id", "edp_load_date", "tran_date", "reason_for_excluding"],
        "comp_financial_tran_repos_dly",
    )
    floor = F.lit(lookback_floor(obs_base, 100))
    cifs = obs_base.select("cif_id").filter(F.col("cif_id").isNotNull()).distinct()
    return (
        casa_txn.select("cif_id", "edp_load_date", "tran_date", "reason_for_excluding")
        .join(F.broadcast(cifs), on="cif_id", how="leftsemi")
        .filter(
            (F.col("edp_load_date") >= floor)
            & (F.col("tran_date") >= floor)
            & F.col("reason_for_excluding").isin(*RETURN_REASONS)
        )
        .select(
            "cif_id",
            F.to_date("tran_date").alias("event_date"),
            F.col("reason_for_excluding").alias("reason"),
        )
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/b01_check.py`
action: replace · base sha256 `4902f638057a7b6f8972d3f1ab11058d64ea03a8644dcda79679539d0803405b` · base trailing newline: yes · new sha256 `abe80aa8d256b3fd723e51600d0f980fa9c99657ef748c9cbecae53e4c33e510` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""TEMPORARY (mirror bundle 01): checks for the CC A1 rebuild, run in PROD.

The last nodes of the ``crx_cc_a1_ability_b01_check`` pipeline (aggregates only):

* ``compare_a1_outputs`` — the untouched ``crx_cc_a1_ability_v2`` against the new
  ``crx_cc_a1_ability_b01_check``; logs the ``B01 OUTPUT`` block;
* ``compare_salary_months`` — salary months recovered from the WM snapshots against
  ``feat_payroll_indicator``; logs the ``B01 SALARY`` block.

Removed by the bundle's cleanup.
"""

import logging

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)
_GRAIN = ["account_id", "observation_date"]


def _counts(df: DataFrame, col: str) -> dict:
    return {r[col]: r["count"] for r in df.groupBy(col).count().collect()}


def compare_a1_outputs(old: DataFrame, new: DataFrame, model_id: str) -> None:
    """Log old vs new state crosstab, level distributions and anchor coverage."""
    both = (
        new.select(
            *_GRAIN,
            F.col("a1_state").alias("new_state"),
            "a1_income_level",
            "a1_liquidity_level",
            "liquidity_anchor_amt",
        )
        .join(
            old.select(*_GRAIN, F.col("a1_state_v2").alias("old_state")), _GRAIN, "full"
        )
        .fillna({"old_state": "(absent)", "new_state": "(absent)"})
        .cache()
    )
    n = both.count()
    changed = both.filter(F.col("old_state") != F.col("new_state")).count()
    anchor = both.agg(
        F.avg(F.col("liquidity_anchor_amt").isNotNull().cast("double")).alias("share"),
        F.expr("percentile_approx(liquidity_anchor_amt, array(0.1, 0.5, 0.9))").alias(
            "q"
        ),
    ).first()
    lines = [
        "=== B01 OUTPUT START ===",
        f"model_id={model_id} rows={n} changed={changed} "
        f"({100.0 * changed / max(n, 1):.2f}%)",
        f"  income levels:    {_counts(both, 'a1_income_level')}",
        f"  liquidity levels: {_counts(both, 'a1_liquidity_level')}",
        f"  anchor present: {anchor['share'] or 0.0:.4f}  p10/p50/p90: {anchor['q']}",
    ]
    for r in (
        both.groupBy("old_state", "new_state")
        .count()
        .orderBy("old_state", "new_state")
        .collect()
    ):
        lines.append(f"  {r['old_state']:<18} -> {r['new_state']:<18} {r['count']:>9}")
    lines.append("=== B01 OUTPUT END ===")
    LOG.info("\n%s", "\n".join(lines))
    both.unpersist()


def compare_salary_months(
    obs_base: DataFrame, income: DataFrame, payroll: DataFrame
) -> None:
    """Log recovered salary months (income_m1..m3 > 0) against feat_payroll_indicator."""
    months = (
        income.join(obs_base.select(*_GRAIN, "cif_id"), _GRAIN)
        .select(
            "cif_id",
            F.explode(
                F.array(
                    *[
                        F.struct(
                            F.trunc(
                                F.add_months("observation_date", -k), "month"
                            ).alias("month"),
                            (F.coalesce(F.col(f"income_m{k}"), F.lit(0.0)) > 0).alias(
                                "recovered"
                            ),
                        )
                        for k in (1, 2, 3)
                    ]
                )
            ).alias("m"),
        )
        .select("cif_id", "m.month", "m.recovered")
        .filter(F.col("cif_id").isNotNull())
    )
    flags = (
        payroll.select(
            "cif_id",
            F.trunc(
                F.to_date(F.col("month_number").cast("string"), "yyyyMMdd"), "month"
            ).alias("month"),
            (F.col("payroll_flag") == 1).alias("payroll"),
        )
        .groupBy("cif_id", "month")
        .agg(F.max("payroll").alias("payroll"))
    )
    rows = (
        months.join(flags, ["cif_id", "month"], "left")
        .fillna({"payroll": False})
        .groupBy("recovered", "payroll")
        .count()
        .orderBy("recovered", "payroll")
        .collect()
    )
    lines = ["=== B01 SALARY START ===", "  recovered  payroll_flag      count"]
    lines += [
        f"  {r['recovered']!s:<10} {r['payroll']!s:<13} {r['count']:>9}" for r in rows
    ]
    lines.append("=== B01 SALARY END ===")
    LOG.info("\n%s", "\n".join(lines))
`````

New:

`````python
"""TEMPORARY (mirror bundle 01): checks for the CC A1 rebuild, run in PROD.

The last nodes of the ``crx_cc_a1_ability_b01_check`` pipeline (aggregates only):

* ``compare_a1_outputs`` — the untouched ``crx_cc_a1_ability_v2`` against the new
  ``crx_cc_a1_ability_b01_check``, plus income × liquidity levels; ``B01 OUTPUT`` block;
* ``compare_salary_months`` — salary months recovered from the WM snapshots against
  ``feat_payroll_indicator`` in the same month and one month either side; ``B01 SALARY``;
* ``compare_distress_sources`` — bureau vs internal returns, and each internal
  ``reason_for_excluding`` value; ``B01 DISTRESS`` block.

Removed by the bundle's cleanup.
"""

import logging

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)
_GRAIN = ["account_id", "observation_date"]


def _counts(df: DataFrame, col: str) -> dict:
    return {r[col]: r["count"] for r in df.groupBy(col).count().collect()}


def _crosstab(df: DataFrame, a: str, b: str) -> list[str]:
    rows = df.groupBy(a, b).count().orderBy(a, b).collect()
    return [f"  {r[a]!s:<18} x {r[b]!s:<18} {r['count']:>9}" for r in rows]


def _log(name: str, lines: list[str]) -> None:
    block = [f"=== B01 {name} START ===", *lines, f"=== B01 {name} END ==="]
    LOG.info("\n%s", "\n".join(block))


def _in_last_3_months(date_col: str) -> Column:
    k = F.months_between(
        F.trunc("observation_date", "month"), F.trunc(F.col(date_col), "month")
    )
    return k.between(1, 3)


def compare_a1_outputs(old: DataFrame, new: DataFrame, model_id: str) -> None:
    """Old vs new state, level distributions and crosstab, anchor coverage."""
    both = (
        new.select(
            *_GRAIN,
            F.col("a1_state").alias("new_state"),
            "a1_income_level",
            "a1_liquidity_level",
            "a1_distress_flag",
            "liquidity_anchor_amt",
        )
        .join(
            old.select(*_GRAIN, F.col("a1_state_v2").alias("old_state")), _GRAIN, "full"
        )
        .fillna({"old_state": "(absent)", "new_state": "(absent)"})
        .cache()
    )
    n = both.count()
    changed = both.filter(F.col("old_state") != F.col("new_state")).count()
    anchor = both.agg(
        F.avg(F.col("liquidity_anchor_amt").isNotNull().cast("double")).alias("share"),
        F.expr("percentile_approx(liquidity_anchor_amt, array(0.1, 0.5, 0.9))").alias(
            "q"
        ),
    ).first()
    _log(
        "OUTPUT",
        [
            f"model_id={model_id} rows={n} changed={changed} "
            f"({100.0 * changed / max(n, 1):.2f}%)",
            f"  distress flag: {_counts(both, 'a1_distress_flag')}",
            f"  anchor present: {anchor['share'] or 0.0:.4f}  p10/p50/p90: {anchor['q']}",
            "  income level x liquidity level:",
            *_crosstab(both, "a1_income_level", "a1_liquidity_level"),
            "  old state x new state:",
            *_crosstab(both, "old_state", "new_state"),
        ],
    )
    both.unpersist()


def compare_salary_months(
    obs_base: DataFrame, income: DataFrame, payroll: DataFrame
) -> None:
    """Recovered salary months (income_m1..m3 > 0) against payroll_flag in the same
    month, the month before and the month after."""
    month = lambda k: F.trunc(F.add_months("observation_date", -k), "month")  # noqa: E731
    credits = (
        income.join(obs_base.select(*_GRAIN, "cif_id"), _GRAIN)
        .filter(F.col("cif_id").isNotNull())
        .select(
            "cif_id",
            F.explode(
                F.array(
                    *[
                        F.struct(
                            month(k).alias("month"),
                            F.col(f"income_m{k}").alias("amount"),
                        )
                        for k in (1, 2, 3)
                    ]
                )
            ).alias("m"),
        )
        .select(
            "cif_id",
            "m.month",
            "m.amount",
            (F.coalesce(F.col("m.amount"), F.lit(0.0)) > 0).alias("recovered"),
        )
    )
    flags = (
        payroll.select(
            "cif_id",
            F.trunc(
                F.to_date(F.col("month_number").cast("string"), "yyyyMMdd"), "month"
            ).alias("pmonth"),
            (F.col("payroll_flag") == 1).cast("int").alias("payroll"),
        )
        .groupBy("cif_id", "pmonth")
        .agg(F.max("payroll").alias("payroll"))
    )
    # payroll_prev: flag in the month before the credit month; payroll_next: the month after
    for shift, name in ((-1, "prev"), (0, "same"), (1, "next")):
        f = flags.select(
            "cif_id",
            F.add_months("pmonth", -shift).alias("month"),
            F.col("payroll").alias(f"payroll_{name}"),
        )
        credits = credits.join(f, ["cif_id", "month"], "left")
    credits = credits.fillna(
        0, ["payroll_prev", "payroll_same", "payroll_next"]
    ).cache()
    amounts = (
        credits.filter("recovered")
        .groupBy("payroll_same")
        .agg(
            F.expr("percentile_approx(amount, array(0.1, 0.5, 0.9))").alias("q"),
            F.avg((F.col("amount") >= 3000).cast("double")).alias("ge3000"),
        )
        .orderBy("payroll_same")
        .collect()
    )
    lines = []
    for name in ("same", "prev", "next"):
        lines += [f"  recovered x payroll flag ({name} month):"]
        lines += _crosstab(credits, "recovered", f"payroll_{name}")
    lines += ["  recovered credit amount by payroll flag (same month):"]
    lines += [
        f"  payroll={r['payroll_same']} p10/p50/p90={r['q']} "
        f"share>=3000={r['ge3000']:.3f}"
        for r in amounts
    ]
    _log("SALARY", lines)
    credits.unpersist()


def compare_distress_sources(
    obs_base: DataFrame, bureau_alert: DataFrame, internal_returns: DataFrame
) -> None:
    """Rows flagged by bureau bounces vs internal returns (last 3 complete months), and
    events / rows flagged per internal reason."""
    obs = obs_base.filter(F.col("cif_id").isNotNull()).select(*_GRAIN, "cif_id")
    bureau = bureau_alert.filter(F.col("bounced_cheque_amount") > 0).select(
        "cif_id", F.to_date("extract_date").alias("event_date")
    )
    internal = (
        obs.join(internal_returns, "cif_id")
        .filter(_in_last_3_months("event_date"))
        .cache()
    )
    hit = lambda df, name: (  # noqa: E731
        df.select(*_GRAIN).distinct().withColumn(name, F.lit(1))
    )
    flags = (
        obs.join(
            hit(
                obs.join(bureau, "cif_id").filter(_in_last_3_months("event_date")),
                "bureau",
            ),
            _GRAIN,
            "left",
        )
        .join(hit(internal, "internal"), _GRAIN, "left")
        .fillna(0, ["bureau", "internal"])
    )
    per_reason = (
        internal.groupBy("reason")
        .agg(
            F.count(F.lit(1)).alias("events"),
            F.countDistinct(*_GRAIN).alias("rows"),
        )
        .orderBy("reason")
        .collect()
    )
    lines = [f"  rows with a CIF: {obs.count()}", "  bureau x internal:"]
    lines += _crosstab(flags, "bureau", "internal")
    lines += ["  internal reason: events in window / rows flagged"]
    lines += [
        f"  {r['reason']:<24} {r['events']:>9} {r['rows']:>9}" for r in per_reason
    ]
    _log("DISTRESS", lines)
    internal.unpersist()
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/nodes.py`
action: replace · base sha256 `3f12c6fe7ee0f86e54a65a287174640a8694bf35f4e5b95c8e5e17b2ef869992` · base trailing newline: yes · new sha256 `5cb0d9f21a093685fc39936236a09c381eb18af5487326b1ae630b55d0a81036` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CC-specific parts of the A1 ability axis: the liquidity anchor and internal returns.

Everything else (evidence, levels, points, state) is the shared ``a1_ability`` engine.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, lookback_floor, pit_latest, require_columns
from .._dpd_journey import MODEL_ID_SEGMENT

# OVD_k holds the amount k cycles overdue (DPD bucket k+1): OVD_01 1-30 … OVD_06
# 151-180 DPD. OVD_07 (181-210) and the catch-all OVD_08 (211+) never anchor.
_OVERDUE_BUCKETS = [f"overdue_bucket_{i:02d}" for i in range(1, 7)]
# reason_for_excluding values marking a returned cheque or DDS return (profiled sample).
_RETURN_REASONS = ["CHEQUE RETURNS", "DDS Rejects/Reversal", "RETURNS"]
# A balance snapshot older than this means the card stopped reporting; no anchor then.
_BALANCE_MAX_AGE_D = 31


def build_cc_liquidity_anchor(
    obs_base: DataFrame, prm_balance: DataFrame, model_id: str
) -> DataFrame:
    """Amount in the oldest non-empty overdue bucket on the latest balance snapshot at
    or before the observation date — what the customer must pay to stop the roll.

    Only for the 60-180 segments: at 180+ the buckets no longer track what is due, so
    the anchor is NULL and A1 uses its flat floors. Also NULL (flat floors) when the
    snapshot is missing or stale, or every bucket is empty.
    """
    if MODEL_ID_SEGMENT[model_id] != "60_180":
        return obs_base.select(
            *GRAIN, F.lit(None).cast("double").alias("liquidity_anchor_amt")
        )
    require_columns(
        prm_balance,
        ["contract_id", "observation_date", *_OVERDUE_BUCKETS],
        "prm_balance",
    )
    src = prm_balance.select(
        F.col("contract_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date").alias("snapshot_date"),
        *[F.col(c).cast("double") for c in _OVERDUE_BUCKETS],
    )
    latest = pit_latest(
        obs_base,
        src,
        key="account_id",
        date_col="snapshot_date",
        value_cols=_OVERDUE_BUCKETS,
        inclusive=True,
        max_age_days=_BALANCE_MAX_AGE_D,
    )
    oldest = F.coalesce(
        *[F.when(F.col(c) > 0, F.col(c)) for c in reversed(_OVERDUE_BUCKETS)]
    )
    return latest.select(*GRAIN, oldest.alias("liquidity_anchor_amt"))


def build_cc_internal_returns(
    obs_base: DataFrame, comp_financial_tran_repos_dly: DataFrame
) -> DataFrame:
    """The bank's own returned cheques / DDS returns as ``(cif_id, event_date)``, across
    all of the customer's CASA accounts (R20: scoped by CIF before any other filter)."""
    require_columns(
        comp_financial_tran_repos_dly,
        ["cif_id", "tran_date", "reason_for_excluding"],
        "comp_financial_tran_repos_dly",
    )
    cifs = obs_base.select("cif_id").filter(F.col("cif_id").isNotNull()).distinct()
    return (
        comp_financial_tran_repos_dly.select(
            "cif_id", "tran_date", "reason_for_excluding"
        )
        .join(F.broadcast(cifs), on="cif_id", how="leftsemi")
        .filter(
            (F.col("tran_date") >= F.lit(lookback_floor(obs_base, 100)))
            & F.col("reason_for_excluding").isin(_RETURN_REASONS)
        )
        .select("cif_id", F.to_date("tran_date").alias("event_date"))
    )
`````

New:

`````python
"""CC-specific part of the A1 ability axis: the liquidity anchor.

Everything else (evidence, levels, points, state) is the shared ``a1_ability`` engine.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, pit_latest, require_columns
from .._dpd_journey import MODEL_ID_SEGMENT

# OVD_k holds the amount k cycles overdue (DPD bucket k+1): OVD_01 1-30 … OVD_06
# 151-180 DPD. OVD_07 (181-210) and the catch-all OVD_08 (211+) never anchor.
_OVERDUE_BUCKETS = [f"overdue_bucket_{i:02d}" for i in range(1, 7)]
# A balance snapshot older than this means the card stopped reporting; no anchor then.
_BALANCE_MAX_AGE_D = 31


def build_cc_liquidity_anchor(
    obs_base: DataFrame, prm_balance: DataFrame, model_id: str
) -> DataFrame:
    """Amount in the oldest non-empty overdue bucket on the latest balance snapshot at
    or before the observation date — what the customer must pay to stop the roll.

    Only for the 60-180 segments: at 180+ the buckets no longer track what is due, so
    the anchor is NULL and A1 uses its flat floors. Also NULL (flat floors) when the
    snapshot is missing or stale, or every bucket is empty.
    """
    if MODEL_ID_SEGMENT[model_id] != "60_180":
        return obs_base.select(
            *GRAIN, F.lit(None).cast("double").alias("liquidity_anchor_amt")
        )
    require_columns(
        prm_balance,
        ["contract_id", "observation_date", *_OVERDUE_BUCKETS],
        "prm_balance",
    )
    src = prm_balance.select(
        F.col("contract_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date").alias("snapshot_date"),
        *[F.col(c).cast("double") for c in _OVERDUE_BUCKETS],
    )
    latest = pit_latest(
        obs_base,
        src,
        key="account_id",
        date_col="snapshot_date",
        value_cols=_OVERDUE_BUCKETS,
        inclusive=True,
        max_age_days=_BALANCE_MAX_AGE_D,
    )
    oldest = F.coalesce(
        *[F.when(F.col(c) > 0, F.col(c)) for c in reversed(_OVERDUE_BUCKETS)]
    )
    return latest.select(*GRAIN, oldest.alias("liquidity_anchor_amt"))
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/pipeline.py`
action: replace · base sha256 `ebd7ab651221b8b035c1420dc5d4eda67781b02b6f052e2ae3645e6892aedb53` · base trailing newline: yes · new sha256 `f1fa725a5a187561deb0119512119d2f53f3aa7f3ac4574f0664b8e388447654` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: CC A1 ability axis.

    crx_cc_obs_base ─┬─ income signals ────┐
                     ├─ liquidity signals ─┤
                     ├─ distress signals ──┼─► crx_cc_a1_ability_v2
                     └─ liquidity anchor ──┘

Needs crx_cc_obs_base (``kedro run --pipeline=crx_cc_obs_base``) first. Optional
distress sources (prm_bureau_payment_order, internal cheque / DDS returns) are added as
extra inputs of the distress node once they exist.

    kedro run --pipeline=crx_cc_a1_ability_v2

TEMPORARY (mirror bundle 01): ``create_b01_check_pipeline`` runs the same nodes but
writes the axis to the temporary dataset ``crx_cc_a1_ability_b01_check`` (the existing
``crx_cc_a1_ability_v2`` is not overwritten) and logs the old-vs-new comparison
and recovered salary months vs ``feat_payroll_indicator`` (``b01_check.py``). Removed
by the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability import (
    build_a1_ability,
    build_distress_signals,
    build_income_signals,
    build_liquidity_signals,
)
from ..obs_base import create_cc_pipeline as create_cc_obs_pipeline
from .b01_check import compare_a1_outputs, compare_salary_months
from .nodes import build_cc_internal_returns, build_cc_liquidity_anchor

_OBS = "crx_cc_obs_base"


def create_pipeline(
    output: str = "crx_cc_a1_ability_v2",
    **kwargs,  # pylint: disable=unused-argument
) -> Pipeline:
    return Pipeline(
        [
            node(
                build_income_signals,
                [
                    _OBS,
                    "wm_fea_salary_days_since_increment",
                    "stg_aecb_salary_history",
                    "prm_bureau_cif_bridge",
                ],
                "crx_cc_a1_income_signals",
                name="build_crx_cc_a1_income_signals",
            ),
            node(
                build_liquidity_signals,
                [
                    _OBS,
                    "wm_fea_casa_eod_avg_balance",
                    "wm_fea_casa_cc_inflow_outflow",
                    "wm_pri_labelled_transactions",
                    "raw_beneficiary_cards",
                ],
                "crx_cc_a1_liquidity_signals",
                name="build_crx_cc_a1_liquidity_signals",
            ),
            node(
                build_cc_internal_returns,
                [_OBS, "comp_financial_tran_repos_dly"],
                "crx_cc_a1_internal_returns",
                name="build_crx_cc_a1_internal_returns",
            ),
            node(
                build_distress_signals,
                {
                    "obs_base": _OBS,
                    "bureau_alert": "prm_bureau_alert_enriched",
                    "internal_returns": "crx_cc_a1_internal_returns",
                },
                "crx_cc_a1_distress_signals",
                name="build_crx_cc_a1_distress_signals",
            ),
            node(
                build_cc_liquidity_anchor,
                [_OBS, "prm_balance", "params:model_id"],
                "crx_cc_a1_liquidity_anchor",
                name="build_crx_cc_a1_liquidity_anchor",
            ),
            node(
                build_a1_ability,
                [
                    _OBS,
                    "crx_cc_a1_income_signals",
                    "crx_cc_a1_liquidity_signals",
                    "crx_cc_a1_distress_signals",
                    "crx_cc_a1_liquidity_anchor",
                    "params:crx_log_stats",
                ],
                output,
                name="build_crx_cc_a1_ability",
            ),
        ],
        tags=["crx_persona", "crx", "a1", "ability", "persona_axis"],
    )


def create_b01_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: observation base + the A1 pipeline writing to
    crx_cc_a1_ability_b01_check + the old-vs-new and salary-month comparison nodes.
    Remove with b01_check.py and the catalog entry."""
    return (
        create_cc_obs_pipeline()
        + create_pipeline(output="crx_cc_a1_ability_b01_check")
        + Pipeline(
            [
                node(
                    compare_a1_outputs,
                    [
                        "crx_cc_a1_ability_v2",
                        "crx_cc_a1_ability_b01_check",
                        "params:model_id",
                    ],
                    None,
                    name="compare_crx_cc_a1_b01",
                ),
                node(
                    compare_salary_months,
                    [_OBS, "crx_cc_a1_income_signals", "feat_payroll_indicator"],
                    None,
                    name="compare_crx_cc_a1_b01_salary",
                ),
            ],
            tags=["crx_persona"],
        )
    )
`````

New:

`````python
"""Kedro pipeline: CC A1 ability axis.

    crx_cc_obs_base ─┬─ income signals ──────────────────────┐
                     ├─ liquidity signals ───────────────────┤
                     ├─ internal returns ─► distress signals ┼─► crx_cc_a1_ability_v2
                     └─ liquidity anchor ────────────────────┘

Needs crx_cc_obs_base (``kedro run --pipeline=crx_cc_obs_base``) first.
prm_bureau_payment_order joins the distress node once it exists in PROD.

    kedro run --pipeline=crx_cc_a1_ability_v2

TEMPORARY (mirror bundle 01): ``create_b01_check_pipeline`` runs the same nodes but
writes the axis to the temporary dataset ``crx_cc_a1_ability_b01_check`` (the existing
``crx_cc_a1_ability_v2`` is not overwritten) and logs the old-vs-new comparison
plus diagnostics on salary months, distress sources and levels (``b01_check.py``).
Removed by the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability import (
    build_a1_ability,
    build_distress_signals,
    build_income_signals,
    build_internal_returns,
    build_liquidity_signals,
)
from ..obs_base import create_cc_pipeline as create_cc_obs_pipeline
from .b01_check import (
    compare_a1_outputs,
    compare_distress_sources,
    compare_salary_months,
)
from .nodes import build_cc_liquidity_anchor

_OBS = "crx_cc_obs_base"


def create_pipeline(
    output: str = "crx_cc_a1_ability_v2",
    **kwargs,  # pylint: disable=unused-argument
) -> Pipeline:
    return Pipeline(
        [
            node(
                build_income_signals,
                [
                    _OBS,
                    "wm_fea_salary_days_since_increment",
                    "stg_aecb_salary_history",
                    "prm_bureau_cif_bridge",
                ],
                "crx_cc_a1_income_signals",
                name="build_crx_cc_a1_income_signals",
            ),
            node(
                build_liquidity_signals,
                [
                    _OBS,
                    "wm_fea_casa_eod_avg_balance",
                    "wm_fea_casa_cc_inflow_outflow",
                    "wm_pri_labelled_transactions",
                    "raw_beneficiary_cards",
                ],
                "crx_cc_a1_liquidity_signals",
                name="build_crx_cc_a1_liquidity_signals",
            ),
            node(
                build_internal_returns,
                [_OBS, "comp_financial_tran_repos_dly"],
                "crx_cc_a1_internal_returns",
                name="build_crx_cc_a1_internal_returns",
            ),
            node(
                build_distress_signals,
                {
                    "obs_base": _OBS,
                    "bureau_alert": "prm_bureau_alert_enriched",
                    "internal_returns": "crx_cc_a1_internal_returns",
                },
                "crx_cc_a1_distress_signals",
                name="build_crx_cc_a1_distress_signals",
            ),
            node(
                build_cc_liquidity_anchor,
                [_OBS, "prm_balance", "params:model_id"],
                "crx_cc_a1_liquidity_anchor",
                name="build_crx_cc_a1_liquidity_anchor",
            ),
            node(
                build_a1_ability,
                [
                    _OBS,
                    "crx_cc_a1_income_signals",
                    "crx_cc_a1_liquidity_signals",
                    "crx_cc_a1_distress_signals",
                    "crx_cc_a1_liquidity_anchor",
                    "params:crx_log_stats",
                ],
                output,
                name="build_crx_cc_a1_ability",
            ),
        ],
        tags=["crx_persona", "crx", "a1", "ability", "persona_axis"],
    )


def create_b01_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: observation base + the A1 pipeline writing to
    crx_cc_a1_ability_b01_check + the log-only comparison nodes.
    Remove with b01_check.py and the catalog entry."""
    return (
        create_cc_obs_pipeline()
        + create_pipeline(output="crx_cc_a1_ability_b01_check")
        + Pipeline(
            [
                node(
                    compare_a1_outputs,
                    [
                        "crx_cc_a1_ability_v2",
                        "crx_cc_a1_ability_b01_check",
                        "params:model_id",
                    ],
                    None,
                    name="compare_crx_cc_a1_b01",
                ),
                node(
                    compare_salary_months,
                    [_OBS, "crx_cc_a1_income_signals", "feat_payroll_indicator"],
                    None,
                    name="compare_crx_cc_a1_b01_salary",
                ),
                node(
                    compare_distress_sources,
                    [
                        _OBS,
                        "prm_bureau_alert_enriched",
                        "crx_cc_a1_internal_returns",
                    ],
                    None,
                    name="compare_crx_cc_a1_b01_distress",
                ),
            ],
            tags=["crx_persona"],
        )
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/obs_base/pipeline.py`
action: replace · base sha256 `d1b957c04ba57fea55b0e37a00af27c1bcf48f8ffb260500bb05c472e4541fdc` · base trailing newline: yes · new sha256 `c924e25529b82e01dc2b85ddc07f2c7255c1b281b61281ac3dedd213a0e2ec4c` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipelines building the observation base every persona axis reads.

kedro run --pipeline=crx_cc_obs_base   (cc_60_180 / cc_180_plus)
kedro run --pipeline=crx_rl_obs_base   (rl_60_180 / rl_180_plus)
"""

from kedro.pipeline import Pipeline, node

from .._common import build_cc_obs_base, build_rl_obs_base


def create_cc_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    return Pipeline(
        [
            node(
                func=build_cc_obs_base,
                inputs=["cc_spine", "prm_contract", "prm_client"],
                outputs="crx_cc_obs_base",
                name="build_crx_cc_obs_base",
            )
        ],
        tags=["crx_persona", "crx", "obs_base"],
    )


def create_rl_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    return Pipeline(
        [
            node(
                func=build_rl_obs_base,
                inputs=["rl_spine"],
                outputs="crx_rl_obs_base",
                name="build_crx_rl_obs_base",
            )
        ],
        tags=["crx_persona", "crx", "obs_base"],
    )
`````

New:

`````python
"""Kedro pipelines building the observation base every persona axis reads.

kedro run --pipeline=crx_cc_obs_base   (cc_60_180 / cc_180_plus)
kedro run --pipeline=crx_rl_obs_base   (rl_60_180 / rl_180_plus)
"""

from kedro.pipeline import Pipeline, node

from .._common import build_cc_obs_base, build_rl_obs_base


def create_cc_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    return Pipeline(
        [
            node(
                func=build_cc_obs_base,
                inputs="cc_spine",
                outputs="crx_cc_obs_base",
                name="build_crx_cc_obs_base",
            )
        ],
        tags=["crx_persona", "crx", "obs_base"],
    )


def create_rl_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    return Pipeline(
        [
            node(
                func=build_rl_obs_base,
                inputs=["rl_spine"],
                outputs="crx_rl_obs_base",
                name="build_crx_rl_obs_base",
            )
        ],
        tags=["crx_persona", "crx", "obs_base"],
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

Safety rules:
  * every file the bundle replaces or deletes must be byte-identical (line endings aside) to
    the version the bundle was built from; otherwise nothing is written and the diff is
    printed. Someone else's edits are never overwritten.
  * refuses to write on main/master, or when a touched file has uncommitted changes.
  * the bundle carries a SHA-256 for every block, so a damaged copy (rendered instead of raw
    markdown, smart quotes, lost lines) is detected before anything is written.

Options: --no-import skips the import check (e.g. outside the dev container).
         --accept PATH (repeatable) replaces a conflicting file anyway — only after
         reading its code diff, and only for a file nobody edited by hand.
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

APPLY_VERSION = 5
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
    import ast

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
            import ast

            dump = lambda t: ast.dump(_strip_docstrings(ast.parse(t)))  # noqa: E731
            return dump(a) == dump(b)
        if path.endswith((".yml", ".yaml")):
            import yaml

            return yaml.safe_load(a) == yaml.safe_load(b)
    except Exception:  # pylint: disable=broad-except
        return False
    return False


def _is_new(current: str, e: dict) -> bool:
    """The repo file already holds the bundle's new version (comment noise aside)."""
    return _loose(current) == _loose(e["new"]) or _same_code(e["path"], current, e["new"])


def _code_text(path: str, text: str) -> str:
    """The text with comments and docstrings removed (Python) or normalised (YAML)."""
    try:
        if path.endswith(".py"):
            import ast

            return ast.unparse(_strip_docstrings(ast.parse(text)))
        if path.endswith((".yml", ".yaml")):
            import yaml

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


ACCEPTED: set[str] = set()  # paths given with --accept


def file_status(e: dict) -> str:
    """One of: todo, done, conflict, accepted."""
    current = _read(pathlib.Path(e["path"]))
    cur_sha = None if current is None else _sha(current)
    if e["action"] == "add":
        if current is None:
            return "todo"
        return "done" if cur_sha == e["new_sha"] else "conflict"
    if e["action"] == "replace":
        if current is not None and _loose(current) == _loose(e["new"]):
            return "done"
        if current is not None and _loose(current) == _loose(e["base"]):
            return "todo"
        if current is not None and _same_code(e["path"], current, e["new"]):
            return "done"
        if _matches_base(current, e):
            return "todo"
        return "accepted" if e["path"] in ACCEPTED else "conflict"
    # delete
    if current is None:
        return "done"
    if _matches_base(current, e):
        return "todo"
    return "accepted" if e["path"] in ACCEPTED else "conflict"


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
    print("    The CODE differs (comments, docstrings, spacing are already ignored).")
    print("    Code-only diff — bundle's copy (-) vs this repo (+):")
    diff = list(
        difflib.unified_diff(
            _code_text(e["path"], expected).splitlines(),
            _code_text(e["path"], current or "").splitlines(),
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


def _comment_only(e: dict) -> bool:
    current = _read(pathlib.Path(e["path"]))
    return (
        e["action"] in ("replace", "delete")
        and current is not None
        and _loose(current) != _loose(e["base"])
        and _matches_base(current, e)
    )


def print_table(entries: list[dict], statuses: list[str]) -> None:
    word = {
        "todo": "will apply",
        "done": "already applied",
        "conflict": "CONFLICT",
        "accepted": "CONFLICT, accepted (--accept): will apply",
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


def _prune_empty_dirs(folder: pathlib.Path) -> None:
    """Remove folders left with nothing but bytecode caches after a delete."""
    import shutil

    while folder != pathlib.Path(".") and folder.is_dir():
        rest = [p for p in folder.iterdir() if p.name != "__pycache__"]
        if rest:
            return
        shutil.rmtree(folder)
        folder = folder.parent


# ── Commands ─────────────────────────────────────────────────────────────────


def cmd_check(entries: list[dict], quiet: bool = False) -> bool:
    statuses = [file_status(e) for e in entries]
    problems = git_problems(entries)
    if not quiet:
        print_table(entries, statuses)
    for e, s in zip(entries, statuses):
        if s in ("conflict", "accepted"):
            explain_conflict(e)
    for p in problems:
        print("REFUSED: " + p)
    n_conflict = statuses.count("conflict")
    ok = n_conflict == 0 and not problems
    n_todo = statuses.count("todo") + statuses.count("accepted")
    print(
        f"\n{n_todo} to apply, {statuses.count('done')} already applied, "
        f"{n_conflict} conflicts"
    )
    print("CHECK PASSED" if ok else "CHECK FAILED — nothing was written")
    if n_conflict:
        print(
            "A conflict means this repo's code differs from the copy the bundle was built\n"
            "from (above: the code-only diff). If nobody edited that file by hand, the\n"
            "difference is a transcription slip in the bundle's copy: add\n"
            "  --accept <path>\n"
            "to both the --check and the --apply command. Otherwise send the diff back."
        )
    return ok


def cmd_apply(entries: list[dict], do_import: bool) -> bool:
    if not cmd_check(entries, quiet=True):
        return False
    for e in entries:
        status = file_status(e)
        if status not in ("todo", "accepted"):
            continue
        path = pathlib.Path(e["path"])
        if e["action"] == "delete":
            path.unlink()
            _prune_empty_dirs(path.parent)
        else:
            new = e["new"]
            if e["action"] == "replace" and status == "todo":
                new = _rebase(new, e["base"], _read(path))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(new.encode("utf-8"))
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
    print("APPLY PASSED — review with `git status` / `git diff`")
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
        elif (current is not None and e["new"] is not None and _is_new(current, e)) or (
            e["action"] == "delete" and current is None
        ):
            # restore the committed bytes (the repo's own file, exactly); apply refuses
            # to run over uncommitted changes, so HEAD is the state before --apply
            committed = _head_version(e["path"])
            restore = committed if committed is not None else e["base"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(restore.encode("utf-8"))
        elif not _matches_base(current, e):
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
    ap.add_argument("--accept", action="append", default=[], metavar="PATH")
    args = ap.parse_args()
    ACCEPTED.update(args.accept)

    md = pathlib.Path(args.bundle).read_text(encoding="utf-8")
    need = re.search(r"apply_bundle version: (\d+)", md)
    if need and int(need.group(1)) > APPLY_VERSION:
        print(f"This bundle needs apply_bundle.py version {need.group(1)}; you have "
              f"{APPLY_VERSION}. Redo step 3 of the bundle.")
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
Clean up after mirror bundle 02_a1_engine_checks.md, on the bundle's branch.
- Remove the temporary check (everything marked TEMPORARY for bundle 01):
  - conf/base/catalog/catalog_crx.yml: the `crx_cc_a1_ability_b01_check` entry and its
    TEMPORARY comment;
  - src/enbd_collections/pipeline_registry.py: the `"crx_cc_a1_ability_b01_check"` entry;
  - crx_persona/cc_a1_ability_v2/pipeline.py: `create_b01_check_pipeline`, the imports of
    `create_cc_obs_pipeline` and `b01_check`, and the TEMPORARY paragraph of the module
    docstring;
  - crx_persona/cc_a1_ability_v2/__init__.py: the `create_b01_check_pipeline` export;
  - delete crx_persona/cc_a1_ability_v2/b01_check.py.
  Then check: `kedro registry list` still works and no file mentions `b01`
  (`grep -rn b01 src conf` prints nothing).
- HDFS (the user runs this in PROD; UAT has no data): resolve the catalog path
  `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_b01_check`
  from the workplace conf for model_id cc_60_180 and cc_180_plus, and write out the two
  commands in full, e.g. `hdfs dfs -rm -r <resolved path>`. Do this before removing the
  catalog entry.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
