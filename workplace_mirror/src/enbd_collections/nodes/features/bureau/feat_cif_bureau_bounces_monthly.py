"""Feature node: bureau-reported bounced cheques per customer and month.

One row per ``(cif_id, month_end)`` with a bounce, dated by the bureau's return date
(``dt_of_return``), not by the pull. A bounce is a ``(cif_id, dt_of_return)``: the same
return date repeated in later pulls is one bounce, and several cheques returned on one
day are one bounce with the largest amount.

* ``bounce_events`` — bounce days in the month;
* ``max_bounce_amount`` — the largest bounced amount of those days.

Rows with a bounced amount but no return date are not counted.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def build(alerts: DataFrame) -> DataFrame:
    """Bounce days per month from ``prm_bureau_alert_enriched``."""
    missing = sorted(
        {"cif_id", "dt_of_return", "bounced_cheque_amount"} - set(alerts.columns)
    )
    if missing:
        raise ValueError(f"prm_bureau_alert_enriched is missing columns: {missing}")
    amount = F.col("bounced_cheque_amount").cast("double")
    bounces = (
        alerts.filter(
            F.col("cif_id").isNotNull()
            & F.col("dt_of_return").isNotNull()
            & (amount > 0)
        )
        .groupBy(
            F.col("cif_id").cast("string").alias("cif_id"),
            F.to_date("dt_of_return").alias("bounce_date"),
        )
        .agg(F.max(amount).alias("amount"))
    )
    return bounces.groupBy("cif_id", F.last_day("bounce_date").alias("month_end")).agg(
        F.count(F.lit(1)).alias("bounce_events"),
        F.max("amount").alias("max_bounce_amount"),
    )
