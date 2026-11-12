"""Feature node: bureau salary per customer and month, the A1 income contract.

One row per ``(cif_id, month_end)`` from the DE's ``feat_bureau_salary_unified``, which
picks one monthly salary per customer across three AECB sources (``alert`` change events,
``salary_credit`` application-time history, ``bureau_salary`` bulk-pull aggregates spread
back over 12 months):

* ``bureau_salary`` - the unified ``monthly_salary`` (AED; 0 = no usable amount that
  month, e.g. a salary account closed);
* ``salary_source`` - the source that gave it (reporting only).

Months without a row have no bureau salary. How far a row carries is decided by the
consumer (A1 carries it one month, S14). To swap the bureau source, rebuild this table
from the new one; the A1 engine reads only this contract.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.utils.frames import require_columns


def build(unified: DataFrame) -> DataFrame:
    """``cif_id`` (string), ``month_end``, ``bureau_salary``, ``salary_source`` from
    ``feat_bureau_salary_unified`` (already one row per customer and month)."""
    require_columns(
        unified,
        ["cif_id", "salary_month_end", "monthly_salary", "salary_source"],
        "feat_bureau_salary_unified",
    )
    return unified.filter(
        F.col("cif_id").isNotNull() & F.col("monthly_salary").isNotNull()
    ).select(
        F.trim(F.col("cif_id").cast("string")).alias("cif_id"),
        F.last_day("salary_month_end").alias("month_end"),
        F.col("monthly_salary").cast("double").alias("bureau_salary"),
        "salary_source",
    )
