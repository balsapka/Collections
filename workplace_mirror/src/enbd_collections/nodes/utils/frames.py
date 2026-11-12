"""Small helpers shared by the primary and feature nodes (CASA, products)."""

from __future__ import annotations

from datetime import date

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F


def months_back(day: str | date, months: int) -> date:
    """First day of the month ``months`` calendar months before ``day``'s month."""
    day = date.fromisoformat(str(day))
    year, month = divmod(day.year * 12 + day.month - 1 - months, 12)
    return date(year, month + 1, 1)


def require_columns(df: DataFrame, columns: list[str], source: str) -> None:
    """Raise ``ValueError`` naming ``source`` when ``df`` lacks any of ``columns``."""
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f"{source} is missing columns: {missing}")


def wm_month(week_number: str = "week_number") -> Column:
    """First day of the month of a WM ``yyyyMM0W`` week."""
    return F.to_date(F.substring(F.col(week_number).cast("string"), 1, 6), "yyyyMM")


def cif_column() -> Column:
    """``cif_id`` as a string (the persona join type)."""
    return F.col("cif_id").cast("string").alias("cif_id")
