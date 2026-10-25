"""Shared building blocks for the crx_persona axes.

Every axis works at the observation grain ``(account_id, observation_date)`` and looks
up customer-level sources by ``cif_id``. The helpers here encode the conventions once:

* missing source columns stop the run (``require_columns``);
* windows are whole calendar months: the observation month (observation dates are month
  ends) and the months before it;
* point-in-time lookups read before the observation date and can be bounded in age
  (``pit_latest``), window aggregates read the last N months (``window_agg``);
* source partition floors follow from the earliest observation month
  (``lookback_floor``);
* each axis logs its state distribution for the latest observation month only
  (``log_latest_month``).
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Sequence

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from ._dpd_journey.constants import MODEL_ID_SEGMENT

LOG = logging.getLogger(__name__)

GRAIN = ("account_id", "observation_date")

# Months every axis looks back, the observation month included; the dry 180+ buckets
# look further.
WINDOW_MONTHS = {"60_180": 3, "180_plus": 6}


def window_months(model_id: str) -> int:
    """The lookback window of ``model_id``'s segment, in calendar months."""
    return WINDOW_MONTHS[MODEL_ID_SEGMENT[model_id]]


def require_columns(df: DataFrame, columns: Sequence[str], source: str) -> None:
    """Raise if ``df`` lacks any of ``columns`` — a renamed source must fail the run."""
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns {missing}")


def parse_yyyymmdd(col: str) -> Column:
    """``20260531`` (int or string) -> date."""
    return F.to_date(F.col(col).cast("string"), "yyyyMMdd")


def _window_start(anchor: Column, months: int) -> Column:
    """First day of the last ``months`` calendar months, the anchor's month included."""
    return F.add_months(F.trunc(anchor, "month"), 1 - months)


def pit_latest(  # pylint: disable=too-many-arguments
    base: DataFrame,
    src: DataFrame,
    *,
    date_col: str,
    value_cols: Sequence[str],
    key: str = "cif_id",
    anchor: Column | None = None,
    max_age_months: int | None = None,
    inclusive: bool = False,
) -> DataFrame:
    """Latest ``src`` row dated before each base row's anchor, per ``GRAIN``.

    ``src`` must carry ``key``, ``date_col`` (a date) and ``value_cols``. The anchor
    defaults to ``observation_date``; ``inclusive`` also accepts rows dated on it (same-
    day snapshots). ``max_age_months`` keeps only rows in the anchor's last N calendar
    months (1 = its own month), so a stale record never stands in for a current one.
    Ties on the date are broken by the values (descending), so reruns agree. Returns
    ``GRAIN + value_cols`` for base rows with a match only.
    """
    anchor = F.col("observation_date") if anchor is None else anchor
    before = (
        F.col("_d") <= F.col("_anchor") if inclusive else F.col("_d") < F.col("_anchor")
    )
    cond = before
    if max_age_months is not None:
        cond = cond & (F.col("_d") >= _window_start(F.col("_anchor"), max_age_months))
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
    months: int,
    key: str = "cif_id",
) -> DataFrame:
    """Aggregate ``src`` rows dated in the last ``months`` calendar months — the
    observation month and the ``months - 1`` before it, up to the observation date.

    ``src`` holds ``key``, ``date_col`` and the columns ``aggs`` read.
    Returns ``GRAIN + aggs`` for base rows with at least one row in the window.
    """
    obs = F.col("observation_date")
    return (
        base.select(*GRAIN, key)
        .join(src, on=key)
        .filter(
            (F.col(date_col) >= _window_start(obs, months)) & (F.col(date_col) <= obs)
        )
        .groupBy(*GRAIN)
        .agg(*aggs)
    )


def lookback_floor(base: DataFrame, months: int) -> str:
    """ISO start of the earliest observation's ``months``-month window (partition floor)."""
    first: date = base.agg(_window_start(F.min("observation_date"), months)).first()[0]
    return first.isoformat()


def left_join_all(base: DataFrame, parts: Sequence[DataFrame]) -> DataFrame:
    """Left-join every part onto ``base.select(*GRAIN)`` on ``GRAIN``."""
    result = base.select(*GRAIN)
    for part in parts:
        result = result.join(part, on=list(GRAIN), how="left")
    return result


def log_latest_month(df: DataFrame, col: str, name: str, persona_end_date: str) -> None:
    """Log the ``col`` distribution of the latest observation month — the month of
    ``persona_end_date`` (one aggregate job; the month filter pushes down). A logging
    failure is a warning, never a failed run."""
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    try:
        rows = (
            df.filter(F.trunc("observation_date", "month") == month)
            .groupBy(col)
            .count()
            .orderBy(col)
            .collect()
        )
    except Exception as exc:  # pylint: disable=broad-except
        LOG.warning("%s: %s distribution not logged: %s", name, col, exc)
        return
    total = sum(r["count"] for r in rows)
    LOG.info("%s — %s, month of %s (n=%d)", name, col, persona_end_date, total)
    for r in rows:
        LOG.info(
            "  %-28s %9d  (%5.1f%%)",
            r[col],
            r["count"],
            100.0 * r["count"] / max(total, 1),
        )


# ── Observation base ──────────────────────────────────────────────────────────


def _obs_base(spine: DataFrame, id_col: str, crx_persona: dict) -> DataFrame:
    """The spine rows in the persona months — ``crx_persona.persona_start_date`` to
    ``persona_end_date``, whole months — with the ``cif_id`` the spine already carries.

    Rows without a CIF are kept: customer-level signals are simply absent for them.
    Observation dates must be month ends; any other date stops the run.
    """
    month = F.trunc("observation_date", "month")
    in_persona = month.between(
        F.trunc(F.lit(str(crx_persona["persona_start_date"])), "month"),
        F.trunc(F.lit(str(crx_persona["persona_end_date"])), "month"),
    )
    base = (
        spine.select(
            F.col(id_col).cast("string").alias("account_id"),
            F.col("observation_date").cast("date"),
            "cif_id",
        )
        .filter(in_persona)
        .dropDuplicates(list(GRAIN))
    )
    mid_month = base.filter(F.col("observation_date") != F.last_day("observation_date"))
    if mid_month.limit(1).count():
        raise ValueError("spine observation dates must be month ends")
    return base


def build_cc_obs_base(cc_spine: DataFrame, crx_persona: dict) -> DataFrame:
    """The CC observation base at month ends. Until ``cc_spine`` itself is month-end, each
    billing-date row moves to its month end; an account's rows in one month become one
    (the largest ``cif_id`` if they disagree). Remove the shift once the spine is month-end.
    """
    month_end = cc_spine.select(
        "contract_id",
        F.last_day(F.col("observation_date").cast("date")).alias("observation_date"),
        "cif_id",
    )
    collapsed = month_end.groupBy("contract_id", "observation_date").agg(
        F.max("cif_id").alias("cif_id")
    )
    return _obs_base(collapsed, "contract_id", crx_persona)


def build_rl_obs_base(rl_spine: DataFrame, crx_persona: dict) -> DataFrame:
    """The RL observation base (``rl_spine`` is already month-end)."""
    return _obs_base(rl_spine, "account_id", crx_persona)
