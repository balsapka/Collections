"""Shared per-account windowing helpers for cc_raw_extract's nodes.

Factors out two blocks that were duplicated near-verbatim across
build_cc_transactions / build_cc_balance / build_cc_billing (and, for the
join+filter mechanics only, build_cc_limits) — pure extraction, no behavior
change (2026-10-21).
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

from enbd_collections.nodes.utils.config import EDP_LOAD_DATE_BUFFER_MONTHS


def prune_by_edp_load_date(raw_df: DataFrame, acct_windows: DataFrame) -> DataFrame:
    """Partition-prune raw_df on edp_load_date to the global acct window ± buffer.

    acct_windows: any DataFrame with acct_start/acct_end columns (e.g.
    crx_cc_acct_windows). The global [min(acct_start), max(acct_end)] bound is
    widened by +/-EDP_LOAD_DATE_BUFFER_MONTHS before filtering raw_df's
    edp_load_date column — see build_cc_transactions' docstring for why the
    buffer is needed (absorbs load-date lag; cc_spine has no backward lookback
    of its own). This is a superset filter only — callers still apply their
    own per-account date-range filter afterwards (see scope_to_acct_window).
    """
    window_lo, window_hi = acct_windows.agg(
        F.min("acct_start"), F.max("acct_end")
    ).first()
    load_date_lo = F.add_months(F.lit(window_lo), -EDP_LOAD_DATE_BUFFER_MONTHS)
    load_date_hi = F.add_months(F.lit(window_hi), EDP_LOAD_DATE_BUFFER_MONTHS)
    return raw_df.where(
        F.col("edp_load_date").cast(DateType()).between(load_date_lo, load_date_hi)
    )


def scope_to_acct_window(
    raw_df: DataFrame, acct_windows: DataFrame, date_col: str
) -> DataFrame:
    """Cast contract_idt to long, inner-join to acct_windows, filter date_col
    to [acct_start, acct_end].

    acct_windows: a DataFrame keyed by contract_idt with acct_start/acct_end
    columns — either crx_cc_acct_windows (re-keyed via _as_contract_windows)
    or build_cc_limits' own locally-built, T0-only window. date_col is the
    only thing that varies across call sites ("banking_date" or
    "billing_date").
    """
    return (
        raw_df.withColumn("contract_idt", F.col("contract_idt").cast("long"))
        .join(acct_windows, on="contract_idt", how="inner")
        .filter(
            (F.col(date_col).cast(DateType()) >= F.col("acct_start"))
            & (F.col(date_col).cast(DateType()) <= F.col("acct_end"))
        )
    )
