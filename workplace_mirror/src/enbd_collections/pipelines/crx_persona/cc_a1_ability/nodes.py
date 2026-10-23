# pylint: disable=R0917,R0801
"""T26 — A1 Ability axis v1 (4-state, multi-signal).

# pylint: disable=too-many-locals, too-many-statements, too-many-branches

Nine-node modular pipeline:
    build_a1_base(cc_spine, crx_cc_spell_table, crx_cc_departure_signature)
        → crx_cc_a1_base                [Node 1]   Group A departure signals

    build_a1_cif_bridge(crx_cc_a1_base, prm_contract, prm_client)
        → crx_cc_a1_cif_enriched        [Node 2]   CIF-resolved rows only

    build_a1_group_b_income(crx_cc_a1_cif_enriched, ...)
        → crx_cc_a1_group_b_income      [Node 3]   T0-anchored income signals (spell-grain)

    build_a1_group_b_bureau(crx_cc_a1_cif_enriched, ...)
        → crx_cc_a1_group_b_bureau      [Node 4]   T0-anchored bureau + recurring (spell-grain)

    build_a1_group_c(crx_cc_a1_base, ...)
        → crx_cc_a1_group_c             [Node 5]   Payment/utilisation/balance (T0 anchor)
                                                   ← Nodes 3, 4, 5 run in parallel

    build_a1_group_b_income_recent(crx_cc_a1_cif_enriched, ...)
        → crx_cc_a1_group_b_income_recent  [Node 3r]  obs-date-anchored income signals

    build_a1_group_b_bureau_recent(crx_cc_a1_cif_enriched, ...)
        → crx_cc_a1_group_b_bureau_recent  [Node 4r]  obs-date-anchored bureau + recurring

    build_a1_group_c_recent(crx_cc_a1_base, prm_balance)
        → crx_cc_a1_group_c_recent      [Node 5r]  obs-date-anchored balance
                                                   ← Nodes 3r, 4r, 5r run in parallel

    build_a1_classify(crx_cc_a1_base, ..., crx_cc_a1_group_c_recent)
        → crx_cc_a1_ability             [Node 6]   ← shipped persona axis
                                                   (a1_state obs-date anchored; no T0 backup)

Goal (personas.md §1): assign each (account_id, observation_date) one of:

    ability_high      — strong, consistent income evidence; not overextended;
                        no pre-existing deterioration.
    ability_moderate  — income weakening or overextended but still earning;
                        OR stopped-but-recoverable (sudden shock, good history);
                        OR stable non-salary recurring income.
    ability_limited   — income stopped/stale AND no savings buffer;
                        OR income present but trajectory already deteriorating;
                        OR EOSB without confirmed post-EOSB salary.
    ability_unknown   — no CASA / payroll / bureau signal from any source.

Signal sources:
  Group A — crx_cc_departure_signature (T06, zero new joins; R14 reuse):
    payroll_present_h2      Pass I — salary deposit observed in any H2 month
    payroll_stopped_flag    Pass I — salary was present H1 but absent/stopping H2
    casa_inflow_stop_gap_d  Pass B — days since last salary CASA credit
                                     (diagnostic output only; not used in classifier)
    eosb_like_flag          Pass B — lump-sum gratuity inflow (termination signal)
    prior_spell_cnt_24m     Pass C — chronic default pattern vs first-time
    aecb_new_enquiry_3m     Pass G — credit-seeking in H2 (distress signal)

  Group B — sibling-repo features (schema-guarded; NULL emitted if absent):
    feat_payroll_indicator    (retail.feature_space) → salary_months_h2
    feat_casa_eod_balance     (retail.feature_space) → casa_eod_bal_h2
      ⚠ date col: month_end_date (YYYY-MM-dd); balance col:
        ft_avg_eod_balance_in_last_0_2_months_avg — PIT join (latest < T0)
    wm_fea_salary_days_since_increment (WM) → salary_amt_last,
                                              salary_change_pct (D5 only, not in output)
    wm_fea_casa_weekly_repeated_inflow (WM) → recurring_inflow_amt_h2,
                                              recurring_inflow_cnt_h2
    stg_aecb_salary_history  (AECB) → bureau_salary_present_6m_flag,
                                      bureau_salary_amt_last (6m window)
      ⚠ requires prm_bureau_cif_bridge for subj_salcr_hist_hdr_file_id→cif_id
    prm_bureau_alert_enriched (AECB) → a1_new_salary_acct_flag (alert_type_flag),
                                        a1_offus_paying_flag (90d window)
      ⚠ _ALERT_OFFUS_PAYING uses "positivealerts" prefix — confirmed from T26a EDA
        2026-09-17. Covers all DPD bands and product types.

  Group C — upstream crx tables (account/spell grain, no CIF bridge):
    crx_cc_payment_trajectory   (T04b) → pay_ratio_slope, pay_ratio_mean_h1/h2
    crx_cc_utilisation_features (T05)  → util_t0, util_slope, spend_cliff_flag
    prm_balance
                                       → cc_total_outstanding (PIT at T0)
  ⚠ WM feature coverage on delinquent CC population is UNPROVEN until T26 CHK-6.

Guard thresholds (tagged [CONFIRM] = pending stakeholder sign-off; Leg B tuning):
    _TAU_SALARY_ACTIVE_D     = 60   salary PIT gap: active if < this (days)  [CONFIRM]
    _TAU_SALARY_RECENCY_D    = 90   salary PIT gap: present if < this        [CONFIRM]
    _TAU_INFLOW_GAP_D        = 90   CASA inflow stop gap: active if < this   [CONFIRM]
    _TAU_RECURRING           = 2    recurring inflow months H2 ≥ this        [CONFIRM]
    _TAU_SALARY_H2_MIN       = 2    H2 payroll months needed for active      [CONFIRM]
    _TAU_UTIL_PRESSURE       = 0.80 util_t0 ≥ this → pressure_high          [CONFIRM]
    _TAU_PAY_SLOPE_GRADUAL   = -0.02 pay_ratio_slope < this → trajectory_gradual [CONFIRM]
    _TAU_UTIL_SLOPE_GRADUAL  =  0.02 util_slope > this → rising utilization  [CONFIRM]
    _TAU_MONTHS_RUNWAY       =  1.0 buffer_adequate: months_runway ≥ this    [CONFIRM]
    _TAU_CASA_INFLOW_H2_MIN  =   4  H2 weeks with any CASA inflow for active  [CONFIRM]

Five dimensions, ordered CASE WHEN:

  D1 — Income flow (salary_days_since_t0 removed; casa_inflow_stop_gap_d restored):
    income_active:  (payroll ≥ 2 H2 months AND not stopped)
                    OR bureau_salary_present_6m_flag=1
                    OR casa_inflow_stop_gap_d ≤ _TAU_INFLOW_GAP_D (salary CASA recent)
                    OR casa_inflow_cnt_h2 ≥ _TAU_CASA_INFLOW_H2_MIN (all CASA types)
    income_present: payroll_present_h2=1 AND salary_months_h2=1
                    OR payroll_stopped=1 (was present but stopping)
                    OR recurring_inflow_cnt_h2 ≥ 1
    income_stopped: payroll_stopped=1 AND bureau_salary_present_6m_flag≠1
                    AND (payroll_present_h2=0 OR salary_months_h2=0)

  ⚠ NULL-safe design: salary_months_h2 and payroll_stopped_flag are coalesced to their
    threshold defaults when NULL so Group A payroll signal is sufficient when Group B
    (feat_payroll_indicator) is absent. income_active + trajectory_gradual + NOT
    pressure_high falls to ability_unknown (spec gap — flag for GRR Leg B).
  ⚠ Income denominator (months_runway, cc_outstanding_vs_income): composite coalesce —
    salary_amt_last → bureau_salary_amt_last → casa_inflow_amt_h2 / 3 months.

  D2 — Savings buffer:
    buffer_adequate:     months_runway ≥ 1.0
    buffer_not_adequate: months_runway NULL or < 1.0

  D3 — Financial pressure at T0 (uses util_t0 from T05):
    pressure_high:  util_t0 ≥ 0.80

  D4 — Pre-T0 trajectory (uses pay_ratio_slope from T04b, util_slope from T05):
    trajectory_gradual: pay_ratio_slope < -0.02
                        OR (util_slope > 0.02 AND pay_ratio_mean_h2 < pay_ratio_mean_h1)
    trajectory_sudden:  pay_ratio_slope ≥ -0.02 AND spend_cliff_flag=1

  D5 — Recovery likelihood:
    recovery_likely: (salary_change_pct ≥ 0
                      OR (eosb_like_flag=1 AND eosb_post_salary_flag=1))
                     AND prior_spell_cnt_24m = 0
    eosb_post_salary_flag: proxy — eosb_like_flag=1 AND bureau_salary_present_6m_flag_recent=1

State rules (ordered CASE WHEN — falls through to ability_unknown):
  1. ability_high:     income_active AND NOT pressure_high AND NOT trajectory_gradual
  2. ability_moderate: (income_active AND pressure_high)
                       OR (income_present AND buffer_adequate)
                       OR (income_stopped AND trajectory_sudden AND recovery_likely)
                       OR recurring_inflow_cnt_h2 ≥ 2
  3. ability_limited:  (income_stopped AND buffer_not_adequate)
                       OR (income_present AND trajectory_gradual)
                       OR (pressure_high AND trajectory_gradual)
                       OR (eosb_like_flag=1 AND eosb_post_salary_flag≠1)
                         — EOSB without confirmed post-EOSB salary → limited
  4. ability_unknown:  everything else (no signal from any source)

  ⚠ All _TAU_ thresholds are PLACEHOLDERS — tune at Leg B after T26 PROD run.

H2 window: [T0 - 3 months, T0) — last 3 complete months before spell anchor.
PIT join (WM weekly): last record with week_number strictly before T0.
PIT join (CASA balance): latest month_end_date < T0.
H2 window (WM weekly): weeks with week_date in [T0 - 90 days, T0).
Bureau salary window: [T0 - 6 months, T0) — H1+H2.
Bureau alert window:  [T0 - 90 days, T0) — pre-T0 only (no leakage).

Design decisions:
  • 9-node pipeline: Nodes 3, 3r, 4, 4r, 5, 5r run in parallel after Node 2.
  • Node 2 (crx_cc_a1_cif_enriched) contains only CIF-resolved rows — the
    downstream Group B enrichers only see rows where cif_id is known.
  • Spine grain (account_id, observation_date): build_a1_base reworked to use
    cc_spine as grain anchor (same pattern as A2).  T0-anchored enrichers dedup
    to (account_id, spell_id) internally to prevent N×M overcounting.
  • Obs-date-anchored enrichers (_recent variants) use full spine grain — each
    observation_date gets its own income window anchored to scoring time.
  • CIF bridge uses the same _build_cif_bridge helper as A2 (R14).
  • Schema guards on all Group B joins: columns missing → NULL, no row loss.
  • account_id == contract_id in CC domain (confirmed by CIF bridge pattern).
  • Group C (T04b / T05 / prm_balance) joined at (account_id, spell_id) —
    no CIF bridge required.
"""

# pylint: disable=too-many-lines  # justified: 9-node pipeline with T0 + recent classifiers

import datetime
import logging

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enbd_collections.pipelines.crx_persona._spine_utils import (
    _build_cif_bridge,
    join_spine_to_spell,
)
from . import enrichers

LOG = logging.getLogger(__name__)

# ── Guard thresholds — [CONFIRM] = pending stakeholder sign-off (Leg B) ──────
_TAU_SALARY_ACTIVE_D = 60  # salary PIT gap (days): active if < this    [CONFIRM]
_TAU_SALARY_RECENCY_D = 90  # salary PIT gap (days): present if < this  [CONFIRM]
_TAU_INFLOW_GAP_D = 90  # CASA inflow stop gap: active if < this       [CONFIRM]
_TAU_RECURRING = 2  # recurring inflow months H2 ≥ this              [CONFIRM]
_TAU_SALARY_H2_MIN = 2  # H2 payroll months needed for active          [CONFIRM]
_TAU_UTIL_PRESSURE = 0.80  # util_t0 ≥ this → pressure_high              [CONFIRM]
_TAU_PAY_SLOPE_GRADUAL = -0.02  # pay_ratio_slope < this → gradual          [CONFIRM]
_TAU_UTIL_SLOPE_GRADUAL = 0.02  # util_slope > this → rising util           [CONFIRM]
_TAU_MONTHS_RUNWAY = 1.0  # buffer_adequate: months_runway ≥ this      [CONFIRM]
_TAU_CASA_INFLOW_H2_MIN = 4  # H2 weeks with any CASA inflow for active   [CONFIRM]

# ── Departure-sig columns forwarded in Node 1 ─────────────────────────────────
_DEPART_COLS = [
    "payroll_present_h2",
    "payroll_stopped_flag",
    "casa_inflow_stop_gap_d",
    "eosb_like_flag",
    "prior_spell_cnt_24m",  # Pass C — chronic pattern vs first-time default
    "aecb_new_enquiry_3m",  # Pass G — credit-seeking in H2 (distress signal)
]


# ── Node 1: build_a1_base ─────────────────────────────────────────────────────


def build_a1_base(
    cc_spine: DataFrame,
    spell_table: DataFrame,
    departure_sig: DataFrame,
) -> DataFrame:
    """Attach spell window + Group A income signals to the spine grain.

    Uses cc_spine as the grain anchor — identical pattern to build_a2_base.
    Spine→spell window join keeps all spine rows; spell columns are NULL for
    spine points with no active spell at that observation_date.

    Group A columns forwarded (zero-cost T06 Pass I/B/C/G reuse — R14):
        payroll_present_h2      salary deposit observed in any H2 month
        payroll_stopped_flag    salary was present H1 but absent/stopping H2
        casa_inflow_stop_gap_d  days since last salary CASA credit (NULL=no CASA)
        eosb_like_flag          lump-sum gratuity inflow (employment termination)
        prior_spell_cnt_24m     count of prior spells in last 24m (0 = first-time)
        aecb_new_enquiry_3m     new bureau enquiries in H2 (credit-seeking signal)

    Schema guard: any column absent from departure_sig is emitted as NULL.

    Args:
        cc_spine:      cc_spine — (contract_id, observation_date) grain model spine.
        spell_table:   crx_cc_spell_table (T03b). Grain: (account_id, spell_id).
        departure_sig: crx_cc_departure_signature (T06).

    Returns:
        DataFrame at (account_id, observation_date) grain with spell_id, t0,
        and Group A departure signal columns.
    """
    dep_sig = departure_sig
    for col in _DEPART_COLS:
        if col not in dep_sig.columns:
            LOG.warning(
                "build_a1_base: column '%s' absent from departure_sig — emitting NULL",
                col,
            )
            dep_sig = dep_sig.withColumn(col, F.lit(None))

    dep_sel = dep_sig.select("account_id", "spell_id", *_DEPART_COLS)

    # Spine→spell window join (shared utility — equality join + date filters)
    spine_with_spell = join_spine_to_spell(cc_spine, spell_table)

    result = spine_with_spell.join(dep_sel, on=["account_id", "spell_id"], how="left")
    return result


# ── Node 2: build_a1_cif_bridge ───────────────────────────────────────────────


def build_a1_cif_bridge(
    base: DataFrame,
    contract: DataFrame,
    client: DataFrame,
) -> DataFrame:
    """Resolve CIF for every spell; emit only CIF-resolved rows.

    Builds a two-hop bridge (prm_contract → prm_client) and left-joins onto
    the spell base.  Rows without a resolved cif_id are filtered out here so
    that all downstream Group B enrichers operate only on the joinable subset.
    The full base (including unresolved rows) is still passed to Nodes 5 and 6
    directly via crx_cc_a1_base.

    Logs the CIF resolution rate for CHK-7 validation.

    Args:
        base:     crx_cc_a1_base. Grain: (account_id, spell_id).
        contract: prm_contract — contract_id → client_id.
        client:   prm_client  — client_id → cif_id.

    Returns:
        crx_cc_a1_cif_enriched — (account_id, spell_id, t0, cif_id).
        Only rows where CIF was resolved; NULLs excluded.
    """
    cif_bridge = _build_cif_bridge(contract, client)

    with_cif = base.join(
        cif_bridge,
        on=base["account_id"] == cif_bridge["contract_id"],
        how="left",
    ).drop("contract_id")

    LOG.info(
        "build_a1_cif_bridge: CIF bridge built — resolution rate logged in PROD validation"
    )

    return with_cif.filter(F.col("cif_id").isNotNull()).select(
        F.col("account_id").cast("string"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("observation_date").cast("date"),
        F.col("cif_id"),
    )


# ── Node 3: build_a1_group_b_income ───────────────────────────────────────────


def build_a1_group_b_income(  # pylint: disable=too-many-locals
    cif_enriched: DataFrame,
    feat_payroll: DataFrame,
    feat_casa_bal: DataFrame,
    wm_salary: DataFrame,
    wm_casa_inflow: DataFrame,
    wm_labelled_transactions: DataFrame,
    beneficiary_cards: DataFrame,
    crx_persona: dict,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame:
    """WM / retail.feature_space income signals at CIF grain.

    Five enrichers, all schema-guarded:
      1. feat_payroll_indicator   (monthly, CIF-grain) → salary_months_h2
      2. feat_casa_eod_balance    (monthly, CIF-grain) → casa_eod_bal_h2 (PIT)
      3. wm_fea_salary_days_since_increment (weekly, CIF-grain) → salary_amt_last,
         salary_change_pct  [salary_days_since_t0 extracted but dropped — GRR Row 7]
      4. wm_fea_casa_cc_inflow_outflow (weekly, CIF-grain) → casa_inflow_amt_h2,
         casa_inflow_cnt_h2  — ALL CASA credit types, not salary-only
      5. wm_pri_labelled_transactions + raw_beneficiary_cards →
         ext_cc_payment_amt_h2, ext_cc_payment_cnt_h2
         CASA outflows to registered external CC numbers (H2 window)

    Also computes months_runway = casa_eod_bal_h2 / composite_income_monthly
    (savings buffer in months of income). Income denominator waterfall (Node 3 v1):
        salary_amt_last → casa_inflow_amt_h2 / 3 months.
    Note: bureau_salary_amt_last fallback is added by build_a1_classify
    (_assemble_classify_inputs) where Node 4 data is available, overriding this value.

    grain_key controls the output grain:
        ("account_id", "spell_id")         — T0-anchored (default); dedups to spell grain
        ("account_id", "observation_date") — obs-date-anchored (no dedup)

    Args:
        cif_enriched:             crx_cc_a1_cif_enriched — spine-grain CIF-resolved rows.
        feat_payroll:             feat_payroll_indicator. Required column: payroll_flag.
        feat_casa_bal:            feat_casa_eod_balance. Required columns: month_end_date,
                                  ft_avg_eod_balance_in_last_0_2_months_avg.
        wm_salary:                wm_fea_salary_days_since_increment. Required columns:
                                  ft_last_salary_amount, ft_days_since_salary_transaction,
                                  ft_percent_monthly_salary_change.
        wm_casa_inflow:           wm_fea_casa_cc_inflow_outflow. Required column:
                                  ft_inflow_casa_amt_in_last_0_0_weeks_sum.
        wm_labelled_transactions: wm_pri_labelled_transactions. Required columns:
                                  cif_id, in_out_flow, product_category, tran_date,
                                  tran_amt, transaction_acid.
        beneficiary_cards:        raw_beneficiary_cards. Required columns:
                                  instrument_number, instrument_type.
        crx_persona:              Persona param dict with persona_start_date used to
                                  floor wm_pri_labelled_transactions (one week per partition).
        grain_key:                Output grain key columns. Default ("account_id", "spell_id").

    Returns:
        DataFrame at grain_key grain — (grain_key..., salary_months_h2,
            casa_eod_bal_h2, salary_amt_last, salary_change_pct, months_runway,
            casa_inflow_amt_h2, casa_inflow_cnt_h2, ext_cc_payment_amt_h2,
            ext_cc_payment_cnt_h2).
        salary_change_pct is included for D5 use in build_a1_classify; it is
        dropped from the final output.
    """
    wm_labelled_transactions = wm_labelled_transactions.filter(
        F.col("tran_date") >= F.lit(crx_persona["persona_start_date"])
    )
    # Dedup to spell grain for T0-anchored variant to prevent NxM explosion
    # when spine-grain cif_enriched (N rows per spell) joins external features.
    if "spell_id" in grain_key:
        cif_enriched = cif_enriched.dropDuplicates(["account_id", "spell_id"])

    salary_h2 = enrichers.enrich_salary_months_h2(
        cif_enriched, feat_payroll, anchor_col, grain_key
    )
    casa_h2 = enrichers.enrich_casa_eod_bal_h2(
        cif_enriched, feat_casa_bal, anchor_col, grain_key
    )
    sal_pit = enrichers.enrich_salary_pit(
        cif_enriched, wm_salary, anchor_col, grain_key
    )
    casa_inflow_h2 = enrichers.enrich_casa_inflow_h2(
        cif_enriched, wm_casa_inflow, anchor_col, grain_key
    )
    obt_h2 = enrichers.enrich_ext_cc_payments_h2(
        cif_enriched, wm_labelled_transactions, beneficiary_cards, anchor_col, grain_key
    )

    result = cif_enriched.select(*grain_key)

    if salary_h2 is not None:
        result = result.join(salary_h2, on=list(grain_key), how="left")
    else:
        result = result.withColumn("salary_months_h2", F.lit(None).cast("int"))

    if casa_h2 is not None:
        result = result.join(casa_h2, on=list(grain_key), how="left")
    else:
        result = result.withColumn("casa_eod_bal_h2", F.lit(None).cast("double"))

    if sal_pit is not None:
        result = result.join(sal_pit, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "salary_amt_last", F.lit(None).cast("double")
        ).withColumn("salary_change_pct", F.lit(None).cast("double"))

    if casa_inflow_h2 is not None:
        result = result.join(casa_inflow_h2, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "casa_inflow_amt_h2", F.lit(None).cast("double")
        ).withColumn("casa_inflow_cnt_h2", F.lit(None).cast("int"))

    if obt_h2 is not None:
        result = result.join(obt_h2, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "ext_cc_payment_amt_h2", F.lit(None).cast("double")
        ).withColumn(
            "ext_cc_payment_cnt_h2", F.lit(None).cast("int")
        )  # schema guard

    # months_runway: savings buffer in months of income.
    # Denominator waterfall: WM salary → CASA inflow monthly average (H2 / 3m).
    _income_monthly = F.coalesce(
        F.col("salary_amt_last"),
        F.col("casa_inflow_amt_h2") / F.lit(3.0),
    )
    result = result.withColumn(
        "months_runway",
        F.when(
            F.col("casa_eod_bal_h2").isNotNull()
            & _income_monthly.isNotNull()
            & (_income_monthly > 0),
            F.col("casa_eod_bal_h2") / _income_monthly,
        ).otherwise(F.lit(None).cast("double")),
    )

    return result.select(
        *grain_key,
        F.col("salary_months_h2").cast("int"),
        F.col("casa_eod_bal_h2").cast("double"),
        F.col("salary_amt_last").cast("double"),
        F.col("salary_change_pct").cast(
            "double"
        ),  # D5 input; dropped from final output
        F.col("months_runway").cast("double"),
        F.col("casa_inflow_amt_h2").cast("double"),
        F.col("casa_inflow_cnt_h2").cast("int"),
        F.col("ext_cc_payment_amt_h2").cast("double"),
        F.col("ext_cc_payment_cnt_h2").cast("int"),
    )


# ── Node 4: build_a1_group_b_bureau ───────────────────────────────────────────


def build_a1_group_b_bureau(  # pylint: disable=too-many-arguments
    cif_enriched: DataFrame,
    wm_recurring: DataFrame,
    stg_salary_hist: DataFrame,
    prm_bureau_alert: DataFrame,
    prm_bureau_cif_bridge: DataFrame,
    fea_aecb_alerts: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame:
    """AECB bureau + WM recurring inflow signals at CIF grain.

    Four enrichers, all schema-guarded:
      1. wm_fea_casa_weekly_repeated_inflow → recurring_inflow_amt_h2,
         recurring_inflow_cnt_h2
      2. stg_aecb_salary_history + prm_bureau_cif_bridge → bureau_salary_present_6m_flag,
         bureau_salary_amt_last (6m window)
      3. prm_bureau_alert_enriched → a1_new_salary_acct_flag (add-only, exact),
         a1_offus_paying_flag (positivealerts* prefix, 90d pre-T0 window)
      4. fea_monthly_aecb_alerts → fea_salary_acct_flag (add-or-close, 3m rolling sum)

    a1_new_salary_acct_flag is the union of sources 3 and 4: fires if either
    source detects a salary account event.  This provides redundancy while the
    bureau pipeline correctness is being validated.  Source 3 is add-only and
    more precise; source 4 (feature_space) is add-or-close and serves as a
    corroborating fallback.

    Combination rule (NULL-safe OR):
        1 if either source returns 1
        0 if at least one source returned data and neither returned 1
        NULL only if both sources returned NULL (no CIF coverage at all)

    prm_bureau_cif_bridge is required to bridge stg_aecb_salary_history
    (subj_salcr_hist_hdr_file_id) to cif_id.

    grain_key controls the output grain:
        ("account_id", "spell_id")         — T0-anchored (default); dedups to spell grain
        ("account_id", "observation_date") — obs-date-anchored (no dedup)

    Args:
        cif_enriched:          crx_cc_a1_cif_enriched — spine-grain CIF-resolved rows.
        wm_recurring:          wm_fea_casa_weekly_repeated_inflow.
        stg_salary_hist:       stg_aecb_salary_history (AECB bureau salary history).
        prm_bureau_alert:      prm_bureau_alert_enriched (AECB bureau alerts).
        prm_bureau_cif_bridge: prm_bureau_cif_bridge — (bureau_file_id → cif_id).
        fea_aecb_alerts:       fea_monthly_aecb_alerts (retail.feature_space).
        grain_key:             Output grain key columns. Default ("account_id", "spell_id").

    Returns:
        DataFrame at grain_key grain — (grain_key..., recurring_inflow_amt_h2,
            recurring_inflow_cnt_h2, bureau_salary_present_6m_flag,
            a1_new_salary_acct_flag, a1_offus_paying_flag).
    """
    # Dedup to spell grain for T0-anchored variant to prevent NxM explosion
    if "spell_id" in grain_key:
        cif_enriched = cif_enriched.dropDuplicates(["account_id", "spell_id"])

    rec_h2 = enrichers.enrich_recurring_inflow_h2(
        cif_enriched, wm_recurring, anchor_col, grain_key
    )
    bur_sal = enrichers.enrich_bureau_salary(
        cif_enriched, stg_salary_hist, prm_bureau_cif_bridge, anchor_col, grain_key
    )
    bur_alerts = enrichers.enrich_bureau_alerts(
        cif_enriched, prm_bureau_alert, anchor_col, grain_key
    )
    fea_alerts = enrichers.enrich_fea_bureau_alerts(
        cif_enriched, fea_aecb_alerts, anchor_col, grain_key
    )

    result = cif_enriched.select(*grain_key)

    if rec_h2 is not None:
        result = result.join(rec_h2, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "recurring_inflow_amt_h2", F.lit(None).cast("double")
        ).withColumn("recurring_inflow_cnt_h2", F.lit(None).cast("int"))

    if bur_sal is not None:
        result = result.join(bur_sal, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "bureau_salary_present_6m_flag", F.lit(None).cast("int")
        ).withColumn("bureau_salary_amt_last", F.lit(None).cast("double"))

    # Join both alert sources; combine into a single a1_new_salary_acct_flag
    if bur_alerts is not None:
        result = result.join(bur_alerts, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "a1_new_salary_acct_flag", F.lit(None).cast("int")
        ).withColumn("a1_offus_paying_flag", F.lit(None).cast("int"))

    if fea_alerts is not None:
        result = result.join(
            fea_alerts.withColumnRenamed(
                "fea_salary_acct_flag", "_fea_salary_acct_flag"
            ),
            on=list(grain_key),
            how="left",
        )
    else:
        result = result.withColumn("_fea_salary_acct_flag", F.lit(None).cast("int"))

    # NULL-safe OR: 1 if either fires; NULL only when both are NULL
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


# ── Node 3r: build_a1_group_b_income_recent ───────────────────────────────────


def build_a1_group_b_income_recent(
    cif_enriched: DataFrame,
    feat_payroll: DataFrame,
    feat_casa_bal: DataFrame,
    wm_salary: DataFrame,
    wm_casa_inflow: DataFrame,
    wm_labelled_transactions: DataFrame,
    beneficiary_cards: DataFrame,
    crx_persona: dict,
) -> DataFrame:
    """observation_date-anchored income signals.

    Same logic as build_a1_group_b_income but anchors all H2 windows to
    observation_date instead of t0.  Enables dynamic re-scoring at each
    collection run: answers "what is the customer's financial state RIGHT NOW?"
    rather than "what was it when they went delinquent?".

    For accounts where observation_date == t0 (freshly delinquent), results
    are identical to the T0 variant — correct by design.
    """
    return build_a1_group_b_income(
        cif_enriched,
        feat_payroll,
        feat_casa_bal,
        wm_salary,
        wm_casa_inflow,
        wm_labelled_transactions,
        beneficiary_cards,
        crx_persona,
        anchor_col="observation_date",
        grain_key=("account_id", "observation_date"),
    )


# ── Node 4r: build_a1_group_b_bureau_recent ───────────────────────────────────


def build_a1_group_b_bureau_recent(  # pylint: disable=too-many-arguments
    cif_enriched: DataFrame,
    wm_recurring: DataFrame,
    stg_salary_hist: DataFrame,
    prm_bureau_alert: DataFrame,
    prm_bureau_cif_bridge: DataFrame,
    fea_aecb_alerts: DataFrame,
) -> DataFrame:
    """observation_date-anchored bureau + recurring inflow signals.

    Same logic as build_a1_group_b_bureau but anchors all windows to
    observation_date instead of t0.
    """
    return build_a1_group_b_bureau(
        cif_enriched,
        wm_recurring,
        stg_salary_hist,
        prm_bureau_alert,
        prm_bureau_cif_bridge,
        fea_aecb_alerts,
        anchor_col="observation_date",
        grain_key=("account_id", "observation_date"),
    )


# ── Node 5: build_a1_group_c ──────────────────────────────────────────────────


def build_a1_group_c(
    base: DataFrame,
    payment_traj: DataFrame,
    util_features: DataFrame,
    prm_balance: DataFrame,
) -> DataFrame:
    """Payment trajectory, utilisation, and outstanding balance (spell-grain).

    Three enrichers joined at (account_id, spell_id) — no CIF bridge required:
      1. crx_cc_payment_trajectory (T04b) → pay_ratio_slope, pay_ratio_mean_h1/h2
      2. crx_cc_utilisation_features (T05) → util_t0, util_slope, spend_cliff_flag
      3. prm_balance — PIT at banking_date ≤ T0 → cc_total_outstanding

    This node runs in parallel with Nodes 3 and 4 (depends only on Node 1 output).

    Args:
        base:          crx_cc_a1_base. Grain: (account_id, spell_id).
        payment_traj:  crx_cc_payment_trajectory (T04b).
        util_features: crx_cc_utilisation_features (T05).
        prm_balance:   prm_balance.

    Returns:
        crx_cc_a1_group_c — (account_id, spell_id, pay_ratio_slope,
            pay_ratio_mean_h1, pay_ratio_mean_h2, util_t0, util_slope,
            spend_cliff_flag, cc_total_outstanding).
    """
    # Dedup base to spell grain — base is at spine grain after build_a1_base rework.
    # T04b / T05 / prm_balance are all T0-anchored spell-grain enrichers; feeding
    # N spine rows per spell would produce Nx overcounting in those joins.
    spell_base = base.dropDuplicates(["account_id", "spell_id"])

    t04b = enrichers.enrich_payment_trajectory(spell_base, payment_traj)
    t05 = enrichers.enrich_utilisation(spell_base, util_features)
    bal = enrichers.enrich_prm_balance(spell_base, prm_balance)

    result = spell_base.select("account_id", "spell_id")

    if t04b is not None:
        result = result.join(t04b, on=["account_id", "spell_id"], how="left")
    else:
        result = (
            result.withColumn("pay_ratio_slope", F.lit(None).cast("double"))
            .withColumn("pay_ratio_mean_h1", F.lit(None).cast("double"))
            .withColumn("pay_ratio_mean_h2", F.lit(None).cast("double"))
        )

    if t05 is not None:
        result = result.join(t05, on=["account_id", "spell_id"], how="left")
    else:
        result = (
            result.withColumn("util_t0", F.lit(None).cast("double"))
            .withColumn("util_slope", F.lit(None).cast("double"))
            .withColumn("spend_cliff_flag", F.lit(None).cast("int"))
        )

    if bal is not None:
        result = result.join(bal, on=["account_id", "spell_id"], how="left")
    else:
        result = result.withColumn("cc_total_outstanding", F.lit(None).cast("double"))

    return result.select(
        F.col("account_id").cast("string"),
        F.col("spell_id").cast("int"),
        F.col("pay_ratio_slope").cast("double"),
        F.col("pay_ratio_mean_h1").cast("double"),
        F.col("pay_ratio_mean_h2").cast("double"),
        F.col("util_t0").cast("double"),
        F.col("util_slope").cast("double"),
        F.col("spend_cliff_flag").cast("int"),
        F.col("cc_total_outstanding").cast("double"),
    )


# ── Node 5r: build_a1_group_c_recent ──────────────────────────────────────────


def build_a1_group_c_recent(
    base: DataFrame,
    prm_balance: DataFrame,
) -> DataFrame:
    """Outstanding balance at observation_date grain (spine-grain counterpart to group_c).

    Single enricher — only cc_total_outstanding_recent is needed at obs-date anchor.
    Payment trajectory and utilisation are T0-anchored spell-grain features and are
    not re-windowed here.

    Args:
        base:        crx_cc_a1_base — spine grain (account_id, observation_date).
        prm_balance: prm_balance — CC outstanding balance history.

    Returns:
        DataFrame (account_id, observation_date, cc_total_outstanding_recent).
        cc_total_outstanding_recent is NULL if prm_balance has no row at or before
        the scoring observation_date.
    """
    bal = enrichers.enrich_prm_balance(
        base,
        prm_balance,
        anchor_col="observation_date",
        grain_key=("account_id", "observation_date"),
    )

    result = base.select("account_id", "observation_date").dropDuplicates(
        ["account_id", "observation_date"]
    )

    if bal is not None:
        result = result.join(bal, on=["account_id", "observation_date"], how="left")
    else:
        result = result.withColumn(
            "cc_total_outstanding_recent", F.lit(None).cast("double")
        )

    return result.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("cc_total_outstanding_recent").cast("double"),
    )


# ── Classify helpers (private) ────────────────────────────────────────────────


def _assemble_classify_inputs(  # pylint: disable=too-many-arguments
    base: DataFrame,
    group_b_income: DataFrame,
    group_b_bureau: DataFrame,
    group_c: DataFrame,
    inc_recent: DataFrame,
    bur_recent: DataFrame,
    group_c_recent: DataFrame,
) -> DataFrame:
    """Join all enrichments onto base; derive EOSB proxy flags and T0 debt-load ratio.

    Renames obs-date-anchored (_recent) columns with the ``_recent`` suffix so
    both T0 and obs-date variants coexist on the same row.  All subsequent
    classifier helpers operate on the assembled result.
    """
    _inc_recent_cols = [
        "salary_months_h2",
        "casa_eod_bal_h2",
        "salary_amt_last",
        "salary_change_pct",
        "months_runway",
        "casa_inflow_amt_h2",
        "casa_inflow_cnt_h2",
        "ext_cc_payment_amt_h2",
        "ext_cc_payment_cnt_h2",
    ]
    _bur_recent_cols = [
        "recurring_inflow_amt_h2",
        "recurring_inflow_cnt_h2",
        "bureau_salary_present_6m_flag",
        "bureau_salary_amt_last",
        "a1_new_salary_acct_flag",
        "a1_offus_paying_flag",
    ]
    inc_recent_renamed = inc_recent.select(
        "account_id",
        "observation_date",
        *[F.col(c).alias(f"{c}_recent") for c in _inc_recent_cols],
    )
    bur_recent_renamed = bur_recent.select(
        "account_id",
        "observation_date",
        *[F.col(c).alias(f"{c}_recent") for c in _bur_recent_cols],
    )

    # T0-anchored (spell-grain) joins broadcast to all spine obs_dates.
    # Obs-date-anchored (_recent) joins match the exact scoring date.
    result = (
        base.join(group_b_income, on=["account_id", "spell_id"], how="left")
        .join(group_b_bureau, on=["account_id", "spell_id"], how="left")
        .join(group_c, on=["account_id", "spell_id"], how="left")
        .join(inc_recent_renamed, on=["account_id", "observation_date"], how="left")
        .join(bur_recent_renamed, on=["account_id", "observation_date"], how="left")
        .join(group_c_recent, on=["account_id", "observation_date"], how="left")
    )

    # eosb_post_salary_flag: obs-date bureau signal confirms post-EOSB income
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

    # eosb_post_salary_flag_recent: same proxy anchored to obs-date bureau signal
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

    # Fix 4b: recompute months_runway with bureau_salary_amt_last fallback.
    # Node 3 computes months_runway without bureau salary because bureau data
    # (Node 4) is not yet available.  Here in Node 6, all inputs are joined so
    # we override with the full denominator waterfall matching cc_outstanding_vs_income.
    _runway_income_t0 = F.coalesce(
        F.col("salary_amt_last"),
        F.col("bureau_salary_amt_last"),
        F.col("casa_inflow_amt_h2") / F.lit(3.0),
    )
    result = result.withColumn(
        "months_runway",
        F.when(
            F.col("casa_eod_bal_h2").isNotNull()
            & _runway_income_t0.isNotNull()
            & (_runway_income_t0 > 0),
            F.col("casa_eod_bal_h2") / _runway_income_t0,
        ).otherwise(F.lit(None).cast("double")),
    )
    _runway_income_recent = F.coalesce(
        F.col("salary_amt_last_recent"),
        F.col("bureau_salary_amt_last_recent"),
        F.col("casa_inflow_amt_h2_recent") / F.lit(3.0),
    )
    result = result.withColumn(
        "months_runway_recent",
        F.when(
            F.col("casa_eod_bal_h2_recent").isNotNull()
            & _runway_income_recent.isNotNull()
            & (_runway_income_recent > 0),
            F.col("casa_eod_bal_h2_recent") / _runway_income_recent,
        ).otherwise(F.lit(None).cast("double")),
    )

    # cc_outstanding_vs_income: debt load in months of T0-anchored income
    _income_monthly = F.coalesce(
        F.col("salary_amt_last"),
        F.col("bureau_salary_amt_last"),
        F.col("casa_inflow_amt_h2") / F.lit(3.0),
    )
    result = result.withColumn(
        "cc_outstanding_vs_income",
        F.when(
            F.col("cc_total_outstanding").isNotNull()
            & _income_monthly.isNotNull()
            & (_income_monthly > 0),
            F.col("cc_total_outstanding") / _income_monthly,
        ).otherwise(F.lit(None).cast("double")),
    )

    return result


def _build_ability_conditions(suffix: str = "", obs_date_only: bool = False) -> dict:
    """Build D1–D5 condition expressions for a given signal anchor.

    Args:
        suffix: ``""`` for T0-anchored signals; ``"_recent"`` for obs-date-anchored.
                D3 (pressure_high) and D4 (trajectory_gradual, trajectory_sudden)
                always use T0-anchored Group C columns regardless of suffix —
                Group C is not re-windowed at obs-date.
        obs_date_only: When True, removes T0 Group A gates (payroll_present_h2,
                payroll_stopped_flag, casa_inflow_stop_gap_d) from income_active,
                income_stopped, and income_present.  Used for the primary
                a1_state classifier.  GRR feedback (Sep 2026): ability must
                reflect current state, not pre-delinquency behaviour.

    Returns:
        Dict of Spark Column expressions keyed by condition name.
    """
    # D1 — Income flow
    if obs_date_only:
        # Obs-date-only variant: no T0 Group A gates.
        # income_active: any obs-date income signal above threshold fires.
        # casa_inflow_stop_gap_d (T0 Group A) is excluded; casa_inflow_cnt_h2_recent
        # covers the same population via the obs-date CASA inflow count.
        cond_income_active = (
            (
                F.col(f"salary_months_h2{suffix}").isNotNull()
                & (F.col(f"salary_months_h2{suffix}") >= _TAU_SALARY_H2_MIN)
            )
            | (F.col(f"bureau_salary_present_6m_flag{suffix}") == 1)
            | (
                F.col(f"casa_inflow_cnt_h2{suffix}").isNotNull()
                & (F.col(f"casa_inflow_cnt_h2{suffix}") >= _TAU_CASA_INFLOW_H2_MIN)
            )
            | (F.coalesce(F.col(f"ext_cc_payment_cnt_h2{suffix}"), F.lit(0)) >= 2)
        )

        # income_stopped: no obs-date income signal from any source (absence check).
        # payroll_stopped_flag and payroll_present_h2 (T0) are excluded.
        cond_income_stopped = (
            (F.coalesce(F.col(f"salary_months_h2{suffix}"), F.lit(0)) == 0)
            & (
                F.coalesce(F.col(f"bureau_salary_present_6m_flag{suffix}"), F.lit(0))
                != 1
            )
            & (F.coalesce(F.col(f"casa_inflow_cnt_h2{suffix}"), F.lit(0)) == 0)
        )

        # income_present: obs-date-only variant; T0 Group A gates excluded.
        # Fix: null-safe coalesce on salary_months_h2 — NULL comparison returns NULL
        # in Spark (treated as false). For cc_180_plus ~58% of rows have NULL
        # salary_months_h2; without coalesce the first arm is silently dead.
        cond_income_present = (
            (F.coalesce(F.col(f"salary_months_h2{suffix}"), F.lit(0)) >= 1)
            | (
                F.col(f"recurring_inflow_cnt_h2{suffix}").isNotNull()
                & (F.col(f"recurring_inflow_cnt_h2{suffix}") >= 1)
            )
            | (F.coalesce(F.col(f"ext_cc_payment_cnt_h2{suffix}"), F.lit(0)) >= 1)
        )
    else:
        # Full T0-anchored variant with Group A gates.
        # Arm 1 requires payroll_present_h2 (Group A T0) as a gate.
        # Arm 3 uses casa_inflow_stop_gap_d (Group A T0).
        cond_income_active = (
            (
                (F.col("payroll_present_h2") == 1)
                & (
                    F.coalesce(
                        F.col(f"salary_months_h2{suffix}"), F.lit(_TAU_SALARY_H2_MIN)
                    )
                    >= _TAU_SALARY_H2_MIN
                )
                & (F.coalesce(F.col("payroll_stopped_flag"), F.lit(0)) == 0)
            )
            | (F.col(f"bureau_salary_present_6m_flag{suffix}") == 1)
            | (
                F.col("casa_inflow_stop_gap_d").isNotNull()
                & (F.col("casa_inflow_stop_gap_d") <= _TAU_INFLOW_GAP_D)
            )
            | (
                F.col(f"casa_inflow_cnt_h2{suffix}").isNotNull()
                & (F.col(f"casa_inflow_cnt_h2{suffix}") >= _TAU_CASA_INFLOW_H2_MIN)
            )
            | (F.coalesce(F.col(f"ext_cc_payment_cnt_h2{suffix}"), F.lit(0)) >= 2)
        )

        cond_income_stopped = (
            (F.col("payroll_stopped_flag") == 1)
            & (
                F.coalesce(F.col(f"bureau_salary_present_6m_flag{suffix}"), F.lit(0))
                != 1
            )
            & (
                (F.coalesce(F.col("payroll_present_h2"), F.lit(0)) == 0)
                | (
                    F.col(f"salary_months_h2{suffix}").isNotNull()
                    & (F.col(f"salary_months_h2{suffix}") == 0)
                )
            )
        )

        # Fix: null-safe coalesce on salary_months_h2 — NULL comparison returns NULL
        # in Spark (treated as false). For cc_180_plus ~58% of rows have NULL
        # salary_months_h2; without coalesce the first arm of income_present is
        # silently dead for most of the population.
        cond_income_present = (
            (
                (F.col("payroll_present_h2") == 1)
                & (F.coalesce(F.col(f"salary_months_h2{suffix}"), F.lit(0)) == 1)
            )
            | (F.col("payroll_stopped_flag") == 1)
            | (
                F.col(f"recurring_inflow_cnt_h2{suffix}").isNotNull()
                & (F.col(f"recurring_inflow_cnt_h2{suffix}") >= 1)
            )
            | (F.coalesce(F.col(f"ext_cc_payment_cnt_h2{suffix}"), F.lit(0)) >= 1)
        )

    # D2 — Savings buffer
    cond_buffer_adequate = F.col(f"months_runway{suffix}").isNotNull() & (
        F.col(f"months_runway{suffix}") >= _TAU_MONTHS_RUNWAY
    )
    cond_buffer_not_adequate = F.col(f"months_runway{suffix}").isNull() | (
        F.col(f"months_runway{suffix}") < _TAU_MONTHS_RUNWAY
    )

    # D3 — Financial pressure at T0 (always T0-anchored — Group C not re-windowed)
    cond_pressure_high = F.col("util_t0").isNotNull() & (
        F.col("util_t0") >= _TAU_UTIL_PRESSURE
    )

    # D4 — Pre-T0 trajectory (always T0-anchored — Group C not re-windowed)
    cond_trajectory_gradual = (
        F.col("pay_ratio_slope").isNotNull()
        & (F.col("pay_ratio_slope") < _TAU_PAY_SLOPE_GRADUAL)
    ) | (
        F.col("util_slope").isNotNull()
        & (F.col("util_slope") > _TAU_UTIL_SLOPE_GRADUAL)
        & F.col("pay_ratio_mean_h2").isNotNull()
        & F.col("pay_ratio_mean_h1").isNotNull()
        & (F.col("pay_ratio_mean_h2") < F.col("pay_ratio_mean_h1"))
    )

    cond_trajectory_sudden = (
        F.col("pay_ratio_slope").isNull()
        | (F.col("pay_ratio_slope") >= _TAU_PAY_SLOPE_GRADUAL)
    ) & (F.col("spend_cliff_flag") == 1)

    # D5 — Recovery likelihood
    cond_recovery_likely = (
        (
            F.col(f"salary_change_pct{suffix}").isNotNull()
            & (F.col(f"salary_change_pct{suffix}") >= 0)
        )
        | (
            (F.col("eosb_like_flag") == 1)
            & (F.col(f"eosb_post_salary_flag{suffix}") == 1)
        )
    ) & (F.coalesce(F.col("prior_spell_cnt_24m"), F.lit(0)) == 0)

    # Derived compound conditions (suffix-dependent; kept in conds to avoid
    # passing suffix into _apply_ability_classifier)
    cond_recurring_moderate = F.col(f"recurring_inflow_cnt_h2{suffix}").isNotNull() & (
        F.col(f"recurring_inflow_cnt_h2{suffix}") >= _TAU_RECURRING
    )

    # EOSB limited: no confirmed post-EOSB salary; coalesce NULL → 0 (conservative)
    cond_eosb_limited = (F.col("eosb_like_flag") == 1) & (
        F.coalesce(F.col(f"eosb_post_salary_flag{suffix}"), F.lit(0)) != 1
    )

    return {
        "income_active": cond_income_active,
        "income_present": cond_income_present,
        "income_stopped": cond_income_stopped,
        "buffer_adequate": cond_buffer_adequate,
        "buffer_not_adequate": cond_buffer_not_adequate,
        "pressure_high": cond_pressure_high,
        "trajectory_gradual": cond_trajectory_gradual,
        "trajectory_sudden": cond_trajectory_sudden,
        "recovery_likely": cond_recovery_likely,
        "recurring_moderate": cond_recurring_moderate,
        "eosb_limited": cond_eosb_limited,
    }


def _apply_ability_classifier(df: DataFrame, conds: dict, state_col: str) -> DataFrame:
    """Apply the 4-state ordered CASE WHEN and return df with state_col added.

    Full waterfall: HIGH → MODERATE → LIMITED → UNKNOWN, using pressure,
    trajectory, and buffer gates from the supplied conditions dict.
    """
    cond_high = (
        conds["income_active"] & ~conds["pressure_high"] & ~conds["trajectory_gradual"]
    )

    cond_moderate = (
        (conds["income_active"] & conds["pressure_high"])
        | (conds["income_present"] & conds["buffer_adequate"])
        | (
            conds["income_stopped"]
            & conds["trajectory_sudden"]
            & conds["recovery_likely"]
        )
        | conds["recurring_moderate"]
    )

    cond_limited = (
        (conds["income_stopped"] & conds["buffer_not_adequate"])
        | (conds["income_present"] & conds["trajectory_gradual"])
        | (conds["pressure_high"] & conds["trajectory_gradual"])
        | conds["eosb_limited"]
    )

    return df.withColumn(
        state_col,
        F.when(cond_high, "ability_high")
        .when(cond_moderate, "ability_moderate")
        .when(cond_limited, "ability_limited")
        .otherwise("ability_unknown"),
    )


def _apply_ability_classifier_primary(
    df: DataFrame, conds: dict, state_col: str
) -> DataFrame:
    """Simplified 4-state waterfall for primary obs-date-anchored a1_state.

    GRR feedback (Sep 2026 workshop): ability must reflect the customer's current
    state, not pre-delinquency behaviour.  T0-anchored gates (pressure_high,
    trajectory_*, buffer_*) are excluded.

    Waterfall:
        HIGH:     income_active (obs-date income signals only)
        MODERATE: income_present | recovery_likely | recurring_moderate
        LIMITED:  income_stopped | eosb_limited
        UNKNOWN:  fallthrough (no obs-date income signal from any source)

    The CASA buffer (months_runway) is not a gate here — Collections places a lien
    on accessible ENBD CASA funds, so CASA balance is not genuinely available for
    voluntary repayment at 60+ DPD. months_runway_recent remains in the output as a
    pass-through diagnostic column.
    """
    cond_high = conds["income_active"]

    cond_moderate = (
        conds["income_present"] | conds["recovery_likely"] | conds["recurring_moderate"]
    )

    cond_limited = conds["income_stopped"] | conds["eosb_limited"]

    return df.withColumn(
        state_col,
        F.when(cond_high, "ability_high")
        .when(cond_moderate, "ability_moderate")
        .when(cond_limited, "ability_limited")
        .otherwise("ability_unknown"),
    )


def _build_a1_output_select(result: DataFrame) -> DataFrame:
    """Apply typed output schema and return final crx_cc_a1_ability DataFrame."""
    return result.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("a1_state").cast("string"),
        F.col("a1_provenance").cast("string"),
        F.col("a1_confidence").cast("double"),
        F.col("a1_payroll_stopped").cast("int"),
        F.col("casa_inflow_stop_gap_d").cast("double").alias("a1_casa_gap_d"),
        F.col("eosb_like_flag").cast("int").alias("a1_eosb_signal"),
        F.col("eosb_post_salary_flag").cast("int").alias("a1_eosb_post_salary"),
        F.col("salary_months_h2").cast("int"),
        F.col("casa_eod_bal_h2").cast("double"),
        F.col("salary_amt_last").cast("double"),
        F.col("bureau_salary_amt_last").cast("double"),
        F.col("casa_inflow_amt_h2").cast("double"),
        F.col("casa_inflow_cnt_h2").cast("int"),
        F.col("ext_cc_payment_amt_h2").cast("double"),
        F.col("ext_cc_payment_cnt_h2").cast("int"),
        F.col("recurring_inflow_amt_h2").cast("double"),
        F.col("recurring_inflow_cnt_h2").cast("int"),
        F.col("bureau_salary_present_6m_flag").cast("int"),
        F.col("a1_new_salary_acct_flag").cast("int"),
        F.col("a1_offus_paying_flag").cast("int"),
        F.col("months_runway").cast("double"),
        F.col("cc_total_outstanding").cast("double"),
        F.col("cc_outstanding_vs_income").cast("double"),
        F.col("pre_stress_flag").cast("int"),
        F.col("pay_ratio_slope").cast("double"),
        F.col("util_t0").cast("double"),
        F.col("recovery_signal").cast("int"),
        F.col("a1_income_source").cast("string"),
        # obs-date feature columns (GRR Rows 2 / 6 / 7 / 10 compliance)
        F.col("salary_months_h2_recent").cast("int"),
        F.col("casa_eod_bal_h2_recent").cast("double"),
        F.col("casa_inflow_cnt_h2_recent").cast("int"),
        F.col("recurring_inflow_cnt_h2_recent").cast("int"),
        F.col("bureau_salary_present_6m_flag_recent").cast("int"),
        F.col("salary_amt_last_recent").cast("double"),
        F.col("months_runway_recent").cast("double"),
        F.col("cc_total_outstanding_recent").cast("double"),
        F.col("cc_outstanding_vs_income_recent").cast("double"),
        F.col("casa_coverage_ratio").cast("double"),
        F.lit(datetime.date.today().isoformat()).cast("date").alias("computed_at"),
    )


# ── Node 6: build_a1_classify ─────────────────────────────────────────────────


def build_a1_classify(  # pylint: disable=too-many-arguments
    base: DataFrame,
    group_b_income: DataFrame,
    group_b_bureau: DataFrame,
    group_c: DataFrame,
    inc_recent: DataFrame,
    bur_recent: DataFrame,
    group_c_recent: DataFrame,
) -> DataFrame:
    """Assemble enriched signals and classify A1 income-ability state.

    Thin orchestrator: delegates assembly, condition building, classification,
    and output typing to private helpers.  a1_state is obs-date-anchored.
    a1_provenance: "obs_date" when ≥1 _recent income signal is non-null;
    "no_signal" when all _recent signals are null.

    The EOSB post-salary proxy is derived in _assemble_classify_inputs because
    it requires eosb_like_flag from the departure signature (Group A / base).
    Proxy logic: eosb_like_flag=1 AND bureau_salary_present_6m_flag_recent=1 → 1
                 eosb_like_flag=1 AND bureau_salary_present_6m_flag_recent≠1 → 0
                 eosb_like_flag≠1 → NULL

    Args:
        base:           crx_cc_a1_base — Group A signals + t0.
        group_b_income: crx_cc_a1_group_b_income — T0-anchored income signals.
        group_b_bureau: crx_cc_a1_group_b_bureau — T0-anchored bureau + recurring.
        group_c:        crx_cc_a1_group_c — payment/utilisation/balance.
        inc_recent:     crx_cc_a1_group_b_income_recent — obs-date-anchored income.
        bur_recent:     crx_cc_a1_group_b_bureau_recent — obs-date-anchored bureau.
        group_c_recent: crx_cc_a1_group_c_recent — obs-date-anchored balance.

    Returns:
        crx_cc_a1_ability — ability axis with obs-date primary state.
    """
    result = _assemble_classify_inputs(
        base,
        group_b_income,
        group_b_bureau,
        group_c,
        inc_recent,
        bur_recent,
        group_c_recent,
    )

    # ── Obs-date-anchored state (primary) ─────────────────────────────────────
    # obs_date_only=True: removes T0 Group A gates from income_active and
    # income_stopped. T0 Group A signals (eosb_like_flag, prior_spell_cnt_24m)
    # remain in recovery_likely and eosb_limited — these describe spell-level
    # history that is still valid context, not current financial position.
    # GRR feedback (Sep 2026): ability must reflect current state.
    conds_recent = _build_ability_conditions("_recent", obs_date_only=True)
    result = _apply_ability_classifier_primary(
        result, conds_recent, state_col="a1_state"
    )

    # a1_payroll_stopped derives from the primary obs-date a1_state
    result = result.withColumn(
        "a1_payroll_stopped",
        F.when(
            F.col("a1_state").isin("ability_high", "ability_moderate")
            & (F.col("payroll_stopped_flag") == 1),
            F.lit(1),
        )
        .otherwise(F.lit(0))
        .cast("int"),
    )

    # pre_stress_flag intentionally broader than cond_trajectory_gradual:
    # rising utilisation alone is an early stress signal even before payment
    # performance deteriorates. cond_trajectory_gradual requires both.
    result = result.withColumn(
        "pre_stress_flag",
        F.when(
            (
                F.col("pay_ratio_slope").isNotNull()
                & (F.col("pay_ratio_slope") < _TAU_PAY_SLOPE_GRADUAL)
            )
            | (
                F.col("util_slope").isNotNull()
                & (F.col("util_slope") > _TAU_UTIL_SLOPE_GRADUAL)
            ),
            F.lit(1),
        )
        .otherwise(F.lit(0))
        .cast("int"),
    )

    # Fix 4: recovery_signal derived directly from cond_recovery_likely — no duplication
    result = result.withColumn(
        "recovery_signal",
        F.when(conds_recent["recovery_likely"], F.lit(1))
        .otherwise(F.lit(0))
        .cast("int"),
    )

    # Provenance: obs_date when ≥1 _recent income signal present; no_signal otherwise
    result = result.withColumn(
        "a1_provenance",
        F.when(
            F.coalesce(
                F.col("salary_months_h2_recent"),
                F.col("casa_inflow_cnt_h2_recent"),
                F.col("bureau_salary_present_6m_flag_recent"),
            ).isNotNull(),
            F.lit("obs_date"),
        ).otherwise(F.lit("no_signal")),
    ).withColumn(
        "a1_confidence",
        F.when(F.col("a1_state") == "ability_high", F.lit(0.9))
        .when(F.col("a1_state") == "ability_moderate", F.lit(0.7))
        .when(F.col("a1_state") == "ability_limited", F.lit(0.4))
        .otherwise(F.lit(0.0)),
    )

    # a1_income_source: obs-date-anchored _recent signals only
    result = result.withColumn(
        "a1_income_source",
        F.when(
            F.coalesce(F.col("salary_months_h2_recent"), F.lit(0))
            >= _TAU_SALARY_H2_MIN,
            F.lit("payroll"),
        )
        .when(
            F.col("bureau_salary_present_6m_flag_recent") == 1,
            F.lit("bureau_salary"),
        )
        .when(
            F.col("casa_inflow_cnt_h2_recent").isNotNull()
            & (F.col("casa_inflow_cnt_h2_recent") >= _TAU_CASA_INFLOW_H2_MIN),
            F.lit("casa_generic"),
        )
        .when(
            F.coalesce(F.col("ext_cc_payment_cnt_h2_recent"), F.lit(0)) >= 2,
            F.lit("ext_cc_payment"),
        )
        .otherwise(F.lit(None).cast("string")),
    )

    # CASA coverage ratio: obs-date balance vs obs-date outstanding (falls back to T0)
    _casa_bal_eff = F.coalesce(
        F.col("casa_eod_bal_h2_recent"), F.col("casa_eod_bal_h2")
    )
    _outstanding_eff = F.coalesce(
        F.col("cc_total_outstanding_recent"), F.col("cc_total_outstanding")
    )
    result = result.withColumn(
        "casa_coverage_ratio",
        F.when(
            _outstanding_eff.isNotNull() & (_outstanding_eff > 0),
            _casa_bal_eff / _outstanding_eff,
        ).otherwise(F.lit(None).cast("double")),
    )

    # DBR at scoring month (GRR Row 10): outstanding / monthly income at obs-date
    _income_recent = F.coalesce(
        F.col("salary_amt_last_recent"),
        F.col("bureau_salary_amt_last_recent"),
        F.col("casa_inflow_amt_h2_recent") / F.lit(3.0),
    )
    result = result.withColumn(
        "cc_outstanding_vs_income_recent",
        F.when(
            _outstanding_eff.isNotNull()
            & _income_recent.isNotNull()
            & (_income_recent > 0),
            _outstanding_eff / _income_recent,
        ).otherwise(F.lit(None).cast("double")),
    )

    result = _build_a1_output_select(result)
    enrichers.log_a1_stats(result)
    return result
