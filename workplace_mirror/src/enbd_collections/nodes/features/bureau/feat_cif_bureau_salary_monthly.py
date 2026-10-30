"""Feature node: AECB-reported salary per customer and pull month.

One row per ``(cif_id, month_end)`` with a salary alert, dated by the pull
(``extract_date``). ``bureau_salary`` is the salary reported on the month's latest pull, an
accurate level on that date, not a month's credit: salary rows are ``alert_type_number`` 31
(average salary changed) and 32 (salary account added) with an amount; 43 (salary account
closed) gives 0. Months without a pull have no row. How far a pull carries is decided by the
consumer.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

_SALARY_TYPES = (31, 32)
_CLOSED_TYPE = 43


def build(alerts: DataFrame) -> DataFrame:
    """The month's latest pull from ``prm_bureau_alert_enriched``; on the same pull a
    closure wins, then the largest amount."""
    columns = {"cif_id", "extract_date", "alert_type_number", "salary_credit_amount"}
    missing = sorted(columns - set(alerts.columns))
    if missing:
        raise ValueError(f"prm_bureau_alert_enriched is missing columns: {missing}")
    alert_type = F.col("alert_type_number").cast("double")
    amount = F.col("salary_credit_amount").cast("double")
    closed = alert_type == _CLOSED_TYPE
    latest = F.max(F.struct("pull_date", "closed", "amount")).alias("_latest")
    return (
        alerts.filter(
            F.col("cif_id").isNotNull()
            & (closed | (alert_type.isin(*_SALARY_TYPES) & (amount > 0)))
        )
        .select(
            F.col("cif_id").cast("string").alias("cif_id"),
            F.to_date("extract_date").alias("pull_date"),
            closed.alias("closed"),
            F.when(closed, 0.0).otherwise(amount).alias("amount"),
        )
        .groupBy("cif_id", F.last_day("pull_date").alias("month_end"))
        .agg(latest)
        .select("cif_id", "month_end", F.col("_latest.amount").alias("bureau_salary"))
    )
