"""T31 — A1 Ability axis v2: GRR MECE points redesign.

Replaces T26's 5-dimension T0-anchored waterfall (``cc_a1_ability``) with the
GRR-specified MECE points system (`data/input/A1_ability_framework_1008_blueprint.md`):
two point dimensions (``income_points``, ``liquidity_points``, each 0/1/2)
summed to a total, a single distress override (cheque bounce / DDS return)
that drops the state one level, and a no-signal gate to ``ability_unknown``.
Purely ``observation_date``-anchored — the blueprint drops every T0-anchored
dimension (utilisation pressure, payment trajectory) the old waterfall used,
so there is no T0 variant here at all.

Additive beside T26 (R18): ``cc_a1_ability/{nodes,enrichers,pipeline}.py`` are
never imported for their classifier logic, only reused via
``enrichers.enrich_salary_months_h2`` / ``enrich_salary_pit`` /
``enrich_bureau_salary`` / ``enrich_ext_cc_payments_h2`` /
``enrich_casa_inflow_h2`` (R14 — zero duplication of those functions).

Five-node pipeline:
    build_a1v2_cif_base(cc_spine, prm_contract, prm_client)
        -> crx_cc_a1v2_cif_base                [Node 1]  CIF-resolved spine rows
    build_a1v2_income_signals(...)
        -> crx_cc_a1v2_income_signals          [Node 2]  salary_months_h2,
                                                         salary_amt_last,
                                                         bureau_salary_*
    build_a1v2_liquidity_signals(...)
        -> crx_cc_a1v2_liquidity_signals       [Node 3]  oldest_overdue_amount,
                                                         casa_recent3m/prior3m_avg,
                                                         ext_cc_payment_*,
                                                         casa_inflow/outflow_cnt_h2
    build_a1v2_distress_signals(...)
        -> crx_cc_a1v2_distress_signals        [Node 4]  bounced_cheque_amt_3m
    build_a1v2_classify(...)
        -> crx_cc_a1_ability_v2                [Node 5]  shipped v2 axis

Grounding (T31 Leg A, `docs/context/results/T31_a1_mece_eda_cc_{60_180,180_plus}_20261022.json`):
  - Oldest-active-overdue-bucket anchor: 100% coverage on both segments,
    monotonic bucket population confirmed by eyeball sample — used as the
    balance-relative anchor (``k_casa``/``k_pay``) per blueprint §4, replacing
    the sheet's rejected ``min_due`` formula.
  - Distress: ``prm_bureau_alert_enriched.bounced_cheque_amount`` confirmed
    present and populated — used directly. ``prm_bureau_payment_order``
    (reason_code) and ``feature_retail_loans`` (aecb_direct_debit_returns_6m)
    are real primary-model fields (confirmed against
    ``src/data_engineering/primary/models/{bureau,external_risk}.py``) but
    both PATH_NOT_FOUND in this PROD environment today (not yet
    materialized) — accepted per the card's decision gate; the optional
    enrichers below degrade to "no evidence" (not an error) when their
    source DataFrame is absent, and are not wired into ``pipeline.py`` yet.
    Wiring them is a pipeline.py input addition only, once the tables land
    — no change to the distress formula itself.
  - Income monthly-amount series: NOT available (``feat_payroll_indicator``
    carries only presence/count columns, no amount column). Approximated
    per the card's sanctioned fallback: ``salary_months_h2`` (presence
    count) combined with the scalar PIT amounts T26 already sources
    (``salary_amt_last``, ``bureau_salary_amt_last``) against the flat
    income floor. The sheet's literal "25% weakening vs prior 3m" trend
    test is NOT built for income — no monthly amount series exists to
    trend. Flagged as a known approximation, same discipline as T26's own
    [CONFIRM] thresholds.
  - CASA 2-of-3-months test: real monthly series confirmed (6 distinct
    months per CIF in a 6m window, ~99.9% coverage). Approximated as a
    recent-3m-average vs prior-3m-average comparison (reusing
    ``ft_avg_eod_balance_in_last_0_2_months_avg`` — already a 3-month
    trailing average per monthly row) rather than a literal per-month
    qualifying count, since the only confirmed balance column is itself a
    rolling average, not a single-month balance. Flagged as an
    approximation of the sheet's literal 2-of-3 test.

Locked decisions (blueprint, do not reopen):
  - Income floor is flat AED 3,000 (``k_inc = 0``) — no balance-relative term.
  - ``k_casa = k_pay = 1`` anchor to ``oldest_overdue_amount``, not
    ``cc_total_outstanding`` and not a derived minimum-due figure.
  - State names carry over unchanged: High/Moderate/Limited/Unknown ->
    ability_high/ability_moderate/ability_low/ability_unknown. T26's
    `cc_a1_ability` keeps its own `ability_limited` label (not renamed).

No confidence column — not needed for this axis (user direction). Breakdown
columns (``a1_income_level_v2``, ``a1_liquidity_level_v2``,
``a1_points_total_v2``, ``a1_distress_flag_v2``) are presence/evidence
breakdowns, analogous to A3's own dimension-level columns.

All ``_TAU_A1V2_*`` / ``_F_*`` / ``_K_*`` thresholds are the blueprint's own
starting values (§6) — explicitly un-validated against PROD data, same
[CONFIRM] discipline as every other axis in this programme.
"""

import datetime
import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.pipelines.crx_persona._spine_utils import _build_cif_bridge
from enbd_collections.pipelines.crx_persona.cc_a1_ability import enrichers
from enbd_collections.pipelines.crx_persona.scoring_engine import (
    StateLadder,
    points_from_level,
)

LOG = logging.getLogger(__name__)

# ── Blueprint thresholds (§6) — starting values, [CONFIRM] against PROD ──────
_TAU_A1V2_N3 = 2  # months out of last 3 that must qualify
_F_INT = (
    3000.0  # internal/bureau salary floor (k_inc=0 — flat, no balance-relative term)
)
_F_CASA = 3000.0  # CASA average balance floor
_F_PAY = 500.0  # external card payment floor
_DEMIN = 1000.0  # smallest amount counting as any evidence
_K_CASA = 1.0  # CASA x oldest-overdue-bucket multiple
_K_PAY = 1.0  # external payment x oldest-overdue-bucket multiple
_D_CASA = 0.5  # CASA weakening threshold (share drop, recent-3m vs prior-3m)
_S_HIGH = 4  # points needed for High
_S_MOD = 2  # points needed for Moderate

_INCOME_POINTS_BY_LEVEL = {"stable": 2, "weak": 1, "none": 0}
_LIQUIDITY_POINTS_BY_LEVEL = {"adequate": 2, "weak": 1, "none": 0}

_STATE_LADDER = StateLadder(
    high="ability_high",
    moderate="ability_moderate",
    low="ability_low",
    unknown="ability_unknown",
    high_from_points=_S_HIGH,
    moderate_from_points=_S_MOD,
)

_OVERDUE_BUCKET_COLS = [f"overdue_bucket_{i:02d}" for i in range(1, 9)]


# ── Node 1: build_a1v2_cif_base ──────────────────────────────────────────────


def build_a1v2_cif_base(
    cc_spine: DataFrame,
    contract: DataFrame,
    client: DataFrame,
) -> DataFrame:
    """Resolve CIF for every spine row; emit only CIF-resolved rows.

    Purely observation_date-anchored (no T0/spell join — this axis has no
    T0-anchored dimension, per the blueprint). Mirrors T26's build_a1_cif_bridge
    CIF-resolution shape (R14 — same _build_cif_bridge helper), but applied
    directly to the spine instead of a spell-windowed base.

    Args:
        cc_spine:  Model-id-scoped spine — (contract_id, observation_date).
        contract:  prm_contract — contract_id -> client_id.
        client:    prm_client  — client_id -> cif_id.

    Returns:
        crx_cc_a1v2_cif_base — (account_id, observation_date, cif_id).
        Only rows where CIF was resolved.
    """
    cif_bridge = _build_cif_bridge(contract, client)

    # Rename contract_id -> account_id before joining (not after) so the two
    # sides never carry a same-named column into the join at the same time —
    # cif_bridge's own contract_id is then unambiguous and can be dropped
    # directly. Same shape as T26's build_a1_cif_bridge / enrich_prm_balance.
    spine_sel = cc_spine.select(
        F.col("contract_id").alias("account_id"),
        F.col("observation_date").cast("date"),
    )

    with_cif = spine_sel.join(
        cif_bridge,
        on=spine_sel["account_id"] == cif_bridge["contract_id"],
        how="left",
    ).drop("contract_id")

    return with_cif.filter(F.col("cif_id").isNotNull()).select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("cif_id"),
    )


# ── Node 2: build_a1v2_income_signals ────────────────────────────────────────


def build_a1v2_income_signals(
    cif_base: DataFrame,
    feat_payroll: DataFrame,
    wm_salary: DataFrame,
    stg_salary_hist: DataFrame,
    prm_bureau_cif_bridge: DataFrame,
) -> DataFrame:
    """Income evidence at observation_date anchor — presence counts + scalar amounts.

    Three enrichers reused unmodified from cc_a1_ability.enrichers (R14),
    anchored to observation_date instead of t0:
      1. enrich_salary_months_h2   -> salary_months_h2 (count of last-3-months
         with payroll_flag=1 — presence, not a monthly amount series; see
         module docstring on the income-amount-series gap).
      2. enrich_salary_pit         -> salary_amt_last (latest WM PIT salary
         amount — scalar, not monthly).
      3. enrich_bureau_salary      -> bureau_salary_present_6m_flag,
         bureau_salary_amt_last (6m window bureau salary — single-pull
         reality per T31 Leg A §5/§9.5).

    Args:
        cif_base:               crx_cc_a1v2_cif_base.
        feat_payroll:           feat_payroll_indicator (retail.feature_space).
        wm_salary:              wm_fea_salary_days_since_increment (WM).
        stg_salary_hist:        stg_aecb_salary_history (AECB).
        prm_bureau_cif_bridge:  bureau file UUID -> cif_id bridge.

    Returns:
        crx_cc_a1v2_income_signals — (account_id, observation_date,
            salary_months_h2, salary_amt_last, bureau_salary_present_6m_flag,
            bureau_salary_amt_last).
    """
    grain_key = ("account_id", "observation_date")
    anchor_col = "observation_date"

    salary_h2 = enrichers.enrich_salary_months_h2(
        cif_base, feat_payroll, anchor_col, grain_key
    )
    sal_pit = enrichers.enrich_salary_pit(cif_base, wm_salary, anchor_col, grain_key)
    bur_sal = enrichers.enrich_bureau_salary(
        cif_base, stg_salary_hist, prm_bureau_cif_bridge, anchor_col, grain_key
    )

    result = cif_base.select(*grain_key)

    if salary_h2 is not None:
        result = result.join(salary_h2, on=list(grain_key), how="left")
    else:
        result = result.withColumn("salary_months_h2", F.lit(None).cast("int"))

    if sal_pit is not None:
        result = result.join(
            sal_pit.select(*grain_key, "salary_amt_last"),
            on=list(grain_key),
            how="left",
        )
    else:
        result = result.withColumn("salary_amt_last", F.lit(None).cast("double"))

    if bur_sal is not None:
        result = result.join(bur_sal, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "bureau_salary_present_6m_flag", F.lit(None).cast("int")
        ).withColumn("bureau_salary_amt_last", F.lit(None).cast("double"))

    return result.select(
        *grain_key,
        F.col("salary_months_h2").cast("int"),
        F.col("salary_amt_last").cast("double"),
        F.col("bureau_salary_present_6m_flag").cast("int"),
        F.col("bureau_salary_amt_last").cast("double"),
    )


# ── Node 3: build_a1v2_liquidity_signals ─────────────────────────────────────


def _enrich_oldest_overdue_amount(
    base: DataFrame,
    prm_balance: DataFrame,
    anchor_col: str,
    grain_key: tuple,
) -> DataFrame | None:
    """PIT-join prm_balance's 8 overdue buckets; derive the oldest active amount.

    "Oldest active overdue bucket" = the value in the highest-indexed
    non-null/non-zero overdue_bucket_01..08 column — buckets accumulate
    (confirmed by T31 Leg A check 1 eyeball sample: lower-indexed buckets
    populate first and stay populated as the account ages), so the
    highest-active-index bucket is the longest-aged unpaid slice. Replaces
    the rejected cc_total_outstanding/min_due anchor (blueprint §4).

    Mirrors cc_a1_ability.enrichers.enrich_prm_balance's exact PIT join
    pattern (anchor-collision handling, contract_id == account_id join).

    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (grain_key..., oldest_overdue_amount).
    """
    _required = ["contract_id", "observation_date"] + _OVERDUE_BUCKET_COLS
    missing = [c for c in _required if c not in prm_balance.columns]
    if missing:
        LOG.warning(
            "_enrich_oldest_overdue_amount: prm_balance missing %s"
            " — oldest_overdue_amount will be NULL",
            missing,
        )
        return None

    _grain_cols = list(grain_key)

    bal = prm_balance.select(
        F.col("contract_id"),
        F.col("observation_date").cast("date").alias("_bal_obs_date"),
        *[F.col(c).cast("double").alias(c) for c in _OVERDUE_BUCKET_COLS],
    )

    if anchor_col in _grain_cols:
        base_sel = base.select(*_grain_cols).withColumn("_anchor", F.col(anchor_col))
    else:
        base_sel = base.select(*_grain_cols, F.col(anchor_col).alias("_anchor"))

    joined = (
        base_sel.join(
            bal,
            on=(base_sel["account_id"] == bal["contract_id"]),
            how="left",
        )
        .filter(
            F.col("_bal_obs_date").isNotNull()
            & (F.col("_bal_obs_date") <= F.col("_anchor"))
        )
        .drop("contract_id", "_anchor")
    )

    w = Window.partitionBy(*_grain_cols).orderBy(F.col("_bal_obs_date").desc())
    pit = joined.withColumn("_rn", F.row_number().over(w)).filter(F.col("_rn") == 1)

    # Highest-indexed non-null/non-zero bucket wins — buckets accumulate from
    # 01 upward, so coalescing from 08 down to 01 (skipping nulls/zeros) picks
    # the longest-aged unpaid slice.
    oldest_expr = F.coalesce(
        *[F.when(F.col(c) > 0, F.col(c)) for c in reversed(_OVERDUE_BUCKET_COLS)]
    )

    return pit.select(*_grain_cols, oldest_expr.alias("oldest_overdue_amount"))


def _enrich_casa_eod_balance_windows(
    base: DataFrame,
    feat_casa_bal: DataFrame,
    anchor_col: str,
    grain_key: tuple,
) -> DataFrame | None:
    """Recent-3m vs prior-3m CASA average balance from feat_casa_eod_balance.

    T31 Leg A check 3 confirmed 6 distinct month_end_date rows per CIF in the
    [obs-6m, obs) window for ~99.9% of CIFs on both segments — a real monthly
    series exists. Each row's ft_avg_eod_balance_in_last_0_2_months_avg is
    already a 3-month-trailing average as of that row's month_end_date (the
    same column cc_a1_ability.enrichers uses for a single PIT sample), so the
    latest row in [obs-3m, obs) stands in for "the recent 3-month average" and
    the latest row in [obs-6m, obs-3m) stands in for "the prior 3-month
    average" — reusing the one confirmed real column rather than deriving a
    new one (R9). This approximates the blueprint's literal 2-of-3-months
    qualifying count with a window-average comparison; flagged as an
    approximation, not an exact re-derivation.

    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (grain_key..., casa_recent3m_avg, casa_prior3m_avg).
    """
    _CASA_BAL_COL = enrichers._CASA_BAL_COL  # pylint: disable=protected-access
    _required = ["month_end_date", _CASA_BAL_COL]
    missing = [c for c in _required if c not in feat_casa_bal.columns]
    if missing:
        LOG.warning(
            "_enrich_casa_eod_balance_windows: feat_casa_eod_balance missing %s"
            " — casa_recent3m_avg/casa_prior3m_avg will be NULL",
            missing,
        )
        return None

    cb_dated = feat_casa_bal.withColumn(
        "_month_date", F.col("month_end_date").cast("date")
    ).select("cif_id", "_month_date", _CASA_BAL_COL)

    joined = base.join(cb_dated, on="cif_id", how="inner").filter(
        (F.col("_month_date") >= F.date_sub(F.col(anchor_col), 180))
        & (F.col("_month_date") < F.col(anchor_col))
    )

    recent = joined.filter(F.col("_month_date") >= F.date_sub(F.col(anchor_col), 90))
    prior = joined.filter(F.col("_month_date") < F.date_sub(F.col(anchor_col), 90))

    w_recent = Window.partitionBy(*grain_key).orderBy(F.col("_month_date").desc())
    recent_pit = (
        recent.withColumn("_rn", F.row_number().over(w_recent))
        .filter(F.col("_rn") == 1)
        .select(*grain_key, F.col(_CASA_BAL_COL).alias("casa_recent3m_avg"))
    )

    w_prior = Window.partitionBy(*grain_key).orderBy(F.col("_month_date").desc())
    prior_pit = (
        prior.withColumn("_rn", F.row_number().over(w_prior))
        .filter(F.col("_rn") == 1)
        .select(*grain_key, F.col(_CASA_BAL_COL).alias("casa_prior3m_avg"))
    )

    return recent_pit.join(prior_pit, on=list(grain_key), how="outer")


def _enrich_casa_outflow_h2(
    cif_base: DataFrame,
    wm_casa_inflow: DataFrame,
    anchor_col: str,
    grain_key: tuple,
) -> DataFrame | None:
    """H2 generic CASA outflow count from wm_fea_casa_cc_inflow_outflow.

    Mirrors cc_a1_ability.enrichers.enrich_casa_inflow_h2 exactly, reading
    the outflow-named column T31 Leg A check 4 confirmed exists alongside the
    inflow column (ft_outflow_casa_amt_in_last_0_0_weeks_sum) — needed for
    the any-direction CASA-activity signal gate (blueprint §2.4).

    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (grain_key..., casa_outflow_cnt_h2).
    """
    _OUTFLOW_COL = "ft_outflow_casa_amt_in_last_0_0_weeks_sum"
    if _OUTFLOW_COL not in wm_casa_inflow.columns:
        LOG.warning(
            "_enrich_casa_outflow_h2: wm_fea_casa_cc_inflow_outflow missing '%s'"
            " — casa_outflow_cnt_h2 will be NULL",
            _OUTFLOW_COL,
        )
        return None

    co_dated = wm_casa_inflow.withColumn(
        "_week_date", F.to_date(F.col("week_number").cast("string"), "yyyyMMdd")
    ).select("cif_id", "_week_date", _OUTFLOW_COL)

    outflow_h2 = (
        cif_base.join(co_dated, on="cif_id", how="inner")
        .filter(
            (F.col("_week_date") >= F.date_sub(F.col(anchor_col), 90))
            & (F.col("_week_date") < F.col(anchor_col))
        )
        .groupBy(*grain_key)
        .agg(
            F.sum(F.when(F.col(_OUTFLOW_COL) > 0, F.lit(1)).otherwise(F.lit(0)))
            .cast("int")
            .alias("casa_outflow_cnt_h2")
        )
    )

    return outflow_h2


def build_a1v2_liquidity_signals(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    cif_base: DataFrame,
    prm_balance: DataFrame,
    feat_casa_bal: DataFrame,
    wm_casa_inflow: DataFrame,
    wm_labelled_transactions: DataFrame,
    beneficiary_cards: DataFrame,
    crx_persona: dict,
) -> DataFrame:
    """Liquidity evidence + the balance-relative anchor, at observation_date.

    New enrichers (oldest_overdue_amount, casa window averages, CASA
    outflow count) plus one reused unmodified from cc_a1_ability.enrichers
    (R14): enrich_ext_cc_payments_h2 and enrich_casa_inflow_h2.

    Args:
        cif_base:                 crx_cc_a1v2_cif_base.
        prm_balance:              prm_balance — overdue_bucket_01..08.
        feat_casa_bal:            feat_casa_eod_balance (retail.feature_space).
        wm_casa_inflow:           wm_fea_casa_cc_inflow_outflow (WM).
        wm_labelled_transactions: wm_pri_labelled_transactions (WM).
        beneficiary_cards:        raw_beneficiary_cards.
        crx_persona:              Persona param dict (persona_start_date).

    Returns:
        crx_cc_a1v2_liquidity_signals — (account_id, observation_date,
            oldest_overdue_amount, casa_recent3m_avg, casa_prior3m_avg,
            ext_cc_payment_amt_h2, ext_cc_payment_cnt_h2, casa_inflow_cnt_h2,
            casa_outflow_cnt_h2).
    """
    grain_key = ("account_id", "observation_date")
    anchor_col = "observation_date"

    wm_labelled_transactions = wm_labelled_transactions.filter(
        F.col("tran_date") >= F.lit(crx_persona["persona_start_date"])
    )

    overdue = _enrich_oldest_overdue_amount(
        cif_base, prm_balance, anchor_col, grain_key
    )
    casa_windows = _enrich_casa_eod_balance_windows(
        cif_base, feat_casa_bal, anchor_col, grain_key
    )
    ext_pay = enrichers.enrich_ext_cc_payments_h2(
        cif_base, wm_labelled_transactions, beneficiary_cards, anchor_col, grain_key
    )
    casa_inflow = enrichers.enrich_casa_inflow_h2(
        cif_base, wm_casa_inflow, anchor_col, grain_key
    )
    casa_outflow = _enrich_casa_outflow_h2(
        cif_base, wm_casa_inflow, anchor_col, grain_key
    )

    result = cif_base.select(*grain_key)

    if overdue is not None:
        result = result.join(overdue, on=list(grain_key), how="left")
    else:
        result = result.withColumn("oldest_overdue_amount", F.lit(None).cast("double"))

    if casa_windows is not None:
        result = result.join(casa_windows, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "casa_recent3m_avg", F.lit(None).cast("double")
        ).withColumn("casa_prior3m_avg", F.lit(None).cast("double"))

    if ext_pay is not None:
        result = result.join(ext_pay, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "ext_cc_payment_amt_h2", F.lit(None).cast("double")
        ).withColumn("ext_cc_payment_cnt_h2", F.lit(None).cast("int"))

    if casa_inflow is not None:
        result = result.join(
            casa_inflow.select(*grain_key, "casa_inflow_cnt_h2"),
            on=list(grain_key),
            how="left",
        )
    else:
        result = result.withColumn("casa_inflow_cnt_h2", F.lit(None).cast("int"))

    if casa_outflow is not None:
        result = result.join(casa_outflow, on=list(grain_key), how="left")
    else:
        result = result.withColumn("casa_outflow_cnt_h2", F.lit(None).cast("int"))

    return result.select(
        *grain_key,
        F.col("oldest_overdue_amount").cast("double"),
        F.col("casa_recent3m_avg").cast("double"),
        F.col("casa_prior3m_avg").cast("double"),
        F.col("ext_cc_payment_amt_h2").cast("double"),
        F.col("ext_cc_payment_cnt_h2").cast("int"),
        F.col("casa_inflow_cnt_h2").cast("int"),
        F.col("casa_outflow_cnt_h2").cast("int"),
    )


# ── Node 4: build_a1v2_distress_signals ──────────────────────────────────────


def _enrich_distress_bureau_alert(
    cif_base: DataFrame,
    prm_bureau_alert: DataFrame,
    anchor_col: str,
    grain_key: tuple,
) -> DataFrame | None:
    """3-month bounced-cheque amount from prm_bureau_alert_enriched.

    T31 Leg A check 2 confirmed bounced_cheque_amount is present and
    populated on this table (independent of the return_date column, which
    is absent — not used here). Window: [anchor-90d, anchor), same pre-T0-
    style lookback discipline as cc_a1_ability.enrichers.enrich_bureau_alerts.

    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (grain_key..., bounced_cheque_amt_3m).
    """
    _required = ["cif_id", "extract_date", "bounced_cheque_amount"]
    missing = [c for c in _required if c not in prm_bureau_alert.columns]
    if missing:
        LOG.warning(
            "_enrich_distress_bureau_alert: prm_bureau_alert_enriched missing %s"
            " — bounced_cheque_amt_3m will be NULL",
            missing,
        )
        return None

    alerts_dated = prm_bureau_alert.withColumn(
        "_alert_date", F.to_date(F.col("extract_date"))
    ).select(
        F.col("cif_id").alias("_bur_cif_id"),
        "_alert_date",
        F.col("bounced_cheque_amount").cast("double").alias("_bounced_amt"),
    )

    joined = cif_base.join(
        alerts_dated,
        on=cif_base["cif_id"] == alerts_dated["_bur_cif_id"],
        how="inner",
    ).filter(
        (F.col("_alert_date") >= F.date_sub(F.col(anchor_col), 90))
        & (F.col("_alert_date") < F.col(anchor_col))
    )

    return joined.groupBy(*grain_key).agg(
        F.sum(F.coalesce(F.col("_bounced_amt"), F.lit(0.0)))
        .cast("double")
        .alias("bounced_cheque_amt_3m")
    )


def _enrich_distress_payment_order(
    cif_base: DataFrame,
    prm_bureau_payment_order: DataFrame | None,
    anchor_col: str,
    grain_key: tuple,
) -> DataFrame | None:
    """Optional distress source: prm_bureau_payment_order.reason_code (3m window).

    PATH_NOT_FOUND in this PROD environment as of T31 Leg A (2026-10-22) — not
    yet materialized. Degrades to None (no evidence, not an error) whenever
    the caller doesn't have this table to pass in; wiring it is a pipeline.py
    input addition only (see nodes.py module docstring) — no change needed
    here once it lands, since the schema guard and join logic are already
    written against the real BureauPaymentOrder primary-model field names
    (cif_id, return_date, reason_code — confirmed from
    src/data_engineering/primary/models/bureau.py, not guessed).

    Returns None if the table is absent or required columns are missing.
    Returns DataFrame with (grain_key..., payment_order_distress_flag).
    """
    if prm_bureau_payment_order is None:
        return None

    _required = ["cif_id", "return_date", "reason_code"]
    missing = [c for c in _required if c not in prm_bureau_payment_order.columns]
    if missing:
        LOG.warning(
            "_enrich_distress_payment_order: prm_bureau_payment_order missing %s"
            " — payment_order_distress_flag will be NULL",
            missing,
        )
        return None

    po_dated = prm_bureau_payment_order.withColumn(
        "_return_date", F.to_date(F.col("return_date"))
    ).select(
        F.col("cif_id").alias("_po_cif_id"),
        "_return_date",
        F.col("reason_code"),
    )

    joined = cif_base.join(
        po_dated,
        on=cif_base["cif_id"] == po_dated["_po_cif_id"],
        how="inner",
    ).filter(
        (F.col("_return_date") >= F.date_sub(F.col(anchor_col), 90))
        & (F.col("_return_date") < F.col(anchor_col))
        & F.col("reason_code").isNotNull()
    )

    return joined.groupBy(*grain_key).agg(
        F.lit(1).cast("int").alias("payment_order_distress_flag")
    )


def _enrich_distress_retail_loans(
    cif_base: DataFrame,
    feature_retail_loans: DataFrame | None,
    grain_key: tuple,
) -> DataFrame | None:
    """Optional distress source: feature_retail_loans.aecb_direct_debit_returns_6m.

    PATH_NOT_FOUND in this PROD environment as of T31 Leg A (2026-10-22) — not
    yet materialized. cif_id-only join, explicitly not PIT-correct (bureau
    data is person-level and this table carries no per-row date column usable
    for a windowed join at this grain — same caveat T31 Leg A flagged). Same
    "degrades to None" contract as _enrich_distress_payment_order.

    Returns None if the table is absent or required columns are missing.
    Returns DataFrame with (grain_key..., retail_loans_distress_flag).
    """
    if feature_retail_loans is None:
        return None

    _required = ["cif_id", "aecb_direct_debit_returns_6m"]
    missing = [c for c in _required if c not in feature_retail_loans.columns]
    if missing:
        LOG.warning(
            "_enrich_distress_retail_loans: feature_retail_loans missing %s"
            " — retail_loans_distress_flag will be NULL",
            missing,
        )
        return None

    rl_dated = feature_retail_loans.select(
        F.col("cif_id").alias("_rl_cif_id"),
        F.col("aecb_direct_debit_returns_6m").cast("int").alias("_dd_returns_6m"),
    )

    joined = cif_base.join(
        rl_dated, on=cif_base["cif_id"] == rl_dated["_rl_cif_id"], how="inner"
    ).filter(F.col("_dd_returns_6m") > 0)

    return joined.groupBy(*grain_key).agg(
        F.lit(1).cast("int").alias("retail_loans_distress_flag")
    )


def build_a1v2_distress_signals(
    cif_base: DataFrame,
    prm_bureau_alert: DataFrame,
    prm_bureau_payment_order: DataFrame | None = None,
    feature_retail_loans: DataFrame | None = None,
) -> DataFrame:
    """Cheque-bounce / DDS-return distress evidence at observation_date anchor.

    prm_bureau_payment_order / feature_retail_loans default to None — not
    wired as formal pipeline inputs yet (both PATH_NOT_FOUND in PROD today,
    T31 Leg A). When wired later (pipeline.py input addition only), their
    OR-terms activate automatically with no change to this function.

    Args:
        cif_base:                 crx_cc_a1v2_cif_base.
        prm_bureau_alert:         prm_bureau_alert_enriched (AECB).
        prm_bureau_payment_order: Optional — prm_bureau_payment_order (AECB).
        feature_retail_loans:     Optional — feature_retail_loans.

    Returns:
        crx_cc_a1v2_distress_signals — (account_id, observation_date,
            distress_flag).
    """
    grain_key = ("account_id", "observation_date")
    anchor_col = "observation_date"

    bur_alert = _enrich_distress_bureau_alert(
        cif_base, prm_bureau_alert, anchor_col, grain_key
    )
    pay_order = _enrich_distress_payment_order(
        cif_base, prm_bureau_payment_order, anchor_col, grain_key
    )
    retail_loans = _enrich_distress_retail_loans(
        cif_base, feature_retail_loans, grain_key
    )

    result = cif_base.select(*grain_key)

    if bur_alert is not None:
        result = result.join(bur_alert, on=list(grain_key), how="left")
    else:
        result = result.withColumn("bounced_cheque_amt_3m", F.lit(None).cast("double"))

    if pay_order is not None:
        result = result.join(pay_order, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "payment_order_distress_flag", F.lit(None).cast("int")
        )

    if retail_loans is not None:
        result = result.join(retail_loans, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "retail_loans_distress_flag", F.lit(None).cast("int")
        )

    result = result.withColumn(
        "distress_flag",
        F.when(
            (F.coalesce(F.col("bounced_cheque_amt_3m"), F.lit(0.0)) > 0)
            | (F.coalesce(F.col("payment_order_distress_flag"), F.lit(0)) == 1)
            | (F.coalesce(F.col("retail_loans_distress_flag"), F.lit(0)) == 1),
            F.lit(1),
        )
        .otherwise(F.lit(0))
        .cast("int"),
    )

    return result.select(*grain_key, "distress_flag")


# ── Node 5: build_a1v2_classify ──────────────────────────────────────────────


def _income_level_col() -> "F.Column":
    """income_points dimension: Stable/Weak/None (blueprint §2.1, k_inc=0 flat floor)."""
    _amt_evidence = F.coalesce(
        F.col("salary_amt_last"), F.col("bureau_salary_amt_last")
    )
    _stable = (
        (F.coalesce(F.col("salary_months_h2"), F.lit(0)) >= _TAU_A1V2_N3)
        & _amt_evidence.isNotNull()
        & (_amt_evidence >= _F_INT)
    )
    _weak = (
        (F.coalesce(F.col("salary_months_h2"), F.lit(0)) >= 1)
        | (F.coalesce(F.col("bureau_salary_present_6m_flag"), F.lit(0)) == 1)
        | (_amt_evidence.isNotNull() & (_amt_evidence >= _DEMIN))
    )
    return (
        F.when(_stable, F.lit("stable"))
        .when(_weak, F.lit("weak"))
        .otherwise(F.lit("none"))
    )


def _liquidity_level_col() -> "F.Column":
    """liquidity_points dimension: Adequate/Weak/None (blueprint §2.2).

    casa_floor/pay_floor anchor to oldest_overdue_amount (k_casa=k_pay=1);
    falls back to the flat floor alone when oldest_overdue_amount is NULL
    (account has no active overdue bucket in scope — treat the balance-
    relative term as 0, consistent with setting k=0 per blueprint §4).
    """
    _casa_floor = F.greatest(
        F.lit(_F_CASA), _K_CASA * F.coalesce(F.col("oldest_overdue_amount"), F.lit(0.0))
    )
    _pay_floor = F.greatest(
        F.lit(_F_PAY), _K_PAY * F.coalesce(F.col("oldest_overdue_amount"), F.lit(0.0))
    )

    _casa_weakening = (
        F.col("casa_recent3m_avg").isNotNull()
        & F.col("casa_prior3m_avg").isNotNull()
        & (F.col("casa_recent3m_avg") < F.col("casa_prior3m_avg") * (1 - _D_CASA))
    )

    _casa_adequate = (
        F.col("casa_recent3m_avg").isNotNull()
        & (F.col("casa_recent3m_avg") >= _casa_floor)
        & (~_casa_weakening)
    )
    _ext_pay_adequate = (F.coalesce(F.col("ext_cc_payment_cnt_h2"), F.lit(0)) >= 1) & (
        F.coalesce(F.col("ext_cc_payment_amt_h2"), F.lit(0.0)) >= _pay_floor
    )

    _casa_weak = F.col("casa_recent3m_avg").isNotNull() & (
        F.col("casa_recent3m_avg") >= _DEMIN
    )
    _ext_pay_weak = (F.coalesce(F.col("ext_cc_payment_cnt_h2"), F.lit(0)) >= 1) & (
        F.coalesce(F.col("ext_cc_payment_amt_h2"), F.lit(0.0)) >= _DEMIN
    )

    _adequate = _casa_adequate | _ext_pay_adequate
    _weak = _casa_weak | _ext_pay_weak

    return (
        F.when(_adequate, F.lit("adequate"))
        .when(_weak, F.lit("weak"))
        .otherwise(F.lit("none"))
    )


def build_a1v2_classify(
    cif_base: DataFrame,
    income_signals: DataFrame,
    liquidity_signals: DataFrame,
    distress_signals: DataFrame,
) -> DataFrame:
    """Assemble signals and classify the A1 v2 MECE state.

    income_points/liquidity_points via scoring_engine.points_from_level;
    distress is a single boolean override (OR of the 3 distress sources —
    never a prioritized reason list, unlike A3; A1 has exactly one override
    condition per the blueprint); is_unknown (signal gate, blueprint §2.4) is
    computed inline here and passed to StateLadder.state() alongside
    points_total and the distress override.

    Args:
        cif_base:          crx_cc_a1v2_cif_base.
        income_signals:    crx_cc_a1v2_income_signals.
        liquidity_signals: crx_cc_a1v2_liquidity_signals.
        distress_signals:  crx_cc_a1v2_distress_signals.

    Returns:
        crx_cc_a1_ability_v2 — (account_id, observation_date, a1_state_v2,
            a1_provenance_v2, a1_income_level_v2, a1_liquidity_level_v2,
            a1_points_total_v2, a1_distress_flag_v2, computed_at).
        a1_state_v2 in {ability_high, ability_moderate, ability_low,
            ability_unknown}.
    """
    grain_key = ["account_id", "observation_date"]

    result = (
        cif_base.select(*grain_key)
        .join(income_signals, on=grain_key, how="left")
        .join(liquidity_signals, on=grain_key, how="left")
        .join(distress_signals, on=grain_key, how="left")
    )

    result = result.withColumn("a1_income_level_v2", _income_level_col()).withColumn(
        "a1_liquidity_level_v2", _liquidity_level_col()
    )

    result = result.withColumn(
        "a1_income_points_v2",
        points_from_level(F.col("a1_income_level_v2"), _INCOME_POINTS_BY_LEVEL),
    ).withColumn(
        "a1_liquidity_points_v2",
        points_from_level(F.col("a1_liquidity_level_v2"), _LIQUIDITY_POINTS_BY_LEVEL),
    )

    result = result.withColumn(
        "a1_points_total_v2",
        F.col("a1_income_points_v2") + F.col("a1_liquidity_points_v2"),
    )

    result = result.withColumn(
        "a1_distress_flag_v2", F.coalesce(F.col("distress_flag"), F.lit(0)) == 1
    )

    _has_casa_activity = (F.coalesce(F.col("casa_inflow_cnt_h2"), F.lit(0)) > 0) | (
        F.coalesce(F.col("casa_outflow_cnt_h2"), F.lit(0)) > 0
    )
    _is_unknown = (
        (F.col("a1_income_points_v2") == 0)
        & (F.col("a1_liquidity_points_v2") == 0)
        & (~F.col("a1_distress_flag_v2"))
        & (~_has_casa_activity)
    )

    result = result.withColumn(
        "a1_state_v2",
        _STATE_LADDER.state(
            F.col("a1_points_total_v2"), F.col("a1_distress_flag_v2"), _is_unknown
        ),
    )

    result = result.withColumn(
        "a1_provenance_v2",
        F.when(F.col("a1_state_v2") == "ability_unknown", F.lit("no_signal")).otherwise(
            F.lit("observed")
        ),
    )

    output = result.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("a1_state_v2").cast("string"),
        F.col("a1_provenance_v2").cast("string"),
        F.col("a1_income_level_v2").cast("string"),
        F.col("a1_liquidity_level_v2").cast("string"),
        F.col("a1_points_total_v2").cast("int"),
        F.col("a1_distress_flag_v2").cast("int"),
        F.lit(datetime.date.today().isoformat()).cast("date").alias("computed_at"),
    )

    _log_a1v2_stats(output)
    return output


def _log_a1v2_stats(df: DataFrame) -> None:
    """Log state distribution for the A1 ability v2 axis."""
    state_counts = df.groupBy("a1_state_v2").count().orderBy("a1_state_v2").collect()
    total = sum(r["count"] for r in state_counts)
    LOG.info("build_a1v2_classify — state distribution (n=%d):", total)
    for row in state_counts:
        pct = 100.0 * row["count"] / max(total, 1)
        LOG.info(
            "  a1_state_v2=%-25s %6d  (%5.1f%%)",
            row["a1_state_v2"],
            row["count"],
            pct,
        )
