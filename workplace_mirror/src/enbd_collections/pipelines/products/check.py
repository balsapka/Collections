"""TEMPORARY (bundle 24): the cross-product feature rebuilt from the product primaries
against the persisted ``feat_cif_cross_product_monthly`` (bundle 21, raw Way4 reads).

The check builds the new table into ``feat_cif_cross_product_monthly_b24_new`` (the real
output is untouched) and logs:

- ``B24 PRODUCTS``: rows per product type, old / new / only old / only new, and the rows
  in both whose balance, current flag or instalment differ;
- ``B24 A1 INPUTS``: customer-months whose A1 cross-product inputs (assets, largest
  current instalment, any current credit product, any asset holding) differ.

Expected: only the term-deposit holder rows without a balance disappear (``deposit``,
NULL balance), and no A1 input changes. Removed by the bundle's cleanup.

    kedro run --pipeline=product_features_b24_check
"""

import logging

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

logger = logging.getLogger(__name__)
_KEY = ["cif_id", "month_end", "product_account_id", "product_type"]
_VALUES = ["balance_aed", "is_current", "instalment_aed"]


def _block(name: str, lines: list[str]) -> None:
    body = "\n".join(lines)
    logger.info("\n=== %s START ===\n%s\n=== %s END ===", name, body, name)


def _differs(column: str) -> Column:
    old, new = F.col(f"old_{column}"), F.col(f"new_{column}")
    both = old.isNotNull() & new.isNotNull()
    return (old.isNull() != new.isNull()) | (both & (F.abs(old - new) > 1e-6))


def _side(df: DataFrame, side: str) -> DataFrame:
    return df.select(
        *[F.col(c).cast("string").alias(c) if c != "month_end" else c for c in _KEY],
        *[F.col(c).cast("double").alias(f"{side}_{c}") for c in _VALUES],
        F.lit(1).alias(f"_{side}"),
    )


def _a1_inputs(df: DataFrame) -> DataFrame:
    asset = F.col("product_type").isin("deposit", "investment", "wm")
    current = F.col("product_type").isin("card", "loan") & (
        F.coalesce(F.col("is_current").cast("int"), F.lit(0)) == 1
    )
    return df.groupBy(F.col("cif_id").cast("string").alias("cif_id"), "month_end").agg(
        F.sum(F.when(asset, F.col("balance_aed"))).alias("assets"),
        F.max(F.when(current, F.col("instalment_aed"))).alias("instalment"),
        F.max(current.cast("int")).alias("current"),
        F.max((asset & (F.col("balance_aed") > 0)).cast("int")).alias("holding"),
    )


def compare(old: DataFrame, new: DataFrame, persona_end_date: str) -> None:
    """Log the ``B24 PRODUCTS`` and ``B24 A1 INPUTS`` blocks."""
    joined = _side(old, "old").join(_side(new, "new"), _KEY, "full")
    in_both = F.col("_old").isNotNull() & F.col("_new").isNotNull()
    rows = (
        joined.groupBy("product_type")
        .agg(
            F.count("_old").alias("old"),
            F.count("_new").alias("new"),
            F.sum(F.col("_new").isNull().cast("int")).alias("only_old"),
            F.sum(F.col("_old").isNull().cast("int")).alias("only_new"),
            F.sum(
                (F.col("_new").isNull() & F.col("old_balance_aed").isNull()).cast("int")
            ).alias("only_old_null_balance"),
            *[
                F.sum((in_both & _differs(c)).cast("int")).alias(f"diff_{c}")
                for c in _VALUES
            ],
        )
        .orderBy("product_type")
        .collect()
    )
    _block(
        "B24 PRODUCTS",
        [
            f"  {r['product_type']}: old {r['old']} | new {r['new']} | only old "
            f"{r['only_old']} (null balance {r['only_old_null_balance']}) | only new "
            f"{r['only_new']} | differ balance {r['diff_balance_aed']} / current "
            f"{r['diff_is_current']} / instalment {r['diff_instalment_aed']}"
            for r in rows
        ],
    )
    inputs = ["assets", "instalment", "current", "holding"]
    a = _a1_inputs(old).select(
        "cif_id", "month_end", *[F.col(c).alias(f"old_{c}") for c in inputs]
    )
    b = _a1_inputs(new).select(
        "cif_id", "month_end", *[F.col(c).alias(f"new_{c}") for c in inputs]
    )
    latest = F.last_day(F.lit(str(persona_end_date)).cast("date"))
    diff = a.join(b, ["cif_id", "month_end"], "full").select(
        "month_end", *[_differs(c).alias(c) for c in inputs]
    )
    any_diff = F.greatest(*[F.col(c).cast("int") for c in inputs])
    stats = diff.agg(
        F.count(F.lit(1)).alias("months"),
        F.sum(any_diff).alias("any"),
        F.sum(F.when(F.col("month_end") == latest, 1)).alias("latest_months"),
        F.sum(F.when(F.col("month_end") == latest, any_diff)).alias("latest_any"),
        *[F.sum(F.col(c).cast("int")).alias(c) for c in inputs],
    ).collect()[0]
    _block(
        "B24 A1 INPUTS",
        [
            f"  customer-months: {stats['months']}, any input differs: {stats['any']}",
            f"  latest month ({persona_end_date}): {stats['latest_months']}, "
            f"differ: {stats['latest_any']}",
            "  by input: " + " | ".join(f"{c} {stats[c]}" for c in inputs),
        ],
    )
