"""Spine-driven staging utilities for the Collections risk-modeling pipeline.

Public API:
    Scd2Schema        -- column + interval-semantics contract for SCD2 tables
    OPEN_END_SENTINEL -- the bank's "still open" effective_end_date value
    active_as_of      -- one active row per key at a single observation_date
    prefilter_scd2    -- reduce a billion-row SCD2 table to the spine
    prefilter_daily   -- reduce a daily-grain table to the spine
    build_spine       -- (account_id x observation_date) spine builder
    stage_scd2_table  -- Kedro node wrapper around prefilter_scd2
    stage_daily_table -- Kedro node wrapper around prefilter_daily
"""

from .spine import (
    OPEN_END_SENTINEL,
    Scd2Schema,
    active_as_of,
    build_spine,
    prefilter_daily,
    prefilter_scd2,
    stage_daily_table,
    stage_scd2_table,
)

__all__ = [
    "OPEN_END_SENTINEL",
    "Scd2Schema",
    "active_as_of",
    "build_spine",
    "prefilter_daily",
    "prefilter_scd2",
    "stage_daily_table",
    "stage_scd2_table",
]
