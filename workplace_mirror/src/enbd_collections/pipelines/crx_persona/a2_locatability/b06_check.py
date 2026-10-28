"""TEMPORARY (mirror bundle 06): the old A2 vs the new engine, run in PROD.

Log blocks, aggregates only:

* ``compare_a2_outputs`` (``B06 OUTPUT``): the old output (``crx_<p>_a2_locatability``)
  against the new one (``crx_<p>_a2_locatability_b06_check``) in the latest month — an
  old row is matched to the new row of the same account and month (the month's latest
  old observation) — plus the new location / reachability shares per month.
* ``describe_a2_rules`` (``B06 RULES``): which rule fires, which source holds the
  deciding evidence, unknown reasons, call days, deceased sources.
* ``describe_debit_evidence`` (``B06 DEBIT``): the base customers' rows in
  ``prm_casa_card_transactions`` by month, channel / type and place (the Offline → Machine
  change, ATM placement), and their ``reason_for_excluding`` values.
* ``split_by_product`` (``B06 PRODUCT``, RL only): the latest month by ``loan_type``.

Removed by the bundle's cleanup.
"""

import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.nodes.utils.location import is_uae

LOG = logging.getLogger(__name__)


def _log(name: str, model_id: str, lines: list[str]) -> None:
    block = [
        f"=== B06 {name} START === [{model_id}]",
        *lines,
        f"=== B06 {name} END ===",
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


def _snake(col: str) -> F.Column:
    """'In Country' → 'in_country', 'Non-Reachable' → 'non_reachable'."""
    return F.regexp_replace(F.lower(F.trim(col)), "[ -]+", "_")


def compare_a2_outputs(old: DataFrame, new: DataFrame, model_id: str) -> None:
    """Old vs new location, reachability and deceased in the latest month; new shares
    per month."""
    latest_new = _latest_month(new)
    month = latest_new.agg(F.trunc(F.max("observation_date"), "month")).first()[0]
    in_month = Window.partitionBy("account_id").orderBy(
        F.col("observation_date").desc()
    )
    old_m = (
        old.filter(F.trunc("observation_date", "month") == F.lit(month))
        .withColumn("_rn", F.row_number().over(in_month))
        .filter(F.col("_rn") == 1)
        .select(
            F.col("account_id").cast("string").alias("account_id"),
            _snake("location_state").alias("old_location"),
            _snake("reachability_state").alias("old_reachability"),
            F.col("deceased_flag_v2").cast("int").alias("old_deceased"),
        )
    )
    both = latest_new.join(old_m, on="account_id", how="full")
    lines = [
        (
            f"month {month}: new rows {latest_new.count()}, old rows {old_m.count()}, "
            f"new only {both.filter(F.col('old_location').isNull()).count()}, "
            f"old only {both.filter(F.col('a2_state').isNull()).count()}"
        ),
        "new a2_state:",
        *_table(latest_new, "a2_state"),
        "location old x new:",
        *_table(
            both.filter(F.col("a2_state").isNotNull()), "old_location", "location_state"
        ),
        "reachability old x new:",
        *_table(
            both.filter(F.col("a2_state").isNotNull()),
            "old_reachability",
            "reachability_state",
        ),
        "deceased old x new:",
        *_table(
            both.filter(F.col("a2_state").isNotNull()), "old_deceased", "deceased_flag"
        ),
        "new location_state by month:",
        *_table(
            new.withColumn("month", F.trunc("observation_date", "month")),
            "month",
            "location_state",
        ),
        "new reachability_state by month:",
        *_table(
            new.withColumn("month", F.trunc("observation_date", "month")),
            "month",
            "reachability_state",
        ),
    ]
    _log("OUTPUT", model_id, lines)


def describe_a2_rules(new: DataFrame, model_id: str) -> None:
    """Rules, deciding sources, unknown reasons, call days and deceased sources in the
    latest month."""
    df = _latest_month(new)
    days = F.col("attempt_days_in_window")
    lines = [
        "location_rule x deciding source (L1: latest foreign, else latest UAE):",
        *_table(
            df.withColumn(
                "source",
                F.when(
                    F.col("location_rule") == "L1", F.col("last_foreign_source")
                ).otherwise(F.col("last_uae_source")),
            ),
            "location_rule",
            "source",
        ),
        "location_unknown_reason:",
        *_table(
            df.filter(F.col("location_state") == "unknown"), "location_unknown_reason"
        ),
        "L2 rows by months since the latest UAE evidence:",
        *_table(
            df.filter(F.col("location_rule") == "L2").withColumn(
                "months",
                F.floor(F.months_between("observation_date", "last_uae_date")).cast(
                    "int"
                ),
            ),
            "months",
        ),
        "reachability_state x reason:",
        *_table(df, "reachability_state", "reachability_unknown_reason"),
        "call days in the window:",
        *_table(
            df.withColumn(
                "call_days",
                F.when(days == 0, "0")
                .when(days < 3, "1-2")
                .when(days < 6, "3-5")
                .otherwise("6+"),
            ),
            "call_days",
        ),
        "skip-trace status ever (diagnostic) x location_state:",
        *_table(
            df.withColumn("skip_trace", F.col("last_skip_trace_date").isNotNull()),
            "skip_trace",
            "location_state",
        ),
        "deceased_source:",
        *_table(df.filter(F.col("deceased_flag") == 1), "deceased_source"),
    ]
    _log("RULES", model_id, lines)


def describe_debit_evidence(
    obs_base: DataFrame, casa_cards: DataFrame, model_id: str
) -> None:
    """The latest month's base customers' debit-card rows by month, type and place."""
    cifs = (
        _latest_month(obs_base)
        .select("cif_id")
        .filter(F.col("cif_id").isNotNull())
        .distinct()
    )
    uae = is_uae(F.col("place_country"))
    rows = (
        casa_cards.withColumn("cif_id", F.col("cif_id").cast("string"))
        .join(F.broadcast(cifs), on="cif_id", how="leftsemi")
        .withColumn(
            "type",
            F.when(F.col("channel_desc") == "ATM Transactions", F.lit("ATM")).otherwise(
                F.coalesce(F.col("merchant_type_desc"), F.lit("NULL"))
            ),
        )
        .withColumn("place", F.when(uae, "uae").when(~uae, "abroad").otherwise("none"))
        .withColumn("month", F.trunc(F.coalesce("value_date", "tran_date"), "month"))
    )
    lines = [
        "rows by month x type x place:",
        *_table(rows, "month", "type", "place"),
        "place_source by type:",
        *_table(rows, "type", "place_source"),
        "reason_for_excluding (all months):",
        *_table(rows, "reason_for_excluding"),
    ]
    _log("DEBIT", model_id, lines)


def split_by_product(new: DataFrame, rl_spine: DataFrame, model_id: str) -> None:
    """The latest month's states by ``loan_type`` (RL)."""
    products = rl_spine.select(
        F.col("account_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date").alias("observation_date"),
        "loan_type",
    ).dropDuplicates(["account_id", "observation_date"])
    df = _latest_month(new).join(
        products, on=["account_id", "observation_date"], how="left"
    )
    lines = [
        "loan_type x location_state:",
        *_table(df, "loan_type", "location_state"),
        "loan_type x reachability_state:",
        *_table(df, "loan_type", "reachability_state"),
        "loan_type x deceased_flag:",
        *_table(df, "loan_type", "deceased_flag"),
    ]
    _log("PRODUCT", model_id, lines)
