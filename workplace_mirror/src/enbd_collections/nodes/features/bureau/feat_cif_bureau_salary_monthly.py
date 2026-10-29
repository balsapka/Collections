"""Feature node: bureau-reported salary per customer and month.

One row per ``(cif_id, month_end)`` with a reported salary: ``bureau_salary`` is the
largest monthly total any provider reported for the month, over every pull of every
bureau file linked to the customer. All history the source holds is kept.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def _require(df: DataFrame, columns: list[str], source: str) -> None:
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f"{source} is missing columns: {missing}")


def build(salary_history: DataFrame, cif_bridge: DataFrame) -> DataFrame:
    """Join ``prm_bureau_salary_history`` to its customers through
    ``prm_bureau_cif_bridge`` on the bureau file (one CIF per file), then take the
    month's largest total."""
    _require(
        salary_history,
        ["bureau_file_id", "reference_month", "total_salary_amount"],
        "prm_bureau_salary_history",
    )
    _require(cif_bridge, ["bureau_file_id", "cif_id"], "prm_bureau_cif_bridge")
    files = (
        cif_bridge.filter(F.col("cif_id").isNotNull())
        .select(
            F.col("bureau_file_id").cast("string").alias("bureau_file_id"),
            F.col("cif_id").cast("string").alias("cif_id"),
        )
        .distinct()
    )
    return (
        salary_history.filter(F.col("total_salary_amount") > 0)
        .join(files, on="bureau_file_id")
        .groupBy("cif_id", F.last_day("reference_month").alias("month_end"))
        .agg(F.max("total_salary_amount").alias("bureau_salary"))
    )
