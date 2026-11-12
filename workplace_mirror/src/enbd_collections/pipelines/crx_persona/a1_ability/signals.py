"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A1_ability_family_rule.md`` (income: S2–S16 of
``A1_ability_spec.md``).

Observation dates are month ends. The window is W calendar months, the observation month
included (``_common.window_months``: 3 for 60–180, 6 for 180+): m1 = the observation
month … mW; "the prior window" is m(W+1)–m(2W). The builders read the observation base
and monthly ``(cif_id, month_end)`` feature tables, and return what the classifier
compares with its thresholds:

* income   — salary in each month: the larger of the internal credit and the bureau
             salary, a bureau row counting in its own month and the next (S14);
* CASA     — money in and money out per month (the counted flow classes of
             ``feat_cif_casa_flows_monthly``), the CASA average balance per month, whether
             any counted leg falls in the window (the Unknown gate) and whether the
             customer holds a CASA with us at all;
* products — the customer's other products with us at the observation month (F4);
* distress — a cheque return, a direct-debit (DDS) return or a new bureau bounce in
             the window;
* EOSB     — a DCORE end-of-service result in the window (diagnostic only).

Features are per customer (CIF): every account of the customer counts, never the scored
account_id alone (an RL account_id is not a CASA account).
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.features.casa.feat_cif_casa import (
    MONEY_IN_CLASSES,
    MONEY_OUT_CLASSES,
)
from enbd_collections.nodes.features.products.feat_cif_cross_product import (
    COLUMNS as CROSS_PRODUCT_COLUMNS,
)

from .._common import (
    GRAIN,
    left_join_all,
    lookback_floor,
    require_columns,
    window_agg,
    window_months,
    window_start,
)

# prm_casa_return_events reasons that count as distress; it also carries "RETURNS"
# (POS refunds).
CHEQUE_RETURN, DDS_RETURN = "CHEQUE RETURNS", "DDS Rejects/Reversal"
REASON_BUREAU_BOUNCE = "BUREAU"  # the reason given to bureau-reported bounces (S15)
# Months in which a CASA leg or a positive balance shows the customer holds a CASA
# with us (WM may fill missing balances with 0, so a zero balance proves nothing).
CASA_HELD_MONTHS = 12
EOSB = "EOSB"  # in a DCORE result name: end-of-service benefits expected / received
# Which source a salary row comes from, in ``build_income_signals``.
SOURCE_INTERNAL, SOURCE_BUREAU = "int", "bur"


def _cifs(obs_base: DataFrame) -> DataFrame:
    """Observation rows with a CIF, ``cif_id`` as string (the features' type)."""
    return obs_base.filter(F.col("cif_id").isNotNull()).withColumn(
        "cif_id", F.col("cif_id").cast("string")
    )


def _month_index(date: Column) -> Column:
    """1 for the observation month, 2 for the one before, …"""
    obs_month = F.trunc(F.col("observation_date"), "month")
    return F.months_between(obs_month, F.trunc(date, "month")).cast("int") + 1


def _by_month(value: str, prefix: str, months: int) -> list[Column]:
    """Aggregates spreading ``value`` of a ``(cif_id, month_end, …)`` series over
    ``{prefix}_m1 … _m{months}`` per observation (NULL where the month has no value)."""
    k = _month_index(F.col("month_end"))
    return [
        F.max(F.when(k == i, F.col(value))).alias(f"{prefix}_m{i}")
        for i in range(1, months + 1)
    ]


def _in_window(obs: DataFrame, series: DataFrame, months: int, *aggs) -> DataFrame:
    """``aggs`` over the ``(cif_id, month_end, …)`` rows of the last ``months`` months."""
    return window_agg(obs, series, date_col="month_end", aggs=list(aggs), months=months)


# ── Income ────────────────────────────────────────────────────────────────────


def _with_next_month(bureau: DataFrame) -> DataFrame:
    """One bureau salary per ``(cif_id, month_end)``: each row's month, and the month
    after it unless that month has its own row (never before a row; pulls every 2 months
    make a continuous series). A row of 0 ends the carry.
    """
    none = F.lit(None).cast("double")
    own = bureau.select("cif_id", "month_end", "bureau_salary", none.alias("_carried"))
    carried = bureau.select(
        "cif_id",
        F.last_day(F.add_months("month_end", 1)).alias("month_end"),
        none.alias("bureau_salary"),
        F.col("bureau_salary").alias("_carried"),
    )
    return (
        own.unionByName(carried)
        .groupBy("cif_id", "month_end")
        .agg(
            F.coalesce(F.max("bureau_salary"), F.max("_carried")).alias("bureau_salary")
        )
    )


def build_income_signals(
    obs_base: DataFrame,
    internal_salary: DataFrame,
    bureau_salary: DataFrame,
    model_id: str,
) -> DataFrame:
    """``income_m1 … income_m{2W}`` (S3, S12, S14): salary received per month — the
    larger of the internal salary (``feat_cif_internal_salary_monthly``) and the bureau
    salary (``feat_cif_bureau_salary_monthly``, carried one month forward); NULL: no
    salary that month. Also the largest month per source: ``internal_salary_w`` /
    ``bureau_salary_w`` in the window, ``internal_salary_prior`` in the prior window.
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
        F.lit(SOURCE_INTERNAL).alias("src"),
    )
    bureau = bureau_salary.select("cif_id", "month_end", "bureau_salary")
    sources = internal.unionByName(
        _with_next_month(bureau).select(
            "cif_id",
            "month_end",
            F.col("bureau_salary").alias("amount"),
            F.lit(SOURCE_BUREAU).alias("src"),
        )
    ).filter(F.col("month_end") >= F.lit(since))
    in_w = _month_index(F.col("month_end")) <= w
    internal_rows = F.col("src") == SOURCE_INTERNAL
    return left_join_all(
        obs_base,
        [
            _in_window(
                obs,
                sources,
                2 * w,
                *_by_month("amount", "income", 2 * w),
                F.max(F.when(internal_rows & in_w, F.col("amount"))).alias(
                    "internal_salary_w"
                ),
                F.max(F.when(~internal_rows & in_w, F.col("amount"))).alias(
                    "bureau_salary_w"
                ),
                F.max(F.when(internal_rows & ~in_w, F.col("amount"))).alias(
                    "internal_salary_prior"
                ),
            )
        ],
    )


# ── CASA: money in / out / held ──────────────────────────────────────────────


def _casa_rows(casa_flows: DataFrame, casa_balance: DataFrame) -> DataFrame:
    """CASA rows of both features by ``(cif_id, month_end)``: ``money_in`` / ``money_out``
    (AED of the counted classes; NULL on a balance row), ``balance`` (NULL on a flow row),
    ``counted`` (1: a counted leg) and ``held`` (1: any leg, or a positive balance)."""
    null = F.lit(None).cast("double")
    counted_in = F.col("flow_class").isin(*MONEY_IN_CLASSES)
    counted_out = F.col("flow_class").isin(*MONEY_OUT_CLASSES)
    flows = casa_flows.groupBy("cif_id", "month_end").agg(
        F.sum(F.when(counted_in, F.col("credit_aed"))).alias("money_in"),
        F.sum(F.when(counted_out, F.col("debit_aed"))).alias("money_out"),
        F.max((counted_in | counted_out).cast("int")).alias("counted"),
    )
    return flows.select(
        "cif_id",
        "month_end",
        "money_in",
        "money_out",
        null.alias("balance"),
        "counted",
        F.lit(1).alias("held"),
    ).unionByName(
        casa_balance.select(
            "cif_id",
            "month_end",
            null.alias("money_in"),
            null.alias("money_out"),
            F.col("casa_balance").cast("double").alias("balance"),
            F.lit(0).alias("counted"),
            (F.col("casa_balance") > 0).cast("int").alias("held"),
        )
    )


def build_casa_signals(
    obs_base: DataFrame,
    casa_balance: DataFrame,
    casa_flows: DataFrame,
    model_id: str,
    *,
    crx_persona: dict,
) -> DataFrame:
    """``in_m1 … in_mW`` / ``out_m1 … out_mW`` (money in / out per month, the counted
    classes of ``feat_cif_casa_flows_monthly``; salary credits are income, not money in),
    ``casa_m1 … casa_m{2W}`` (``feat_cif_casa_balance_monthly``), ``casa_active`` (a
    counted leg in W: the Unknown gate) and ``casa_held`` (any CASA leg or a positive
    balance in the last ``CASA_HELD_MONTHS`` months). CASA means the scheme-code accounts
    of S16."""
    require_columns(
        casa_balance,
        ["cif_id", "month_end", "casa_balance"],
        "feat_cif_casa_balance_monthly",
    )
    require_columns(
        casa_flows,
        ["cif_id", "month_end", "flow_class", "credit_aed", "debit_aed"],
        "feat_cif_casa_flows_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    # The obs base starts in the persona start month: no window reaches older rows.
    first = F.lit(str(crx_persona["persona_start_date"])).cast("date")
    rows = _casa_rows(casa_flows, casa_balance).filter(
        F.col("month_end") >= window_start(CASA_HELD_MONTHS, first)
    )
    in_w = _month_index(F.col("month_end")) <= w
    signals = left_join_all(
        obs_base,
        [
            _in_window(
                obs,
                rows,
                CASA_HELD_MONTHS,
                *_by_month("money_in", "in", w),
                *_by_month("money_out", "out", w),
                *_by_month("balance", "casa", 2 * w),
                F.max(F.when((F.col("counted") == 1) & in_w, F.lit(1))).alias(
                    "casa_active"
                ),
                F.max(F.when(F.col("held") == 1, F.lit(1))).alias("casa_held"),
            )
        ],
    )
    return signals.fillna(0, subset=["casa_active", "casa_held"]).select(
        *GRAIN,
        *[f"in_m{i}" for i in range(1, w + 1)],
        *[f"out_m{i}" for i in range(1, w + 1)],
        *[f"casa_m{i}" for i in range(1, 2 * w + 1)],
        "casa_active",
        "casa_held",
    )


# ── Cross-product (F4) ────────────────────────────────────────────────────────


def build_cross_product_signals(obs_base: DataFrame, products: DataFrame) -> DataFrame:
    """At the observation month end, the customer's other products with us
    (``feat_cif_cross_product_monthly``), the scored account itself left out:
    ``xp_assets_aed`` (deposits + investments + WM), ``xp_instalment_max`` (the largest
    instalment / minimum due of another credit product that is current), ``xp_current``
    (1: another credit product is current) and ``xp_holding`` (1: any asset above 0)."""
    require_columns(
        products, list(CROSS_PRODUCT_COLUMNS), "feat_cif_cross_product_monthly"
    )
    obs = _cifs(obs_base).select(*GRAIN, "cif_id")
    asset = F.col("product_type").isin("deposit", "investment", "wm")
    current_credit = F.col("product_type").isin("card", "loan") & (
        F.coalesce(F.col("is_current").cast("int"), F.lit(0)) == 1
    )
    rows = (
        obs.join(
            products.select(
                F.col("cif_id").cast("string").alias("cif_id"),
                F.col("month_end").alias("observation_date"),
                F.col("product_account_id").cast("string").alias("_acct"),
                "product_type",
                F.col("balance_aed").cast("double").alias("_bal"),
                "is_current",
                F.col("instalment_aed").cast("double").alias("_inst"),
            ),
            on=["cif_id", "observation_date"],
        )
        .filter(F.col("_acct") != F.col("account_id").cast("string"))
        .groupBy(*GRAIN)
        .agg(
            F.sum(F.when(asset, F.col("_bal"))).alias("xp_assets_aed"),
            F.max(F.when(current_credit, F.col("_inst"))).alias("xp_instalment_max"),
            F.max(current_credit.cast("int")).alias("xp_current"),
            F.max((asset & (F.col("_bal") > 0)).cast("int")).alias("xp_holding"),
        )
    )
    return left_join_all(obs_base, [rows]).fillna(
        0, subset=["xp_current", "xp_holding"]
    )


# ── Distress ──────────────────────────────────────────────────────────────────


def _flag(reason: str) -> Column:
    """1 when any event in the window has this ``reason``."""
    return F.max((F.col("reason") == reason).cast("int"))


def _require_returns_from(returns: DataFrame, since: str) -> None:
    """Stop the run when the returns table starts after ``since`` (an ISO date)."""
    first = returns.agg(F.min("month_end")).first()[0]
    if first is None or first.isoformat()[:7] > since[:7]:
        raise ValueError(
            f"feat_cif_returns_monthly starts at {first}, but the observations need "
            f"returns from {since}: rerun casa_primary and casa_features after changing "
            "crx_persona.persona_start_date"
        )


def _distress_events(
    returns: DataFrame,
    bureau_bounces: DataFrame,
    payment_order: DataFrame | None,
    since: str,
) -> DataFrame:
    """``(cif_id, month_end, reason)`` per distress event: the bank's own cheque / DDS
    returns, bureau bounces and, when given, ``payment_order`` returns. The returns and
    bounces are read from ``since`` (an ISO date) on."""
    events = bureau_bounces.filter(
        (F.col("bounce_events") > 0) & (F.col("month_end") >= F.lit(since))
    ).select("cif_id", "month_end", F.lit(REASON_BUREAU_BOUNCE).alias("reason"))
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
                F.lit(REASON_BUREAU_BOUNCE).alias("reason"),
            )
        )
    return events.unionByName(
        returns.filter(
            F.col("reason").isin(CHEQUE_RETURN, DDS_RETURN)
            & (F.col("events") > 0)
            & (F.col("month_end") >= F.lit(since))
        ).select("cif_id", "month_end", "reason")
    )


def build_distress_signals(
    obs_base: DataFrame,
    returns: DataFrame,
    bureau_bounces: DataFrame,
    model_id: str,
    payment_order: DataFrame | None = None,
) -> DataFrame:
    """``distress_flag`` (S9) and its parts in the window, each 0 / 1:

    * ``distress_cheque`` / ``distress_dds`` — the bank's own returned cheques and DDS
      returns, across all the customer's CASA accounts (``feat_cif_returns_monthly``);
    * ``distress_bureau`` — a bureau-reported bounce dated by its return date
      (``feat_cif_bureau_bounces_monthly`` ``bounce_events``, S15);
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
    _require_returns_from(returns, since)
    events = _distress_events(returns, bureau_bounces, payment_order, since)
    hits = _in_window(
        obs,
        events,
        w,
        _flag(CHEQUE_RETURN).alias("distress_cheque"),
        _flag(DDS_RETURN).alias("distress_dds"),
        _flag(REASON_BUREAU_BOUNCE).alias("distress_bureau"),
    )
    parts = ["distress_cheque", "distress_dds", "distress_bureau"]
    return (
        left_join_all(obs_base, [hits])
        .fillna(0, subset=parts)
        .withColumn("distress_flag", F.greatest(*[F.col(p) for p in parts]))
    )


# ── EOSB (diagnostic) ─────────────────────────────────────────────────────────


def build_eosb_signals(
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame, model_id: str
) -> DataFrame:
    """``eosb_flag`` (S13): 1 when a DCORE result on any of the customer's agreements
    names an end-of-service benefit (EOSB expected / awaited / received) in the
    window. A diagnostic only: it changes no level or state."""
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
