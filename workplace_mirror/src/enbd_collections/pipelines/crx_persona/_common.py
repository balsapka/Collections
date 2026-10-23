"""Shared building blocks for the crx_persona axes.

Every axis works at the observation grain ``(account_id, observation_date)`` and looks
up customer-level sources by ``cif_id``. The helpers here encode the conventions once:

* missing source columns stop the run (``require_columns``);
* point-in-time lookups read strictly before the observation date and can be bounded in
  age (``pit_latest``), window aggregates read ``[start, observation_date)``
  (``window_agg``);
* source partition floors follow from the earliest observation date
  (``lookback_floor``);
* logging is opt-in and costs one job (``log_distribution``).
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Sequence

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.pipelines.crx_persona._spine_utils import _build_cif_bridge

LOG = logging.getLogger(__name__)

GRAIN = ("account_id", "observation_date")


def require_columns(df: DataFrame, columns: Sequence[str], source: str) -> None:
    """Raise if ``df`` lacks any of ``columns`` — a renamed source must fail the run."""
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns {missing}")


def parse_yyyymmdd(col: str) -> Column:
    """``20260531`` (int or string) -> date."""
    return F.to_date(F.col(col).cast("string"), "yyyyMMdd")


def _days_before(anchor: Column, days: int) -> Column:
    return F.date_sub(anchor, days)


def pit_latest(  # pylint: disable=too-many-arguments
    base: DataFrame,
    src: DataFrame,
    *,
    date_col: str,
    value_cols: Sequence[str],
    key: str = "cif_id",
    anchor: Column | None = None,
    max_age_days: int | None = None,
    inclusive: bool = False,
) -> DataFrame:
    """Latest ``src`` row dated before each base row's anchor, per ``GRAIN``.

    ``src`` must carry ``key``, ``date_col`` (a date) and ``value_cols``. The anchor
    defaults to ``observation_date``; ``inclusive`` also accepts rows dated on it (same-
    day snapshots). ``max_age_days`` drops rows older than that, so a stale record never
    stands in for a current one. Ties on the date are broken by the values (descending),
    so reruns agree. Returns ``GRAIN + value_cols`` for base rows with a match only.
    """
    anchor = F.col("observation_date") if anchor is None else anchor
    before = (
        F.col("_d") <= F.col("_anchor") if inclusive else F.col("_d") < F.col("_anchor")
    )
    cond = before
    if max_age_days is not None:
        cond = cond & (F.col("_d") >= _days_before(F.col("_anchor"), max_age_days))
    order = [F.col("_d").desc(), *[F.col(c).desc_nulls_last() for c in value_cols]]
    return (
        base.select(*GRAIN, key, anchor.alias("_anchor"))
        .join(src.select(key, F.col(date_col).alias("_d"), *value_cols), on=key)
        .filter(cond)
        .withColumn(
            "_rn", F.row_number().over(Window.partitionBy(*GRAIN).orderBy(*order))
        )
        .filter(F.col("_rn") == 1)
        .select(*GRAIN, *value_cols)
    )


def window_agg(  # pylint: disable=too-many-arguments
    base: DataFrame,
    src: DataFrame,
    *,
    date_col: str,
    aggs: Sequence[Column],
    days: int | None = None,
    months: int | None = None,
    key: str = "cif_id",
) -> DataFrame:
    """Aggregate ``src`` rows dated in a window ending before each observation date.

    ``days``: ``[obs - days, obs)``. ``months``: whole calendar months
    ``[trunc(obs) - months, trunc(obs))`` — for month-stamped series.
    ``src`` holds ``key``, ``date_col`` and the columns ``aggs`` read.
    Returns ``GRAIN + aggs`` for base rows with at least one row in the window.
    """
    if (days is None) == (months is None):
        raise ValueError("give exactly one of days / months")
    obs = F.col("observation_date")
    if days is not None:
        start, end = _days_before(obs, days), obs
    else:
        end = F.trunc(obs, "month")
        start = F.add_months(end, -months)
    return (
        base.select(*GRAIN, key)
        .join(src, on=key)
        .filter((F.col(date_col) >= start) & (F.col(date_col) < end))
        .groupBy(*GRAIN)
        .agg(*aggs)
    )


def lookback_floor(base: DataFrame, days: int) -> str:
    """ISO date ``days`` before the earliest observation date (partition floor)."""
    first: date = base.agg(F.min("observation_date")).first()[0]
    return (first - timedelta(days=days)).isoformat()


def left_join_all(base: DataFrame, parts: Sequence[DataFrame]) -> DataFrame:
    """Left-join every part onto ``base.select(*GRAIN)`` on ``GRAIN``."""
    result = base.select(*GRAIN)
    for part in parts:
        result = result.join(part, on=list(GRAIN), how="left")
    return result


def log_distribution(df: DataFrame, col: str, name: str, enabled: bool) -> None:
    """Log the value distribution of ``col`` (one job) when ``enabled``."""
    if not enabled:
        return
    rows = df.groupBy(col).count().orderBy(col).collect()
    total = sum(r["count"] for r in rows)
    LOG.info("%s — %s distribution (n=%d)", name, col, total)
    for r in rows:
        LOG.info(
            "  %-28s %9d  (%5.1f%%)",
            r[col],
            r["count"],
            100.0 * r["count"] / max(total, 1),
        )


# ── Observation base ──────────────────────────────────────────────────────────


def build_cc_obs_base(
    cc_spine: DataFrame, contract: DataFrame, client: DataFrame
) -> DataFrame:
    """Every CC spine row with its ``cif_id`` (NULL if the contract has no client).

    Rows without a CIF are kept: customer-level signals are simply absent for them.
    """
    spine = cc_spine.select(
        F.col("contract_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date"),
    ).dropDuplicates(list(GRAIN))
    bridge = _build_cif_bridge(contract, client).select(
        F.col("contract_id").cast("string").alias("account_id"), "cif_id"
    )
    return spine.join(bridge, on="account_id", how="left")


def build_rl_obs_base(rl_spine: DataFrame) -> DataFrame:
    """Every RL spine row with the ``cif_id`` the spine already carries."""
    return rl_spine.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        "cif_id",
    ).dropDuplicates(list(GRAIN))
