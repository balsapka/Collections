# Mirror bundle 02 — Rename the A1 engine package to a1_ability

apply_bundle version: 2 · built 2026-10-23 from `c26637d..2824a8d` · 3 added, 3 replaced, 3 deleted

**Only for a repo that already has bundle 01 applied** (the version with `crx_persona/_a1/`).
If bundle 01 is not applied yet, skip this bundle and apply the current bundle 01 instead —
it already uses the new name.

Renames the A1 engine package `crx_persona/_a1/` to `crx_persona/a1_ability/` and points the
CC A1 pipeline at it. No logic change; no re-run needed.

## Run this (from the workplace repo root)

```bash
git checkout -b feature/persona_redesign_b01            # never apply on main
# save this file RAW as docs/mirror_bundles/02_a1_ability_rename.md
# first time / version bump only: create docs/mirror_bundles/apply_bundle.py from the 'Apply script' section
python docs/mirror_bundles/apply_bundle.py docs/mirror_bundles/02_a1_ability_rename.md --check     # dry run -> CHECK PASSED
python docs/mirror_bundles/apply_bundle.py docs/mirror_bundles/02_a1_ability_rename.md --apply     # writes + compile + imports -> APPLY PASSED
git status && git diff --stat
git add -A src conf docs && git commit -m "Mirror bundle 02: Rename the A1 engine package to a1_ability"
```

Undo before committing: `python docs/mirror_bundles/apply_bundle.py docs/mirror_bundles/02_a1_ability_rename.md --revert`. After committing: `git revert <commit>`.

## Instructions for the workplace assistant

1. **Do not retype or hand-edit code from this file.** Save it raw (GitHub "Copy raw file", not the rendered page) and let `apply_bundle.py` write the files.
2. `--check` must print **CHECK PASSED**. If it prints CONFLICT, the workplace file differs from the version this bundle was built from: stop, and give the printed diff to the user. Do not edit files to make the check pass.
3. `DAMAGED` means the markdown copy was altered — recopy the raw file.
4. `--apply` must print **APPLY PASSED**. If an import fails, run `--revert` and report the message.
5. Touch nothing outside the files listed in the manifest.

## Manifest

| Action | Path |
|---|---|
| add | `src/enbd_collections/pipelines/crx_persona/a1_ability/__init__.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a1_ability/classify.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/pipeline.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/_a1/__init__.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/_a1/classify.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/_a1/signals.py` |

## Files

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/__init__.py`
action: add · new sha256 `de7eff27ace0fdcdc5690de1b1cd9c56a44085dae4e10e8c75e0a33ae1cecf4e` · new trailing newline: yes

New:

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

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/classify.py`
action: add · new sha256 `537653831b6fe08435661252621aee9642766eb7b10390ed82a44f6bd393a6d3` · new trailing newline: yes

New:

`````python
"""A1 ability state — GRR MECE points.

Spec: ``workplace_mirror/specs/A1_ability_spec.md``.

    income level     stable 2 / weak 1 / none 0
  + liquidity level  adequate 2 / weak 1 / none 0
  = points           4 high, 2–3 moderate, 0–1 low
  distress (cheque bounce / DDS return) lowers the state one level;
  no income, no liquidity, no distress and no CASA transaction → unknown.

Thresholds scale with ``liquidity_anchor_amt`` — what the customer must find now
(CC 60–180: the oldest overdue bucket; RL: one instalment; NULL: flat floors only).
Values are the workbook's starting values (sheet Thresholds), not yet tuned on PROD.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_distribution
from ..scoring_engine import StateLadder, points_from_level

N3 = 2  # months of the last 3 that must qualify
F_INC = 3000.0  # salary floor (internal and bureau), AED
K_INC = 2.0  # income must also cover this multiple of the anchor
D_INC = 0.25  # stable income may fall at most this share vs the prior 3 months
F_CASA = 3000.0
K_CASA = 1.0
D_CASA = 0.50
F_PAY = 500.0
K_PAY = 1.0
DEMIN = 1000.0  # smallest amount that counts as any evidence

_LADDER = StateLadder(
    high="ability_high",
    moderate="ability_moderate",
    low="ability_low",
    unknown="ability_unknown",
    high_from_points=4,
    moderate_from_points=2,
)
_LAST3, _PRIOR3 = (1, 2, 3), (4, 5, 6)


def _months(prefix: str, months: tuple[int, ...]) -> list[Column]:
    return [F.col(f"{prefix}_m{i}") for i in months]


def _count_at_least(cols: list[Column], floor: Column) -> Column:
    return sum((F.coalesce(c, F.lit(0.0)) >= floor).cast("int") for c in cols)


def _mean(cols: list[Column], missing_is_zero: bool) -> Column:
    """Mean over the months; a month without data counts as 0 (income) or is skipped
    (balances)."""
    total = sum(F.coalesce(c, F.lit(0.0)) for c in cols)
    if missing_is_zero:
        return total / len(cols)
    present = sum(c.isNotNull().cast("int") for c in cols)
    return F.when(present > 0, total / present)


def _not_weakening(prefix: str, max_drop: float, missing_is_zero: bool) -> Column:
    """The last-3-month average is not more than ``max_drop`` below the prior 3 months
    (true when there is no prior quarter to compare with)."""
    recent = _mean(_months(prefix, _LAST3), missing_is_zero)
    prior = _mean(_months(prefix, _PRIOR3), missing_is_zero)
    return F.coalesce(F.when(prior > 0, recent >= prior * (1 - max_drop)), F.lit(True))


def income_level(anchor: Column) -> Column:
    last3 = _months("income", _LAST3)
    floor = F.greatest(F.lit(F_INC), K_INC * anchor)
    stable = (_count_at_least(last3, floor) >= N3) & _not_weakening(
        "income", D_INC, True
    )
    weak = _count_at_least(last3, F.lit(DEMIN)) > 0
    return F.when(stable, "stable").when(weak, "weak").otherwise("none")


def liquidity_level(anchor: Column) -> Column:
    last3 = _months("casa", _LAST3)
    payment = F.coalesce(F.col("ext_card_payment_max_3m"), F.lit(0.0))
    casa_floor = F.greatest(F.lit(F_CASA), K_CASA * anchor)
    casa_ok = (_count_at_least(last3, casa_floor) >= N3) & _not_weakening(
        "casa", D_CASA, False
    )
    adequate = casa_ok | (payment >= F.greatest(F.lit(F_PAY), K_PAY * anchor))
    weak = (_count_at_least(last3, F.lit(DEMIN)) > 0) | (payment >= DEMIN)
    return F.when(adequate, "adequate").when(weak, "weak").otherwise("none")


def build_a1_ability(  # pylint: disable=too-many-arguments
    obs_base: DataFrame,
    income: DataFrame,
    liquidity: DataFrame,
    distress: DataFrame,
    anchor: DataFrame,
    log_stats: bool = False,
) -> DataFrame:
    """One A1 state per observation-base row.

    ``anchor`` carries ``GRAIN + liquidity_anchor_amt`` (product-specific builder).
    """
    df = left_join_all(obs_base, [income, liquidity, distress, anchor])
    amt = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))  # missing → flat floors
    df = (
        df.withColumn("a1_income_level", income_level(amt))
        .withColumn("a1_liquidity_level", liquidity_level(amt))
        .withColumn("a1_distress_flag", F.col("distress_flag") == 1)
    )
    df = df.withColumn(
        "a1_points_total",
        points_from_level(F.col("a1_income_level"), {"stable": 2, "weak": 1})
        + points_from_level(F.col("a1_liquidity_level"), {"adequate": 2, "weak": 1}),
    )
    unknown = (
        (F.col("a1_points_total") == 0)
        & ~F.col("a1_distress_flag")
        & (F.coalesce(F.col("casa_active_3m"), F.lit(0)) == 0)
    )
    df = df.withColumn(
        "a1_state",
        _LADDER.state(F.col("a1_points_total"), F.col("a1_distress_flag"), unknown),
    )
    out = df.select(
        *GRAIN,
        "a1_state",
        F.when(F.col("a1_state") == _LADDER.unknown, "no_signal")
        .otherwise("observed")
        .alias("a1_provenance"),
        "a1_income_level",
        "a1_liquidity_level",
        F.col("a1_points_total").cast("int"),
        F.col("a1_distress_flag").cast("int"),
        F.col("liquidity_anchor_amt").cast("double"),
        F.current_date().alias("computed_at"),
    )
    log_distribution(out, "a1_state", "a1_ability", log_stats)
    return out
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py`
action: add · new sha256 `1736daea69c92ee7bcec3245b5f5ca33319f8e9ade24c5e1ad12ec654173e8f5` · new trailing newline: yes

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
      ``(cif_id, event_date)``.

    TODO(sonnet): no internal source exists in the code base yet. Find where returned
    cheques and DDS returns are recorded internally (candidates: CASA transaction codes
    or narrations in ``comp_financial_tran_repos_dly``, a DDS mandate table), build a
    ``(cif_id, event_date)`` frame and pass it here from the pipeline. Take every
    account of the customer (CIF level), not the scored account: an RL account_id is
    not the customer's CASA account.
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

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/__init__.py`
action: replace · base sha256 `fb7fc1c45e3cbb4e868956df219329fce6b4cde99372aeff71f3b3c0e67dc5ee` · base trailing newline: yes · new sha256 `65c9988c7d9e81a1dfeba967bdfe4f03037ccf21b7749032026e46e7beafee42` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CC A1 ability axis (GRR MECE points) on the shared ``_a1`` engine."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

New:

`````python
"""CC A1 ability axis (GRR MECE points) on the shared ``a1_ability`` engine."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/nodes.py`
action: replace · base sha256 `8ea58ab45ff337b86008342aa4ff0f9aa63693becb487c9f39958c3f789d1d2c` · base trailing newline: yes · new sha256 `5cb0d9f21a093685fc39936236a09c381eb18af5487326b1ae630b55d0a81036` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CC-specific part of the A1 ability axis: the liquidity anchor.

Everything else (evidence, levels, points, state) is the shared engine in ``_a1``.
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
action: replace · base sha256 `05d867a3e057d2d16ce6c9c6d8ed7f6f5a061024c0717b17efcd7aad2fceb653` · base trailing newline: yes · new sha256 `ad2071bcfae2ddfff5691fd9597d30eceaa91d9fec5df525823dd58d665a3e29` · new trailing newline: yes

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
"""

from kedro.pipeline import Pipeline, node

from .._a1 import (
    build_a1_ability,
    build_distress_signals,
    build_income_signals,
    build_liquidity_signals,
)
from .nodes import build_cc_liquidity_anchor

_OBS = "crx_cc_obs_base"


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
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
                build_distress_signals,
                [_OBS, "prm_bureau_alert_enriched"],
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
                "crx_cc_a1_ability_v2",
                name="build_crx_cc_a1_ability",
            ),
        ],
        tags=["crx_persona", "crx", "a1", "ability", "persona_axis"],
    )
`````

New:

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
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability import (
    build_a1_ability,
    build_distress_signals,
    build_income_signals,
    build_liquidity_signals,
)
from .nodes import build_cc_liquidity_anchor

_OBS = "crx_cc_obs_base"


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
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
                build_distress_signals,
                [_OBS, "prm_bureau_alert_enriched"],
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
                "crx_cc_a1_ability_v2",
                name="build_crx_cc_a1_ability",
            ),
        ],
        tags=["crx_persona", "crx", "a1", "ability", "persona_axis"],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/_a1/__init__.py`
action: delete · base sha256 `de7eff27ace0fdcdc5690de1b1cd9c56a44085dae4e10e8c75e0a33ae1cecf4e` · base trailing newline: yes

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

### FILE: `src/enbd_collections/pipelines/crx_persona/_a1/classify.py`
action: delete · base sha256 `537653831b6fe08435661252621aee9642766eb7b10390ed82a44f6bd393a6d3` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A1 ability state — GRR MECE points.

Spec: ``workplace_mirror/specs/A1_ability_spec.md``.

    income level     stable 2 / weak 1 / none 0
  + liquidity level  adequate 2 / weak 1 / none 0
  = points           4 high, 2–3 moderate, 0–1 low
  distress (cheque bounce / DDS return) lowers the state one level;
  no income, no liquidity, no distress and no CASA transaction → unknown.

Thresholds scale with ``liquidity_anchor_amt`` — what the customer must find now
(CC 60–180: the oldest overdue bucket; RL: one instalment; NULL: flat floors only).
Values are the workbook's starting values (sheet Thresholds), not yet tuned on PROD.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_distribution
from ..scoring_engine import StateLadder, points_from_level

N3 = 2  # months of the last 3 that must qualify
F_INC = 3000.0  # salary floor (internal and bureau), AED
K_INC = 2.0  # income must also cover this multiple of the anchor
D_INC = 0.25  # stable income may fall at most this share vs the prior 3 months
F_CASA = 3000.0
K_CASA = 1.0
D_CASA = 0.50
F_PAY = 500.0
K_PAY = 1.0
DEMIN = 1000.0  # smallest amount that counts as any evidence

_LADDER = StateLadder(
    high="ability_high",
    moderate="ability_moderate",
    low="ability_low",
    unknown="ability_unknown",
    high_from_points=4,
    moderate_from_points=2,
)
_LAST3, _PRIOR3 = (1, 2, 3), (4, 5, 6)


def _months(prefix: str, months: tuple[int, ...]) -> list[Column]:
    return [F.col(f"{prefix}_m{i}") for i in months]


def _count_at_least(cols: list[Column], floor: Column) -> Column:
    return sum((F.coalesce(c, F.lit(0.0)) >= floor).cast("int") for c in cols)


def _mean(cols: list[Column], missing_is_zero: bool) -> Column:
    """Mean over the months; a month without data counts as 0 (income) or is skipped
    (balances)."""
    total = sum(F.coalesce(c, F.lit(0.0)) for c in cols)
    if missing_is_zero:
        return total / len(cols)
    present = sum(c.isNotNull().cast("int") for c in cols)
    return F.when(present > 0, total / present)


def _not_weakening(prefix: str, max_drop: float, missing_is_zero: bool) -> Column:
    """The last-3-month average is not more than ``max_drop`` below the prior 3 months
    (true when there is no prior quarter to compare with)."""
    recent = _mean(_months(prefix, _LAST3), missing_is_zero)
    prior = _mean(_months(prefix, _PRIOR3), missing_is_zero)
    return F.coalesce(F.when(prior > 0, recent >= prior * (1 - max_drop)), F.lit(True))


def income_level(anchor: Column) -> Column:
    last3 = _months("income", _LAST3)
    floor = F.greatest(F.lit(F_INC), K_INC * anchor)
    stable = (_count_at_least(last3, floor) >= N3) & _not_weakening(
        "income", D_INC, True
    )
    weak = _count_at_least(last3, F.lit(DEMIN)) > 0
    return F.when(stable, "stable").when(weak, "weak").otherwise("none")


def liquidity_level(anchor: Column) -> Column:
    last3 = _months("casa", _LAST3)
    payment = F.coalesce(F.col("ext_card_payment_max_3m"), F.lit(0.0))
    casa_floor = F.greatest(F.lit(F_CASA), K_CASA * anchor)
    casa_ok = (_count_at_least(last3, casa_floor) >= N3) & _not_weakening(
        "casa", D_CASA, False
    )
    adequate = casa_ok | (payment >= F.greatest(F.lit(F_PAY), K_PAY * anchor))
    weak = (_count_at_least(last3, F.lit(DEMIN)) > 0) | (payment >= DEMIN)
    return F.when(adequate, "adequate").when(weak, "weak").otherwise("none")


def build_a1_ability(  # pylint: disable=too-many-arguments
    obs_base: DataFrame,
    income: DataFrame,
    liquidity: DataFrame,
    distress: DataFrame,
    anchor: DataFrame,
    log_stats: bool = False,
) -> DataFrame:
    """One A1 state per observation-base row.

    ``anchor`` carries ``GRAIN + liquidity_anchor_amt`` (product-specific builder).
    """
    df = left_join_all(obs_base, [income, liquidity, distress, anchor])
    amt = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))  # missing → flat floors
    df = (
        df.withColumn("a1_income_level", income_level(amt))
        .withColumn("a1_liquidity_level", liquidity_level(amt))
        .withColumn("a1_distress_flag", F.col("distress_flag") == 1)
    )
    df = df.withColumn(
        "a1_points_total",
        points_from_level(F.col("a1_income_level"), {"stable": 2, "weak": 1})
        + points_from_level(F.col("a1_liquidity_level"), {"adequate": 2, "weak": 1}),
    )
    unknown = (
        (F.col("a1_points_total") == 0)
        & ~F.col("a1_distress_flag")
        & (F.coalesce(F.col("casa_active_3m"), F.lit(0)) == 0)
    )
    df = df.withColumn(
        "a1_state",
        _LADDER.state(F.col("a1_points_total"), F.col("a1_distress_flag"), unknown),
    )
    out = df.select(
        *GRAIN,
        "a1_state",
        F.when(F.col("a1_state") == _LADDER.unknown, "no_signal")
        .otherwise("observed")
        .alias("a1_provenance"),
        "a1_income_level",
        "a1_liquidity_level",
        F.col("a1_points_total").cast("int"),
        F.col("a1_distress_flag").cast("int"),
        F.col("liquidity_anchor_amt").cast("double"),
        F.current_date().alias("computed_at"),
    )
    log_distribution(out, "a1_state", "a1_ability", log_stats)
    return out
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/_a1/signals.py`
action: delete · base sha256 `1736daea69c92ee7bcec3245b5f5ca33319f8e9ade24c5e1ad12ec654173e8f5` · base trailing newline: yes

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
      ``(cif_id, event_date)``.

    TODO(sonnet): no internal source exists in the code base yet. Find where returned
    cheques and DDS returns are recorded internally (candidates: CASA transaction codes
    or narrations in ``comp_financial_tran_repos_dly``, a DDS mandate table), build a
    ``(cif_id, event_date)`` frame and pass it here from the pipeline. Take every
    account of the customer (CIF level), not the scored account: an RL account_id is
    not the customer's CASA account.
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

## Apply script

Save as `docs/mirror_bundles/apply_bundle.py` (only when missing or older than version 2).

`````python
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

APPLY_VERSION = 2
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
            _prune_empty_dirs(path.parent)
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
`````
