"""The episode anchor: the month the current delinquency episode began, point in time.

A4 scores each spine row on the account's monthly history up to that row's month; the
episode (spell) is the last run of delinquent months in it (a cure back to current ends
one) and starts ``months_before_spell`` months into that history. Axes that window on
the episode read its start here instead of from a spell table (D-A3-2: the anchor is
the latest episode start as of the observation date).
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, pit_latest, require_columns, string_key

# The A4 row read is the latest one in the observation's own month.
_A4_MAX_AGE_M = 1


def episode_start(obs_base: DataFrame, deterioration: DataFrame) -> DataFrame:
    """``GRAIN + episode_start, episode_left_censored`` for the base rows A4 scored in
    the observation month.

    ``episode_start`` is the first day of the month the current episode began, taken
    from the latest A4 row on or before the observation date in that month (CC: a
    billing date). ``episode_left_censored``: A4 cropped the history (source start,
    floor, truncation) and the episode already ran in its first kept month, so the true
    onset may be earlier and the consumer treats the anchor as unknown (A3: Q-25); an
    uncropped history delinquent from its first month has a true onset. Base rows A4
    did not score get no row.
    """
    require_columns(
        deterioration,
        [*GRAIN, "months_before_spell", "history_months"]
        + ["left_censored", "history_cropped"],
        "crx_<product>_a4_deterioration",
    )
    # months from the episode's first month to the row's month, back from history end
    months_back = F.col("history_months") - 1 - F.col("months_before_spell")
    censored = F.col("left_censored") & F.col("history_cropped")
    src = deterioration.select(
        string_key(deterioration).alias("account_id"),
        F.col("observation_date").cast("date").alias("a4_date"),
        F.add_months(F.trunc("observation_date", "month"), -months_back).alias(
            "episode_start"
        ),
        censored.alias("episode_left_censored"),
    )
    return pit_latest(
        obs_base,
        src,
        key="account_id",
        date_col="a4_date",
        value_cols=["episode_start", "episode_left_censored"],
        inclusive=True,
        max_age_months=_A4_MAX_AGE_M,
    )
