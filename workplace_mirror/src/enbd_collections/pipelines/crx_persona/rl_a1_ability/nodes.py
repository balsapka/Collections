# pylint: disable=R0917,R0801
"""RL-A1-1/9 — A1 Income-Ability axis for Retail Loans (4-node pipeline).

Four-node modular pipeline (T0 nodes removed in RL-A1-5 cleanup; Group A
departure removed in RL-A1-6 cleanup; Node 1 base join eliminated in
RL-A1-7 cleanup — trivial pass-through, crx_rl_a4_spine feeds Nodes 2r/3r/4r/4b
directly, and Node 5 inlines the eosb_like_flag / prior_spell_cnt_12m lookup).
cif_id is carried directly in crx_rl_a4_spine — no separate CIF bridge node needed.

    build_rl_a1_group_b_income_recent(crx_rl_a4_spine, ...)
        → crx_rl_a1_group_b_income_recent  [Node 2r] obs-date income signals

    build_rl_a1_group_b_bureau_recent(crx_rl_a4_spine, ...)
        → crx_rl_a1_group_b_bureau_recent  [Node 3r] obs-date bureau signals

    build_rl_a1_group_c_recent(crx_rl_a4_spine, int_loan_master)
        → crx_rl_a1_group_c_recent         [Node 4r] obs-date EMI coverage

    build_rl_a1_group_d_origination(crx_rl_a4_spine, feat_loan_application_risk)
        → crx_rl_a1_group_d                [Node 4b] Group D: static origination anchors

    build_rl_a1_classify(crx_rl_a4_spine, crx_rl_departure_signature,
        crx_rl_spell_table, ..., crx_rl_a1_group_d)
        → crx_rl_a1_ability                [Node 5]  ← shipped persona axis

Nodes removed (RL-A1-5 cleanup): Node 2 (T0 income), Node 3 (T0 bureau), Node 4 (Group C T0).
Nodes removed (RL-A1-6 cleanup): Node 0 (Group A T0 payroll departure).
Nodes removed (RL-A1-7 cleanup): Node 1 (crx_rl_a1_base join — trivial pass-through).
All a1_state and a1_income_source derivations use obs-date-anchored _recent signals only.
a1_provenance value set: {obs_date, no_signal}.

RL-A1-9 redesign (`data/input/ability_redesign_v3.md`): the classifier no longer
imports `_build_ability_conditions` / `_apply_ability_classifier_primary` from
`cc_a1_ability.nodes` — those stay untouched (R18). The RL waterfall is now
EMI-relative (Signal C: `monthly_emi_recent`) with CASA/payroll refinements
(Signals A/B/D/E) and AECB-anchored arms RL-A1-8 decided KEEP
(`moderate_arm2`, `low_tier2`) plus RL-A1-19's timing-anchored salary arm
(`high_arm3c`, replacing `high_arm7`/`high_arm3b`), built fresh in
`_build_rl_ability_conditions` / `_apply_rl_ability_classifier` below.
`"ability_limited"` is renamed `"ability_low"` (RL pipeline only — CC keeps
`"ability_limited"`), `recovery_signal` is dropped (depended only on the now-
removed import; v3 §7.4 — no replacement, see RESULTS_RL.md schema diff).
Excluded this round (separate follow-up task, see TASKS_RL.md Track E
RL-A1-14): `moderate_arm4a`, `moderate_arm4b`, `low_tier1` and their unique
AECB input columns. `ability_low` Condition 2 shipped under RL-A1-15 —
**removed entirely by RL-A1-21** (see below), its premise
(`inflow_present_h4_h6_recent`) no longer exists.

RL-A1-17 (fixed directly, per the RL-A4-2 cif_id precedent — RL-A1-9 is still
in-progress/unshipped, so R19 does not block iterating our own in-progress
build): Node 4r carried `disbursement_amount_recent`/`disbursement_date_recent`
(intermediate-only) to give Signal D a real disbursement exclusion instead of
RL-A1-9's unfiltered-alias fallback; `aecb_is_recent` is now a genuine
6-month recency cutoff instead of "any pull ever". **Historical note:** the
disbursement-exclusion half is removed entirely by RL-A1-21 (Signal D is
gone); the `high_arm7`/`high_arm3b` AECB carve-out this paragraph originally
described is removed and replaced by RL-A1-19's timing-anchored arms (see
below) — only the plain 6-month `aecb_is_recent` cutoff survives, still used
by `moderate_arm2`/`low_tier2`.

RL-A1-18 (CASA GL self-transfer wash exclusion for Signal D): Node 2r called
`enrichers.enrich_casa_self_transfer_wash_h2` on `comp_financial_tran_repos_dly`
(scope-first, R20/R14) to sum same-day GL-subhead bookkeeping credits
(`tran_type == "INTERNAL TRANSFER - SELF"`) in the same trailing-3m window
Signal D covered — a second, independent correction to
`casa_inflow_excl_disb_amt_3m_recent`. **Removed entirely by RL-A1-21** —
Signal D itself is gone, so this correction has nothing left to correct.

RL-A1-20 (CASA(CA+SA)/all-accounts EOD balance signals): Node 2r now pulls 12
balance columns from enrich_casa_eod_avg_balance (3 scope prefixes — ca
current-account-only, casa CA+SA, all CASA+investments+FDs — x 2 windows x
plain/_max), up from the 2 CA-only columns RL-A1-9 shipped. Every
balance-vs-EMI comparison (High Arm 1/4, the shared casa_low helper,
no_casa_flag_recent) is re-pointed to the casa (CA+SA) variant, which becomes
the primary gating balance; ca and all variants (plus every _max variant)
ship as diagnostic/passthrough columns only, wired into no gate.

RL-A1-19 (timing-anchored salary arms, replacing high_arm3/high_arm3b/
high_arm7): the user rejected comparing a bureau-reported salary amount
against monthly_emi_recent (old Arm 7) and the plain alert-only Arm 3/3b as
not meaningful affordability checks when the underlying bureau pull can be
dated anywhere in the past. Node 2 now also calls
enrichers.enrich_salary_stop_month (new function, mirrors
enrich_salary_months_h4_h6's [obs-6m, obs-3m) window with F.max instead of a
count) to carry salary_stop_month_recent — the actual calendar month payroll
last showed payroll_flag=1. `_aecb_recent_salary_arm` and the old
high_arm7/high_arm3b definitions are removed; replaced by a reworked
high_arm3 (salary stopped AND a bureau new-salary signal whose pull-dated leg
falls within _RL_TAU_SALARY_STOP_PULL_LEAD_MONTHS before salary_stop_month)
and a new high_arm3c (salary never present in the 6m lookback AND the same
bureau new-salary signal, pull-dated leg within
_RL_TAU_NEW_SALARY_PULL_RECENCY_MONTHS of observation_date). Both arms are
amount-agnostic. `bureau_new_salary_signal_*` is an OR of an alert-based leg
(already recency-anchored to observation_date inside its own enricher — no
extra date gate) and a pull-dated leg (shares aecb_bureau_pull_date_recent
with feature_retail_loans — carries its own per-arm date gate). moderate_arm2/
low_tier2 are unaffected — they gate on plain aecb_is_recent, never
_aecb_recent_salary_arm.

RL-A1-23 (High Arm 6b, external loan payments): Node 2r now also calls
`enrichers.enrich_ext_loan_payments_h2` on `wm_fea_external_loan_payments`
(weekly PIT-joinable, no R2 look-ahead flag, confirmed Leg B) to carry
`ext_loan_payment_amt_h2_recent`/`_cnt_h2_recent` — "servicing another bank's
loan from this account" is the same evidentiary logic as the existing
`high_arm6` ("servicing another bank's credit card"), additive sibling arm,
`high_arm6` itself untouched.

RL-A1-21 (Signal D removal): Signal D (`casa_inflow_excl_disb_amt_3m`, a raw
sum of generic CASA credit transactions) and every dependent are removed
entirely — `enrich_casa_inflow_h2`/`enrich_casa_inflow_h4_h6`/
`enrich_casa_self_transfer_wash_h2` are no longer called from Node 2,
`months_runway` is gone, `high_arm5`/`moderate_arm3`/`low_cond2` are dropped
with no replacement, `low_cond1`'s trailing income clause is narrowed (not
replaced), `no_casa_flag_recent` is redefined on balance-nullness alone (its
`casa_inflow_cnt_h2_recent` clause is gone), and `a1_income_source`'s
`"casa_generic"` branch is removed. Per an explicit user ruling (2026-10-07):
no reliable PIT-joinable income source currently exists —
`wm_fea_income_from_sources` (RL-A1-22's planned replacement) is confirmed to
have no row-level history (see RESULTS_RL.md's 2026-10-07
RL-A1-22-REJECTED entry); a schema intelligence pipeline is being run on WM
feature datasets to find future candidates, but nothing is available now.
`enrich_casa_inflow_h2` itself is NOT deleted from `cc_a1_ability/enrichers.py`
— it is still used by the CC pipeline (R18) — only RL's call site to it is
removed.
"""

# pylint: disable=too-many-lines,too-many-locals,too-many-statements

import datetime
import logging

from dateutil.relativedelta import relativedelta

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.pipelines.crx_persona.cc_a1_ability import enrichers
from enbd_collections.pipelines.crx_persona.cc_a1_ability.nodes import (
    _TAU_SALARY_H2_MIN,
)

LOG = logging.getLogger(__name__)

# ── RL-A1-9 threshold constants (`_RL_TAU_*` prefix) ──────────────────────────
# Fires on count > 1 (repeated default) — RL-A1-8 chk8 live distribution
# (n=1,577, p10=5.0, p50=35.0) confirms real non-null values sit far from the
# 0/1 boundary, so the doc's placeholder is safe to keep as-is (no retuning).
_RL_TAU_AECB_DEFAULT_RECIDIVISM = 1

# RL-A1-17: genuine AECB recency cutoff, replacing the "any pull ever" framing.
# User-confirmed value (RL-A1-16 Leg B chk7 recency-sensitivity table).
_RL_TAU_AECB_RECENCY_MONTHS = 6

# RL-A1-19: timing-anchored salary-arm thresholds (replace high_arm3/3b/7's
# amount-vs-EMI framing with a pull-date-vs-salary-timing framing). User's
# starting values, PROD-confirmed sane by trl_a1_19_salary_timing_probe.py
# (Arm 3 fires 2.86%/691 rows, Arm 3c fires 3.04%/734 rows, mutually
# exclusive) — see RESULTS_RL.md 2026-10-07.
_RL_TAU_SALARY_STOP_PULL_LEAD_MONTHS = 2
_RL_TAU_NEW_SALARY_PULL_RECENCY_MONTHS = 3

# RL-A1-20: the 12 CASA(CA+SA)/CA-only/all-accounts EOD balance columns
# enrich_casa_eod_avg_balance now emits (bare names, before the generic
# {col}_recent rename loop in _assemble_rl_classify_inputs). Shared between
# the NULL-fallback branch and the final output select below.
_CASA_EOD_BAL_OUTPUT_COLS = (
    "casa_eod_spot_ca",
    "casa_eod_spot_ca_max",
    "casa_eod_avg_3m_ca",
    "casa_eod_avg_3m_ca_max",
    "casa_eod_spot_casa",
    "casa_eod_spot_casa_max",
    "casa_eod_avg_3m_casa",
    "casa_eod_avg_3m_casa_max",
    "casa_eod_spot_all",
    "casa_eod_spot_all_max",
    "casa_eod_avg_3m_all",
    "casa_eod_avg_3m_all_max",
)


# ── Node 2: build_rl_a1_group_b_income ─────────────────────────────────────────


def build_rl_a1_group_b_income(
    cif_enriched: DataFrame,
    feat_payroll: DataFrame,
    feat_casa_bal: DataFrame,
    wm_salary: DataFrame,
    wm_labelled_transactions: DataFrame,
    beneficiary_cards: DataFrame,
    wm_casa_avg_bal: DataFrame,
    wm_ext_loan_payments: DataFrame,
    *,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame:
    """WM / retail.feature_space income signals at CIF grain (Node 2).

    Calls CC enrichers directly (R14 reuse). Default grain is T0-anchored
    (account_id, spell_id). Pass anchor_col="observation_date" and
    grain_key=("account_id", "observation_date") for the obs-date delegate
    (Node 2r, build_rl_a1_group_b_income_recent).

    Enrichers called:
        1. enrich_salary_months_h2      → salary_months_h2
        2. enrich_casa_eod_bal_h2       → casa_eod_bal_h2
        3. enrich_salary_pit            → salary_amt_last, salary_change_pct
        4. enrich_ext_cc_payments_h2    → ext_cc_payment_amt_h2, ext_cc_payment_cnt_h2
        5. enrich_salary_months_h4_h6   → salary_months_h4_h6  (RL-A1-9 Signal A)
        6. enrich_casa_eod_avg_balance  → 12 CASA(CA+SA)/CA-only/all-accounts
                                          EOD balance columns (RL-A1-9/20
                                          Signal B; casa is the primary
                                          balance-vs-EMI gate, ca/all/_max
                                          are diagnostic-only)
        7. enrich_salary_stop_month     → salary_stop_month
                                          (RL-A1-19, timing-anchored high_arm3)
        8. enrich_ext_loan_payments_h2  → ext_loan_payment_amt_h2,
                                          ext_loan_payment_cnt_h2
                                          (RL-A1-23, High Arm 6b — external-
                                          bank loan servicing, same evidentiary
                                          logic as Arm 6's external-CC check)

    RL-A1-21 (Signal D removal): Signal D (`casa_inflow_excl_disb_amt_3m`, a
    raw sum of generic CASA credit transactions) and every dependent are
    removed entirely — `enrich_casa_inflow_h2`/`enrich_casa_inflow_h4_h6`/
    `enrich_casa_self_transfer_wash_h2` are no longer called here,
    `months_runway` is gone, and no replacement income-corroboration signal
    is wired in its place. Per an explicit user ruling (2026-10-07): no
    reliable PIT-joinable income source currently exists —
    `wm_fea_income_from_sources` (RL-A1-22's planned replacement) is
    confirmed to have no row-level history (see RESULTS_RL.md's 2026-10-07
    RL-A1-22-REJECTED entry); a schema intelligence pipeline is being run on
    WM feature datasets to find future candidates, but nothing is available
    now. `high_arm5`, `moderate_arm3`, and `low_cond2` are dropped entirely
    with no replacement; `low_cond1`'s trailing income clause is narrowed
    (not replaced). See `_build_rl_ability_conditions` below.

    Args:
        cif_enriched:             crx_rl_a1_base (carries cif_id).
        feat_payroll:             feat_payroll_indicator.
        feat_casa_bal:            feat_casa_eod_balance.
        wm_salary:                wm_fea_salary_days_since_increment.
        wm_labelled_transactions: wm_pri_labelled_transactions.
        beneficiary_cards:        raw_beneficiary_cards.
        wm_casa_avg_bal:          wm_fea_casa_eod_avg_balance.
        wm_ext_loan_payments:     wm_fea_external_loan_payments (RL-A1-23).
        anchor_col:               date column used as enricher anchor; default "t0".
        grain_key:                output grain tuple; default (account_id, spell_id).

    Returns:
        DataFrame at grain_key grain with 22 income columns.
    """
    # Dedup to grain to prevent NxM explosion
    cif_spell = cif_enriched.dropDuplicates(list(grain_key))

    salary_h2 = enrichers.enrich_salary_months_h2(
        cif_spell, feat_payroll, anchor_col, grain_key
    )
    casa_h2 = enrichers.enrich_casa_eod_bal_h2(
        cif_spell, feat_casa_bal, anchor_col, grain_key
    )
    sal_pit = enrichers.enrich_salary_pit(cif_spell, wm_salary, anchor_col, grain_key)
    obt_h2 = enrichers.enrich_ext_cc_payments_h2(
        cif_spell, wm_labelled_transactions, beneficiary_cards, anchor_col, grain_key
    )
    salary_h4_h6 = enrichers.enrich_salary_months_h4_h6(
        cif_spell, feat_payroll, anchor_col, grain_key
    )
    casa_avg_bal = enrichers.enrich_casa_eod_avg_balance(
        cif_spell, wm_casa_avg_bal, anchor_col, grain_key
    )
    salary_stop_month = enrichers.enrich_salary_stop_month(
        cif_spell, feat_payroll, anchor_col, grain_key
    )
    ext_loan_h2 = enrichers.enrich_ext_loan_payments_h2(
        cif_spell, wm_ext_loan_payments, anchor_col, grain_key
    )

    result = enrichers.join_required_signals(
        cif_spell.select(*grain_key),
        grain_key,
        [
            enrichers.RequiredJoin("enrich_salary_months_h2", salary_h2),
            enrichers.RequiredJoin("enrich_casa_eod_bal_h2", casa_h2),
            enrichers.RequiredJoin("enrich_salary_pit", sal_pit),
            enrichers.RequiredJoin("enrich_ext_cc_payments_h2", obt_h2),
            enrichers.RequiredJoin("enrich_salary_months_h4_h6", salary_h4_h6),
            enrichers.RequiredJoin("enrich_casa_eod_avg_balance", casa_avg_bal),
            enrichers.RequiredJoin("enrich_salary_stop_month", salary_stop_month),
            enrichers.RequiredJoin("enrich_ext_loan_payments_h2", ext_loan_h2),
        ],
    )

    return result.select(
        *grain_key,
        F.col("salary_months_h2").cast("int"),
        F.col("casa_eod_bal_h2").cast("double"),
        F.col("salary_amt_last").cast("double"),
        F.col("salary_change_pct").cast("double"),
        F.col("ext_cc_payment_amt_h2").cast("double"),
        F.col("ext_cc_payment_cnt_h2").cast("int"),
        F.col("salary_months_h4_h6").cast("int"),
        *[F.col(c).cast("double") for c in _CASA_EOD_BAL_OUTPUT_COLS],
        F.col("salary_stop_month").cast("date"),
        F.col("ext_loan_payment_amt_h2").cast("double"),
        F.col("ext_loan_payment_cnt_h2").cast("double"),
    )


# ── Node 2r: build_rl_a1_group_b_income_recent ─────────────────────────────────


def build_rl_a1_group_b_income_recent(
    cif_enriched: DataFrame,
    feat_payroll: DataFrame,
    feat_casa_bal: DataFrame,
    wm_salary: DataFrame,
    wm_labelled_transactions: DataFrame,
    beneficiary_cards: DataFrame,
    wm_casa_avg_bal: DataFrame,
    wm_ext_loan_payments: DataFrame,
    crx_persona: dict,
) -> DataFrame:
    """Obs-date-anchored income signals (Node 2r). Delegate of Node 2.

    Calls build_rl_a1_group_b_income with anchor_col="observation_date" so
    the H2 window is [observation_date-3m, observation_date) rather than
    [t0-3m, t0). Grain is (account_id, observation_date).

    wm_pri_labelled_transactions is partitioned by week_number (one week per partition),
    so filter by tran_date >= persona_start_date to avoid a full-history scan.
    feat_payroll_indicator is a full-history snapshot within its partition; apply a
    row-level month_number floor to avoid shipping years of payroll history.
    wm_fea_casa_eod_avg_balance (RL-A1-9 Signal B) is unpinned on adv_load_date
    (no catalog leaf pin) — no raw-source filter needed here.
    wm_fea_external_loan_payments (RL-A1-23) is a weekly PIT-joinable series
    (week_number is the real per-row date, confirmed Leg B — see
    enrich_ext_loan_payments_h2) — no raw-source filter needed here, same
    treatment as wm_fea_casa_eod_avg_balance.

    Args:
        crx_persona: Persona param dict with persona_start_date.
    """
    persona_start = crx_persona["persona_start_date"]
    wm_labelled_transactions = wm_labelled_transactions.filter(
        F.col("tran_date") >= F.lit(persona_start)
    )
    payroll_floor_int = int(
        (datetime.date.fromisoformat(persona_start) - relativedelta(months=12))
        .isoformat()
        .replace("-", "")
    )
    feat_payroll = feat_payroll.filter(F.col("month_number") >= payroll_floor_int)
    # raw_beneficiary_cards is a live snapshot (no partition column)
    return build_rl_a1_group_b_income(
        cif_enriched,
        feat_payroll,
        feat_casa_bal,
        wm_salary,
        wm_labelled_transactions,
        beneficiary_cards,
        wm_casa_avg_bal,
        wm_ext_loan_payments,
        anchor_col="observation_date",
        grain_key=("account_id", "observation_date"),
    )


# ── Node 3: build_rl_a1_group_b_bureau ─────────────────────────────────────────


def build_rl_a1_group_b_bureau(
    cif_enriched: DataFrame,
    wm_recurring: DataFrame,
    stg_salary_hist: DataFrame,
    prm_bureau_alert: DataFrame,
    prm_bureau_cif_bridge: DataFrame,
    fea_aecb_alerts: DataFrame,
    *,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame:
    """AECB bureau + WM recurring inflow signals at CIF grain (Node 3).

    Calls CC enrichers directly (R14 reuse). Default grain is T0-anchored
    (account_id, spell_id). Pass anchor_col="observation_date" and
    grain_key=("account_id", "observation_date") for the obs-date delegate
    (Node 3r, build_rl_a1_group_b_bureau_recent).

    Enrichers called:
        1. enrich_recurring_inflow_h2  → recurring_inflow_amt_h2, recurring_inflow_cnt_h2
        2. enrich_bureau_salary        → bureau_salary_present_6m_flag, bureau_salary_amt_last
        3. enrich_bureau_alerts        → a1_new_salary_acct_flag, a1_offus_paying_flag
        4. enrich_fea_bureau_alerts    → fea_salary_acct_flag (combined into a1_new_salary_acct_flag)

    NULL-safe OR for a1_new_salary_acct_flag (verbatim from CC Node 4).

    Args:
        cif_enriched:          crx_rl_a1_base (carries cif_id).
        wm_recurring:          wm_fea_casa_weekly_repeated_inflow.
        stg_salary_hist:       stg_aecb_salary_history.
        prm_bureau_alert:      prm_bureau_alert_enriched.
        prm_bureau_cif_bridge: prm_bureau_cif_bridge.
        fea_aecb_alerts:       fea_monthly_aecb_alerts.
        anchor_col:            date column used as enricher anchor; default "t0".
        grain_key:             output grain tuple; default (account_id, spell_id).

    Returns:
        DataFrame at grain_key grain with 6 bureau columns.
    """
    cif_spell = cif_enriched.dropDuplicates(list(grain_key))

    rec_h2 = enrichers.enrich_recurring_inflow_h2(
        cif_spell, wm_recurring, anchor_col, grain_key
    )
    bur_sal = enrichers.enrich_bureau_salary(
        cif_spell, stg_salary_hist, prm_bureau_cif_bridge, anchor_col, grain_key
    )
    bur_alerts = enrichers.enrich_bureau_alerts(
        cif_spell, prm_bureau_alert, anchor_col, grain_key
    )
    fea_alerts = enrichers.enrich_fea_bureau_alerts(
        cif_spell, fea_aecb_alerts, anchor_col, grain_key
    )
    if fea_alerts is not None:
        fea_alerts = fea_alerts.withColumnRenamed(
            "fea_salary_acct_flag", "_fea_salary_acct_flag"
        )

    result = enrichers.join_required_signals(
        cif_spell.select(*grain_key),
        grain_key,
        [
            enrichers.RequiredJoin("enrich_recurring_inflow_h2", rec_h2),
            enrichers.RequiredJoin("enrich_bureau_salary", bur_sal),
            enrichers.RequiredJoin("enrich_bureau_alerts", bur_alerts),
            enrichers.RequiredJoin("enrich_fea_bureau_alerts", fea_alerts),
        ],
    )

    # NULL-safe OR (verbatim from CC Node 4)
    result = result.withColumn(
        "a1_new_salary_acct_flag",
        F.when(
            (F.coalesce(F.col("a1_new_salary_acct_flag"), F.lit(0)) == 1)
            | (F.coalesce(F.col("_fea_salary_acct_flag"), F.lit(0)) == 1),
            F.lit(1),
        )
        .when(
            F.col("a1_new_salary_acct_flag").isNull()
            & F.col("_fea_salary_acct_flag").isNull(),
            F.lit(None).cast("int"),
        )
        .otherwise(F.lit(0)),
    ).drop("_fea_salary_acct_flag")

    return result.select(
        *grain_key,
        F.col("recurring_inflow_amt_h2").cast("double"),
        F.col("recurring_inflow_cnt_h2").cast("int"),
        F.col("bureau_salary_present_6m_flag").cast("int"),
        F.col("bureau_salary_amt_last").cast("double"),
        F.col("a1_new_salary_acct_flag").cast("int"),
        F.col("a1_offus_paying_flag").cast("int"),
    )


# ── Node 3r: build_rl_a1_group_b_bureau_recent ─────────────────────────────────


#: feature_retail_loans → crx_rl_a1_group_b_bureau_recent AECB column schema
#: (RL-A1-9). Only the 7 columns the 4 decided-KEEP arms need (R18/task-card
#: "no reporting-only columns" rule) — excludes the Signal-B-dependent arms'
#: unique inputs (aecb_unique_income_records, aecb_total_products_dpd90_6m,
#: aecb_direct_debit_returns_6m, aecb_bank_outstanding_to_loan_pct,
#: bank_ever_90dpd_flag — RL-A1-14) and diagnostic-only columns
#: (aecb_cc_enquiries_30d, aecb_total_outstanding_balance).
_RL_A1_9_AECB_SCHEMA = {
    "aecb_bureau_pull_date": "date",
    "aecb_last_salary_credit_amount": "double",
    "aecb_salary_bank_product_count": "int",
    "aecb_income_record_changes_30d": "int",
    "aecb_total_active_cc_contracts": "long",
    "bank_worst_delinquency_6m_encoded": "int",
    "aecb_bank_times_in_default_90d": "long",
}


def build_rl_a1_group_b_bureau_recent(
    cif_enriched: DataFrame,
    wm_recurring: DataFrame,
    stg_salary_hist: DataFrame,
    prm_bureau_alert: DataFrame,
    prm_bureau_cif_bridge: DataFrame,
    fea_aecb_alerts: DataFrame,
    feature_retail_loans: DataFrame,
    crx_persona: dict,
) -> DataFrame:
    """Obs-date-anchored bureau + recurring signals (Node 3r). Delegate of Node 3.

    Calls build_rl_a1_group_b_bureau with anchor_col="observation_date" so the
    bureau and recurring-inflow windows are anchored to observation_date rather
    than t0. Grain is (account_id, observation_date).

    WM inputs are pre-filtered to a single partition via the catalog
    (snapshot_adv_load_date global). Way4/AECB staging tables are range-filtered
    by edp_load_date to avoid full-history scans.

    RL-A1-9: left-joins feature_retail_loans directly on
    (account_id, observation_date) — already the grain feature_retail_loans
    is built at (feat_loan_application_risk's own PIT join: freshest
    bureau_pull_date <= observation_date), so no CIF bridge or additional
    PIT logic is needed here; see feat_loan_application_risk.py's module
    docstring for the forward-fill mechanics (PIT correctness for the rare
    multi-pull account, not frequent refresh).

    Schema guard: any missing AECB column raises RuntimeError — schema
    drift on this source is a defect to surface at build time, not degrade
    through silently.

    Args:
        feature_retail_loans: Retail-loan feature table at
            (account_id, observation_date) grain carrying the AECB columns.
        crx_persona: Persona param dict with persona_start_date.
    """
    bureau_floor = (
        datetime.date.fromisoformat(crx_persona["persona_start_date"])
        - relativedelta(months=12)
    ).isoformat()
    stg_salary_hist = stg_salary_hist.filter(
        F.col("edp_load_date") >= F.lit(bureau_floor)
    )
    prm_bureau_alert = prm_bureau_alert.filter(
        F.col("edp_load_date") >= F.lit(bureau_floor)
    )
    prm_bureau_cif_bridge = prm_bureau_cif_bridge.filter(
        F.col("edp_load_date") >= F.lit(bureau_floor)
    )
    # fea_monthly_aecb_alerts pre-filtered via catalog (snapshot_adv_load_date)
    result = build_rl_a1_group_b_bureau(
        cif_enriched,
        wm_recurring,
        stg_salary_hist,
        prm_bureau_alert,
        prm_bureau_cif_bridge,
        fea_aecb_alerts,
        anchor_col="observation_date",
        grain_key=("account_id", "observation_date"),
    )

    missing = [c for c in _RL_A1_9_AECB_SCHEMA if c not in feature_retail_loans.columns]
    if missing:
        raise RuntimeError(
            "build_rl_a1_group_b_bureau_recent: feature_retail_loans missing "
            f"{missing} — required source columns are missing. Fix the "
            "source or the schema; do not silently null the signal."
        )

    aecb = feature_retail_loans.select(
        "account_id",
        "observation_date",
        *[F.col(c).cast(dtype).alias(c) for c, dtype in _RL_A1_9_AECB_SCHEMA.items()],
    )
    result = result.join(aecb, on=["account_id", "observation_date"], how="left")

    return result


# ── Node 4r: build_rl_a1_group_c_recent ────────────────────────────────────────


def build_rl_a1_group_c_recent(
    base: DataFrame,
    int_loan_master: DataFrame,
    crx_persona: dict,
) -> DataFrame:
    """Obs-date-anchored EMI coverage window + monthly EMI (Node 4r).

    PIT window: [observation_date - 3m, observation_date]. Averages
    emi_coverage_ratio from int_loan_master over the 3 months
    immediately before each observation_date.

    monthly_emi_recent (RL-A1-9 Signal C): PIT installment_due_amount at the
    latest loan row in the same window, falling back to overdue_total when
    installment_due_amount is NULL — the EMI-relative threshold used
    throughout the redesigned ability_* waterfall.

    RL-A1-21: disbursement_amount_recent/disbursement_date_recent (RL-A1-17)
    are removed — they fed only Signal D's disbursement-exclusion
    correction, which no longer exists (see _build_rl_ability_conditions).

    Schema guard: if any of account_id, observation_date, emi_coverage_ratio,
    installment_due_amount, overdue_total are absent from int_loan_master,
    raises RuntimeError — schema drift on this source is a defect to surface
    at build time, not degrade through silently.

    Applies a 3-month partition floor on int_loan_master (persona_start_date - 3m)
    to avoid scanning the full loan history.

    Args:
        base:            crx_rl_a1_base — (account_id, observation_date, spell_id).
        int_loan_master: Trusted intermediate loan layer. Required: account_id,
                         observation_date, emi_coverage_ratio,
                         installment_due_amount, overdue_total.
        crx_persona:     Persona param dict with persona_start_date.

    Returns:
        DataFrame at (account_id, observation_date, spell_id) grain:
            account_id                string
            observation_date          date
            spell_id                  int
            emi_coverage_mean_recent  double  (NULL ~where feature absent)
            monthly_emi_recent        double  (NULL ~where feature absent)
    """
    c_floor = (
        datetime.date.fromisoformat(crx_persona["persona_start_date"])
        - relativedelta(months=3)
    ).isoformat()
    int_loan_master = int_loan_master.filter(
        F.col("observation_date") >= F.lit(c_floor)
    )

    obs_dates = base.select("account_id", "observation_date", "spell_id").distinct()

    _required = [
        "account_id",
        "observation_date",
        "emi_coverage_ratio",
        "installment_due_amount",
        "overdue_total",
    ]
    missing = [c for c in _required if c not in int_loan_master.columns]
    if missing:
        raise RuntimeError(
            f"build_rl_a1_group_c_recent: int_loan_master missing {missing}"
            " — required source columns are missing. Fix the source or the"
            " schema; do not silently null the signal."
        )

    loans_windowed = (
        int_loan_master.select(
            F.col("account_id").cast("string"),
            F.col("observation_date").cast("date").alias("_loan_obs_date"),
            F.col("emi_coverage_ratio").cast("double"),
            F.col("installment_due_amount").cast("double"),
            F.col("overdue_total").cast("double"),
        )
        .join(obs_dates, on="account_id", how="inner")
        .filter(
            (F.col("_loan_obs_date") <= F.col("observation_date"))
            & (F.col("_loan_obs_date") >= F.add_months(F.col("observation_date"), -3))
        )
    )

    emi_recent = loans_windowed.groupBy(
        "account_id", "observation_date", "spell_id"
    ).agg(F.mean("emi_coverage_ratio").alias("emi_coverage_mean_recent"))

    result = obs_dates.join(
        emi_recent, on=["account_id", "observation_date", "spell_id"], how="left"
    )

    w_pit = Window.partitionBy("account_id", "observation_date", "spell_id").orderBy(
        F.col("_loan_obs_date").desc()
    )
    pit_recent = (
        loans_windowed.withColumn("_rn", F.row_number().over(w_pit))
        .filter(F.col("_rn") == 1)
        .select(
            "account_id",
            "observation_date",
            "spell_id",
            F.coalesce(F.col("installment_due_amount"), F.col("overdue_total")).alias(
                "monthly_emi_recent"
            ),
        )
    )
    result = result.join(
        pit_recent, on=["account_id", "observation_date", "spell_id"], how="left"
    )

    total = result.count()
    covered = result.filter(F.col("emi_coverage_mean_recent").isNotNull()).count()
    covered_emi = result.filter(F.col("monthly_emi_recent").isNotNull()).count()
    LOG.info(
        "build_rl_a1_group_c_recent: %d rows | emi_coverage_mean_recent coverage %.1f%%"
        " | monthly_emi_recent coverage %.1f%%",
        total,
        100.0 * covered / max(total, 1),
        100.0 * covered_emi / max(total, 1),
    )

    return result.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("spell_id").cast("int"),
        F.col("emi_coverage_mean_recent").cast("double"),
        F.col("monthly_emi_recent").cast("double"),
    )


# ── Node 4b: build_rl_a1_group_d_origination ───────────────────────────────────

#: Source → output column rename map for Group D origination signals.
_GROUP_D_RENAME = {
    "aecb_score_at_orig": "aecb_score_at_origination",
    "aecb_total_outstanding_balance": "aecb_total_outstanding_at_origination",
    "bank_worst_delinquency_encoded": "aecb_bank_worst_dlq_at_origination",
    "bank_worst_delinquency_6m_encoded": "aecb_bank_worst_dlq_6m_at_origination",
    "bank_high_utilization_pct": "aecb_bank_high_util_pct_at_origination",
    "aecb_bank_outstanding_to_loan_pct": "aecb_bank_ob_to_loan_pct_at_origination",
    "credit_card_enquiries_12m": "aecb_cc_enquiries_12m_at_origination",
    "aecb_cc_enquiries_30d": "aecb_cc_enquiries_30d_at_origination",
    "aecb_direct_debit_returns_6m": "aecb_dd_returns_6m_at_origination",
    "aecb_bank_times_in_default_90d": "aecb_bank_times_default_90d_at_origination",
    "aecb_total_products_dpd90_6m": "aecb_tot_contracts_dpd90_6m_at_origination",
    "unauthorized_overdraft_flag": "aecb_has_unauth_od_at_origination",
    "bank_ever_90dpd_flag": "aecb_ever_90dpd_at_origination",
    "employer_validation_encoded": "dms_employer_validation_at_origination",
    "ale_indicator_flag": "dms_ale_indicator_at_origination",
    "first_salary_waiver_flag": "dms_first_sal_waiver_at_origination",
}

#: Output column types for Group D (after rename).
_GROUP_D_SCHEMA = {
    "aecb_score_at_origination": "double",
    "aecb_total_outstanding_at_origination": "double",
    "aecb_bank_worst_dlq_at_origination": "int",
    "aecb_bank_worst_dlq_6m_at_origination": "int",
    "aecb_bank_high_util_pct_at_origination": "double",
    "aecb_bank_ob_to_loan_pct_at_origination": "double",
    "aecb_cc_enquiries_12m_at_origination": "long",
    "aecb_cc_enquiries_30d_at_origination": "long",
    "aecb_dd_returns_6m_at_origination": "double",
    "aecb_bank_times_default_90d_at_origination": "long",
    "aecb_tot_contracts_dpd90_6m_at_origination": "long",
    "aecb_has_unauth_od_at_origination": "int",
    "aecb_ever_90dpd_at_origination": "int",
    "dms_employer_validation_at_origination": "int",
    "dms_ale_indicator_at_origination": "int",
    "dms_first_sal_waiver_at_origination": "int",
}


def build_rl_a1_group_d_origination(
    base: DataFrame,
    feat_loan_application_risk: DataFrame,
) -> DataFrame:
    """Add cross-bank origination bureau signals to the spell spine (Node 4b).

    Consumes feat_loan_application_risk — a pre-built, pre-encoded feature table
    combining AECB bureau pull + DMS underwriting at origination. All encoding is
    already done there; no re-implementation here.

    Join strategy: feat_loan_application_risk is at (account_id, observation_date)
    grain from the retail_loans pipeline. Since the same origination record is
    replicated identically across all observation_dates per account, we deduplicate
    to one row per account_id (taking the latest observation_date for safety) and
    join to the spell spine on account_id alone.

    Schema guard: if any required source column is missing from
    feat_loan_application_risk, raises RuntimeError — schema drift on this
    source is a defect to surface at build time, not degrade through
    silently.

    Not wired into create_pipeline() (orphaned since RL-A1-5) — kept for
    consistency with the fail-loud treatment applied to the other nodes in
    this file.

    Args:
        base:                       crx_rl_a1_base — (account_id, spell_id) grain.
        feat_loan_application_risk: Pre-encoded origination feature table.

    Returns:
        crx_rl_a1_group_d at (account_id, spell_id) grain with 16 _at_origination
        columns (AECB cross-bank bureau + DMS underwriting signals).
    """
    spell_base = base.dropDuplicates(["account_id", "spell_id"])

    missing = [
        c for c in _GROUP_D_RENAME if c not in feat_loan_application_risk.columns
    ]
    if missing:
        raise RuntimeError(
            "build_rl_a1_group_d_origination: feat_loan_application_risk missing "
            f"{missing} — required source columns are missing. Fix the source "
            "or the schema; do not silently null the signal."
        )

    # Deduplicate to one row per account — all rows are identical, take latest for safety
    w = Window.partitionBy("account_id").orderBy(F.col("observation_date").desc())
    feat_deduped = (
        feat_loan_application_risk.select(
            "account_id", "observation_date", *_GROUP_D_RENAME.keys()
        )
        .withColumn("_rn", F.row_number().over(w))
        .filter(F.col("_rn") == 1)
        .drop("_rn", "observation_date")
    )

    # Rename source columns to _at_origination output names
    for src, dst in _GROUP_D_RENAME.items():
        feat_deduped = feat_deduped.withColumnRenamed(src, dst)

    result = spell_base.select("account_id", "spell_id").join(
        feat_deduped, on="account_id", how="left"
    )

    total = result.count()
    covered = result.filter(F.col("aecb_score_at_origination").isNotNull()).count()
    LOG.info(
        "build_rl_a1_group_d_origination: %d rows | aecb_score coverage %.1f%%",
        total,
        100.0 * covered / max(total, 1),
    )

    return result.select(
        F.col("account_id").cast("string"),
        F.col("spell_id").cast("int"),
        *[
            F.col(out_col).cast(dtype).alias(out_col)
            for out_col, dtype in _GROUP_D_SCHEMA.items()
        ],
    )


# ── Node 5 helpers (private) ───────────────────────────────────────────────────


def _assemble_rl_classify_inputs(
    spine: DataFrame,
    departure_signature: DataFrame,
    spell_table: DataFrame,
    group_b_income_recent: DataFrame,
    group_b_bureau_recent: DataFrame,
    group_c_recent: DataFrame,
) -> DataFrame:
    """Join all enrichment inputs onto spine for RL A1 classify (Node 5).

    Inlines the former Node 1 join: pulls eosb_like_flag from
    crx_rl_departure_signature and prior_spell_cnt_12m (renamed →
    prior_spell_cnt_24m) from crx_rl_spell_table directly — these were pure
    passthroughs inside the now-superseded crx_rl_a4_class (removed; see
    rl_a4_spine pipeline for its structural replacement). Only classification
    signals are selected — casa_inflow_stop_gap_d and emi_coverage_mean_h2 are
    A4-axis carry-through and not gates in _build_ability_conditions.

    All subsequent joins are obs-date-anchored (RL-A1-3 cleanup — T0 nodes removed;
    RL-A1-6 cleanup — Group A T0 departure removed).
    Obs-date joins at (account_id, observation_date) grain:
        group_b_income_recent → {col}_recent columns (salary_months_h2_recent, etc.)
        group_b_bureau_recent → {col}_recent columns (bureau_salary_present_6m_flag_recent
        group_c_recent        → emi_coverage_mean_recent

    eosb_post_salary_flag uses bureau_salary_present_6m_flag_recent (obs-date signal).

    RL-A1-21: Signal D (`casa_inflow_excl_disb_amt_3m_recent`) and both of
    its corrections (RL-A1-17's disbursement exclusion, RL-A1-18's GL
    self-transfer wash exclusion) are removed entirely — the column no
    longer exists.
    """
    # Inline Node 1: attach eosb_like_flag (from crx_rl_departure_signature,
    # deduped to spell grain — constant per spell) and prior_spell_cnt_12m
    # (from crx_rl_spell_table, already at spell grain), renamed →
    # prior_spell_cnt_24m. Formerly sourced from crx_rl_a4_class, which was a
    # pure passthrough of both columns — no unique logic lost by reading them
    # directly from their origin tables.
    eosb_sel = departure_signature.select(
        "account_id", "spell_id", F.col("eosb_like_flag").cast("int")
    ).dropDuplicates(["account_id", "spell_id"])
    prior_spell_sel = spell_table.select(
        "account_id",
        "spell_id",
        F.col("prior_spell_cnt_12m").cast("int").alias("prior_spell_cnt_24m"),
    )
    result = spine.join(eosb_sel, on=["account_id", "spell_id"], how="left").join(
        prior_spell_sel, on=["account_id", "spell_id"], how="left"
    )

    # group_b_income_recent: rename data columns to *_recent before joining
    _income_keys = {"account_id", "observation_date"}
    income_recent = group_b_income_recent
    for _col in [c for c in income_recent.columns if c not in _income_keys]:
        income_recent = income_recent.withColumnRenamed(_col, f"{_col}_recent")
    result = result.join(
        income_recent, on=["account_id", "observation_date"], how="left"
    )

    # group_b_bureau_recent: rename data columns to *_recent before joining
    _bureau_keys = {"account_id", "observation_date"}
    bureau_recent = group_b_bureau_recent
    for _col in [c for c in bureau_recent.columns if c not in _bureau_keys]:
        bureau_recent = bureau_recent.withColumnRenamed(_col, f"{_col}_recent")
    result = result.join(
        bureau_recent, on=["account_id", "observation_date"], how="left"
    )

    # group_c_recent: emi_coverage_mean_recent / monthly_emi_recent (RL-A1-9 Signal C)
    result = result.join(
        group_c_recent.select(
            "account_id",
            "observation_date",
            "emi_coverage_mean_recent",
            "monthly_emi_recent",
        ),
        on=["account_id", "observation_date"],
        how="left",
    )

    # eosb_post_salary_flag: obs-date-anchored bureau signal
    result = result.withColumn(
        "eosb_post_salary_flag",
        F.when(
            (F.col("eosb_like_flag") == 1)
            & (F.col("bureau_salary_present_6m_flag_recent") == 1),
            F.lit(1),
        )
        .when(F.col("eosb_like_flag") == 1, F.lit(0))
        .otherwise(F.lit(None).cast("int")),
    )

    # eosb_post_salary_flag_recent: mirrors eosb_post_salary_flag (same signal, obs-date variant)
    result = result.withColumn(
        "eosb_post_salary_flag_recent",
        F.when(
            (F.col("eosb_like_flag") == 1)
            & (F.col("bureau_salary_present_6m_flag_recent") == 1),
            F.lit(1),
        )
        .when(F.col("eosb_like_flag") == 1, F.lit(0))
        .otherwise(F.lit(None).cast("int")),
    )

    # ── RL-A1-9 derived signals (built before the classifier) ──────────────────

    # salary_stopped_flag_recent (v3 §7): payroll present 3-6m back, stopped
    # in the last 3m. Always a definite 0/1 (coalesced inputs — never NULL).
    result = result.withColumn(
        "salary_stopped_flag_recent",
        (
            (F.coalesce(F.col("salary_months_h4_h6_recent"), F.lit(0)) > 0)
            & (F.coalesce(F.col("salary_months_h2_recent"), F.lit(0)) == 0)
        ).cast("int"),
    )

    # no_casa_flag_recent (v3 §7 Signal E): no observable ENBD CASA
    # relationship — all CASA(CA+SA) balance signals NULL (RL-A1-20
    # re-point — was CA-only casa_eod_spot_recent/casa_eod_avg_3m_recent)
    # and casa_eod_bal_h2_recent NULL. RL-A1-21: the casa_inflow_cnt_h2_recent
    # clause is dropped — that column no longer exists (Signal D removal).
    result = result.withColumn(
        "no_casa_flag_recent",
        (
            F.col("casa_eod_spot_casa_recent").isNull()
            & F.col("casa_eod_avg_3m_casa_recent").isNull()
            & F.col("casa_eod_bal_h2_recent").isNull()
        ).cast("int"),
    )

    # aecb_is_recent (RL-A1-17): genuine recency cutoff, replacing the "any
    # pull ever" framing RL-A1-9 shipped with. RL-A1-16 Leg B's chk7 recency-
    # sensitivity table showed "any pull" collapses the overall ability_high
    # rate from 70.9% to 59.2%/60.1%/62.8% under 3m/6m/12m cutoffs — user
    # confirmed 6 months as the cutoff to ship. moderate_arm2/low_tier2 use
    # this base definition unmodified. high_arm3/high_arm3c (RL-A1-19) do not
    # use aecb_is_recent at all — they gate on their own, narrower timing
    # comparisons (pull date vs. salary_stop_month_recent / observation_date)
    # instead of this 6-month cutoff.
    result = result.withColumn(
        "aecb_is_recent",
        (
            F.col("aecb_bureau_pull_date_recent").isNotNull()
            & (
                F.months_between(
                    F.col("observation_date"), F.col("aecb_bureau_pull_date_recent")
                )
                <= _RL_TAU_AECB_RECENCY_MONTHS
            )
        ).cast("int"),
    )

    return result


def _build_rl_ability_conditions() -> dict:
    """Build the RL-A1-9 ability waterfall condition expressions (RL-local).

    Replaces the shared `_build_ability_conditions` import from
    `cc_a1_ability.nodes` entirely (R18 — that function and
    `_apply_ability_classifier_primary` are untouched). Built from
    `ability_redesign_v3.md` Sections 2-5, scoped per RESULTS_RL.md
    (2026-10-02): the full EMI-relative base waterfall, plus the AECB-anchored
    arms RL-A1-8 decided KEEP (`moderate_arm2`, `low_tier2`) and RL-A1-19's
    timing-anchored salary arm (`high_arm3c`, replacing `high_arm7`/
    `high_arm3b`).

    Explicitly NOT built here (separate follow-up task — TASKS_RL.md Track E
    RL-A1-14, see this module's docstring):
        moderate_arm4a, moderate_arm4b (Signal-B-dependent, RL-A1-8 undecided)
        low_tier1                      (Signal-B-dependent, RL-A1-8 undecided)

    monthly_emi_recent is coalesced to a large sentinel in every comparison so
    a NULL EMI makes the comparison False, not NULL (v3 §2 note) — otherwise
    a missing EMI would silently drop a row out of every EMI-gated arm.

    aecb_is_recent (RL-A1-17) is a genuine 6-month recency cutoff on
    aecb_bureau_pull_date_recent (see _assemble_rl_classify_inputs), replacing
    RL-A1-9's "any pull ever" framing. moderate_arm2/low_tier2 gate on this
    plain cutoff, unmodified. high_arm3/high_arm3c (RL-A1-19) use their own,
    narrower timing comparisons instead (pull date vs. salary_stop_month_recent
    / observation_date) — see below.

    Returns:
        Dict of Spark Column expressions keyed by state name
        (cond_high / cond_low / cond_moderate).
    """
    _emi = F.coalesce(F.col("monthly_emi_recent"), F.lit(1.0e18))
    _aecb_recent = F.col("aecb_is_recent") == 1
    _pull_date = F.col("aecb_bureau_pull_date_recent")

    # ── RL-A1-19: timing-anchored salary-arm bureau signal ─────────────────────
    # Replaces RL-A1-17's _aecb_recent_salary_arm (amount-vs-EMI framing,
    # high_arm7/high_arm3b) — a stale bureau pull showing a large historical
    # salary says nothing about ability to pay today. bureau_new_salary_signal
    # is an OR of two sub-signals that do NOT share a pull date (2026-10-06
    # correction, RESULTS_RL.md "Proposed amendments" — AND'ing the whole OR
    # against aecb_bureau_pull_date_recent produced a near-zero fire rate by
    # stacking two independent, uncorrelated date constraints):
    #   - alert-based leg: already recency-anchored to observation_date
    #     inside its own enricher (enrich_bureau_alerts' 90d window /
    #     enrich_fea_bureau_alerts' latest-month-before PIT join) — fires on
    #     its own, no additional date gate here.
    #   - pull-dated leg: genuinely shares aecb_bureau_pull_date_recent with
    #     the same feature_retail_loans row — keeps its own per-arm date gate.
    _bureau_new_salary_signal_alert_based = (
        F.coalesce(F.col("a1_new_salary_acct_flag_recent"), F.lit(0)) == 1
    )
    _bureau_new_salary_signal_pull_dated = (
        F.coalesce(F.col("aecb_income_record_changes_30d_recent"), F.lit(0)) > 0
    ) | (F.coalesce(F.col("aecb_salary_bank_product_count_recent"), F.lit(0)) >= 1)

    # casa_low (v3 §3): single reusable expression — gates Low Cond 1/2 and
    # Moderate Arm 3 (Arm 4a/4b, which also use it, are out of scope).
    # RL-A1-20: re-pointed to CASA(CA+SA) — was CA-only casa_eod_avg_3m_recent.
    casa_low = F.col("casa_eod_avg_3m_casa_recent").isNull() | (
        F.col("casa_eod_avg_3m_casa_recent") < _emi
    )

    # ── ability_high: Arms 1-6 (Arm 3 now timing-anchored, RL-A1-19) + Arm 3c
    # (AECB-only, RL-A1-19, replaces high_arm7/high_arm3b) + Arm 6b
    # (external loan payments, RL-A1-23) (v3 §2) ──────────────────────────────
    # RL-A1-20: High Arm 1 re-pointed to CASA(CA+SA) spot — was CA-only
    # casa_eod_spot_recent.
    high_arm1 = F.col("casa_eod_spot_casa_recent").isNotNull() & (
        F.col("casa_eod_spot_casa_recent") >= _emi
    )
    high_arm2 = (
        F.coalesce(F.col("salary_months_h2_recent"), F.lit(0)) >= _TAU_SALARY_H2_MIN
    ) & (F.col("salary_stopped_flag_recent") == 0)
    # Arm 3 (RL-A1-19, timing-anchored, replaces the plain alert-only check):
    # salary stopped AND a bureau new-salary signal whose pull-dated leg (if
    # that's the leg firing) falls at/within _RL_TAU_SALARY_STOP_PULL_LEAD_MONTHS
    # before the month salary stopped — the alert-based leg needs no extra gate.
    _high_arm3_pull_dated_leg = (
        _bureau_new_salary_signal_pull_dated
        & _pull_date.isNotNull()
        & F.col("salary_stop_month_recent").isNotNull()
        & (
            _pull_date
            >= F.add_months(
                F.col("salary_stop_month_recent"),
                -_RL_TAU_SALARY_STOP_PULL_LEAD_MONTHS,
            )
        )
        & (_pull_date <= F.col("salary_stop_month_recent"))
    )
    high_arm3 = (F.col("salary_stopped_flag_recent") == 1) & (
        _bureau_new_salary_signal_alert_based | _high_arm3_pull_dated_leg
    )
    # RL-A1-20: High Arm 4 re-pointed to CASA(CA+SA) 3m avg — was CA-only
    # casa_eod_avg_3m_recent.
    high_arm4 = F.col("casa_eod_avg_3m_casa_recent").isNotNull() & (
        F.col("casa_eod_avg_3m_casa_recent") >= _emi
    )
    # High Arm 5 (RL-A1-21): removed entirely — it gated on Signal D
    # (casa_inflow_excl_disb_amt_3m_recent), which no longer exists. No
    # replacement income-corroboration arm is wired in its place (see
    # module docstring).
    high_arm6 = F.col("ext_cc_payment_amt_h2_recent").isNotNull() & (
        F.col("ext_cc_payment_amt_h2_recent") >= _emi
    )
    # Arm 6b (RL-A1-23): servicing another bank's loan from this CASA account —
    # same evidentiary logic as Arm 6's external-CC check, additive sibling.
    high_arm6b = F.col("ext_loan_payment_amt_h2_recent").isNotNull() & (
        F.col("ext_loan_payment_amt_h2_recent") >= _emi
    )
    # Arm 3c (RL-A1-19, timing-anchored, replaces high_arm7/high_arm3b):
    # salary never present in the full 6m lookback AND a bureau new-salary
    # signal whose pull-dated leg (if that's the leg firing) is within
    # _RL_TAU_NEW_SALARY_PULL_RECENCY_MONTHS of observation_date — the fresh
    # 3-month window is independent of the base 6-month aecb_is_recent cutoff
    # (must not reuse it here, per ability_redesign_v3.md §6).
    _high_arm3c_pull_dated_leg = (
        _bureau_new_salary_signal_pull_dated
        & _pull_date.isNotNull()
        & (
            F.months_between(F.col("observation_date"), _pull_date)
            <= _RL_TAU_NEW_SALARY_PULL_RECENCY_MONTHS
        )
    )
    high_arm3c = (
        (F.coalesce(F.col("salary_months_h2_recent"), F.lit(0)) == 0)
        & (F.coalesce(F.col("salary_months_h4_h6_recent"), F.lit(0)) == 0)
        & (_bureau_new_salary_signal_alert_based | _high_arm3c_pull_dated_leg)
    )

    cond_high = (
        high_arm1
        | high_arm2
        | high_arm3
        | high_arm3c
        | high_arm4
        | high_arm6
        | high_arm6b
    )

    # ── ability_low: Conditions 1 & 3 + Tier 2 (v3 §3) ─────────────────────────
    # Tier 1 (Signal-B-dependent) is out of scope this round — see docstring.
    # RL-A1-21: Condition 1's trailing income clause (Signal D) is dropped,
    # narrowing the condition rather than replacing it (no reliable income
    # source currently exists — see module docstring). Condition 2 (RL-A1-15)
    # is removed entirely — its premise, inflow_present_h4_h6_flag, was
    # itself a bottom-up aggregation of the same rejected category.
    low_cond1 = (
        (F.col("salary_stopped_flag_recent") == 1)
        & (F.coalesce(F.col("a1_new_salary_acct_flag_recent"), F.lit(0)) != 1)
        & casa_low
    )
    low_cond3 = (F.col("eosb_like_flag") == 1) & (
        F.coalesce(F.col("eosb_post_salary_flag_recent"), F.lit(0)) != 1
    )
    # Tier 2: repeated cross-bank default is strong enough alone — no buffer
    # (casa_low) check required, unlike Tier 1.
    low_tier2 = _aecb_recent & (
        F.coalesce(F.col("aecb_bank_times_in_default_90d_recent"), F.lit(0))
        > _RL_TAU_AECB_DEFAULT_RECIDIVISM
    )

    cond_low = low_cond1 | low_cond3 | low_tier2

    # ── ability_moderate: Arms 1 & 2 (v3 §4) ───────────────────────────────────
    # Arm 4a/4b (Signal-B-dependent) are out of scope this round — see docstring.
    # RL-A1-21: Arm 3 (Signal D) removed entirely, no replacement.
    moderate_arm1 = (F.col("no_casa_flag_recent") == 1) & (
        F.col("a1_new_salary_acct_flag_recent") == 1
    )
    # Arm 2 resolves v2's "performing CC elsewhere" gap. CAVEAT:
    # bank_worst_delinquency_6m_encoded is an aggregate across ALL
    # bureau-registered trade lines, not CC-specific. "<=1" on the aggregate
    # worst necessarily implies every individual product (incl. any CC) is
    # also <=1 — that direction is sound. It does NOT work the other way: if
    # the aggregate worst is high because of a *different* (non-CC) product,
    # this arm correctly stays silent (false negative, never a false
    # positive) rather than wrongly asserting the CC itself is distressed.
    moderate_arm2 = (
        (F.col("no_casa_flag_recent") == 1)
        & _aecb_recent
        & (F.coalesce(F.col("aecb_total_active_cc_contracts_recent"), F.lit(0)) > 0)
        & (F.col("bank_worst_delinquency_6m_encoded_recent") <= 1)
    )

    cond_moderate = moderate_arm1 | moderate_arm2

    return {
        "cond_high": cond_high,
        "cond_low": cond_low,
        "cond_moderate": cond_moderate,
    }


def _apply_rl_ability_classifier(
    df: DataFrame, conds: dict, state_col: str
) -> DataFrame:
    """Apply the ability_redesign_v3.md waterfall: high -> low -> moderate -> unknown.

    Low gates before moderate (v3 §1) so a stopped-income customer isn't
    accidentally caught by a moderate arm first. ability_unknown is the
    fallthrough — v3 §5 Condition 1 (total signal absence, incl.
    aecb_is_recent == 0) is implied by this ordering: whenever AECB data is
    recent and carries signal, one of the arms above fires first, so by the
    time execution reaches here that's the only case left.
    """
    return df.withColumn(
        state_col,
        F.when(conds["cond_high"], "ability_high")
        .when(conds["cond_low"], "ability_low")
        .when(conds["cond_moderate"], "ability_moderate")
        .otherwise("ability_unknown"),
    )


def _build_rl_a1_output_select(result: DataFrame) -> DataFrame:
    """Apply typed output schema and return final crx_rl_a1_ability DataFrame.

    Schema matches crx_cc_a1_ability core columns for assembly compatibility
    (RL-G1), with _recent columns from obs-date-anchored enrichers (RL-A1-3)
    and RL-specific additions appended at the end.

    recovery_signal is dropped (RL-A1-9): it depended only on the now-removed
    _build_ability_conditions import; v3 §7.4 states this concept is removed
    entirely from the RL classifier with no replacement.
    """
    return result.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("a1_state").cast("string"),
        F.col("a1_provenance").cast("string"),
        F.col("a1_confidence").cast("double"),
        F.col("eosb_like_flag").cast("int").alias("a1_eosb_signal"),
        F.col("eosb_post_salary_flag").cast("int").alias("a1_eosb_post_salary"),
        F.col("a1_income_source").cast("string"),
        # _recent columns: obs-date-anchored (RL-A1-3)
        F.col("salary_months_h2_recent").cast("int"),
        F.col("casa_eod_bal_h2_recent").cast("double"),
        F.col("recurring_inflow_cnt_h2_recent").cast("int"),
        F.col("bureau_salary_present_6m_flag_recent").cast("int"),
        F.col("salary_amt_last_recent").cast("double"),
        F.col("emi_coverage_mean_recent").cast("double"),
        # RL-A1-9 Signals A-E + Signal C EMI threshold
        F.col("salary_months_h4_h6_recent").cast("int"),
        F.col("salary_stopped_flag_recent").cast("int"),
        F.col("no_casa_flag_recent").cast("int"),
        # RL-A1-19: timing-anchor for high_arm3/high_arm3c (gates both arms).
        F.col("salary_stop_month_recent").cast("date"),
        # RL-A1-20: 12 CASA(CA+SA)/CA-only/all-accounts balance columns —
        # casa_eod_spot/avg_3m_recent (CA-only names) replaced by the full
        # ca/casa/all x spot/avg_3m x plain/_max set; casa is the live gate
        # (High Arm 1/4, casa_low), ca/all/_max are diagnostic-only.
        *[F.col(f"{c}_recent").cast("double") for c in _CASA_EOD_BAL_OUTPUT_COLS],
        F.col("monthly_emi_recent").cast("double"),
        # RL-A1-9 AECB columns (4 decided-KEEP arms only)
        F.col("aecb_bureau_pull_date_recent").cast("date"),
        F.col("aecb_is_recent").cast("int"),
        F.col("aecb_last_salary_credit_amount_recent").cast("double"),
        F.col("aecb_salary_bank_product_count_recent").cast("int"),
        F.col("aecb_income_record_changes_30d_recent").cast("int"),
        F.col("aecb_total_active_cc_contracts_recent").cast("long"),
        F.col("bank_worst_delinquency_6m_encoded_recent").cast("int"),
        F.col("aecb_bank_times_in_default_90d_recent").cast("long"),
        F.lit(datetime.date.today().isoformat()).cast("date").alias("computed_at"),
    )


# ── Node 5: build_rl_a1_classify ───────────────────────────────────────────────


def build_rl_a1_classify(
    crx_rl_a4_spine: DataFrame,
    crx_rl_departure_signature: DataFrame,
    crx_rl_spell_table: DataFrame,
    group_b_income_recent: DataFrame,
    group_b_bureau_recent: DataFrame,
    group_c_recent: DataFrame,
) -> DataFrame:
    """Assemble all signals and classify A1 income-ability state for RL (Node 5).

    a1_state uses the RL-A1-9 EMI-relative waterfall (ability_redesign_v3.md
    Sections 2-5): _build_rl_ability_conditions() + _apply_rl_ability_classifier()
    drive the ability_high/low/moderate/unknown state purely from local RL
    functions — the shared cc_a1_ability._build_ability_conditions /
    _apply_ability_classifier_primary import is no longer used (R18).

    a1_provenance: "obs_date" when ≥1 _recent income signal is non-null;
        "no_signal" when all _recent signals are null.

    eosb_post_salary_flag: operable — eosb_like_flag from crx_rl_departure_signature
    + bureau_salary_recent. Group D suspended (RL-A1-5): feat_loan_application_risk
    pull_date unknown. The former Node 1 join (eosb_like_flag, prior_spell_cnt_12m)
    is inlined here (Node 1 eliminated in RL-A1-7 cleanup) and now reads directly
    from crx_rl_departure_signature / crx_rl_spell_table — the superseded
    crx_rl_a4_class was a pure passthrough of both columns (removed; see
    rl_a4_spine pipeline for crx_rl_a4_spine's structural-only replacement).

    Args:
        crx_rl_a4_spine:            Windowed spine (account_id, observation_date,
                                    spell_id, t0).
        crx_rl_departure_signature: Obs-date-grain departure signals — provides
                                    eosb_like_flag (deduped to spell grain).
        crx_rl_spell_table:         Spell-grain T0 anchor — provides
                                    prior_spell_cnt_12m.
        group_b_income_recent: crx_rl_a1_group_b_income_recent — obs-date income.
        group_b_bureau_recent: crx_rl_a1_group_b_bureau_recent — obs-date bureau.
        group_c_recent:        crx_rl_a1_group_c_recent — obs-date EMI coverage.

    Returns:
        crx_rl_a1_ability — A1 axis for every (account_id, observation_date)
        in crx_rl_a4_spine.
    """
    result = _assemble_rl_classify_inputs(
        crx_rl_a4_spine,
        crx_rl_departure_signature,
        crx_rl_spell_table,
        group_b_income_recent,
        group_b_bureau_recent,
        group_c_recent,
    )

    # ── Primary obs-date-anchored state (a1_state) ─────────────────────────────
    # RL-A1-9 waterfall: EMI-relative base arms + 4 decided-KEEP AECB arms.
    # recovery_signal is dropped entirely (depended only on the removed
    # cc_a1_ability import; v3 §7.4 — no replacement, see RESULTS_RL.md).
    conds_rl = _build_rl_ability_conditions()
    result = _apply_rl_ability_classifier(result, conds_rl, state_col="a1_state")

    # Provenance: obs_date when ≥1 _recent income signal populated; no_signal
    # otherwise. RL-A1-21: casa_inflow_cnt_h2_recent dropped from the
    # coalesce — that column no longer exists (Signal D removal).
    result = result.withColumn(
        "a1_provenance",
        F.when(
            F.coalesce(
                F.col("salary_months_h2_recent"),
                F.col("bureau_salary_present_6m_flag_recent"),
            ).isNotNull(),
            F.lit("obs_date"),
        ).otherwise(F.lit("no_signal")),
    ).withColumn(
        "a1_confidence",
        F.when(F.col("a1_state") == "ability_high", F.lit(0.9))
        .when(F.col("a1_state") == "ability_moderate", F.lit(0.7))
        .when(F.col("a1_state") == "ability_low", F.lit(0.4))
        .otherwise(F.lit(0.0)),
    )

    # a1_income_source: obs-date-anchored _recent signals only. RL-A1-21:
    # the "casa_generic" branch (gated on casa_inflow_cnt_h2_recent, Signal D)
    # is removed with no replacement.
    result = result.withColumn(
        "a1_income_source",
        F.when(
            F.coalesce(F.col("salary_months_h2_recent"), F.lit(0))
            >= _TAU_SALARY_H2_MIN,
            F.lit("payroll"),
        )
        .when(
            F.col("bureau_salary_present_6m_flag_recent") == 1, F.lit("bureau_salary")
        )
        .when(
            F.coalesce(F.col("ext_cc_payment_cnt_h2_recent"), F.lit(0)) >= 2,
            F.lit("ext_cc_payment"),
        )
        .otherwise(F.lit(None).cast("string")),
    )

    result = _build_rl_a1_output_select(result)
    enrichers.log_a1_stats(result)
    return result
