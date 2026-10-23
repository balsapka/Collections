"""RL Departure Signature — 5-node pipeline (RL-A2-2, aligned to CC T06 order).

# pylint: disable=too-many-locals

Departure signature runs standalone BEFORE rl_a1_ability, mirroring the CC
T06→T07 execution order. Node 0 (build_rl_depart_spine) is also reused directly
by the rl_a4_spine pipeline (R14) to produce crx_rl_a4_spine's structural
projection, and Node 5 of rl_a1_ability reads this pipeline's output
(crx_rl_departure_signature) for eosb_like_flag.

Signals produced:
    travel_mcc_flag_h2       : H2 debit travel MCC hits from comp_financial_tran_repos_dly
    last_txn_foreign_flag    : FX leakage proxy (99.88% coverage)
    foreign_login_flag       : PIT foreign login from prm_digital_login_monthly
    casa_inflow_stop_gap_d   : days from last salary credit to M0 (Pass B)
    eosb_like_flag           : end-of-service benefit spike detection (Pass B)
    payroll_present_h2       : payroll present in H2 [T0-3m, T0) (Pass I)
    payroll_stopped_flag     : payroll was in H1 but absent in H2 (Pass I)

Output dataset: crx_rl_departure_signature at grain (account_id, observation_date).

Pipeline nodes:
    build_rl_depart_spine          → crx_rl_depart_spine           [Node 0]
    build_rl_depart_casa_signals   → crx_rl_depart_casa_signals    [Node 1]
    build_rl_depart_travel_mcc     → crx_rl_depart_travel_mcc      [Node 2]
    build_rl_depart_foreign_signals → crx_rl_depart_foreign_signals [Node 3]
    build_rl_departure_final       → crx_rl_departure_signature     [Node 4]

Window anchor: t0 (first delinquency onset month).
H2_blk = [add_months(trunc(t0,'month'), -3), trunc(t0,'month'))
"""

# pylint: disable=too-many-locals,duplicate-code

import logging
from datetime import date

from dateutil.relativedelta import relativedelta
from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.pipelines.crx_persona.cc_departure_signature.nodes import (
    _TRAVEL_KEYWORDS_RE,
    _TRAVEL_MCCS,
)

LOG = logging.getLogger(__name__)

_FX_COL = "ft_amt_cross_border_outflow_txn_in_last_0_2_months_sum"

# ── CASA salary / payroll constants (moved from rl_a4_class/nodes.py) ──────────
# FI-1 resolved 2026-08-21: sourced from wealth_management ENBD entity params
_SALARY_CODES = [
    "505",
    "506",
    "507",
    "503",
    "585",
    "586",
    "587",
    "588",
    "085",
    "086",
    "087",
    "088",
    "328",
    "828",
]
_SALARY_EXCLUDE_CODES = ["947", "LV3", "LV4"]
_TRAN_DC_CREDIT = "C"  # confirmed: WM ENBD entity config
_PAYROLL_HAS_COL = "payroll_flag"  # confirmed via t06d 2026-08-26

__all__ = [
    "build_rl_depart_spine",
    "build_rl_depart_casa_signals",
    "build_rl_depart_travel_mcc",
    "build_rl_depart_foreign_signals",
    "build_rl_departure_final",
]


# ── Node 0: build_rl_depart_spine ──────────────────────────────────────────────


def build_rl_depart_spine(
    rl_spine: DataFrame,
    crx_rl_spell_table: DataFrame,
    crx_persona: dict,
) -> DataFrame:
    """Build spell-scoped spine for departure signal computation (Node 0 of 5).

    Mirrors steps 1–4 of build_rl_a4_spine_projection WITHOUT the A4 label join,
    producing the raw spine grain used by all downstream departure nodes.

    Join logic (mirrors join_spine_to_spell pattern from _spine_utils.py):
        rl_spine["account_id"] == t0_table["account_id"]
        AND t0 <= observation_date
        AND spell_end IS NULL (always passes — open spell for RL)

    Args:
        rl_spine:           Model spine at (account_id, observation_date) grain.
        crx_rl_spell_table: T0 anchor. Required cols: account_id, spell_id, t0,
                            t0_censored_flag, spell_end, cif_id.
        crx_persona:        Persona param dict with persona_start_date /
                            persona_end_date.

    Returns:
        DataFrame at (account_id, observation_date) grain with cols::

            cif_id           string  NULL if no active non-censored spell
            account_id       string
            observation_date date
            spell_id         int     NULL if no active spell
            t0               date    NULL if no active spell
    """
    persona_start_date = crx_persona["persona_start_date"]
    persona_end_date = crx_persona["persona_end_date"]

    # Step 1: non-censored active spells (spell_end IS NULL = current episode)
    t0_filtered = crx_rl_spell_table.filter(
        (F.col("t0_censored_flag") == 0) & F.col("spell_end").isNull()
    ).select("account_id", "spell_id", "t0", "spell_end", "cif_id")

    # Step 2: left-join spine to spell info (all spine rows preserved)
    spine_for_join = (
        rl_spine.drop("cif_id") if "cif_id" in rl_spine.columns else rl_spine
    )
    spine_with_t0 = spine_for_join.join(t0_filtered, on="account_id", how="left")

    # Step 3: date filter — t0 <= observation_date (spell_end IS NULL always passes)
    spine_filtered = spine_with_t0.filter(
        F.col("t0").isNull() | (F.col("t0") <= F.col("observation_date"))
    )

    # Step 4: persona window filter
    start_dt = F.to_date(F.lit(persona_start_date))
    end_dt = F.to_date(F.lit(persona_end_date))
    result = spine_filtered.filter(
        (F.col("observation_date") >= start_dt) & (F.col("observation_date") <= end_dt)
    )

    n_rows = result.count()
    n_with_spell = result.filter(F.col("spell_id").isNotNull()).count()
    LOG.info(
        "build_rl_depart_spine [%s → %s]: %d spine rows | with active spell: %d (%.1f%%)",
        persona_start_date,
        persona_end_date,
        n_rows,
        n_with_spell,
        100.0 * n_with_spell / max(n_rows, 1),
    )

    return result.select(
        F.col("cif_id").cast("string"),
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
    )


# ── Node 1: build_rl_depart_casa_signals ───────────────────────────────────────


def build_rl_depart_casa_signals(  # pylint: disable=too-many-locals
    crx_rl_depart_spine: DataFrame,
    comp_financial_tran_repos_dly: DataFrame,
    feat_payroll_indicator: DataFrame,
    crx_persona: dict,
) -> DataFrame:
    """Compute CASA salary + payroll signals for departure signature (Node 1 of 5).

    Ports build_rl_a4_casa_signals (formerly rl_a4_class Node 1) to use
    crx_rl_depart_spine as the scope anchor. The spine is already filtered to
    persona-window non-censored active spells; no additional spell-table join needed.

    Sub-A (Pass B port — CASA salary inflow stop):
        Window: [M0-24m, M0) per account.
        Outputs: casa_inflow_stop_gap_d, eosb_like_flag.

    Sub-B (Pass I port — payroll indicator):
        Window: [M0-12m, M0), H2=[M0-3m, M0), H1=[M0-12m, M0-3m).
        Outputs: payroll_present_h2, payroll_stopped_flag.

    Args:
        crx_rl_depart_spine:           Node 0 output — (account_id, observation_date)
            grain scoped to persona window. Required cols: account_id, spell_id, t0,
            cif_id.
        comp_financial_tran_repos_dly: Raw CASA transactions (2.4B rows, R20).
        feat_payroll_indicator:        pri_monthly_payroll_indicator.
        crx_persona:                   Persona param dict — used for edp_load_date
                                       partition filter.

    Returns:
        DataFrame at grain (account_id, spell_id) with schema::

            account_id              string
            spell_id                int
            casa_inflow_stop_gap_d  double  NULL if no salary in [M0-24m, M0)
            eosb_like_flag          int     0/1/NULL
            payroll_present_h2      int     0/1/NULL
            payroll_stopped_flag    int     0/1/NULL
    """
    # Derive spell-grain base from the already-scoped spine
    spell_base = (
        crx_rl_depart_spine.filter(F.col("spell_id").isNotNull())
        .select("account_id", "spell_id", "t0", "cif_id")
        .dropDuplicates(["account_id", "spell_id"])
    )

    persona_start_date = crx_persona["persona_start_date"]
    LOG.info(
        "[%s → %s] build_rl_depart_casa_signals: %d accounts scoped",
        persona_start_date,
        crx_persona["persona_end_date"],
        spell_base.count(),
    )

    # Partition floor for efficiency — same as former build_rl_a4_casa_signals
    casa_floor = (
        date.fromisoformat(persona_start_date) - relativedelta(months=12)
    ).isoformat()
    comp_financial_tran_repos_dly = comp_financial_tran_repos_dly.filter(
        F.col("edp_load_date") >= F.lit(casa_floor)
    )

    payroll_floor_int = int(
        (date.fromisoformat(persona_start_date) - relativedelta(months=12))
        .isoformat()
        .replace("-", "")
    )
    feat_payroll_indicator = feat_payroll_indicator.filter(
        F.col("month_number") >= payroll_floor_int
    )

    account_cif = spell_base.select("account_id", "cif_id")
    t0_for_signals = spell_base.select("account_id", "t0")

    sub_a = _build_rl_pass_b(comp_financial_tran_repos_dly, account_cif, t0_for_signals)
    sub_b = _build_rl_pass_i(feat_payroll_indicator, account_cif, t0_for_signals)

    return (
        spell_base.select("account_id", "spell_id")
        .join(sub_a, on="account_id", how="left")
        .join(sub_b, on="account_id", how="left")
        .select(
            F.col("account_id").cast("string"),
            F.col("spell_id").cast("int"),
            F.col("casa_inflow_stop_gap_d").cast("double"),
            F.col("eosb_like_flag").cast("int"),
            F.col("payroll_present_h2").cast("int"),
            F.col("payroll_stopped_flag").cast("int"),
        )
    )


def _build_rl_pass_b(  # pylint: disable=too-many-locals
    comp_financial_tran_repos_dly: DataFrame,
    account_cif: DataFrame,  # (account_id, cif_id)
    t0_base: DataFrame,  # (account_id, t0)
) -> DataFrame:
    """CASA inflow stop signals — RL adaptation of CC _build_pass_b.

    Returns DataFrame at grain account_id:
        (account_id, casa_inflow_stop_gap_d, eosb_like_flag).

    Window: [M0-24m, M0). Grain: account_id.
    """
    _CASA_REQUIRED = [
        "cif_id",
        "tran_date",
        "tran_amt_aed",
        "tran_dc",
        "tran_particular_code",
        "tran_narration_1",
    ]
    casa_cols_lower = {c.lower() for c in comp_financial_tran_repos_dly.columns}
    missing = [c for c in _CASA_REQUIRED if c not in casa_cols_lower]

    if missing:
        LOG.warning(
            "RL Pass B [CASA]: missing columns %s in comp_financial_tran_repos_dly "
            "— emitting NULL for casa_inflow_stop_gap_d and eosb_like_flag",
            missing,
        )
        return (
            t0_base.select("account_id")
            .withColumn("casa_inflow_stop_gap_d", F.lit(None).cast("double"))
            .withColumn("eosb_like_flag", F.lit(None).cast("int"))
        )

    # R20: scope CASA to relevant CIF IDs BEFORE any date filter
    cif_scope = account_cif.select(
        F.col("cif_id").cast("string").alias("cif_id")
    ).distinct()

    casa_scoped = comp_financial_tran_repos_dly.select(
        "cif_id",
        "tran_date",
        "tran_amt_aed",
        "tran_dc",
        "tran_particular_code",
        "tran_narration_1",
    ).join(F.broadcast(cif_scope), on="cif_id", how="leftsemi")

    t0_cif = t0_base.join(
        account_cif.select("account_id", F.col("cif_id").cast("string")),
        on="account_id",
        how="left",
    )

    is_salary = (
        (F.col("tran_dc") == _TRAN_DC_CREDIT)
        & ~F.col("tran_particular_code").isin(_SALARY_EXCLUDE_CODES)
        & (
            F.col("tran_particular_code").isin(_SALARY_CODES)
            | F.upper(F.coalesce(F.col("tran_narration_1"), F.lit(""))).rlike(
                r"SALARY|PAYROLL|SALAR|INCENTIVE|BONUS|OVERTIME|COMMISSION|COMISS|SALBNK|SALABNK"
            )
        )
    )

    casa_w = (
        casa_scoped.join(t0_cif, on="cif_id", how="inner")
        .filter(
            (F.col("tran_dc") == _TRAN_DC_CREDIT)
            & (F.col("tran_date") >= F.add_months(F.trunc(F.col("t0"), "month"), -24))
            & (F.col("tran_date") < F.trunc(F.col("t0"), "month"))
        )
        .withColumn("is_salary", is_salary)
    )

    last_sal = (
        casa_w.filter(F.col("is_salary"))
        .groupBy("account_id", "t0")
        .agg(F.max("tran_date").alias("last_sal_date"))
        .withColumn(
            "casa_inflow_stop_gap_d",
            F.datediff(F.trunc(F.col("t0"), "month"), F.col("last_sal_date")).cast(
                "double"
            ),
        )
        .select("account_id", "casa_inflow_stop_gap_d")
    )

    monthly_sal = (
        casa_w.filter(F.col("is_salary"))
        .withColumn(
            "m_from_m0",
            F.floor(
                F.months_between(
                    F.trunc(F.col("t0"), "month"),
                    F.trunc(F.col("tran_date"), "month"),
                )
            ).cast("int"),
        )
        .groupBy("account_id", "m_from_m0")
        .agg(F.sum("tran_amt_aed").alias("monthly_sal_total"))
    )

    sal_median = (
        monthly_sal.filter((F.col("m_from_m0") >= 7) & (F.col("m_from_m0") <= 24))
        .groupBy("account_id")
        .agg(
            F.percentile_approx("monthly_sal_total", 0.5).alias("monthly_salary_median")
        )
    )

    recent_max = (
        casa_w.filter(
            F.col("is_salary")
            & (F.col("tran_date") >= F.add_months(F.trunc(F.col("t0"), "month"), -6))
        )
        .groupBy("account_id")
        .agg(F.max("tran_amt_aed").alias("max_sal_recent"))
    )

    eosb = (
        t0_base.select("account_id")
        .join(last_sal, on="account_id", how="left")
        .join(sal_median, on="account_id", how="left")
        .join(recent_max, on="account_id", how="left")
        .withColumn(
            "eosb_like_flag",
            F.when(F.col("monthly_salary_median").isNull(), F.lit(None).cast("int"))
            .when(
                F.col("max_sal_recent").isNotNull()
                & (F.col("monthly_salary_median") > 0)
                & (F.col("max_sal_recent") > 3.0 * F.col("monthly_salary_median"))
                & F.col("casa_inflow_stop_gap_d").isNotNull()
                & (F.col("casa_inflow_stop_gap_d") <= 90.0),
                F.lit(1),
            )
            .otherwise(F.lit(0)),
        )
        .select("account_id", "casa_inflow_stop_gap_d", "eosb_like_flag")
    )

    return eosb


def _build_rl_pass_i(
    feat_payroll_indicator: DataFrame,
    account_cif: DataFrame,  # (account_id, cif_id)
    t0_base: DataFrame,  # (account_id, t0)
) -> DataFrame:
    """Payroll presence and stop signals — RL adaptation of CC _build_pass_i.

    Returns DataFrame at grain account_id:
        (account_id, payroll_present_h2, payroll_stopped_flag).

    Window: [M0-12m, M0). H2 = m_from_m0 in [1, 3]; H1 = m_from_m0 in [4, 12].
    _PAYROLL_HAS_COL = 'payroll_flag' confirmed via t06d 2026-08-26.
    """
    _REQUIRED = ["cif_id", "month_number"]
    pay_cols_lower = {c.lower() for c in feat_payroll_indicator.columns}
    missing_base = [c for c in _REQUIRED if c not in pay_cols_lower]

    if missing_base:
        LOG.warning(
            "RL Pass I [payroll]: missing base columns %s in feat_payroll_indicator "
            "— emitting NULL for payroll_present_h2, payroll_stopped_flag",
            missing_base,
        )
        return (
            t0_base.select("account_id")
            .withColumn("payroll_present_h2", F.lit(None).cast("int"))
            .withColumn("payroll_stopped_flag", F.lit(None).cast("int"))
        )

    if _PAYROLL_HAS_COL not in pay_cols_lower:
        LOG.warning(
            "RL Pass I [payroll]: column '%s' absent in feat_payroll_indicator "
            "— emitting NULL for payroll_present_h2, payroll_stopped_flag",
            _PAYROLL_HAS_COL,
        )
        return (
            t0_base.select("account_id")
            .withColumn("payroll_present_h2", F.lit(None).cast("int"))
            .withColumn("payroll_stopped_flag", F.lit(None).cast("int"))
        )

    cif_scope = account_cif.select(
        F.col("cif_id").cast("string").alias("cif_id")
    ).distinct()

    pay_scoped = feat_payroll_indicator.select(
        F.col("cif_id").cast("string").alias("cif_id"),
        F.to_date(F.col("month_number"), "yyyyMMdd").alias("pay_month"),
        F.col(_PAYROLL_HAS_COL).cast("int").alias("_has_payroll"),
    ).join(F.broadcast(cif_scope), on="cif_id", how="leftsemi")

    t0_cif = t0_base.join(
        account_cif.select("account_id", F.col("cif_id").cast("string")),
        on="account_id",
        how="left",
    )

    pay_w = (
        pay_scoped.join(t0_cif, on="cif_id", how="inner")
        .filter(
            (F.col("pay_month") >= F.add_months(F.trunc(F.col("t0"), "month"), -12))
            & (F.col("pay_month") < F.trunc(F.col("t0"), "month"))
        )
        .withColumn(
            "m_from_m0",
            F.floor(
                F.months_between(
                    F.trunc(F.col("t0"), "month"),
                    F.col("pay_month"),
                )
            ).cast("int"),
        )
    )

    agg = pay_w.groupBy("account_id").agg(
        F.max(
            F.when(
                (F.col("m_from_m0") >= 1) & (F.col("m_from_m0") <= 3),
                F.col("_has_payroll"),
            )
        ).alias("_h2_max"),
        F.max(
            F.when(
                (F.col("m_from_m0") >= 4) & (F.col("m_from_m0") <= 12),
                F.col("_has_payroll"),
            )
        ).alias("_h1_max"),
        F.count(
            F.when((F.col("m_from_m0") >= 4) & (F.col("m_from_m0") <= 12), F.lit(1))
        ).alias("_h1_row_count"),
    )

    result = (
        agg.withColumn(
            "payroll_present_h2",
            F.when(
                F.col("_h2_max").isNotNull(), F.col("_h2_max").cast("int")
            ).otherwise(F.lit(None).cast("int")),
        )
        .withColumn(
            "payroll_stopped_flag",
            F.when(
                F.col("_h1_row_count").isNull() | (F.col("_h1_row_count") == 0),
                F.lit(None).cast("int"),
            )
            .when(
                (F.col("_h1_max") == 1) & (F.coalesce(F.col("_h2_max"), F.lit(0)) == 0),
                F.lit(1),
            )
            .otherwise(F.lit(0)),
        )
        .select("account_id", "payroll_present_h2", "payroll_stopped_flag")
    )

    return t0_base.select("account_id").join(result, on="account_id", how="left")


# ── Node 2: build_rl_depart_travel_mcc ─────────────────────────────────────────


def build_rl_depart_travel_mcc(
    crx_rl_depart_spine: DataFrame,
    comp_financial_tran_repos_dly: DataFrame,
) -> DataFrame:
    """Derive travel_mcc_flag_h2 from CASA debit transactions (Node 2 of 5).

    Source: comp_financial_tran_repos_dly.merchant_category (4-digit MCC).
    ~50% populated on POS/debit rows; ~0% on credit-only rows.

    Window: H2_blk = [add_months(trunc(t0,'month'), -3), trunc(t0,'month')).
    Filter: tran_dc = 'D' (debit side only).
    Travel detection: merchant_category.cast(int).isin(_TRAVEL_MCCS) OR
        _TRAVEL_KEYWORDS_RE regex on merchant_name (keyword fallback).

    Null semantics:
        1    — any H2 debit travel hit
        0    — H2 debits exist but none match travel criteria
        NULL — no H2 debit transactions found (not coalesced here; coalesced to 0 in Node 4)

    R20 compliance: CIF-level leftsemi scope applied before any date filter.

    Args:
        crx_rl_depart_spine:           Node 0 output at (account_id, observation_date).
            Required cols: account_id, spell_id, t0, cif_id.
        comp_financial_tran_repos_dly: Raw CASA/debit transaction table.
            Required cols: cif_id, tran_date, tran_dc, merchant_category.
            Optional col: merchant_name (keyword fallback).

    Returns:
        DataFrame at (account_id, observation_date) grain with travel_mcc_flag_h2.
    """
    casa_cols_lower = {c.lower() for c in comp_financial_tran_repos_dly.columns}
    _REQUIRED = ["cif_id", "tran_date", "tran_dc"]

    missing = [c for c in _REQUIRED if c not in casa_cols_lower]
    has_mcc = "merchant_category" in casa_cols_lower
    has_name = "merchant_name" in casa_cols_lower

    if missing or not has_mcc:
        if missing:
            LOG.warning(
                "build_rl_depart_travel_mcc: comp_financial_tran_repos_dly missing columns "
                "%s — travel_mcc_flag_h2 = NULL for all rows.",
                missing,
            )
        else:
            LOG.warning(
                "build_rl_depart_travel_mcc: merchant_category absent from "
                "comp_financial_tran_repos_dly — travel_mcc_flag_h2 = NULL for all rows."
            )
        return crx_rl_depart_spine.select("account_id", "observation_date").withColumn(
            "travel_mcc_flag_h2", F.lit(None).cast("int")
        )

    # ── Account-level scope anchor ─────────────────────────────────────────────
    spell_base = crx_rl_depart_spine.select(
        "account_id", "spell_id", "t0", "cif_id"
    ).dropDuplicates(["account_id", "spell_id"])

    cif_scope = spell_base.select(
        F.col("cif_id").cast("string").alias("cif_id")
    ).distinct()

    # R20 scope: leftsemi before date filter
    select_exprs = [
        F.col("cif_id").cast("string").alias("cif_id"),
        F.col("tran_date").cast("date").alias("tran_date"),
        F.col("tran_dc").cast("string").alias("tran_dc"),
        F.col("merchant_category").cast("string").alias("merchant_category"),
    ]
    if has_name:
        select_exprs.append(
            F.col("merchant_name").cast("string").alias("merchant_name")
        )
    else:
        select_exprs.append(F.lit(None).cast("string").alias("merchant_name"))

    casa_scoped = comp_financial_tran_repos_dly.select(*select_exprs).join(
        F.broadcast(cif_scope), on="cif_id", how="leftsemi"
    )

    # ── Join to spell base ─────────────────────────────────────────────────────
    casa_spell = casa_scoped.join(
        spell_base.select(
            "account_id",
            "spell_id",
            "t0",
            F.col("cif_id").cast("string").alias("_cif"),
        ),
        on=(casa_scoped["cif_id"] == F.col("_cif")),
        how="inner",
    ).filter(
        (F.col("tran_dc") == "D")
        & (F.col("tran_date") >= F.add_months(F.trunc(F.col("t0"), "month"), -3))
        & (F.col("tran_date") < F.trunc(F.col("t0"), "month"))
    )

    # Travel detection: MCC primary + keyword fallback
    mcc_int = F.col("merchant_category").cast("int")
    is_travel_mcc = mcc_int.isNotNull() & mcc_int.isin(_TRAVEL_MCCS)
    is_travel_kw = F.upper(F.coalesce(F.col("merchant_name"), F.lit(""))).rlike(
        _TRAVEL_KEYWORDS_RE
    )
    is_travel = is_travel_mcc | is_travel_kw

    agg = casa_spell.groupBy("account_id", "spell_id").agg(
        F.max(F.when(is_travel, F.lit(1)).otherwise(F.lit(0))).alias(
            "travel_mcc_flag_h2"
        )
    )

    # Expand to all observation dates via spine join
    spine_obs = crx_rl_depart_spine.select("account_id", "observation_date", "spell_id")
    result = spine_obs.join(agg, on=["account_id", "spell_id"], how="left").select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("travel_mcc_flag_h2").cast("int"),
    )

    n_accounts = spell_base.count()
    n_flagged = agg.filter(F.col("travel_mcc_flag_h2") == 1).count()
    n_null = (
        result.select("account_id")
        .dropDuplicates()
        .join(
            agg.select("account_id"),
            on="account_id",
            how="leftanti",
        )
        .count()
    )
    LOG.info(
        "build_rl_depart_travel_mcc: %d accounts | travel_hit: %d (%.1f%%) | "
        "no_h2_debits (NULL): %d (%.1f%%)",
        n_accounts,
        n_flagged,
        100.0 * n_flagged / max(n_accounts, 1),
        n_null,
        100.0 * n_null / max(n_accounts, 1),
    )

    return result


# ── Node 3: build_rl_depart_foreign_signals ────────────────────────────────────


def build_rl_depart_foreign_signals(  # pylint: disable=too-many-locals
    crx_rl_depart_spine: DataFrame,
    feat_fx_leakage: DataFrame,
    prm_digital_login_monthly: DataFrame,
) -> DataFrame:
    """Derive last_txn_foreign_flag and foreign_login_flag (Node 3 of 5).

    last_txn_foreign_flag:
        FX leakage proxy — same logic as former RL A2 Node 1.
        Account-grain join at T0 month; broadcast to all observation dates.
        Source: feat_fx_leakage (fea_monthly_agg_fx_leakage).
        flag=1 if ft_amt_cross_border_outflow_txn_in_last_0_2_months_sum > 0 at T0.

    foreign_login_flag:
        PIT join per (account_id, observation_date).
        Most recent login month <= trunc(observation_date, 'month').
        Extracts last_login_foreign_flag from prm_digital_login_monthly.
        Same source and semantics as CC Pass J.

    Args:
        crx_rl_depart_spine:       Node 0 output at (account_id, observation_date).
            Required cols: account_id, observation_date, spell_id, t0, cif_id.
        feat_fx_leakage:           fea_monthly_agg_fx_leakage.
            Required cols: cif_id, month_number, _FX_COL.
        prm_digital_login_monthly: Monthly OMB login aggregation.
            Required cols: cif_id, month_number, last_login_foreign_flag.

    Returns:
        DataFrame at (account_id, observation_date) grain with:
            last_txn_foreign_flag   (int) 0/1
            foreign_login_flag      (int) 0/1/NULL
    """
    # ── Part A: last_txn_foreign_flag ──────────────────────────────────────────
    spell_base = crx_rl_depart_spine.select(
        "account_id", "spell_id", "t0", "cif_id"
    ).dropDuplicates(["account_id", "spell_id"])

    _required_fx = {"cif_id", "month_number", _FX_COL}
    if not _required_fx.issubset({c.lower() for c in feat_fx_leakage.columns}):
        missing = _required_fx - {c.lower() for c in feat_fx_leakage.columns}
        LOG.warning(
            "build_rl_depart_foreign_signals: feat_fx_leakage missing %s "
            "— last_txn_foreign_flag = 0 for all rows.",
            missing,
        )
        fx_flag_by_account = spell_base.select("account_id", "spell_id").withColumn(
            "last_txn_foreign_flag", F.lit(0).cast("int")
        )
    else:
        fx_dated = feat_fx_leakage.select(
            F.col("cif_id").cast("string").alias("_fx_cif"),
            F.to_date(F.col("month_number").cast("string"), "yyyyMMdd").alias(
                "_fx_month"
            ),
            F.col(_FX_COL).alias("_fx_amt"),
        )

        joined_fx = spell_base.join(
            fx_dated,
            on=(
                (spell_base["cif_id"].cast("string") == fx_dated["_fx_cif"])
                & (
                    F.trunc(fx_dated["_fx_month"], "month")
                    == F.trunc(spell_base["t0"], "month")
                )
            ),
            how="left",
        ).withColumn(
            "last_txn_foreign_flag",
            F.coalesce(
                F.when(F.col("_fx_amt") > 0, F.lit(1)).otherwise(F.lit(0)),
                F.lit(0),
            ).cast("int"),
        )

        fx_flag_by_account = joined_fx.select(
            "account_id", "spell_id", "last_txn_foreign_flag"
        ).dropDuplicates(["account_id", "spell_id"])

        n_fx = fx_flag_by_account.count()
        n_fx_flagged = fx_flag_by_account.filter(
            F.col("last_txn_foreign_flag") == 1
        ).count()
        LOG.info(
            "build_rl_depart_foreign_signals: FX — %d accounts | "
            "last_txn_foreign_flag=1: %d (%.1f%%)",
            n_fx,
            n_fx_flagged,
            100.0 * n_fx_flagged / max(n_fx, 1),
        )

    # Broadcast fx flag to all observation dates
    spine_obs = crx_rl_depart_spine.select(
        "account_id", "observation_date", "spell_id", "cif_id"
    )
    with_fx = spine_obs.join(
        fx_flag_by_account, on=["account_id", "spell_id"], how="left"
    ).withColumn(
        "last_txn_foreign_flag",
        F.coalesce(F.col("last_txn_foreign_flag"), F.lit(0)).cast("int"),
    )

    # ── Part B: foreign_login_flag ─────────────────────────────────────────────
    _required_login = {"cif_id", "month_number", "last_login_foreign_flag"}
    login_cols_lower = {c.lower() for c in prm_digital_login_monthly.columns}
    missing_login = [c for c in _required_login if c not in login_cols_lower]

    if missing_login:
        LOG.warning(
            "build_rl_depart_foreign_signals: prm_digital_login_monthly missing %s "
            "— foreign_login_flag = 0 for all rows.",
            missing_login,
        )
        result = with_fx.select(
            F.col("account_id").cast("string"),
            F.col("observation_date").cast("date"),
            F.col("last_txn_foreign_flag").cast("int"),
            F.lit(0).cast("int").alias("foreign_login_flag"),
        )
        return result

    cif_scope = spine_obs.select(
        F.col("cif_id").cast("string").alias("cif_id")
    ).distinct()

    login_scoped = prm_digital_login_monthly.select(
        F.col("cif_id").cast("string").alias("cif_id"),
        F.to_date(F.col("month_number").cast("string"), "yyyyMMdd").alias(
            "login_month"
        ),
        F.col("last_login_foreign_flag").cast("int").alias("_foreign_flag"),
    ).join(F.broadcast(cif_scope), on="cif_id", how="leftsemi")

    # PIT join: all login months <= trunc(observation_date, 'month')
    login_w = with_fx.join(
        login_scoped,
        on=(with_fx["cif_id"].cast("string") == login_scoped["cif_id"]),
        how="left",
    ).filter(
        F.col("login_month").isNull()
        | (F.col("login_month") <= F.trunc(F.col("observation_date"), "month"))
    )

    # Most recent login per (account_id, observation_date)
    w_recent = Window.partitionBy("account_id", "observation_date").orderBy(
        F.col("login_month").desc_nulls_last()
    )

    result = (
        login_w.withColumn("_rn", F.row_number().over(w_recent))
        .filter(F.col("_rn") == 1)
        .select(
            F.col("account_id").cast("string"),
            F.col("observation_date").cast("date"),
            F.col("last_txn_foreign_flag").cast("int"),
            F.col("_foreign_flag").cast("int").alias("foreign_login_flag"),
        )
    )

    n_obs = result.count()
    n_login_flagged = result.filter(F.col("foreign_login_flag") == 1).count()
    n_login_null = result.filter(F.col("foreign_login_flag").isNull()).count()
    LOG.info(
        "build_rl_depart_foreign_signals: login — %d obs rows | "
        "foreign_login_flag=1: %d (%.1f%%) | NULL: %d (%.1f%%)",
        n_obs,
        n_login_flagged,
        100.0 * n_login_flagged / max(n_obs, 1),
        n_login_null,
        100.0 * n_login_null / max(n_obs, 1),
    )

    return result


# ── Node 4: build_rl_departure_final ───────────────────────────────────────────


def build_rl_departure_final(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    crx_rl_depart_spine: DataFrame,
    crx_rl_depart_travel_mcc: DataFrame,
    crx_rl_depart_foreign_signals: DataFrame,
    crx_rl_depart_casa_signals: DataFrame,
) -> DataFrame:
    """Assemble crx_rl_departure_signature (Node 4 of 5).

    Joins Nodes 1–3 outputs to the spine. CASA signals sourced from Node 1
    (crx_rl_depart_casa_signals) at spell grain, broadcast to obs-date rows.

    Coalesce defaults applied here (not in upstream nodes to preserve NULL
    semantics for diagnostic purposes):
        travel_mcc_flag_h2   → 0 on NULL (no H2 debits)
        foreign_login_flag   → 0 on NULL (no login history)

    Args:
        crx_rl_depart_spine:           Node 0 output at (account_id, observation_date).
        crx_rl_depart_travel_mcc:      Node 2 output — travel_mcc_flag_h2.
        crx_rl_depart_foreign_signals: Node 3 output — last_txn_foreign_flag,
                                       foreign_login_flag.
        crx_rl_depart_casa_signals:    Node 1 output at (account_id, spell_id) grain.
                                       Cols: casa_inflow_stop_gap_d, eosb_like_flag,
                                       payroll_present_h2, payroll_stopped_flag.

    Returns:
        crx_rl_departure_signature at (account_id, observation_date) grain::

            account_id              string
            observation_date        date
            spell_id                int
            travel_mcc_flag_h2      int     0/1 (coalesced, no NULL)
            last_txn_foreign_flag   int     0/1
            foreign_login_flag      int     0/1 (coalesced, no NULL)
            casa_inflow_stop_gap_d  double  NULL if no salary inflow in [M0-24m, M0)
            eosb_like_flag          int     0/1/NULL
            payroll_present_h2      int     0/1/NULL
            payroll_stopped_flag    int     0/1/NULL
    """
    spine = crx_rl_depart_spine.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("spell_id").cast("int"),
    )

    # CASA signals are at (account_id, spell_id) grain — broadcast to obs-date rows
    _casa_cols = {c.lower() for c in crx_rl_depart_casa_signals.columns}
    _expected = {
        "casa_inflow_stop_gap_d",
        "eosb_like_flag",
        "payroll_present_h2",
        "payroll_stopped_flag",
    }
    _missing_casa = _expected - _casa_cols
    if _missing_casa:
        LOG.warning(
            "build_rl_departure_final: crx_rl_depart_casa_signals missing %s "
            "— emitting NULL for missing cols.",
            _missing_casa,
        )

    casa_src = crx_rl_depart_casa_signals.select(
        F.col("account_id").cast("string"),
        F.col("spell_id").cast("int"),
        (
            F.col("casa_inflow_stop_gap_d").cast("double")
            if "casa_inflow_stop_gap_d" in _casa_cols
            else F.lit(None).cast("double").alias("casa_inflow_stop_gap_d")
        ),
        (
            F.col("eosb_like_flag").cast("int")
            if "eosb_like_flag" in _casa_cols
            else F.lit(None).cast("int").alias("eosb_like_flag")
        ),
        (
            F.col("payroll_present_h2").cast("int")
            if "payroll_present_h2" in _casa_cols
            else F.lit(None).cast("int").alias("payroll_present_h2")
        ),
        (
            F.col("payroll_stopped_flag").cast("int")
            if "payroll_stopped_flag" in _casa_cols
            else F.lit(None).cast("int").alias("payroll_stopped_flag")
        ),
    )

    result = (
        spine.join(
            crx_rl_depart_travel_mcc.select(
                "account_id", "observation_date", "travel_mcc_flag_h2"
            ),
            on=["account_id", "observation_date"],
            how="left",
        )
        .join(
            crx_rl_depart_foreign_signals.select(
                "account_id",
                "observation_date",
                "last_txn_foreign_flag",
                "foreign_login_flag",
            ),
            on=["account_id", "observation_date"],
            how="left",
        )
        .join(
            casa_src,
            on=["account_id", "spell_id"],
            how="left",
        )
    )

    # Apply coalesce defaults
    result = result.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("spell_id").cast("int"),
        F.coalesce(F.col("travel_mcc_flag_h2"), F.lit(0))
        .cast("int")
        .alias("travel_mcc_flag_h2"),
        F.coalesce(F.col("last_txn_foreign_flag"), F.lit(0))
        .cast("int")
        .alias("last_txn_foreign_flag"),
        F.coalesce(F.col("foreign_login_flag"), F.lit(0))
        .cast("int")
        .alias("foreign_login_flag"),
        F.col("casa_inflow_stop_gap_d").cast("double"),
        F.col("eosb_like_flag").cast("int"),
        F.col("payroll_present_h2").cast("int"),
        F.col("payroll_stopped_flag").cast("int"),
    )

    n_rows = result.count()
    n_travel = result.filter(F.col("travel_mcc_flag_h2") == 1).count()
    n_foreign_login = result.filter(F.col("foreign_login_flag") == 1).count()
    n_casa = result.filter(F.col("casa_inflow_stop_gap_d").isNotNull()).count()
    n_payroll_stopped = result.filter(F.col("payroll_stopped_flag") == 1).count()
    LOG.info(
        "build_rl_departure_final: %d rows | travel_mcc_flag_h2=1: %d (%.1f%%) | "
        "foreign_login_flag=1: %d (%.1f%%) | casa_inflow_stop_gap_d non-null: %d (%.1f%%) | "
        "payroll_stopped_flag=1: %d (%.1f%%)",
        n_rows,
        n_travel,
        100.0 * n_travel / max(n_rows, 1),
        n_foreign_login,
        100.0 * n_foreign_login / max(n_rows, 1),
        n_casa,
        100.0 * n_casa / max(n_rows, 1),
        n_payroll_stopped,
        100.0 * n_payroll_stopped / max(n_rows, 1),
    )

    return result
