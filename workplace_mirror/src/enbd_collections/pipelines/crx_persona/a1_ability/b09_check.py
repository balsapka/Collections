"""TEMPORARY (mirror bundle 09): the A1 report tables and the AECB salary check, in PROD.

Log blocks, aggregates only, latest observation month unless named:

* ``compare_a1_outputs`` (``B09 OUTPUT``): states (M1) — latest month, old
  (``crx_<p>_a1_ability_v2``) × new, the monthly range; RL by ``loan_type``.
* ``describe_a1_report`` (``B09 REPORT``): income source and level (M4), CASA
  relationship (M5), liquidity (M6), Unknown / Low / Moderate-High reasons (M7–M9),
  distress parts (M10), EOSB and the anchor (M11).
* ``describe_a1_sources`` (``B09 SOURCES``): how far back each source goes, internal
  salary history (M2), AECB salary coverage (M3), CASA legs by lane, WM vs FTR coverage.
* ``explain_a1_aecb`` (``B09 AECB``): the state without the alert salary, with its pull
  months, then with the 1-month carry (S14); the last step is checked against the output.

Removed by the bundle's cleanup.
"""

from __future__ import annotations

import logging
from itertools import pairwise

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.features.casa.feat_cif_casa import transaction_lane

from .._common import GRAIN, lookback_floor, window_months
from ..scoring_engine import points_from_level
from .classify import (
    _LADDER,
    DEMIN,
    F_CASA,
    F_INC,
    F_PAY,
    INC_FLOORS,
    K_CASA,
    K_INC,
    K_PAY,
    _months,
    _window,
    income_level,
)
from .signals import CUSTOMER_LANES, _loan_bureau_salary, _with_next_month

LOG = logging.getLogger(__name__)
_STATES = ("high", "moderate", "low", "unknown")


def _log(name: str, model_id: str, lines: list[str]) -> None:
    block = [
        f"=== B09 {name} START === [{model_id}]",
        *lines,
        f"=== B09 {name} END ===",
    ]
    LOG.info("\n%s", "\n".join(block))


def _table(df: DataFrame, *cols: str) -> list[str]:
    """Counts by ``cols`` with the share of all rows."""
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    total = sum(r["count"] for r in rows) or 1
    return [
        "  "
        + " x ".join(f"{r[c]!s:<24}" for c in cols)
        + f" {r['count']:>9}  {100.0 * r['count'] / total:5.1f}%"
        for r in rows
    ]


def _latest_month(df: DataFrame) -> DataFrame:
    last = df.agg(F.max("observation_date")).first()[0]
    return df.filter(
        F.trunc("observation_date", "month") == F.trunc(F.lit(last), "month")
    )


def _rows_and_cifs(df: DataFrame) -> str:
    r = df.agg(
        F.count(F.lit(1)).alias("n"), F.countDistinct("cif_id").alias("c")
    ).first()
    return f"{r['n']} accounts, {r['c']} CIFs"


def _with_cif(df: DataFrame, obs_base: DataFrame) -> DataFrame:
    cifs = obs_base.select(*GRAIN, F.col("cif_id").cast("string").alias("cif_id"))
    return df.join(cifs, on=list(GRAIN), how="left")


# ── B09 OUTPUT (M1) ───────────────────────────────────────────────────────────


def _product(df: DataFrame, products: DataFrame) -> DataFrame:
    """``loan_type`` from ``rl_spine`` (RL), else one product."""
    if "loan_type" not in products.columns:
        return df.withColumn("loan_type", F.lit("all"))
    types = products.select(
        F.col("account_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date").alias("observation_date"),
        "loan_type",
    ).dropDuplicates(list(GRAIN))
    return df.join(types, on=list(GRAIN), how="left")


def compare_a1_outputs(
    old: DataFrame, new: DataFrame, products: DataFrame, model_id: str
) -> None:
    """New states in the latest month (and by product), old × new, the monthly range."""
    latest = _latest_month(new)
    month = latest.agg(F.max("observation_date")).first()[0]
    old_m = old.filter(F.col("observation_date") == F.lit(month)).select(
        F.col("account_id").cast("string").alias("account_id"),
        F.col("a1_state").alias("old_state"),
    )
    both = latest.join(old_m, on="account_id", how="full")
    monthly = (
        new.groupBy(F.trunc("observation_date", "month").alias("month"))
        .agg(
            F.count(F.lit(1)).alias("n"),
            *[F.sum((F.col("a1_state") == s).cast("int")).alias(s) for s in _STATES],
        )
        .orderBy("month")
        .collect()
    )
    lines = [
        (
            f"month {month}: new {latest.count()} rows, old {old_m.count()}, "
            f"new only {both.filter(F.col('old_state').isNull()).count()}, "
            f"old only {both.filter(F.col('a1_state').isNull()).count()}"
        ),
        "new a1_state:",
        *_table(latest, "a1_state"),
        "by product x a1_state:",
        *_table(_product(latest, products), "loan_type", "a1_state"),
        "old x new a1_state:",
        *_table(both.filter(F.col("a1_state").isNotNull()), "old_state", "a1_state"),
        "new a1_state share by month (n, high, moderate, low, unknown %):",
        *[
            f"  {r['month']} {r['n']:>8} "
            + " ".join(f"{100.0 * r[s] / max(r['n'], 1):6.2f}" for s in _STATES)
            for r in monthly
        ],
        "range over the months (min-max %):",
        *[
            f"  {s:<9} "
            + f"{min(100.0 * r[s] / max(r['n'], 1) for r in monthly):6.2f}-"
            + f"{max(100.0 * r[s] / max(r['n'], 1) for r in monthly):6.2f}"
            for s in _STATES
        ],
    ]
    _log("OUTPUT", model_id, lines)


# ── B09 REPORT (M4–M11) ──────────────────────────────────────────────────────


def _bucket(amount: Column, edges: list[tuple[float, str]], none: str) -> Column:
    expr = F.when(amount.isNull() | (amount <= 0), none)
    for edge, label in edges:
        expr = expr.when(amount < edge, label)
    return expr.otherwise(f">={edges[-1][0]:,.0f}")


def describe_a1_report(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    obs_base: DataFrame,
    new: DataFrame,
    income: DataFrame,
    liquidity: DataFrame,
    distress: DataFrame,
    products: DataFrame,
    model_id: str,
) -> None:
    """The latest month's report tables, M4–M11."""
    w = window_months(model_id)
    df = (
        _with_cif(_latest_month(new), obs_base)
        .join(income, on=list(GRAIN), how="left")
        .join(liquidity, on=list(GRAIN), how="left")
        .join(distress, on=list(GRAIN), how="left")
    )
    df = _product(df, products)
    anchor = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))
    casa_w = F.greatest(
        *[F.coalesce(c, F.lit(0.0)) for c in _months("casa", _window(w)[0])]
    )
    has_int = F.coalesce(F.col("internal_salary_w"), F.lit(0.0)) >= DEMIN
    has_bur = F.coalesce(F.col("bureau_salary_w"), F.lit(0.0)) >= DEMIN
    parts = [
        ("distress_cheque", "cheque"),
        ("distress_dds", "dds"),
        ("distress_bureau", "bureau"),
    ]
    df = df.select(
        "*",
        F.when(has_int & has_bur, "both")
        .when(has_int, "internal_only")
        .when(has_bur, "bureau_only")
        .otherwise("neither")
        .alias("income_source_w"),
        F.when(F.col("casa_held") == 0, "no_casa")
        .when(F.col("casa_active") == 0, "dormant_casa")
        .otherwise("active_casa")
        .alias("casa_relationship"),
        _bucket(casa_w, [(1000.0, "<1000"), (3000.0, "1000-3000")], "none").alias(
            "casa_max_w"
        ),
        (casa_w >= F.greatest(F.lit(F_CASA), K_CASA * anchor)).alias(
            "casa_covers_floor"
        ),
        (F.coalesce(F.col("ext_card_payment_max"), F.lit(0.0)) > 0).alias(
            "ext_card_payment"
        ),
        F.when(F.col("a1_state") != "low", None)
        .when(
            (F.col("a1_points_total") == 0) & (F.col("a1_distress_flag") == 0),
            "0pt_active_casa",
        )
        .when(F.col("a1_points_total") == 0, "0pt_distress")
        .when(F.col("a1_points_total") == 1, "1pt")
        .otherwise("2-3pt_distress")
        .alias("low_reason"),
        F.concat_ws(
            "+", *[F.when(F.col(c) == 1, F.lit(label)) for c, label in parts]
        ).alias("distress_parts"),
        F.col("liquidity_anchor_amt").isNotNull().alias("anchor_present"),
        (K_INC * anchor > F_INC).alias("anchor_raises_income"),
        (K_CASA * anchor > F_CASA).alias("anchor_raises_casa"),
        (K_PAY * anchor > F_PAY).alias("anchor_raises_payment"),
    )
    q = (
        df.filter(F.col("liquidity_anchor_amt").isNotNull())
        .agg(F.percentile_approx("liquidity_anchor_amt", [0.1, 0.5, 0.9]).alias("p"))
        .first()["p"]
    )
    mh = df.filter(F.col("a1_state").isin("high", "moderate"))
    lines = [
        f"base: {_rows_and_cifs(df)}",
        "M4 income source in W x income level:",
        *_table(df, "income_source_w", "a1_income_level"),
        "M5 CASA relationship x a1_state:",
        *_table(df, "casa_relationship", "a1_state"),
        "M6 max monthly CASA balance in W x covers max(3000, anchor):",
        *_table(df, "casa_max_w", "casa_covers_floor"),
        "M6 external card payment in W x liquidity level:",
        *_table(df, "ext_card_payment", "a1_liquidity_level"),
        "M6 liquidity level:",
        *_table(df, "a1_liquidity_level"),
        "M7 unknown reason:",
        *_table(df.filter(F.col("a1_state") == "unknown"), "a1_unknown_reason"),
        "M8 low reason:",
        *_table(df.filter(F.col("a1_state") == "low"), "low_reason"),
        "M9 moderate / high: state x income x liquidity x distress:",
        *_table(
            mh, "a1_state", "a1_income_level", "a1_liquidity_level", "a1_distress_flag"
        ),
        "M10 distress parts in W ('' = none):",
        *_table(df, "distress_parts"),
        "M10 distress parts x a1_state:",
        *_table(
            df.filter(F.col("a1_distress_flag") == 1), "distress_parts", "a1_state"
        ),
        "M11 EOSB result in W x a1_state:",
        *_table(df, "a1_eosb_flag", "a1_state"),
        "M11 EOSB in W x liquidity level:",
        *_table(df.filter(F.col("a1_eosb_flag") == 1), "a1_liquidity_level"),
        f"M11 anchor present / p10 p50 p90: {q}",
        *_table(df, "anchor_present"),
        "M11 anchor raises the income x CASA x card-payment floor:",
        *_table(
            df, "anchor_raises_income", "anchor_raises_casa", "anchor_raises_payment"
        ),
        "by product: loan_type x a1_state, x unknown reason, x low reason:",
        *_table(df, "loan_type", "a1_state"),
        *_table(
            df.filter(F.col("a1_state") == "unknown"), "loan_type", "a1_unknown_reason"
        ),
        *_table(df.filter(F.col("a1_state") == "low"), "loan_type", "low_reason"),
    ]
    _log("REPORT", model_id, lines)


# ── B09 SOURCES (M2, M3, lanes, coverage) ────────────────────────────────────


def _months_since(last: Column) -> Column:
    return F.months_between(
        F.trunc("observation_date", "month"), F.trunc(last, "month")
    ).cast("int")


def describe_a1_sources(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    obs_base: DataFrame,
    new: DataFrame,
    internal_salary: DataFrame,
    bureau_salary: DataFrame,
    casa_balance: DataFrame,
    casa_activity: DataFrame,
    transactions: DataFrame,
    alerts: DataFrame,
    model_id: str,
) -> None:
    """Source depth, salary history (M2), AECB coverage (M3), legs by lane, WM vs FTR."""
    w = window_months(model_id)
    base = _with_cif(_latest_month(new).select(*GRAIN, "a1_state"), obs_base).filter(
        F.col("cif_id").isNotNull()
    )
    cifs = base.select("cif_id").distinct()

    def depth(df: DataFrame, col: str, name: str) -> str:
        all_ = df.agg(F.min(col), F.max(col)).first()
        ours = df.join(cifs, on="cif_id").agg(F.min(col)).first()[0]
        return f"  {name:<36} all CIFs {all_[0]} .. {all_[1]}, base CIFs from {ours}"

    def last_before(df: DataFrame, value: str) -> DataFrame:
        return (
            base.join(df.filter(F.col(value) >= DEMIN), on="cif_id")
            .filter(F.col("month_end") <= F.col("observation_date"))
            .groupBy(*GRAIN)
            .agg(F.max("month_end").alias("last"))
        )

    def history(last: DataFrame, label: str) -> DataFrame:
        since = _months_since(F.col("last")) + 1
        return base.join(last, on=list(GRAIN), how="left").withColumn(
            label,
            F.when(F.col("last").isNull(), "never")
            .when(since <= w, "in_W")
            .when(since <= 6, "last_m4-6")
            .when(since <= 12, "last_m7-12")
            .when(since <= 24, "last_m13-24")
            .otherwise("last_m25+"),
        )

    internal = history(last_before(internal_salary, "salary"), "internal_salary")
    alert_cifs = (
        alerts.filter(F.col("cif_id").isNotNull())
        .select(F.col("cif_id").cast("string").alias("cif_id"))
        .distinct()
        .withColumn("_alert", F.lit(1))
    )
    bureau = (
        history(last_before(bureau_salary, "bureau_salary"), "_hist")
        .join(alert_cifs, on="cif_id", how="left")
        .withColumn(
            "bureau",
            F.when(F.col("_alert").isNull(), "no_alert_row")
            .when(F.col("_hist") == "never", "alert_never_salary")
            .otherwise(F.col("_hist")),
        )
    )
    salary_sources = internal.select(*GRAIN, "internal_salary").join(
        bureau.select(*GRAIN, "bureau"), on=list(GRAIN)
    )
    obs_month = base.agg(F.max("observation_date")).first()[0]
    w_floor = lookback_floor(base, w)
    legs = (
        transactions.filter(
            (F.col("tran_date") >= F.lit(w_floor))
            & (F.col("tran_date") <= F.lit(obs_month))
        )
        .withColumn("cif_id", F.col("cif_id").cast("string"))
        .join(cifs, on="cif_id")
        .withColumn("lane", transaction_lane())
    )
    by_lane = (
        legs.groupBy("lane")
        .agg(F.count(F.lit(1)).alias("legs"), F.countDistinct("cif_id").alias("cifs"))
        .orderBy("lane")
        .collect()
    )
    odd = (
        legs.filter(F.col("lane").isin("unclassified", "ambiguous"))
        .groupBy("lane", "tran_type", "reason_for_excluding")
        .count()
        .orderBy(F.col("count").desc())
        .limit(25)
        .collect()
    )
    held_floor = lookback_floor(base, 12)
    wm12 = (
        casa_balance.filter(F.col("month_end") >= F.lit(held_floor))
        .groupBy("cif_id")
        .agg(
            F.max(F.coalesce(F.col("casa_balance"), F.lit(0.0)) > 0).alias(
                "wm_positive"
            )
        )
        .withColumn("wm_row", F.lit(True))
    )
    ftr12 = (
        casa_activity.filter(F.col("month_end") >= F.lit(held_floor))
        .groupBy("cif_id")
        .agg(F.max(F.col("lane").isin(*CUSTOMER_LANES)).alias("ftr_customer"))
        .withColumn("ftr_leg", F.lit(True))
    )
    coverage = (
        cifs.join(wm12, on="cif_id", how="left")
        .join(ftr12, on="cif_id", how="left")
        .fillna(False, subset=["wm_row", "wm_positive", "ftr_leg", "ftr_customer"])
    )
    lines = [
        f"base (latest month): {_rows_and_cifs(base)}",
        "source depth (month_end):",
        depth(internal_salary, "month_end", "feat_cif_internal_salary_monthly"),
        depth(bureau_salary, "month_end", "feat_cif_bureau_salary_monthly"),
        depth(casa_balance, "month_end", "feat_cif_casa_balance_monthly"),
        depth(casa_activity, "month_end", "feat_cif_casa_activity_monthly"),
        "M2 internal salary (>= 1000) history x a1_state:",
        *_table(internal, "internal_salary"),
        *_table(internal, "internal_salary", "a1_state"),
        "M3 AECB salary (>= 1000) by last pull month, before the carry:",
        *_table(bureau, "bureau"),
        "M3 internal salary x AECB salary history:",
        *_table(salary_sources, "internal_salary", "bureau"),
        f"CASA legs of base CIFs in W ({w_floor} .. {obs_month}) by lane (legs, CIFs):",
        *[f"  {r['lane']:<16} {r['legs']:>10} {r['cifs']:>8}" for r in by_lane],
        "top unclassified / ambiguous (lane, tran_type, reason):",
        *[
            f"  {r['lane']:<12} {r['tran_type']!s:<34} {r['reason_for_excluding']!s:<28}"
            f" {r['count']:>8}"
            for r in odd
        ],
        (
            "WM vs FTR, base CIFs, last 12 months: WM row x WM positive x FTR leg x"
            " FTR customer leg:"
        ),
        *_table(coverage, "wm_row", "wm_positive", "ftr_leg", "ftr_customer"),
    ]
    _log("SOURCES", model_id, lines)


# ── B09 AECB ──────────────────────────────────────────────────────────────────


def _spread(base: DataFrame, series: DataFrame, prefix: str, months: int) -> DataFrame:
    """``(cif_id, month_end, amount)`` → ``{prefix}_m1 … _m{months}`` (max per month)."""
    k = (
        F.months_between(
            F.trunc("observation_date", "month"), F.trunc("month_end", "month")
        ).cast("int")
        + 1
    )
    return (
        base.select(*GRAIN, "cif_id")
        .join(series, on="cif_id")
        .withColumn("_k", k)
        .filter(F.col("_k").between(1, months))
        .groupBy(*GRAIN)
        .agg(
            *[
                F.max(F.when(F.col("_k") == i, F.col("amount"))).alias(f"{prefix}_m{i}")
                for i in range(1, months + 1)
            ]
        )
    )


def explain_a1_aecb(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    obs_base: DataFrame,
    new: DataFrame,
    liquidity: DataFrame,
    internal_salary: DataFrame,
    bureau_salary: DataFrame,
    model_id: str,
    loan_features: DataFrame | None = None,
) -> None:
    """Latest month: the state without the alert salary, with its pull months, with the
    1-month carry. RL's loan salary stays in every step and is carried in the last."""
    w = window_months(model_id)
    keys = list(GRAIN)
    base = (
        _with_cif(_latest_month(new), obs_base)
        .filter(F.col("cif_id").isNotNull())
        .join(liquidity.select(*keys, "casa_active"), on=keys, how="left")
        .fillna(0, subset=["casa_active"])
    )
    since = lookback_floor(base, 2 * w)
    columns = ["cif_id", "month_end", "amount"]
    internal = internal_salary.withColumnRenamed("salary", "amount").select(*columns)
    alert = bureau_salary.select("cif_id", "month_end", "bureau_salary")
    if loan_features is not None:
        loans = _loan_bureau_salary(obs_base, loan_features)
    else:
        loans = alert.limit(0)
    carried = _with_next_month(alert.unionByName(loans))

    def amounts(df: DataFrame) -> DataFrame:
        return df.withColumnRenamed("bureau_salary", "amount").select(*columns)

    def recent(df: DataFrame) -> DataFrame:
        return df.filter(F.col("month_end") >= F.lit(since))

    steps = {
        "s0_no_aecb": internal.unionByName(amounts(loans)),
        "s1_pull_months": internal.unionByName(amounts(loans)).unionByName(
            amounts(alert)
        ),
        "s2_one_month_carry": internal.unionByName(amounts(carried)),
    }
    amt = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))
    liq = points_from_level(F.col("a1_liquidity_level"), {"adequate": 2, "weak": 1})
    distressed = F.col("a1_distress_flag") == 1
    last = _months("income", _window(w)[0])
    total = sum(F.coalesce(c, F.lit(0.0)) for c in last)
    floor = F.greatest(F.lit(F_INC), K_INC * amt)
    df = base
    for name, series in steps.items():
        level = income_level(amt, w)
        points = points_from_level(level, {"stable": 2, "weak": 1}) + liq
        unknown = (points == 0) & ~distressed & (F.col("casa_active") == 0)
        step = base.join(
            _spread(base, recent(series), "income", 2 * w), on=keys, how="left"
        ).select(
            *keys,
            level.alias(f"{name}_income"),
            _LADDER.state(points, distressed, unknown).alias(name),
            (total >= INC_FLOORS[w] * floor).alias(f"{name}_total_ok"),
        )
        df = df.join(step, on=keys, how="left")
    aecb_w = (
        base.select(*keys, "cif_id")
        .join(amounts(carried).filter(F.col("amount") >= DEMIN), on="cif_id")
        .filter(
            (
                F.col("month_end")
                >= F.add_months(F.trunc("observation_date", "month"), 1 - w)
            )
            & (F.col("month_end") <= F.col("observation_date"))
        )
        .groupBy(*keys)
        .agg(F.count(F.lit(1)).alias("aecb_months_w"))
    )
    df = df.join(aecb_w, on=keys, how="left").fillna(0, subset=["aecb_months_w"])
    final = "s2_one_month_carry"
    checks = df.agg(
        F.sum((~F.col(final).eqNullSafe(F.col("a1_state"))).cast("int")).alias("state"),
        F.sum(
            (~F.col(f"{final}_income").eqNullSafe(F.col("a1_income_level"))).cast("int")
        ).alias("income"),
        F.sum(
            (
                (F.col("aecb_months_w") > 0)
                & F.col(f"{final}_total_ok")
                & (F.col("a1_income_level") != "stable")
            ).cast("int")
        ).alias("fall"),
    ).first()
    lines = [
        (
            f"rows {df.count()}; last step vs the output: {checks['state']} states, "
            f"{checks['income']} income levels differ"
        ),
        "rows per state at each step (high, moderate, low, unknown):",
        *[
            f"  {n:<20} "
            + " ".join(
                f"{r[s]:>8}"
                for r in [
                    df.agg(
                        *[F.sum((F.col(n) == s).cast("int")).alias(s) for s in _STATES]
                    ).first()
                ]
                for s in _STATES
            )
            for n in steps
        ],
    ]
    for a, b in pairwise(steps):
        moved = df.filter(~F.col(a).eqNullSafe(F.col(b)))
        lines += [f"{a} -> {b}: {moved.count()} rows move", *_table(moved, a, b)]
    lines += [
        "income source x income level:",
        *_table(df, "a1_income_source", "a1_income_level"),
        "income source x a1_state:",
        *_table(df, "a1_income_source", "a1_state"),
        "AECB months in W (with the carry) x income level:",
        *_table(df, "aecb_months_w", "a1_income_level"),
        f"AECB in W, window total passes, the 25% check fails: {checks['fall']}",
        "salary stopped x income source x income level:",
        *_table(
            df.filter(F.col("a1_salary_stopped") == 1),
            "a1_income_source",
            "a1_income_level",
        ),
        "salary stopped x a1_state:",
        *_table(df, "a1_salary_stopped", "a1_state"),
    ]
    _log("AECB", model_id, lines)
