"""Month arithmetic for ``spark.py``, in plain Python and as Spark columns.

A month index is ``year * 12 + month - 1``, so the gap between two months is a
subtraction.
"""

from __future__ import annotations

import datetime as _dt

from pyspark.sql import functions as F


def _month_idx(d) -> int:
    """Month as an integer (year * 12 + month - 1) — gap arithmetic without date math."""
    d = _dt.date.fromisoformat(str(d)[:10]) if not isinstance(d, _dt.date) else d
    return d.year * 12 + d.month - 1


def _month_col(c) -> F.Column:
    """Spark column twin of ``_month_idx``."""
    return (F.year(c) * 12 + F.month(c) - 1).cast("int")
