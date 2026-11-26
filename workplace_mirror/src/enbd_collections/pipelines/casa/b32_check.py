"""TEMPORARY (bundle 32): ``feat_cif_casa_balance_monthly`` before and after the switch
of ``wm_fea_casa_eod_avg_balance`` from every ``adv_load_date`` partition to one.

``casa_b32_snapshot`` (run before ``casa_features``) copies the persisted table into
``casa_b32_old_balance`` (explicit entry in ``catalog_tmp_b32_check.yml``).
``casa_b32_compare`` (run after ``casa_features``) logs, for ``model_id``, per month the
two tables share:

- rows only in the old table, only in the new one, in both;
- of the rows in both with a balance on both sides: the share equal (within 0.01 AED),
  the median and p99 absolute difference of the unequal ones, and the share where the
  new balance is lower;
- balance NULL on one side only, and ``casa_flow`` disagreements.

Months after the old table's last month are new and left out. Removed by the bundle's
cleanup.

    kedro run --pipeline=casa_b32_snapshot      (before casa_features)
    kedro run --pipeline=casa_b32_compare       (after casa_features)
"""

import logging

from kedro.pipeline import Pipeline, node
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

logger = logging.getLogger(__name__)
TAGS = ["casa", "b32_check"]
KEY = ["cif_id", "month_end"]


def snapshot(balance: DataFrame) -> DataFrame:
    """The persisted table as it is."""
    return balance


def _side(df: DataFrame, tag: str) -> DataFrame:
    return df.select(
        *KEY,
        F.col("casa_balance").alias(f"{tag}_bal"),
        F.col("casa_flow").alias(f"{tag}_flow"),
        F.lit(1).alias(f"in_{tag}"),
    )


def compare(old: DataFrame, new: DataFrame, model_id: str) -> None:
    """Log the ``B32 CASA OLD NEW`` block (see the module docstring)."""
    last_old = old.agg(F.max("month_end")).first()[0]
    new = new.filter(F.col("month_end") <= last_old)
    joined = (
        _side(old, "o")
        .join(_side(new, "n"), KEY, "full")
        .withColumn("d", F.abs(F.col("o_bal") - F.col("n_bal")))
        .withColumn("ud", F.when(F.col("d") > 0.01, F.col("d")))
    )
    in_o, in_n = F.col("in_o").isNotNull(), F.col("in_n").isNotNull()
    rows = (
        joined.groupBy("month_end")
        .agg(
            F.sum((in_o & ~in_n).cast("int")).alias("only_old"),
            F.sum((in_n & ~in_o).cast("int")).alias("only_new"),
            F.sum((in_o & in_n).cast("int")).alias("both"),
            F.count("d").alias("n_bal"),
            F.count("ud").alias("n_diff"),
            F.expr("percentile_approx(ud, 0.5)").alias("p50"),
            F.expr("percentile_approx(ud, 0.99)").alias("p99"),
            F.count(F.when(F.col("n_bal") < F.col("o_bal"), F.col("ud"))).alias(
                "n_lower"
            ),
            F.count(
                F.when(
                    in_o & in_n & (F.col("o_bal").isNull() != F.col("n_bal").isNull()),
                    1,
                )
            ).alias("null_one_side"),
            F.count(F.when(F.col("o_flow") != F.col("n_flow"), 1)).alias("flow_diff"),
        )
        .orderBy("month_end")
        .collect()
    )
    lines = [
        f"  model_id {model_id}",
        (
            "  month_end: only_old / only_new / both | equal % of n_bal (n_bal) |"
            " unequal p50 / p99 abs diff, new lower % | balance NULL one side |"
            " flow diff"
        ),
    ]
    for r in rows:
        equal = 100 * (r["n_bal"] - r["n_diff"]) / r["n_bal"] if r["n_bal"] else 0.0
        lower = 100 * r["n_lower"] / r["n_diff"] if r["n_diff"] else 0.0
        lines.append(
            f"  {r['month_end']}: {r['only_old']} / {r['only_new']} / {r['both']}"
            f" | {equal:.2f}% ({r['n_bal']}) | {r['p50']} / {r['p99']}, {lower:.1f}%"
            f" | {r['null_one_side']} | {r['flow_diff']}"
        )
    name = "B32 CASA OLD NEW"
    logger.info("\n=== %s START ===\n%s\n=== %s END ===", name, "\n".join(lines), name)


def create_snapshot_pipeline() -> Pipeline:
    """Copy the persisted ``feat_cif_casa_balance_monthly`` aside."""
    return Pipeline(
        [
            node(
                func=snapshot,
                inputs="feat_cif_casa_balance_monthly",
                outputs="casa_b32_old_balance",
                name="casa_b32_snapshot",
                tags=TAGS,
            )
        ]
    )


def create_compare_pipeline() -> Pipeline:
    """Log the old x new comparison."""
    return Pipeline(
        [
            node(
                func=compare,
                inputs={
                    "old": "casa_b32_old_balance",
                    "new": "feat_cif_casa_balance_monthly",
                    "model_id": "params:model_id",
                },
                outputs=None,
                name="casa_b32_compare",
                tags=TAGS,
            )
        ]
    )
