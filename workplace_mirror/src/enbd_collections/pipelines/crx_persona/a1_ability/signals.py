"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A1_ability_spec.md`` (GRR workbook A1_ability_20261022).

Observation dates are month ends. The window is W calendar months, the observation month
included (``_common.window_months``: 3 for 60–180, 6 for 180+): m1 = the observation
month … mW; "the prior window" is m(W+1)–m(2W). The builders read the observation base
and monthly ``(cif_id, month_end)`` feature tables, and return what the classifier
compares with its thresholds:

* income    — salary in each month: the larger of the internal credit and the bureau
              salary, a pull counting in its own month and the next (S14);
* liquidity — CASA average balance in each month, largest single external card payment;
* activity  — customer-initiated CASA movement in the window (the Unknown gate) and
              whether the customer holds a CASA with us at all;
* distress  — a cheque return, a direct-debit (DDS) return or a new bureau bounce in
              the window;
* EOSB      — a DCORE end-of-service result in the window (diagnostic only).

Features are per customer (CIF): every account of the customer counts, never the scored
account_id alone (an RL account_id is not a CASA account).
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import (
    GRAIN,
    left_join_all,
    lookback_floor,
    require_columns,
    window_agg,
    window_months,
)

# prm_casa_return_events reasons that count as distress; it also carries "RETURNS"
# (POS refunds).
CHEQUE_RETURN, DDS_RETURN = "CHEQUE RETURNS", "DDS Rejects/Reversal"
# feat_cif_casa_activity_monthly lanes that are money the customer moved (S11): third-
# party credits, transfers to others, cash, clearing, bill payments, card spend and
# paying their own credit card. Not: own-account wash, the bank recovering the
# customer's loan instalment, fees, interest, reversals, returns, group-internal and
# ambiguous rows.
CUSTOMER_LANES = ("economic", "card_spend", "card_payment")
# Months in which a CASA leg or a positive balance shows the customer holds a CASA
# with us (WM may fill missing balances with 0, so a zero balance proves nothing).
CASA_HELD_MONTHS = 12
EOSB = "EOSB"  # in a DCORE result name: end-of-service benefits expected / received


def _cifs(obs_base: DataFrame) -> DataFrame:
    """Observation rows with a CIF, ``cif_id`` as string (the features' type)."""
    return obs_base.filter(F.col("cif_id").isNotNull()).withColumn(
        "cif_id", F.col("cif_id").cast("string")
    )


def _month_index(date: Column) -> Column:
    """1 for the observation month, 2 for the one before, …"""
    obs_month = F.trunc(F.col("observation_date"), "month")
    return F.months_between(obs_month, F.trunc(date, "month")).cast("int") + 1


def _by_month(
    obs: DataFrame, series: DataFrame, value: str, prefix: str, months: int
) -> DataFrame:
    """Spread a ``(cif_id, month_end, value)`` series over ``{prefix}_m1 …
    _m{months}`` per observation (NULL where the month has no value)."""
    return (
        obs.select(*GRAIN, "cif_id")
        .join(series.select("cif_id", "month_end", value), on="cif_id")
        .withColumn("_k", _month_index(F.col("month_end")))
        .filter(F.col("_k").between(1, months))
        .groupBy(*GRAIN)
        .agg(
            *[
                F.max(F.when(F.col("_k") == i, F.col(value))).alias(f"{prefix}_m{i}")
                for i in range(1, months + 1)
            ]
        )
    )


def _in_window(obs: DataFrame, series: DataFrame, months: int, *aggs) -> DataFrame:
    """``aggs`` over the ``(cif_id, month_end, …)`` rows of the last ``months`` months."""
    return window_agg(obs, series, date_col="month_end", aggs=list(aggs), months=months)


# ── Income ────────────────────────────────────────────────────────────────────


def _loan_bureau_salary(obs_base: DataFrame, loan_features: DataFrame) -> DataFrame:
    """RL: the last salary credit reported by each loan's latest bureau pull
    (``feature_retail_loans``, one row per spine row), dated by the pull month.

    Pulls are rare (most accounts have one), so this rarely falls in the window.
    """
    require_columns(
        loan_features,
        ["account_id", "aecb_bureau_pull_date", "aecb_last_salary_credit_amount"],
        "feature_retail_loans",
    )
    cifs = _cifs(obs_base).select("account_id", "cif_id").distinct()
    return (
        loan_features.select(
            F.col("account_id").cast("string").alias("account_id"),
            F.last_day(F.to_date("aecb_bureau_pull_date")).alias("month_end"),
            F.col("aecb_last_salary_credit_amount")
            .cast("double")
            .alias("bureau_salary"),
        )
        .filter(F.col("month_end").isNotNull() & (F.col("bureau_salary") > 0))
        .join(cifs, on="account_id")
        .select("cif_id", "month_end", "bureau_salary")
    )


def _with_next_month(bureau: DataFrame) -> DataFrame:
    """One bureau salary per ``(cif_id, month_end)``: each pull's month, and the month
    after it unless that month has its own pull (never before a pull; pulls every 2
    months make a continuous series). A pull of 0 (salary account closed) ends the carry.
    """
    pulls = bureau.groupBy("cif_id", "month_end").agg(
        F.max("bureau_salary").alias("bureau_salary")
    )
    carried = pulls.select(
        "cif_id",
        F.last_day(F.add_months("month_end", 1)).alias("month_end"),
        F.col("bureau_salary").alias("_carried"),
    )
    return pulls.join(carried, on=["cif_id", "month_end"], how="full").select(
        "cif_id",
        "month_end",
        F.coalesce("bureau_salary", "_carried").alias("bureau_salary"),
    )


def build_income_signals(
    obs_base: DataFrame,
    internal_salary: DataFrame,
    bureau_salary: DataFrame,
    model_id: str,
    loan_features: DataFrame | None = None,
) -> DataFrame:
    """``income_m1 … income_m{2W}``: salary received per month — the larger of the
    internal salary (``feat_cif_internal_salary_monthly``) and the bureau salary
    (``feat_cif_bureau_salary_monthly``, carried one month forward); NULL: no salary that
    month. Also the largest month per source: ``internal_salary_w`` / ``bureau_salary_w`` in
    the window, ``internal_salary_prior`` in the prior window.

    ``loan_features`` (RL only): ``feature_retail_loans``, whose latest-pull bureau salary
    joins the bureau salary.
    """
    require_columns(
        internal_salary,
        ["cif_id", "month_end", "salary"],
        "feat_cif_internal_salary_monthly",
    )
    require_columns(
        bureau_salary,
        ["cif_id", "month_end", "bureau_salary"],
        "feat_cif_bureau_salary_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    since = lookback_floor(obs, 2 * w)
    internal = internal_salary.select(
        "cif_id",
        "month_end",
        F.col("salary").alias("amount"),
        F.lit("int").alias("src"),
    )
    bureau = bureau_salary.select("cif_id", "month_end", "bureau_salary")
    if loan_features is not None:
        bureau = bureau.unionByName(_loan_bureau_salary(obs_base, loan_features))
    sources = internal.unionByName(
        _with_next_month(bureau).select(
            "cif_id",
            "month_end",
            F.col("bureau_salary").alias("amount"),
            F.lit("bur").alias("src"),
        )
    ).filter(F.col("month_end") >= F.lit(since))
    monthly = sources.groupBy("cif_id", "month_end").agg(
        F.max("amount").alias("amount")
    )
    in_w = _month_index(F.col("month_end")) <= w
    internal_rows = F.col("src") == "int"
    return left_join_all(
        obs_base,
        [
            _by_month(obs, monthly, "amount", "income", 2 * w),
            _in_window(
                obs,
                sources,
                2 * w,
                F.max(F.when(internal_rows & in_w, F.col("amount"))).alias(
                    "internal_salary_w"
                ),
                F.max(F.when(~internal_rows & in_w, F.col("amount"))).alias(
                    "bureau_salary_w"
                ),
                F.max(F.when(internal_rows & ~in_w, F.col("amount"))).alias(
                    "internal_salary_prior"
                ),
            ),
        ],
    )


# ── Liquidity and activity ────────────────────────────────────────────────────


def build_liquidity_signals(
    obs_base: DataFrame,
    casa_balance: DataFrame,
    ext_card_payments: DataFrame,
    casa_activity: DataFrame,
    model_id: str,
) -> DataFrame:
    """``casa_m1 … casa_m{2W}`` (``feat_cif_casa_balance_monthly``),
    ``ext_card_payment_max`` (largest single payment to an external card in W),
    ``casa_active`` (1: a leg in ``CUSTOMER_LANES`` in W) and ``casa_held`` (1: any CASA
    leg or a positive balance in the last ``CASA_HELD_MONTHS`` months)."""
    require_columns(
        casa_balance,
        ["cif_id", "month_end", "casa_balance"],
        "feat_cif_casa_balance_monthly",
    )
    require_columns(
        ext_card_payments,
        ["cif_id", "month_end", "max_payment"],
        "feat_cif_ext_card_payment_monthly",
    )
    require_columns(
        casa_activity,
        ["cif_id", "month_end", "lane", "legs"],
        "feat_cif_casa_activity_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    customer = casa_activity.filter(F.col("lane").isin(*CUSTOMER_LANES))
    held = casa_activity.select("cif_id", "month_end").unionByName(
        casa_balance.filter(F.col("casa_balance") > 0).select("cif_id", "month_end")
    )
    return left_join_all(
        obs_base,
        [
            _by_month(obs, casa_balance, "casa_balance", "casa", 2 * w),
            _in_window(
                obs,
                ext_card_payments,
                w,
                F.max("max_payment").alias("ext_card_payment_max"),
            ),
            _in_window(obs, customer, w, F.max(F.lit(1)).alias("casa_active")),
            _in_window(obs, held, CASA_HELD_MONTHS, F.max(F.lit(1)).alias("casa_held")),
        ],
    ).fillna(0, subset=["casa_active", "casa_held"])


# ── Distress ──────────────────────────────────────────────────────────────────


def build_distress_signals(
    obs_base: DataFrame,
    returns: DataFrame,
    bureau_bounces: DataFrame,
    model_id: str,
    payment_order: DataFrame | None = None,
) -> DataFrame:
    """``distress_flag`` and its parts in the window, each 0 / 1:

    * ``distress_cheque`` / ``distress_dds`` — the bank's own returned cheques and DDS
      returns, across all the customer's CASA accounts (``feat_cif_returns_monthly``);
    * ``distress_bureau`` — a new bureau-reported bounce (``feat_cif_bureau_bounces_monthly``
      ``bounce_events``; a bounce repeated unchanged in later pulls counts once);
    * ``payment_order`` — prm_bureau_payment_order returns; not in PROD yet.

    Stops the run when the returns table starts after the earliest observation's window
    (it follows ``crx_persona.persona_start_date``; rebuilt for an older one otherwise).
    """
    require_columns(
        returns, ["cif_id", "month_end", "reason", "events"], "feat_cif_returns_monthly"
    )
    require_columns(
        bureau_bounces,
        ["cif_id", "month_end", "bounce_events"],
        "feat_cif_bureau_bounces_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    since = lookback_floor(obs, w)
    first = returns.agg(F.min("month_end")).first()[0]
    if first is None or first.isoformat()[:7] > since[:7]:
        raise ValueError(
            f"feat_cif_returns_monthly starts at {first}, but the observations need "
            f"returns from {since}: rerun casa_primary and casa_features after changing "
            "crx_persona.persona_start_date"
        )

    def flag(reason: str) -> Column:
        return F.max((F.col("reason") == reason).cast("int"))

    events = bureau_bounces.filter(F.col("bounce_events") > 0).select(
        "cif_id", "month_end", F.lit("BUREAU").alias("reason")
    )
    if payment_order is not None:
        require_columns(
            payment_order,
            ["cif_id", "return_date", "reason_code"],
            "prm_bureau_payment_order",
        )
        events = events.unionByName(
            payment_order.filter(F.col("reason_code").isNotNull()).select(
                F.col("cif_id").cast("string").alias("cif_id"),
                F.last_day(F.to_date("return_date")).alias("month_end"),
                F.lit("BUREAU").alias("reason"),
            )
        )
    events = events.unionByName(
        returns.filter(
            F.col("reason").isin(CHEQUE_RETURN, DDS_RETURN) & (F.col("events") > 0)
        ).select("cif_id", "month_end", "reason")
    )
    parts = ["distress_cheque", "distress_dds", "distress_bureau"]
    hits = _in_window(
        obs,
        events,
        w,
        flag(CHEQUE_RETURN).alias("distress_cheque"),
        flag(DDS_RETURN).alias("distress_dds"),
        flag("BUREAU").alias("distress_bureau"),
    )
    return (
        left_join_all(obs_base, [hits])
        .fillna(0, subset=parts)
        .withColumn("distress_flag", F.greatest(*[F.col(p) for p in parts]))
    )


# ── EOSB (diagnostic) ─────────────────────────────────────────────────────────


def build_eosb_signals(
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame, model_id: str
) -> DataFrame:
    """``eosb_flag``: 1 when a DCORE result on any of the customer's agreements names an
    end-of-service benefit (EOSB expected / awaited / received) in the window. A
    diagnostic only: it changes no level or state."""
    require_columns(
        followup,
        ["agreement_id", "action_ts", "result_name"],
        "dcore_prm_followup_outcomes",
    )
    require_columns(
        agreements, ["agreement_id", "cif_id"], "prm_dcore_account_agreements"
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    notes = (
        followup.filter(F.upper(F.col("result_name")).contains(EOSB))
        .select(
            F.col("agreement_id").cast("string").alias("agreement_id"),
            F.to_date("action_ts").alias("day"),
        )
        .join(
            agreements.select(
                F.col("agreement_id").cast("string").alias("agreement_id"),
                F.col("cif_id").cast("string").alias("cif_id"),
            ).distinct(),
            on="agreement_id",
        )
        .filter(F.col("day") >= F.lit(lookback_floor(obs, w)))
    )
    hits = window_agg(
        obs, notes, date_col="day", aggs=[F.max(F.lit(1)).alias("eosb_flag")], months=w
    )
    return left_join_all(obs_base, [hits]).fillna(0, subset=["eosb_flag"])
