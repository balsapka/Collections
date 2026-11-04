"""TEMPORARY (mirror bundle 14): the A1 check of CASA accounts and bounce dates, in PROD.

Log blocks, aggregates only, latest observation month:

* ``compare_a1_outputs`` (``B14 OUTPUT``): states old (``crx_<p>_a1_ability``, the output
  before this bundle) × new, by product, and why rows moved (Unknown reason, distress).
* ``describe_a1_accounts`` (``B14 ACCOUNTS``): the base CIFs' legs of the last 12 months by
  account length × scheme class (current / savings / other scheme / no scheme), the top
  other schemes, and the CIFs left with no CASA leg.
* ``describe_a1_bounces`` (``B14 BOUNCES``): bureau bounce events by the pull rule (before)
  and by the return date (S15), CIF-months and rows with a bounce in the window.

Removed by the bundle's cleanup.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from .._common import GRAIN, window_agg, window_months

LOG = logging.getLogger(__name__)


def _log(name: str, model_id: str, lines: list[str]) -> None:
    block = [
        f"=== B14 {name} START === [{model_id}]",
        *lines,
        f"=== B14 {name} END ===",
    ]
    LOG.info("\n%s", "\n".join(block))


def _table(df: DataFrame, *cols: str) -> list[str]:
    """Counts by ``cols`` with the share of all rows; under 10 shown as ``<10``."""
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    total = sum(r["count"] for r in rows) or 1
    return [
        "  "
        + " x ".join(f"{r[c]!s:<22}" for c in cols)
        + f" {r['count'] if r['count'] >= 10 else '<10':>9}"
        + f"  {100.0 * r['count'] / total:5.1f}%"
        for r in rows
    ]


def _latest(df: DataFrame) -> DataFrame:
    last = df.agg(F.max("observation_date")).first()[0]
    return df.filter(F.col("observation_date") == F.lit(last))


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


def _cifs(obs_base: DataFrame) -> DataFrame:
    return (
        _latest(obs_base)
        .filter(F.col("cif_id").isNotNull())
        .select(F.col("cif_id").cast("string").alias("cif_id"))
        .distinct()
    )


# ── B14 OUTPUT ────────────────────────────────────────────────────────────────


def compare_a1_outputs(
    old: DataFrame, new: DataFrame, products: DataFrame, model_id: str
) -> None:
    """Latest month: old × new state, by product, and the reason behind each move."""
    latest = _latest(new)
    month = latest.agg(F.max("observation_date")).first()[0]
    cols = ["a1_state", "a1_unknown_reason", "a1_distress_flag"]
    old_m = old.filter(F.col("observation_date") == F.lit(month)).select(
        F.col("account_id").cast("string").alias("account_id"),
        *[F.col(c).alias(f"old_{c}") for c in cols],
    )
    both = _product(latest, products).join(old_m, on="account_id", how="inner")
    moved = both.filter(F.col("old_a1_state") != F.col("a1_state")).withColumn(
        "why",
        F.when(
            F.col("old_a1_distress_flag") != F.col("a1_distress_flag"), "distress"
        ).otherwise(F.coalesce("a1_unknown_reason", F.lit("gate_opened"))),
    )
    lines = [
        (
            f"month {month}: new {latest.count()} rows, old {old_m.count()}, "
            f"matched {both.count()}"
        ),
        "new a1_state:",
        *_table(latest, "a1_state"),
        "new a1_state by product:",
        *_table(both, "loan_type", "a1_state"),
        "old x new a1_state:",
        *_table(both, "old_a1_state", "a1_state"),
        "moved rows: old x new x why (distress changed / new Unknown reason):",
        *_table(moved, "old_a1_state", "a1_state", "why"),
        "a1_unknown_reason old x new (Unknown rows):",
        *_table(
            both.filter(F.col("a1_state") == "unknown").fillna(
                "not_unknown", subset=["old_a1_unknown_reason"]
            ),
            "old_a1_unknown_reason",
            "a1_unknown_reason",
        ),
        "a1_unknown_reason by product (new):",
        *_table(
            both.filter(F.col("a1_state") == "unknown"),
            "loan_type",
            "a1_unknown_reason",
        ),
        "a1_distress_flag old x new:",
        *_table(both, "old_a1_distress_flag", "a1_distress_flag"),
    ]
    _log("OUTPUT", model_id, lines)


# ── B14 ACCOUNTS ──────────────────────────────────────────────────────────────


def describe_a1_accounts(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    obs_base: DataFrame,
    transactions: DataFrame,
    acid_to_cif: DataFrame,
    current_account_codes: Sequence[str],
    saving_account_codes: Sequence[str],
    casa_activity: DataFrame,
    model_id: str,
) -> None:
    """Legs of the latest month's CIFs by account length × scheme class, the top other
    schemes, and the CIFs with no CASA leg in 12 months."""
    cifs = _cifs(obs_base)
    schemes = acid_to_cif.select(
        F.trim(F.col("foracid").cast("string")).alias("foracid"),
        F.trim(F.col("schm_code").cast("string")).alias("schm_code"),
    ).dropDuplicates(["foracid"])
    last = transactions.agg(F.max("tran_date")).first()[0]
    legs = (
        transactions.withColumn("cif_id", F.col("cif_id").cast("string"))
        .join(cifs, on="cif_id", how="leftsemi")
        .filter(F.col("tran_date") > F.add_months(F.lit(last), -12))
        .withColumn("foracid", F.trim(F.col("foracid").cast("string")))
        .join(schemes, on="foracid", how="left")
        .withColumn("length", F.length("foracid"))
        .withColumn(
            "scheme_class",
            F.when(F.col("schm_code").isin(*current_account_codes), "current")
            .when(F.col("schm_code").isin(*saving_account_codes), "savings")
            .when(F.col("schm_code").isNotNull(), "other_scheme")
            .otherwise("no_scheme"),
        )
    )
    by_class = (
        legs.groupBy("length", "scheme_class")
        .agg(F.count(F.lit(1)).alias("legs"), F.countDistinct("cif_id").alias("cifs"))
        .orderBy("length", "scheme_class")
        .collect()
    )
    top = (
        legs.filter(F.col("scheme_class") == "other_scheme")
        .groupBy("schm_code")
        .agg(F.count(F.lit(1)).alias("legs"), F.countDistinct("cif_id").alias("cifs"))
        .orderBy(F.desc("legs"))
        .limit(10)
        .collect()
    )
    with_casa = (
        casa_activity.withColumn("cif_id", F.col("cif_id").cast("string"))
        .filter(F.col("month_end") > F.add_months(F.lit(last), -12))
        .select("cif_id")
        .distinct()
    )
    n_cifs = cifs.count()
    n_casa = cifs.join(with_casa, on="cif_id", how="leftsemi").count()
    lines = [
        f"{n_cifs} base CIFs; legs since {last} minus 12 months",
        "length x scheme_class: legs, CIFs",
        *[
            f"  {r['length']!s:<4} {r['scheme_class']:<13} {r['legs']:>10} {r['cifs']:>8}"
            for r in by_class
        ],
        "top other schemes: schm_code, legs, CIFs",
        *[f"  {r['schm_code']:<8} {r['legs']:>10} {r['cifs']:>8}" for r in top],
        (
            f"CIFs with a CASA leg (new feat_cif_casa_activity_monthly) in 12 months: "
            f"{n_casa} ({100.0 * n_casa / max(n_cifs, 1):.1f}%)"
        ),
    ]
    _log("ACCOUNTS", model_id, lines)


# ── B14 BOUNCES ───────────────────────────────────────────────────────────────


def _pull_rule(alerts: DataFrame) -> DataFrame:
    """Bounce events by the rule before S15: per (cif, contract type, description), a
    pull whose bounced amount differs from the key's previous pull, dated by the pull.
    """
    key = ["cif_id", "contract_type", "alert_description"]
    pulls = (
        alerts.filter(F.col("cif_id").isNotNull())
        .select(
            F.col("cif_id").cast("string").alias("cif_id"),
            "contract_type",
            "alert_description",
            F.to_date("extract_date").alias("pull_date"),
            F.coalesce(F.col("bounced_cheque_amount").cast("double"), F.lit(0.0)).alias(
                "amount"
            ),
        )
        .groupBy(*key, "pull_date")
        .agg(F.max("amount").alias("amount"))
    )
    previous = F.lag("amount").over(Window.partitionBy(*key).orderBy("pull_date"))
    new = (F.col("amount") > 0) & (F.coalesce(previous, F.lit(0.0)) != F.col("amount"))
    return (
        pulls.filter(new)
        .groupBy("cif_id", F.last_day("pull_date").alias("month_end"))
        .agg(F.count(F.lit(1)).alias("bounce_events"))
    )


def describe_a1_bounces(
    obs_base: DataFrame, alerts: DataFrame, bureau_bounces: DataFrame, model_id: str
) -> None:
    """Bureau bounce events, pull rule against return date: CIF-months, and the latest
    month's rows with a bounce in the window under each."""
    old = _pull_rule(alerts)
    new = bureau_bounces.filter(F.col("bounce_events") > 0).select(
        F.col("cif_id").cast("string").alias("cif_id"), "month_end", "bounce_events"
    )
    months = (
        old.select("cif_id", "month_end")
        .withColumn("old", F.lit(1))
        .join(
            new.select("cif_id", "month_end").withColumn("new", F.lit(1)),
            on=["cif_id", "month_end"],
            how="full",
        )
    )
    obs = _latest(obs_base).filter(F.col("cif_id").isNotNull())
    obs = obs.withColumn("cif_id", F.col("cif_id").cast("string"))
    w = window_months(model_id)

    def flag(series: DataFrame, name: str) -> DataFrame:
        return window_agg(
            obs,
            series,
            date_col="month_end",
            aggs=[F.max(F.lit(1)).alias(name)],
            months=w,
        )

    rows = (
        obs.select(*GRAIN)
        .join(flag(old, "old"), on=list(GRAIN), how="left")
        .join(flag(new, "new"), on=list(GRAIN), how="left")
        .fillna(0, subset=["old", "new"])
    )
    lag = alerts.filter(
        (F.col("bounced_cheque_amount").cast("double") > 0)
        & F.col("dt_of_return").isNotNull()
    ).select(
        F.datediff(F.to_date("extract_date"), F.to_date("dt_of_return")).alias("days")
    )
    q = lag.approxQuantile("days", [0.5, 0.75, 0.95], 0.01)
    lines = [
        (
            f"events: pull rule {old.agg(F.sum('bounce_events')).first()[0]}, "
            f"return date {new.agg(F.sum('bounce_events')).first()[0]}"
        ),
        "CIF-months with an event: old x new",
        *_table(months.fillna(0, subset=["old", "new"]), "old", "new"),
        f"latest-month rows with a bureau bounce in the {w}-month window: old x new",
        *_table(rows, "old", "new"),
        f"extract minus return date, days: p50 / p75 / p95 = {q}",
    ]
    _log("BOUNCES", model_id, lines)
