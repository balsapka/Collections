"""Month-arithmetic helpers, plain-Python and Spark-column alike.

`_month_col` is a Spark column expression, not a date-parsing helper like its neighbours —
it lives here anyway (rather than in spark.py) so that both spark.py and logging.py can
import it one-directionally from a common module. spark.py also calls into logging.py
(build_dpd_sequences/build_deterioration trigger the stats logs), so if `_month_col` lived
in spark.py, logging.py importing it back would make the two modules import each other.
"""

from __future__ import annotations

import datetime as _dt

from pyspark.sql import functions as F


def _month_idx(d) -> int:
    """Month as an integer (year * 12 + month - 1) — gap arithmetic without date math."""
    d = _dt.date.fromisoformat(str(d)[:10]) if not isinstance(d, _dt.date) else d
    return d.year * 12 + d.month - 1


def _month_label(d) -> str:
    """'YYYY Month' from a date-like value, e.g. 2026-08-31 -> '2026 August' —
    human-readable logging only, never a machine-compared value."""
    d = _dt.date.fromisoformat(str(d)[:10]) if not isinstance(d, _dt.date) else d
    return d.strftime("%Y %B")


def _month_col(c) -> F.Column:
    return (F.year(c) * 12 + F.month(c) - 1).cast("int")
