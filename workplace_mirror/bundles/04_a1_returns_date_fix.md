# Mirror bundle 04 — A1 — internal-returns coverage guard: date vs string

apply_bundle version: 6 · built 2026-10-26 from `bfe52a3..a46e2e2` · source: 0 added, 1 replaced, 0 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 4). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Continue on the branch of the earlier bundle (nothing uncommitted on it):

```bash
git checkout feature/persona_redesign_b01 && git pull && git status --short
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/04_a1_returns_date_fix.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '04_a1_returns_date_fix.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/04_a1_returns_date_fix.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Commit the source only, and push:

```bash
git add src conf && git commit -m "A1: prm_casa_return_events coverage guard compares ISO strings" && git push
```

**Undo** (before step 4) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/04_a1_returns_date_fix.md --revert
```

### In PROD

**Step 5.** Get the branch:

```bash
git fetch origin && git checkout feature/persona_redesign_b01 && git pull
```

Same `model_id` (`cc_60_180`) and persona dates as bundle 03. `prm_casa_return_events` is
already built (bundle 03 Step 7), so it is not rerun.

**Step 6.** Rerun the bundle 03 check pipeline:

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability_b03_check
```

Paste back the `B03 OUTPUT` and `B03 INCOME` blocks (from `=== B03 … START ===` to
`=== B03 … END ===`). Then continue with bundle 03 Step 9 only after they have been
reviewed.

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

Fixes the `crx_cc_a1_ability_b03_check` failure in `build_internal_returns`
(`a1_ability/signals.py:351`: `TypeError: '>' not supported between instances of
'datetime.date' and 'str'`).

`prm_casa_return_events` is partitioned by `event_month`, written as a `yyyy-MM-dd` string.
On read, Spark turns the partition folder values back into dates, so the coverage guard
compared a date with the ISO string from `lookback_floor`. Both sides are now compared as
ISO strings. The `event_month >= since` filter itself was already fine (Spark casts it).

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
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py` |

## Files

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py`
action: replace · base sha256 `18fdacb2b998536b9750303a8c423e965c4277586843014003f85c78943f9183` · base trailing newline: yes · new sha256 `6cd55f2f0cee8a72486eb8e4109e4bb4c0b54cec84118169dcf33dbeabe4e0dc` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A1_ability_spec.md`` (GRR workbook A1_ability_20261022).

Observation dates are month ends. The window is W calendar months, the observation month
included (``_common.window_months``: 3 for 60–180, 6 for 180+): m1 = the observation
month … mW; "the prior window" is m(W+1)–m(2W). The builders return the amounts the
classifier compares with its thresholds:

* income    — salary received in each month (internal credit or bureau salary,
              the larger);
* liquidity — CASA average balance in each month, largest single external card payment;
* activity  — any CASA transaction in the window (the Unknown gate);
* distress  — a cheque bounce or direct-debit return in the window.

Customer-level sources are always read for the whole CIF — all the customer's accounts —
never for the scored account_id alone (an RL account_id is not a CASA account). Each
builder reads its sources from the earliest observation's first month on
(``lookback_floor``), so source history before it is never shuffled.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import (
    GRAIN,
    left_join_all,
    lookback_floor,
    parse_yyyymmdd,
    require_columns,
    window_agg,
    window_months,
)

# reason_for_excluding values that count as distress. prm_casa_return_events also carries
# "RETURNS", which is POS reversals (checked in PROD, Sonnet v01).
DISTRESS_RETURN_REASONS = ("CHEQUE RETURNS", "DDS Rejects/Reversal")
_CASA_MONTH_COL = "ft_avg_casa_eod_balance_in_last_0_3_weeks_avg"  # CA+SA, ~1 month
_CASA_IN_COL = "ft_inflow_casa_amt_in_last_0_0_weeks_sum"
_CASA_OUT_COL = "ft_outflow_casa_amt_in_last_0_0_weeks_sum"


def _month_index(date: Column) -> Column:
    """1 for the observation month, 2 for the one before, …"""
    obs_month = F.trunc(F.col("observation_date"), "month")
    return F.months_between(obs_month, F.trunc(date, "month")).cast("int") + 1


def _by_month(
    obs: DataFrame, series: DataFrame, value: str, prefix: str, months: int
) -> DataFrame:
    """Spread a ``(cif_id, month, value)`` series over ``{prefix}_m1 … _m{months}`` per
    observation (NULL where the month has no value)."""
    return (
        obs.select(*GRAIN, "cif_id")
        .join(series, on="cif_id")
        .withColumn("_k", _month_index(F.col("month")))
        .filter(F.col("_k").between(1, months))
        .groupBy(*GRAIN)
        .agg(
            *[
                F.max(F.when(F.col("_k") == i, F.col(value))).alias(f"{prefix}_m{i}")
                for i in range(1, months + 1)
            ]
        )
    )


# ── Income ────────────────────────────────────────────────────────────────────


def _internal_salary(wm_salary: DataFrame, since: str) -> DataFrame:
    """Salary credits by month, recovered from the weekly WM snapshots dated ``since`` on
    (an earlier snapshot cannot see a later credit).

    Each snapshot carries the last salary credited and how many days before the snapshot
    it was, so snapshot date minus that gap is the credit date. Several snapshots see
    the same credit; they collapse to one value per month.

    This is the only internal salary source. ``feat_payroll_indicator`` is not used: it is
    stamped the month after the credit and flags a subset of these months.
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
    week = parse_yyyymmdd("week_number")
    credit_date = F.date_sub(
        week, F.col("ft_days_since_salary_transaction").cast("int")
    )
    return wm_salary.filter(week >= F.lit(since)).select(
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
    model_id: str,
) -> DataFrame:
    """``income_m1 … income_m{2W}``: salary received per month — the larger of the
    internal credit and the bureau salary (NULL: no salary that month)."""
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    months = 2 * window_months(model_id)
    since = lookback_floor(obs, months)
    monthly = (
        _internal_salary(wm_salary, since)
        .unionByName(_bureau_salary(salary_hist, bureau_cif_bridge))
        .filter(F.col("month") >= F.lit(since))
        .groupBy("cif_id", "month")
        .agg(F.max("amount").alias("amount"))
    )
    return left_join_all(
        obs_base, [_by_month(obs, monthly, "amount", "income", months)]
    )


# ── Liquidity and activity ────────────────────────────────────────────────────


def _casa_by_month(wm_casa_bal: DataFrame, since: str) -> DataFrame:
    """CASA (current + savings) average balance per month from ``since`` on: the 4-week
    average at the month's last weekly snapshot."""
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
        wm_casa_bal.filter(week >= F.lit(since))
        .groupBy("cif_id", F.trunc(week, "month").alias("month"))
        .agg(last_in_month.alias("_last"))
        .select("cif_id", "month", F.col("_last.v").alias("balance"))
    )


def _ext_card_payments(
    obs: DataFrame,
    labelled_txn: DataFrame,
    beneficiary_cards: DataFrame,
    months: int,
    since: str,
) -> DataFrame:
    """Largest single CASA payment to one of the customer's registered external credit
    cards in the window.

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
            (F.col("tran_date") >= F.lit(since))
            & (F.col("in_out_flow") == "outflow")
            & (F.col("product_category") == "CASA")
        )
        .join(F.broadcast(cards), on="transaction_acid", how="leftsemi")
        .select(
            "cif_id", F.col("tran_date").cast("date"), F.col("tran_amt").cast("double")
        )
    )
    return window_agg(
        obs,
        src,
        date_col="tran_date",
        aggs=[F.max("tran_amt").alias("ext_card_payment_max")],
        months=months,
    )


def _casa_activity(
    obs: DataFrame, wm_casa_flow: DataFrame, months: int, since: str
) -> DataFrame:
    """Any CASA credit or debit in the window."""
    require_columns(
        wm_casa_flow,
        ["cif_id", "week_number", _CASA_IN_COL, _CASA_OUT_COL],
        "wm_fea_casa_cc_inflow_outflow",
    )
    week = parse_yyyymmdd("week_number")
    src = wm_casa_flow.filter(week >= F.lit(since)).select(
        "cif_id",
        week.alias("week"),
        ((F.col(_CASA_IN_COL) > 0) | (F.col(_CASA_OUT_COL) > 0))
        .cast("int")
        .alias("_active"),
    )
    return window_agg(
        obs,
        src,
        date_col="week",
        aggs=[F.max("_active").alias("casa_active")],
        months=months,
    )


def build_liquidity_signals(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    wm_casa_bal: DataFrame,
    wm_casa_flow: DataFrame,
    labelled_txn: DataFrame,
    beneficiary_cards: DataFrame,
    model_id: str,
) -> DataFrame:
    """``casa_m1 … casa_m{2W}``, ``ext_card_payment_max``, ``casa_active``."""
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    w = window_months(model_id)
    since = lookback_floor(obs, 2 * w)  # the balances' prior window reaches furthest
    return left_join_all(
        obs_base,
        [
            _by_month(
                obs, _casa_by_month(wm_casa_bal, since), "balance", "casa", 2 * w
            ),
            _ext_card_payments(obs, labelled_txn, beneficiary_cards, w, since),
            _casa_activity(obs, wm_casa_flow, w, since),
        ],
    )


# ── Distress ──────────────────────────────────────────────────────────────────


def build_distress_signals(
    obs_base: DataFrame,
    bureau_alert: DataFrame,
    internal_returns: DataFrame,
    model_id: str,
    payment_order: DataFrame | None = None,
) -> DataFrame:
    """distress_flag: a cheque bounce or direct-debit (DDS) return in the window,
    from the bureau and from the bank's own records.

    * ``bureau_alert`` — bureau-reported bounced cheques, dated by ``extract_date``
      (the bureau pull date, not the bounce date: a bounce can repeat in later pulls);
    * ``internal_returns`` — the bank's own returned cheques / DDS returns as
      ``(cif_id, event_date)`` from ``build_internal_returns``;
    * ``payment_order`` — prm_bureau_payment_order returns; not in PROD yet.
    """
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    w = window_months(model_id)
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
    require_columns(internal_returns, ["cif_id", "event_date"], "internal_returns")
    events = events.unionByName(
        internal_returns.select("cif_id", F.to_date("event_date").alias("event_date"))
    )
    hits = window_agg(
        obs,
        events.filter(F.col("event_date") >= F.lit(lookback_floor(obs, w))),
        date_col="event_date",
        aggs=[F.max(F.lit(1)).alias("distress_flag")],
        months=w,
    )
    return left_join_all(obs_base, [hits]).fillna(0, subset=["distress_flag"])


def build_internal_returns(
    obs_base: DataFrame, return_events: DataFrame, model_id: str
) -> DataFrame:
    """The bank's own returned cheques and DDS returns for the observation base's CIFs, as
    distinct ``(cif_id, event_date, reason)`` from ``prm_casa_return_events`` (all of the
    customer's CASA accounts; the debit and credit legs of a return collapse to one row).

    Stops the run when the table starts after the earliest observation's window (both
    follow ``crx_persona.persona_start_date``; the table was built for an older one).
    """
    require_columns(
        return_events,
        ["cif_id", "tran_date", "reason_for_excluding", "event_month"],
        "prm_casa_return_events",
    )
    since = lookback_floor(obs_base, window_months(model_id))
    first = return_events.agg(F.min("event_month")).first()[0]  # partition column
    if first is None or first > since:
        raise ValueError(
            f"prm_casa_return_events starts at {first}, but the observations need returns "
            f"from {since}: rerun casa_primary after changing "
            "crx_persona.persona_start_date"
        )
    cifs = obs_base.select("cif_id").filter(F.col("cif_id").isNotNull()).distinct()
    # since is a month start, so event_month >= since is tran_date >= since, and prunes
    return (
        return_events.filter(
            (F.col("event_month") >= F.lit(since))
            & F.col("reason_for_excluding").isin(*DISTRESS_RETURN_REASONS)
        )
        .join(F.broadcast(cifs), on="cif_id", how="leftsemi")
        .select(
            "cif_id",
            F.to_date("tran_date").alias("event_date"),
            F.col("reason_for_excluding").alias("reason"),
        )
        .distinct()
    )
`````

New:

`````python
"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A1_ability_spec.md`` (GRR workbook A1_ability_20261022).

Observation dates are month ends. The window is W calendar months, the observation month
included (``_common.window_months``: 3 for 60–180, 6 for 180+): m1 = the observation
month … mW; "the prior window" is m(W+1)–m(2W). The builders return the amounts the
classifier compares with its thresholds:

* income    — salary received in each month (internal credit or bureau salary,
              the larger);
* liquidity — CASA average balance in each month, largest single external card payment;
* activity  — any CASA transaction in the window (the Unknown gate);
* distress  — a cheque bounce or direct-debit return in the window.

Customer-level sources are always read for the whole CIF — all the customer's accounts —
never for the scored account_id alone (an RL account_id is not a CASA account). Each
builder reads its sources from the earliest observation's first month on
(``lookback_floor``), so source history before it is never shuffled.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import (
    GRAIN,
    left_join_all,
    lookback_floor,
    parse_yyyymmdd,
    require_columns,
    window_agg,
    window_months,
)

# reason_for_excluding values that count as distress. prm_casa_return_events also carries
# "RETURNS", which is POS reversals (checked in PROD, Sonnet v01).
DISTRESS_RETURN_REASONS = ("CHEQUE RETURNS", "DDS Rejects/Reversal")
_CASA_MONTH_COL = "ft_avg_casa_eod_balance_in_last_0_3_weeks_avg"  # CA+SA, ~1 month
_CASA_IN_COL = "ft_inflow_casa_amt_in_last_0_0_weeks_sum"
_CASA_OUT_COL = "ft_outflow_casa_amt_in_last_0_0_weeks_sum"


def _month_index(date: Column) -> Column:
    """1 for the observation month, 2 for the one before, …"""
    obs_month = F.trunc(F.col("observation_date"), "month")
    return F.months_between(obs_month, F.trunc(date, "month")).cast("int") + 1


def _by_month(
    obs: DataFrame, series: DataFrame, value: str, prefix: str, months: int
) -> DataFrame:
    """Spread a ``(cif_id, month, value)`` series over ``{prefix}_m1 … _m{months}`` per
    observation (NULL where the month has no value)."""
    return (
        obs.select(*GRAIN, "cif_id")
        .join(series, on="cif_id")
        .withColumn("_k", _month_index(F.col("month")))
        .filter(F.col("_k").between(1, months))
        .groupBy(*GRAIN)
        .agg(
            *[
                F.max(F.when(F.col("_k") == i, F.col(value))).alias(f"{prefix}_m{i}")
                for i in range(1, months + 1)
            ]
        )
    )


# ── Income ────────────────────────────────────────────────────────────────────


def _internal_salary(wm_salary: DataFrame, since: str) -> DataFrame:
    """Salary credits by month, recovered from the weekly WM snapshots dated ``since`` on
    (an earlier snapshot cannot see a later credit).

    Each snapshot carries the last salary credited and how many days before the snapshot
    it was, so snapshot date minus that gap is the credit date. Several snapshots see
    the same credit; they collapse to one value per month.

    This is the only internal salary source. ``feat_payroll_indicator`` is not used: it is
    stamped the month after the credit and flags a subset of these months.
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
    week = parse_yyyymmdd("week_number")
    credit_date = F.date_sub(
        week, F.col("ft_days_since_salary_transaction").cast("int")
    )
    return wm_salary.filter(week >= F.lit(since)).select(
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
    model_id: str,
) -> DataFrame:
    """``income_m1 … income_m{2W}``: salary received per month — the larger of the
    internal credit and the bureau salary (NULL: no salary that month)."""
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    months = 2 * window_months(model_id)
    since = lookback_floor(obs, months)
    monthly = (
        _internal_salary(wm_salary, since)
        .unionByName(_bureau_salary(salary_hist, bureau_cif_bridge))
        .filter(F.col("month") >= F.lit(since))
        .groupBy("cif_id", "month")
        .agg(F.max("amount").alias("amount"))
    )
    return left_join_all(
        obs_base, [_by_month(obs, monthly, "amount", "income", months)]
    )


# ── Liquidity and activity ────────────────────────────────────────────────────


def _casa_by_month(wm_casa_bal: DataFrame, since: str) -> DataFrame:
    """CASA (current + savings) average balance per month from ``since`` on: the 4-week
    average at the month's last weekly snapshot."""
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
        wm_casa_bal.filter(week >= F.lit(since))
        .groupBy("cif_id", F.trunc(week, "month").alias("month"))
        .agg(last_in_month.alias("_last"))
        .select("cif_id", "month", F.col("_last.v").alias("balance"))
    )


def _ext_card_payments(
    obs: DataFrame,
    labelled_txn: DataFrame,
    beneficiary_cards: DataFrame,
    months: int,
    since: str,
) -> DataFrame:
    """Largest single CASA payment to one of the customer's registered external credit
    cards in the window.

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
            (F.col("tran_date") >= F.lit(since))
            & (F.col("in_out_flow") == "outflow")
            & (F.col("product_category") == "CASA")
        )
        .join(F.broadcast(cards), on="transaction_acid", how="leftsemi")
        .select(
            "cif_id", F.col("tran_date").cast("date"), F.col("tran_amt").cast("double")
        )
    )
    return window_agg(
        obs,
        src,
        date_col="tran_date",
        aggs=[F.max("tran_amt").alias("ext_card_payment_max")],
        months=months,
    )


def _casa_activity(
    obs: DataFrame, wm_casa_flow: DataFrame, months: int, since: str
) -> DataFrame:
    """Any CASA credit or debit in the window."""
    require_columns(
        wm_casa_flow,
        ["cif_id", "week_number", _CASA_IN_COL, _CASA_OUT_COL],
        "wm_fea_casa_cc_inflow_outflow",
    )
    week = parse_yyyymmdd("week_number")
    src = wm_casa_flow.filter(week >= F.lit(since)).select(
        "cif_id",
        week.alias("week"),
        ((F.col(_CASA_IN_COL) > 0) | (F.col(_CASA_OUT_COL) > 0))
        .cast("int")
        .alias("_active"),
    )
    return window_agg(
        obs,
        src,
        date_col="week",
        aggs=[F.max("_active").alias("casa_active")],
        months=months,
    )


def build_liquidity_signals(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    wm_casa_bal: DataFrame,
    wm_casa_flow: DataFrame,
    labelled_txn: DataFrame,
    beneficiary_cards: DataFrame,
    model_id: str,
) -> DataFrame:
    """``casa_m1 … casa_m{2W}``, ``ext_card_payment_max``, ``casa_active``."""
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    w = window_months(model_id)
    since = lookback_floor(obs, 2 * w)  # the balances' prior window reaches furthest
    return left_join_all(
        obs_base,
        [
            _by_month(
                obs, _casa_by_month(wm_casa_bal, since), "balance", "casa", 2 * w
            ),
            _ext_card_payments(obs, labelled_txn, beneficiary_cards, w, since),
            _casa_activity(obs, wm_casa_flow, w, since),
        ],
    )


# ── Distress ──────────────────────────────────────────────────────────────────


def build_distress_signals(
    obs_base: DataFrame,
    bureau_alert: DataFrame,
    internal_returns: DataFrame,
    model_id: str,
    payment_order: DataFrame | None = None,
) -> DataFrame:
    """distress_flag: a cheque bounce or direct-debit (DDS) return in the window,
    from the bureau and from the bank's own records.

    * ``bureau_alert`` — bureau-reported bounced cheques, dated by ``extract_date``
      (the bureau pull date, not the bounce date: a bounce can repeat in later pulls);
    * ``internal_returns`` — the bank's own returned cheques / DDS returns as
      ``(cif_id, event_date)`` from ``build_internal_returns``;
    * ``payment_order`` — prm_bureau_payment_order returns; not in PROD yet.
    """
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    w = window_months(model_id)
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
    require_columns(internal_returns, ["cif_id", "event_date"], "internal_returns")
    events = events.unionByName(
        internal_returns.select("cif_id", F.to_date("event_date").alias("event_date"))
    )
    hits = window_agg(
        obs,
        events.filter(F.col("event_date") >= F.lit(lookback_floor(obs, w))),
        date_col="event_date",
        aggs=[F.max(F.lit(1)).alias("distress_flag")],
        months=w,
    )
    return left_join_all(obs_base, [hits]).fillna(0, subset=["distress_flag"])


def build_internal_returns(
    obs_base: DataFrame, return_events: DataFrame, model_id: str
) -> DataFrame:
    """The bank's own returned cheques and DDS returns for the observation base's CIFs, as
    distinct ``(cif_id, event_date, reason)`` from ``prm_casa_return_events`` (all of the
    customer's CASA accounts; the debit and credit legs of a return collapse to one row).

    Stops the run when the table starts after the earliest observation's window (both
    follow ``crx_persona.persona_start_date``; the table was built for an older one).
    """
    require_columns(
        return_events,
        ["cif_id", "tran_date", "reason_for_excluding", "event_month"],
        "prm_casa_return_events",
    )
    since = lookback_floor(obs_base, window_months(model_id))
    # partition column: Spark infers its folder values as dates, so compare ISO strings
    first = return_events.agg(F.min("event_month")).first()[0]
    if first is None or str(first) > since:
        raise ValueError(
            f"prm_casa_return_events starts at {first}, but the observations need returns "
            f"from {since}: rerun casa_primary after changing "
            "crx_persona.persona_start_date"
        )
    cifs = obs_base.select("cif_id").filter(F.col("cif_id").isNotNull()).distinct()
    # since is a month start, so event_month >= since is tran_date >= since, and prunes
    return (
        return_events.filter(
            (F.col("event_month") >= F.lit(since))
            & F.col("reason_for_excluding").isin(*DISTRESS_RETURN_REASONS)
        )
        .join(F.broadcast(cifs), on="cif_id", how="leftsemi")
        .select(
            "cif_id",
            F.to_date("tran_date").alias("event_date"),
            F.col("reason_for_excluding").alias("reason"),
        )
        .distinct()
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

APPLY_VERSION = 6
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
            else:
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
Clean up after mirror bundle 04_a1_returns_date_fix.md, on the bundle's branch.
This bundle adds no temporary pipeline or catalog entry. The bundle 03 check
(`crx_cc_a1_ability_b03_check`) stays until bundle 03's own cleanup prompt.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
