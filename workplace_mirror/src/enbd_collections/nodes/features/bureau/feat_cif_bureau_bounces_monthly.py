"""Feature node: bureau-reported bounced cheques per customer and month.

One row per ``(cif_id, month_end)`` with a bureau pull that reports a bounced cheque,
dated by the pull (``extract_date``; the bureau gives no bounce date):

* ``bounce_pulls``  — pulls that report a bounced amount;
* ``bounce_events`` — of those, the pulls that report something new: per alert key
  ``(cif_id, contract_type, alert_description)``, the bounced amount differs from the
  key's previous pull, or the previous pull had none. A bounce repeated unchanged in
  later pulls counts once.
"""

from __future__ import annotations

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

_KEY = ["cif_id", "contract_type", "alert_description"]


def build(alerts: DataFrame) -> DataFrame:
    """Bounce pulls and new bounce events from ``prm_bureau_alert_enriched``. Several
    rows of one key in one pull count as one pull, with the largest amount."""
    missing = sorted(
        {*_KEY, "extract_date", "bounced_cheque_amount"} - set(alerts.columns)
    )
    if missing:
        raise ValueError(f"prm_bureau_alert_enriched is missing columns: {missing}")
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
        .groupBy(*_KEY, "pull_date")
        .agg(F.max("amount").alias("amount"))
    )
    previous = F.lag("amount").over(Window.partitionBy(*_KEY).orderBy("pull_date"))
    bounced = F.col("amount") > 0
    new = bounced & (F.coalesce(previous, F.lit(0.0)) != F.col("amount"))
    return (
        pulls.withColumn("_new", new)
        .filter(bounced)
        .groupBy("cif_id", F.last_day("pull_date").alias("month_end"))
        .agg(
            F.count(F.lit(1)).alias("bounce_pulls"),
            F.sum(F.col("_new").cast("int")).alias("bounce_events"),
        )
    )
