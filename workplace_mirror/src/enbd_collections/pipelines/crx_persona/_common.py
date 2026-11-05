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
  (``log_latest_month``);
* DCORE events are read per scored account, through its agreements
  (``dcore_account_events``); each axis applies its own date window.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Sequence

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql import types as T

LOG = logging.getLogger(__name__)

GRAIN = ("account_id", "observation_date")

# The two segments; every per-segment setting in crx_persona is keyed by them.
SEG_60_180, SEG_180_PLUS = "60_180", "180_plus"

# The DPD segment each model_id scores; every segment-dependent rule keys on it.
MODEL_ID_SEGMENT = {
    "cc_60_180": SEG_60_180,
    "cc_180_plus": SEG_180_PLUS,
    "rl_60_180": SEG_60_180,
    "rl_180_plus": SEG_180_PLUS,
}

# Months every axis looks back, the observation month included; the dry 180+ buckets
# look further.
WINDOW_MONTHS = {SEG_60_180: 3, SEG_180_PLUS: 6}
# Failed call days in a row that make a customer gone dark: A2 Non-Reachable (D-A2-20),
# A3's no-pickup diagnostic (D-A3-19).
GONE_DARK_DAYS = {SEG_60_180: 3, SEG_180_PLUS: 6}


def segment(model_id: str) -> str:
    """``model_id``'s DPD segment: ``60_180`` or ``180_plus``."""
    if model_id not in MODEL_ID_SEGMENT:
        raise ValueError(
            f"model_id must be one of {sorted(MODEL_ID_SEGMENT)}, got {model_id!r}"
        )
    return MODEL_ID_SEGMENT[model_id]


def window_months(model_id: str) -> int:
    """The lookback window of ``model_id``'s segment, in calendar months."""
    return WINDOW_MONTHS[segment(model_id)]


def require_columns(df: DataFrame, columns: Sequence[str], source: str) -> None:
    """Raise if ``df`` lacks any of ``columns`` — a renamed source must fail the run."""
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns {missing}")


def string_key(df: DataFrame, col: str = "account_id") -> Column:
    """``col`` as a trimmed string join key. A double or decimal id is cast to ``long``
    first: cast straight to string it reads ``1.23456789E8`` and matches nothing."""
    key = F.col(col)
    if isinstance(df.schema[col].dataType, (T.DoubleType, T.FloatType, T.DecimalType)):
        key = key.cast("long")
    return F.trim(key.cast("string"))


def window_start(months: int, anchor: Column | None = None) -> Column:
    """First day of the last ``months`` calendar months, the month of ``anchor``
    (default ``observation_date``) included."""
    anchor = F.col("observation_date") if anchor is None else anchor
    return F.add_months(F.trunc(anchor, "month"), 1 - months)


def scoped(src: DataFrame, base: DataFrame, key: str) -> DataFrame:
    """``src`` rows whose ``key`` occurs in ``base``. Sources span the whole bank, the
    base one model's customers: the broadcast semi-join drops the rest before the
    shuffle of the join that follows."""
    return src.join(F.broadcast(base.select(key).distinct()), on=key, how="left_semi")


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
    Ties on the date are broken by the values (largest first, NULL last), so reruns
    agree. Returns ``GRAIN + value_cols`` for base rows with a match only.
    """
    anchor = F.col("observation_date") if anchor is None else anchor
    before = (
        F.col("_d") <= F.col("_anchor") if inclusive else F.col("_d") < F.col("_anchor")
    )
    cond = before
    if max_age_months is not None:
        cond = cond & (F.col("_d") >= window_start(max_age_months, F.col("_anchor")))
    latest = F.max(F.struct("_d", *value_cols))
    return (
        base.select(*GRAIN, key, anchor.alias("_anchor"))
        .join(
            scoped(
                src.select(key, F.col(date_col).alias("_d"), *value_cols), base, key
            ),
            on=key,
        )
        .filter(cond)
        .groupBy(*GRAIN)
        .agg(latest.alias("_latest"))
        .select(*GRAIN, *[F.col("_latest")[c].alias(c) for c in value_cols])
    )


def window_agg(  # pylint: disable=too-many-arguments
    base: DataFrame,
    src: DataFrame,
    *,
    date_col: str,
    aggs: Sequence[Column],
    months: int,
    key: str = "cif_id",
    start: str | None = None,
) -> DataFrame:
    """Aggregate ``src`` rows dated in the last ``months`` calendar months — the
    observation month and the ``months - 1`` before it, up to the observation date.

    ``src`` holds ``key``, ``date_col`` and the columns ``aggs`` read. ``start`` names a
    base date column that bounds each row's window from below as well (A3, D-A3-2:
    the episode start); ``aggs`` may read it. Returns ``GRAIN + aggs`` for base rows
    with at least one row in the window.
    """
    obs = F.col("observation_date")
    lower = window_start(months)
    if start is not None:
        lower = F.greatest(lower, F.col(start))
    return (
        base.select(*GRAIN, key, *([start] if start is not None else []))
        .join(scoped(src, base, key), on=key)
        .filter((F.col(date_col) >= lower) & (F.col(date_col) <= obs))
        .groupBy(*GRAIN)
        .agg(*aggs)
    )


def lookback_floor(base: DataFrame, months: int) -> str:
    """ISO start of the earliest observation's ``months``-month window (the partition
    floor for a source read)."""
    first: date = base.agg(window_start(months, F.min("observation_date"))).first()[0]
    return first.isoformat()


def left_join_all(base: DataFrame, parts: Sequence[DataFrame]) -> DataFrame:
    """Left-join every part onto ``base.select(*GRAIN)`` on ``GRAIN``."""
    result = base.select(*GRAIN)
    for part in parts:
        result = result.join(part, on=list(GRAIN), how="left")
    return result


def log_latest_month(
    df: DataFrame,
    col: str,
    name: str,
    persona_end_date: str,
    *,
    latest_per_account: bool = False,
) -> None:
    """Log the ``col`` distribution of the latest observation month — the month of
    ``persona_end_date`` (one aggregate job; the month filter pushes down). A logging
    failure is a warning, never a failed run. ``latest_per_account`` counts each
    account's latest row of that month once (A4 scores the spine's billing dates, which
    can put two rows of a card in one month)."""
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    try:
        latest = df.filter(F.trunc("observation_date", "month") == month)
        if latest_per_account:
            newest_first = Window.partitionBy("account_id").orderBy(
                F.col("observation_date").desc()
            )
            latest = latest.withColumn("_rn", F.row_number().over(newest_first)).filter(
                F.col("_rn") == 1
            )
        rows = latest.groupBy(col).count().orderBy(col).collect()
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
    require_columns(cc_spine, ["contract_id", "observation_date", "cif_id"], "cc_spine")
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
    require_columns(rl_spine, ["account_id", "observation_date", "cif_id"], "rl_spine")
    return _obs_base(rl_spine, "account_id", crx_persona)


# ── DCORE ─────────────────────────────────────────────────────────────────────


def dcore_account_events(
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame
) -> DataFrame:
    """DCORE events on the agreements of the base's accounts: ``account_id``,
    ``day``, ``action_code``, ``category``, ``name`` (upper-cased, trimmed, '' when
    missing). Shared by A2 (D-A2-8: all history, one agreement per account) and A3
    (D-A3-7: account level). Not dated by the observation: the caller joins its rows
    and window."""
    require_columns(
        followup,
        ["agreement_id", "action_ts", "action_code", "result_category", "result_name"],
        "dcore_prm_followup_outcomes",
    )
    require_columns(
        agreements, ["account_id", "agreement_id"], "prm_dcore_account_agreements"
    )
    accounts = obs_base.select("account_id").distinct()
    scope = agreements.select("account_id", "agreement_id").join(
        F.broadcast(accounts), on="account_id", how="leftsemi"
    )

    def text(col: str) -> Column:
        return F.coalesce(F.upper(F.trim(col)), F.lit(""))

    return followup.select(
        F.col("agreement_id").cast("string").alias("agreement_id"),
        F.to_date("action_ts").alias("day"),
        text("action_code").alias("action_code"),
        text("result_category").alias("category"),
        text("result_name").alias("name"),
    ).join(F.broadcast(scope), on="agreement_id")
